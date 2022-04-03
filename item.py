import logging
import os
from typing import Generator, List

from db import get_media_details, insert_media, update_media
from util import SUPPORTED_EXTS, get_media_length, ms_to_hms


class DirectoryItem:

    __slots__ = ('cursor', 'filepath', 'is_media', 'title', 'duration', 'stoptime', 'was_played')

    def __init__(self, cursor, filepath):
        self.filepath = filepath
        self.cursor = cursor

        if os.path.isdir(filepath):
            self.is_media = False
            self.title = os.path.basename(self.filepath)
            # For directories, we don't need to fill anything else.
            return None
        elif not os.path.splitext(self.filepath)[1] in SUPPORTED_EXTS:
            logging.debug(os.path.splitext(self.filepath))
            raise ValueError(f'Unsupported file type: {self.filepath}')

        self.is_media = True
        self.title = os.path.basename(self.filepath).split('.')[0]

        details = get_media_details(self.cursor, self.filepath)
        if details:
            self.duration = details[0]
            self.stoptime = details[1]
            self.was_played = details[2]
        else:
            # Media not in the database. Get the duration from the file and insert media.
            logging.debug(f'No details found for {self.filepath}')
            self.duration = get_media_length(self.filepath)
            self.stoptime = 0
            self.was_played = False
            insert_media(self.cursor, self.filepath, self.duration)    

    def __repr__(self):
        base = f'<{self.filepath} ({self.is_media})>'
        if self.is_media:
            return base + f' ({self.was_played}, {self.stoptime}, {self.duration})'
        return base

    @property
    def status_icon(self):
        if self.is_media and self.was_played:
            return '✓' 
        elif self.is_media and self.stoptime:
            return '❚❚'
        else:
            return ''

    def make_savepoint(self, stoptime):
        if not self.is_media:
            return

        update_media(self.cursor, self.filepath, stoptime=stoptime)
        self.stoptime = stoptime

    def as_row(self):        
        logging.debug(repr(self))
        return [
            self.status_icon,
            self.title,
            ms_to_hms(self.duration) if self.is_media and self.duration else '',
        ]


def sort_items(items: List[DirectoryItem]) -> Generator[DirectoryItem, None, None]:
    """
    Sort the items in the list by title. Directories are sorted first, then media files.
    """
    dirs = filter(lambda item: not item.is_media, items)
    yield from sorted(dirs, key=lambda item: item.title)

    files = filter(lambda item: item.is_media, items)
    yield from sorted(files, key=lambda item: item.title)
