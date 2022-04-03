import curses
from dataclasses import dataclass
from typing import Literal


class Menu:
    def __init__(
        self,
        stdscr,
        items=[],
        starty=0,
        startx=0,
        endy=0,
        endx=0,
        active=False,
        selected=0,
        scroll_start=0,
    ):
        self.stdscr = stdscr
        self.starty = starty + 2
        self.startx = startx + 2
        self.endy = endy - 1
        self.endx = endx - 2
        self.items = items
        self.selected = selected
        self.active = active
        self.available_space = self.endy - self.starty + 1
        self.scroll_start = scroll_start
        self.scroll_end = (
            len(items) - 1
            if len(items) <= self.available_space + self.scroll_start
            else self.available_space + self.scroll_start - 1
        )

    def select(self, index):
        if index >= 0 and index <= len(self.items) - 1:
            self.selected = index

    def render(self, status: dict = None):
        scry, scrx = self.stdscr.getmaxyx()
        for i, item_idx in enumerate(range(self.scroll_start, self.scroll_end + 1)):
            item = self.items[item_idx]
            x = self.startx
            y = self.starty + i
            selected = item_idx == self.selected and self.active
            if y >= 0 and y <= scry and x >= 0 and x <= scrx:
                color = None
                if status and 'title' in status and item == status['title']:
                    color = 12
                if selected:
                    color = 6
                self.print_string(y, x, item, color)

    def receive_input(self, key):
        if key == 'KEY_UP':
            self.select((self.selected - 1) % len(self.items))
        if key == 'KEY_DOWN':
            self.select((self.selected + 1) % len(self.items))
        if key == 'g' and self.selected > 0:
            self.select(0)
        if key == 'G' and self.selected < len(self.items) - 1:
            self.select(len(self.items) - 1)
        if self.selected < self.scroll_start:
            self.scroll_up(self.scroll_start - self.selected)
        if self.selected > self.scroll_end:
            self.scroll_down(self.selected - self.scroll_end)

    def scroll_up(self, amount):
        self.scroll_start -= amount
        self.scroll_end -= amount

    def scroll_down(self, amount):
        self.scroll_start += amount
        self.scroll_end += amount

    def print_string(self, y, x, text, color):
        if color:
            self.stdscr.attron(curses.color_pair(color))
        self.stdscr.addstr(y, x, text)
        if color:
            self.stdscr.attroff(curses.color_pair(color))


@dataclass
class Column:
    name: str
    width: int = 0
    align: Literal['left', 'center', 'right'] = 'left'

    def align_item(self, item) -> str:
        """Returns aligned string based on cell value"""
        if self.align == 'left':
            return f'{item:<{self.width}}'
        elif self.align == 'right':
            return f'{item:>{self.width}}'
        else:
            return f'{item:^{self.width}}'


class TableMenu(Menu):

    SEPARATOR = ' '

    def __init__(
        self,
        stdscr,
        columns,
        items=[],
        starty=0,
        startx=0,
        endy=0,
        endx=0,
        active=False,
        selected=0,
        scroll_start=0,
    ):
        self.columns = columns
        free_row_width = endx - startx - 2
        free_row_width -= len(self.SEPARATOR) * (len(self.columns) - 1) 
        free_row_width -= sum([c.width for c in self.columns])

        if free_row_width < 0:
            raise Exception('Table too wide')

        flexible_cols = [c for c in columns if c.width == 0]
        for col in flexible_cols:
            col.width = free_row_width // len(flexible_cols)

        super().__init__(stdscr, items, starty, startx, endy, endx, active, selected, scroll_start)

    def render_table_row(self, row) -> str:
        """
        Returns a string representation of a table row
        """
        return self.SEPARATOR.join([self.columns[i].align_item(item) for i, item in enumerate(row)])

    def render(self, status: dict = None):
        scry, scrx = self.stdscr.getmaxyx()
        for i, item_idx in enumerate(range(self.scroll_start, self.scroll_end + 1)):
            item = self.items[item_idx]
            x = self.startx
            y = self.starty + i
            selected = item_idx == self.selected and self.active

            if y >= 0 and y <= scry and x >= 0 and x <= scrx:
                color = None
                if 'title' in status and status['title'] == item[1]:
                    color = 12
                if selected:
                    color = 6
                self.print_string(y, x, self.render_table_row(item), color)
