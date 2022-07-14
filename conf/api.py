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
VERBOSITY_COUNT_TO_LEVEL: Final = MappingProxyType({
    0: "ERROR",
    1: "WARNING",
    2: "INFO",
    3: "DEBUG",
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
            'propagate': True if DEBUG == "DEBUG" else False
        },
    },
    "formatters": {
        "std_out": {
            "format": "%(levelname)s## %(asctime)s ## (Process Details: (%(process)d, %(processName)s), Thread Details:"
                      " (%(thread)d, %(threadName)s))\n %(module)s.%(funcName)s : %(lineno)d : Log : %(message)s\n",
            "datefmt": "%d-%m-%Y %H:%M:%S"
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
