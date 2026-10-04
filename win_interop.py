"""Win32 API interoperability for ARIS DockGlass."""
import ctypes
from ctypes import wintypes

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
ACCENT_DISABLED = 0
ACCENT_ENABLE_GRADIENT = 2
ACCENT_ENABLE_TRANSPARENTGRADIENT = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

SHGFI_ICON = 0x000000100
SHGFI_LARGEICON = 0x000000000
SHGFI_SMALLICON = 0x000000001

HKEY_CURRENT_USER = 0x80000001
KEY_SET_VALUE = 0x0002
REG_SZ = 1

# ----------------------------------------------------------------------------
# Structures
# ----------------------------------------------------------------------------
class ACCENTPOLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_uint),
        ("AccentFlags", ctypes.c_uint),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_uint),
    ]

class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_uint),
        ("Data", ctypes.POINTER(ctypes.c_void_p)),
        ("SizeOfData", ctypes.c_size_t),
    ]

class SHFILEINFOW(ctypes.Structure):
    _fields_ = [
        ("hIcon", wintypes.HICON),
        ("iIcon", ctypes.c_int),
        ("dwAttributes", wintypes.DWORD),
        ("szDisplayName", wintypes.WCHAR * 260),
        ("szTypeName", wintypes.WCHAR * 80),
    ]

# ----------------------------------------------------------------------------
# User32 Functions
# ----------------------------------------------------------------------------
user32 = ctypes.windll.user32

try:
    SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
    SetWindowCompositionAttribute.argtypes = [wintypes.HWND, ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA)]
    SetWindowCompositionAttribute.restype = wintypes.BOOL
except AttributeError:
    SetWindowCompositionAttribute = None

FindWindowW = user32.FindWindowW
FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
FindWindowW.restype = wintypes.HWND

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
EnumWindows = user32.EnumWindows
EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
EnumWindows.restype = wintypes.BOOL

GetWindowRect = user32.GetWindowRect
GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
GetWindowRect.restype = wintypes.BOOL

if ctypes.sizeof(ctypes.c_void_p) == 8:
    SetWindowLongPtrW = user32.SetWindowLongPtrW
    SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LPARAM]
    SetWindowLongPtrW.restype = wintypes.LPARAM

    GetWindowLongPtrW = user32.GetWindowLongPtrW
    GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    GetWindowLongPtrW.restype = wintypes.LPARAM
else:
    SetWindowLongPtrW = user32.SetWindowLongW
    SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
    SetWindowLongPtrW.restype = wintypes.LONG

    GetWindowLongPtrW = user32.GetWindowLongW
    GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
    GetWindowLongPtrW.restype = wintypes.LONG

DestroyIcon = user32.DestroyIcon
DestroyIcon.argtypes = [wintypes.HICON]
DestroyIcon.restype = wintypes.BOOL

RegisterWindowMessageW = user32.RegisterWindowMessageW
RegisterWindowMessageW.argtypes = [wintypes.LPCWSTR]
RegisterWindowMessageW.restype = wintypes.UINT

# ----------------------------------------------------------------------------
# Shell32 Functions
# ----------------------------------------------------------------------------
shell32 = ctypes.windll.shell32

SHGetFileInfoW = shell32.SHGetFileInfoW
SHGetFileInfoW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(SHFILEINFOW), ctypes.c_uint, ctypes.c_uint]
SHGetFileInfoW.restype = wintypes.DWORD

# ----------------------------------------------------------------------------
# Advapi32 Functions
# ----------------------------------------------------------------------------
advapi32 = ctypes.windll.advapi32

RegOpenKeyExW = advapi32.RegOpenKeyExW
RegOpenKeyExW.argtypes = [wintypes.HKEY, wintypes.LPCWSTR, wintypes.DWORD, wintypes.REGSAM, ctypes.POINTER(wintypes.HKEY)]
RegOpenKeyExW.restype = wintypes.LONG

RegSetValueExW = advapi32.RegSetValueExW
RegSetValueExW.argtypes = [wintypes.HKEY, wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPBYTE, wintypes.DWORD]
RegSetValueExW.restype = wintypes.LONG

RegDeleteValueW = advapi32.RegDeleteValueW
RegDeleteValueW.argtypes = [wintypes.HKEY, wintypes.LPCWSTR]
RegDeleteValueW.restype = wintypes.LONG

RegCloseKey = advapi32.RegCloseKey
RegCloseKey.argtypes = [wintypes.HKEY]
RegCloseKey.restype = wintypes.LONG
