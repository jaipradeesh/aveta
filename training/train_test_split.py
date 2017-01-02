"""Given a data directory, with data organized in label folders, produces
three directory trees, each identical to the input directory tree in structure.
The three trees are called train/, test/ and valid/"""
from __future__ import print_function
import os
import shutil
import sys
import argparse

import numpy as np

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="input directory")
    parser.add_argument("output_dir", help="output root directory")

    parser.add_argument("--test_fraction", type=float,
                        help="test set proportion, as a floating point number "
                             "between 0 and 1.",
                        default=0.1)

    parser.add_argument("--valid_fraction", type=float,
                        help="validation set proportion, as a floating point number "
                             "between 0 and 1.",
                        default=0.1)

    args = parser.parse_args()
    return args

def _labelnames(input_dir):
    labelnames = [entry for entry in os.listdir(input_dir)
                        if entry.isdigit() and
                           os.path.isdir(os.path.join(input_dir, entry))]
    return labelnames
    

def main(input_dir, output_dir, test_fraction, valid_fraction):
    if not os.path.exists(input_dir):
        print("Input directory {} does not exist.".format(input_dir))
        return 1

    if test_fraction + valid_fraction > 1.0:
        print("test_fraction and valid_fraction must sum to at most 1.0")
        return 1
    
    _prepare_output_dir(input_dir, output_dir)

    for labelname in _labelnames(input_dir):
        if _process_label(input_dir, output_dir, labelname, test_fraction,
                          valid_fraction):
            return 1

def _read_speedfile(filename):
    def _mapper(line):
        imgfile, lspeed, rspeed = line.strip().split(",")
        return imgfile, lspeed, rspeed
    with open(filename) as fp:
        lines = [_mapper(line) for line in fp]
    np.random.shuffle(lines)
    return lines 

def _process_label(input_dir, output_dir, label, test_fraction, valid_fraction):
    speedfile_path = os.path.join(input_dir, label, "speeds.txt")

    if not os.path.exists(speedfile_path):
        print("speedfile {} does not exist, quitting.".format(speedfile_path))
        return 1

    speeds = _read_speedfile(speedfile_path) # this can be used like dictionary file

    nb_test = int(test_fraction * len(speeds))
    nb_valid = int(valid_fraction * len(speeds))

    for split, start, end in (("test", 0, nb_test),
                              ("valid", nb_test, nb_test+nb_valid),
                              ("train", nb_test+nb_valid, None)):
        speedinfos = speeds[start:end]
        split_outdir = os.path.join(output_dir, split, label)
        out_speeds = open(os.path.join(split_outdir, "speeds.txt"), "wb")
        try:
            for imgfile, lspeed, rspeed in speedinfos:
                in_imgpath = os.path.join(input_dir, label, imgfile)
                out_imgpath = os.path.join(split_outdir, imgfile)
                shutil.copy(in_imgpath, out_imgpath)
                for speedinfo in speedinfos:
                    out_speeds.write("{}\n".format(",".join(speedinfo)))
        finally:
            out_speeds.close()

def _prepare_output_dir(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    labelnames = _labelnames(input_dir)
    for d in ("train", "test", "valid"):
        dirname = os.path.join(output_dir, d)
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.makedirs(dirname)
        for labelname in labelnames:
            os.makedirs(os.path.join(dirname, labelname))

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.input_dir, args.output_dir, args.test_fraction,
                  args.valid_fraction))
