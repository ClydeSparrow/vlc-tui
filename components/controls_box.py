from menu import Menu
from util import SEEK_STEP

from components.base import BaseComponent


class ControlsBox(BaseComponent):
    def restart(self):
        scry, scrx = self.stdscr.getmaxyx()
        self.startx = int(scrx / 4) * 3 + 1
        self.endx = scrx
        self.starty = 0
        self.endy = scry - 8
        self.component = Menu(
            self.stdscr, self.items, self.starty, self.startx, self.endy, self.endx
        )

    @property
    def items(self):
        return [
            "[ ] Play/Pause",
            f"[→] Skip {SEEK_STEP}s forward",
            f"[←] Skip {SEEK_STEP}s backward",
            "[P] Previous track",
            "[N] Next track",
            "[G] Scroll to top",
            "[⇧+G] Scroll to bottom",
            "[O] Skip opening (+90s)",
            "[Q] Quit",
        ]
