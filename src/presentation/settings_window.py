from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout, QComboBox, 
    QSlider, QCheckBox, QPushButton, QLabel, QColorDialog, QLineEdit, QHBoxLayout
)
from PySide6.QtCore import Qt

class SettingsWindow(QWidget):
    def __init__(self, app_state=None) -> None:
        super().__init__()
        self.app_state = app_state
        self.setWindowTitle("DockGlass Settings")

        self.resize(600, 450)
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)
        
        self._init_taskbar_tab()
        self._init_dock_tab()
        self._init_labels_tab()
        self._init_general_tab()

    def _init_taskbar_tab(self) -> None:
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.mode_cb = QComboBox()
        self.mode_cb.addItems(["CLEAR", "BLUR", "ACRYLIC", "TINT"])
        
        self.btn_color = QPushButton("Pick Tint Color")
        self.btn_color.clicked.connect(self._pick_color)
        
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(0, 255)
        
        self.cb_hide_taskbar = QCheckBox("Hide Native Windows Taskbar (macOS Style)")
        self.cb_hide_taskbar.setChecked(True)
        
        layout.addRow("Taskbar Mode:", self.mode_cb)
        layout.addRow("Tint Color:", self.btn_color)
        layout.addRow("Opacity:", self.slider_opacity)
        layout.addRow("", self.cb_hide_taskbar)
        self.tabs.addTab(tab, "Taskbar")


    def _init_dock_tab(self) -> None:
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.pos_cb = QComboBox()
        self.pos_cb.addItems(["CENTER", "LEFT", "RIGHT"])
        
        self.offset_spin = QLineEdit() # Replace with spinbox in full implementation
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.falloff_slider = QSlider(Qt.Orientation.Horizontal)
        
        layout.addRow("Position:", self.pos_cb)
        layout.addRow("Vertical Offset:", self.offset_spin)
        layout.addRow("Base Icon Size:", self.size_slider)
        layout.addRow("Max Scale:", self.max_scale_slider)
        layout.addRow("Falloff Sigma:", self.falloff_slider)
        self.tabs.addTab(tab, "Dock")

    def _init_labels_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("Add Label"))
        btn_layout.addWidget(QPushButton("Edit Selected"))
        btn_layout.addWidget(QPushButton("Remove Selected"))
        btn_layout.addWidget(QPushButton("Duplicate"))
        
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Label styles editor goes here (font, size, weight, italic, colors, etc)"))
        self.tabs.addTab(tab, "Labels")

    def _init_general_tab(self) -> None:
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.chk_startup = QCheckBox("Start with Windows")
        
        self.log_cb = QComboBox()
        self.log_cb.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        
        btn_import = QPushButton("Import Config")
        btn_export = QPushButton("Export Config")
        
        layout.addRow("", self.chk_startup)
        layout.addRow("Log Level:", self.log_cb)
        layout.addRow("Configuration:", btn_import)
        layout.addRow("", btn_export)
        self.tabs.addTab(tab, "General")

    def _pick_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            pass # Apply live
