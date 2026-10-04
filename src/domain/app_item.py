import os
import subprocess
import urllib.parse
import logging
from typing import Any, Optional
from .dock_item import DockItem
from .config_models import AppConfig
from PySide6.QtCore import QRect, Qt, QFileInfo
from PySide6.QtGui import QPainter, QIcon, QColor, QPen, QPixmap
from PySide6.QtWidgets import QFileIconProvider

logger = logging.getLogger(__name__)

class AppItem(DockItem):
    def __init__(self, item_id: str, config: AppConfig, base_size: int = 48):
        super().__init__(item_id)
        self.config = config
        self.base_size = base_size
        self.is_running = False
        self.bounce_offset = 0.0
        self.bounce_velocity = 0.0
        self.bounce_count = 0
        self.is_bouncing = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.x = 0.0
        self.y = 0.0
        self.width = float(base_size)
        self.height = float(base_size)
        self._pixmap: Optional[QPixmap] = None

    @property
    def display_name(self) -> str:
        if self.config.display_name:
            return self.config.display_name
        target = self.config.target
        if not target:
            return "Application"
        base = os.path.basename(target)
        if base.lower().endswith(".exe") or base.lower().endswith(".lnk"):
            base = os.path.splitext(base)[0]
        return base or "App"

    def base_width(self) -> int:
        return self.base_size

    def _load_pixmap(self) -> None:
        target = self.config.icon_path or self.config.target
        if not target:
            return
        try:
            if os.path.exists(target):
                provider = QFileIconProvider()
                icon = provider.icon(QFileInfo(target))
                if not icon.isNull():
                    self._pixmap = icon.pixmap(256, 256)
        except Exception as e:
            logger.debug(f"Could not load icon for {target}: {e}")

    def paint(self, painter: QPainter, rect: QRect, scale: float, state: Any) -> None:
        size = int(self.base_size * scale)
        y_offset = int(self.bounce_offset)
        
        # Center horizontally, and align to bottom baseline with bounce
        icon_rect = QRect(
            rect.center().x() - size // 2,
            rect.bottom() - size - y_offset,
            size,
            size
        )
        
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if self._pixmap is None:
            self._load_pixmap()

        if self.display_name == "Start Menu" or self.config.target == "start-menu":
            gap = max(2, int(3 * scale))
            half = (size - gap) // 2
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 164, 239))
            painter.drawRoundedRect(icon_rect.left(), icon_rect.top(), half, half, 3, 3)
            painter.drawRoundedRect(icon_rect.left() + half + gap, icon_rect.top(), half, half, 3, 3)
            painter.drawRoundedRect(icon_rect.left(), icon_rect.top() + half + gap, half, half, 3, 3)
            painter.drawRoundedRect(icon_rect.left() + half + gap, icon_rect.top() + half + gap, half, half, 3, 3)
        elif self._pixmap and not self._pixmap.isNull():
            painter.drawPixmap(icon_rect, self._pixmap)
        else:
            painter.setBrush(QColor(45, 55, 75, 230))
            painter.setPen(QPen(QColor(255, 255, 255, 70), 1.5))
            painter.drawRoundedRect(icon_rect, max(8, size // 5), max(8, size // 5))
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setBold(True)
            font.setPointSize(max(10, int(size * 0.35)))
            painter.setFont(font)
            initial = (self.display_name or "A")[:1].upper()
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, initial)

        if self.is_running:
            dot_size = max(4, int(4 * scale))
            dot_rect = QRect(
                rect.center().x() - dot_size // 2,
                rect.bottom() + 4,
                dot_size,
                dot_size
            )
            painter.setBrush(QColor(255, 255, 255, 240))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(dot_rect)

        painter.restore()

    def on_click(self) -> None:
        self.trigger_bounce()
        self.launch()

    def launch(self) -> None:
        target = self.config.target
        if not target:
            return

        if target == "start-menu" or self.display_name == "Start Menu":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                VK_LWIN = 0x5B
                KEYEVENTF_KEYUP = 0x0002
                user32.keybd_event(VK_LWIN, 0, 0, 0)
                user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
            except Exception as e:
                logger.error(f"Failed to trigger start menu: {e}")
            return


        parsed = urllib.parse.urlparse(target)
        if parsed.scheme in ('http', 'https'):
            try:
                os.startfile(target)
            except Exception as e:
                logger.error(f"Failed to open URL {target}: {e}")
            return

        if os.path.isdir(target):
            try:
                os.startfile(target)
            except Exception as e:
                logger.error(f"Failed to open directory {target}: {e}")
            return

        try:
            if target.lower().endswith('.lnk'):
                os.startfile(target)
            else:
                args = self.config.args.split() if self.config.args else []
                subprocess.Popen(
                    [target] + args,
                    shell=False,
                    close_fds=True
                )
            self.is_running = True
        except Exception as e:
            logger.error(f"Failed to launch app {target}: {e}")
            try:
                os.startfile(target)
                self.is_running = True
            except Exception:
                pass

    def trigger_bounce(self) -> None:
        self.is_bouncing = True
        self.bounce_offset = 0.0
        self.bounce_velocity = 15.0
        self.bounce_count = 0

    def tick(self, dt: float) -> None:
        if self.is_bouncing:
            self.bounce_offset += self.bounce_velocity
            self.bounce_velocity -= 1.8
            if self.bounce_offset <= 0:
                self.bounce_offset = 0.0
                self.bounce_count += 1
                if self.bounce_count < 3:
                    self.bounce_velocity = 14.0 / (self.bounce_count + 0.6)
                else:
                    self.is_bouncing = False
                    self.bounce_velocity = 0.0
