"""
Created by: Mistayan
Project: Audio-Informer
"""

import logging
from types import MappingProxyType
from typing import Final

VERBOSITY_COUNT_TO_LEVEL: Final = MappingProxyType({
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
})
DEBUG: Final = VERBOSITY_COUNT_TO_LEVEL[0]
VALID_EXTENSIONS: Final = tuple([".WAV", ".MP3", ".OGG", ".FLAC", ".MP4",
                                 ".AIFF", ".AAC", ".C3", ".SMF", ".TAK", ".DSL"])
REC_LIMIT: Final = 5
