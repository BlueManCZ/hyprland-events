"""Typed event payloads for Hyprland events."""

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Self, get_type_hints

# --- Auto-parse machinery ---

_COERCIONS: dict[type, Callable[[str], Any]] = {
    str: str,
    int: int,
    bool: lambda s: s == "1",
}


class _AutoParse:
    """Mixin that auto-generates ``parse()`` from dataclass field types.

    Fields are filled left-to-right from comma-split parts. The last field
    receives the unsplit remainder, preserving commas in values like titles.
    Bool fields use the Hyprland convention: ``"1"`` is True, anything else
    is False.
    """

    @classmethod
    def parse(cls, data: str) -> Self:
        hints = get_type_hints(cls)
        fields = dataclasses.fields(cls)  # type: ignore[arg-type]
        if not fields:
            return cls()
        if len(fields) == 1:
            f = fields[0]
            return cls(**{f.name: _COERCIONS[hints[f.name]](data)})
        parts = data.split(",", len(fields) - 1)
        return cls(**{f.name: _COERCIONS[hints[f.name]](v) for f, v in zip(fields, parts)})


# --- Event dataclasses ---


@dataclass(frozen=True, slots=True)
class WorkspaceEvent(_AutoParse):
    """Active workspace changed (workspacev2>>ID,NAME)."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class FocusedMonitorEvent(_AutoParse):
    """Focused monitor changed (focusedmonv2>>MONNAME,WORKSPACEID)."""

    monitor: str
    workspace_id: int


@dataclass(frozen=True, slots=True)
class ActiveWindowEvent(_AutoParse):
    """Active window changed (activewindow>>CLASS,TITLE)."""

    wm_class: str
    title: str


@dataclass(frozen=True, slots=True)
class ActiveWindowV2Event(_AutoParse):
    """Active window changed (activewindowv2>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class FullscreenEvent(_AutoParse):
    """Fullscreen state changed (fullscreen>>STATE)."""

    active: bool


@dataclass(frozen=True, slots=True)
class MonitorAddedEvent(_AutoParse):
    """Monitor added (monitoraddedv2>>ID,NAME,DESCRIPTION)."""

    id: int
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class MonitorRemovedEvent(_AutoParse):
    """Monitor removed (monitorremovedv2>>ID,NAME,DESCRIPTION)."""

    id: int
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class CreateWorkspaceEvent(_AutoParse):
    """Workspace created (createworkspacev2>>ID,NAME)."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class DestroyWorkspaceEvent(_AutoParse):
    """Workspace destroyed (destroyworkspacev2>>ID,NAME)."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class MoveWorkspaceEvent(_AutoParse):
    """Workspace moved to monitor (moveworkspacev2>>ID,NAME,MONNAME)."""

    id: int
    name: str
    monitor: str


@dataclass(frozen=True, slots=True)
class RenameWorkspaceEvent(_AutoParse):
    """Workspace renamed (renameworkspace>>ID,NEWNAME)."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class ActiveSpecialEvent(_AutoParse):
    """Active special workspace changed (activespecialv2>>ID,NAME,MONNAME)."""

    id: int
    name: str
    monitor: str


@dataclass(frozen=True, slots=True)
class ActiveLayoutEvent(_AutoParse):
    """Keyboard layout changed (activelayout>>KEYBOARD,LAYOUT)."""

    keyboard: str
    layout: str


@dataclass(frozen=True, slots=True)
class OpenWindowEvent(_AutoParse):
    """Window opened (openwindow>>ADDRESS,WORKSPACE,CLASS,TITLE)."""

    address: str
    workspace: str
    wm_class: str
    title: str


@dataclass(frozen=True, slots=True)
class CloseWindowEvent(_AutoParse):
    """Window closed (closewindow>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class MoveWindowEvent(_AutoParse):
    """Window moved (movewindowv2>>ADDRESS,ID,NAME)."""

    address: str
    workspace_id: int
    workspace_name: str


@dataclass(frozen=True, slots=True)
class OpenLayerEvent(_AutoParse):
    """Layer surface opened (openlayer>>NAMESPACE)."""

    namespace: str


@dataclass(frozen=True, slots=True)
class CloseLayerEvent(_AutoParse):
    """Layer surface closed (closelayer>>NAMESPACE)."""

    namespace: str


@dataclass(frozen=True, slots=True)
class SubmapEvent(_AutoParse):
    """Submap changed (submap>>NAME)."""

    name: str


@dataclass(frozen=True, slots=True)
class FloatingEvent(_AutoParse):
    """Floating mode changed (changefloatingmode>>ADDRESS,FLOATING)."""

    address: str
    floating: bool


@dataclass(frozen=True, slots=True)
class UrgentEvent(_AutoParse):
    """Urgent window (urgent>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class MinimizeEvent(_AutoParse):
    """Window minimized (minimize>>ADDRESS,MINIMIZED)."""

    address: str
    minimized: bool


@dataclass(frozen=True, slots=True)
class ScreencastEvent(_AutoParse):
    """Screencast state changed (screencast>>STATE,OWNER)."""

    active: bool
    owner: str


@dataclass(frozen=True, slots=True)
class WindowTitleEvent(_AutoParse):
    """Window title changed (windowtitlev2>>ADDRESS,TITLE)."""

    address: str
    title: str


@dataclass(frozen=True, slots=True)
class ConfigReloadedEvent(_AutoParse):
    """Config reloaded (configreloaded>>)."""


@dataclass(frozen=True, slots=True)
class PinEvent(_AutoParse):
    """Window pinned (pin>>ADDRESS,STATE)."""

    address: str
    pinned: bool


@dataclass(frozen=True, slots=True)
class KillEvent(_AutoParse):
    """Window killed via hyprctl kill (kill>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class ToggleGroupEvent:
    """Group toggled (togglegroup>>STATE,ADDRESSES).

    Addresses is a comma-separated list of window addresses in the group.
    """

    active: bool
    addresses: tuple[str, ...]

    @classmethod
    def parse(cls, data: str) -> Self:
        state, rest = data.split(",", 1)
        addrs = tuple(a for a in rest.split(",") if a) if rest else ()
        return cls(active=state == "1", addresses=addrs)


@dataclass(frozen=True, slots=True)
class MoveIntoGroupEvent(_AutoParse):
    """Window moved into group (moveintogroup>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class MoveOutOfGroupEvent(_AutoParse):
    """Window moved out of group (moveoutofgroup>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class IgnoreGroupLockEvent(_AutoParse):
    """ignoregrouplock toggled (ignoregrouplock>>STATE)."""

    active: bool


@dataclass(frozen=True, slots=True)
class LockGroupsEvent(_AutoParse):
    """lockgroups toggled (lockgroups>>STATE)."""

    locked: bool


@dataclass(frozen=True, slots=True)
class BellEvent(_AutoParse):
    """System bell requested (bell>>ADDRESS).

    Address may be empty if the bell is not associated with a window.
    """

    address: str


# --- Parser registry ---
# Maps v2 event names (preferred) to their parse functions.
# For events that have both v1 and v2 variants, only the v2 is registered.

EVENT_PARSERS: dict[str, type[_AutoParse] | type[ToggleGroupEvent]] = {
    "workspacev2": WorkspaceEvent,
    "focusedmonv2": FocusedMonitorEvent,
    "activewindow": ActiveWindowEvent,
    "activewindowv2": ActiveWindowV2Event,
    "fullscreen": FullscreenEvent,
    "monitoraddedv2": MonitorAddedEvent,
    "monitorremovedv2": MonitorRemovedEvent,
    "createworkspacev2": CreateWorkspaceEvent,
    "destroyworkspacev2": DestroyWorkspaceEvent,
    "moveworkspacev2": MoveWorkspaceEvent,
    "renameworkspace": RenameWorkspaceEvent,
    "activespecialv2": ActiveSpecialEvent,
    "activelayout": ActiveLayoutEvent,
    "openwindow": OpenWindowEvent,
    "closewindow": CloseWindowEvent,
    "movewindowv2": MoveWindowEvent,
    "openlayer": OpenLayerEvent,
    "closelayer": CloseLayerEvent,
    "submap": SubmapEvent,
    "changefloatingmode": FloatingEvent,
    "urgent": UrgentEvent,
    "minimize": MinimizeEvent,
    "screencast": ScreencastEvent,
    "windowtitlev2": WindowTitleEvent,
    "configreloaded": ConfigReloadedEvent,
    "pin": PinEvent,
    "kill": KillEvent,
    "togglegroup": ToggleGroupEvent,
    "moveintogroup": MoveIntoGroupEvent,
    "moveoutofgroup": MoveOutOfGroupEvent,
    "ignoregrouplock": IgnoreGroupLockEvent,
    "lockgroups": LockGroupsEvent,
    "bell": BellEvent,
}


def parse_event(name: str, data: str) -> object | None:
    """Parse a raw event name and data into a typed dataclass, or None if unknown."""
    cls = EVENT_PARSERS.get(name)
    if cls is None:
        return None
    return cls.parse(data)
