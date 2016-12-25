"""Given a command file, write a new command file with two extra columns, for
the left and right wheel velocities. The "velocities" are estimated using
the motion module's inner workings. To be clear, each output row is

    <timestamp>,<command>,<left-velocity>,<right-velocity>

where both velocity values represent the speed _before_ executing the command
(which implies the velocities in the first entry in a file are always zero."""
import argparse
import sys


def read(filename):
    ret = {}
    with open(filename) as fp:
        for line in fp:
            key, value = line.strip().split(",")
            # For command files, there *might* be multiple commands per tick, but
            # we'll just pick the last one in the file.
            ret[key] = value
    return sorted(ret.items(), key=lambda t: t[0])

def _clamp(x):
    if x < -255:
        return -255
    if x > 255:
        return 255
    return x

def _update_velocities(cmd, vels):
    step_size = 3
    if cmd in "udlr":
        if cmd == "u":
            n_steps = (1, 1)
        elif cmd == "d":
            n_steps = (-1, -1)
        elif cmd == "l":
            n_steps = (-1, 1)
        elif cmd == "r":
            n_steps = (1, -1)
        for i in range(len(vels)):
            vels[i] = _clamp(vels[i] + n_steps[i] * step_size)
    elif cmd == "h":
        vels[0] = vels[1] = 0
    elif cmd == "s":
        vels[0] = vels[1] = sum(vels) / 2


def main(cmdfile, outfile):
    cmds = read(cmdfile)
    velocities = [0, 0] # left, right
    with open(outfile, "wb") as out:
        for timestamp, cmd in cmds:
            out.write("{},{},{},{}\n".format(timestamp, cmd, *velocities))
            _update_velocities(cmd, velocities)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cmdfile", help="Input command file")
    parser.add_argument("outfile", help="Output (new-format) command file")

    args = parser.parse_args()
    sys.exit(main(args.cmdfile, args.outfile))
