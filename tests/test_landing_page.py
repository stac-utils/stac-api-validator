from stac_api_validator.validations import Errors
from stac_api_validator.validations import validate_core_landing_page_body


def test_landing_page_1() -> None:
    errors = Errors()
    validate_core_landing_page_body(
        body={},
        headers={},
        errors=errors,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "LP-1" in errors

    errors = Errors()
    validate_core_landing_page_body(
        body={},
        headers={"content-type": "text/html"},
        errors=errors,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "LP-1" in errors

    errors = Errors()
    validate_core_landing_page_body(
        body={},
        headers={"content-type": "application/json"},
        errors=errors,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "LP-1" not in errors

    errors = Errors()
    validate_core_landing_page_body(
        body={},
        headers={"content-type": "application/json; charset=utf-8"},
        errors=errors,
        conformance_classes=[],
        collection=None,
        geometry=None,
    )
    assert "LP-1" not in errors

    # body: Dict[str, Any] = {
    #     "conformsTo": [],
    # }
    #
    # print(errors)
