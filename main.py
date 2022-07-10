import os
import re
import sys
import time
from pprint import pprint
import multiprocessing

from conf import api_conf as conf
from informer.MediaHolder import MediaHolder


def print_help(msg: str = None) -> None:
    """print help (optional: with an additional message) and exits with status -1 (Error)"""
    print(f"Hi, please enter a valid Audio File {conf.VALID_EXTENSIONS}")
    print(f"You may enter multiples files and / or include a folder")
    print(f"{msg}")
    exit(-1)


def list_files_in_dir(current_dir: str) -> list:
    """
    :param initial_folder:
    :param current_dir:
    :return:
    """
    ret = []
    for root, dirs, files in os.walk(current_dir):
        current_dir_files = {}
        for file in files:
            abs_file_path = os.path.join(root, file)
            # First filter
            # File exists and has valid extension
            if os.path.isfile(abs_file_path):
                job = MediaHolder(abs_file_path)
                # Second filter
                # Do not append files that failed opening with mutagen
                current_dir_files.setdefault(job) if job.__repr__() else None
                """
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

        # removing root from file's name for cleaner __repr__
        ret.append(current_dir_files) if current_dir_files else None
        #
        # for sub_dir in dirs:
        #     sub_list = list_files_in_dir(sub_dir)
        #     ret.setdefault(sub_dir, sub_list) if sub_list else None
    print(ret)
    return ret if ret else None


def parse_main_args(args: list) -> list:
    """
    :param args: list of program's arguments
    :return: a dict of every valid files found in args (files or paths)
    {dir: [valid_files] | [{sub_dir: [valid_files]}],
    file: "file.ext"}
    """
    if len(args) <= 1:
        print_help()

    ret = []
    path = os.getcwd()  # Current_workdir
    for arg in args:
        abs_path = re.sub(r"\\+", "/", os.path.join(path, arg))
        if not os.path.exists(abs_path):
            print(f"{abs_path}  : does not exists")
        elif os.path.isdir(abs_path):  # if path is a folder
            files_list = list_files_in_dir(abs_path)
            ret.append(files_list)
        elif os.path.isfile(path) and str(path).upper().endswith(conf.VALID_EXTENSIONS):
            job = MediaHolder(abs_path)
            ret.append(job) if job.valid else None
    return ret if ret != [] else None


if __name__ == '__main__':

    # list compatible files in folder
    # else append single file to list (if compatible)
    s = time.perf_counter()
    files_dict = parse_main_args(sys.argv)
    elapsed = time.perf_counter() - s
    print(f"intels gathered in {elapsed:0.2f} seconds.")
    for file in files_dict:
        print(file)
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")

