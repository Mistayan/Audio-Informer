"""
Created by: 
Project: 
Creation date: 07/10/22
"""
import json
import os
import re

_String_to_Htm_ = {
    r'&': '%26',  # Htm_Type
    r' ': '+',  # Htm_Type
    r'\?': '%3F',  # Htm_Type
    r"¿": '%3F',  # PERSONAL Htm_Type
    r'_+$': '',  # Ending spaces
    r'^_+': '',  # Starting spaces
    r'[(\[]|[\])]': '',  # Brackets
    r"\#|\~|\t|\r|\n|\|": ''
}


def clean_string(s: str, replacements: dict = None):
    """
    Input: String, {pattern:replace}
    Output: String - pattern + replace
    """
    if replacements is None:
        replacements = _String_to_Htm_
    if type(s) is not str:
        s = str(s)
    for pattern in replacements:
        s = re.sub(pattern, replacements[pattern], s)
    return s


def format_htm(raw_string: str):
    """
        Turns Raw_string to Html version for requests lookup
        removes unseless spaces(before/after the content)
        CRAP sub : ' ' -> '+', removes '(*)'|'[*]'
    """
    return clean_string(raw_string.capitalize())


def rmkdir(path: str):
    """Requires an absolute path.
    recursively create folders to the asked path.
    """
    try:
        root = path.split(":/")[0] + ":/"
        if not os.path.exists(root):
            raise ReferenceError("Requires an absolute path")
        for sub in path.split("/")[1:]:
            root += sub + '/'
            if not os.path.isdir(sub) and not os.path.exists(root):
                os.mkdir(root)
    except IndexError | ReferenceError:
        raise NotADirectoryError(f"Invalid path : {path}")


def save_json(jjson, path, file_name):
    rmkdir(path)  # Ensure path asked is recursively checked
    fp = open(path + file_name, 'w')
    json.dump(jjson, fp, indent=4)
    fp.close()


def test():
    print(clean_string("Hello World!"))
    print(clean_string("azk,eîna $a)je,o)aê$*)ô j, o)aê"))


if __name__ == "__main__":
    pass
