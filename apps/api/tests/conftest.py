"""Test configuration for the AutoHire API package."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from app.services.opencats_sync import reset_sync_state


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(autouse=True)
def cleanup_sync_state() -> None:
    """Reset in-memory sync state around each test."""

    reset_sync_state()
    yield
    reset_sync_state()

