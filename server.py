"""MCP server for tmux-session — terminal session management via tmux."""

import shutil
import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tmux-session")


@mcp.tool()
def create_session(name: str, command: str) -> dict:
    """Create a detached tmux session running a command.

    Args:
        name: Session name (used to reference it later).
        command: Shell command to run inside the session.

    Returns:
        {"session": name, "created": bool, "error": str | None}
    """
    result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", name, command],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"session": name, "created": False, "error": result.stderr.strip()}
    return {"session": name, "created": True, "error": None}


@mcp.tool()
def send_keys(session: str, keys: str) -> dict:
    """Send keystrokes to a tmux session.

    Args:
        session: Session name.
        keys: Keys to send (e.g., "Enter", "q", "echo hello").

    Returns:
        {"session": session, "sent": bool, "error": str | None}
    """
    result = subprocess.run(
        ["tmux", "send-keys", "-t", session, keys],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"session": session, "sent": False, "error": result.stderr.strip()}
    return {"session": session, "sent": True, "error": None}


@mcp.tool()
def kill_session(session: str) -> dict:
    """Terminate a tmux session.

    Args:
        session: Session name.

    Returns:
        {"session": session, "killed": bool, "error": str | None}
    """
    result = subprocess.run(
        ["tmux", "kill-session", "-t", session],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"session": session, "killed": False, "error": result.stderr.strip()}
    return {"session": session, "killed": True, "error": None}


@mcp.tool()
def has_session(session: str) -> dict:
    """Check if a tmux session is alive.

    Args:
        session: Session name.

    Returns:
        {"session": session, "alive": bool}
    """
    result = subprocess.run(
        ["tmux", "has-session", "-t", session],
        capture_output=True,
    )
    return {"session": session, "alive": result.returncode == 0}


@mcp.tool()
def capture_output(session: str, lines: int = 50) -> dict:
    """Read recent output from a tmux session's pane.

    Args:
        session: Session name.
        lines: Number of lines to capture (default 50).

    Returns:
        {"session": session, "output": str | None, "error": str | None}
    """
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session, "-p", "-S", f"-{lines}"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        return {"session": session, "output": None, "error": result.stderr.strip()}
    return {"session": session, "output": result.stdout, "error": None}


def _qdbus(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["qdbus", "org.kde.yakuake", *args],
        capture_output=True, text=True, timeout=5,
    )


def _yakuake_available() -> bool:
    if not shutil.which("qdbus"):
        return False
    return _qdbus("/yakuake/sessions", "org.kde.yakuake.activeSessionId").returncode == 0


@mcp.tool()
def show_session(session: str, title: str = "") -> dict:
    """Show a tmux session in a visible terminal tab.

    Opens the session in Yakuake if available, otherwise returns
    the manual attach command.

    Args:
        session: tmux session name to display.
        title: Tab title (defaults to session name).

    Returns:
        {"session": str, "displayed": bool, "backend": str | None, "error": str | None}
    """
    if not title:
        title = session

    if _yakuake_available():
        result = _qdbus("/yakuake/sessions", "org.kde.yakuake.addSession")
        if result.returncode != 0:
            return {"session": session, "displayed": False, "backend": "yakuake", "error": result.stderr.strip()}

        yak_session = result.stdout.strip()
        term_result = _qdbus("/yakuake/sessions", "org.kde.yakuake.terminalIdsForSessionId", yak_session)
        term_id = term_result.stdout.strip().split(",")[0]

        _qdbus("/yakuake/tabs", "org.kde.yakuake.setTabTitle", yak_session, title)
        _qdbus("/yakuake/sessions", "org.kde.yakuake.runCommandInTerminal", term_id, f"tmux attach -t {session}")
        _qdbus("/yakuake/sessions", "org.kde.yakuake.raiseSession", yak_session)

        return {"session": session, "displayed": True, "backend": "yakuake", "yakuake_session": yak_session, "error": None}

    return {"session": session, "displayed": False, "backend": None, "error": f"No display backend available. Attach manually: tmux attach -t {session}"}


@mcp.tool()
def close_display(yakuake_session: str) -> dict:
    """Close a previously opened display tab.

    Args:
        yakuake_session: The Yakuake session ID returned by show_session.

    Returns:
        {"closed": bool, "error": str | None}
    """
    if not _yakuake_available():
        return {"closed": False, "error": "Yakuake not available"}

    result = _qdbus("/yakuake/sessions", "org.kde.yakuake.removeSession", yakuake_session)
    if result.returncode != 0:
        return {"closed": False, "error": result.stderr.strip()}
    return {"closed": True, "error": None}


if __name__ == "__main__":
    mcp.run()
