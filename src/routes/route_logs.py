import os
import sys
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
import aiofiles

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    sys.path.append(MAIN_DIR)

    from src.logs import log_debug, log_error


except ImportError as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

logers_router = APIRouter()

# Define the log file path
LOG_FILE_PATH = f"{MAIN_DIR}/log/app.log"
print(LOG_FILE_PATH)
@logers_router.get("/logs", response_class=PlainTextResponse, status_code=HTTP_200_OK)
async def get_logs():
    """
    Return the content of the application log file.
    """
    # Verify that the log file exists
    if not os.path.exists(LOG_FILE_PATH):
        error_msg = "Log file not found."
        log_error(error_msg)
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=error_msg)

    try:
        # Use asynchronous file I/O to read the log file without blocking the event loop
        async with aiofiles.open(LOG_FILE_PATH, "r", encoding="utf-8") as log_file:
            logs = await log_file.read()
        log_debug("Successfully retrieved log file content.")
        return logs

    except Exception as e:
        error_msg = f"Error reading log file: {str(e)}"
        log_error("Exception occurred while reading the log file.")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)
