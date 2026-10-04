import ctypes
import ctypes.wintypes
from typing import Optional
from PySide6.QtWidgets import QWidget, QApplication, QMenu
from PySide6.QtCore import Qt, QTimer, QRect, QRectF, QPoint, QEvent
from PySide6.QtGui import (
    QPainter, QColor, QRegion, QMouseEvent, QPaintEvent,
    QPen, QFont, QFontMetrics, QAction
)
from .dock_controller import DockController

user32 = ctypes.windll.user32
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000

class DockWindow(QWidget):
    def __init__(self, controller: DockController, app_state=None) -> None:
        super().__init__()
        self.controller = controller
        self.app_state = app_state

        # Window Flags: Frameless, Always on Top, Tool Window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Translucent background & no activation focus
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

        # 60 FPS animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)
        self.anim_timer.timeout.connect(self.on_frame)

        self.controller.layout_updated.connect(self.on_layout_updated)
        self.controller.items_changed.connect(self.on_layout_updated)

        self._apply_noactivate()
        self.update_geometry()

    def _apply_noactivate(self) -> None:
        try:
            hwnd = int(self.winId())
            ex_style = user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)
        except Exception:
            pass

    def update_geometry(self) -> None:
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.geometry()
        
        # Room for upwards magnification wave (60px icon height + margin)
        win_height = 80
        win_width = geo.width()
        
        # Span across the screen horizontally, anchored right at the bottom
        win_x = 0
        win_y = geo.height() - win_height

        self.setGeometry(win_x, win_y, win_width, win_height)
        self.update_click_mask()

    def update_click_mask(self) -> None:
        # Mask strictly around the middle dock icons area so Start button & Tray are 100% clickable!
        items_w = self.controller.total_width + 24
        items_x = (self.width() - items_w) / 2.0
        
        mask_rect = QRect(
            int(items_x),
            0,
            int(items_w),
            self.height()
        )
        self.setMask(QRegion(mask_rect))

    def on_layout_updated(self) -> None:
        self.update_click_mask()
        self.update()

    def on_frame(self) -> None:
        active = self.controller.tick(0.016)
        self.update()
        if not active and not self.underMouse():
            self.anim_timer.stop()

    def enterEvent(self, event: QEvent) -> None:
        self.anim_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self.controller.update_hover(QPoint(-1000, -1000))
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        items_start_x = (self.width() - self.controller.total_width) / 2.0
        local_x = event.position().x() - items_start_x
        self.controller.update_hover(QPoint(int(local_x), int(event.position().y())))
        if not self.anim_timer.isActive():
            self.anim_timer.start()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            items_start_x = (self.width() - self.controller.total_width) / 2.0
            click_x = event.position().x() - items_start_x
            for item in self.controller.items:
                if item.x <= click_x <= item.x + item.width:
                    item.on_click()
                    if not self.anim_timer.isActive():
                        self.anim_timer.start()
                    break
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def _show_context_menu(self, global_pos: QPoint) -> None:
        menu = QMenu(self)
        
        items_start_x = (self.width() - self.controller.total_width) / 2.0
        local_pos = self.mapFromGlobal(global_pos)
        click_x = local_pos.x() - items_start_x
        clicked_item = None
        for item in self.controller.items:
            if item.x <= click_x <= item.x + item.width:
                clicked_item = item
                break

        if clicked_item:
            act_launch = QAction(f"Open {clicked_item.display_name}", self)
            act_launch.triggered.connect(clicked_item.on_click)
            menu.addAction(act_launch)
            
            act_remove = QAction("Remove from Dock", self)
            act_remove.triggered.connect(lambda: self.controller.remove_item(clicked_item.id))
            menu.addAction(act_remove)
            menu.addSeparator()

        act_settings = QAction("DockGlass Settings", self)
        if self.app_state:
            act_settings.triggered.connect(self.app_state.settings_requested.emit)
        menu.addAction(act_settings)

        act_quit = QAction("Quit DockGlass", self)
        if self.app_state:
            act_quit.triggered.connect(self.app_state.quit_requested.emit)
        else:
            act_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(act_quit)

        menu.exec(global_pos)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        items_start_x = (self.width() - self.controller.total_width) / 2.0
        # Bottom of icons aligns with the taskbar icons baseline
        baseline_y = self.height() - 4

        # 1. Subtle sleek hover glow shelf under the middle items
        if self.underMouse() or self.controller.hovered_item:
            glow_w = self.controller.total_width + 20
            glow_rect = QRectF(items_start_x - 10, baseline_y - self.controller.base_size - 4, glow_w, self.controller.base_size + 8)
            painter.setBrush(QColor(255, 255, 255, 12))
            painter.setPen(QPen(QColor(255, 255, 255, 25), 1.0))
            painter.drawRoundedRect(glow_rect, 10, 10)

        # 2. Draw Items with Mac Magnification Wave
        for item in self.controller.items:
            scale = getattr(item, 'scale', 1.0)
            item_center_x = items_start_x + item.x + item.width / 2.0
            
            item_draw_rect = QRect(
                int(item_center_x - item.width / 2.0),
                int(baseline_y - item.height),
                int(item.width),
                int(item.height)
            )
            item.paint(painter, item_draw_rect, scale, None)

        # 3. macOS Floating Tooltip Bubble
        hovered = self.controller.hovered_item
        if hovered and hovered.display_name:
            scale = getattr(hovered, 'scale', 1.0)
            item_center_x = items_start_x + hovered.x + hovered.width / 2.0
            top_y = baseline_y - (hovered.height * scale) - getattr(hovered, 'bounce_offset', 0)
            
            font = QFont("Segoe UI", 9)
            font.setBold(True)
            painter.setFont(font)
            fm = QFontMetrics(font)
            
            text = hovered.display_name
            text_w = fm.horizontalAdvance(text) + 16
            text_h = fm.height() + 8
            
            tip_rect = QRectF(
                item_center_x - text_w / 2.0,
                top_y - text_h - 6,
                text_w,
                text_h
            )
            
            painter.setBrush(QColor(15, 18, 26, 225))
            painter.setPen(QPen(QColor(255, 255, 255, 40), 1.0))
            painter.drawRoundedRect(tip_rect, 6, 6)
            
            painter.setPen(QColor(255, 255, 255, 240))
            painter.drawText(tip_rect, Qt.AlignmentFlag.AlignCenter, text)
