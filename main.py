import logging
import os
import pprint
import re
import sys
import time

from conf import api as conf
from informer.MediaHolder import MediaHolder

logger = logging.getLogger(__name__)


def print_help(msg: str = None) -> None:
    """print help (optional: with an additional message) and exits with status -1 (Error)"""
    print(f"Hi, please enter a valid Audio File {conf.VALID_EXTENSIONS}")
    print(f"You may enter multiples files and / or include a folder")
    print(f"{msg}")
    exit(-1)


def load_files(current_dir: str) -> list:
    """
    :param current_dir: directory to scan for valid audio files
    :return list:
    """
    ret = []
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            abs_file_path = os.path.join(root, file)
            # File exists and has valid extension
            if MediaHolder.is_valid(abs_file_path):
                print(abs_file_path)
                ret.append(MediaHolder(abs_file_path))

    return ret


def parse_main_args(args: list) -> list:
    """
    :param args: list of program's arguments
    :return : a list of every valid files found in args, loaded in a MediaHolder
     File: [valid_file]
     Path: [[valid_files_in_dir]]
    """
    if len(args) <= 1:
        print_help()

    path = os.getcwd()  # Current_workdir
    ret = []
    for arg in args:
        abs_path = re.sub(r"\\+", "/", os.path.join(path, arg))
        if not os.path.exists(abs_path):
            logger.warning(f"{abs_path}  : does not exists")
            return ret
        elif os.path.isdir(abs_path):  # if path is a folder
            ret = load_files(abs_path)
        elif MediaHolder.is_valid(abs_path):
            ret.append(MediaHolder(abs_path))
    return ret


if __name__ == '__main__':
    # list compatible files in folder
    # else append single file to MediaHolder_list (if compatible)
    s = time.perf_counter()
    if len(sys.argv) >= 2 and re.match(r"", sys.argv[0].split("\\")[-1]):  # python main args
        medias = parse_main_args(sys.argv)
    else:
        print("no path/media chosen. Executing on src/tests/test_dir")
        medias = parse_main_args([__name__, "src/tests/test_dir"])
    print(f"files found , loaded, and researches have started in {time.perf_counter() - s:0.5f} seconds.")
    # media: MediaHolder
    for media in medias:
        print(media.__repr__())
    # TODO: next step, compare found intel and ask user to validate.
    print(f"{__file__} executed in {time.perf_counter() - s:0.3f} seconds. ({len(medias)} files processed)")
