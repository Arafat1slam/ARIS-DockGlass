"""Path resolution for ARIS DockGlass."""
import os

def get_appdata_dir() -> str:
    """Get the roaming app data directory and ensure it exists."""
    base_dir = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    app_dir = os.path.realpath(os.path.join(base_dir, "ARIS", "TaskbarDock"))
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_localappdata_dir() -> str:
    """Get the local app data directory and ensure it exists."""
    base_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    app_dir = os.path.realpath(os.path.join(base_dir, "ARIS", "TaskbarDock"))
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_logs_dir() -> str:
    """Get the logs directory and ensure it exists."""
    logs_dir = os.path.realpath(os.path.join(get_localappdata_dir(), "logs"))
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def get_cache_dir() -> str:
    """Get the cache directory for icons and ensure it exists."""
    cache_dir = os.path.realpath(os.path.join(get_localappdata_dir(), "cache"))
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir
