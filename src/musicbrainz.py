"""
Created by: Mistayan
Project: Audio-Informer
Creation date: 07/10/22
"""
import logging
from easy_async import AsyncRequest
from utils import save_json, get_content


def get_intel(intel):
    # shazam:  only one value per field {'label': 'name'}
    # mutagen:  may have multiple values {'label': ['name'(, ...)]}
    return intel if isinstance(intel, str) \
        else intel[0] if isinstance(intel, list) and len(intel) == 1 \
        else None


def musicbrainz_api(intel: dict, save=True) -> dict | None:
    """uses intel['artist' | 'title' | 'album']"""
    log = logging.getLogger(__name__)
    if not intel or not isinstance(intel, dict) or intel == {}:
        log.info(f"Could not request musicbrainz. No datas")
        return
    # mutagen/user_input integration
    site = "https://musicbrainz.org/ws/2/recording?query="
    artist = get_intel(intel['artist']) if 'artist' in intel else None
    title = get_intel(intel['title']) if 'title' in intel else None
    album = get_intel(intel['album']) if 'album' in intel else None
    query = f"\"{artist}\""
    search_factors = "&limit=1&fmt=json"
    request = AsyncRequest(get_content, site, query + f"+AND+\"{title}\"{search_factors}")
    request2 = AsyncRequest(get_content, site, query + f"+AND+\"{album}\"{search_factors}")
    _json = request.get().get('recordings') if request.get() else None
    compare_json = request2.get().get('recordings') if request2.get() else None

    if save:
        save_json(_json, title + ".mb", artist, album) if _json else None
        save_json(compare_json, title + ".mb_compare", artist, album) if compare_json else None
        log.info(f"{artist}/{title} :  saved")

    ret = {}
    try:
        ret.setdefault("rbid", _json['recordings'][0]['id'])  # lazy_mode = True
    except (IndexError, KeyError, TypeError):  # No recordings associated with the search
        return None
    for recording in _json['recordings']:
        log.debug(recording)
        if hasattr(intel, 'length') and intel['length'] == recording['length']:
            # TODO: compare with current intel (if any)
            pass
        # TODO: gather more intel to categorize song for more accurate recognitions
    return ret if ret != {} else None
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
