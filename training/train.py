import re
import os
import sys
import argparse

import numpy as np
from scipy import misc

from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Activation, Dense
from keras.optimizers import SGD

from sklearn.cross_validation import train_test_split

from common import (command_mapping, command_rev_mapping, load_mapping,
                    command_readable_mapping)

import vgg16

class DataIterator(object):
    def __init__(self, dirname, batch_size=64, resize_to=(100,100)):
        pat = re.compile(r'^\d+\..+$')
        label_hist = {
            label: sum(1 for f in os.listdir(os.path.join(dirname, label)) if pat.match(f))
            for label in os.listdir(dirname) if label.isdigit()
        }
        total = float(sum(label_hist.values()))

        self.approx_counts = {
            label: int(batch_size * count / total) for label, count in label_hist.items()
        }

        self.cmd_dirs = {}
        self.speeds = {}
        self.batch_size = batch_size
        for entry in os.listdir(dirname):
            if not entry.isdigit():
                continue
            cmddir = os.path.join(dirname, entry)
            self.cmd_dirs[entry] = cmddir
            speedfile = os.path.join(cmddir, "speeds.txt")
            self.speeds[entry] = {}
            with open(speedfile) as fp:
                for line in fp:
                    fname, lspeed, rspeed = line.strip().split(",")
                    self.speeds[entry][fname] = (float(lspeed)/255., float(rspeed)/255.)

    def _read_img(self, filename):
        imgpath = os.path.join(self.cmd_dirs[cmdcode], filename)
        img = misc.imread(imgpath, mode="F").reshape(-1)
        img /= 255.
        return img

    def _read_batch(self, filenames):
        imgs = []
        speeds = []
        labels = []
        for filename in filenames:
            img = self._read_img(filename)
            imgs.append(img)
            speeds.append(np.array(self.speeds[cmdcode][filename]))
            labels.append(int(cmdcode))
        return imgs, speeds, labels

    def iter(self):
        while True:
            imgs, speeds, labels = [], [], []
            for cmdcode, count in self.approx_counts.items():
                filenames = [np.random.choice(self.speeds[cmdcode].keys())
                             for _ in range(count)]
                _imgs, _speeds, _labels = self._read_batch(filenames)
                imgs.extend(_imgs)
                speeds.extend(_speeds)
                labels.extend(_labels)
            yield ([np.vstack(batch), np.vstack(speeds)],
                   np_utils.to_categorical(labels, nb_classes=7))

def main(input_dir):
    train_dir, test_dir, val_dir = [os.path.join(input_dir, split)
                                    for split in ("train", "test", "valid")]

    batches = DataIterator(train_dir).iter()
    val_batches = DataIterator(val_dir).iter()

    model = vgg16.Vgg16()
    model.finetune(nb_class=7)
    model.fit(batches, val_batches, batches.batch_size, nb_epoch=1)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",
                        help="Input directory, with a structure identical to "
                             "that of the output of gather_data.py")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.input_dir))

