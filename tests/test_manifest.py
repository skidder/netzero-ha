"""Basic manifest sanity checks."""

from __future__ import annotations

import json
from pathlib import Path


def test_manifest_domain():
    manifest_path = Path("custom_components/netzero/manifest.json")
    manifest = json.loads(manifest_path.read_text())
    assert manifest["domain"] == "netzero"
    assert manifest.get("config_flow") is True

