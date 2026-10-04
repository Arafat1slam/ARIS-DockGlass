import sys
import os
import atexit
import signal
import traceback

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from single_instance import SingleInstance
from logger import setup_logging, get_logger
from settings_store import SettingsStore
from app_state import AppState
from taskbar_theme import TaskbarTheme
from dock_controller import DockController
from dock_window import DockWindow
from settings_window import SettingsWindow
from tray import TrayIcon
from pinned_apps import PinnedApps
from label_service import LabelService
from constants import APP_NAME

logger = get_logger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    cleanup()

def cleanup():
    logger.info("Cleaning up before exit...")
    # Add cleanup code here (e.g., restoring taskbar)
    TaskbarTheme.restore_default()

def main():
    # 1. Single Instance
    instance = SingleInstance(APP_NAME)
    if not instance.lock():
        sys.exit(0)

    # 2. Setup Logging
    setup_logging()
    logger.info(f"Starting {APP_NAME}...")

    # 3. Create QApplication
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)

    # Crash-safe restore
    sys.excepthook = handle_exception
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())
    signal.signal(signal.SIGTERM, lambda sig, frame: app.quit())

    try:
        # 4. Load Settings
        settings_store = SettingsStore()
        
        # 5. Create app_state
        app_state = AppState(settings_store)
        
        # 6. Create taskbar_theme
        taskbar_theme = TaskbarTheme(app_state)
        taskbar_theme.apply_theme()

        # 7. Create dock_controller
        dock_controller = DockController(app_state)

        # 8. Create dock_window
        dock_window = DockWindow(dock_controller, app_state)
        dock_window.show()

        # 9. Create settings_window (lazy)
        settings_window = None
        def show_settings():
            nonlocal settings_window
            if not settings_window:
                settings_window = SettingsWindow(app_state)
            settings_window.show()
            settings_window.raise_()
            settings_window.activateWindow()

        # 10. Create tray icon
        tray_icon = TrayIcon(app, show_settings, app.quit)
        tray_icon.show()

        # 12. Run event loop
        exit_code = app.exec()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Application error: {e}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
