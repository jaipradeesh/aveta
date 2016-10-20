from __future__ import print_function
import getch
import motion


if __name__ == "__main__":
    control = motion.MotionController()
    while True:
        c = getch.getch()
        if c == 'q':
            break
        elif c == 'j':
            control.speed_ahead()
        elif c == 'k':
            control.speed_back()
        elif c == 'h':
            control.turn_left()
        elif c == 'l':
            control.turn_right()
        elif c == 's':
            control.straighten_course()
        else:
            print("unrecognized input {}".format(c))
        

