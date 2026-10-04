import os
from typing import List
from PySide6.QtCore import QObject, Signal

class PinnedAppsManager(QObject):
    apps_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._apps: List[str] = []

    def add_app(self, path_or_url: str) -> bool:
        valid_path = self.validate_path(path_or_url)
        if valid_path and valid_path not in self._apps:
            self._apps.append(valid_path)
            self.apps_changed.emit()
            return True
        return False

    def remove_app(self, path_or_url: str) -> None:
        if path_or_url in self._apps:
            self._apps.remove(path_or_url)
            self.apps_changed.emit()

    def reorder(self, old_index: int, new_index: int) -> None:
        if 0 <= old_index < len(self._apps) and 0 <= new_index < len(self._apps):
            app = self._apps.pop(old_index)
            self._apps.insert(new_index, app)
            self.apps_changed.emit()

    def validate_path(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        try:
            real = os.path.realpath(path)
            if os.path.exists(real):
                return real
        except Exception:
            pass
        return ""

    def get_apps(self) -> List[str]:
        return self._apps.copy()

PinnedApps = PinnedAppsManager

