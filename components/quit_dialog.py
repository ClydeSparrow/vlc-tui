import curses
import logging
import sys

from menu import Menu

from components.base import BaseComponent


class QuitDialog(BaseComponent):

    BOX_HEIGHT = 4

    def __init__(self, stdscr, close_handler):
        self.stdscr = stdscr
        self.close_handler = close_handler
        self.active = True
        self.popup = True
        self.title = "Quit?"
        self.interactive = True
        self.restart()

    def restart(self):
        scry, scrx = self.stdscr.getmaxyx()
        box_width = round(scrx / 3)
        self.startx = round((scrx / 2) - (box_width / 2))
        self.endx = self.startx + box_width
        self.starty = round((scry / 2) - (self.BOX_HEIGHT / 2))
        self.endy = self.starty + self.BOX_HEIGHT

        self.component = Menu(
            self.stdscr,
            ['Yes', 'No'],
            self.starty,
            self.startx,
            self.endy,
            self.endx,
        )

    def receive_input(self, key):
        if key == curses.KEY_ENTER or key == '\n':
            if self.component.selected == 0:
                sys.exit(0)
            self.close_handler()
        else:
            self.component.receive_input(key)
