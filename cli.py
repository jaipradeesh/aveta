from __future__ import print_function
import getch
import motion

cmds = {
    'k': 'forward',
    'j': 'backward',
    'l': 'right',
    'h': 'left',
    't': 'stop (gradually)',
    'a': 'stop (abruptly)',
    's': 'straighten course',
    'q': 'quit',
    '?': 'help',
}

def show_help():
    print("Aveta movement keys:")
    print("\t{}".format("\n\t".join("{}: {}".format(key, cmd) for key, cmd in cmds.items())))

if __name__ == "__main__":
    control = motion.MotionController()
    while True:
        c = getch.getch()

        if c in cmds:
            print("<{}>".format(cmds[c]))
        else:
            print("unrecognized input {} (press q to quit, ? for help)".format(c))
            continue

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

    print("Bye.")
        

