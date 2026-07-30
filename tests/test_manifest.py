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
    assert server["command"] == "uv"
    assert any("server.py" in arg for arg in server["args"])


# --- userConfig schema validation (added to prevent regressions like the
# `enum` field in claude-browser-bridge 3.3.0 that broke install). Schema:
# https://code.claude.com/docs/en/plugins-reference.md#user-configuration ---

import json as _json
import os as _os

USER_CONFIG_COMMON_KEYS = {"type", "title", "description", "default", "required", "sensitive"}
USER_CONFIG_TYPE_KEYS = {
    "string": USER_CONFIG_COMMON_KEYS | {"multiple"},
    "number": USER_CONFIG_COMMON_KEYS | {"min", "max"},
    "boolean": USER_CONFIG_COMMON_KEYS,
    "directory": USER_CONFIG_COMMON_KEYS,
    "file": USER_CONFIG_COMMON_KEYS,
}


def _load_manifest_for_uc():
    root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    with open(_os.path.join(root, ".claude-plugin", "plugin.json")) as f:
        return _json.load(f)


def test_user_config_types():
    """Every userConfig entry must declare a recognized type."""
    plugin_json = _load_manifest_for_uc()
    for name, entry in plugin_json.get("userConfig", {}).items():
        assert "type" in entry, f"userConfig.{name} missing 'type'"
        assert entry["type"] in USER_CONFIG_TYPE_KEYS, (
            f"userConfig.{name}.type={entry['type']!r} is not a recognized "
            f"type. Valid: {sorted(USER_CONFIG_TYPE_KEYS)}"
        )


def test_user_config_schema_strict():
    """userConfig entries must only use keys from the official schema.

    Catches regressions like an `enum` field — the Claude Code manifest schema
    does not support `enum`, `pattern`, or arbitrary JSON Schema keywords.
    """
    plugin_json = _load_manifest_for_uc()
    for name, entry in plugin_json.get("userConfig", {}).items():
        allowed = USER_CONFIG_TYPE_KEYS.get(entry.get("type"), USER_CONFIG_COMMON_KEYS)
        unknown = set(entry.keys()) - allowed
        assert not unknown, (
            f"userConfig.{name} contains unknown keys: {sorted(unknown)}. "
            f"Allowed for type={entry.get('type')!r}: {sorted(allowed)}. "
            f"See https://code.claude.com/docs/en/plugins-reference.md#user-configuration"
        )
