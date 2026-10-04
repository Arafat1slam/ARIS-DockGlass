# ARIS Taskbar & Dock — Engineering Plan

**Document type:** Implementation Plan / Handoff Specification
**Target agent:** AntiGravity
**Owner:** Aris
**Status:** Draft v1.0

---

## 1. Overview

A Windows desktop utility with three coordinated capabilities:

1. **Taskbar Transparency Engine:** Makes the Windows taskbar transparent, blurred (acrylic), or tinted, with user-controlled opacity and color.
2. **macOS-style Dock Overlay:** A floating, pinned-app dock with smooth hover magnification and launch animations, rendered on top of the taskbar region.
3. **Customizable Label Widget:** A user-defined text block (name, slogan, or any text) placed inside the dock's free space, with full control over font, size, weight, text color, background color, opacity, corner radius, and alignment.

The app runs in the system tray, starts with Windows (optional), and stores all configuration locally.

---

## 2. Assumptions and Scope

| Item | Decision |
|---|---|
| OS | Windows 10 (1809+) and Windows 11 (22H2, 23H2, 24H2) |
| Language | Python 3.11+ |
| UI framework | PySide6 (Qt 6) |
| Native access | `ctypes` against `user32`, `shell32`, `dwmapi`, `advapi32` (no compiled extensions) |
| Architecture style | Flat module files beside `main.py` (no nested packages), layered services, dependency injection by constructor |
| Packaging | PyInstaller (one-folder build first; one-file optional later) |
| Config storage | `%APPDATA%\ARIS\TaskbarDock\settings.json` |
| Cache storage | `%LOCALAPPDATA%\ARIS\TaskbarDock\cache\` |
| Privileges | Standard user only. No admin rights, no service, no driver. |
| Network | None. The app makes no outbound network calls. |
| Primary taskbar position | Bottom (v1). Left, right, and top are v2. |

**Why Python + PySide6:** It fits the existing ARIS ecosystem (Python desktop assistant with `main.py` and flat modules), Qt provides hardware-accelerated transparent frameless windows, and `ctypes` covers every required Win32 call without extra dependencies.

**Non-goals (v1):**
- Replacing or re-implementing the Windows Start menu or system tray.
- Hiding native taskbar icons (officially unsupported; tracked as experimental task T-EXP-01).
- Linux or macOS support.
- Cloud sync of settings.

---

## 3. Functional Requirements

### FR-1: Taskbar Transparency

| ID | Requirement |
|---|---|
| FR-1.1 | Apply transparency to the primary taskbar (`Shell_TrayWnd`) and all secondary taskbars (`Shell_SecondaryTrayWnd`). |
| FR-1.2 | Modes: `CLEAR` (fully transparent), `BLUR` (blur behind), `ACRYLIC` (acrylic with tint), `TINT` (solid color with opacity). |
| FR-1.3 | User can set tint color (RGB hex) and opacity (0–100%). |
| FR-1.4 | Re-apply automatically when Explorer restarts (listen for the registered `TaskbarCreated` message). |
| FR-1.5 | Re-apply automatically after display resolution, DPI, or monitor changes (`WM_DISPLAYCHANGE`, `WM_SETTINGCHANGE`). |
| FR-1.6 | Restore the original taskbar appearance on app exit, crash handler, and user "Disable" action. |
| FR-1.7 | If the OS build does not support a mode, fall back to the nearest supported mode and show a notice in the settings window. |

### FR-2: Dock Overlay

| ID | Requirement |
|---|---|
| FR-2.1 | Display a frameless, always-on-top, translucent dock centered horizontally over the taskbar area. |
| FR-2.2 | The dock must not appear in Alt+Tab or the taskbar button list (`WS_EX_TOOLWINDOW`). |
| FR-2.3 | Pinned items: user can add any `.exe`, `.lnk`, folder, or URL. Items can be reordered by drag and removed via context menu. |
| FR-2.4 | Icons are extracted from the target file and cached. Missing icons use a default placeholder. |
| FR-2.5 | Hover magnification: the icon under the cursor and its neighbors scale smoothly (macOS-like falloff). Scale range is configurable (1.0x to 2.0x). |
| FR-2.6 | Launch animation: a bounce on click, and a running-indicator dot when the app process is alive. |
| FR-2.7 | Dock layout is recalculated on every animation frame and never blocks the UI thread. |
| FR-2.8 | Dock position: bottom-center (default), bottom-left, bottom-right. Vertical offset is configurable. |
| FR-2.9 | The dock must never intercept clicks outside its own bounding region, so native taskbar icons remain clickable. |

### FR-3: Custom Label Widget

| ID | Requirement |
|---|---|
| FR-3.1 | The user can add one or more label items to the dock. Each label is a separate dock item. |
| FR-3.2 | Text content: free text, up to 60 characters per label (validated). |
| FR-3.3 | Style controls: font family, font size (8–48 px), weight (Normal, Bold), italic, text color, background color, background opacity, corner radius (0–24 px), padding, horizontal alignment. |
| FR-3.4 | Labels can be edited by double-click or from the settings window. |
| FR-3.5 | Labels support magnification the same way as app icons, optionally (per-label toggle). |
| FR-3.6 | Labels can be removed or duplicated. |

### FR-4: Settings and Persistence

| ID | Requirement |
|---|---|
| FR-4.1 | Settings are stored as versioned JSON (`schema_version` field). |
| FR-4.2 | Corrupt or invalid settings must fall back to defaults and back up the bad file as `settings.corrupt-<timestamp>.json`. |
| FR-4.3 | Settings changes apply live (no restart required). |
| FR-4.4 | Import/export settings as a single JSON file. |
| FR-4.5 | Settings window has tabs: Taskbar, Dock, Labels, General. |

### FR-5: App Shell

| ID | Requirement |
|---|---|
| FR-5.1 | System tray icon with menu: Settings, Enable/Disable, Reset Taskbar, Quit. |
| FR-5.2 | Single-instance enforcement via a named mutex. A second launch brings the existing settings window forward and exits. |
| FR-5.3 | Optional "Start with Windows" using `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` only. |
| FR-5.4 | Graceful shutdown: restore taskbar, remove tray icon, release handles. |

---

## 4. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Security** | No shell execution (`subprocess` with argument lists only, `shell=False`). Launch targets are limited to user-selected paths. No admin elevation. Registry writes limited to `HKCU`. Settings and cache paths are validated against path traversal. Logs never contain full user paths beyond the filename. |
| **Performance** | Idle CPU under 1% on the reference machine. Dock animation holds 60 FPS with 15 items. Cold start under 2 seconds. Icons are pre-rendered at max scale and cached in memory as `QPixmap`. No per-frame disk or registry access. |
| **Memory** | Under 150 MB resident with 20 items and 5 labels. |
| **Scalability** | Dock items are plugins implementing one interface (`DockItem`). New item types (clock, weather, media) can be added without changing the dock layout engine. |
| **Maintainability** | Type hints on all public functions. `ruff` and `mypy --strict` must pass. Pure logic (magnification math, settings migration, path validation) has unit tests. |
| **Reliability** | Taskbar state is always restored on exit, crash (`sys.excepthook`), and termination signal. A watchdog timer re-applies transparency if Explorer resets it. |
| **Compatibility** | Works at DPI scales 100%, 125%, 150%, 175%, 200%. Works with 1 to 3 monitors. |
| **Observability** | Rotating log file at `%LOCALAPPDATA%\ARIS\TaskbarDock\logs\app.log` (5 MB x 3 files). Log levels configurable. |

---

## 5. Architecture

### 5.1 Layered Design

```
┌───────────────────────────────────────────────────────────┐
│ Presentation (Qt Widgets)                                 │
│  dock_window.py   settings_window.py   tray.py            │
│  dock_item_views.py                                       │
├───────────────────────────────────────────────────────────┤
│ Application Services                                      │
│  taskbar_theme.py   dock_controller.py   pinned_apps.py   │
│  label_service.py   startup.py          app_state.py      │
├───────────────────────────────────────────────────────────┤
│ Domain / Models (pure Python, no Qt, no ctypes)           │
│  config_models.py   magnification.py   dock_layout.py     │
├───────────────────────────────────────────────────────────┤
│ Infrastructure                                            │
│  win_interop.py (ctypes)   icon_provider.py               │
│  settings_store.py   logger.py   paths.py   single_instance.py │
└───────────────────────────────────────────────────────────┘
```

**Rule:** Domain layer must not import Qt or ctypes. This keeps the math and validation testable on any machine.

### 5.2 Flat Module Layout (beside `main.py`)

```
TaskbarDock/
├── main.py                 # Entry point, composition root (DI wiring)
├── constants.py            # Versions, app name, default values
├── paths.py                # %APPDATA% / %LOCALAPPDATA% resolution
├── logger.py               # Rotating logger setup
├── single_instance.py      # Named mutex guard
├── win_interop.py          # All ctypes Win32 declarations (single source)
├── config_models.py        # Dataclasses for settings schema + migrations
├── settings_store.py       # Load, validate, save, backup corrupt files
├── taskbar_theme.py        # Accent state logic + apply/restore/watchdog
├── magnification.py        # Pure math: falloff, scale, easing (no Qt)
├── dock_layout.py          # Pure math: item positions and widths
├── dock_item.py            # Abstract DockItem interface
├── app_item.py             # DockItem for launchable apps/files/URLs
├── label_item.py           # DockItem for custom text labels
├── dock_window.py          # Frameless transparent overlay window
├── dock_controller.py      # Owns items, handles hover/animation timers
├── icon_provider.py        # Icon extraction + disk cache + memory cache
├── pinned_apps.py          # Add/remove/reorder pinned targets
├── label_service.py        # CRUD for label items
├── settings_window.py      # Tabbed settings UI
├── tray.py                 # System tray icon and menu
├── startup.py              # HKCU Run key toggle
├── app_state.py            # Enabled/disabled state, signals hub
└── tests/
    ├── test_magnification.py
    ├── test_dock_layout.py
    ├── test_settings_store.py
    └── test_path_validation.py
