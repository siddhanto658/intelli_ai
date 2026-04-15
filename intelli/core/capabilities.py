import shutil
from dataclasses import dataclass

from intelli.core.platform import PlatformAdapter


@dataclass
class PlatformCapabilities:
    os_name: str
    can_hotword: bool
    can_screenshot: bool
    can_shutdown: bool
    has_camera_launcher: bool
    has_whatsapp_web: bool


def detect_capabilities(adapter: PlatformAdapter) -> PlatformCapabilities:
    os_name = adapter.system
    has_camera_launcher = os_name in {"windows", "darwin"} or bool(shutil.which("camera")) or bool(shutil.which("cheese"))
    return PlatformCapabilities(
        os_name=os_name,
        can_hotword=True,
        can_screenshot=True,
        can_shutdown=True,
        has_camera_launcher=has_camera_launcher,
        has_whatsapp_web=True,
    )

