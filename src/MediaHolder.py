"""
Created by: Mistayan
Project: Audio-Informer
"""
import logging
import multiprocessing
import os
import re
import mutagen
import time
import asyncio
import logging

import parse

from utils import get_content
import conf
from easy_async import AsyncRequest
from utils import get_file_name
from src.musicbrainz import musicbrainz_api
from src.shazam import shazam_it
logger = logging.getLogger(__name__)


class MediaHolder:
    """
    Holds a valid file, with path, name, media details and its fingerprint

    How to use:
    if MediaHolder.is_valid(file):
        media = MediaHolder(file)
        print(media.get_shazam())
        print(media.get_mutagen())
        print(media.get_musicbrainz())
        print(media.__repr__())  # will user all search methods at once and display gathered intel
    """
    name = None
    path = None
    musicbrainz = None
    repr = None
    intel = None
    shazam = None

    def __init__(self, path: str, *args, **kwargs):
        if not self.is_valid(path):
            logger.error(f"{path} => not a valid file")
            return
        try:
            self.path = re.sub(r"\\+", "/", path)
            self.name = get_file_name(self.path)
        except IndexError:
            logger.error(f"{self.path} => not a valid path")
            return
        cp = multiprocessing.current_process()
        pp = multiprocessing.parent_process()
        if pp and not cp.is_alive():  # Multiprocessing support Start
            logger.debug(f"{cp.pid} Run")
            cp.run()
        self.shazam = AsyncRequest(shazam_it, self.path)
        self.get_mutagen()
        # TODO: ensure MPEG 'TABL', 'TIT2', 'TPE1', TCON to be loaded as classic intel
        # TODO: ensure FLAC 'TITLE', 'ALBUMARTIST' > 'ARTIST', 'DATE', 'ALBUM', 'GENRE', 'TRACKNUMUBER', 'TOTALTRACKS'

        if not (self.intel or self.shazam):
            logger.warning(f"failed to open : {self.name} ")
            return
        logger.info(f"Storing {self.name} as Media")
        if pp and cp.is_alive():  # Multiprocessing support
            self.__repr__()

    # ---------------------------------- Logic methods ---------------------------------- #
    @staticmethod
    def is_valid(path: str) -> bool:
        """returns True if file can be theoretically loaded as media"""
        return os.path.isfile(path) and str(path).upper().endswith(conf.VALID_EXTENSIONS)

    # ---------------------------------- Outer methods ---------------------------------- #
    # -------------------------- methods that should be used  --------------------------- #
    def get_mutagen(self) -> mutagen.FileType | None:
        """ uses mutagen to gather datas from file"""
        if not self.intel:
            try:
                self.intel = mutagen.File(self.path, easy=True)
                if self.intel:
                    logger.info(f"opened successfully : {self.name} ")
                    logger.debug(f"results: {self.intel}")
            except mutagen.MutagenError as err:
                logger.warning(f"failed to open: {err}")
                return
        return self.intel

    def get_shazam(self) -> dict | None:
        """ uses shazam_api to collect datas"""
        if isinstance(self.shazam, AsyncRequest):
            self.shazam = self.shazam.get()
        return self.shazam

    def get_musicbrainz(self):
        """ uses musicbrainz_api to collect datas"""
        if not self.musicbrainz and self.get_shazam() or self.get_mutagen():
            self.musicbrainz = musicbrainz_api(self.get_shazam() or self.get_mutagen())
        return self.musicbrainz

    def save(self):
        """ WIP """
        pass
        # save_json(self.__repr__(), self.name)
        # Compare datas
        # save most valuable datas in intel
        # self.update_tags()

    def update_tags(self):  # from https://programtalk.com/python-examples/mutagen.File/
        """Update ID3 tags in outfile"""
        # TODO: evaluate gathered intel to store in-file
        audio = mutagen.File(self.path, easy=True)
        audio.add_tags()
        audio["title"] = self.intel["title"]
        audio["album"] = self.intel["album"]
        audio["artist"] = self.intel["artist"]
        audio["performer"] = self.intel["albumArtist"]
        audio["composer"] = self.intel["composer"]
        audio["genre"] = self.intel["genre"]
        audio["date"] = str(self.intel["year"])
        audio["tracknumber"] = str(self.intel["trackNumber"])
        audio["discnumber"] = str(self.intel["discNumber"])
        audio["compilation"] = str(self.intel["compilation"])
        audio.save()

    # ---------------------------------- Magic functions ---------------------------------- #
    def __str__(self):
        return str(self.__repr__())

    def __repr__(self) -> dict:
        if not self.repr:
            self.shazam.__await__() if self.shazam else None
            self.repr = {
                "name": self.name,
                "mutagen": self.intel,
                "shazam": self.get_shazam(),  # includes lyrics: { text,  writers } found on shazam
                "musicbrainz":  self.get_musicbrainz(),
                # TODO: Implement more researches for :
                # better genders analysis
                #
            }
        return self.repr


# ---------------------------------- Test Class ---------------------------------- #
def test_class(file="../tests/test_dir/music_without_tags.mp3"):
    import pprint
    import time
    print()
    s = time.perf_counter()
    media = MediaHolder(file)
    if media:
        pprint.pprint(media.__repr__())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")


if __name__ == "__main__":
    test_class()
