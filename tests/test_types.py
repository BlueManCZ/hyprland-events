"""Tests for typed event parsing."""

from hyprland_events.types import (
    ActiveLayoutEvent,
    ActiveSpecialEvent,
    ActiveWindowEvent,
    ActiveWindowV2Event,
    BellEvent,
    CloseLayerEvent,
    CloseWindowEvent,
    ConfigReloadedEvent,
    CreateWorkspaceEvent,
    DestroyWorkspaceEvent,
    FloatingEvent,
    FocusedMonitorEvent,
    FullscreenEvent,
    IgnoreGroupLockEvent,
    KillEvent,
    LockGroupsEvent,
    MinimizeEvent,
    MonitorAddedEvent,
    MonitorRemovedEvent,
    MoveIntoGroupEvent,
    MoveOutOfGroupEvent,
    MoveWindowEvent,
    MoveWorkspaceEvent,
    OpenLayerEvent,
    OpenWindowEvent,
    PinEvent,
    RenameWorkspaceEvent,
    ScreencastEvent,
    SubmapEvent,
    ToggleGroupEvent,
    UrgentEvent,
    WindowTitleEvent,
    WorkspaceEvent,
    parse_event,
)


class TestWorkspaceEvent:
    def test_parse(self):
        e = WorkspaceEvent.parse("3,code")
        assert e.id == 3
        assert e.name == "code"

    def test_parse_name_with_comma(self):
        e = WorkspaceEvent.parse("1,my,workspace")
        assert e.id == 1
        assert e.name == "my,workspace"


class TestFocusedMonitorEvent:
    def test_parse(self):
        e = FocusedMonitorEvent.parse("DP-1,2")
        assert e.monitor == "DP-1"
        assert e.workspace_id == 2


class TestActiveWindowEvent:
    def test_parse(self):
        e = ActiveWindowEvent.parse("firefox,YouTube")
        assert e.wm_class == "firefox"
        assert e.title == "YouTube"

    def test_title_with_comma(self):
        e = ActiveWindowEvent.parse("code,file.py — project, editor")
        assert e.wm_class == "code"
        assert e.title == "file.py — project, editor"


class TestActiveWindowV2Event:
    def test_parse(self):
        e = ActiveWindowV2Event.parse("0x55a6c3b0")
        assert e.address == "0x55a6c3b0"


class TestFullscreenEvent:
    def test_active(self):
        assert FullscreenEvent.parse("1").active is True

    def test_inactive(self):
        assert FullscreenEvent.parse("0").active is False


class TestMonitorAddedEvent:
    def test_parse(self):
        e = MonitorAddedEvent.parse("1,HDMI-A-1,LG Electronics 27GL850")
        assert e.id == 1
        assert e.name == "HDMI-A-1"
        assert e.description == "LG Electronics 27GL850"


class TestMonitorRemovedEvent:
    def test_parse(self):
        e = MonitorRemovedEvent.parse("1,HDMI-A-1,LG Electronics 27GL850")
        assert e.id == 1
        assert e.name == "HDMI-A-1"
        assert e.description == "LG Electronics 27GL850"


class TestCreateWorkspaceEvent:
    def test_parse(self):
        e = CreateWorkspaceEvent.parse("5,main")
        assert e.id == 5
        assert e.name == "main"


class TestDestroyWorkspaceEvent:
    def test_parse(self):
        e = DestroyWorkspaceEvent.parse("5,main")
        assert e.id == 5
        assert e.name == "main"


class TestMoveWorkspaceEvent:
    def test_parse(self):
        e = MoveWorkspaceEvent.parse("2,web,DP-2")
        assert e.id == 2
        assert e.name == "web"
        assert e.monitor == "DP-2"


class TestRenameWorkspaceEvent:
    def test_parse(self):
        e = RenameWorkspaceEvent.parse("3,new name")
        assert e.id == 3
        assert e.name == "new name"


class TestActiveSpecialEvent:
    def test_parse(self):
        e = ActiveSpecialEvent.parse("1,special:scratch,DP-1")
        assert e.id == 1
        assert e.name == "special:scratch"
        assert e.monitor == "DP-1"


class TestActiveLayoutEvent:
    def test_parse(self):
        e = ActiveLayoutEvent.parse("at-translated-set-2-keyboard,English (US)")
        assert e.keyboard == "at-translated-set-2-keyboard"
        assert e.layout == "English (US)"


class TestOpenWindowEvent:
    def test_parse(self):
        e = OpenWindowEvent.parse("0x1234,2,kitty,~")
        assert e.address == "0x1234"
        assert e.workspace == "2"
        assert e.wm_class == "kitty"
        assert e.title == "~"

    def test_title_with_comma(self):
        e = OpenWindowEvent.parse("0x1234,1,code,main.py — proj, src")
        assert e.title == "main.py — proj, src"


