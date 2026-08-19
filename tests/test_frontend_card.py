"""Tests for the bundled Tessie Drive Stats Lovelace card."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
INTEGRATION = ROOT / "custom_components" / "tessie_drive_stats"
CARD = INTEGRATION / "www" / "tessie-drive-stats-card.js"


def test_manifest_and_frontend_versions_match():
    manifest = json.loads((INTEGRATION / "manifest.json").read_text())
    const = (INTEGRATION / "const.py").read_text()
    match = re.search(r'FRONTEND_VERSION: Final = "([^"]+)"', const)
    assert match
    assert manifest["version"] == match.group(1)
    assert "frontend" in manifest["dependencies"]


def test_bundled_card_registers_all_views():
    text = CARD.read_text()
    for view in (
        "overview",
        "drive",
        "efficiency",
        "charging",
        "charging_economics",
        "battery",
        "lifetime",
        "idle",
    ):
        assert f'["{view}",' in text
    assert "customElements.define(CARD_TAG, TessieDriveStatsCard)" in text
    assert "window.customCards.push({" in text
    assert "static getConfigForm()" in text


def test_bundled_card_is_theme_aware():
    text = CARD.read_text()
    assert "var(--primary-text-color)" in text
    assert "var(--secondary-text-color)" in text
    assert "var(--primary-color)" in text
    assert "var(--divider-color)" in text
    assert "var(--secondary-background-color)" in text
    assert not re.search(r"(?<!&)#[0-9A-Fa-f]{3,8}\b", text)
    assert not re.search(r"\brgba?\(", text)


def test_bundled_card_has_no_external_runtime_dependencies():
    text = CARD.read_text()
    assert "https://unpkg.com" not in text
    assert "https://cdn." not in text
    assert not re.search(r"\bimport\s+['\"]https?://", text)
