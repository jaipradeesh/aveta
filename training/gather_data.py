# coding: utf-8
"""
gather_data.py

Usage:
    python gather_data.py RAW_DATA_DIR OUTPUT_DIR

RAW_DATA_DIR must have a specific structure, like the one generated by
aveta-bastion's movedata.pl (github.com/yati-sagade/aveta-bastion)

An example:

    $ ls ~/aveta-training-data-final
    /home/ys/aveta-training-data-final/
    ├── cochlea
    │   ├── 0
    │   │   ├── commands.txt
    │   │   ├── original-name
    │   │   ├── sync.txt
    │   │   └── video.avi
    │   └── 1
    │       ├── commands.txt
    │       ├── original-name
    │       ├── sync.txt
    │       └── video.avi
    └── simple
        ├── 0
        │   ├── commands.txt
        │   ├── original-name
        │   ├── sync.txt
        │   └── video.avi
        ├── 1
        │   ├── commands.txt
        │   ├── original-name
        │   ├── sync.txt
        │   └── video.avi
        ├── 2
        │   ├── commands.txt
        │   ├── original-name
        │   ├── sync.txt
        │   └── video.avi
        ├── 3
        │   ├── commands.txt
        │   ├── original-name
        │   ├── sync.txt
        │   └── video.avi
        └── 4
            ├── commands.txt
            ├── original-name
            ├── sync.txt
            └── video.avi

This script collects all video and command files -- using the sync files to match
commands with frames -- and writes the final training data into OUTPUT_DIR. The
video frames are converted to grayscale before writing.

Two files are written, images.pkl and labels.pkl. The former contains a numpy
array with one flattened video frame per row, and the latter contains a numpy
array of integers, each representing user input at the corresponding frame in
the images array.

Command codes:

    0: No input
    1: Forward
    2: Left
    3: Back
    4: Right
    5: Straighten course
    6: Halt

"""
import cv2
import sys
import argparse
import os
from collections import defaultdict
from itertools import izip, chain
try:
    import cPickle as pkl
except ImportError:
    import pickle as pkl


import numpy as np

from common import (command_mapping, command_rev_mapping,
                    command_readable_mapping, write_mapping)


def main(input_dir, output_dir, verbose):
    if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
        print("{} does not name a directory.".format(input_dir))
        return 1

    if os.path.exists(output_dir) and not os.path.isdir(output_dir):
        print("{} does not name a directory.".format(output_dir))
        return 1
    elif not os.path.exists(output_dir):
        os.makedirs(output_dir)

    mappings = []
    for tagname in os.listdir(input_dir):
        tagdir = os.path.join(input_dir, tagname)
        if not os.path.isdir(tagdir):
            continue
        mapping = _process_tagdir(tagdir)
        if mapping is not None:
            mappings.append(mapping)

    mapping = _merge_mappings(*mappings)
    if verbose:
        print("Mapping built, size: {} bytes".format(sys.getsizeof(mapping)))

    outfile = os.path.join(output_dir, "mapping.pkl")
    write_mapping(mapping, outfile)

    return 0


def _process_tagdir(dirname):
    """Build and return the mapping for a single tagdir."""
    mappings = []
    for idx in os.listdir(dirname):
        datadir = os.path.join(dirname, idx)
        if not idx.isdigit() or not os.path.isdir(datadir):
            continue
        vidfile, syncfile, cmdfile = [
            os.path.join(datadir, fname)
            for fname in ("video.avi", "sync.txt", "commands.txt")
        ]
        mappings.append(build_mapping(vidfile, syncfile, cmdfile))
    return _merge_mappings(*mappings)


def _merge_mappings(*mappings):
    """Return a merger of multiple mappings."""
    if not mappings:
        return None

    all_sizes = {mapping["frame_size"] for mapping in mappings}
    if len(all_sizes) != 1:
        raise ValueError("Different frame_size mappings cannot be merged.")

    all_frames = [mapping["frames"] for mapping in mappings]
    all_commands = [mapping["commands"] for mapping in mappings]
    all_speeds = [mapping["speeds"] for mapping in mappings]

    img_size = all_sizes.pop()
    return {
        "frames": np.vstack(all_frames),
        "commands": np.hstack(all_commands),
        "speeds": np.vstack(all_speeds),
        "frame_size": img_size,
    }


