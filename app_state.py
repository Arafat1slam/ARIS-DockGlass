from PySide6.QtCore import QObject, Signal

class AppState(QObject):
    """
    Global enabled/disabled state and signals hub.
    Stores runtime state (not persisted).
    """
    state_changed = Signal(bool)
    config_changed = Signal()
    settings_requested = Signal()
    quit_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._enabled: bool = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        if self._enabled != value:
            self._enabled = value
            self.state_changed.emit(self._enabled)

global_state = AppState()
