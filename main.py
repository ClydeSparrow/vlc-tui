import argparse
import curses
import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from email import parser
from functools import partial

from db import init_database
from main_form import MainForm
from util import SUPPORTED_EXTS


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
    def __init__(self, stdscr, filepath, cursor):
        init_colors()
        self.main_form = MainForm(stdscr, filepath, cursor)


def validate_filepath(filepath):
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError(f"Filepath '{filepath}' does not exist")
    if (
        os.path.isfile(filepath)
        and not os.path.splitext(filepath)[1] in SUPPORTED_EXTS
        # os.path.basename(filepath).split(".")[-1] in SUPPORTED_EXTS
    ):
        raise argparse.ArgumentTypeError(
            f"File '{filepath}' is not a supported filetype"
        )
    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VLC Terminal Player")
    parser.add_argument(
        "player_path", type=str, help="Path to directory or file to play"
    )
    args = parser.parse_args()

    validate_filepath(args.player_path)

    os.environ["VLC_VERBOSE"] = "-1"
    os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"

    conn = init_database()

    app_partial = partial(App, filepath=args.player_path, cursor=conn.cursor())
    with supress_stdout_stderr():
        curses.wrapper(app_partial)
    conn.close()
