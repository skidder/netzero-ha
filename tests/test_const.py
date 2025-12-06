"""Tests for const definitions."""

from __future__ import annotations

from custom_components.netzero.const import SENSOR_DESCRIPTIONS


def test_sensor_keys_unique():
    keys = [desc.key for desc in SENSOR_DESCRIPTIONS]
    assert len(keys) == len(set(keys))

