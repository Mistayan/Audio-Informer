"""
Created by: Mistayan
Project: Audio-Informer
Creation date: 07/10/22
"""
import logging
import time

import conf.api
from lib.my_async import AsyncRequest, get_content
from lib.my_json import save_json
from lib.utils import format_htm


def get_intel(intel):
    return intel if isinstance(intel, str) \
        else intel[0] if isinstance(intel, list) and len(intel) == 1 \
        else None


def musicbrainz_api(intel: dict, save=False) -> dict | None:
    """uses intel['artist' | 'title' | 'album']"""
    start = time.time()
    log = logging.getLogger(__name__)
    if not intel or not isinstance(intel, dict) or intel == {}:
        log.info(f"Could not request musicbrainz. No datas")
        return
    # mutagen/user_input integration
    query = f"\"{format_htm(get_intel(intel['artist']))}\"" if 'artist' in intel else ''
    query += f"+AND+\"{format_htm(get_intel(intel['title']))}\"" if 'title' in intel else ''
    query += f"+AND+{format_htm(get_intel(intel['album']))}" if 'album' in intel else ''
    query += "&limit=5&fmt=json"  # json <3
    log.debug(f"@{time.time() - start} : {query}")
    _json = AsyncRequest(get_content, "https://musicbrainz.org/ws/2/recording?query=", query).get()

    if save:
        artist = get_intel(intel['artist']) if 'artist' in intel else ''
        title = get_intel(intel['title']) if 'title' in intel else ''
        # TODO: make target_dir dynamic (after global integration)
        target_dir = f"./json/{artist}/"
        file_name = f"{title}.json"
        save_json(_json, target_dir, file_name) if conf.api.DEBUG else None
        log.debug(f"{__name__} @{time.time() - start} : json saved")

    ret = {}
    try:
        ret.setdefault("rbid", _json['recordings'][0]['id'])  # lazy_mode = True
    except IndexError or KeyError:  # No recordings associated with the search
        return None
    for recording in _json['recordings']:
        log.debug(recording)
        if hasattr(intel, 'length') and intel['length'] == recording['length']:
            # TODO: compare with current intels (if any)
            pass
        # TODO: gather more intel to categorize song for more accurate recognitions
    return ret
    pass


# ____________________________________________________ #
# ______________________ TESTS _______________________ #
# ____________________________________________________ #
def test_1():
    print()
    intel = {"artist": "Lady Gaga", "title": "Feed My Pop Heart"}
    assert musicbrainz_api(intel)['rbid'] == "0be3e96d-4e55-4f42-9367-b72a882aa4e7"


def test_2():
    print()
    intel = {"artist": "ratatat", "title": "Loud pipe", "album": "Classics"}
    res = musicbrainz_api(intel)
    assert res['rbid'] == "69d8064a-1b6e-49af-933d-3e689b380af0"


def test_multi():
    print()
    intels = [{"artist": "ratatat", "title": "Lou pipe"},
              {"artist": "ratatat", "title": "loud ppe"},  # None (Bad request)
              {"artist": "rattat", "title": "Loud pipe"},  # None (Bad request)
              {"artist": "Neelix", "title": "waterfall"},
              {"artist": "Jay Hardway", "title": "Bootcamp"},
              {"artist": "Soundgarden", "title": "Boot Camp"},
              {"artist": "Scorpions", "title": "Still loving you"}]
    res = [musicbrainz_api(intel) for intel in intels]
    assert res[0]['rbid'] == "69d8064a-1b6e-49af-933d-3e689b380af0"
    assert res[1] is None
    assert res[2] is None
    assert res[3]['rbid'] == "7989fd97-7678-42a6-95bb-c0b3cfefa298"
    assert res[4]['rbid'] == "2f9b538f-d34c-49d7-a8bc-ceccbfadc1e2"
    assert res[5]['rbid'] == "994b50c6-eed8-4b0a-88d6-6c84d05fd2b4"
    assert res[6]['rbid'] == "f4c8a80f-febf-4d66-a70e-62f177d6a081"


if __name__ == "__main__":
    pass
