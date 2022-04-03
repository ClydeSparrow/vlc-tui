import curses
import logging
from component import Component
from util import ms_to_hms, truncate

play_icon = "▶️"
pause_icon = "⏸️"


class NowPlaying(Component):
    def restart(self):
        scry, scrx = self.stdscr.getmaxyx()
        self.startx = 0
        self.endx = scrx - 2
        self.starty = scry - 6
        self.endy = scry - 4
        self.component = NowPlayingComponent(
            self.stdscr,
            self.starty,
            self.startx,
            self.endy,
            self.endx,
        )

class NowPlayingComponent:
    def __init__(self, stdscr, starty, startx, endy, endx):
        self.stdscr = stdscr
        self.starty = starty
        self.startx = startx
        self.endy = endy
        self.endx = endx
        self.active = False
        self.playing = False
        self.track_name = "-"
        self.track_length = 0
        self.time_elapsed = 0
        self.progress_percent = 0

    def render(self, status):
        self.playing = status["state"] == "playing"        
        if self.playing:
            self.track_name = status["title"]
            self.track_length = status["length"]
            self.time_elapsed = status["time"]
            self.progress_percent = self.time_elapsed / self.track_length * 100

        status_symbol = play_icon if self.playing else pause_icon
        timestamp = ms_to_hms(self.time_elapsed) + "/" + ms_to_hms(self.track_length)
        
        max_length = self.endx - self.startx - (len(timestamp) + 3)
        max_length = max_length if max_length > 0 else 0

        progress_length = round(((self.endx - self.startx - 4) / 100) * self.progress_percent)
        track_info = truncate(status_symbol + "  " + self.track_name, max_length)
        
        # Track info line
        self.stdscr.addstr(self.starty, self.startx + 1, track_info)
        self.stdscr.addstr(self.starty, self.endx - len(timestamp), timestamp)

        # Progress bar
        for i in range(round(self.endx - self.startx - 4 - self.progress_percent) + 1):
            self.stdscr.addstr(self.endy, self.endx - 2 - i, "░")

        self.stdscr.attron(curses.color_pair(11))
        self.stdscr.addstr(self.endy, self.startx + 1, "")
        for i in range(0, progress_length + 1):
            self.stdscr.addstr(self.endy, self.startx + 2 + i, "█")
        if self.progress_percent > 99.4:
            self.stdscr.addstr(self.endy, self.endx - 1, "")
        self.stdscr.attroff(curses.color_pair(11))
        if self.progress_percent < 99.5:
            self.stdscr.addstr(self.endy, self.endx - 1, "")
