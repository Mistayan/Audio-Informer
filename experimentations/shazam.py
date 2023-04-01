"""
Created by: Mistayan
Project: Learning-Python
Creation date: 07/15/22
"""
import os.path

import parse
import logging

import pydub.exceptions
from shazamio import Shazam
from lib.my_async import AsyncRequest, get_content
# from lib.utils import save_thumbnail

log = logging.getLogger(__name__)


async def shazam_it(file_path: str) -> dict | None:
    if not file_path or not os.path.exists(file_path):
        return
    try:
        name = file_path.split('/')[-1]
    except IndexError:
        name = file_path
    try:
        log.debug(f"trying to shazam : {name}")
        async with aiofiles.open('filename', mode='r') as f:
            contents = await f.read()
        shazam = await Shazam().recognize_song(contents)
    except pydub.exceptions.PydubException:
        shazam = None
    if not shazam:
        log.info(f"shazam failed on : {name}")
        return
    log.debug(f"shazam succeeded on : {name}")

    track = shazam['track']
    sections = track['sections']
    meta = sections[0]['metadata']
    # TODO: Test with different songs, to avoid errors (so far so good, but need more testings)
    return {"title": track['title'],
            "group_name": track['subtitle'],
            "genres": track['genres'],
            "album": meta[0]['text'],
            "release_date": meta[2]['text'],
            "record_label": meta[1]['text'],
            "youtube_redirect": sections[2]['youtubeurl'] if len(sections) >= 3 and 'youtubeurl' in sections[2] else '',
            "similar_songs_url": sections[3]['url'] if len(sections) >= 4 and 'url' in sections[3] else '',
            "thumb_url": track['images']['coverart'] if 'images' in track and 'coverart' in track['images'] else '',
            "lyrics_url": sections[1]['url'] if len(sections) >= 2 and 'url' in sections[1] else '',
            }
    # thu = AsyncRequest(intel['thumb_url'])
    # save_thumbnail(f"{intel['album']}", thu.get())


def get_lyrics(url: str) -> dict | None:
    if not url or not isinstance(url, str):
        return
    lyrics_infos = AsyncRequest(get_content, url).get()

    if not lyrics_infos:
        return
    pattern = parse.Parser("): {0}\n")
    wr_infos = pattern.search(lyrics_infos['footer'])
    if wr_infos:
        if wr_infos[0].find(","):
            writers = wr_infos[0].split(", ")
        else:
            writers = wr_infos[0]
    else:
        writers = ''

    return {"writers": writers,
            "lyrics": lyrics_infos['syncedtext']}


if __name__ == "__main__":
    import pprint

    file_path = "../../tests/test_dir/music_without_tags(Shpongle - Dorset Perception).mp3"
    result = AsyncRequest(shazam_it, file_path).get()
    pprint.pprint(result)
    pprint.pprint(get_lyrics(result), compact=False, indent=2)

