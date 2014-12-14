"""
@file
@brief Various function to clean the code.
"""

import os
from ..sync.synchelper import explore_folder

def remove_extra_spaces(filename):
    """
    removes extra spaces in a filename, replace the file in place

    @param      filename        file name
    @return                     number of removed extra spaces
    """
    try:
        with open(filename, "r") as f :
            lines = f.readlines()
    except PermissionError as e :
        raise PermissionError (filename) from e

    lines2 = [ _.rstrip(" \r\n") for _ in lines ]
    last = len(lines2)-1
    while last >= 0 and len(lines2[last]) == 0 :
        last -= 1
    last+=1
    lines2 = lines2[:last]

    diff = len("".join(lines)) - len("\n".join(lines2))
    if diff != 0:
        with open(filename,"w") as f :
            f.write("\n".join(lines2))
    return diff

def remove_extra_spaces_folder(folder, extensions = (".py",".rst")):
    """
    removes extra files in a folder for specific file extensions

    @param      folder      folder to explore
    @param      extensions  list of file extensions to process
    @return                 the list of modified files
    """
    files = explore_folder(folder)[1]
    mod = [ ]
    for f in files :
        ext = os.path.splitext(f)[-1]
        if ext in extensions:
            d = remove_extra_spaces(f)
            if d != 0 :
                mod.append(f)
    return mod