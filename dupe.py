import argparse
import glob
import hashlib
import os
import shutil
import signal
import sys
from collections import defaultdict

parser = argparse.ArgumentParser(
    description="Finds duplicate files by size and moves them to a .dupe directory."
)
parser.add_argument("-c", const=True, action="store_const", help="Delete empty files.")
parser.add_argument(
    "-l", const=True, action="store_const", help="List deleted directories."
)
parser.add_argument(
    "-d", const=True, action="store_const", help="Dry run. Does not modify any files."
)
parser.add_argument(
    "-f", const=True, action="store_const", help="Delete files instead of moving."
)

size_map = defaultdict(list)
empty = False


def keyboardInterruptHandler(signal, frame):
    sys.exit()


def exit():
    if empty:
        print("There are empty files present. Run the script with -c to remove them.")
    sys.exit()


def getEmpty(dirpath):
    filesList = []
    pattern = os.path.join(dirpath, "*")
    transdict = {"[": "[[]", "]": "[]]"}
    pattern = pattern.translate(str.maketrans(transdict))
    for file in glob.glob(pattern):
        if os.path.isfile(file) and os.stat(file).st_size == 0:
            filesList.append(os.path.join(os.getcwd(), file))
    return filesList


def getFileHash(file):
    with open(file, "rb") as hf:
        md5 = hashlib.md5(hf.read())
    return md5.hexdigest()


def makeDir(dirpath):
    os.makedirs(os.path.join(dirpath, ".dupe"), exist_ok=True)
    return


def getFiles(dirpath):
    pattern = os.path.join(dirpath, "*")
    transdict = {"[": "[[]", "]": "[]]"}
    pattern = pattern.translate(str.maketrans(transdict))
    for file in glob.glob(pattern):
        if os.path.isfile(file):
            size_map[os.stat(file).st_size].append(file)


def compareFiles():
    dupelist = []
    if size_map.pop(0, None):
        global empty
        empty = True
    for size in size_map:
        if len(size_map[size]) > 1:
            hash_map = defaultdict(list)
            for file in size_map[size]:
                hash_map[getFileHash(file)].append(file)
            for size in hash_map:
                if len(hash_map[size]) > 1:
                    for file in hash_map[size]:
                        dupelist.append(file)
                    dupelist.pop()
    return dupelist


def moveDuplicates(dupelist, dirpath):
    if len(dupelist) > 0:
        makeDir(os.path.join(os.getcwd(), dirpath))
    else:
        return
    for file in dupelist:
        try:
            shutil.move(file, os.path.join(dirpath, ".dupe"))
        except shutil.Error:
            prompt(
                f"Destination path '{os.path.join(dirpath, '.dupe')}' already exists, overwrite?"
            )
    return


def prompt(msg: str = "", choice: str = "y/N"):
    return True if input(f"{msg} [{choice}] ").lower() == choice[0].lower() else False


def deleteEmpty(dry):
    if dry:
        for folder in getDirectories():
            print("Directory: {0}".format(folder))
            print(getEmpty(folder))
    else:
        for folder in getDirectories():
            deleteFiles(getEmpty(folder))


def deleteFiles(filesList):
    for file in filesList:
        os.remove(file)


def getDirectories():
    directories = []
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
        directories.extend(dirnames)
        break
    directories = list(set(directories))
    return directories


def checkDupe(dry, del_files):
    if dry:
        for dirpath in getDirectories():
            getFiles(os.path.join(os.getcwd(), dirpath))
            print("Directory: {0}".format(dirpath))
            print(compareFiles())
            size_map.clear()
    else:
        for dirpath in getDirectories():
            getFiles(os.path.join(os.getcwd(), dirpath))
            if del_files:
                removeDuplicates(compareFiles())
            else:
                moveDuplicates(compareFiles(), os.path.join(os.getcwd(), dirpath))
            size_map.clear()


def removeDuplicates(dupelist):
    if len(dupelist) <= 0:
        return
    for file in dupelist:
        try:
            os.remove(file)
        except OSError as e:
            if prompt(f"{e}, continue?"):
                continue
            else:
                return
    return


def listDel():
    directories = getDirectories()
    delstring = " (deleted)"
    deleteddirs = []
    for name in directories:
        if name[-10:] == delstring:
            deleteddirs.append(name)
    coldirs = []
    for item in deleteddirs:
        if item[:-10] in directories:
            coldirs.append((item[:-10], item))
    return coldirs


def main():
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    args = vars(parser.parse_args())
    if args["l"]:
        print(listDel())
        exit()
    if args["c"]:
        deleteEmpty(args["d"])
        exit()
    checkDupe(args["d"], args["f"])
    exit()


if __name__ == "__main__":
    main()