```

### 5.3 Key Data Model (summary)

```text
Settings
 ├─ schema_version: int
 ├─ taskbar: TaskbarSettings
 │    ├─ enabled: bool
 │    ├─ mode: CLEAR | BLUR | ACRYLIC | TINT
 │    ├─ tint_hex: str            (e.g. "#101820")
 │    └─ opacity_percent: int     (0..100)
 ├─ dock: DockSettings
 │    ├─ enabled: bool
 │    ├─ position: BOTTOM_CENTER | BOTTOM_LEFT | BOTTOM_RIGHT
 │    ├─ vertical_offset_px: int
 │    ├─ base_icon_px: int        (32..96)
 │    ├─ max_scale: float         (1.0..2.0)
 │    └─ falloff_sigma: float     (0.5..3.0 in item-widths)
 ├─ items: list[DockItemConfig]   (ordered)
 │    ├─ id: str (UUID)
 │    ├─ kind: APP | LABEL
 │    ├─ app: { target_path, args, display_name }        (kind=APP)
 │    └─ label: { text, font, size, weight, italic,
 │               text_hex, bg_hex, bg_opacity, radius,
 │               padding, align, magnify: bool }          (kind=LABEL)
 └─ general: GeneralSettings
      ├─ start_with_windows: bool
      ├─ log_level: str
      └─ language_ui: "en"
