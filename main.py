from contextlib import contextmanager, redirect_stderr, redirect_stdout
import curses
import os

from main_form import MainForm


@contextmanager
def supress_stdout_stderr():
    """
    Supress stdout and stderr
    """
    with open(os.devnull, "w") as devnull:
        with redirect_stdout(devnull), redirect_stderr(devnull):
            yield None


def init_colors():
    # Default text
    curses.init_pair(1, curses.COLOR_WHITE, 0)
    # White text
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # Yellow text
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    # Magenta text
    curses.init_pair(10, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    # Green text
    curses.init_pair(11, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # Cyan text
    curses.init_pair(12, curses.COLOR_CYAN, curses.COLOR_BLACK)
    # Selected item
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # Highlighted (no bg)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    # Highlighted (bg)
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_MAGENTA)


class App:
    def __init__(self, stdscr):
        init_colors()
        self.main_form = MainForm(stdscr, "/home/pi/Downloads/Unicorn - 20.mp4")
        # self.main_form = MainForm(stdscr)


def main():
    os.environ['VLC_VERBOSE'] = '-1'
    os.environ['XDG_RUNTIME_DIR'] = '/run/user/1000'

    with supress_stdout_stderr():
        curses.wrapper(App)


if __name__ == "__main__":
    main()
