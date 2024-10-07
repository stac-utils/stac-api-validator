import importlib.metadata

import pytest


@pytest.fixture
def requests_version() -> str:
    return importlib.metadata.version("requests")
