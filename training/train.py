import os
import sys
import argparse

import cv2
import numpy as np

from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Activation, Dense
from keras.optimizers import SGD

from sklearn.cross_validation import train_test_split

from common import (command_mapping, command_rev_mapping, load_mapping,
                    command_readable_mapping)


def main(infile):
    mapping = load_mapping(infile)

    h, w = mapping["frame_size"]

    data = np.zeros(shape=(len(mapping["frames"]), w*h), dtype=np.float)
    data[:] = mapping["frames"]
    data /= 255.

    labels = np_utils.to_categorical(mapping["commands"], nb_classes=7)

    train_data, test_data, train_labels, test_labels = train_test_split(
        data, labels, test_size=0.15, random_state=42
    )

    model = Sequential()
    model.add(Dense(2048, input_dim=h*w, init="uniform", activation="relu"))
    model.add(Dense(1024, init="uniform", activation="relu"))
    model.add(Dense(7))
    model.add(Activation("softmax"))

    sgd = SGD(lr=0.01)
    model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

    model.fit(train_data, train_labels, nb_epoch=50, batch_size=128)

    loss, accuracy = model.evaluate(test_data, test_labels, batch_size=128,
                                    verbose=1)
    print("loss={:.4f}, accuracy={:.4f}%".format(loss, accuracy * 100))



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Input mapping pickle file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.infile))

