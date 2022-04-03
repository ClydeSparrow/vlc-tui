from component import Component
from menu import Menu
from util import list_files


class PlaylistMenu(Component):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.title = "Playlist"
        self.interactive = True
        self.restart()

    def restart(self):
        scry, scrx = self.stdscr.getmaxyx()
        self.startx = 0
        self.endx = int(scrx / 4) * 3
        self.starty = 0
        self.endy = scry - 8
        self.component = Menu(
            self.stdscr,
            self.items,
            self.starty,
            self.startx,
            self.endy,
            self.endx,
            self.component and self.component.active,
            self.component.selected if self.component and self.component.selected else 0,
            self.component.scroll_start if self.component and self.component.scroll_start else 0,
        )

    @property
    def items(self):
        return sorted(item for item in list_files('/home/pi/Downloads') if item.endswith('.mp4'))

    @property
    def selected(self):
        return self.items[self.component.selected]

    def receive_input(self, key):
        self.component.receive_input(key)
