from glob import glob
from os import path, remove
from shutil import rmtree
from zipfile import ZipFile

zippath = r""
appdir = r""
dirname = "vscode"
installpath = path.join(appdir, dirname)


def main():
    for files in glob(path.join(zippath, "vscode*.zip")):
        filename = files
    try:
        if path.isfile(filename):
            if path.isdir(installpath):
                try:
                    rmtree(installpath)
                except:
                    pass
            with ZipFile(filename, "r") as zip:
                zip.extractall(installpath)
            remove(filename)
    except UnboundLocalError:
        print("no update zip found")


if __name__ == "__main__":
    main()
