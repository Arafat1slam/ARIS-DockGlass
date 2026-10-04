import os
import subprocess
import urllib.parse
import logging
from typing import Any
from .dock_item import DockItem
from .config_models import AppConfig
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QIcon, QColor, QPen

logger = logging.getLogger(__name__)

class AppItem(DockItem):
    def __init__(self, item_id: str, config: AppConfig, base_size: int = 48):
        super().__init__(item_id)
        self.config = config
        self.base_size = base_size
        self.is_running = False
        self.bounce_offset = 0.0
        self.bounce_velocity = 0.0
        self.is_bouncing = False

    def base_width(self) -> int:
        return self.base_size

    def paint(self, painter: QPainter, rect: QRect, scale: float, state: Any) -> None:
        size = int(self.base_size * scale)
        y_offset = int(self.bounce_offset)
        
        icon_rect = QRect(
            rect.center().x() - size // 2,
            rect.center().y() - size // 2 - y_offset,
            size,
            size
        )
        
        if self.config.icon_path and os.path.exists(self.config.icon_path):
            icon = QIcon(self.config.icon_path)
            icon.paint(painter, icon_rect)
        else:
            painter.setBrush(QColor('#444444'))
            painter.setPen(QPen(QColor('#ffffff'), 1))
            painter.drawRoundedRect(icon_rect, size // 4, size // 4)

        if self.is_running:
            dot_size = int(4 * scale)
            if dot_size < 2:
                dot_size = 2
            dot_rect = QRect(
                rect.center().x() - dot_size // 2,
                rect.bottom() - dot_size - 2,
                dot_size,
                dot_size
            )
            painter.setBrush(QColor('#ffffff'))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(dot_rect)

    def on_click(self) -> None:
        self.trigger_bounce()
        self.launch()

    def launch(self) -> None:
        target = self.config.target
        if not target:
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
            args = self.config.args.split() if self.config.args else []
            subprocess.Popen(
                [target] + args,
                shell=False,
                close_fds=True
            )
            self.is_running = True
        except Exception as e:
            logger.error(f"Failed to launch app {target}: {e}")

    def trigger_bounce(self) -> None:
        self.is_bouncing = True
        self.bounce_velocity = 15.0

    def tick(self, dt: float) -> None:
        if self.is_bouncing:
            self.bounce_offset += self.bounce_velocity
            self.bounce_velocity -= 2.0
            if self.bounce_offset <= 0:
                self.bounce_offset = 0.0
                self.bounce_velocity = 0.0
                self.is_bouncing = False
