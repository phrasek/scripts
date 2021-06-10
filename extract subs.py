from glob import glob
from os import getcwd, path
from subprocess import check_output, CalledProcessError
from sys import argv


def call_ffmpeg(zippedfiles):
    n = argv[1] if len(argv) > 1 else "0"
    for input, output in zippedfiles:
        command = ["ffmpeg", "-i", f"{input}", "-map", f"0:s:{n}", f"{output}"]
        try:
            check_output(command, cwd=getcwd(), shell=False)
        except CalledProcessError:
            exit()


def get_files():
    inlist = []
    outlist = []
    for files in glob("*.mkv"):
        if not path.isfile(files[:-3] + "ssa"):
            inlist.append(files)
            outlist.append(files[:-3] + "ssa")
    return zip(inlist, outlist)


def main():
    call_ffmpeg(get_files())
    exit()


if __name__ == "__main__":
    main()
