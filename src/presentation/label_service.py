import re
from dataclasses import dataclass
from typing import List, Optional
from PySide6.QtCore import QObject, Signal

@dataclass
class LabelStyle:
    font_family: str = "Segoe UI"
    font_size: int = 12
    font_weight: int = 400
    italic: bool = False
    text_color: str = "#FFFFFF"
    bg_color: str = "#00000000"
    opacity: float = 1.0
    radius: int = 4
    padding: int = 4
    alignment: str = "center"

@dataclass
class LabelItem:
    id: str
    text: str
    style: LabelStyle

class LabelService(QObject):
    labels_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._labels: List[LabelItem] = []

    def validate_text(self, text: str) -> str:
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        if not text:
            return "New Label"
        return text[:60]

    def add_label(self, id: str, text: str, style: Optional[LabelStyle] = None) -> None:
        style = style or LabelStyle()
        text = self.validate_text(text)
        self._labels.append(LabelItem(id, text, style))
        self.labels_changed.emit()

    def edit_label(self, id: str, text: str, style: LabelStyle) -> None:
        for idx, lbl in enumerate(self._labels):
            if lbl.id == id:
                self._labels[idx].text = self.validate_text(text)
                self._labels[idx].style = style
                self.labels_changed.emit()
                return

    def remove_label(self, id: str) -> None:
        self._labels = [lbl for lbl in self._labels if lbl.id != id]
        self.labels_changed.emit()

    def duplicate_label(self, id: str, new_id: str) -> None:
        for lbl in self._labels:
            if lbl.id == id:
                import copy
                new_style = copy.deepcopy(lbl.style)
                self.add_label(new_id, f"{lbl.text} (Copy)", new_style)
                return
