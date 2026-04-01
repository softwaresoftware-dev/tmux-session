# CLAUDE.md — tmux-session

Terminal session management provider via tmux. Provides the `terminal-ops` capability.

## Quick Reference

| Tool | What it does |
|------|-------------|
| `create_session(name, command)` | Create a detached tmux session |
| `send_keys(session, keys)` | Send keystrokes to a session |
| `kill_session(session)` | Terminate a session |
| `has_session(session)` | Check if a session is alive |
| `capture_output(session, lines)` | Read recent pane output |

## Stack

- Python 3.11+, FastMCP, subprocess (tmux CLI)

## Development

```bash
pip install "mcp[cli]"
python server.py          # run MCP server
make test                 # run tests
```
