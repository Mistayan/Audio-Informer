"""
Created by: Mistayan
Project: Audio-Informer
"""

import logging
from types import MappingProxyType
from typing import Final

MB_URLS: Final = {
    # https://musicbrainz.org/search?query="lady+gaga"+AND+"shallow"&type=release&limit=25&method=advanced
    "search": "https://musicbrainz.org/search?query=\"{artist}\"+AND+\"{song}\"&type=release&limit=2",

}
MB_SEARCH_ELEMS: Final = {
    "mbid": "/release/{0}\"",
    "cover": "/release/{0}/cover-art",
    "country": "abbr title=\"[{0}]\"",
    "release_date": "class=\"release-date\">{0}</",
    "label_id": "/label/{0}\"",
}

VERBOSITY_COUNT_TO_LEVEL: Final = MappingProxyType({
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
})
DEBUG: Final = 3
VALID_EXTENSIONS: Final = tuple([".WAV", ".MP3", ".OGG", ".FLAC", ".MP4",
                                 ".AIFF", ".AAC", ".C3", ".SMF", ".TAK", ".DSL"])
REC_LIMIT: Final = 5
