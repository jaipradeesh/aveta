"""Given a mapping file, sequentially show the frame with the corresponding
command overlaid on top."""
import os
import sys
import argparse
from itertools import izip

import cv2
import numpy as np

from common import (command_mapping, command_rev_mapping,
                    command_readable_mapping, load_mapping)

def display_mapping(mapping):
    """Display mapping in an interactive window.

    Open a window with a frame from the `mapping` overlaid with the command
    corresponding to the frame in the mapping. If `random_order` is False,
    walk sequentially through the mapping, else select randomly.
    """
    img_size = mapping["frame_size"]
    win_name = "mappings"
    win = cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

    for frame, cmd in izip(mapping["frames"], mapping["commands"]):
        read_cmd = command_readable_mapping[cmd]
        msg = read_cmd
        img = frame.reshape(img_size)
        cv2.putText(img, msg, (10, 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.6, (0, 0, 0))
        cv2.imshow(win_name, img)
        if cv2.waitKey(0) & ord("q") == ord("q"):
            break

    cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Input pickle file.")
    return parser.parse_args()


def main(infile):
    mapping = load_mapping(infile)
    display_mapping(mapping)
    return 0


if __name__ == "__main__":
    args = parse_args()
    main(args.infile)

