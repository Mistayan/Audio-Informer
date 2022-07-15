"""
Created by: 
Project: 
Creation date: 07/14/22
"""
from conf import api
import os
import json
import logging

from lib.utils import r_mkdir

logger = logging.getLogger(__name__)


def append_jsons(absolute_path, _json):
    with open(absolute_path, 'r') as fp:
        try:
            file_json: dict = json.load(fp)
            logger.debug(f"{file_json} already exists. appending infos")
            if len(file_json) <= api.MAX_HISTORY:
                return _json  # TODO: remove oldest instead
            return _json
        except json.JSONDecodeError as err:
            logger.warning(err)
            return _json


def save_json(_json, path, file_name):
    if not (path and len(path) and isinstance(path, str)):
        logger.error(f"invalid path: {path}")
        return
    r_mkdir(path)  # Ensure path asked is recursively checked
    absolute_path = path + file_name
    # TODO : implement append limit
    if os.path.exists(absolute_path):  # append to already existing files
        logger.info(f"{absolute_path} already exists. appending infos")
        _json = append_jsons(absolute_path, _json)
    fp = open(absolute_path, 'w')
    json.dump(_json, fp, indent=4)
    fp.close()
