import logging
import os
import sqlite3


def init_database() -> sqlite3.Connection:
    """
    Initialize the database.
    """
    conn = sqlite3.connect("/tmp/vlc-tui/media.db", check_same_thread=False)
    cursor = conn.cursor()
    create_table(cursor)
    conn.commit()
    return conn


def close(conn: sqlite3.Connection):
    conn.close()


def create_table(cursor: sqlite3.Cursor):
    """
    Create the table if it doesn't exist with fields:
     filepath: absolute path to the media file
     duration: duration in seconds
     stoptime: time in seconds when the media file was stopped
     was_played: boolean, True if the media file was played, False otherwise
    """
    cursor.execute("""CREATE TABLE IF NOT EXISTS media (
        filepath TEXT,
        duration INTEGER,
        stoptime INTEGER,
        was_played BOOLEAN
    )""")


def get_media_details(cursor: sqlite3.Cursor, filepath: str) -> tuple | None:
    """
    Get the details of a media file from the database.
    Returns a tuple of (duration, stoptime, was_played)
    """
    cursor.execute("""SELECT duration, stoptime, was_played FROM media WHERE filepath = ?""", (filepath,))
    media = cursor.fetchone()
    if not media:
        return None
    return (media[0], media[1], media[2])


def insert_media(cursor: sqlite3.Cursor, filepath: str, duration: int, stoptime: int = None, was_played: bool = False):
    """
    Insert a new media file into the database.
    """
    if not filepath or not duration:
        raise ValueError("filepath and duration are required")

    cursor.execute("""INSERT INTO media (filepath, duration, stoptime, was_played)
        VALUES (?, ?, ?, ?)""", (filepath, duration, stoptime, was_played))
    logging.debug(f"Inserted media file: {filepath}")


def update_media(cursor: sqlite3.Cursor, filepath: str, *, stoptime: int = None, was_played: bool = False):
    """
    Update a media file in the database. If was_played is True, then reset stoptime to 0.
    """
    new_stoptime = 0 if was_played else stoptime
    logging.debug(f"Updating media file: {filepath} (stoptime: {new_stoptime})")
    cursor.execute("""UPDATE media SET stoptime = ?
        WHERE filepath = ?""", (new_stoptime, filepath))
    cursor.connection.commit()
