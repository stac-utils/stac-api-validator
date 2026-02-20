"""
Test cases for the 'validations' module
"""

import json
import os
import pathlib
import unittest.mock
from copy import copy
from typing import Dict
from typing import Generator

import pystac
import pytest
import requests
import sys

from stac_api_validator import validations


@pytest.fixture
def r_session() -> Generator[requests.Session, None, None]:
    yield requests.Session()


@pytest.fixture
def catalog_dict() -> Generator[Dict[str, str], None, None]:
    current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

    with open(current_path / "resources" / "landing_page.json") as f:
        # Load the contents of the file into a Python dictionary
        data = json.load(f)

    yield data


@pytest.fixture
def sample_item() -> Generator[pystac.Item, None, None]:
    current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

    with open(current_path / "resources" / "sample-item.json") as f:
        # Load the contents of the file into a Python dictionary
        data = json.load(f)

    yield pystac.Item.from_dict(data)


@pytest.fixture
def stac_check_config() -> Generator[str, None, None]:
    current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

    yield current_path / "resources" / "stac-check-config.yaml"


@pytest.fixture
def expected_headers(requests_version: str) -> Generator[Dict[str, str], None, None]:
    yield {
        "User-Agent": f"python-requests/{requests_version}",
        "Accept-Encoding": "gzip, deflate, zstd"
        if sys.version_info >= (3, 14)
        else "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Authorization": "api-key fake-api-key-value",
    }


def test_get_catalog(
    r_session: requests.Session,
    catalog_dict: Dict[str, str],
    expected_headers: Dict[str, str],
) -> None:
    r_session.headers = copy(expected_headers)  # type: ignore
    expected_headers.update({"Accept-Encoding": "*"})

    catalog = validations.get_catalog(catalog_dict, r_session)
    assert catalog._stac_io.headers == expected_headers  # type: ignore


def test_retrieve(
    r_session: requests.Session, expected_headers: Dict[str, str]
) -> None:
    headers = {"Authorization": "api-key fake-api-key-value"}
    r_session.send = unittest.mock.MagicMock()  # type: ignore
    r_session.send.status_code = 500

    validations.retrieve(
        validations.Method.GET,
        "https://invalid",
        validations.Errors(),
        validations.Context.CORE,
        r_session=r_session,
        headers=headers,
    )
    assert r_session.send.call_count == 1
    prepared_request_headers = r_session.send.call_args_list[0].args[0].headers
    assert prepared_request_headers == expected_headers


def test_validate_api(
    request: pytest.FixtureRequest,
    r_session: requests.Session,
    expected_headers: Dict[str, str],
    stac_check_config: str,
) -> None:
    if request.config.getoption("typeguard_packages"):
        pytest.skip(
            "The import hook that typeguard uses seems to break the mock below."
        )
    headers = {"Authorization": "api-key fake-api-key-value"}

    with unittest.mock.patch(
        "stac_api_validator.validations.retrieve"
    ) as retrieve_mock:
        retrieve_mock.return_value = None, None, None
        validations.validate_api(
            "https://invalid",
            ccs_to_validate=["core"],
            collection=None,
            geometry=None,
            auth_bearer_token=None,
            auth_query_parameter=None,
            fields_nested_property=None,
            validate_pagination=None,
            query_config=None,
            transaction_collection=None,
            headers=headers,
            stac_check_config=stac_check_config,
        )
        assert retrieve_mock.call_count == 1
        r_session = retrieve_mock.call_args.args[-1]
        assert r_session.headers == expected_headers


def test_validate_browseable(
    request: pytest.FixtureRequest,
    r_session: requests.Session,
    catalog_dict: Dict[str, str],
    sample_item: pystac.Item,
    expected_headers: Dict[str, str],
) -> None:
    if request.config.getoption("typeguard_packages"):
        pytest.skip(
            "The import hook that typeguard uses seems to break the mock below."
        )

    r_session.headers = copy(expected_headers)  # type: ignore

    with unittest.mock.patch(
        "stac_api_validator.validations.get_catalog"
    ) as get_catalog_mock:
        get_catalog_mock.get_all_items.return_value = [sample_item]

        validations.validate_browseable(
            catalog_dict,
            errors=validations.Errors(),
            warnings=validations.Warnings(),
            r_session=r_session,
        )
        assert get_catalog_mock.call_count == 1
        session_from_mock = get_catalog_mock.call_args.args[-1]
        assert session_from_mock.headers == expected_headers
