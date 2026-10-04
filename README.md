<p align="center">
  <img src="https://img.shields.io/badge/ARIS-DockGlass-blueviolet?style=for-the-badge&logo=windows&logoColor=white" alt="ARIS DockGlass"/>
</p>

<h1 align="center">🪟 ARIS DockGlass</h1>

<p align="center">
  <strong>Transform your Windows taskbar into a stunning, transparent, macOS-style dock experience.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=flat-square&logo=windows" alt="Platform"/>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/UI-PySide6%20(Qt%206)-41CD52?style=flat-square&logo=qt&logoColor=white" alt="PySide6"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/github/stars/Arafat1slam/ARIS-DockGlass?style=flat-square&color=yellow" alt="Stars"/>
  <img src="https://img.shields.io/github/forks/Arafat1slam/ARIS-DockGlass?style=flat-square" alt="Forks"/>
</p>

<p align="center">
  <em>A free, open-source Windows utility that brings macOS-like dock beauty to your desktop — with full taskbar transparency, smooth hover magnification, and customizable labels.</em>
</p>

---

## ✨ Features

### 🪟 Taskbar Transparency Engine
| Mode | Description |
|------|-------------|
| **Clear** | Fully transparent taskbar — see your wallpaper through it |
| **Blur** | Frosted glass blur-behind effect |
| **Acrylic** | Modern acrylic material with tint color |
| **Tint** | Solid color overlay with adjustable opacity |

- 🎨 Custom tint color (any RGB hex)
- 🔆 Adjustable opacity (0–100%)
- 🔄 Auto-recovers after Explorer restarts
- 🖥️ Multi-monitor support (primary + secondary taskbars)

### 🚀 macOS-Style Dock Overlay
- 📌 Pin any `.exe`, `.lnk`, folder, or URL to your dock
- 🔍 **Smooth hover magnification** — icons scale up with a Gaussian falloff, just like macOS
- 💫 **Bounce animation** on app launch
- 🟢 Running indicator dot for active apps
- 🖱️ Drag-and-drop reordering
- 🎯 Click-through — native taskbar remains fully functional underneath

### 🏷️ Custom Label Widgets
- ✏️ Add personalized text labels (name, slogan, status)
- 🎨 Full style control:
  - Font family, size (8–48px), weight, italic
  - Text color, background color, background opacity
  - Corner radius (0–24px), padding, alignment
- 🔍 Optional magnification per label

### ⚙️ Settings & Customization
- 📋 Tabbed settings window (Taskbar, Dock, Labels, General)
- ⚡ **Live preview** — all changes apply instantly, no restart
- 📤 Import/Export settings as JSON
- 🚀 Optional "Start with Windows"
- 🔒 All settings stored locally — no cloud, no telemetry

---

## 🖼️ How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Desktop                              │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│  ░░░░░░ Transparent/Blurred Taskbar ░░░░░░░░░░░░░░░░░░░░░░░░░  │
│       🔵  📁  🌐  🎵  📝  ║ ARIS ║  🎮  💬  📸  🛠️            │
│       ↑              magnified↗       ↑                          │
│     dock icons                     custom label                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Windows 10** (version 1809+) or **Windows 11**
- **Python 3.11** or newer

### Installation

```bash
# Clone the repository
git clone https://github.com/Arafat1slam/ARIS-DockGlass.git
cd ARIS-DockGlass

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

### Build Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build (one-folder mode)
pyinstaller --noconsole --name "ARIS DockGlass" --icon=icon.ico main.py
```

---

## 🏗️ Architecture

ARIS DockGlass follows a clean **layered architecture** with organized packages:

