"""Single instance enforcement for ARIS DockGlass."""
import ctypes
import sys
from ctypes import wintypes
from typing import Optional

SW_RESTORE = 9

def enforce_single_instance() -> Optional[wintypes.HANDLE]:
    """
    Ensure only one instance of the application is running.
    If another instance is found, bring its window to the front and exit.
    Returns the mutex handle if successful, otherwise exits.
    """
    mutex_name = "Global\\ARIS_TaskbarDock_Mutex"
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    
    # Create or open the named mutex
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    
    ERROR_ALREADY_EXISTS = 183
    if last_error == ERROR_ALREADY_EXISTS:
        # Mutex already exists, meaning another instance is running.
        hwnd = user32.FindWindowW(None, "ARIS DockGlass Settings")
        if hwnd:
            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.SetForegroundWindow(hwnd)
        
        sys.exit(0)
    
    return mutex

class SingleInstance:
    def __init__(self, name: str = "ARIS_TaskbarDock"):
        self.name = f"Global\\{name}_Mutex"
        self.mutex = None

    def lock(self) -> bool:
        kernel32 = ctypes.windll.kernel32
        self.mutex = kernel32.CreateMutexW(None, False, self.name)
        last_error = kernel32.GetLastError()
        ERROR_ALREADY_EXISTS = 183
        if last_error == ERROR_ALREADY_EXISTS:
            user32 = ctypes.windll.user32
            hwnd = user32.FindWindowW(None, "ARIS DockGlass Settings")
            if hwnd:
                user32.ShowWindow(hwnd, SW_RESTORE)
                user32.SetForegroundWindow(hwnd)
            return False
        return True

    def unlock(self) -> None:
        if self.mutex:
            ctypes.windll.kernel32.CloseHandle(self.mutex)
            self.mutex = None
