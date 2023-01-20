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
@click.option(
    "--auth-bearer-token",
    help="Authorization Bearer token value to append to all requests.",
)
@click.option(
    "--auth-query-parameter",
    help="Query pararmeter key and value to pass for authorization, e.g., 'key=xyz'.",
)
def main(
    log_level: str,
    root_url: str,
    conformance_classes: List[str],
    collection: Optional[str],
    geometry: Optional[str],
    auth_bearer_token: Optional[str] = None,
    auth_query_parameter: Optional[str] = None,
) -> int:
    """STAC API Validator."""
    logging.basicConfig(stream=sys.stdout, level=log_level)

    try:
        (warnings, errors) = validate_api(
            root_url=root_url,
            conformance_classes=conformance_classes,
            collection=collection,
            geometry=geometry,
            auth_bearer_token=auth_bearer_token,
            auth_query_parameter=auth_query_parameter,
        )
    except Exception as e:
        click.secho(
            f"Failed.\nError {root_url}: {type(e)} {str(e)} {traceback.format_exc()}",
            fg="red",
        )
        return 1

    if warnings:
        click.secho("Warnings:", fg="blue")
    else:
        click.secho("Warnings: none", fg="green")
    for warning in warnings:
        click.secho(f"- {warning}")

    if errors:
        click.secho("Errors:", fg="red")
        for error in errors:
            click.secho(f"- {error}")
    else:
        click.secho("Errors: none", fg="green")

    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main(prog_name="stac-api-validator")  # pragma: no cover
