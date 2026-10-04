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

        # Window Flags: Frameless, Always on Top, Tool Window (no Alt-Tab)
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
        
        max_icon_h = self.controller.base_size * self.controller.max_scale
        win_height = int(max_icon_h + 36)
        win_width = max(int(self.controller.total_width + 50), 200)
        
        win_x = (geo.width() - win_width) // 2
        win_y = geo.height() - win_height

        self.setGeometry(win_x, win_y, win_width, win_height)
        self.update_click_mask()

    def update_click_mask(self) -> None:
        pill_w = self.controller.total_width + 16
        pill_h = self.controller.base_size + 10
        pill_x = (self.width() - pill_w) / 2.0
        pill_y = self.height() - pill_h - 3
        
        mask_rect = QRect(
            int(pill_x - 6),
            int(pill_y - 30),
            int(pill_w + 12),
            int(pill_h + 36)
        )
        self.setMask(QRegion(mask_rect))


    def on_layout_updated(self) -> None:
        self.update_geometry()
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
        pill_left = (self.width() - self.controller.total_width) / 2.0
        local_x = event.position().x() - pill_left
        self.controller.update_hover(QPoint(int(local_x), int(event.position().y())))
        if not self.anim_timer.isActive():
            self.anim_timer.start()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pill_left = (self.width() - self.controller.total_width) / 2.0
            click_x = event.position().x() - pill_left
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
        
        # Check if clicked on a specific item
        pill_left = (self.width() - self.controller.total_width) / 2.0
        local_pos = self.mapFromGlobal(global_pos)
        click_x = local_pos.x() - pill_left
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

        pill_w = self.controller.total_width + 16
        pill_h = self.controller.base_size + 10
        pill_x = (self.width() - pill_w) / 2.0
        pill_y = self.height() - pill_h - 3
        pill_rect = QRectF(pill_x, pill_y, pill_w, pill_h)

        # 1. macOS Glass Pill Background
        painter.setBrush(QColor(18, 22, 32, 175))
        painter.setPen(QPen(QColor(255, 255, 255, 55), 1.2))
        painter.drawRoundedRect(pill_rect, 14, 14)

        # Inner glossy top reflection
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1.0))
        painter.drawLine(int(pill_x + 14), int(pill_y + 1), int(pill_x + pill_w - 14), int(pill_y + 1))

        # 2. Draw Items
        items_start_x = pill_x + 8.0
        for item in self.controller.items:
            scale = getattr(item, 'scale', 1.0)
            item_center_x = items_start_x + item.x + item.width / 2.0
            
            # Bottom of icon anchored near bottom of pill
            baseline_y = pill_y + pill_h - 5
            
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
            baseline_y = pill_y + pill_h - 10
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
