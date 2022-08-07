import logging
import os
import re
import sys
import time
from multiprocessing import Pool

from src import conf
from src.MediaHolder import MediaHolder

logger = logging.getLogger(__name__)


def print_help(msg: str = None) -> None:
    """print help (optional: with an additional message) and exits with status -1 (Error)"""
    print(f"Hi, please enter a valid Audio File {conf.VALID_EXTENSIONS}")
    print(f"You may enter multiples files and / or include a folder")
    print(f"{msg}")
    exit(-1)


def run_multi_process(files):
    """ Start the process of finding metadata as fast as we can"""
    with Pool(processes=conf.MAX_WORKERS) as pool:
        return pool.map_async(MediaHolder, files).get()


def run_one_process(files):
    """ Start the process of finding metadata file by file"""
    return [MediaHolder(file) for file in files]


def find_files(current_dir: str) -> list:
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
                ret.append(abs_file_path)
    return ret


def parse_main_args(args: list) -> list:
    """
        :param args: list of program's arguments
        :return :
        a list of every valid files found in args.
        File: [valid_file]
        Path: [valid_files in arg]
        multiple args: [valid file(s), valid_files_in_folder(s)]
    """
    if len(args) <= 0:
        print_help()
    ret = []
    path = os.getcwd()  # Current_workdir
    for arg in args:
        # friendly path formatting of an absolute path
        abs_path = re.sub(r"\\+", "/", arg if os.path.isabs(arg) else os.path.join(path, arg))
        if not os.path.exists(abs_path):
            logger.warning(f"{abs_path}  : does not exists")
            return []
        elif os.path.isdir(abs_path):
            return parse_main_args(find_files(abs_path))
        elif MediaHolder.is_valid(abs_path):
            ret.append(abs_path)
    return ret


if __name__ == '__main__':
    # list compatible files in folder
    # else append single file to MediaHolder_list (if compatible)
    s = time.perf_counter()
    if len(sys.argv) >= 2 and re.match(r"", sys.argv[0].split("\\")[-1]):  # python main args
        files = parse_main_args(sys.argv[1:])
    else:
        print("no path/media chosen. Executing on tests/test_dir")
        files = parse_main_args(["tests/test_dir"])
    print(files)
    # medias = run_one_process(files)  # You can compare speed by un-commenting this line
    print(f"files found , loaded, and researches have started in {time.perf_counter() - s:0.5f} seconds.")
    medias = run_multi_process(files)
    # media: MediaHolder
    for media in medias:
        print(media.__repr__())
    # TODO: next step, improve musicbrainz api then compare found intel and ask user to validate.
    print(f"{__file__} executed in {time.perf_counter() - s:0.3f} seconds. ({len(medias)} files processed)")
