"""Test cases for the __main__ module."""

import unittest.mock

import pytest
import sys
from click.testing import CliRunner

from stac_api_validator import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_fails(runner: CliRunner) -> None:
    result = runner.invoke(__main__.main)
    assert result.exit_code == 2


def test_retrieve_called_with_auth_headers(
    request: pytest.FixtureRequest, runner: CliRunner, requests_version: str
) -> None:
    if request.config.getoption("typeguard_packages"):
        pytest.skip(
            "The import hook that typeguard uses seems to break the mock below."
        )

    expected_headers = {
        "User-Agent": f"python-requests/{requests_version}",
        "Accept-Encoding": "gzip, deflate, zstd"
        if sys.version_info >= (3, 14)
        else "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Authorization": "api-key fake-api-key-value",
    }

    with unittest.mock.patch(
        "stac_api_validator.validations.retrieve"
    ) as retrieve_mock:
        runner.invoke(
            __main__.main,
            args=[
                "--root-url",
                "https://invalid",
                "--conformance",
                "core",
                "-H",
                "Authorization: api-key fake-api-key-value",
            ],
        )
        assert retrieve_mock.call_count == 1
        r_session = retrieve_mock.call_args.args[-1]
        assert r_session.headers == expected_headers
