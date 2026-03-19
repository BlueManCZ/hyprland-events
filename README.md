# hyprland-events

Typed event dispatch layer for [Hyprland](https://hyprland.org/) IPC.
Built on top of [hyprland-socket](https://github.com/BlueManCZ/hyprland-socket).

Every Hyprland event is parsed into a frozen dataclass with named fields — no
more splitting strings on commas.

## Installation

```bash
pip install hyprland-events
```

## Usage

### Blocking event loop

```python
from hyprland_events import EventDispatcher, WorkspaceEvent, MonitorAddedEvent

dispatcher = EventDispatcher()

@dispatcher.on("workspacev2")
def on_workspace(event: WorkspaceEvent):
    print(f"Switched to workspace {event.id} ({event.name})")

@dispatcher.on("monitoraddedv2")
def on_monitor(event: MonitorAddedEvent):
    print(f"Monitor {event.name} connected")

dispatcher.run()  # blocks until the socket closes
```

`on()` also works without the decorator syntax:

```python
dispatcher.on("workspacev2", my_handler)
```

### GLib / GTK integration

```python
from gi.repository import GLib
from hyprland_events import EventDispatcher

dispatcher = EventDispatcher()
dispatcher.on("configreloaded", lambda e: print("Config reloaded"))

sock, feed = dispatcher.connect()
GLib.io_add_watch(
    sock.fileno(), GLib.IO_IN,
    lambda *_: feed(sock.recv(4096)) or True,
)
```

### Wildcard handler

```python
dispatcher.on("*", lambda event: print(event))
```

### One-off parsing

```python
from hyprland_events import parse_event

event = parse_event("workspacev2", "3,code")
# WorkspaceEvent(id=3, name='code')
```

## Supported events

| Socket name          | Dataclass               | Fields                                      |
|----------------------|-------------------------|---------------------------------------------|
| `workspacev2`        | `WorkspaceEvent`        | `id`, `name`                                |
| `focusedmonv2`       | `FocusedMonitorEvent`   | `monitor`, `workspace_id`                   |
| `activewindow`       | `ActiveWindowEvent`     | `wm_class`, `title`                         |
| `activewindowv2`     | `ActiveWindowV2Event`   | `address`                                   |
| `fullscreen`         | `FullscreenEvent`       | `active`                                    |
| `monitoraddedv2`     | `MonitorAddedEvent`     | `id`, `name`, `description`                 |
| `monitorremovedv2`   | `MonitorRemovedEvent`   | `id`, `name`, `description`                 |
| `createworkspacev2`  | `CreateWorkspaceEvent`  | `id`, `name`                                |
| `destroyworkspacev2` | `DestroyWorkspaceEvent` | `id`, `name`                                |
| `moveworkspacev2`    | `MoveWorkspaceEvent`    | `id`, `name`, `monitor`                     |
| `renameworkspace`    | `RenameWorkspaceEvent`  | `id`, `name`                                |
| `activespecialv2`    | `ActiveSpecialEvent`    | `id`, `name`, `monitor`                     |
| `activelayout`       | `ActiveLayoutEvent`     | `keyboard`, `layout`                        |
| `openwindow`         | `OpenWindowEvent`       | `address`, `workspace`, `wm_class`, `title` |
| `closewindow`        | `CloseWindowEvent`      | `address`                                   |
| `movewindowv2`       | `MoveWindowEvent`       | `address`, `workspace_id`, `workspace_name` |
| `openlayer`          | `OpenLayerEvent`        | `namespace`                                 |
| `closelayer`         | `CloseLayerEvent`       | `namespace`                                 |
| `submap`             | `SubmapEvent`           | `name`                                      |
| `changefloatingmode` | `FloatingEvent`         | `address`, `floating`                       |
| `urgent`             | `UrgentEvent`           | `address`                                   |
| `minimize`           | `MinimizeEvent`         | `address`, `minimized`                      |
| `screencast`         | `ScreencastEvent`       | `active`, `owner`                           |
| `windowtitlev2`      | `WindowTitleEvent`      | `address`, `title`                          |
| `configreloaded`     | `ConfigReloadedEvent`   | *(none)*                                    |
| `pin`                | `PinEvent`              | `address`, `pinned`                         |
| `kill`               | `KillEvent`             | `address`                                   |
| `togglegroup`        | `ToggleGroupEvent`      | `active`, `addresses`                       |
| `moveintogroup`      | `MoveIntoGroupEvent`    | `address`                                   |
| `moveoutofgroup`     | `MoveOutOfGroupEvent`   | `address`                                   |
| `ignoregrouplock`    | `IgnoreGroupLockEvent`  | `active`                                    |
| `lockgroups`         | `LockGroupsEvent`       | `locked`                                    |
| `bell`               | `BellEvent`             | `address`                                   |

Unrecognized events are passed to handlers as the raw
`hyprland_socket.Event(name, data)` object.

## License

MIT
