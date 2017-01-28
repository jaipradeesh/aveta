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

import numpy as np
from StringIO import StringIO
from PIL import Image
from matplotlib import pyplot as plt

from network import read_n_strict


def read_input_msg(stream):
    fmt = "<BIhh"
    sz = struct.calcsize(fmt)
    header_bytes = read_n_strict(stream, sz)
    flags, img_size, left_speed, right_speed = struct.unpack(fmt, header_bytes)

    if flags & 0x1:
        raise StopIteration

    img_bytes = read_n_strict(img_size)
    fp = StringIO(img_bytes)
    img = Image.open(fp)
    imarr = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)

    print(imarr.shape)

    return imarr, left_speed, right_speed


def main(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(addr)
    sock.listen(1)

    while True:
        conn, cli = sock.accept()
        handle_conn(conn)


def handle_conn(conn):
    fmt = "<Bhh"
    while True:
        try:
            img, lspeed, rspeed = read_input_msg(conn)
            conn.sendall(struct.pack(fmt, 0x1, 0, 0))
        except StopIteration:
            return
        conn.sendall(struct.pack(fmt, 0, lspeed, rspeed))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("address",
                        default="0.0.0.0:4000",
                        help="Address to listen on.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    host, port = args.address.split(":")
    port = int(port)
    sys.exit(main((host, port)))
