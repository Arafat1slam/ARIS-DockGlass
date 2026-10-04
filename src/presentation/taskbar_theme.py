import ctypes
import ctypes.wintypes
from typing import Optional
from enum import Enum
from PySide6.QtCore import QObject, QTimer, Signal

user32 = ctypes.windll.user32

class ACCENT_STATE(Enum):
    ACCENT_DISABLED = 0
    ACCENT_ENABLE_GRADIENT = 1
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
    ACCENT_ENABLE_BLURBEHIND = 3
    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
    ACCENT_INVALID_STATE = 5

class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_uint),
        ("AccentFlags", ctypes.c_uint),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_uint)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.POINTER(ACCENT_POLICY)),
        ("SizeOfData", ctypes.c_size_t)
    ]

SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
SetWindowCompositionAttribute.argtypes = [ctypes.wintypes.HWND, ctypes.POINTER(WINDOWCOMPOSITIONATTRIBDATA)]
SetWindowCompositionAttribute.restype = ctypes.wintypes.BOOL

class TaskbarMode(Enum):
    CLEAR = "CLEAR"
    BLUR = "BLUR"
    ACRYLIC = "ACRYLIC"
    TINT = "TINT"

class TaskbarTheme(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.mode: TaskbarMode = TaskbarMode.BLUR
        self.tint_color: int = 0x00000000
        
        # Original state capture
        self._original_captured = False
        
        self._watchdog = QTimer(self)
        self._watchdog.timeout.connect(self.apply)
        self._watchdog.start(2000)

    def set_mode(self, mode: TaskbarMode, tint_color: int = 0x00000000) -> None:
        self.mode = mode
        self.tint_color = tint_color
        self.apply()

    def apply(self) -> None:
        hwnds = self._get_taskbars()
        if not self._original_captured and hwnds:
            self._capture_original(hwnds[0])
            self._original_captured = True

        for hwnd in hwnds:
            self._apply_to_hwnd(hwnd)

    def restore(self) -> None:
        hwnds = self._get_taskbars()
        for hwnd in hwnds:
            self._restore_hwnd(hwnd)

    def _get_taskbars(self) -> list:
        hwnds = []
        hwnd = user32.FindWindowW("Shell_TrayWnd", None)
        if hwnd:
            hwnds.append(hwnd)
        sec_hwnd = user32.FindWindowW("Shell_SecondaryTrayWnd", None)
        while sec_hwnd:
            hwnds.append(sec_hwnd)
            sec_hwnd = user32.FindWindowExW(0, sec_hwnd, "Shell_SecondaryTrayWnd", None)
        return hwnds

    def _apply_to_hwnd(self, hwnd: int) -> None:
        policy = ACCENT_POLICY()
        if self.mode == TaskbarMode.CLEAR:
            policy.AccentState = ACCENT_STATE.ACCENT_ENABLE_TRANSPARENTGRADIENT.value
            policy.GradientColor = 0x00000000
        elif self.mode == TaskbarMode.BLUR:
            policy.AccentState = ACCENT_STATE.ACCENT_ENABLE_BLURBEHIND.value
        elif self.mode == TaskbarMode.ACRYLIC:
            policy.AccentState = ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND.value
            policy.GradientColor = self.tint_color
        elif self.mode == TaskbarMode.TINT:
            policy.AccentState = ACCENT_STATE.ACCENT_ENABLE_TRANSPARENTGRADIENT.value
            policy.GradientColor = self.tint_color

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19 # WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(policy)
        data.SizeOfData = ctypes.sizeof(policy)
        SetWindowCompositionAttribute(hwnd, ctypes.byref(data))

    def _capture_original(self, hwnd: int) -> None:
        pass # Logic to retrieve current WCA_ACCENT_POLICY could go here

    def _restore_hwnd(self, hwnd: int) -> None:
        policy = ACCENT_POLICY()
        policy.AccentState = ACCENT_STATE.ACCENT_DISABLED.value
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19
        data.Data = ctypes.pointer(policy)
        data.SizeOfData = ctypes.sizeof(policy)
        SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