```
ARIS-DockGlass/
│
├── 🚀 main.py                          # Entry point & composition root
│
├── 📂 src/                              # Source packages
│   ├── 📦 infrastructure/              # System-level services
│   │   ├── constants.py                # App constants & defaults
│   │   ├── paths.py                    # %APPDATA% / %LOCALAPPDATA% resolution
│   │   ├── logger.py                   # Rotating log (5MB × 3 files)
│   │   ├── single_instance.py          # Named mutex (one instance only)
│   │   ├── win_interop.py              # All Win32 ctypes declarations
│   │   ├── icon_provider.py            # Icon extraction & two-level cache
│   │   └── startup.py                  # Windows startup registry toggle
│   │
│   ├── 🧮 domain/                      # Pure Python — no Qt, no ctypes
│   │   ├── config_models.py            # Settings dataclasses & validation
│   │   ├── settings_store.py           # Load/save/backup/migrate settings
│   │   ├── magnification.py            # Gaussian scale math & easing
│   │   ├── dock_layout.py              # Item positioning math
│   │   ├── dock_item.py                # Abstract DockItem interface
│   │   ├── app_item.py                 # Launchable app/folder/URL item
│   │   └── label_item.py               # Custom styled text label item
│   │
│   └── 🎨 presentation/               # PySide6 / Qt 6 UI layer
│       ├── dock_window.py              # Frameless transparent overlay
│       ├── dock_controller.py          # Animation & hover management
│       ├── taskbar_theme.py            # Transparency engine & watchdog
│       ├── settings_window.py          # Tabbed settings UI
│       ├── tray.py                     # System tray icon & menu
│       ├── label_service.py            # Label CRUD operations
│       ├── pinned_apps.py              # Pinned app management
│       └── app_state.py                # Runtime state & signal hub
│
├── 🧪 tests/                           # Unit & integration tests
│   ├── test_magnification.py
│   ├── test_dock_layout.py
│   ├── test_settings_store.py
│   └── test_path_validation.py
│
├── 📚 docs/                             # Documentation & specs
│   └── ARIS_TaskbarDock_PLAN.md         # Engineering plan
│
├── 🎨 assets/                           # Icons, images & resources
│
├── requirements.txt
├── LICENSE                              # MIT License
└── README.md
```

---

## 🔒 Security

ARIS DockGlass is built with security as a priority:

| # | Control |
|---|---------|
| 🛡️ | No `shell=True` — all processes launched with argument lists |
| 🚫 | No `eval()`, `exec()`, `pickle`, or dynamic imports |
| 🔐 | Registry writes limited to `HKEY_CURRENT_USER` only |
| 🌐 | URL launch restricted to `https://` and `http://` only |
| 📁 | All file paths normalized and validated against traversal |
| 🔇 | **Zero network calls** — no telemetry, no analytics, no phoning home |
| 🪪 | Standard user only — no admin rights required |

---

## ⚡ Performance

| Metric | Target |
|--------|--------|
| 🎯 Dock animation | **60 FPS** with 15 items |
| 💤 Idle CPU usage | **< 1%** |
| ⚡ Cold start | **< 2 seconds** |
| 💾 Memory | **< 150 MB** with 20 items + 5 labels |

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 **Fork** the repository
2. 🌿 **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. 📤 **Push** to the branch (`git push origin feature/amazing-feature`)
5. 🔃 **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ARIS-DockGlass.git
cd ARIS-DockGlass

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run linter
pip install ruff
ruff check .
```

---

## 📋 Roadmap

- [x] Taskbar transparency (Clear, Blur, Acrylic, Tint)
- [x] macOS-style dock with hover magnification
- [x] Custom label widgets
- [x] System tray integration
- [x] Live settings with import/export
- [ ] Top/Left/Right taskbar positions
- [ ] Plugin system (clock, weather, media controls)
- [ ] Theme presets
- [ ] Hide native taskbar icons (experimental)
- [ ] Animated wallpaper integration

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Free to use, modify, and distribute. ❤️

---

## 👤 Author

**Arafat Islam (ARIS)**

- GitHub: [@Arafat1slam](https://github.com/Arafat1slam)

---

<p align="center">
  <strong>⭐ If you like ARIS DockGlass, give it a star! ⭐</strong>
</p>

<p align="center">
  <sub>Made with ❤️ by ARIS • Free & Open Source Forever</sub>
</p>
