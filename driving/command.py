from __future__ import print_function
import os
import sys
import curses
import atexit
import multiprocessing as mp
import time

AVETA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(AVETA_DIR)
print(AVETA_DIR)
import getch
from control import Driver
from video import VideoWriter
from cam import stream_camera

def init(outfile):
    scr = curses.initscr()
    vid = VideoWriter(outfile)
    camstream = stream_camera()

    curses.noecho()
    curses.cbreak()
    scr.keypad(1)

    def cleanup():
        print("Cleaning up.")
        destroy(scr)
        vid.close()

    atexit.register(cleanup)
    return scr, vid, camstream

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


def main():
    drv = Driver()
    try:
        outfile = sys.argv[1]
    except IndexError:
        outfile = "/home/pi/aveta.avi"

    handlers = {
        "u": drv.speed_ahead,
        "d": drv.speed_back,
        "l": drv.turn_left,
        "r": drv.turn_right,
        "s": drv.straighten_course,
        "h": drv.stop,
    }

    drv.start_drive_mode()

    scr, vid, camstream = init(outfile)
    curses.curs_set(False)  # No blinking cursor
    helpstr = """
Up-Arrow: Speed up
Dn-Arrow: Speed down
Rt-Arrow: Turn right
Lt-Arrow: Turn left
SPC     : Straighten course
h       : Halt

Output video file: {}""".format(outfile)

    scr.addstr("Aveta Control", curses.A_REVERSE)
    scr.addstr(helpstr)

    scr.nodelay(1) # Non-blocking user input.

    while True:
        try:
            frame = next(camstream)
            scr.addstr("wrote frame")
        except StopIteration:
            break
        vid.write_frame(frame)

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
            break

        if c in KEY_MAP:
            what = KEY_MAP[c]
            handlers[what]()
        else:
            what = "nothing of interest"
            
        scr.move(2, w/2)
        scr.clrtoeol()
        scr.addstr("[Last input] {}: {} pressed".format(epoch, what))
    drv.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
