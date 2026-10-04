from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DockItem(ABC):
    """
    Abstract base class for all dock items.
    """
    def __init__(self, item_id: str):
        self.id = item_id

    @abstractmethod
    def base_width(self) -> int:
        pass

    @abstractmethod
    def paint(self, painter: Any, rect: Any, scale: float, state: Any) -> None:
        pass

    @abstractmethod
    def on_click(self) -> None:
        pass

    def on_double_click(self) -> None:
        """Called when item is double-clicked."""
        pass

    def context_actions(self) -> List[Dict[str, Any]]:
        """Return a list of context menu actions (dicts with label, callback)."""
        return []

    def tick(self, dt: float) -> None:
        """Update physics/animations. Called every frame."""
        pass
