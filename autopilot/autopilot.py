import io
import os
import sys
import time
import socket
import struct
import argparse

import picamera

sys.path.append("..")
from motion import MotionController
from network import read_n_strict


def main(server):
    client_sock = socket.socket()
    client_sock.connect(server)
    conn = client_sock.makefile("wb")
    motionctl = MotionController()
    total_sent = 0
    start = time.time()
    outfmt = "<BIhh"
    infmt = "<Bhh"
    try:
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 1
            time.sleep(2)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, "jpeg",
                                               use_video_port=True):
                img_size = stream.tell()
                header = struct.pack(outfmt,
                                     0x00,
                                     img_size,
                                     motionctl.left_speed,
                                     motionctl.right_speed)
                conn.write(header)
                conn.flush()
                stream.seek(0)
                conn.write(stream.read())
                stream.seek(0)
                conn.flush()
                stream.truncate()
                
                speed_bytes = read_n_strict(client_sock, struct.calcsize(infmt))
                flags, lspeed, rspeed = struct.unpack(infmt, speed_bytes)
                print("Received: {}".format((flags, lspeed, rspeed)))

                motionctl._update_speed(lspeed, rspeed)

                total_sent += 1
    except KeyboardInterrupt:
        print("user exit")
    finally:
        conn.write(struct.pack(outfmt, 0x01, 0, 0, 0))
        read_n_strict(client_sock, struct.calcsize(infmt))
        conn.close()
        client_sock.close()
        motionctl.halt()
    end = time.time()
    print("{} cycles in {:.2f}s".format(total_sent, end-start))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("server_address",
                        help="Server address in host:port format.")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    host, port = args.server_address.split(":")
    port = int(port)
    sys.exit(main((host, port)))
    main()
