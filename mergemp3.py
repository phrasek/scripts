from glob import glob
from os import remove
from re import search
from subprocess import check_output

lengths = []
inputAudioFiles = glob("*.mp3")


def getDuration(filename):
    command = ["ffprobe", "-hide_banner", "-loglevel", "8", "-show_streams", filename]
    vid_metadata = check_output(command).decode("utf-8")
    regexes = {
        "dur": r"DURATION=(\d\d:\d\d:\d\d\.\d+)|duration=(\d+\.\d+)",
    }
    vid_info = {}
    for parameter, regex in regexes.items():
        if match := search(regex, vid_metadata):
            print(match.group(1))
            if match.group(1) is None:
                vid_info[parameter] = float(match.group(2))
            elif ":" in match.group(1):
                dur_string = match.group(1).split(":")
                hours = int(dur_string[0])
                mins = int(dur_string[1])
                secs = float(dur_string[2])
                vid_info[parameter] = (60 * hours) + (60 * mins) + secs
            elif "/" in match.group(1):
                div_string = match.group(1).split("/")
                x = float(div_string[0])
                y = float(div_string[1])
                vid_info[parameter] = x / y
            elif "." in match.group(1):
                vid_info[parameter] = float(match.group(1))
            else:
                vid_info[parameter] = int(match.group(1))

    return int(vid_info["dur"] * 1000)


# create files list for ffmpeg concat and get audio file lengths
with open("files.txt", "w") as txtfile:
    for fil in inputAudioFiles:
        txtfile.write(f"file '{fil}'\n")
        lengths.append(getDuration(fil))

# create ffmpeg metadata file for chapters
command = f'ffmpeg -i "{inputAudioFiles[0]}" -f ffmetadata FFMETADATA'
check_output(command, shell=True)

metadata = open("FFMETADATA", "r", encoding="utf-8").read()
start = "0"
for i in lengths:
    metadata += (
        """[CHAPTER]
TIMEBASE=1/1000
START="""
        + start
        + """
END="""
        + str(int(start) + i)
        + """
title="""
        + str(lengths.index(i) + 1)
        + "\n"
    )
    start = str(int(start) + i)

# write metadata file to disk
metafile = open("FFMETADATA", "w")
print(metadata, file=metafile, encoding="utf-8")
metafile.close()

# merge audio files and map chapters using metadata file
command = 'ffmpeg -f concat -safe 0 -i files.txt -i FFMETADATA -map_metadata 1 -vn -c aac -b:a 64k "merged.m4a"'
check_output(command, shell=True)

# clean up temp files
remove("FFMETADATA")
remove("files.txt")
