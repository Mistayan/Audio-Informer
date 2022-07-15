"""
Created by: Mistayan
Project: Audio-Informer
Creation date: 07/10/22
"""
import time

import conf.api
from lib.my_async import AsyncRequest
from lib.utils import format_htm
from lib.my_json import save_json
import logging


def musicbrainz_api(intel: dict):
    start = time.time()
    log = logging.getLogger(__name__)
    log.setLevel(conf.api_conf.DEBUG)
    log.debug(f"{__name__} @{time.time() - start} : start")
    intels = intel
    if not intels or not intels['Artist'] or not intels['Title']:
        log.warning("Could not request musicbrainz. Insuffisant datas")
        return

    query = f"\"{format_htm(intels['Artist'])}\"+AND+" \
            f"\"{format_htm(intels['Title'])}\"&limit=5" \
            "&fmt=json"  # json <3
    jj = AsyncRequest("https://musicbrainz.org/ws/2/recording?query=", query).get()
    log.debug(f"{__name__} @{time.time() - start} : Async Done")

    # TODO: target_dir dynamic (after global integration)
    target_dir = f"C:/Users/GAMER/Desktop/python-learnin/Audio-Informer/Results/{intels['Artist']}/"
    file_name = f"{intels['Title']}.json"
    save_json(jj, target_dir, file_name)
    log.debug(f"{__name__} @{time.time() - start} : json saved")

    ret = {}
    try:
        ret.setdefault("rbid", jj['recordings'][0]['id'])
    except IndexError:
        return
    for recording in jj['recordings']:
        print(recording)
        if hasattr(intels, 'length') and intels['length'] == recording['length']:
            # TODO: compare with current intels (if any)
            pass
        # TODO: gather more intel to categorize song
    return ret
    pass


def test_1():
    intel = {"Artist": "ratatat", "Title": "Loud pipe"}
    res = musicbrainz_api(intel)
    assert res['rbid'] == "69d8064a-1b6e-49af-933d-3e689b380af0"


def test_2():
    intel = {"Artist": "Lady Gaga", "Title": "Fire"}
    assert musicbrainz_api(intel)['rbid'] == "235f3984-2c07-4b18-8b4c-ccffde43a0de"


def test_multi():
    intels = [{"Artist": "ratatat", "Title": "Lou pipe"},
              {"Artist": "ratatat", "Title": "loud ppe"},
              {"Artist": "rattat", "Title": "Loud pipe"},
              {"Artist": "Neelix", "Title": "waterfall"},
              {"Artist": "Jay Hardway", "Title": "Bootcamp"},
              {"Artist": "Soundgarden", "Title": "Boot Camp"},
              {"Artist": "Scorpio", "Title": "Still loving you"}]
    results = []
    for intel in intels:
        results.append(musicbrainz_api(intel))
    for result in results:
        print(result)


if __name__ == "__main__":
    pass
