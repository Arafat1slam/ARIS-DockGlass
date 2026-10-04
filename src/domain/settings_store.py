import json
import logging
import os
import time
import shutil
from typing import Optional
from src.infrastructure import paths
from .config_models import Settings

logger = logging.getLogger(__name__)

class SettingsStore:
    def __init__(self, file_path: str = getattr(paths, 'SETTINGS_FILE', 'settings.json')):
        self.file_path = file_path
        self._settings: Optional[Settings] = None

    def load(self) -> Settings:
        if not os.path.exists(self.file_path):
            self._settings = Settings()
            return self._settings

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._settings = Settings.from_dict(data)
            return self._settings
        except Exception as e:
            logger.warning(f"Failed to load settings from {self.file_path}: {e}")
            self._backup_corrupt()
            self._settings = Settings()
            return self._settings

    def save(self, settings: Optional[Settings] = None) -> None:
        if settings is not None:
            self._settings = settings
        if self._settings is None:
            self._settings = Settings()

        data = self._settings.to_dict()
        tmp_path = self.file_path + '.tmp'
        
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.file_path)
        except Exception as e:
            logger.error(f"Failed to save settings to {self.file_path}: {e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def _backup_corrupt(self) -> None:
        if os.path.exists(self.file_path):
            timestamp = int(time.time())
            corrupt_path = f"{self.file_path}.corrupt-{timestamp}.json"
            try:
                shutil.copy2(self.file_path, corrupt_path)
                logger.warning(f"Corrupt settings file backed up to {corrupt_path}")
            except Exception as e:
                logger.error(f"Failed to backup corrupt settings file: {e}")

    def export_json(self, export_path: str) -> bool:
        if self._settings is None:
            self.load()
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings.to_dict(), f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to export settings to {export_path}: {e}")
            return False

    def import_json(self, import_path: str) -> bool:
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._settings = Settings.from_dict(data)
            self.save()
            return True
        except Exception as e:
            logger.error(f"Failed to import settings from {import_path}: {e}")
            return False

    @property
    def path(self) -> str:
        return self.file_path

    def get_all(self) -> dict:
        if self._settings is None:
            self.load()
        return self._settings.to_dict()

    def validate(self, data: dict) -> bool:
        try:
            Settings.from_dict(data)
            return True
        except Exception:
            return False

    def get(self, key: str, default=None):
        if self._settings is None:
            self.load()
        if hasattr(self._settings.dock, key):
            return getattr(self._settings.dock, key)
        if key == 'magnification_scale':
            return self._settings.dock.max_scale
        return default

    def set(self, key: str, value) -> None:
        if self._settings is None:
            self.load()
        if key == 'magnification_scale':
            if value < 1.0 or value > 2.0:
                raise ValueError("Magnification scale must be between 1.0 and 2.0")
            self._settings.dock.max_scale = float(value)
        elif hasattr(self._settings.dock, key):
            setattr(self._settings.dock, key, value)
        else:
            raise KeyError(f"Unknown key: {key}")

