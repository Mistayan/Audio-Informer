"""
Created by: Mistayan
Project: Learning-Python
"""

import asyncio
import aiohttp


class AsyncRequest:
    _url: str
    query: str

    def __init__(self, url: str, query: str):
        try:
            self.root = url.split('/')[2]
            if len(self.root.split('.')) != 2:
                raise IndexError
        except IndexError:
            raise AssertionError(f"url format not valid")
        self._url = url
        self.query = query
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)
        self.future = self.__prepare_request()

    async def __prepare_request(self):
        async def async_request(__session):
            async with __session.get(self._url + self.query) as response:
                if response.host != self.root:
                    raise f"{response.host} not {self.root}"
                match response.content_type:
                    case 'application/json':
                        return await response.json()
                    case 'text/html':
                        return await response.content.read()
                    case _:
                        return await response.content

        async with aiohttp.ClientSession() as session:  # Start a new session for current thread
            return await asyncio.gather(async_request(session))  # Do async_request

    def get(self):
        return self.__loop.run_until_complete(self.future)


def test_json():
    import time
    print("-_" * 7 + " Async : " + "-_" * 7)
    start = time.perf_counter()
    prepare = AsyncRequest("https://httpbin.org/", "uuid")
    results = prepare.get()
    exec_time = time.perf_counter() - start
    print(f"nb_of results: {len(results)} \tin: {exec_time:0.3f}s\n")
    print(results)


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
    print(f"async sent in :{time.perf_counter() - start:0.3f}s\n")
    results = [job.get() for job in async_list]
    print(f"nb_of results: {len(results)} \tin :{time.perf_counter() - start:0.3f}s\n")
    print(results)


if __name__ == '__main__':
    import time

    # test_json()
    try:
        test_mb_search()
    except RuntimeError:
        pass
    # prepare2 = AsyncRequest("https://musicbrainz.org/search?query=", "\"{0}\"+AND+{1}&type=release&limit=1")
