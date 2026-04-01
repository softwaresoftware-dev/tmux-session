"""Shared fixtures for tmux-session tests."""

import json

import pytest


@pytest.fixture
def manifest():
    """Load and return the plugin manifest."""
    with open(".claude-plugin/plugin.json") as f:
        return json.load(f)
