"""Integration tests for tmux-session — uses real tmux."""

import time

import pytest

import server

SESSION = "test-tmux-session-integ"


@pytest.fixture(autouse=True)
def cleanup():
    """Kill test session after each test."""
    yield
    server.kill_session(SESSION)


def test_create_and_has_session():
    result = server.create_session(SESSION, "sleep 30")
    assert result["created"] is True

    check = server.has_session(SESSION)
    assert check["alive"] is True


def test_create_duplicate_fails():
    server.create_session(SESSION, "sleep 30")
    result = server.create_session(SESSION, "sleep 30")
    assert result["created"] is False
    assert result["error"]


def test_capture_output():
    create = server.create_session(SESSION, "echo 'hello from tmux'; sleep 30")
    assert create["created"] is True
    time.sleep(1)

    result = server.capture_output(SESSION)
    assert result["error"] is None
    assert "hello from tmux" in result["output"]


def test_send_keys():
    server.create_session(SESSION, "cat")
    time.sleep(0.5)

    result = server.send_keys(SESSION, "test_input")
    assert result["sent"] is True

    server.send_keys(SESSION, "Enter")
    time.sleep(0.5)

    output = server.capture_output(SESSION)
    assert "test_input" in output["output"]


def test_kill_session():
    server.create_session(SESSION, "sleep 30")
    result = server.kill_session(SESSION)
    assert result["killed"] is True

    check = server.has_session(SESSION)
    assert check["alive"] is False


def test_kill_nonexistent():
    result = server.kill_session("nonexistent-session-xyz")
    assert result["killed"] is False


def test_has_session_nonexistent():
    result = server.has_session("nonexistent-session-xyz")
    assert result["alive"] is False


def test_capture_nonexistent():
    result = server.capture_output("nonexistent-session-xyz")
    assert result["output"] is None
    assert result["error"]


@pytest.mark.skipif(
    not server._yakuake_available(),
    reason="Yakuake not running"
)
class TestShowSession:

    def test_show_and_close(self):
        server.create_session(SESSION, "echo visible_test; sleep 30")
        time.sleep(0.5)

        result = server.show_session(SESSION, "Integration Test")
        assert result["displayed"] is True
        assert result["backend"] == "yakuake"

        time.sleep(1)

        close = server.close_display(result["yakuake_session"])
        assert close["closed"] is True
