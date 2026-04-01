"""Tests for plugin.json manifest validity."""

import re


def test_required_fields(manifest):
    for field in ("name", "description", "version", "mcpServers"):
        assert field in manifest, f"Missing required field: {field}"


def test_name(manifest):
    assert manifest["name"] == "tmux-session"


def test_semver(manifest):
    assert re.match(r"^\d+\.\d+\.\d+$", manifest["version"])


def test_mcp_server_config(manifest):
    servers = manifest["mcpServers"]
    assert "tmux-session" in servers
    server = servers["tmux-session"]
    assert server["command"] == "python"
    assert any("server.py" in arg for arg in server["args"])
