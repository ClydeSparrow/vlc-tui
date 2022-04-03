import curses
import os
import sys
import time
from threading import Lock, Thread

import vlc

from components import ControlsBox, DirectoryMenu, NowPlaying, QuitDialog
from item import DirectoryItem
from log import logging
from util import SEEK_STEP

lock = Lock()


class MainForm:
    def __init__(self, stdscr, filepath, cursor) -> None:
        self.stdscr = stdscr
        self.cursor = cursor

        if os.path.isfile(filepath):
            self.filepath = os.path.dirname(os.path.abspath(filepath))
            filename = DirectoryItem(self.cursor, filepath)
        else:
            self.filepath = os.path.abspath(filepath)
            filename = None

        instance = vlc.Instance()
        self.player = instance.media_player_new()
        self.player.set_fullscreen(True)

        self.events = {
            # 155: self.handle_exit,
            # 27: self.handle_exit,
            "q": self.show_quit_dialog,
            curses.KEY_RESIZE: self.handle_resize,
            "o": self.skip_opening,
            "n": self.next_track,
            "p": self.previous_track,
            " ": self.toggle_playback,
            "KEY_RIGHT": self.seek_forward,
            "KEY_LEFT": self.seek_backward,
        }

        # UI components
        self.components = [
            DirectoryMenu(self.stdscr, self.filepath, self.cursor, self.handle_file_selection),
            ControlsBox(self.stdscr),
            NowPlaying(self.stdscr),
        ]

        # Popup components
        self.popup = None
        self.quit_dialog = QuitDialog(self.stdscr, self.hide_popup)

        self.status = {"time": 0, "state": "paused"}

        if filename:
            self.status["state"] = "playing"
            self.play_selected_track(filename)

        # Active media
        self.active_media = None

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
                elif self.popup:
                    self.popup.receive_input(key)
                else:
                    self.components[self.active_component].receive_input(key)
                self.render()
            except Exception as e:
                logging.exception(e)
                sys.exit(0)

    def render(self):
        self.stdscr.erase()
        for component in self.components:
            component.render(self.status)
        if self.popup:
            self.popup.render()
        self.stdscr.refresh()

    def handle_resize(self):
        for component in self.components:
            component.restart()
        self.stdscr.clear()

    def handle_exit(self):
        sys.exit(0)

    def status_loop(self):
        while True:
            try:
                self.status["time"] = self.player.get_time()
                self.status["state"] = "playing" if self.player.is_playing() else "paused"

                with lock:
                    self.render()

                # TODO: Make this configurable
                # TODO: Move inside lock - ???
                if self.status["time"] and self.status["time"] // 1000 % 2 == 0:
                    if self.active_media and self.status["time"] - 1000 > 0:
                        self.active_media.make_savepoint(self.status["time"] - 1000)
            except:
                logging.exception("Error in status loop")
            time.sleep(.5)


    def play_selected_track(self, track: DirectoryItem | None):
        if self.player.is_playing():
            self.player.stop()

        if not track:
            media_item = self.components[0].selected
        else:
            media_item = track

        self.active_media = media_item
        logging.info(f"Active media: {repr(self.active_media)}")

        media = vlc.Media(media_item.filepath)
        logging.info(f"Playing {repr(media_item)}")
        self.player.set_media(media)
        self.player.play()
        if media_item.stoptime:
            self.player.set_time(media_item.stoptime)

        self.status["length"] = media_item.duration
        self.status["title"] = media_item.title

    # =========================
    # Track management methods
    # =========================

    def handle_file_selection(self):
        selected_fn: DirectoryItem = self.components[0].selected
        if not selected_fn.is_media:
            # self.filepath = os.path.abspath(os.path.join(self.filepath, selected_fn))
            self.filepath = os.path.abspath(selected_fn.filepath)
            logging.info(f"Moving to {self.filepath}")
            self.components[0].change_directory(self.filepath)
        else:
            self.status["length"] = self.player.get_length()
            self.status["title"] = selected_fn.title
            self.play_selected_track(selected_fn)

    def toggle_playback(self):
        if self.status["state"] == "playing":
            self.player.pause()
        else:
            self.player.play()

    def skip_opening(self):
        self.player.set_time(self.status["time"] + 88_000)

    def seek_backward(self):
        if self.status["state"] == "playing":
            self.player.set_time(self.status["time"] - SEEK_STEP * 1000)

    def seek_forward(self):
        if self.status["state"] == "playing":
            self.player.set_time(self.status["time"] + SEEK_STEP * 1000)

    def next_track(self):
        """
        Play next media in directory. If last media, do nothing
        """
        # TODO: Fix for DirectoryItem objects
        playing_idx = self.components[0].items.index(self.status["title"])
        if playing_idx == len(self.components[0].items) - 1:
            logging.warning("Reached end of playlist")
            return
        self.play_selected_track(self.components[0].items[playing_idx + 1])

    def previous_track(self):
        """
        Play previous media in directory. If first media, do nothing
        """
        # TODO: Fix for DirectoryItem objects
        playing_idx = self.components[0].items.index(self.status["title"])
        if playing_idx == 0:
            logging.warning("Reached beginning of playlist")
            return
        self.play_selected_track(self.components[0].items[playing_idx - 1])

    # =========================
    # Popup management methods
    # =========================
    
    def show_quit_dialog(self):
        """
        Deactivate the active component and render quit dialog on top of other components
        """
        self.components[self.active_component].deactivate()
        self.popup = self.quit_dialog
        self.popup.restart()
        self.popup.activate()
        self.render()

    def hide_popup(self):
        """
        Hide the popup and return controls to the active component
        """
        if self.popup:
            self.popup.deactivate()
        self.popup = None
        self.components[self.active_component].activate()
        self.stdscr.clear()
        self.render()