```

---

## 6. Technical Design

### 6.1 Taskbar Transparency (`taskbar_theme.py` + `win_interop.py`)

- Use the undocumented `SetWindowCompositionAttribute` from `user32.dll`, loaded via `ctypes.WinDLL`. Resolve the function once at startup and fail gracefully if it is missing.
- Define `WINDOWCOMPOSITIONATTRIBDATA` and `ACCENTPOLICY` structures in `win_interop.py` only.
- Accent states:

| Mode | Accent state | Notes |
|---|---|---|
| CLEAR | `ACCENT_ENABLE_TRANSPARENTGRADIENT` (3) | Fully transparent, uses `GradientColor` alpha |
| BLUR | `ACCENT_ENABLE_BLURBEHIND` (3 variant, see implementation notes) | Blur without tint |
| ACRYLIC | `ACCENT_ENABLE_ACRYLICBLURBEHIND` (4) | Requires Windows 10 1803+ |
| TINT | `ACCENT_ENABLE_GRADIENT` (2) | Solid color with alpha |

- **Target windows:** `FindWindowW("Shell_TrayWnd", None)` and each `Shell_SecondaryTrayWnd` discovered by enumerating top-level windows.
- **Original state capture:** Read and store the current accent policy before the first change, so restore is exact.
- **Watchdog:** A `QTimer` every 2 seconds verifies the taskbar is still in the expected state. Re-apply only if changed (avoid flicker).
- **Explorer restart:** Register `TaskbarCreated` via `RegisterWindowMessageW` in a hidden message-only window and re-apply on receipt.
- **Implementation note for AntiGravity:** Windows 11 24H2 changed some taskbar behavior. Verify each mode on 22H2, 23H2, and 24H2 before marking FR-1 complete. Document any mode that does not render as expected and fall back per FR-1.7.

### 6.2 Dock Window (`dock_window.py`)

- Qt window flags: `FramelessWindowHint | WindowStaysOnTopHint | Tool`.
- Attributes: `WA_TranslucentBackground = True`, `WA_ShowWithoutActivating = True`.
- Add `WS_EX_NOACTIVATE` via `SetWindowLongPtrW` so clicking the dock does not steal focus from the active app.
- **Position:** Query `Shell_TrayWnd` rect via `GetWindowRect`. Place the dock inside the taskbar band, not over the Start button or the system tray area (computed from `Shell_TrayWnd` child windows `Start`, `TrayNotifyWnd`). This keeps those controls clickable.
- **Click-through outside bounds:** Use `WS_EX_TRANSPARENT` on the transparent margin, or use `setMask()` with a `QRegion` that matches the dock's visible silhouette.
- **Animation:** `QTimer` at 16 ms (60 FPS) only while the cursor is inside the dock or an animation is in progress. Stop the timer when idle.

### 6.3 Magnification (`magnification.py`, pure math)

Scale for an item at horizontal distance `d` (in item widths) from the cursor:

```text
scale(d) = 1 + (max_scale - 1) * exp( -(d^2) / (2 * sigma^2) )
```

- `sigma` comes from `falloff_sigma` in settings.
- Smooth the target scale per item with exponential easing: `current += (target - current) * 0.25` each frame.
- Layout: items keep their base slot width, and the dock width grows symmetrically around the cursor. `dock_layout.py` computes the final x-positions from the scaled widths.
- All functions here must be deterministic and unit-tested.

### 6.4 Dock Items (`dock_item.py`, `app_item.py`, `label_item.py`)

```text
DockItem (abstract)
 ├─ id: str
 ├─ base_width() -> int
 ├─ paint(painter, rect, scale, state) -> None
 ├─ on_click() -> None
 ├─ on_double_click() -> None
 ├─ context_actions() -> list[Action]
 └─ tick(dt) -> None           # for bounce or indicator animations
