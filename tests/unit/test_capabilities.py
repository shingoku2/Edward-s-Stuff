import pytest

from omnix.capabilities import AutomationSupport, detect_desktop_capabilities


@pytest.mark.unit
def test_wayland_disables_automation_with_explanation():
    capabilities = detect_desktop_capabilities(
        {"XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0"},
        system="Linux",
    )

    assert capabilities.automation is AutomationSupport.UNSUPPORTED_WAYLAND
    assert not capabilities.global_hotkeys
    assert "Wayland" in capabilities.reason


@pytest.mark.unit
@pytest.mark.parametrize("system", ["Windows", "Darwin"])
def test_native_desktops_support_automation(system):
    capabilities = detect_desktop_capabilities({}, system=system)

    assert capabilities.automation_available
    assert capabilities.global_hotkeys


@pytest.mark.unit
def test_x11_supports_automation():
    capabilities = detect_desktop_capabilities(
        {"XDG_SESSION_TYPE": "x11", "DISPLAY": ":0"}, system="Linux"
    )

    assert capabilities.automation_available
