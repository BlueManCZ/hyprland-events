"""Event dispatcher with blocking and fd-based integration modes."""

from __future__ import annotations

import logging
import socket
from collections import defaultdict
from collections.abc import Callable

from hyprland_socket import Event, connect_event_socket, parse_event_line

from .types import parse_event

log = logging.getLogger(__name__)


class EventDispatcher:
    """Dispatches typed Hyprland events to registered callbacks.

    Callbacks receive the parsed typed event dataclass as their sole argument.
    For unknown events, the raw ``hyprland_socket.Event`` is passed instead.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def on(self, event_name: str, callback: Callable | None = None) -> Callable:
        """Register a callback for an event name.

        Can be used directly or as a decorator::

            dispatcher.on("workspacev2", my_handler)

            @dispatcher.on("workspacev2")
            def my_handler(event):
                ...
        """

        def _register(cb: Callable) -> Callable:
            if cb not in self._handlers[event_name]:
                self._handlers[event_name].append(cb)
            return cb

        if callback is not None:
            return _register(callback)
        return _register

    def off(self, event_name: str, callback: Callable) -> None:
        """Remove a callback for an event name."""
        try:
            self._handlers[event_name].remove(callback)
        except ValueError:
            pass

    def _dispatch(self, raw_event: Event) -> None:
        """Dispatch a raw event to all matching handlers.

        Malformed events that fail to parse are logged and skipped —
        they will not crash the event loop.
        """
        try:
            typed = parse_event(raw_event.name, raw_event.data)
        except Exception:
            log.debug("Failed to parse event %s: %r", raw_event.name, raw_event.data)
            typed = None
        payload = typed if typed is not None else raw_event
        for cb in self._handlers.get(raw_event.name, []):
            cb(payload)
        for cb in self._handlers.get("*", []):
            cb(payload)

    def _process_lines(self, buf: str) -> str:
        """Parse and dispatch complete lines from *buf*, return the remainder."""
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            event = parse_event_line(line)
            if event is not None:
                self._dispatch(event)
        return buf

    def run(self, timeout: float | None = None) -> None:
        """Blocking event loop — reads from the event socket and dispatches.

        Returns when the socket closes or *timeout* is reached (if set).
        """
        sock = connect_event_socket(timeout)
        try:
            buf = ""
            while True:
                try:
                    chunk = sock.recv(4096)
                except TimeoutError:
                    return
                if not chunk:
                    break
                buf = self._process_lines(buf + chunk.decode())
        finally:
            sock.close()

    def connect(
        self, timeout: float | None = None
    ) -> tuple[socket.socket, Callable[[bytes], None]]:
        """For external event loops. Returns (socket, feed_fn).

        The caller adds ``socket.fileno()`` to their event loop and calls
        ``feed_fn(data)`` when data arrives. ``feed_fn`` buffers partial
        lines and dispatches complete events.

        Usage with GLib::

            sock, feed = dispatcher.connect()
            GLib.io_add_watch(
                sock.fileno(), GLib.IO_IN,
                lambda *_: feed(sock.recv(4096)) or True,
            )
        """
        sock = connect_event_socket(timeout)
        buf = ""

        def feed(data: bytes) -> None:
            nonlocal buf
            buf = self._process_lines(buf + data.decode())

        return sock, feed