```

- **AppItem:** Launch with `subprocess.Popen([target, *args], shell=False, close_fds=True)`. For folders, use `os.startfile` only after path validation. For URLs, allow only `https://` and `http://`.
- **LabelItem:** Renders text with `QPainterPath` and rounded `QRect`. Pre-renders a pixmap at max scale and scales down for smaller sizes to avoid repaint cost.

### 6.5 Icon Provider (`icon_provider.py`)

- Extract with `SHGetFileInfoW` (`SHGFI_ICON | SHGFI_LARGEICON`) through `win_interop.py`, then convert `HICON` to `QPixmap` via `QImage`. Free handles with `DestroyIcon`.
- Two-level cache: in-memory `dict[str, QPixmap]` keyed by `(path, mtime, size)`, plus disk PNG cache in the cache folder keyed by SHA-256 of the normalized path.
- Missing or unreadable target returns a built-in placeholder pixmap. Never raise to the UI layer.

### 6.6 Settings Store (`settings_store.py`)

- Load: read, parse, validate with dataclass validators, then migrate if `schema_version` is older.
- Save: write to `settings.json.tmp`, flush, `os.replace` to the final name (atomic write).
- Corrupt file: rename to `settings.corrupt-<timestamp>.json`, load defaults, log a warning.
- Validation rules:
  - `tint_hex` matches `^#[0-9A-Fa-f]{6}$`
  - `opacity_percent` in 0..100
  - `max_scale` in 1.0..2.0
  - `label.text` length 1..60, control characters stripped
  - `target_path` must exist at save time and be a regular file, folder, or allowed URL

---

## 7. Security Requirements (Detailed)

| ID | Control |
|---|---|
| SEC-1 | `subprocess` is always called with a list and `shell=False`. No string concatenation into commands. |
| SEC-2 | No `eval`, `exec`, `pickle`, or dynamic imports from user input. |
| SEC-3 | Settings JSON is parsed with `json.loads` only. Unknown keys are ignored, not executed. |
| SEC-4 | URL launch allowed schemes: `https`, `http`. All others are rejected. |
| SEC-5 | Registry access limited to `HKEY_CURRENT_USER`. Never write to `HKLM`. |
| SEC-6 | File paths normalized with `os.path.realpath` and checked against the user's chosen item list. No recursive directory scanning. |
| SEC-7 | Icon cache filenames use SHA-256 of the path, never raw user input. |
| SEC-8 | Logs redact full paths (keep filename only) and never log settings contents. |
| SEC-9 | Single-instance mutex name is fixed: `Global\ARIS_TaskbarDock_Mutex`. |
| SEC-10 | Clean up all `HICON`, `HWND`, and registry handles in `finally` blocks. |
| SEC-11 | Dependencies pinned in `requirements.txt` with hashes. Run `pip-audit` before each release. |

