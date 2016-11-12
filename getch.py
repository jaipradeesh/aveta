class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self, *args, **kwargs): return self.impl(*args, **kwargs)


class _GetchUnix:
    def __init__(self):
        import tty, sys, select

    def __call__(self, nonblocking=False, timeout=0):
        import sys, tty, termios, select
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        ch = None
        try:
            tty.setraw(sys.stdin.fileno())
            if nonblocking:
                ready_inputs, _, _ = select.select([sys.stdin], [], [], timeout)
                for s in ready_inputs:
                    if s == sys.stdin:
                        ch = sys.stdin.read(1)
            else:
                ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()
