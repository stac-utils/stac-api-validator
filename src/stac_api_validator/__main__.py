"""Command-line interface."""
import logging
import sys
import traceback
from typing import List
from typing import Optional

import click

from stac_api_validator.validations import QueryConfig
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
            "item-search#sort",
            "item-search#fields",
            "item-search#query",
            "features#sort",
            "features#fields",
            "features#query",
            "transaction",
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
    help="Query parameter key and value to pass for authorization, e.g., 'key=xyz'.",
)
@click.option(
    "--fields-nested-property",
    help="Fields Extension: name of a field in Item Properties, e.g. 'properties.eo:cloud_cover'",
)
@click.option(
    "--validate-pagination/--no-validate-pagination",
    default=False,
    help="Validate pagination behavior (can take a long time to run)",
)
@click.option(
    "--query-comparison-field",
    help="Query Extension: name of field to use for comparison operators tests (eq, neq, lt, lte, gt, gte)",
)
@click.option(
    "--query-eq-value",
    help="Query Extension: value of field to use for eq",
)
@click.option(
    "--query-neq-value",
    help="Query Extension: value of field to use for neq",
)
@click.option(
    "--query-lt-value",
    help="Query Extension: value of field to use for lt",
)
@click.option(
    "--query-lte-value",
    help="Query Extension: value of field to use for lte",
)
@click.option(
    "--query-gt-value",
    help="Query Extension: value of field to use for gt",
)
@click.option(
    "--query-gte-value",
    help="Query Extension: value of field to use for gte",
)
@click.option(
    "--query-substring-field",
    help="Query Extension: name of field to use for substring operators tests (startsWith, endsWith, contains)",
)
@click.option(
    "--query-starts-with-value",
    help="Query Extension: value of field to use for startsWith",
)
@click.option(
    "--query-ends-with-value",
    help="Query Extension: value of field to use for endsWith",
)
@click.option(
    "--query-contains-value",
    help="Query Extension: value of field to use for contains",
)
@click.option(
    "--query-in-field",
    help="Query Extension: name of field to use for 'in' operator tests",
)
@click.option(
    "--query-in-values",
    help="Query Extension: comma-separated values of field to use for 'in' operator tests",
)
@click.option(
    "--transaction-collection",
    help="The name of the collection to use for Transaction Extension tests.",
)
def main(
    log_level: str,
    root_url: str,
    conformance_classes: List[str],
    collection: Optional[str],
    geometry: Optional[str],
    auth_bearer_token: Optional[str] = None,
    auth_query_parameter: Optional[str] = None,
    fields_nested_property: Optional[str] = None,
    validate_pagination: bool = False,
    query_comparison_field: Optional[str] = None,
    query_eq_value: Optional[str] = None,
    query_neq_value: Optional[str] = None,
    query_lt_value: Optional[str] = None,
    query_lte_value: Optional[str] = None,
    query_gt_value: Optional[str] = None,
    query_gte_value: Optional[str] = None,
    query_substring_field: Optional[str] = None,
    query_starts_with_value: Optional[str] = None,
    query_ends_with_value: Optional[str] = None,
    query_contains_value: Optional[str] = None,
    query_in_field: Optional[str] = None,
    query_in_values: Optional[str] = None,
    transaction_collection: Optional[str] = None,
) -> int:
    """STAC API Validator."""
    logging.basicConfig(stream=sys.stdout, level=log_level)

    try:
        (warnings, errors) = validate_api(
            root_url=root_url,
            ccs_to_validate=conformance_classes,
            collection=collection,
            geometry=geometry,
            auth_bearer_token=auth_bearer_token,
            auth_query_parameter=auth_query_parameter,
            fields_nested_property=fields_nested_property,
            validate_pagination=validate_pagination,
            query_config=QueryConfig(
                query_comparison_field,
                query_eq_value,
                query_neq_value,
                query_lt_value,
                query_lte_value,
                query_gt_value,
                query_gte_value,
                query_substring_field,
                query_starts_with_value,
                query_ends_with_value,
                query_contains_value,
                query_in_field,
                query_in_values,
            ),
            transaction_collection=transaction_collection,
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
