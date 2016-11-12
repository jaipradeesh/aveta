from __future__ import print_function
import time
import getch
from motion import MotionController
from video import VideoWriter
import argparse


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

def is_motion_cmd(c):
    return c in cmds and c not in ('?', 'q')

def show_help():
    print("Aveta movement keys:")
    print("\t{}".format("\n\t".join("{}: {}".format(key, cmd) for key, cmd in cmds.items())))


def write_cmd(c, outstream):
    if outstream is not None:
        epoch = time.time()
        outstream.write("{},{}\n".format(epoch, c))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move aveta")
    parser.add_argument("-o", "--output",
                        help="Path to output file. When given, comma separated "
                             "lines, each containing the epoch and the command "
                             "given at that epoch.")
    args = parser.parse_args()

    outfile = args.output
    outstream = None
    if outfile is not None:
        outstream = open(outfile, "wb")
        print("Writing commands to {}.".format(outfile))
    else:
        print("No output file given")

    control = MotionController()

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

        if is_motion_cmd(c) and outstream is not None:
            write_cmd(c, outstream)

    print("Bye.")
    if outstream is not None:
        outstream.close()
        

