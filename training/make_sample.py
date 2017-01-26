"""Given a data directory, create another with a fraction of the original data.
"""
import os
import sys
import shutil
import tempfile
import argparse
import random

import train_test_split

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="input directory")
    parser.add_argument("output_dir", help="output root directory")
    parser.add_argument("--fraction", type=float,
                        help="fraction of data(between 0 and 1)",
                        default=0.1)
    args = parser.parse_args()
    return args

def main(input_dir, output_dir, frac):
    if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
        print("Error: {} does not name a directory")
        return 1

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    speedfile = os.path.join(input_dir, "speeds.txt")
    names = []
    lines = []
    print speedfile
    with open(speedfile) as fp:
        for line in fp:
            name, _ = line.strip().split(",", 1)
            names.append(name)
            lines.append(line.strip())
    
    n = int(frac * len(names))
    if not n:
        return 0

    choice = random.sample(range(len(names)), n)
    with open(os.path.join(output_dir, "speeds.txt"), "wb") as fp:
        for i in choice:
            fp.write("{}\n".format(lines[i]))
            shutil.copy(os.path.join(input_dir, names[i]),
                        os.path.join(output_dir, names[i]))

    return 0

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.input_dir,
                  args.output_dir,
                  args.fraction))




