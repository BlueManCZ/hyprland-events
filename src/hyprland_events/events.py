"""Typed event payloads for Hyprland events."""

from dataclasses import dataclass, fields
from typing import Self, get_type_hints

# --- Auto-parse machinery ---


def _parse_bool(s: str) -> bool:
    return s == "1"


class HyprlandEvent:
    """Base class for all typed Hyprland events.

    Auto-generates ``parse()`` from dataclass field types. Fields are filled
    left-to-right from comma-split parts. The last field receives the unsplit
    remainder, preserving commas in values like titles. Bool fields use the
    Hyprland convention: ``"1"`` is True, anything else is False.

    Field metadata is resolved once per subclass and cached on the class.
    """

    @classmethod
    def parse(cls, data: str) -> Self:
        try:
            fc = cls.__dict__["_field_coercions"]
        except KeyError:
            hints = get_type_hints(cls)
            fc = tuple(
                (f.name, _parse_bool if hints[f.name] is bool else hints[f.name])
                for f in fields(cls)  # type: ignore[arg-type]
            )
            cls._field_coercions = fc  # type: ignore[attr-defined]

        if not fc:
            return cls()
        if len(fc) == 1:
            name, coerce = fc[0]
            return cls(**{name: coerce(data)})
        parts = data.split(",", len(fc) - 1)
        return cls(**{name: coerce(v) for (name, coerce), v in zip(fc, parts)})


# --- Event dataclasses ---


@dataclass(frozen=True, slots=True)
class WorkspaceEvent(HyprlandEvent):
    """Active workspace changed (workspacev2>>ID,NAME)."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class FocusedMonitorEvent(HyprlandEvent):
    """Focused monitor changed (focusedmonv2>>MONNAME,WORKSPACEID)."""

    monitor: str
    workspace_id: int


@dataclass(frozen=True, slots=True)
class ActiveWindowEvent(HyprlandEvent):
    """Active window changed (activewindow>>CLASS,TITLE)."""

    wm_class: str
    title: str


@dataclass(frozen=True, slots=True)
class ActiveWindowV2Event(HyprlandEvent):
    """Active window changed (activewindowv2>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class FullscreenEvent(HyprlandEvent):
    """Fullscreen state changed (fullscreen>>STATE)."""

    active: bool


@dataclass(frozen=True, slots=True)
class MonitorAddedEvent(HyprlandEvent):
    """Monitor added (monitoraddedv2>>ID,NAME,DESCRIPTION)."""

    id: int
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class MonitorRemovedEvent(HyprlandEvent):
    """Monitor removed (monitorremovedv2>>ID,NAME,DESCRIPTION)."""

    id: int
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class CreateWorkspaceEvent(HyprlandEvent):
    """Workspace created (createworkspacev2>>ID,NAME)."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class DestroyWorkspaceEvent(HyprlandEvent):
    """Workspace destroyed (destroyworkspacev2>>ID,NAME)."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class MoveWorkspaceEvent(HyprlandEvent):
    """Workspace moved to monitor (moveworkspacev2>>ID,NAME,MONNAME)."""

    id: int
    name: str
    monitor: str


@dataclass(frozen=True, slots=True)
class RenameWorkspaceEvent(HyprlandEvent):
    """Workspace renamed (renameworkspace>>ID,NEWNAME)."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class ActiveSpecialEvent(HyprlandEvent):
    """Active special workspace changed (activespecialv2>>ID,NAME,MONNAME)."""

    id: int
    name: str
    monitor: str


@dataclass(frozen=True, slots=True)
class ActiveLayoutEvent(HyprlandEvent):
    """Keyboard layout changed (activelayout>>KEYBOARD,LAYOUT)."""

    keyboard: str
    layout: str


@dataclass(frozen=True, slots=True)
class OpenWindowEvent(HyprlandEvent):
    """Window opened (openwindow>>ADDRESS,WORKSPACE,CLASS,TITLE)."""

    address: str
    workspace: str
    wm_class: str
    title: str


@dataclass(frozen=True, slots=True)
class CloseWindowEvent(HyprlandEvent):
    """Window closed (closewindow>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class MoveWindowEvent(HyprlandEvent):
    """Window moved (movewindowv2>>ADDRESS,ID,NAME)."""

    address: str
    workspace_id: int
    workspace_name: str


@dataclass(frozen=True, slots=True)
class OpenLayerEvent(HyprlandEvent):
    """Layer surface opened (openlayer>>NAMESPACE)."""

    namespace: str


@dataclass(frozen=True, slots=True)
class CloseLayerEvent(HyprlandEvent):
    """Layer surface closed (closelayer>>NAMESPACE)."""

    namespace: str


@dataclass(frozen=True, slots=True)
class SubmapEvent(HyprlandEvent):
    """Submap changed (submap>>NAME)."""

    name: str


@dataclass(frozen=True, slots=True)
class FloatingEvent(HyprlandEvent):
    """Floating mode changed (changefloatingmode>>ADDRESS,FLOATING)."""

    address: str
    floating: bool


@dataclass(frozen=True, slots=True)
class UrgentEvent(HyprlandEvent):
    """Urgent window (urgent>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class MinimizeEvent(HyprlandEvent):
    """Window minimized (minimized>>ADDRESS,MINIMIZED)."""

    address: str
    minimized: bool


@dataclass(frozen=True, slots=True)
class ScreencastEvent(HyprlandEvent):
    """Screencast state changed (screencast>>STATE,OWNER)."""

    active: bool
    owner: int


@dataclass(frozen=True, slots=True)
class WindowTitleEvent(HyprlandEvent):
    """Window title changed (windowtitlev2>>ADDRESS,TITLE)."""

    address: str
    title: str


@dataclass(frozen=True, slots=True)
class ConfigReloadedEvent(HyprlandEvent):
    """Config reloaded (configreloaded>>)."""


@dataclass(frozen=True, slots=True)
class PinEvent(HyprlandEvent):
    """Window pinned (pin>>ADDRESS,STATE)."""

    address: str
    pinned: bool


@dataclass(frozen=True, slots=True)
class KillEvent(HyprlandEvent):
    """Window killed via hyprctl kill (kill>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class ToggleGroupEvent(HyprlandEvent):
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
class MoveIntoGroupEvent(HyprlandEvent):
    """Window moved into group (moveintogroup>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class MoveOutOfGroupEvent(HyprlandEvent):
    """Window moved out of group (moveoutofgroup>>ADDRESS)."""

    address: str


@dataclass(frozen=True, slots=True)
class IgnoreGroupLockEvent(HyprlandEvent):
    """ignoregrouplock toggled (ignoregrouplock>>STATE)."""

    active: bool


@dataclass(frozen=True, slots=True)
class LockGroupsEvent(HyprlandEvent):
    """lockgroups toggled (lockgroups>>STATE)."""

    locked: bool


@dataclass(frozen=True, slots=True)
class BellEvent(HyprlandEvent):
    """System bell requested (bell>>ADDRESS).

    Address may be empty if the bell is not associated with a window.
    """

    address: str


# --- Parser registry ---
# Maps v2 event names (preferred) to their parse functions.
# For events that have both v1 and v2 variants, only the v2 is registered.

EVENT_PARSERS: dict[str, type[HyprlandEvent]] = {
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
    "minimized": MinimizeEvent,
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


def parse_event(name: str, data: str) -> HyprlandEvent | None:
    """Parse a raw event name and data into a typed dataclass, or None if unknown."""
    cls = EVENT_PARSERS.get(name)
    if cls is None:
        return None
    return cls.parse(data)
