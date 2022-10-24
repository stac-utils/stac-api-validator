"""Command-line interface."""
import logging
import sys
import traceback
from typing import List
from typing import Optional

import click

from stac_api_validator.validations import validate_api


@click.command()
@click.version_option()
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level, one of DEBUG, INFO, WARN, ERROR, CRITICAL",
)
@click.option(
    "--root-url",
    required=True,
    help="STAC API Root / Landing Page URL",
)
@click.option(
    "--collection",
    help="The name of the collection to use for item-search, collections, and features tests.",
)
@click.option(
    "--geometry",
    help="The GeoJSON geometry to use for intersection tests.",
)
@click.option(
    "--conformance",
    "conformance_classes",
    required=True,
    multiple=True,
    type=click.Choice(
        [
            "core",
            "browseable",
            "item-search",
            "features",
            "collections",
            "children",
            "filter",
        ],
        case_sensitive=False,
    ),
    help="The conformance classes to validate.",
)
def main(
    log_level: str,
    root_url: str,
    conformance_classes: List[str],
    collection: Optional[str],
    geometry: Optional[str],
) -> int:
    """STAC API Validator."""

    logging.basicConfig(stream=sys.stdout, level=log_level)

    try:
        (warnings, errors) = validate_api(
            root_url=root_url,
            conformance_classes=conformance_classes,
            collection=collection,
            geometry=geometry,
        )
    except Exception as e:
        print(f"Failed.\nError {root_url}: {type(e)} {str(e)}")
        traceback.print_exc()
        return 1

    if warnings:
        print("warnings:")
    else:
        print("warnings: none")
    for warning in warnings:
        print(f"- {warning}")

    if errors:
        print("errors:")
    else:
        print("errors: none")
    for error in errors:
        print(f"- {error}")

    if errors:
        return 1
    else:
        return 0


if __name__ == "__main__":
    main(prog_name="stac-api-validator")  # pragma: no cover
