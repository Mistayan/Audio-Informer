"""
Created by: Mistayan
Project: Learning-Python
"""

import asyncio
import aiohttp


# ____________________________________________________ #
# __________________ ASYNC FUNCTIONS _________________ #
# ____________________________________________________ #
async def async_get(url, query):
    """
    Generate an async session requesting url + query
    Returns a StreamReader, according to current response formatting
    """
    try:
        # required type : http(s)://[www.][subdomain(s).]site.com[/...]
        root = url.split('/')[2]  # [www.][subdomain(s).]site.com
        rl = len(root.split('.'))
        if 2 < rl > 5:  # Allow 2 subdomains for some specific cases
            raise IndexError
    except IndexError:
        raise AssertionError(f"url format not valid")
    async with aiohttp.ClientSession() as session:  # Start a new session for current thread
        async with session.get(url + query) as response:  # Start a new session for current thread
            if response.host != root:
                raise f"{response.host} not {root}"
            if not response.status == 200:
                return response
            match response.content_type:
                case 'application/json':
                    return await response.json()
                case 'text/html':
                    return await response.read()
                case _:
                    return await response.content.read()


# ____________________________________________________ #
# _____________________ EASY CLASS ___________________ #
# ____________________________________________________ #
class AsyncRequest:
    """
    Start an asynchronous request when you call the class. \
    You can retrieve results later on in your program without the pain to wait.
    -url: "https://[www].site.ext/?q="
    -query: The query to send to the server

    How To Use:
    request = AsyncRequest(url, query)
    # do stuff (like requesting more stuff ?)
    results = request.get()
    # do more stuff with the results
    """

    def __init__(self, url: str, query: str):
        self.__loop = asyncio.get_event_loop()
        if self.__loop is None:
            self.__purge_when_done = True
            self.__loop = asyncio.new_event_loop()
        else:
            self.__purge_when_done = False
        self.future = asyncio.gather(async_get(url, query))  # initiate request in background's loop
        self.result = None

    def get(self):
        """
        Will freeze main process until result is available.
        when done, stop current loop after ensuring _Future
        Release newly created loop (if not main thread's loop)
        """
        return self.__await__()  # wait for request to end then return response

    async def __stop(self) -> None:
        """Internal use only."""
        loop = self.__loop
        loop.stop()
        while loop.is_running():
            await asyncio.sleep(0.2, self.__await__, loop=self.__loop)
        self.__loop.close()

    def __await__(self):
        if not self.result and self.future:
            self.result = self.__loop.run_until_complete(self.future)[0]
            self.future = None
        if self.__purge_when_done:
            self.__stop()
            self.__purge_when_done = False
        return self.result


# ____________________________________________________ #
# _______________________ TESTS ______________________ #
# ____________________________________________________ #
def test_json(n: int = 100):
    import re
    import time
    print("-_" * 7 + " Async : " + "-_" * 7)
    start = time.perf_counter()
    prepares = [AsyncRequest("https://httpbin.org/", "uuid") for _ in range(n)]
    results = [prepare.get()['uuid'] for prepare in prepares]
    assert time.perf_counter() - start < 2  # If timer goes high, may need optimisations
    assert len(results) == n and None not in results
    print("speed test OK")

    for elem in results:
        assert len(elem) == 36  # check if every uuid is valid
        assert re.fullmatch(r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", elem) is not None
    print("content test OK")


def test_mb_search():
    import time
    import parse

    print()
    site = "https://musicbrainz.org/"
    sub = "search?query=\"{0}\"+AND+\"{1}\"&type=release&limit=1"
    queries = [sub.format("Lady Gaga", "Shallow"),
               sub.format("Ratatat", "Loud Pipes"),
               sub.format("Marina ", " Convertible"),
               sub.format("Miley", "Wrecking "),
               sub.format("fleebag", "YUNGBLUD"),
               sub.format("Retour vers le futur", ""),
               sub.format("", "Who Wants to Live Forever"),
               "BadRequest"]
    print("-_" * 7 + " Async : " + "-_" * 7)
    start = time.perf_counter()
    async_list = [AsyncRequest(site, query) for query in queries]
    print(f"async sent in :{time.perf_counter() - start:0.5f}s\n")
    results = [job.get() for job in async_list]
    print(f"nb_of results: {len(results)} \tin :{time.perf_counter() - start:0.5f}s\n")
    compiled = parse.compile("/release/{0}\"")
    for elem in results:
        search = compiled.search(str(elem))
        result = search if not search else search[0]
        if type(result) is str:
            result = result if not result.find('/') else result.split('/')[0]  # Avoid mbid/cover-art in some cases
        print(result)


if __name__ == '__main__':
    req = AsyncRequest("https://www.bing.com/?q=", "top+10+hacks+reasons")
    print(req.get())
    pass
