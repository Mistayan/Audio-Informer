"""
Created by: Mistayan
Project: Learning-Python
"""

import asyncio

import aiohttp


async def async_get(url, query):
    """
    Generate an async session requesting url + query
    Returns a StreamReader, according to current response formatting
    """
    try:
        root = url.split('/')[2]
        rl = len(root.split('.'))
        if 2 < rl > 4:
            raise IndexError
    except IndexError:
        raise AssertionError(f"url format not valid")
    async with aiohttp.ClientSession() as session:  # Start a new session for current thread
        async with session.get(url + query) as response:  # Start a new session for current thread
            if response.host != root:
                raise f"{response.host} not {root}"
            match response.content_type:
                case 'application/json':
                    return await response.json()
                case 'text/html':
                    return await response.read()
                case _:
                    return await response.content.read()
    return  # session or get failed. Unlikely... but may happen


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
            self.__need_purge = True
            self.__loop = asyncio.new_event_loop()
        self.future = asyncio.gather(async_get(url, query))  # initiate request in background's loop
        self.result = None

    def get(self):
        """
        Will freeze main process until result is available.
        when done, stop current loop after ensuring _future
        """
        if not self.result:
            self.result = self.__loop.run_until_complete(self.future)[0]
            self.__stop() if hasattr(self, '__need_purge') else None

        return self.result  # wait for request to end then return response

    def __stop(self):
        loop = self.__loop
        loop.stop()
        while loop.is_running():
            asyncio.sleep(1, self.get, loop=self.__loop)
        self.__loop.close()


def test_json(n: int = 100):
    import re
    import time
    print("-_" * 7 + " Async : " + "-_" * 7)
    start = time.perf_counter()
    prepares = [AsyncRequest("https://httpbin.org/", "uuid") for _ in range(n)]
    results = [prepare.get()['uuid'] for prepare in prepares]

    assert time.perf_counter() - start < 1.1  # If timer goes high, may need optimisations
    assert len(results) == n and None not in results
    print("speed test OK")

    for elem in results:
        assert len(elem) is 36  # check if every uuid is valid
        assert re.fullmatch(r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", elem) is not None
    print("content test OK")


def test_mb_search():
    import time
    import parse

    site = "https://musicbrainz.org/"
    queries = ["search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("Lady Gaga", "Shallow"),
               "search?query=\"{0}\"+AND+\"{1}\"&type=release&limit=1".format("Ratatat", "Loud Pipes"),
               "search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("Marina", "Pink Convertible"),
               "search?query={0}+AND+{1}&type=release&limit=1".format("Miley", "Wrecking "),
               "search?query={0}+AND+{1}&type=release&limit=1".format("fleebag", "YUNGBLUD"),
               "search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("Retour vers le futur", ""),
               "search?query={0}+AND+\"{1}\"&type=release&limit=1".format("Highlander", "Who Wants to Live Forever"),
               "BadRequest"]
    print("-_" * 7 + " Async : " + "-_" * 7)
    start = time.perf_counter()
    async_list = [AsyncRequest(site, query) for query in queries]
    print(f"async sent in :{time.perf_counter() - start:0.5f}s\n")
    results = [job.get() for job in async_list]
    print(f"nb_of results: {len(results)} \tin :{time.perf_counter() - start:0.5f}s\n")
    for elem in results:
        search = parse.search("/release/{0}\"", str(elem))
        result = search if not search else search[0]
        if type(result) is str:
            result = result if not result.find('/') else result.split('/')[0]  # Avoid mbid/cover-art in some cases
        print(result)


if __name__ == '__main__':
    req = AsyncRequest("https://www.bing.com/?q=", "top+10+hacks+reasons")
    print(req.get())
    pass
