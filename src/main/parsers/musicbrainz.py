"""
Created by: 
Project: 
Creation date: 07/10/22
"""
import json
import logging
import os.path
import pprint

from lib.async_testings import AsyncRequest
import requests_html  # Special html parsing tool
from lib.my import format_htm

log = logging.getLogger(__name__)


def musicbrainz_api(intel: dict):
    intels = intel
    if not intels or not intels['Artist'] or not intels['Title']:
        log.warning("Could not request musicbrainz. Insuffisant datas")
        return
    session = requests_html.HTMLSession()
    absolute_link = f"https://musicbrainz.org/ws/2/recording?query=" \
                    f"\"{format_htm(intels['Artist'])}\"+AND+" \
                    f"\"{format_htm(intels['Title'])}\"&limit=5&fmt=json"
    print(absolute_link)
    with session.get(absolute_link) as r:
        print(r.status_code)
        ret = {}
        if r and r.status_code == 200:  # On search page
            target_dir = f"C:/Users/GAMER/Desktop/python-learnin/Audio-Informer/Results/json/{intels['Artist']}/"
            if not os.path.isdir(target_dir):
                os.mkdir(target_dir)
            target_file = f"{intels['Title']}.json"
            fp = open(target_dir + target_file, 'w')
            pprint.pprint(r.json(), fp, compact=False)
            fp.close()

            ret.setdefault("record_bid", r.json()['recordings'])
            for recording in r.json()['recordings']:
                if hasattr(intels, 'length') and intels['length'] == recording['length']:



    #         result_mbid = parse.search("/release/{0}\"", soup) or parse.search("/release/{0}/\"", html)
    #         if result_mbid:
    #             mbid = result_mbid[0]
    return ret
    pass


def test_1():
    intel = {
        "Artist": "ratatat",
        "Title": "Loud pipe"
    }
    res = musicbrainz_api(intel)
    assert "b57a9fe6-3087-41d7-baa7-3b0af00f1589" == res['mbid']


def test_2():
    intel = {
        "Artist": "Lady Gaga",
        "Title": "Fire"
    }
    assert '235f3984-2c07-4b18-8b4c-ccffde43a0de' == musicbrainz_api(intel)


if __name__ == "__main__":
    pass
