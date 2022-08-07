"""
Created by: Mistayan
Project: Learning-Python
Creation date: 07/15/22
"""

import parse
import logging

import pydub.exceptions
from shazamio import Shazam
from easy_async import AsyncRequest
from utils import save_thumbnail, get_file_name, save_json, get_content

log = logging.getLogger(__name__)


async def shazam_it(file, save=True) -> dict | None:
    """
    async shazam the file provided
    gather any useful intel and sends back a dict
    """
    name = get_file_name(file)
    try:
        log.debug(f"trying to shazam : {name}")
        shazam = await Shazam().recognize_song(file)
    except pydub.exceptions.PydubException:
        shazam = None
    if not shazam:
        log.info(f"shazam failed on : {name}")
        return
    try:
        track = shazam['track']
    except KeyError:  # No results
        return
    log.debug(f"shazam succeeded on : {name}")
    sections = track['sections']
    meta = sections[0]['metadata']
    thumb_url = track['images']['coverart'] if 'images' in track and 'coverart' in track['images'] else None

    intel = {"title": track.get('title'),
             "artist": track.get('subtitle'),
             "genres": track.get('genres'),
             "album": meta[0].get('text'),
             "release_date": meta[2].get('text'),
             "record_label": meta[1].get('text'),
             "youtube_redirect": sections[2].get('youtubeurl') if len(sections) >= 3 else None,
             "similar_songs_url": sections[3].get('url') if len(sections) >= 4 else None,
             "lyrics_url": sections[1].get('url') if len(sections) >= 2 else None,
             "lyrics": await get_lyrics(sections[1].get('url')) if len(sections) >= 2 else None,
             }
    if save:
        await save_thumbnail(intel['artist'], intel['album'], thumb_url)
        save_json(intel, intel['title'] + ".szm", intel['artist'], intel['album'])
    return intel


async def get_lyrics(url: str, no_offset=True) -> dict | None:
    """
    get lyrics from shazam url
    returns a dict: { 'text': ['offset': timestamp, text] | [ text ] }
    """
    if not url or not isinstance(url, str):
        return
    lyrics_infos = await get_content(url)  # expect json

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
            "text":
                [offset['text'] for offset in lyrics_infos['syncedtext']]
                if no_offset else lyrics_infos['syncedtext']}


if __name__ == "__main__":
    import pprint

    file_path = "../src/tests/test_dir/music_without_tags.mp3"
    result = AsyncRequest(shazam_it, file_path).get()
    pprint.pprint(result)
    # pprint.pprint(get_lyrics(result['lyrics_url']), compact=False, indent=2)
