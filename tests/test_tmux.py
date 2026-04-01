"""Tests for tmux-session MCP tools."""

from unittest.mock import patch, MagicMock
import subprocess

import server


def _mock_run(returncode=0, stdout="", stderr=""):
    """Create a mock subprocess.CompletedProcess."""
    result = MagicMock(spec=subprocess.CompletedProcess)
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


@patch("server.subprocess.run")
def test_create_session_success(mock_run):
    mock_run.return_value = _mock_run(returncode=0)
    result = server.create_session("test-sess", "echo hello")
    assert result["created"] is True
    assert result["session"] == "test-sess"
    assert result["error"] is None
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[:4] == ["tmux", "new-session", "-d", "-s"]


@patch("server.subprocess.run")
def test_create_session_failure(mock_run):
    mock_run.return_value = _mock_run(returncode=1, stderr="duplicate session")
    result = server.create_session("test-sess", "echo hello")
    assert result["created"] is False
    assert "duplicate" in result["error"]


@patch("server.subprocess.run")
def test_send_keys(mock_run):
    mock_run.return_value = _mock_run(returncode=0)
    result = server.send_keys("test-sess", "Enter")
    assert result["sent"] is True
    args = mock_run.call_args[0][0]
    assert args == ["tmux", "send-keys", "-t", "test-sess", "Enter"]


@patch("server.subprocess.run")
def test_kill_session(mock_run):
    mock_run.return_value = _mock_run(returncode=0)
    result = server.kill_session("test-sess")
    assert result["killed"] is True


@patch("server.subprocess.run")
def test_kill_session_not_found(mock_run):
    mock_run.return_value = _mock_run(returncode=1, stderr="session not found")
    result = server.kill_session("ghost")
    assert result["killed"] is False
    assert "not found" in result["error"]


@patch("server.subprocess.run")
def test_has_session_alive(mock_run):
    mock_run.return_value = _mock_run(returncode=0)
    result = server.has_session("test-sess")
    assert result["alive"] is True


@patch("server.subprocess.run")
def test_has_session_dead(mock_run):
    mock_run.return_value = _mock_run(returncode=1)
    result = server.has_session("ghost")
    assert result["alive"] is False


@patch("server.subprocess.run")
def test_capture_output(mock_run):
    mock_run.return_value = _mock_run(returncode=0, stdout="line1\nline2\nline3\n")
    result = server.capture_output("test-sess", lines=20)
    assert result["output"] == "line1\nline2\nline3\n"
    assert result["error"] is None
    args = mock_run.call_args[0][0]
    assert "-S" in args
    assert "-20" in args


@patch("server.subprocess.run")
def test_capture_output_failure(mock_run):
    mock_run.return_value = _mock_run(returncode=1, stderr="no session")
    result = server.capture_output("ghost")
    assert result["output"] is None
    assert "no session" in result["error"]


# --- show_session ---

@patch("server._yakuake_available", return_value=True)
@patch("server._qdbus")
def test_show_session_yakuake(mock_qdbus, mock_avail):
    mock_qdbus.side_effect = [
        _mock_run(stdout="30\n"),      # addSession
        _mock_run(stdout="45\n"),      # terminalIdsForSessionId
        _mock_run(),                    # setTabTitle
        _mock_run(),                    # runCommandInTerminal
        _mock_run(),                    # raiseSession
    ]
    result = server.show_session("my-session", "My Title")
    assert result["displayed"] is True
    assert result["backend"] == "yakuake"
    assert result["yakuake_session"] == "30"


@patch("server._yakuake_available", return_value=False)
def test_show_session_fallback(mock_avail):
    result = server.show_session("my-session")
    assert result["displayed"] is False
    assert "tmux attach" in result["error"]


# --- close_display ---

@patch("server._yakuake_available", return_value=True)
@patch("server._qdbus")
def test_close_display(mock_qdbus, mock_avail):
    mock_qdbus.return_value = _mock_run()
    result = server.close_display("30")
    assert result["closed"] is True


@patch("server._yakuake_available", return_value=False)
def test_close_display_no_yakuake(mock_avail):
    result = server.close_display("30")
    assert result["closed"] is False
