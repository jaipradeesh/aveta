"""Given a data directory, create another with a fraction of the original data.
"""
import os
import sys
import shutil
import tempfile
import argparse

import train_test_split

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="input directory")
    parser.add_argument("output_dir", help="output root directory")
    parser.add_argument("--fraction", type=float,
                        help="fraction of data(between 0 and 1)",
                        default=0.1)
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


def process_label_dir(indir, outdir, frac):
    speedfile = os.path.join(indir, "speeds.txt")
    entries = train_test_split.read_speedfile(speedfile)
    count = int(frac * len(entries))
    with open(os.path.join(outdir, "speeds.txt"), "w") as fp:
        for entry in entries[:count]:
            fp.write("{}\n".format(",".join(entry)))
            shutil.copy(os.path.join(indir, entry[0]),
                        os.path.join(outdir, entry[0]))


def main(input_dir, output_dir, frac, test_frac, valid_frac):
    if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
        print("Error: {} does not name a directory")
        return 1

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    tmp_output_dir = tempfile.mkdtemp()
    labels = train_test_split.labelnames(input_dir)

    for label in labels:
        os.makedirs(os.path.join(tmp_output_dir, label))
        process_label_dir(os.path.join(input_dir, label),
                          os.path.join(tmp_output_dir, label),
                          frac)

    try:
        ret = train_test_split.main(tmp_output_dir,
                                    output_dir,
                                    test_frac,
                                    valid_frac)

        return ret
    finally:
        shutil.rmtree(tmp_output_dir)

    return 0

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.input_dir,
                  args.output_dir,
                  args.fraction,
                  args.test_fraction,
                  args.valid_fraction))




