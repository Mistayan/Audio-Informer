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


"""
import multiprocessing
    # When everything works fine, go multiprocessing
    jobs = []
    jobs.append(multiprocessing.Process(
        target=MediaHolder,
        kwargs={'path': abs_path},
        name=abs_path
    ))
for job in jobs :
job.wait()
current_dir_files.setdefault(file, job) if job.__repr__() else None
"""


def list_files_in_dir(current_dir: str) -> list:
    """
    :param current_dir: directory to scan for valid audio files
    :return list:
    """
    ret = []
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            abs_file_path = os.path.join(root, file)
            # First filter
            # File exists and has valid extension
            if os.path.isfile(abs_file_path) and MediaHolder.is_valid(abs_file_path):
                job = MediaHolder(abs_file_path)
                ret.append(job) if job.intel or job.shazam else None

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
            ret = list_files_in_dir(abs_path)
        elif os.path.isfile(path) and str(path).upper().endswith(conf.VALID_EXTENSIONS):
            ret.append(MediaHolder(abs_path)) if MediaHolder.is_valid(abs_path) else None
    return ret


if __name__ == '__main__':
    # list compatible files in folder
    # else append single file to list (if compatible)
    s = time.perf_counter()
    medias = parse_main_args(sys.argv)
    elapsed = time.perf_counter() - s
    print(f"intels gathered in {elapsed:0.2f} seconds.")
    pprint.pprint(medias)
    # TODO : next step, is to gather intel on the web, compare those and ask user to validate intel
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
