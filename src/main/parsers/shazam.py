"""
Created by: Mistayan
Project: Learning-Python
Creation date: 07/15/22
"""
import parse
import logging

import pydub.exceptions
from shazamio import Shazam
from lib.my_async import AsyncRequest, get_content
from lib.utils import save_thumbnail, get_file_name

log = logging.getLogger(__name__)


async def shazam_it(file) -> dict | None:
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
    # TODO: Test with different songs, to avoid errors (so far so good, but need more testings)
    return {"title": track['title'],
            "artist": track['subtitle'],
            "genres": track['genres'],
            "album": meta[0]['text'],
            "release_date": meta[2]['text'],
            "record_label": meta[1]['text'],
            "youtube_redirect": sections[2]['youtubeurl'] if len(sections) >= 3 and 'youtubeurl' in sections[2] else '',
            "similar_songs_url": sections[3]['url'] if len(sections) >= 4 and 'url' in sections[3] else '',
            "thumb_url": track['images']['coverart'] if 'images' in track and 'coverart' in track['images'] else '',
            "lyrics_url": sections[1]['url'] if len(sections) >= 2 and 'url' in sections[1] else '',
            "lyrics": get_lyrics(sections[1]['url']) if len(sections) >= 2 and 'url' in sections[1] else '',
            }
    # thu = AsyncRequest(intel['thumb_url'])
    # save_thumbnail(f"{intel['album']}", thu.get())


def get_lyrics(url: str, no_offset=True) -> dict | None:
    """
    get lyrics from shazam url
    returns a dict: { 'text': ['offset': timestamp, text] | [ text ] }
    """
    if not url or not isinstance(url, str):
        return
    lyrics_infos = AsyncRequest(get_content, url).get()  # expect json

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

    file_path = "../../tests/test_dir/music_without_tags.mp3"
    result = AsyncRequest(shazam_it, file_path).get()
    pprint.pprint(result)
    # pprint.pprint(get_lyrics(result['lyrics_url']), compact=False, indent=2)

