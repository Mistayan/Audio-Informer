"""
Created by: Mistayan
Project: Audio-Informer
"""
import asyncio
import os

import logging
import re
import time
from typing import Final

import mutagen
from mutagen import MutagenError
from shazamio import Shazam, Serialize

from conf import api_conf as conf
from lib.my import format_htm

# Test's confs
# from parsers.musicbrainz import musicbrainz_api

logger: Final = logging.getLogger("MediaHolder")
logger.level = 3


class MediaHolder(object):
    """
    Holds a valid file, with path, name, media details and its fingerprint

    """
    intel: mutagen.FileType = None
    shazam = None

    def __init__(self, path: str, **kwargs):
        self.path = re.sub(r"\\+", "/", path)
        if not self.valid:
            self.logger.warning(f"Cannot open {self.path} => not a valid file")
            return
        logger.debug(f"Storing {path} as Media")
        self.name = self.path.split("/")[-1]
        try:
            logger.debug(f"Mutagen on Media")
            self.intel = self.mutagen_load()
        except MutagenError as err:
            logger.error(err)
            raise ChildProcessError(err)

    # ---------------------------------- Logic methods ---------------------------------- #

    def valid(self) -> bool:
        """returns True if file exists and has a valid file extension"""
        return os.path.isfile(self.path) and str(self.path).upper().endswith(conf.VALID_EXTENSIONS)

    # ---------------------------------- Outer methods ---------------------------------- #
    def mutagen_load(self) -> mutagen.FileType | None:
        try:
            logger.info(f"Opening with mutagen...{self.path} ")
            return mutagen.File(self.path)
        except MutagenError as err:
            logger.warning(f"failed to open: {err}")
            return None

    def calc_fingerprint(self):
        async def shazam_it():
            logger.debug(f"Shazaming : {self.path}")
            return await asyncio.gather(Shazam().recognize_song(self.path))

        loop = asyncio.new_event_loop()
        return loop.run_until_complete(shazam_it())

    def update_id3(self, outfile):  # from https://programtalk.com/python-examples/mutagen.File/
        """Update ID3 tags in outfile"""
        audio = mutagen.File(outfile, easy=True)
        audio.add_tags()
        audio["title"] = self.intel["Title"]
        audio["album"] = self.intel["Album"]
        audio["artist"] = self.intel["Artist"]
        audio["performer"] = self.intel["AlbumArtist"]
        audio["composer"] = self.intel["Composer"]
        audio["genre"] = self.intel["Genre"]
        audio["date"] = str(self.intel["Year"])
        audio["tracknumber"] = str(self.intel["TrackNumber"])
        audio["discnumber"] = str(self.intel["DiscNumber"])
        audio["compilation"] = str(self.intel["Compilation"])
        audio.save()

    # ---------------------------------- Magic functions ---------------------------------- #

    def __str__(self):
        return self.name

    def __await__(self):
        # if asyncio.coroutines.iscoroutine(self.shazam):
        #     asyncio.coroutines.
        pass

    def __repr__(self):
        return [self.intel.__repr__(), self.shazam] \
            if self.intel and self.shazam \
            else self.intel if self.intel \
            else ''


# ---------------------------------- Test Class ---------------------------------- #
if __name__ == "__main__":
    from pprint import pprint

    file = "C:/Users/GAMER/Desktop/python-learnin/Audio-Informer/tests/test_dir/second_rec_test/08. Crescent.flac"
    s = time.perf_counter()
    print("Starting ")
    media = MediaHolder(file)
    print(media.intel)
    # print(musicbrainz_api(media.intel))
    pprint(media, indent=4)
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
