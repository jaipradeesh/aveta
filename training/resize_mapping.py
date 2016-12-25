"""Given a mapping file, read it, and resize frames in it to the given size and write
to a given location."""
import os
import sys
import argparse

import cv2
import numpy as np

from common import (command_mapping, command_rev_mapping,
                    command_readable_mapping, write_mapping)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Input mapping pickle file.")
    parser.add_argument("size", help="Target size, in widthxheight notation.")
    parser.add_argument("outfile", help="Output pickle file.")
    return parser.parse_args()


def main(infile, size, outfile):
    mapping = load_mapping(infile)

    w, h = size
    h_orig, w_orig = mapping["frame_size"]
    n_frames = len(mapping["frames"])
    resized_frames = np.zeros(shape=(n_frames, w * h),
                              dtype=mapping["frames"].dtype)

    for i, frame in enumerate(mapping["frames"]):
        img = frame.reshape(h_orig, w_orig)
        resized_frames[i][:] = cv2.resize(
            img, (w, h), interpolation=cv2.INTER_AREA
        ).reshape(-1)

    write_mapping({"frames": resized_frames,
                   "frame_size": (h, w),
                   "commands": mapping["commands"]}, outfile)


if __name__ == "__main__":
    args = parse_args()
    try:
        w, h = map(int, args.size.strip().split("x"))
    except:
        print("Size is expected as WidthxHeight")
        sys.exit(1)

    sys.exit(main(args.infile, (w, h), args.outfile))