class TestCloseWindowEvent:
    def test_parse(self):
        e = CloseWindowEvent.parse("0x1234")
        assert e.address == "0x1234"


class TestMoveWindowEvent:
    def test_parse(self):
        e = MoveWindowEvent.parse("0x1234,3,code")
        assert e.address == "0x1234"
        assert e.workspace_id == 3
        assert e.workspace_name == "code"


class TestOpenLayerEvent:
    def test_parse(self):
        e = OpenLayerEvent.parse("waybar")
        assert e.namespace == "waybar"


class TestCloseLayerEvent:
    def test_parse(self):
        e = CloseLayerEvent.parse("waybar")
        assert e.namespace == "waybar"


class TestSubmapEvent:
    def test_parse(self):
        e = SubmapEvent.parse("resize")
        assert e.name == "resize"

    def test_empty(self):
        e = SubmapEvent.parse("")
        assert e.name == ""


class TestFloatingEvent:
    def test_floating(self):
        e = FloatingEvent.parse("0x1234,1")
        assert e.address == "0x1234"
        assert e.floating is True

    def test_tiled(self):
        e = FloatingEvent.parse("0x1234,0")
        assert e.floating is False


class TestUrgentEvent:
    def test_parse(self):
        e = UrgentEvent.parse("0x1234")
        assert e.address == "0x1234"


class TestMinimizeEvent:
    def test_minimized(self):
        e = MinimizeEvent.parse("0x1234,1")
        assert e.minimized is True

    def test_restored(self):
        e = MinimizeEvent.parse("0x1234,0")
        assert e.minimized is False


class TestScreencastEvent:
    def test_active(self):
        e = ScreencastEvent.parse("1,0")
        assert e.active is True
        assert e.owner == "0"


class TestWindowTitleEvent:
    def test_parse(self):
        e = WindowTitleEvent.parse("0x1234,New Title")
        assert e.address == "0x1234"
        assert e.title == "New Title"


class TestConfigReloadedEvent:
    def test_parse(self):
        e = ConfigReloadedEvent.parse("")
        assert isinstance(e, ConfigReloadedEvent)


class TestPinEvent:
    def test_pinned(self):
        e = PinEvent.parse("0x1234,1")
        assert e.pinned is True

    def test_unpinned(self):
        e = PinEvent.parse("0x1234,0")
        assert e.pinned is False


class TestKillEvent:
    def test_parse(self):
        e = KillEvent.parse("0x55a6c3b0")
        assert e.address == "0x55a6c3b0"


class TestToggleGroupEvent:
    def test_activated(self):
        e = ToggleGroupEvent.parse("1,0x1234,0x5678")
        assert e.active is True
        assert e.addresses == ("0x1234", "0x5678")

    def test_deactivated_single(self):
        e = ToggleGroupEvent.parse("0,0x1234")
        assert e.active is False
        assert e.addresses == ("0x1234",)

    def test_empty_addresses(self):
        e = ToggleGroupEvent.parse("1,")
        assert e.active is True
        assert e.addresses == ()


class TestMoveIntoGroupEvent:
    def test_parse(self):
        e = MoveIntoGroupEvent.parse("0x1234")
        assert e.address == "0x1234"


class TestMoveOutOfGroupEvent:
    def test_parse(self):
        e = MoveOutOfGroupEvent.parse("0x1234")
        assert e.address == "0x1234"


class TestIgnoreGroupLockEvent:
    def test_enabled(self):
        assert IgnoreGroupLockEvent.parse("1").active is True

    def test_disabled(self):
        assert IgnoreGroupLockEvent.parse("0").active is False


class TestLockGroupsEvent:
    def test_locked(self):
        assert LockGroupsEvent.parse("1").locked is True

    def test_unlocked(self):
        assert LockGroupsEvent.parse("0").locked is False


class TestBellEvent:
    def test_with_address(self):
        e = BellEvent.parse("0x1234")
        assert e.address == "0x1234"

    def test_empty_address(self):
        e = BellEvent.parse("")
        assert e.address == ""


class TestParseEvent:
    def test_known_event(self):
        result = parse_event("workspacev2", "3,code")
        assert isinstance(result, WorkspaceEvent)
        assert result.id == 3

    def test_unknown_event(self):
        assert parse_event("unknownevent", "data") is None

    def test_all_registered_events(self):
        from hyprland_events.types import EVENT_PARSERS

        assert len(EVENT_PARSERS) == 33
