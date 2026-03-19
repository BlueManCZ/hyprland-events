"""Tests for EventDispatcher."""

from unittest.mock import MagicMock, patch

from hyprland_socket import Event

from hyprland_events.dispatcher import EventDispatcher
from hyprland_events.types import MonitorRemovedEvent, WorkspaceEvent


class TestOnOff:
    def test_on_registers_callback(self):
        d = EventDispatcher()
        cb = MagicMock()
        d.on("workspacev2", cb)
        assert cb in d._handlers["workspacev2"]

    def test_on_ignores_duplicate(self):
        d = EventDispatcher()
        cb = MagicMock()
        d.on("workspacev2", cb)
        d.on("workspacev2", cb)
        assert d._handlers["workspacev2"].count(cb) == 1

    def test_off_removes_callback(self):
        d = EventDispatcher()
        cb = MagicMock()
        d.on("workspacev2", cb)
        d.off("workspacev2", cb)
        assert cb not in d._handlers["workspacev2"]

    def test_off_missing_is_noop(self):
        d = EventDispatcher()
        d.off("workspacev2", MagicMock())  # should not raise


class TestDecorator:
    def test_decorator_registers_and_returns_function(self):
        d = EventDispatcher()

        @d.on("workspacev2")
        def handler(event):
            pass

        assert handler in d._handlers["workspacev2"]
        assert callable(handler)

    def test_decorator_dispatches(self):
        d = EventDispatcher()
        received = []

        @d.on("workspacev2")
        def handler(event):
            received.append(event)

        d._dispatch(Event(name="workspacev2", data="3,code"))
        assert len(received) == 1
        assert isinstance(received[0], WorkspaceEvent)

    def test_decorator_ignores_duplicate(self):
        d = EventDispatcher()

        @d.on("workspacev2")
        def handler(event):
            pass

        # Decorate the same function object again
        d.on("workspacev2")(handler)
        assert d._handlers["workspacev2"].count(handler) == 1

    def test_off_works_with_decorated_function(self):
        d = EventDispatcher()

        @d.on("workspacev2")
        def handler(event):
            pass

        d.off("workspacev2", handler)
        assert handler not in d._handlers["workspacev2"]


class TestDispatch:
    def test_typed_event(self):
        d = EventDispatcher()
        received = []
        d.on("workspacev2", received.append)
        d._dispatch(Event(name="workspacev2", data="3,code"))
        assert len(received) == 1
        assert isinstance(received[0], WorkspaceEvent)
        assert received[0].id == 3
        assert received[0].name == "code"

    def test_unknown_event_passes_raw(self):
        d = EventDispatcher()
        received = []
        d.on("customevent", received.append)
        raw = Event(name="customevent", data="hello")
        d._dispatch(raw)
        assert received == [raw]

    def test_wildcard_handler(self):
        d = EventDispatcher()
        received = []
        d.on("*", received.append)
        d._dispatch(Event(name="monitorremovedv2", data="1,DP-1,Some Monitor"))
        assert len(received) == 1
        assert isinstance(received[0], MonitorRemovedEvent)

    def test_multiple_handlers(self):
        d = EventDispatcher()
        a, b = MagicMock(), MagicMock()
        d.on("workspacev2", a)
        d.on("workspacev2", b)
        d._dispatch(Event(name="workspacev2", data="1,main"))
        a.assert_called_once()
        b.assert_called_once()

    def test_no_handlers_is_noop(self):
        d = EventDispatcher()
        d._dispatch(Event(name="workspacev2", data="1,x"))  # should not raise

    def test_malformed_event_falls_back_to_raw(self):
        d = EventDispatcher()
        received = []
        d.on("workspacev2", received.append)
        # workspacev2 expects "ID,NAME" but we send garbage
        d._dispatch(Event(name="workspacev2", data="not_a_number"))
        assert len(received) == 1
        # Parse failed, so handler gets the raw Event instead
        assert isinstance(received[0], Event)
        assert received[0].data == "not_a_number"

    def test_malformed_event_does_not_break_loop(self):
        d = EventDispatcher()
        received = []
        d.on("workspacev2", received.append)
        # First event is malformed, second is valid
        d._dispatch(Event(name="workspacev2", data="bad"))
        d._dispatch(Event(name="workspacev2", data="3,code"))
        assert len(received) == 2
        assert isinstance(received[0], Event)  # raw fallback
        assert isinstance(received[1], WorkspaceEvent)  # parsed OK


class TestConnect:
    @patch("hyprland_events.dispatcher.connect_event_socket")
    def test_returns_socket_and_feed(self, mock_connect):
        mock_sock = MagicMock()
        mock_connect.return_value = mock_sock

        d = EventDispatcher()
        sock, feed = d.connect()

        assert sock is mock_sock
        assert callable(feed)

    @patch("hyprland_events.dispatcher.connect_event_socket")
    def test_feed_dispatches_complete_lines(self, mock_connect):
        mock_connect.return_value = MagicMock()

        d = EventDispatcher()
        received = []
        d.on("workspacev2", received.append)

        _, feed = d.connect()
        feed(b"workspacev2>>5,term\n")

        assert len(received) == 1
        assert isinstance(received[0], WorkspaceEvent)
        assert received[0].id == 5

    @patch("hyprland_events.dispatcher.connect_event_socket")
    def test_feed_buffers_partial_lines(self, mock_connect):
        mock_connect.return_value = MagicMock()

        d = EventDispatcher()
        received = []
        d.on("monitorremovedv2", received.append)

        _, feed = d.connect()
        feed(b"monitorremo")
        assert len(received) == 0
        feed(b"vedv2>>1,DP-1,Some Monitor\n")
        assert len(received) == 1
        assert isinstance(received[0], MonitorRemovedEvent)
        assert received[0].name == "DP-1"

    @patch("hyprland_events.dispatcher.connect_event_socket")
    def test_feed_handles_multiple_events_in_chunk(self, mock_connect):
        mock_connect.return_value = MagicMock()

        d = EventDispatcher()
        received = []
        d.on("*", received.append)

        _, feed = d.connect()
        feed(b"kill>>0x1234\nbell>>0x5678\n")
        assert len(received) == 2
