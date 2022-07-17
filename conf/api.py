"""
Created by: Mistayan
Project: Audio-Informer
"""

from types import MappingProxyType
from typing import Final
from logging import config

# ____________________________________________________ #
# _______________ LOGGER CONFIGURATIONS ______________ #
# ____________________________________________________ #
PROPAGATE = False
VERBOSITY_COUNT_TO_LEVEL: Final = MappingProxyType({
    0: "CRITICAL",
    1: "ERROR",
    2: "WARNING",
    3: "INFO",
    4: "DEBUG",
})
DEBUG: Final = VERBOSITY_COUNT_TO_LEVEL[2]  # Prod config
log_config: Final = {
    "version": 1,
    "root": {
        "handlers": ["console"],
        "level": DEBUG
    },
    'handlers': {
        'console': {
            'level': DEBUG,
            'class': 'logging.StreamHandler',
            'formatter': 'std_out',
        }
    },
    'loggers': {
        'myapp': {
            'handlers': ['console'],
            'level': DEBUG,
            'propagate': True if DEBUG == "DEBUG" and PROPAGATE else False
        },
    },
    "formatters": {
        "std_out": {
            "format": "%(levelname)s## %(asctime)s ##  %(module)s.%(funcName)s@%(lineno)d "
                      "[(%(process)d, %(processName)s),(%(thread)d, %(threadName)s)]\t"
                      "==> :  %(message)s",
            "datefmt": "%d-%m %H:%M:%S"
        }
    },
}
config.dictConfig(log_config)

# ____________________________________________________ #
# ____________ APPLICATION CONFIGURATIONS ____________ #
# ____________________________________________________ #
VALID_EXTENSIONS: Final = tuple([".WAV", ".MP3", ".OGG", ".FLAC", ".MP4",
                                 ".AIFF", ".AAC", ".C3", ".SMF", ".TAK", ".DSL"])  # Files types mutagen can open
REC_LIMIT = 5  # Applies for folders discovery
MAX_HISTORY = 6  # Applies for musics search history and results
