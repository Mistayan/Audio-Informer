"""
Created by: Mistayan
Project: Learning-Python
"""

import asyncio
import aiohttp
import parse
import re


async def async_get(url, query):
    try:
        root = url.split('/')[2]
        if len(root.split('.')) != 2:
            raise IndexError
    except IndexError:
        raise AssertionError(f"url format not valid")
    async with aiohttp.ClientSession().get(url + query) as response:  # Start a new session for current thread
        if response.host != root:
            raise f"{response.host} not {root}"
        match response.content_type:
            case 'application/json':
                return await response.json()
            case 'text/html':
                return await response.content.read()
            case _:
                return await response.content.read()
    return  # session or get failed. Unlikely... but may happen


class AsyncRequest:

    def __init__(self, url: str, query: str):
        self.__loop = asyncio.get_event_loop()
        self.future = asyncio.gather(async_get(url, query))

    def get(self):
        return self.__loop.run_until_complete(self.future)[0]


def test_json(n: int = 100):
    import time
    print("-_" * 7 + " Async : " + "-_" * 7)
    start = time.perf_counter()
    prepares = [AsyncRequest("https://httpbin.org/", "uuid") for _ in range(n)]
    # simulate program running
    # time.sleep(2)
    results = [prepare.get()['uuid'] for prepare in prepares]

    assert time.perf_counter() - start < 1.1  # If timer goes high, may need optimisations
    for elem in results:
        assert len(elem) is 36  # check if every uuid is valid
        assert re.fullmatch(r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", elem) is not None


def test_mb_search():
    import time

    site = "https://musicbrainz.org/"
    queries = ["search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("Lady Gaga", "Shallow"),
               "search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("Ratatat", "Loud Pipes"),
               "search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("Marina", "Pink Convertible"),
               "search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("unknow artist", "unkownsong"),
               "search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("YUNGBLUD", "FleeBag"),
               "search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("Retour vers le futur", ""),
               "search?query=\"{0}\"+AND+{1}&type=release&limit=1".format("Highlander", "Who Wants to Live Forever"),
               "BadRequest"]
    print("-_" * 7 + " Async : " + "-_" * 7)
    start = time.perf_counter()
    async_list = [AsyncRequest(site, query) for query in queries]
    print(f"async sent in :{time.perf_counter() - start:0.5f}s\n")
    results = [job.get() for job in async_list]
    print(f"nb_of results: {len(results)} \tin :{time.perf_counter() - start:0.5f}s\n")
    for elem in results:
        search = parse.search("/release/{0}\"", str(elem))
        result = search[0] if search else search
        if type(result) is str:
            result = result.split('/')[0] if result.find('/') else result  # Avoid /cover-art in some cases
        print(result)


if __name__ == '__main__':
    print(AsyncRequest("bing.com/?q=", "top+10+hacks+reasons").get()[0])
    pass
