"""Domain layer - Pure business logic, models, and math (no Qt, no ctypes)."""

from .config_models import Settings, TaskbarSettings, DockSettings, GeneralSettings
from .config_models import DockItemConfig, AppConfig, LabelConfig
from .magnification import compute_scale, ease_toward
from .dock_layout import calculate_layout

__all__ = [
    "Settings",
    "TaskbarSettings",
    "DockSettings",
    "GeneralSettings",
    "DockItemConfig",
    "AppConfig",
    "LabelConfig",
    "compute_scale",
    "ease_toward",
    "calculate_layout",
]
