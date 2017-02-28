import os
import sys
import redis
from os.path import abspath, dirname


AVETA_DIR = dirname(dirname(abspath(__file__)))
sys.path.append(AVETA_DIR)

import getch


if __name__ == "__main__":
    r = redis.Redis()
    keys = {}
    while True:
        c = getch.getch()
        speeds = None
        if c == "q":
            break

        if c == "w":
            speeds = (5, 5)
        elif c == "s":
            speeds = (-5, -5)
        elif c == "a":
            speeds = (-5, 5)
        elif c == "d":
            speeds = (5, -5)

        if speeds is not None:
            print "pushing {}".format(speeds)
            r.rpop("0:q")
            r.lpush("0:q", ",".join(map(str, speeds)))


