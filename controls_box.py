from component import Component
from menu import Menu
from util import SEEK_STEP


class ControlsBox(Component):
    def restart(self):
        scry, scrx = self.stdscr.getmaxyx()
        self.startx = int(scrx / 4) * 3 + 1
        self.endx = scrx
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
            self.component.selected
            if self.component and self.component.selected else 0,
            self.component.scroll_start
            if self.component and self.component.scroll_start else 0,
        )

    @property
    def items(self):
        return [
            '[ ] Play/Pause',
            f'[→] Skip {SEEK_STEP}s forward',
            f'[←] Skip {SEEK_STEP}s backward',
            '[↑] Previous track',
            '[↓] Next track',
            '[G] Scroll to top',
            '[⇧+G] Scroll to bottom',
            '[O] Skip opening',
            '[Q] Quit',
        ]
