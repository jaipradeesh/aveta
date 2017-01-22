from __future__ import print_function
import re
import cv2
import os
import sys
import argparse
import shutil

from scipy.stats import mode
from matplotlib import pyplot as plt

from common import command_readable_mapping

def _imshow(name, img):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.imshow(name, img)

def _process(im):
    kern = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    kern_small = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    gr = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    bl = cv2.GaussianBlur(gr, (11, 11), 0.)
    eq = cv2.equalizeHist(bl)
    edges = cv2.Canny(eq, 70, 210)
    edges = cv2.dilate(edges, kern)
    edges = cv2.erode(edges, kern_small)
    out = im[:]
    out[edges==0] = 0

    return dict(grayscale=gr, blurred=bl, equalized=eq, edges=edges, out=out)


def main(input_dir, output_dir, interactive, augment):
    if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
        print("{} does not name a directory".format(input_dir))
        return 1

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    labels = [entry for entry in os.listdir(input_dir)
              if os.path.isdir(os.path.join(input_dir, entry)) and
                 not entry.startswith(".")]

    for label in labels:
        os.makedirs(os.path.join(output_dir, label))
        _process_labeldir(input_dir, output_dir, interactive, label)

    if augment:
        augment_data(output_dir)


def augment_data(dirname):
    right_label = command_readable_mapping.index("RIGHT")
    for label_readable in ("LEFT", "RIGHT"):
        label = command_readable_mapping.index(label_readable)
        path = os.path.join(dirname, str(label))
        augment_dir(path)


def next_writable_filenum(dirname, extns):
    regex = re.compile(r'^(\d+)\.(?:' + r'|'.join(extns) + r')$')
    names = os.listdir(dirname)
    max_num = 0
    for name in names:
        m = regex.match(name)
        if m is None:
            continue
        filenum = int(m.groups()[0])
        max_num = max(filenum, max_num)
    return max_num + 1


def augment_dir(dirname):
    n = next_writable_filenum(dirname, ["jpeg", "jpg", "png"])
    speedfile = os.path.join(dirname, "speeds.txt")
    speedlines = []

    with open(speedfile, "rb") as fp:
        for line in fp:
            filename, left_speed, right_speed = line.strip().split(",")
            im = cv2.imread(os.path.join(dirname, filename))
            outname = "{}.jpeg".format(n)
            n += 1
            outfile = os.path.join(dirname, outname)
            cv2.imwrite(outfile, cv2.flip(im, 1))
            speedlines.append([outname, right_speed, left_speed])

    with open(speedfile, "a+b") as fp:
        for line in speedlines:
            fp.write("{}\n".format(",".join(line)))


def _process_labeldir(input_dir, output_dir, interactive, label):
    label_outdir = os.path.join(output_dir, label)
    label_indir = os.path.join(input_dir, label)

    for filename in os.listdir(label_indir):
        path = os.path.join(label_indir, filename)
        if filename.startswith(".") or os.path.isdir(path):
            continue

        output_path = os.path.join(label_outdir, filename)
        if filename == "speeds.txt":
            shutil.copy(path, output_path)
            continue

        im = cv2.imread(path)
        processed = _process(im)
        if interactive:
            for name, image in processed.items():
                _imshow(name, image)
            if cv2.waitKey(0) & 0xff == ord("q"):
                break
        else:
            cv2.imwrite(output_path, processed["out"])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="input directory containing images.")
    parser.add_argument("output_dir", help="output  directory containing images.")
    parser.add_argument("--interactive", action="store_true",
                        help="when given, various steps are shown in opencv "
                             "windows, for each image in turn. This does not"
                             " write to output_dir.")
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="verbose output")
    parser.add_argument("--augment", action="store_true", default=False,
                        help="augment training data by flipping right and left images")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.input_dir, args.output_dir, args.interactive,
                  args.augment))

