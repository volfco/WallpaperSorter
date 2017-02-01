import argparse
import os
import shutil
from PIL import Image

# Variables
__RESOLUTIONS = [
    [8192, 4608],
    [5120, 2880],
    [3840, 2160],
    [3440, 1440],
    [2560, 1440],
    [1920, 1200],
    [1920, 1080],
    [1680, 1050],
    [1600, 900],
    [1440, 900],
    [1280, 800],
    [1280, 720]
]


def move_file(basedir, name, target, move=False):
    __PATH = "{0}\\{1}".format(basedir, name)
    __TARGET = basedir + "\\{0}x{1}\\".format(target[0], target[1])

    if not os.path.isdir(__TARGET):
        os.makedirs(__TARGET)

    if not move:
        shutil.copyfile(__PATH, __TARGET + name)
    else:
        shutil.move(__PATH, __TARGET + name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--move", action="store_false")
    parser.add_argument("path", default='.')

    args = parser.parse_args()

    __RESOLUTIONS.sort(key=lambda x: x[1], reverse=True)

    # walk the directory
    for obj in os.listdir(args.path):
        type = obj.split('.')[-1]
        if type.lower() not in ['jpg', 'png', 'jpeg']:
            continue

        # Get the resolution
        __PATH = args.path + "\\" + obj
        with Image.open(__PATH) as im:
            __RES = im.size

        # Walk the list
        for i in range(0, __RESOLUTIONS.__len__()):
            if __RESOLUTIONS[i][0] == __RES[0] and __RESOLUTIONS[i][1] == __RES[1] or \
                                    __RES[0] >= __RESOLUTIONS[i][0] and __RES[1] >= __RESOLUTIONS[i][1]:
                move_file(args.path, obj, __RESOLUTIONS[i], move=args.move)
                break

        print("Unable to sort {0}".format(obj))




