"""Load a model and ask for filename,lspeed,rspeed on stdin to predict speeds."""
import os
import sys
import time
import argparse

import numpy as np
from scipy.misc import imread, imresize
from keras.models import load_model

    
def main(model_file, verbose):
    start = time.time()
    model = load_model(model_file)
    end = time.time()
    if verbose:
        print("Model loaded in {:0.2f}s.".format(end-start))
    while True:
        input_line = raw_input("> ")
        start = time.time()
        filename, lspeed, rspeed = input_line.strip().split(",")

        im = imread(filename, mode="RGB")
        im = imresize(im, (150, 400))
        im = np.rollaxis(im, 2, 0).reshape(1, 3, 150, 400)
        
        X = [im, np.array([[float(lspeed), float(rspeed)]])]
        y = model.predict(X)
        end = time.time()

        if verbose:
            print("{} (took {:0.2f}s)".format(y, end-start))
    return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_file", help="Path to the trained model file.")
    parser.add_argument("--verbose", action="store_true", help="Print timing etc.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.model_file, args.verbose))

