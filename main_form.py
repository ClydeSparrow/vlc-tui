import curses
import os
import sys
import time
import vlc
from threading import Thread, Lock
from controls_box import ControlsBox
from now_playing import NowPlaying
from playlist_menu import PlaylistMenu
from log import logging
from util import SEEK_STEP, ms_to_hms


lock = Lock()


class MainForm:
    def __init__(self, stdscr, filename = None) -> None:
        self.stdscr = stdscr

        instance = vlc.Instance()
        self.player = instance.media_player_new()        

        self.events = {
            # 155: self.handle_exit,
            # 27: self.handle_exit,
            'q': self.handle_exit,
            curses.KEY_RESIZE: self.handle_resize,
            'o': self.skip_opening,
            # 'n': "Switch to next file",
            # 'p': "Switch to previous file",
            ' ': self.toggle_playback,
            '\n': self.play_selected_file,
            'KEY_RIGHT': self.seek_forward,
            'KEY_LEFT': self.seek_backward,
        }

        # UI components
        self.components = [
            PlaylistMenu(self.stdscr),
            ControlsBox(self.stdscr),
            NowPlaying(self.stdscr),
        ]

        if filename:
            media = instance.media_new(filename)
            self.player.set_media(media)

            self.player.play()
            time.sleep(.2)

            self.status = {
                'title': os.path.basename(filename),
                'length': self.player.get_length(),
                'time': 0,
                'state': 'playing'
            }
        else:
            self.status = {
                'title': '-',
                'length': 0,
                'time': 0,
                'state': 'paused'
            }

        # Active component
        self.active_component = 0
        self.components[0].activate()

        # Initial render
        self.render()

        # Poll playing status every second in a new thread
        status_loop = Thread(target=self.status_loop)
        status_loop.daemon = True
        status_loop.start()

        while True:
            try:
                key = self.stdscr.getkey()
                if key in self.events:
                    self.events[key]()
                else:
                    self.components[self.active_component].receive_input(key)
                self.render()
            except Exception as e:
                sys.exit(0)

    def render(self):
        self.stdscr.erase()
        for component in self.components:
            component.render(self.status)
        self.stdscr.refresh()

    def handle_resize(self):
        for component in self.components:
            component.restart()
        self.stdscr.clear()

    def handle_exit(self):
        sys.exit(0)

    def status_loop(self):
        while True:
            self.status['time'] = self.player.get_time()
            self.status['state'] = 'playing' if self.player.is_playing() else 'paused'

            with lock:
                self.render()
            
            time.sleep(.5)

    def play_selected_file(self):
        if self.player.is_playing():
            self.player.stop()

        new_fn = self.components[0].selected
        media = vlc.Media('/home/pi/Downloads/' + new_fn)
        self.player.set_media(media)
        self.player.play()

        time.sleep(.2)
        self.status['length'] = self.player.get_length()
        self.status['title'] = new_fn

    # Track management methods
    def toggle_playback(self):
        if self.status['state'] == 'playing':
            self.player.pause()
        else:
            self.player.play()

    def skip_opening(self):
        self.player.set_time(self.status['time'] + 90_000)

    def seek_backward(self):
        if self.status['state'] == 'playing':
            self.player.set_time(self.status['time'] - SEEK_STEP * 1000)

    def seek_forward(self):
        if self.status['state'] == 'playing':
            self.player.set_time(self.status['time'] + SEEK_STEP * 1000)
