from __future__ import print_function

import sys
import os
import Queue
import multiprocessing as mp

AVETA_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(AVETA_DIR)

import getch
import time
from motion import MotionController

def control_main(cmd_queue, damping=False):
    ctrl = MotionController(verbose=False)
    last_change = time.time()
    while True:
        try:
            cmd = cmd_queue.get_nowait()
            if cmd == "u":
                ctrl.speed_ahead()
            elif cmd == "d":
                ctrl.speed_back()
            elif cmd == "l":
                ctrl.turn_left()
            elif cmd == "r":
                ctrl.turn_right()
            elif cmd == "s":
                ctrl.straighten_course()
            elif cmd == "h":
                ctrl.stop()
            elif cmd == "q":
                ctrl.stop()
                break
            elif damping and ctrl.in_motion():
                t = time.time()
                if t-last_change > 0.1 and ctr.in_motion():
                    last_change = t
                    ctrl.step_towards_zero()
        except Queue.Empty:
            t = time.time()
            if damping and t-last_change > 0.1 and ctrl.in_motion():
                last_change = t
                ctrl.step_towards_zero()

class Driver(object):

    def __init__(self):
        self._init = False
    
    def start_drive_mode(self):
        self.q = mp.Queue()
        self.proc = mp.Process(target=control_main, args=(self.q,))
        self.proc.start()

    def speed_ahead(self):
        self.q.put("u")

    def speed_back(self):
        self.q.put("d")

    def turn_left(self):
        self.q.put("l")

    def turn_right(self):
        self.q.put("r")

    def straighten_course(self):
        self.q.put("s")

    def quit(self):
        self.q.put("q")
        self.proc.join()

    def stop(self):
        self.q.put("h")


if __name__ == "__main__":
    drv = Driver()
    drv.start_drive_mode()
    while True:
        c = getch.getch()
        if c == 'q':
            break
        elif c == '?':
            show_help()
        elif c == 'k':
            drv.speed_ahead()
        elif c == 'j':
            drv.speed_back()
        elif c == 'h':
            drv.turn_left()
        elif c == 'l':
            drv.turn_right()
    drv.stop()



