import sys
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject
from app_state import global_state

class TrayManager(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.tray = QSystemTrayIcon(self)
        # Fallback to standard icon if none exists
        icon = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon)
        self.tray.setIcon(icon)
        
        self.menu = QMenu()
        
        self.action_settings = QAction("Settings", self)
        self.action_settings.triggered.connect(global_state.settings_requested.emit)
        
        self.action_toggle = QAction("Disable DockGlass", self)
        self.action_toggle.triggered.connect(self.toggle_enabled)
        
        self.action_reset = QAction("Reset Taskbar", self)
        
        self.action_quit = QAction("Quit", self)
        self.action_quit.triggered.connect(global_state.quit_requested.emit)
        
        self.menu.addAction(self.action_settings)
        self.menu.addAction(self.action_toggle)
        self.menu.addAction(self.action_reset)
        self.menu.addSeparator()
        self.menu.addAction(self.action_quit)
        
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.on_activated)
        self.tray.show()
        
        global_state.state_changed.connect(self.update_toggle_text)

    def toggle_enabled(self) -> None:
        global_state.enabled = not global_state.enabled

    def update_toggle_text(self, enabled: bool) -> None:
        self.action_toggle.setText("Disable DockGlass" if enabled else "Enable DockGlass")

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            global_state.settings_requested.emit()
