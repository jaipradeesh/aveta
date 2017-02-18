"""Message format
   
    Accept:

        [flags(1 byte)][image_size(4 bytes)][left_speed(2 bytes)][right_speed(2 bytes)][image_data]

    Reply:

        [flags(1 byte)][left_speed(2 bytes)][right_speed(2 bytes)]

    Numbers are little endian encoded.

    flags:
        bit 0 is set to indicate quitting.

"""
import os
import sys
import socket
import argparse
import struct
from os.path import dirname, abspath

import numpy as np
from scipy.misc import imresize, imsave
from StringIO import StringIO
from PIL import Image
from matplotlib import pyplot as plt
from keras.models import load_model

AVETA_DIR = dirname(dirname(abspath(__file__)))

sys.path.append(AVETA_DIR)
from network import read_n_strict


def read_input_msg(stream):
    fmt = "<BIhh"
    sz = struct.calcsize(fmt)
    header_bytes = read_n_strict(stream, sz)
    flags, img_size, left_speed, right_speed = struct.unpack(fmt, header_bytes)

    if flags & 0x1:
        raise StopIteration

    img_bytes = read_n_strict(stream, img_size)
    print("Read {} image bytes.".format(img_size))
    fp = StringIO(img_bytes)
    img = Image.open(fp)
    imarr = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    imarr = np.fliplr(np.flipud(imarr))
    h, w, _ = imarr.shape
    imarr = imarr[h/2:,:]
    print(imarr.shape)
    return imarr, left_speed, right_speed


def main(addr, model_path, verbose):
    if verbose:
        print("Loading model from {}".format(model_path))
    model = load_model(model_path)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(addr)
    sock.listen(1)

    if verbose:
        print("Listening on {}:{}".format(*addr))
        
    while True:
        conn, cli = sock.accept()
        if verbose:
            print("Connection accepted ({})".format(conn))
        handle_conn(conn, model)


def handle_conn(conn, model):
    fmt = "<Bhh"
    while True:
        try:
            img_, lspeed, rspeed = read_input_msg(conn)
            img = np.flipud(img_)
            img = img[len(img)/2:,:]
            img = imresize(img_, (120, 160))
            imsave("/home/ys/aveta-stream.jpg", img)
            img = np.rollaxis(img, 2, 0)
            X = [np.array([img]), np.array([[lspeed, rspeed]])]
            lout, rout = np.clip(model.predict(X).reshape(2,), 50, 255)
            print lout, rout
            conn.sendall(struct.pack(fmt, 0x00, round(lout), round(rout)))
        except StopIteration:
            break
    conn.sendall(struct.pack(fmt, 0x01, lspeed, rspeed))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--address",
                        default="0.0.0.0:4000",
                        help="Address to listen on.")

    model_default_path = os.path.join(AVETA_DIR, "models", "aveta-model.hdf5")
    parser.add_argument("--model_path",
                        default=model_default_path,
                        help="Path to an HDF5 model containing the Keras model.")

    parser.add_argument("--verbose", "-v",
                        action="store_true",
                        help="Print debug information.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    host, port = args.address.split(":")
    port = int(port)
    model_path = args.model_path
    verbose = args.verbose
    sys.exit(main((host, port), model_path, verbose))