def build_mapping(video_filename, sync_filename, cmd_filename):
    """Build a map from video frames to corresponding user commands.

    Given paths to the video, sync and command files, return a dict containing
    the frames, commands, speeds, and the frame size.
    """

    sync = _read_file(sync_filename, value_mapper=lambda vs: (int(vs[0]),))
    cmds = _read_file(cmd_filename)

    frames = izip(weighted_iter(sync), _video_frame_iter(video_filename))

    img_size = None
    ret_frames, ret_commands, ret_speeds = [], [], []
    for frame, command, left_speed, right_speed in _cmd_frame_iter(frames,
                                                                   iter(cmds)):
        if img_size is None:
            img_size = frame.shape
        elif img_size != frame.shape:
            raise ValueError("frames of different sizes encountered.")
        ret_frames.append(frame.reshape(-1))
        ret_commands.append(command_mapping[command])
        ret_speeds.append([left_speed, right_speed])

    return {"frames": np.array(ret_frames),
            "commands": np.array(ret_commands),
            "speeds": np.array(ret_speeds, dtype=np.float64),
            "frame_size": img_size}


def _video_frame_iter(video_filename):
    cap = cv2.VideoCapture(video_filename)
    if cap is None:
        raise Exception("Could not read video {}".format(video_filename))
    while cap.isOpened():
        flag, frame = cap.read()
        if not flag:
            break
        yield cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def _cmd_frame_iter(frames, cmds):
    """Match timestamped frames and commands.

    Args:
        frames: An iterator yielding (str, numpy.ndarray), or timestamped
        video frames.

        cmds: An iterator yielding (str, str, str, str), or timestamped commands.

    Returns:
        An iterator yielding (numpy.array, str), for a video frame and the
        (best-effort) matching command.

    NOTE: Command can be None when there was no command seen for a given frame.
    """
    # NOTE 1: This assignment of "no command" to certain frames is incorrect,
    # strictly speaking, since frames are classified "no command" only when
    # the command stream for a given second has been exhausted.
    def _next_frame(it):
        t, x = next(it)
        return (int(float(t)), x)

    def _next_cmd(it):
        t, c, l, r = next(it)
        return (int(float(t)), c, float(l), float(r))

    ret = []
    read_frame, read_cmd = True, True
    while True:
        if read_frame:
            frame_time, frame = _next_frame(frames)
        if read_cmd:
            cmd_time, cmd, left_speed, right_speed = _next_cmd(cmds)

        if cmd_time < frame_time:
            # Drop this command
            read_cmd, read_frame = True, False
            continue
        elif cmd_time > frame_time:
            read_cmd, read_frame = False, True
            # No command; see `NOTE 1` above.
            yield frame, None, left_speed, right_speed
        else:
            read_frame, read_cmd = True, True
            yield frame, cmd, left_speed, right_speed

    for _, frame in frames:
        yield frame, None, left_speed, right_speed


def _read_file(filename, value_mapper=lambda x: x):
    """Read a file with comma separated <key,val1,val2...> lines.

    Returns a list of (key, val1, val2..) tuples sorted by the key ascending. If
    `value_mapper` is given, it is passed a tuple of length `num_fields-1`
    containing the `num_fields-1` values on line.
    """
    retmap = {}
    with open(filename) as fp:
        for line in fp:
            split_line = line.strip().split(",")
            key = split_line[0]
            vals = tuple(split_line[1:])
            # For command files, there *might* be multiple commands per tick, but
            # we'll just pick the last one in the file.
            retmap[key] = value_mapper(vals)

    for key, vals in sorted(retmap.items(), key=lambda t: t[0]):
        yield tuple(chain([key], vals))



def weighted_iter(buckets):
    """Given a sequence of (key, count) items, return an iterator yielding keys in agreement with the counts."""
    for key, count in buckets:
        for _ in xrange(count):
            yield key


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Input directory")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Give verbose output")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.input_dir, args.output_dir, args.verbose))
