"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner

from stac_api_validator import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_fails(runner: CliRunner) -> None:
    result = runner.invoke(__main__.main)
    assert result.exit_code == 2