---

## 8. Performance Requirements (Detailed)

| ID | Target | Method |
|---|---|---|
| PERF-1 | 60 FPS dock animation with 15 items | Pre-rendered pixmaps, transform-based scaling, no allocations in paint loop |
| PERF-2 | Idle CPU < 1% | Timers stop when idle, watchdog interval at 2 s |
| PERF-3 | Cold start < 2 s | Lazy icon loading, deferred settings window construction |
| PERF-4 | No UI thread blocking on I/O | Icon extraction on a `QThreadPool` worker, results signaled back |
| PERF-5 | Taskbar re-apply < 50 ms | Single `SetWindowCompositionAttribute` call per window |

---

## 9. Testing Strategy

### 9.1 Unit Tests (pure Python, run in CI)
- `magnification`: scale at distance 0 equals `max_scale`, at large distance tends to 1.0, monotonic decrease.
- `dock_layout`: total width equals sum of scaled widths, no overlap, symmetric around cursor.
- `settings_store`: invalid values rejected, corrupt file backed up, migration from v1 to v2 preserves data.
- `path validation`: rejects `..` traversal, rejects `javascript:` and `file:` URLs, accepts `https://`.

### 9.2 Integration Tests (Windows VM or real machine)
- Apply each taskbar mode on Win10 22H2, Win11 23H2, Win11 24H2.
- Kill `explorer.exe` and confirm taskbar is re-themed within 3 seconds.
- Change DPI from 100% to 150% and confirm dock re-anchors.
- Attach a second monitor and confirm the secondary taskbar is themed.
- Quit app and confirm taskbar returns to original appearance.
- Click native taskbar icons that sit under the dock region and confirm they still respond.

### 9.3 Manual UX Checklist
- Hover magnification feels smooth at 60 FPS.
- Label text stays crisp at 125% and 150% DPI.
- Drag-reorder works with 1 and 15 items.
- Settings changes apply live without restart.

### 9.4 Quality Gates
- `ruff check` and `ruff format --check` clean.
- `mypy --strict` clean on all non-UI modules.
- Unit test coverage at least 80% on `magnification.py`, `dock_layout.py`, `settings_store.py`.

---

## 10. Delivery Phases and Task Breakdown

Each task is a single AntiGravity prompt. Complete and verify one task before starting the next. Fixing one module in a live project can break others, so do not batch unrelated tasks.

| Phase | Task ID | Task | Done when |
|---|---|---|---|
| **P0 Spike** | T-00 | Create project skeleton, `requirements.txt`, `main.py` that opens and closes cleanly | App starts and exits with exit code 0 |
| P0 | T-01 | Implement `win_interop.py` with accent policy structures and `SetWindowCompositionAttribute` wrapper | Function resolves and returns without error on Win11 |
| P0 | T-02 | Implement `taskbar_theme.py` with CLEAR mode only, capture and restore original state | Taskbar goes transparent and returns to original on exit |
| **P1 Taskbar** | T-03 | Add BLUR, ACRYLIC, TINT modes with fallback logic (FR-1.7) | All four modes render or fall back correctly on target OS builds |
| P1 | T-04 | Add `TaskbarCreated` listener and watchdog timer (FR-1.4, FR-1.5) | Re-theme after `explorer.exe` restart |
| **P2 Dock** | T-05 | Implement `dock_window.py` as frameless, always-on-top, non-activating overlay (FR-2.1, FR-2.2) | Dock visible over taskbar, not in Alt+Tab, does not steal focus |
| P2 | T-06 | Implement `icon_provider.py` with extraction, memory cache, disk cache (FR-2.4) | Icons appear for `.exe`, `.lnk`, and folders |
| P2 | T-07 | Implement `app_item.py` with safe launch (SEC-1, SEC-4) | Click launches target with no shell involvement |
| P2 | T-08 | Implement `magnification.py` and `dock_layout.py` with unit tests (FR-2.5) | Tests pass, math verified |
| P2 | T-09 | Wire magnification into `dock_controller.py` with 60 FPS animation (FR-2.5, FR-2.7) | Smooth hover scaling with 15 items |
| P2 | T-10 | Click-through and clickable-region masking (FR-2.9) | Native taskbar icons under transparent areas remain clickable |
| **P3 Labels** | T-11 | Implement `label_item.py` with text and style rendering (FR-3.2, FR-3.3) | Label renders with configured font and colors |
| P3 | T-12 | Implement `label_service.py` add, edit, remove, duplicate (FR-3.1, FR-3.4, FR-3.6) | CRUD works from settings, changes reflected live |
| P3 | T-13 | Optional magnification for labels (FR-3.5) | Per-label toggle works |
| **P4 Settings** | T-14 | Implement `config_models.py` and `settings_store.py` with validation and atomic save (FR-4.1 to FR-4.3) | Corrupt file test passes, atomic write verified |
| P4 | T-15 | Build `settings_window.py` with Taskbar, Dock, Labels, General tabs (FR-4.5) | All controls bound to settings |
| P4 | T-16 | Import and export settings (FR-4.4) | Round-trip export then import yields identical settings |
| **P5 Shell** | T-17 | Implement `tray.py` menu (FR-5.1) | Tray actions work |
| P5 | T-18 | Implement `single_instance.py` (FR-5.2) | Second launch focuses existing instance |
| P5 | T-19 | Implement `startup.py` HKCU Run toggle (FR-5.3, SEC-5) | Toggle adds and removes Run key |
| P5 | T-20 | Implement crash-safe restore: `atexit`, `sys.excepthook`, signal handlers (FR-1.6, FR-5.4) | Forced crash still restores taskbar |
| **P6 Hardening** | T-21 | Logging, rotation, log-level config (Observability) | Logs rotate at 5 MB |
| P6 | T-22 | PyInstaller build, folder output, smoke test on clean VM | Runs without Python installed |
| P6 | T-23 | Security pass: `pip-audit`, SEC-1 to SEC-11 checklist | All controls verified and documented |
| **Experimental** | T-EXP-01 | Investigate hiding native taskbar icons (not in v1 scope) | Feasibility note written, go or no-go decision |

