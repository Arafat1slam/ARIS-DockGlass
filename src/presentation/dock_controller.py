import math
import logging
from typing import List, Optional
from PySide6.QtCore import QObject, Signal, QPoint
from src.domain.dock_item import DockItem
from src.domain.app_item import AppItem
from src.domain.label_item import LabelItem
from src.domain.config_models import get_default_dock_items

logger = logging.getLogger(__name__)

class DockController(QObject):
    items_changed = Signal()
    layout_updated = Signal()

    def __init__(self, app_state=None) -> None:
        super().__init__()
        self.app_state = app_state
        self.items: List[DockItem] = []
        self.cursor_pos: QPoint = QPoint(-1000, -1000)
        self.base_size: float = 38.0
        self.max_scale: float = 1.55
        self.falloff_sigma: float = 58.0
        self.spacing: float = 8.0
        self.total_width: float = 0.0
        self.dock_rect_x: float = 0.0
        self.hovered_item: Optional[DockItem] = None
        
        self.load_items()

    def load_items(self) -> None:
        self.items.clear()
        settings = None
        if self.app_state and hasattr(self.app_state, 'settings_store') and self.app_state.settings_store:
            try:
                settings = self.app_state.settings_store.load()
            except Exception as e:
                logger.error(f"Error loading settings in DockController: {e}")
                
        configs = []
        if settings and settings.items:
            configs = settings.items
            self.base_size = float(settings.dock.base_icon_px or 38.0)
            self.max_scale = float(settings.dock.max_scale or 1.55)
            self.falloff_sigma = float(getattr(settings.dock, 'falloff_sigma', 1.4) * self.base_size)
            self.spacing = 8.0

        else:
            configs = get_default_dock_items()

        for cfg in configs:
            if cfg.kind == 'APP' and cfg.app:
                item = AppItem(cfg.id, cfg.app, base_size=int(self.base_size))
                self.items.append(item)
            elif cfg.kind == 'LABEL' and cfg.label:
                item = LabelItem(cfg.id, cfg.label, base_height=int(self.base_size))
                self.items.append(item)

        self.calculate_layout()
        self.items_changed.emit()

    def add_item(self, item: DockItem) -> None:
        self.items.append(item)
        self.calculate_layout()
        self.items_changed.emit()

    def remove_item(self, item_id: str) -> None:
        self.items = [i for i in self.items if i.id != item_id]
        self.calculate_layout()
        self.items_changed.emit()

    def reorder(self, old_idx: int, new_idx: int) -> None:
        if 0 <= old_idx < len(self.items) and 0 <= new_idx < len(self.items):
            item = self.items.pop(old_idx)
            self.items.insert(new_idx, item)
            self.calculate_layout()
            self.items_changed.emit()

    def update_hover(self, pos: QPoint) -> None:
        self.cursor_pos = pos
        if pos.x() >= 0:
            closest_item = None
            min_dist = float('inf')
            for item in self.items:
                center_x = item.x + item.width / 2.0
                dist = abs(pos.x() - center_x)
                if dist < min_dist and dist < item.width / 1.5:
                    min_dist = dist
                    closest_item = item
                if dist < self.falloff_sigma * 2.8:
                    item.target_scale = 1.0 + (self.max_scale - 1.0) * math.exp(-(dist ** 2) / (2.0 * self.falloff_sigma ** 2))
                else:
                    item.target_scale = 1.0
            self.hovered_item = closest_item
        else:
            self.hovered_item = None
            for item in self.items:
                item.target_scale = 1.0

    def tick(self, dt: float = 0.016) -> bool:
        """
        Advance one animation frame. Returns True if animation is still active.
        """
        active = False
        for item in self.items:
            target = getattr(item, 'target_scale', 1.0)
            diff = target - item.scale
            if abs(diff) > 0.002:
                item.scale += diff * 0.32
                active = True
            else:
                item.scale = target
                
            if getattr(item, 'is_bouncing', False):
                item.tick(dt)
                active = True

        self.calculate_layout()
        return active

    def calculate_layout(self) -> None:
        if not self.items:
            self.total_width = 0.0
            self.layout_updated.emit()
            return

        # Calculate item widths
        scaled_widths = []
        for item in self.items:
            w = float(item.base_width()) * getattr(item, 'scale', 1.0)
            item.width = w
            item.height = float(self.base_size) * getattr(item, 'scale', 1.0)
            scaled_widths.append(w)

        self.total_width = sum(scaled_widths) + (len(self.items) - 1) * self.spacing
        
        # Position items sequentially
        curr_x = 0.0
        for i, item in enumerate(self.items):
            item.x = curr_x
            curr_x += item.width + self.spacing

        self.layout_updated.emit()
