import ctypes
import ctypes.wintypes
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRect, QPoint, QEvent
from PySide6.QtGui import QPainter, QColor, QRegion, QMouseEvent, QPaintEvent
from dock_controller import DockController

user32 = ctypes.windll.user32
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000

class DockWindow(QWidget):
    def __init__(self, controller: DockController) -> None:
        super().__init__()
        self.controller = controller
        
        # Window Flags: Frameless, Top, Tool
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        # Attributes: Translucent, Show without act
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)
        
        # Animation timer (60 fps)
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)
        self.anim_timer.timeout.connect(self.on_frame)
        
        self.controller.layout_updated.connect(self.update)
        self._apply_noactivate()
        self._position_over_taskbar()

    def _apply_noactivate(self) -> None:
        hwnd = int(self.winId())
        ex_style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)

    def _position_over_taskbar(self) -> None:
        hwnd = user32.FindWindowW("Shell_TrayWnd", None)
        if hwnd:
            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            self.setGeometry(rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)

    def on_frame(self) -> None:
        self.controller.calculate_layout()

    def enterEvent(self, event: QEvent) -> None:
        self.anim_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self.anim_timer.stop()
        self.controller.update_hover(QPoint(-1, -1))
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.controller.update_hover(event.pos())
        super().mouseMoveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw dock background
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(10, 10, self.width() - 20, self.height() - 20, 15, 15)
        
        # Update click-through mask
        mask = QRegion(10, 10, self.width() - 20, self.height() - 20, QRegion.RegionType.Rectangle)
        self.setMask(mask)
        
        # Draw items
        for item in self.controller.items:
            painter.setBrush(QColor(255, 255, 255, 200))
            painter.drawEllipse(int(item.x + 20), int(self.height() / 2 - item.height / 2), int(item.width), int(item.height))
