import os
import sys
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from logs import SystemMonitor

except ImportError as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

monitor_router = APIRouter()
monitor = SystemMonitor()

@monitor_router.get("/health/cpu", summary="Get CPU usage")
def cpu_usage():
    try:
        data = monitor.check_cpu_usage()
        usage = data.get("cpu_usage", None)
        if usage is None:
            raise ValueError("No CPU data returned")
        return usage  # Return float directly
    except Exception as e:
        log_error(f"Error getting CPU usage: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to retrieve CPU usage"}
        )

@monitor_router.get("/health/memory", summary="Get memory usage")
def memory_usage():
    try:
        data = monitor.check_memory_usage()
        usage = data.get("memory_usage", None)
        if usage is None:
            raise ValueError("No memory data returned")
        return usage  # Return float directly
    except Exception as e:
        log_error(f"Error getting memory usage: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to retrieve memory usage"}
        )

@monitor_router.get("/health/disk", summary="Get disk usage")
def disk_usage():
    try:
        data = monitor.check_disk_usage()
        usage = data.get("disk_usage", None)
        if usage is None:
            raise ValueError("No disk data returned")
        return usage  # Return float directly
    except Exception as e:
        log_error(f"Error getting disk usage: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to retrieve disk usage"}
        )

@monitor_router.get("/health/gpu", summary="Get GPU usage")
def gpu_usage():
    try:
        data = monitor.check_gpu_usage()
        usage = data.get("gpu_usage", None)
        if usage is None or isinstance(usage, str):  # Could be "GPU monitoring unavailable"
            raise NotImplementedError("GPU monitoring not supported or unavailable")
        return usage  # Return int directly
    except NotImplementedError as e:
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"message": "GPU monitoring not supported on this system"}
        )
    except Exception as e:
        log_error(f"Error getting GPU usage: {e}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to retrieve GPU usage"}
        )
