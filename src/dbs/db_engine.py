import os
import sys
import sqlite3
from typing import Optional

FILE_LOCATION = f"{os.path.dirname(__file__)}/create_sqlite_engin.py"

# Add root dir and handle potential import errors
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from helpers import get_settings, Settings
except Exception as e:
    msg = f"Import Error in: {FILE_LOCATION}, Error: {e}"
    raise ImportError(msg)

app_setting: Settings = get_settings()

def get_sqlite_engine(database: Optional[str] = None):
    """
    Creates a connection to an SQLite database.
    If the database does not exist, it will be created.
    """
    try:
        if not database:
            database = app_setting.SQLITE_DB
        # Create a connection to the SQLite database
        conn = sqlite3.connect(database=database)
        log_info(f"Successfully connected to the database: {app_setting.SQLITE_DB}")
        return conn
    except Exception as e:
        log_error(f"Filed to connect to the database: {e}")
        raise
