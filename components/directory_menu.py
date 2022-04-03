import curses
import logging
import os

from item import DirectoryItem, sort_items
from menu import Column, TableMenu
from util import SUPPORTED_EXTS, get_media_length, ms_to_hms

from components.base import BaseComponent


class DirectoryMenu(BaseComponent):

    def __init__(self, stdscr, filepath, cursor, select_handler):
        self.stdscr = stdscr
        self.filepath = filepath
        self.cursor = cursor
        self.select_handler = select_handler
        self.title = self.filepath
        self.interactive = True
        self.restart()

    def restart(self):
        """
        Scan the directory and draw the menu.
        """
        scry, scrx = self.stdscr.getmaxyx()
        self.startx = 0
        self.endx = int(scrx / 4) * 3
        self.starty = 0
        self.endy = scry - 8

        # Draw UI placeholder while program scans directory - ???
        self.scan_directory()

        self.component = TableMenu(
            self.stdscr,
            [
                Column('was_played', 2, 'right'),
                Column('title'),
                Column('duration', len("00:00:00") + 2, 'center'),
            ],
            self.items,
            self.starty,
            self.startx,
            self.endy,
            self.endx,
            self.component and self.component.active,
            self.component.selected
            if self.component and self.component.selected
            else 0,
            self.component.scroll_start
            if self.component and self.component.scroll_start
            else 0,
        )

    def scan_directory(self):
        logging.info(f'Scanning directory: {self.filepath}')
        items = []
        if self.filepath != '/':
            items.append(DirectoryItem(self.cursor, self.filepath + '/..'))

        for item in os.listdir(self.filepath):
            if item.startswith('.'):
                continue

            abs_path = os.path.join(self.filepath, item)
            logging.info('Found item: ' + abs_path)
            items.append(DirectoryItem(self.cursor, abs_path))
        
        self._items = list(sort_items(items))        
        # If any new items were added, insert them into the database as one transaction.
        self.cursor.connection.commit()

    def change_directory(self, filepath):
        self.filepath = filepath
        self.title = self.filepath
        self.component.selected = 0
        self.restart()

    @property
    def items(self):
        for item in self._items:
            logging.info(repr(item))
        return [item.as_row() for item in self._items]

    @property
    def selected(self) -> DirectoryItem:
        """
        Returns the selected item. This function duplicates `.items` without metadata (only filenames)
        """
        return self._items[self.component.selected]

    def receive_input(self, key):
        if (key == curses.KEY_ENTER or key == '\n'):
             self.select_handler()
        else:
            self.component.receive_input(key)
