from dataclasses import dataclass
from typing import List, Dict, Any
from PySide6.QtCore import QObject, Signal, QTimer, QPoint

@dataclass
class DockItem:
    id: str
    is_app: bool
    path: str
    scale: float = 1.0
    x: float = 0.0
    y: float = 0.0
    width: float = 48.0
    height: float = 48.0

class DockController(QObject):
    items_changed = Signal()
    layout_updated = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.items: List[DockItem] = []
        self.cursor_pos: QPoint = QPoint(-1, -1)
        self.base_size: float = 48.0
        self.max_scale: float = 2.0
        self.falloff_sigma: float = 100.0

    def add_item(self, item: DockItem) -> None:
        self.items.append(item)
        self.items_changed.emit()

    def remove_item(self, item_id: str) -> None:
        self.items = [i for i in self.items if i.id != item_id]
        self.items_changed.emit()

    def reorder(self, old_idx: int, new_idx: int) -> None:
        if 0 <= old_idx < len(self.items) and 0 <= new_idx < len(self.items):
            item = self.items.pop(old_idx)
            self.items.insert(new_idx, item)
            self.items_changed.emit()

    def update_hover(self, pos: QPoint) -> None:
        self.cursor_pos = pos
        self.calculate_layout()

    def calculate_layout(self) -> None:
        # Mocking layout and magnification calculation
        current_x = 0.0
        for item in self.items:
            # Simple distance based scale
            scale = 1.0
            if self.cursor_pos.x() >= 0:
                dist = abs(self.cursor_pos.x() - (current_x + self.base_size / 2))
                if dist < self.falloff_sigma:
                    scale = 1.0 + (self.max_scale - 1.0) * (1.0 - dist / self.falloff_sigma)
            item.scale = scale
            item.width = self.base_size * scale
            item.height = self.base_size * scale
            item.x = current_x
            current_x += item.width + 10.0 # 10px spacing
        
        self.layout_updated.emit()
