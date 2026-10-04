"""Startup registry management for ARIS DockGlass."""
import ctypes
import os
import sys
from ctypes import wintypes
from .win_interop import (
    RegOpenKeyExW, RegSetValueExW, RegDeleteValueW, RegCloseKey,
    HKEY_CURRENT_USER, KEY_SET_VALUE, REG_SZ
)
from .logger import logger

REG_RUN_KEY = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
APP_NAME = "ARIS_TaskbarDock"

def set_run_on_startup(enable: bool) -> bool:
    """Enable or disable running the app on startup via HKCU."""
    hkey = wintypes.HKEY()
    
    # Open the Run key
    res = RegOpenKeyExW(
        HKEY_CURRENT_USER, 
        REG_RUN_KEY, 
        0, 
        KEY_SET_VALUE, 
        ctypes.byref(hkey)
    )
    
    if res != 0:
        logger.error(f"Failed to open registry key: {res}")
        return False
        
    try:
        if enable:
            # Set the path to the executable
            executable = os.path.realpath(sys.executable)
            if not executable.endswith("pythonw.exe") and not executable.endswith(".exe"):
                # Basic fallback if running from script
                executable = os.path.realpath(sys.argv[0])
            
            value = f'"{executable}"'
            value_bytes = (value + "\0").encode('utf-16le')
            
            res = RegSetValueExW(
                hkey,
                APP_NAME,
                0,
                REG_SZ,
                value_bytes,
                len(value_bytes)
            )
            
            if res != 0:
                logger.error(f"Failed to set registry value: {res}")
                return False
        else:
            # Delete the value
            res = RegDeleteValueW(hkey, APP_NAME)
            # ERROR_FILE_NOT_FOUND (2) is fine when deleting
            if res != 0 and res != 2:
                logger.error(f"Failed to delete registry value: {res}")
                return False
                
        return True
    finally:
        RegCloseKey(hkey)
