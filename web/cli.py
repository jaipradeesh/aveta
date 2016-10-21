from __future__ import print_function
import getch
import motion

def show_help():
    print("Aveta movement keys:")
    print("\tq: quit\n\tk: move ahead\n\tj: move back\n\th: turn left\n\t"
          "l: turn right\n\ts: straighten course\n\tt: smooth stop\n\t"
          "a: abrupt stop\n\t?: show help")

if __name__ == "__main__":
    control = motion.MotionController()
    while True:
        c = getch.getch()
        if c == 'q':
            break
        elif c == '?':
            show_help()
        elif c == 'k':
            control.speed_ahead()
        elif c == 'j':
            control.speed_back()
        elif c == 'h':
            control.turn_left()
        elif c == 'l':
            control.turn_right()
        elif c == 's':
            control.straighten_course()
        elif c == 't':
            control.stop()
        elif c == 'a':
            control.halt()
        else:
            print("unrecognized input {} (press q to quit, ? for help)".format(c))
    print("Bye.")
        