---

## 11. Acceptance Criteria (Definition of Done for v1)

1. Taskbar can be set to CLEAR, BLUR, ACRYLIC, or TINT, with opacity and color controls, on Windows 10 and 11.
2. Taskbar returns to its original appearance on quit, crash, and Explorer restart recovery.
3. Dock shows pinned apps, folders, and URLs with extracted icons.
4. Hover magnification and click bounce run at 60 FPS with 15 items.
5. Native taskbar icons remain clickable where the dock does not cover them.
6. At least one custom label can be added, styled (font, size, text color, background color, opacity, corner radius), edited, and removed.
7. All settings persist across restarts and apply live.
8. App runs from tray, supports single-instance, and optionally starts with Windows.
9. All SEC and PERF requirements in sections 7 and 8 are verified.
10. Packaged build runs on a clean Windows VM without Python installed.

---

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `SetWindowCompositionAttribute` behavior changes in future Windows builds | Taskbar effects stop working | Feature-detect at startup, fall back per FR-1.7, log the Windows build number |
| Dock overlay blocks native taskbar clicks | Users cannot open Start or tray apps | Position dock within safe region (T-05), mask clicks (T-10), test against Start and tray hit areas |
| Explorer resets taskbar appearance | Visual inconsistency | Watchdog timer and `TaskbarCreated` listener (T-04) |
| High DPI causes blurry icons | Poor visual quality | Extract at 256 px where available, scale with smooth transform |
| Icon extraction slow for network drives | UI freezes | Worker thread (PERF-4), placeholder until ready |
| Antivirus flags a taskbar-modifying app | Installation friction | Code-sign the build (recommended before public release), document behavior in README |

---

## 13. Open Questions (to confirm with Aris before T-05)

1. Target OS: Is Windows 11 the primary target, with Windows 10 as secondary?
2. Does the dock replace the visual taskbar (Windows taskbar auto-hidden), or sit on top of it?
3. Should the label widget support multiple lines in v1, or single line only?
4. Is a bundled default icon set needed for labels and folders?

---

## 14. Handoff Instructions for AntiGravity

1. Read this entire document before writing any code.
2. Implement tasks in the order listed in section 10. Do not skip phases.
3. For each task, produce changes in the OLD CODE / NEW CODE format when modifying existing files. Full files only when explicitly requested.
4. Keep all modules flat beside `main.py`. Do not create nested packages except for `tests/`.
5. Run `ruff`, `mypy`, and the relevant unit tests after each task and report results before moving on.
6. If a Windows API behaves differently from this spec, stop, document the observed behavior, and ask for a decision. Do not silently change the design.
7. Do not add network calls, telemetry, or elevated privileges.
