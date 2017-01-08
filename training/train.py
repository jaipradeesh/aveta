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
    def __init__(self, dirname, batch_size=64, resize_to=None):
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
        self.frame_size_hw = None

        if resize_to is not None:
            w, h = resize_to
            self.frame_size_hw = (h, w) # scipy resize takes (nrows, ncols)

        self._total_samples = 0

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
                    self._total_samples += 1

    def _read_img(self, imgpath):
        img = misc.imread(imgpath, mode="RGB")
        if self.frame_size_hw is not None:
            img = misc.imresize(img, self.frame_size_hw)
        img = np.rollaxis(img, 2, 0) # make it so that theano likes it: (channel,row,col)
        img = np.array(img, dtype=np.float32)
        img /= 255.
        return img

    def _read_batch(self, mapping):
        """Takes a list of (abs_image_path, speed_tuple) tuples."""
        imgs = []
        speeds = []
        for filename, speed_tup in mapping:
            img = self._read_img(filename)
            imgs.append(img)
            speeds.append(np.array(speed_tup))
        return imgs, speeds

    def iter(self):
        while True:
            imgs, speeds, labels = [], [], []
            for cmdcode, count in self.approx_counts.items():
                if not count:
                    continue
                cmddir = self.cmd_dirs[cmdcode]
                cmdspeeds = self.speeds[cmdcode]
                # List of (image_path, (left_speed, right_speed))
                fnames = np.random.choice(cmdspeeds.keys(), size=count)
                fname_speeds = [(os.path.join(cmddir, f), cmdspeeds[f])
                                for f in fnames]
                _imgs, _speeds = self._read_batch(fname_speeds)
                imgs.extend(_imgs)
                speeds.extend(_speeds)
                labels.extend([cmdcode] * count)
            out_imgs = np.array(imgs)
            yield ([out_imgs, np.vstack(speeds)],
                   np_utils.to_categorical(labels, nb_classes=7))

def main(input_dir):
    train_dir, test_dir, val_dir = [os.path.join(input_dir, split)
                                    for split in ("train", "test", "valid")]

    it = DataIterator(train_dir, resize_to=(224,224))
    batch_size = it.batch_size
    tsamples = int(it._total_samples / batch_size)
    batches = it.iter()
    val_it = DataIterator(val_dir, resize_to=(224,224))
    vsamples = int(val_it._total_samples / batch_size)
    val_batches = val_it.iter()

    model = vgg16.Vgg16()
    model.finetune(nb_class=7)
    model.fit(batches, val_batches, batch_size, it._total_samples, val_it._total_samples, nb_epoch=1)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",
                        help="Input directory, with a structure identical to "
                             "that of the output of gather_data.py")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.input_dir))

