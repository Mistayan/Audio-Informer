"""
Created by: Mistayan
Project: Learning-Python
"""
import time
import asyncio
import logging

import aiohttp
import parse
import yarl
import brotli  # Useful for br pages (more and more common on the web)
import nest_asyncio

nest_asyncio.apply()
log = logging.getLogger(__name__)


# ____________________________________________________ #
# __________________ ASYNC FUNCTIONS _________________ #
# ____________________________________________________ #
async def get_content(url: str, query: str = '') -> (dict | str | bytes | None):
    """
    Generate an async session requesting url + query
    Returns a StreamReader, according to current response formatting
    """
    if not url:
        return
    target = yarl.URL(url + query)  # proper request formatting
    log.info(f"request : {target}")
    try:
        async with aiohttp.ClientSession() as session:  # Start a new session for current thread
            async with session.get(target) as response:  # Get session's content
                # if response.host != target.host and "www." + response.host != target.host:
                #     raise ValueError(f"{response.host} not {target.host}")
                if not response.status == 200:
                    return
                else:
                    log.debug(response.content_type)
                    match response.content_type:
                        case 'application/json':
                            ret: dict = await response.json()
                        case 'text/html':
                            ret: str = await response.text()
                        case _:
                            ret: bytes = await response.content.read()
        if response.status == 200:
            log.debug(f"result for {target.human_repr()}: {ret if not isinstance(ret, bytes) else 'bytes.'}")
    except aiohttp.ClientConnectorError:
        log.debug(f"Connection not established with {target.human_repr()}")
        ret = None
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
    request2 = AsyncRequest(get_content, address, callback=print)
    print(request2.get())  # as soon as possible
    # do stuff (like requesting more stuff ?)
    results = request.get()
    # do more stuff with the results
    time.sleep(2)

    """

    def __init__(self, func, *args, **kwargs):
        self.log = logging.getLogger(__name__ + str(func))
        self.start = time.perf_counter()
        self.name = [*args]
        self.__loop = None
        self.future = None
        # sanity checks
        try:
            self.__loop = asyncio.get_event_loop_policy().get_event_loop()
            self.future = asyncio.Task(func(*args), loop=self.__loop)  # initiate request as background task
            self.future.add_done_callback(self._set_result)
            asyncio.set_event_loop(self.__loop)
            self.result = None
        except RuntimeError or RuntimeWarning:  # multithread / multiprocess context
            self.result = asyncio.run(func(*args))
        self.end = time.perf_counter()

    def add_done_callback(self, callback):
        if callback\
                and isinstance(callback, staticmethod) and issubclass(callback, classmethod)\
                and self.future:
            self.future.add_done_callback(callback)

    def _set_result(self, cb):
        if isinstance(cb, Exception):
            self.log.debug(f"Exceptions raised as callback @{time.perf_counter() - self.start}\n{cb}s")
            raise cb
        else:
            self.log.debug(f"callback for {self.name} : {cb} received @{time.perf_counter() - self.start:0.4f}s")
            self.result = cb.result()[0] if isinstance(cb.result(), list) else cb.result()
        return self.result

    def get(self):
        """
        If internal callback is received (Thread raised an Error, or ended), skip freeze \n
        Will freeze calling process until result is available. \n
        When done, stop current loop after ensuring _Future \n
        Release newly created loop (if not main thread's loop)
        """
        try:
            if self.future and (not self.future.done() or not self.result):
                loop = self.future.get_loop()
                if not loop.is_running():
                    loop.run_until_complete(self.future)
                if not self.result:
                    self.result = self.future.result()
                    self.future = None
        except RuntimeError:  # Either loop is done and closed or could not process requested datas.
            pass
        return self.result

    def close(self, cb=None):
        # self.__await__()
        if isinstance(cb, Exception):
            return
        if self.__loop.is_running():
            self.log.debug(f"stopping loop {self.__loop}")
            self.__loop.stop()
        self.log.debug(f"closing loop {self.__loop}")
        self.__loop.close()

    def __str__(self):
        return self.get()

    def __await__(self):
        if self.future:
            self.future.__await__()


# ____________________________________________________ #
# _______________________ TESTS ______________________ #
# ____________________________________________________ #

def test_json(n: int = 10):
    import re
    import time
    from uuid import UUID
    print("-_" * 7 + " Async : " + "-_" * 7)
    s = time.time()
    prepares = [AsyncRequest(get_content, "https://httpbin.org/", "uuid") for _ in range(n)]
    results = [prepare.get() for prepare in prepares]
    assert time.perf_counter() - s < n / 5  # If timer goes high, may need optimisations
    print("speed test OK")

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
    query = "\"{0}\"+AND+\"{1}\"&type=release&limit=1"
    queries = [query.format("Lady Gaga", "Shallow"),
               query.format("Ratatat", "Loud Pipes"),
               query.format("Marina", "Pink"),
               query.format("Miley", "Wrecking "),
               query.format("fleebag", "YUNGBLUD"),
               query.format("Retour vers le futur", ""),
               query.format("", "Who Wants to Live Forever"),  # Sadly returns None
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
    test_mb_search()

    req = AsyncRequest(get_content, "https://www.bing.com/?", "q=top+10+hacks+reasons")
    req.get()
    if req.get():
        href_finder = parse.Parser("href=\"{url}\"")
        links = href_finder.findall(req.get())
        for link in links:
            if link["url"][0] == 'h':
                print(link['url'])
