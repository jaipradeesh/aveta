from __future__ import print_function
import os
import sys
import curses
import atexit
import multiprocessing as mp
import time
import argparse

AVETA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(AVETA_DIR)
print(AVETA_DIR)
import getch
from control import Driver
from video import VideoWriter
import camstream
import logging

logging.basicConfig(filename="/var/log/aveta/driving_command.log",
                    level=logging.DEBUG,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nostream",
                        action="store_true",
                        help="Turn off image streaming")

    return parser.parse_args()

def init(nostream):
    scr = curses.initscr()

    curses.noecho()
    curses.cbreak()
    scr.keypad(1)

    stream = None
    if not nostream:
        stream = camstream.CamStream()

    logging.debug("Initialized camstream object")
    def cleanup():
        logging.debug("Cleaning up")
        destroy(scr)
        if stream is not None:
            stream.stop()

    atexit.register(cleanup)
    return scr, stream

def destroy(scr):
    curses.nocbreak()
    scr.keypad(0)
    curses.echo()
    curses.endwin()


KEY_MAP = {
    curses.KEY_UP: "u",
    curses.KEY_DOWN: "d",
    curses.KEY_LEFT: "l",
    curses.KEY_RIGHT: "r",
    ord("h"): "h",
    ord(" "): "s",
}


def main(nostream):
    drv = Driver()

    handlers = {
        "u": drv.speed_ahead,
        "d": drv.speed_back,
        "l": drv.turn_left,
        "r": drv.turn_right,
        "s": drv.straighten_course,
        "h": drv.stop,
    }

    drv.start_drive_mode()
    logging.debug("Put controller in drive mode.")

    scr, stream = init(nostream)
    if stream is not None:
        logging.debug("Initialized streamer")
    else:
        logging.debug('--nostream was given, not streaming to bastion')

    if stream is not None:
        stream.start()
    curses.curs_set(False)  # No blinking cursor
    helpstr = """
Up-Arrow: Speed up
Dn-Arrow: Speed down
Rt-Arrow: Turn right
Lt-Arrow: Turn left
SPC     : Straighten course
h       : Halt"""

    scr.addstr("Aveta Control", curses.A_REVERSE)
    scr.addstr(helpstr)

    scr.nodelay(1) # Non-blocking user input.

    while True:
        scr.refresh()
        h, w = scr.getmaxyx()
        c = scr.getch()
        epoch = time.time()

        if c == curses.ERR:
            scr.move(0, w/2)
            scr.clrtoeol()
            scr.addstr(0, w/2, "%0.2f: no input" % (epoch,))
            continue
        if c == ord('q'):
            logging.debug("User quit")
            break

        if c in KEY_MAP:
            what = KEY_MAP[c]
            # Send a timestamped record of current state and input.
            speeds = drv.get_speeds()
            ts = time.time()
            handlers[what]()
            if stream is not None:
                stream.send_input(ts, what, *speeds)
        else:
            what = "nothing of interest"
            
        scr.move(2, w/2)
        scr.clrtoeol()
        scr.addstr("[Last input] {}: {} pressed".format(epoch, what))
    logging.debug("Shutting down controller")
    drv.quit()
    logging.debug("exit")
    sys.exit(0)

if __name__ == "__main__":
    args = parse_args()
    try:
        main(nostream=args.nostream)
    except Exception as e:
        logging.exception("Uncaught error")
        raise e
