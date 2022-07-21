"""
Created by: Mistayan
Project: Learning-Python
Creation date: 07/10/22
"""
import json
import logging
import os
import re

from conf import api
from lib.my_async import get_content

logger = logging.getLogger(__name__)
logger.setLevel(api.DEBUG)
# Clean_string & format_htm replaced by YARL


def get_file_name(path):
    if not path:
        return path
    try:
        re.sub(r"\\+", '/', path)
        return path.split('/')[-1]
    except IndexError:
        raise FileNotFoundError(path)


def r_mkdir(path: str):
    """
    Requires an absolute path, or curent path './'
    recursively create folders to the asked path.
    use with caution...
    """
    try:
        if path[0] == '.' and path[1] == '/':
            path = path.replace('.', os.getcwd())
        path = re.sub(r"\\+", '/', path).replace(' ', '_')  # ensure friendly / readable path
        root = path.split(":/")[0] + ":/"
        if not os.path.exists(root):
            raise ReferenceError(f"Requires an absolute (or current './') path: {root}")
        for sub in path.split("/")[1:]:
            root += re.sub(r"[:|^?&#;,%]|_+", "_", sub + '/')
            if not os.path.isdir(sub) and not os.path.exists(root):
                logger.debug(f"making dir : {sub}")
                os.mkdir(root)
    except (IndexError, ReferenceError, TypeError):
        raise


def read_json(file: str) -> list | None:
    with open(file, 'r') as fp:
        try:
            file_json: dict = json.load(fp)
            if isinstance(file_json, list):
                return file_json
            return [file_json]
        except json.JSONDecodeError as err:
            logger.warning(f"could not decode previously saved json : {err}")
            return None


def save_json(_json: dict, file_name: str, group: str = None, album: str = None) -> None:
    if not (file_name or _json):
        return
    group = group if group else 'Unknown'
    album = album if album else 'Unknown'
    dir = f"./Results/{group}/{album}/"
    abs_path = re.sub(r"[:|^?&#;,% ]|_+", "_", dir + f"{file_name}.json")
    r_mkdir(dir)  # Ensure path asked is recursively checked
    # TODO: implement append limit
    uac = f"Saving {abs_path}. "
    if os.path.exists(abs_path):  # append to already existing files
        uac += "Already exists. "
        file_list = read_json(abs_path)
        to_save = [_json]
        if file_list:
            for _dict in file_list:
                to_save.append(_dict) if _dict not in to_save else None
        if len(to_save) == 1:  # Cancel
            to_save = to_save[0]
    else:
        uac += "Creating json dump"
        to_save = _json
    with open(abs_path, 'w') as fp:
        json.dump(to_save, fp, indent=4)
    logger.info(uac)


async def save_thumbnail(group: str, album: str, url) -> None:
    target = f"./Results/{group}/{album}/".replace(' ', '_')
    abs_path = re.sub(r"[:|^?&#;,%]|_+", "_", target + "thumbnail.png")
    r_mkdir(target)
    if os.path.exists(abs_path):
        return
    with open(abs_path, "w+b") as fp:
        fp.write(await get_content(url))
    return


# ____________________________________________________ #
# _______________________ TESTS ______________________ #
# ____________________________________________________ #
if __name__ == "__main__":
    pass
