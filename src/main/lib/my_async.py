"""
Created by: Mistayan
Project: Learning-Python
"""
import time
import asyncio
import logging
from multiprocessing import process
from uuid import UUID

import aiohttp
import yarl
import nest_asyncio

nest_asyncio.apply()
log = logging.getLogger(__name__)


# ____________________________________________________ #
# __________________ ASYNC FUNCTIONS _________________ #
# ____________________________________________________ #
async def get_content(url: str, query: str = ''):
    """
    Generate an async session requesting url + query
    Returns a StreamReader, according to current response formatting
    """

    target = yarl.URL(url + query)
    log.info(f"request : {target}")
    async with aiohttp.ClientSession() as session:  # Start a new session for current thread
        async with session.get(target) as response:  # Start a new session for current thread
            if response.host != target.host:
                raise f"{response.host} not {target.host}"
            if not response.status == 200:
                ret = response
            else:
                match response.content_type:
                    case 'application/json':
                        ret = await response.json()
                    case 'text/html':
                        ret = await response.read()
                    case _:
                        ret = await response.content.read()
    log.debug(f"result for {target.human_repr()}: {ret}")
    return ret


async def async_print(*values, sep: str = None, end: str = None, file: [str] = None, flush: bool = False):
    print([await value for value in values], sep, end, file, flush)


# ____________________________________________________ #
# _____________________ EASY ASYNC ___________________ #
# ____________________________________________________ #
class AsyncRequest:
    """
    !!! can now be instantiated in async coroutines  !!!
    Start an asynchronous request when you call the class. \
    You can retrieve results later on in your program without the pain to wait.

    How To Use:
    request = AsyncRequest(async_function, arg1, arg2, ..., {datas required for async_function to run})
    request2 = AsyncRequest(get_content, address, callback=print)  # print(request2.get()) as soon as possible
    # do stuff (like requesting more stuff ?)
    results = request.get()
    # do more stuff with the results
    time.sleep(2)

    """

    def __init__(self, func, *args, **kwargs):
        self.log = logging.getLogger(__name__ + str(func))

        # sanity checks
        self.start = time.perf_counter()
        try:
            self.__loop = asyncio.get_event_loop()
            self.__purge_when_done = False
        except RuntimeError:
            self.log.debug("creating new loop")
            self.__loop = asyncio.new_event_loop()
            self.__purge_when_done = True
        self.result = None
        asyncio.set_event_loop(self.__loop)

        # Start
        self.future = asyncio.gather(func(*args, **kwargs))  # initiate request in background's loop
        if self.future:
            self.future.add_done_callback(self._set_result)
        else:
            raise asyncio.InvalidStateError(f"No future created : {asyncio.Queue}")

    def add_done_callback(self, callback):
        if callback\
                and isinstance(callback, staticmethod) and issubclass(callback, classmethod)\
                and self.future:
            self.future.add_done_callback(callback)

    def _set_result(self, callback):
        if isinstance(callback, Exception):
            self.log.debug(f"Exceptions raised as callback @{time.perf_counter() - self.start}\n{callback:0.4f}s")
            self.result = None
            raise callback
        else:
            self.log.debug(f"callback {callback} received @{time.perf_counter() - self.start:0.4f}s")
            try:
                self.result = callback.result()[0]
            except TypeError:  # <_GatheringFuture ... result = None>
                self.result = None
                raise
        self.future = None

    def get(self):
        """
        If internal callback is received (Thread raised an Error, or ended), skip freeze
        Will freeze calling process until result is available.
        when done, stop current loop after ensuring _Future
        Release newly created loop (if not main thread's loop)
        """
        if self.future and not self.future.done() or not self.result:
            if not self.__loop.is_running() and self.future:
                self.future.remove_done_callback(self._set_result)
                self.result = self.__loop.run_until_complete(self.future)[0]  # [0] due to asyncio.gather return format
            elif self.future:
                self.future.__await__()
            self.future = None

        if self.__purge_when_done:
            self.__loop.close()
            self.__purge_when_done = False

        return self.result  # wait for request to end then return response

    def __str__(self):
        return self.get()


# ____________________________________________________ #
# _______________________ TESTS ______________________ #
# ____________________________________________________ #

def test_json(n: int = 55):
    import re
    import time
    print("-_" * 7 + " Async : " + "-_" * 7)
    s = time.time()
    prepares = [AsyncRequest(get_content, "https://httpbin.org/", "uuid") for _ in range(n)]
    results = [prepare.get() for prepare in prepares]
    # assert time.perf_counter() - start < n / 6  # If timer goes high, may need optimisations
    # print("speed test OK")

    assert len(results) == n and None not in results
    for elem in results:
        assert type(elem) is dict

        assert len(elem['uuid']) == 36  # check if every uuid is valid
        assert str(UUID(elem['uuid'])) == elem['uuid']
        assert re.fullmatch(r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", elem['uuid']) is not None
    print(f"content test OK. time spent: {time.time() - s:0.3f}s")


def test_mb_search():
    import time
    import parse

    print()
    site = "https://musicbrainz.org/search?query="
    sub = "\"{0}\"+AND+\"{1}\"&type=release&limit=1"
    queries = [sub.format("Lady Gaga", "Shallow"),
               sub.format("Ratatat", "Loud Pipes"),
               sub.format("Marina", "Pink"),
               sub.format("Miley", "Wrecking "),
               sub.format("fleebag", "YUNGBLUD"),
               sub.format("Retour vers le futur", ""),
               sub.format("", "Who Wants to Live Forever"),
               "BadRequest"]
    print("-_" * 7 + " Async : " + "-_" * 7)
    start = time.perf_counter()
    async_list = [AsyncRequest(get_content, site, query) for query in queries]
    print(f"async sent in :{time.perf_counter() - start:0.5f}s\n")
    results = [job.get() for job in async_list]
    compiled = parse.compile("/release/{0}\"")
    print(f"nb_of results: {len(results)} \tin :{time.perf_counter() - start:0.5f}s\n")
    for elem in results:
        search = compiled.search(str(elem))
        result = search if not search else search[0]
        if type(result) is str:
            result = result if not result.find('/') else result.split('/')[0]  # Avoid mbid/cover-art in some cases
        print(result)


if __name__ == '__main__':
    test_json()
    test_mb_search()  # TODO: real tests, no prints
    req = AsyncRequest("https://www.bing.com/?q=", "top+10+hacks+reasons")
    print(req.get())
    pass
