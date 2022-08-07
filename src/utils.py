"""
Created by: Mistayan
Project: Learning-Python
Creation date: 07/10/22
"""
import json
import logging
import os
import re
import aiohttp
import brotli  # Useful for br pages (more and more common on the web)
import yarl
import conf
log = logging.getLogger(__name__)


def get_file_name(path: str) -> str:
    """ :returns:  "file.ext" from given path """
    if not path or type(path) is not str:
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
                log.debug(f"making dir : {sub}")
                os.mkdir(root)
    except (IndexError, ReferenceError, TypeError):
        raise


def read_json(file: str) -> list | None:
    """ :returns: json formatted to list, for easier iterations """
    with open(file, 'r') as fp:
        try:
            file_json: dict = json.load(fp)
            if isinstance(file_json, list):
                return file_json
            return [file_json]
        except json.JSONDecodeError as err:
            log.error(f"could not decode previously saved json : {err}")
            return None


def save_json(_json: dict, file_name: str, group: str = None, album: str = None) -> None:
    """ save _json as dict to ./Results/group/album/file_name"""
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
    log.info(uac)


# ____________________________________________________ #
# __________________ ASYNC FUNCTIONS _________________ #
# ____________________________________________________ #
async def get_content(url: str, query: str = '') -> (dict | str | bytes | None):
    """
    Generate an async session requesting url + query
    Returns a StreamReader, according to current response formatting
    """
    if not url:
        return
    target = yarl.URL(url + query)  # proper request formatting
    log.info(f"request : {target}")
    try:
        async with aiohttp.ClientSession() as session:  # Start a new session for current thread
            async with session.get(target) as response:  # Get session's content
                # if not (response.host != target.host or "www." + response.host != target.host):
                #     raise ValueError(f"{response.host} not {target.host}")
                if not response.status == 200:
                    return
                else:
                    log.debug(response.content_type)
                    match response.content_type:
                        case 'application/json':
                            ret: dict = await response.json()
                        case 'text/html':
                            ret: str = await response.text()
                        case _:
                            ret: bytes = await response.content.read()
        if response.status == 200:
            log.debug(f"result for {target.human_repr()}: {ret if not isinstance(ret, bytes) else 'bytes.'}")
    except aiohttp.ClientConnectorError:
        log.debug(f"Connection not established with {target.human_repr()}")
        ret = None
    return ret


async def save_thumbnail(group: str, album: str, url) -> None:
    """ Async so it fastens the program, since image acquisition may take a while """
    group = group if group else 'Unknown'
    album = album if album else 'Unknown'
    target = re.sub(r"[: |^?&#;<>,%]|_+", "_", f"./Results/{group}/{album}/")
    r_mkdir(target)
    abs_path = re.sub(r"[: |^?&<>#;,%]|_+", "_", target + "thumbnail.png")
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
