import glob
import os
import shutil
import signal
import subprocess
from collections import defaultdict
from datetime import timedelta
from math import isclose
import shutil
from sys import argv
from humanize import naturalsize
from tabulate import tabulate


class VideoFile:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.basename = os.path.basename(self.filepath)
        self.filetype = os.path.splitext(self.basename)[1]
        self.filename = os.path.splitext(self.basename)[0]
        self.__size = None
        self.__length = None

    @property
    def length(self) -> float:
        if self.__length:
            return self.__length
        else:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    self.filepath,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            try:
                self.__length = float(result.stdout)
            except ValueError:
                self.__length = 0

            return self.__length

    @property
    def size(self) -> int:
        if self.__size:
            return self.__size
        else:
            self.__size = os.stat(self.filepath).st_size
            return self.__size


def keyboardInterruptHandler(signal, frame):
    exit()


def about(originalLength, newLength, margin=1) -> bool:
    """
    Returns True if newLength is within accetable error of originalLength.\n
    Acceptable error is defined as margin seconds per minute or margin, whichever is larger
    """
    return isclose(
        originalLength, newLength, abs_tol=max(originalLength * margin / 60, margin)
    )


def getFiles(dirpath, filetype):
    filesList = defaultdict(dict)
    pattern = os.path.join(dirpath, f"*.{filetype}")
    pattern = pattern.translate(str.maketrans({"[": "[[]", "]": "[]]"}))
    for file in glob.glob(pattern):
        if os.path.isfile(file):
            curFile = VideoFile(filepath=file)
            filesList[curFile.filename] = curFile
    return filesList


def compareFiles(origfiles, newfiles):
    if len(origfiles) == 0 or len(newfiles) == 0:
        exit()
    table = []
    headers = [
        "Index",
        "Filename",
        "Original Size",
        "New Size",
        "Original Length",
        "New Length",
        r"% reduction",
    ]
    n = 1
    totalorig = 0
    totalnew = 0
    toMove = []
    for key, videofile in origfiles.items():
        if key in newfiles.keys():
            oldsize = videofile.size
            oldlength = videofile.length
            newsize = newfiles[key].size
            newlength = newfiles[key].length
            totalorig += oldsize
            totalnew += newsize
            star = ""
            if (reduction := int((oldsize - newsize) / oldsize * 100)) > 15 and about(
                oldlength, newlength, margin=3
            ):
                toMove.append(videofile)
                star = "*"
            line = [
                n,
                star + key,
                naturalsize(oldsize),
                naturalsize(newsize),
                str(timedelta(seconds=oldlength)),
                str(timedelta(seconds=newlength)),
                reduction,
            ]
            table.append(line)
            n += 1
    if table:
        line = [
            "",
            "Total",
            naturalsize(totalorig),
            naturalsize(totalnew),
            "",
            "",
            int((totalorig - totalnew) / totalorig * 100),
        ]
        table.append(line)
        print(tabulate(table, headers=headers))
    return toMove


def test():
    filetype = "ts" if len(argv) == 1 else argv[1]
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    origfiles = getFiles(os.getcwd(), filetype)
    newfiles = getFiles(os.getcwd() + r"\\enc\\", "mkv")
    toMove = compareFiles(origfiles=origfiles, newfiles=newfiles)
    while len(toMove) > 0:
        input()
        try:
            os.mkdir("del")
        except OSError:
            pass
        for item in toMove:
            try:
                shutil.move(item.filepath, "del")
            except PermissionError as e:
                print(
                    f"{e}, close any programs using the file and press enter to try again."
                )
                continue
            except shutil.Error as e:
                print(f"{e}, removing file without moving")
                if os.path.isfile(item.filepath):
                    try:
                        os.remove(item.filepath)
                    except PermissionError as e:
                        print(
                            f"{e}, close any programs using the file and press enter to try again."
                        )
                        continue

        origfiles = getFiles("", filetype)
        newfiles = getFiles("enc", "mkv")
        toMove = compareFiles(origfiles=origfiles, newfiles=newfiles)


if __name__ == "__main__":
    test()
