import copy
from typing import Any
from typing import Dict

import pytest

from stac_api_validator.validations import Errors
from stac_api_validator.validations import Warnings
from stac_api_validator.validations import validate_core_landing_page_body


def test_landing_page_1() -> None:
    errors = Errors()
    warnings = Warnings()
    validate_core_landing_page_body(
        body={},
        headers={},
        errors=errors,
        warnings=warnings,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "CORE-1" in errors
    assert "CORE-2" in errors
    assert "CORE-3" in errors
    assert "CORE-4" in errors

    errors = Errors()
    validate_core_landing_page_body(
        body={},
        headers={"content-type": "text/html"},
        errors=errors,
        warnings=warnings,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "CORE-1" in errors

    errors = Errors()
    validate_core_landing_page_body(
        body={},
        headers={"content-type": "application/json"},
        errors=errors,
        warnings=warnings,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "CORE-1" not in errors

    errors = Errors()
    validate_core_landing_page_body(
        body={},
        headers={"content-type": "application/json; charset=utf-8"},
        errors=errors,
        warnings=warnings,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "CORE-1" not in errors

    errors = Errors()
    validate_core_landing_page_body(
        body={
            "conformsTo": ["https://api.stacspec.org/v1.0.0-rc.2/core"],
            "links": [{"href": ""}],
        },
        headers={"content-type": "application/json"},
        errors=errors,
        warnings=warnings,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "CORE-1" not in errors
    assert "CORE-2" not in errors
    assert "CORE-3" not in errors
    assert "CORE-4" not in errors

    errors = Errors()
    body: Dict[str, Any] = {
        "conformsTo": [
            "https://api.stacspec.org/v1.0.0-rc.2/core"
            "https://api.stacspec.org/v1.0.0-rc.2/ogcapi-features"
            "https://api.stacspec.org/v1.0.0-rc.2/collections"
        ],
        "links": [{"href": ""}],
    }
    # collection not defined
    assert not validate_core_landing_page_body(
        body=body,
        headers={"content-type": "application/json"},
        errors=errors,
        warnings=warnings,
        conformance_classes=["collections"],
        collection=None,
        geometry=None,
    )

    # collection not defined
    assert not validate_core_landing_page_body(
        body=body,
        headers={"content-type": "application/json"},
        errors=errors,
        warnings=warnings,
        conformance_classes=["features"],
        collection=None,
        geometry=None,
    )

    errors = Errors()
    body = {
        "conformsTo": ["https://api.stacspec.org/v1.0.0-rc.2/core"],
        "links": [{"href": ""}],
    }
    validate_core_landing_page_body(
        body=body,
        headers={"content-type": "application/json"},
        errors=errors,
        warnings=warnings,
        conformance_classes=["browseable", "children", "collections", "features"],
        collection="foobar",
        geometry=None,
    )
    assert "CORE-5" in errors
    assert "CORE-6" in errors
    assert "CORE-7" in errors
    assert "CORE-8" in errors

    errors = Errors()
    body["conformsTo"].extend(
        [
            "https://api.stacspec.org/v1.0.0-rc.2/browseable",
            "https://api.stacspec.org/v1.0.0-rc.2/children",
            "https://api.stacspec.org/v1.0.0-rc.2/collections",
            "https://api.stacspec.org/v1.0.0-rc.2/ogcapi-features",
        ]
    )
    validate_core_landing_page_body(
        body=body,
        headers={"content-type": "application/json"},
        errors=errors,
        warnings=warnings,
        conformance_classes=["browseable"],
        collection=None,
        geometry=None,
    )
    assert "CORE-5" not in errors
    assert "CORE-6" not in errors
    assert "CORE-7" not in errors
    assert "CORE-8" not in errors

    # todo: item-search


@pytest.fixture
def perfect_core_landing_page() -> Dict[str, Any]:
    return copy.deepcopy(
        {
            "conformsTo": [
                "https://api.stacspec.org/v1.0.0/core",
                "https://api.stacspec.org/v1.0.0/collections",
                "https://api.stacspec.org/v1.0.0/ogcapi-features",
            ],
            "links": [
                {"rel": "data", "href": "http://stac-api-validator.test/collections"}
            ],
        }
    )


def test_perfect_core_landing_page(perfect_core_landing_page: Dict[str, Any]) -> None:
    errors = Errors()
    warnings = Warnings()
    validate_core_landing_page_body(
        body=perfect_core_landing_page,
        headers={"content-type": "application/json"},
        errors=errors,
        warnings=warnings,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert not errors
    assert not warnings


def test_perfect_core_landing_page_with_extension(
    perfect_core_landing_page: Dict[str, Any],
) -> None:
    errors = Errors()
    warnings = Warnings()
    perfect_core_landing_page["conformsTo"].append(
        "https://api.stacspec.org/v1.0.0-rc.3/ogcapi-features#fields",
    )
    validate_core_landing_page_body(
        body=perfect_core_landing_page,
        headers={"content-type": "application/json"},
        errors=errors,
        warnings=warnings,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert not errors
    assert not warnings
