"""Shared pytest fixtures."""
from pathlib import Path
import pytest


@pytest.fixture(scope="session", autouse=True)
def create_output_dirs():
    Path("output/trees").mkdir(parents=True, exist_ok=True)
