"""MCP server for tmux-session — terminal session management via tmux."""

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
        ["tmux", "new-session", "-d", "-s", name, f"bash -lc '{command}'"],
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


if __name__ == "__main__":
    mcp.run()
