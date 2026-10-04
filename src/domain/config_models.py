import uuid
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class TaskbarSettings:
    enabled: bool = True
    mode: str = 'ACRYLIC'
    tint_hex: str = '#101820'
    opacity_percent: int = 80
    hide_windows_taskbar: bool = True

    def validate(self):
        if self.mode not in ('CLEAR', 'BLUR', 'ACRYLIC', 'TINT'):
            self.mode = 'ACRYLIC'
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.tint_hex):
            self.tint_hex = '#101820'
        if not (0 <= self.opacity_percent <= 100):
            self.opacity_percent = 80


@dataclass
class DockSettings:
    enabled: bool = True
    position: str = 'BOTTOM_CENTER'
    vertical_offset_px: int = 0
    base_icon_px: int = 38
    max_scale: float = 1.55
    falloff_sigma: float = 1.4

    def validate(self):
        if self.position not in ('BOTTOM_CENTER', 'BOTTOM_LEFT', 'BOTTOM_RIGHT'):
            self.position = 'BOTTOM_CENTER'
        if not (24 <= self.base_icon_px <= 96):
            self.base_icon_px = 38
        if not (1.0 <= self.max_scale <= 2.0):
            self.max_scale = 1.55
        if not (0.5 <= self.falloff_sigma <= 3.0):
            self.falloff_sigma = 1.4


@dataclass
class AppConfig:
    target: str = ''
    args: str = ''
    icon_path: str = ''
    display_name: str = ''

@dataclass

class LabelConfig:
    text: str = ''
    font_family: str = 'Segoe UI'
    font_size: int = 14
    is_bold: bool = False
    is_italic: bool = False
    text_color: str = '#FFFFFF'
    bg_color: str = '#000000'
    bg_opacity: int = 50
    corner_radius: int = 4
    padding: int = 4
    magnify: bool = True

    def validate(self):
        if not (8 <= self.font_size <= 48):
            self.font_size = 14
        if not (0 <= self.bg_opacity <= 100):
            self.bg_opacity = 50
        if not (0 <= self.corner_radius <= 24):
            self.corner_radius = 4

@dataclass
class DockItemConfig:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    kind: str = 'APP'
    app: Optional[AppConfig] = None
    label: Optional[LabelConfig] = None

    def validate(self):
        if self.kind not in ('APP', 'LABEL'):
            self.kind = 'APP'
        if self.kind == 'APP' and self.app is None:
            self.app = AppConfig()
        if self.kind == 'LABEL' and self.label is None:
            self.label = LabelConfig()
        if self.label:
            self.label.validate()

@dataclass
class GeneralSettings:
    start_with_windows: bool = False
    log_level: str = 'INFO'
    language_ui: str = 'en'

    def validate(self):
        if self.log_level not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            self.log_level = 'INFO'

def get_default_dock_items() -> List[DockItemConfig]:
    import os
    defaults = []
    
    # 0. Windows Start Menu
    defaults.append(DockItemConfig(
        id="default-start",
        kind="APP",
        app=AppConfig(target="start-menu", display_name="Start Menu")
    ))

    # 1. File Explorer
    explorer_path = r"C:\Windows\explorer.exe"
    if os.path.exists(explorer_path):
        defaults.append(DockItemConfig(
            id="default-explorer",
            kind="APP",
            app=AppConfig(target=explorer_path, display_name="File Explorer")
        ))

        
    # 2. Web Browser (Brave or Edge)
    brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(brave_path):
        defaults.append(DockItemConfig(
            id="default-brave",
            kind="APP",
            app=AppConfig(target=brave_path, display_name="Brave Browser")
        ))
    elif os.path.exists(edge_path):
        defaults.append(DockItemConfig(
            id="default-edge",
            kind="APP",
            app=AppConfig(target=edge_path, display_name="Microsoft Edge")
        ))
        
    # 3. Discord
    discord_lnk = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk")
    if os.path.exists(discord_lnk):
        defaults.append(DockItemConfig(
            id="default-discord",
            kind="APP",
            app=AppConfig(target=discord_lnk, display_name="Discord")
        ))
        
    # 4. Notepad
    notepad_path = r"C:\Windows\System32\notepad.exe"
    if os.path.exists(notepad_path):
        defaults.append(DockItemConfig(
            id="default-notepad",
            kind="APP",
            app=AppConfig(target=notepad_path, display_name="Notepad")
        ))
        
    # 5. Terminal / CMD
    cmd_path = r"C:\Windows\System32\cmd.exe"
    if os.path.exists(cmd_path):
        defaults.append(DockItemConfig(
            id="default-cmd",
            kind="APP",
            app=AppConfig(target=cmd_path, display_name="Command Prompt")
        ))
        
    # 6. ARIS Brand Label
    defaults.append(DockItemConfig(
        id="default-label",
        kind="LABEL",
        label=LabelConfig(text="ARIS", is_bold=True, text_color="#00E5FF", bg_color="#1E293B", bg_opacity=80, corner_radius=8)
    ))
    
    return defaults

@dataclass
class Settings:
    schema_version: int = 1
    taskbar: TaskbarSettings = field(default_factory=TaskbarSettings)
    dock: DockSettings = field(default_factory=DockSettings)
    items: List[DockItemConfig] = field(default_factory=get_default_dock_items)
    general: GeneralSettings = field(default_factory=GeneralSettings)


    def validate(self):
        self.taskbar.validate()
        self.dock.validate()
        for item in self.items:
            item.validate()
        self.general.validate()

    @classmethod
    def migrate(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        schema_version = data.get('schema_version', 1)
        if schema_version < 1:
            pass # Apply structural migrations here if any
        data['schema_version'] = 1
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        data = cls.migrate(data)
        
        taskbar_data = data.get('taskbar', {})
        taskbar = TaskbarSettings(**{k: v for k, v in taskbar_data.items() if hasattr(TaskbarSettings, k)})
        
        dock_data = data.get('dock', {})
        dock = DockSettings(**{k: v for k, v in dock_data.items() if hasattr(DockSettings, k)})
        
        general_data = data.get('general', {})
        general = GeneralSettings(**{k: v for k, v in general_data.items() if hasattr(GeneralSettings, k)})
        
        items_data = data.get('items', [])
        items = []
        for item_data in items_data:
            app_data = item_data.get('app')
            app_config = AppConfig(**{k: v for k, v in app_data.items() if hasattr(AppConfig, k)}) if app_data else None
            
            label_data = item_data.get('label')
            label_config = LabelConfig(**{k: v for k, v in label_data.items() if hasattr(LabelConfig, k)}) if label_data else None
            
            item = DockItemConfig(
                id=item_data.get('id', str(uuid.uuid4())),
                kind=item_data.get('kind', 'APP'),
                app=app_config,
                label=label_config
            )
            items.append(item)
            
        settings = cls(
            schema_version=data.get('schema_version', 1),
            taskbar=taskbar,
            dock=dock,
            items=items,
            general=general
        )
        settings.validate()
        return settings

    def to_dict(self) -> Dict[str, Any]:
        return {
            'schema_version': self.schema_version,
            'taskbar': self.taskbar.__dict__,
            'dock': self.dock.__dict__,
            'items': [
                {
                    'id': i.id,
                    'kind': i.kind,
                    'app': i.app.__dict__ if i.app else None,
                    'label': i.label.__dict__ if i.label else None,
                }
                for i in self.items
            ],
            'general': self.general.__dict__
        }
