"""Desktop capability detection for transparent cross-platform behavior."""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class AutomationSupport(str, Enum):
    SUPPORTED = "supported"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED_WAYLAND = "unsupported_wayland"


@dataclass(frozen=True)
class DesktopCapabilities:
    system: str
    session_type: str
    automation: AutomationSupport
    global_hotkeys: bool
    overlay: bool
    reason: str = ""

    @property
    def automation_available(self) -> bool:
        return self.automation is AutomationSupport.SUPPORTED


def detect_desktop_capabilities(
    environ: Mapping[str, str] | None = None,
    system: str | None = None,
) -> DesktopCapabilities:
    """Describe supported desktop integrations without probing user input devices."""
    env = os.environ if environ is None else environ
    current_system = (system or platform.system()).lower()
    session = env.get("XDG_SESSION_TYPE", "").lower()

    if current_system == "linux" and (
        session == "wayland" or (env.get("WAYLAND_DISPLAY") and not env.get("DISPLAY"))
    ):
        reason = "Desktop automation is disabled on Wayland; use an X11 session for macros."
        return DesktopCapabilities(
            system="Linux",
            session_type="wayland",
            automation=AutomationSupport.UNSUPPORTED_WAYLAND,
            global_hotkeys=False,
            overlay=True,
            reason=reason,
        )

    if current_system in {"windows", "darwin"}:
        display = "native"
    elif current_system == "linux":
        display = session or "x11"
    else:
        return DesktopCapabilities(
            system=platform.system() or "Unknown",
            session_type=session or "unknown",
            automation=AutomationSupport.UNAVAILABLE,
            global_hotkeys=False,
            overlay=True,
            reason="Desktop automation is not certified on this operating system.",
        )

    return DesktopCapabilities(
        system=platform.system() if system is None else system,
        session_type=display,
        automation=AutomationSupport.SUPPORTED,
        global_hotkeys=True,
        overlay=True,
    )
