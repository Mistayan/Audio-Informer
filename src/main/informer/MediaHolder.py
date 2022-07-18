"""
Created by: Mistayan
Project: Audio-Informer
"""
import logging
import os
import re
import time

import mutagen

from conf import api as conf
from lib.my_async import AsyncRequest
from lib.utils import get_file_name
from parsers.musicbrainz import musicbrainz_api
from parsers.shazam import shazam_it, get_shazam_lyrics
logger = logging.getLogger(__name__)


class MediaHolder:
    """
    Holds a valid file, with path, name, media details and its fingerprint

    """

    def __init__(self, path: str, callback=None, **kwargs):
        if not self.is_valid(path):
            logger.error(f"{path} => not a valid file")
            return
        try:
            self.path = re.sub(r"\\+", "/", path)
            self.name = get_file_name(self.path)
        except IndexError:
            logger.error(f"{self.path} => not a valid path")
            return
        self.intel = None
        self.future = None
        self.shazam = None
        self.musicbrainz = None
        self.additional = None
        self.lyrics = None

        self.shazam = AsyncRequest(shazam_it, self.path)
        self.shazam.add_done_callback(callback)
        self.get_mutagen()
        # TODO: ensure MPEG 'TABL', 'TIT2', 'TPE1', TCON to be loaded as classic intel
        # TODO: ensure FLAC 'TITLE', 'ALBUMARTIST' > 'ARTIST', 'DATE', 'ALBUM', 'GENRE', 'TRACKNUMUBER', 'TOTALTRACKS'

        if not (self.intel or self.shazam):
            logger.warning(f"failed to open : {self.name} ")
            return
        logger.info(f"Storing {self.name} as Media")

    # ---------------------------------- Logic methods ---------------------------------- #
    @staticmethod
    def is_valid(path: str) -> bool:
        """returns True if file can be theoretically loaded as media"""
        return os.path.isfile(path) and str(path).upper().endswith(conf.VALID_EXTENSIONS)

    # ---------------------------------- Outer methods ---------------------------------- #
    # -------------------------- methods that should be used  --------------------------- #
    def get_mutagen(self) -> mutagen.FileType | None:
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
        if isinstance(self.shazam, AsyncRequest):
            self.shazam = self.shazam.get()
        return self.shazam

    def get_musicbrainz(self):
        if not self.musicbrainz:
            self.musicbrainz = musicbrainz_api(self.get_shazam() or self.get_mutagen())
        return self.musicbrainz

    def get_lyrics(self):
        if not self.lyrics:
            self.lyrics = get_shazam_lyrics(self.get_shazam()['lyrics_url']) if self.shazam else None
        return  self.lyrics

    def update_id3(self):  # from https://programtalk.com/python-examples/mutagen.File/
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
        return self.name

    def __repr__(self):
        return {
            "name": self.name,
            "mutagen": self.intel,
            "shazam": self.get_shazam(),
            "lyrics": self.get_lyrics(),
            "musicbrainz":  self.get_musicbrainz(),
            # TODO: Implement more researches for :
            # better genders analysis
            #
        }


# ---------------------------------- Test Class ---------------------------------- #
def test_class(file="../../tests/test_dir/music_without_tags.mp3"):
    import pprint
    import time
    print()
    s = time.perf_counter()
    media = MediaHolder(file)
    if media:
        pprint.pprint(media.__repr__())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")


def test_rubbish():
    media = MediaHolder("../../tests/test_dir/dumb_folder/15.mp4").__repr__()
    for field in media:
        assert media[field] is None

if __name__ == "__main__":
    pass
