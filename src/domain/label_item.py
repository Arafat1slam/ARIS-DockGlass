from typing import Any, Optional
from .dock_item import DockItem
from .config_models import LabelConfig
from PySide6.QtCore import QRect, QRectF, Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPainterPath, QPixmap

class LabelItem(DockItem):
    def __init__(self, item_id: str, config: LabelConfig, base_height: int = 48):
        super().__init__(item_id)
        self.config = config
        self.base_height = base_height
        self._base_width = max(60, len(config.text) * 12 + 24)
        self.scale = 1.0
        self.target_scale = 1.0
        self.x = 0.0
        self.y = 0.0
        self.width = float(self._base_width)
        self.height = float(base_height)
        self.bounce_offset = 0.0
        self._pixmap: Optional[QPixmap] = None

    @property
    def display_name(self) -> str:
        return self.config.text or "Label"

    def base_width(self) -> int:
        return self._base_width

    def paint(self, painter: QPainter, rect: QRect, scale: float, state: Any) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        effective_scale = scale if self.config.magnify else 1.0
        
        w = int(self.base_width() * effective_scale)
        h = int(self.base_height * effective_scale)
        
        draw_rect = QRectF(
            rect.center().x() - w / 2.0,
            rect.bottom() - h,
            w,
            h
        )
        
        path = QPainterPath()
        radius = float(self.config.corner_radius) * effective_scale
        path.addRoundedRect(draw_rect, radius, radius)
        
        bg_color = QColor(self.config.bg_color)
        bg_color.setAlpha(int(self.config.bg_opacity * 255 / 100))
        painter.fillPath(path, bg_color)
        
        font = QFont(self.config.font_family, max(9, int(self.config.font_size * effective_scale)))
        font.setBold(self.config.is_bold)
        font.setItalic(self.config.is_italic)
        painter.setFont(font)
        
        text_color = QColor(self.config.text_color)
        painter.setPen(text_color)
        painter.drawText(draw_rect, Qt.AlignmentFlag.AlignCenter, self.config.text)
        
        painter.restore()

    def on_click(self) -> None:
        pass

    def on_double_click(self) -> None:
        pass

    def tick(self, dt: float) -> None:
        pass
