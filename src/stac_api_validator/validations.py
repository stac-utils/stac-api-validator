"""Validations module."""
import copy
import itertools
import json
import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional
from typing import Pattern
from typing import Set
from typing import Tuple
from typing import Union

import pystac
import yaml
from deepdiff import DeepDiff
from more_itertools import take
from pystac import Catalog
from pystac import Collection
from pystac import Item
from pystac import ItemCollection
from pystac import STACValidationError
from pystac_client import Client
from requests import Request
from requests import Session
from shapely.geometry import shape
from stac_check.lint import Linter
from stac_validator.stac_validator import StacValidate

from stac_api_validator.geometries import geometry_collection
from stac_api_validator.geometries import linestring
from stac_api_validator.geometries import multilinestring
from stac_api_validator.geometries import multipoint
from stac_api_validator.geometries import multipolygon
from stac_api_validator.geometries import point
from stac_api_validator.geometries import polygon
from stac_api_validator.geometries import polygon_with_hole

from .filters import cql2_json_and
from .filters import cql2_json_between
from .filters import cql2_json_common_1
from .filters import cql2_json_ex_2
from .filters import cql2_json_ex_3
from .filters import cql2_json_ex_4
from .filters import cql2_json_ex_6
from .filters import cql2_json_ex_8
from .filters import cql2_json_ex_9
from .filters import cql2_json_like
from .filters import cql2_json_not
from .filters import cql2_json_not_between
from .filters import cql2_json_not_like
from .filters import cql2_json_numeric_comparisons
from .filters import cql2_json_or
from .filters import cql2_json_s_intersects
from .filters import cql2_json_string_comparisons
from .filters import cql2_json_timestamp_comparisons
from .filters import cql2_text_and
from .filters import cql2_text_between
from .filters import cql2_text_ex_2
from .filters import cql2_text_ex_3
from .filters import cql2_text_ex_4
from .filters import cql2_text_ex_6
from .filters import cql2_text_ex_8
from .filters import cql2_text_ex_9
from .filters import cql2_text_like
from .filters import cql2_text_not
from .filters import cql2_text_not_between
from .filters import cql2_text_not_like
from .filters import cql2_text_numeric_comparisons
from .filters import cql2_text_or
from .filters import cql2_text_s_intersects
from .filters import cql2_text_string_comparisons
from .filters import cql2_text_timestamp_comparisons


logger = logging.getLogger(__name__)

LATEST_STAC_API_FOUNDATION_VERSION = "https://api.stacspec.org/v1.0.0/"


class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

    def __str__(self) -> str:
        return self.value


class Context(Enum):
    CORE = "Core"
    ITEM_SEARCH = "Item Search"
    FEATURES = "Features"
    COLLECTIONS = "Collections"
    CHILDREN = "Children Ext"
    BROWSEABLE = "Browseable Ext"
    ITEM_SEARCH_FILTER = "Item Search - Filter Ext"
    ITEM_SEARCH_SORT = "Item Search - Sort Ext"
    ITEM_SEARCH_FIELDS = "Item Search - Fields Ext"
    ITEM_SEARCH_QUERY = "Item Search - Query Ext"
    FEATURES_FILTER = "Features - Filter Ext"
    FEATURES_SORT = "Features - Sort Ext"
    FEATURES_FIELDS = "Features - Fields Ext"
    FEATURES_QUERY = "Features - Query Ext"
    FEATURES_TXN = "Features - Transaction Ext"

    def __str__(self) -> str:
        return self.value


class BaseErrors:
    def __init__(self) -> None:
        self.errors: List[Tuple[str, str]] = []

    def __contains__(self, item: str) -> bool:
        return item in (e[0] for e in self.errors)

    def __bool__(self) -> bool:
        return bool(self.errors)

    def __str__(self) -> str:
        return str(self.errors)

    def __repr__(self) -> str:
        return str(self.errors)

    def __iter__(self) -> Iterator[str]:
        return iter(self.as_list())

    def as_list(self) -> List[str]:
        return [e[1] for e in self.errors]


class Errors(BaseErrors):
    def __iadd__(self, x: Union[Tuple[str, str], str]) -> "Errors":
        if isinstance(x, str):
            self.errors.append(("none", x))
        elif isinstance(x, tuple):
            self.errors.append(x)
        return self


class Warnings(BaseErrors):
    def __iadd__(self, x: Union[Tuple[str, str], str]) -> "Warnings":
        if isinstance(x, str):
            self.errors.append(("none", x))
        elif isinstance(x, tuple):
            self.errors.append(x)
        return self


@dataclass
class QueryConfig:
    query_comparison_field: Optional[str]
    query_eq_value: Optional[str]
    query_neq_value: Optional[str]
    query_lt_value: Optional[str]
    query_lte_value: Optional[str]
    query_gt_value: Optional[str]
    query_gte_value: Optional[str]
    query_substring_field: Optional[str]
    query_starts_with_value: Optional[str]
    query_ends_with_value: Optional[str]
    query_contains_value: Optional[str]
    query_in_field: Optional[str]
    query_in_values: Optional[str]


cc_core_regex = re.compile(r"https://api\.stacspec\.org/(.+)/core")
cc_browseable_regex = re.compile(r"https://api\.stacspec\.org/(.+)/browseable")
cc_children_regex = re.compile(r"https://api\.stacspec\.org/(.+)/children")
cc_collections_regex = re.compile(r"https://api\.stacspec\.org/(.+)/collections")
cc_features_regex = re.compile(r"https://api\.stacspec\.org/(.+)/ogcapi-features")
cc_features_transaction_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/ogcapi-features/extensions/transaction"
)
cc_features_fields_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/ogcapi-features#fields"
)
cc_features_sort_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/ogcapi-features#sort"
)
cc_features_query_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/ogcapi-features#query"
)
cc_features_filter_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/ogcapi-features#filter"
)

cc_item_search_regex = re.compile(r"https://api\.stacspec\.org/(.+)/item-search")
cc_item_search_fields_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/item-search#fields"
)
cc_item_search_sort_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/item-search#sort"
)
cc_item_search_query_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/item-search#query"
)
cc_item_search_filter_regex = re.compile(
    r"https://api\.stacspec\.org/(.+)/item-search#filter"
)

geojson_mt = "application/geo+json"
geojson_charset_mt = "application/geo+json; charset=utf-8"

valid_datetimes = [
    "1985-04-12T23:20:50.52Z",
    "1996-12-19T16:39:57-00:00",
    "1996-12-19T16:39:57+00:00",
    "1996-12-19T16:39:57-08:00",
    "1996-12-19T16:39:57+08:00",
    "../1985-04-12T23:20:50.52Z",
    "1985-04-12T23:20:50.52Z/..",
    "/1985-04-12T23:20:50.52Z",
    "1985-04-12T23:20:50.52Z/",
    "1985-04-12T23:20:50.52Z/1986-04-12T23:20:50.52Z",
    "1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52+01:00",
    "1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52-01:00",
    "1937-01-01T12:00:27.87+01:00",
    "1985-04-12T23:20:50.52Z",
    "1937-01-01T12:00:27.8710+01:00",
    "1937-01-01T12:00:27.8+01:00",
    "1937-01-01T12:00:27.8Z",
    "2020-07-23T00:00:00.000+03:00",
    "2020-07-23T00:00:00+03:00",
    "1985-04-12t23:20:50.000z",
    "2020-07-23T00:00:00Z",
    "2020-07-23T00:00:00.0Z",
    "2020-07-23T00:00:00.01Z",
    "2020-07-23T00:00:00.012Z",
    "2020-07-23T00:00:00.0123Z",
    "2020-07-23T00:00:00.01234Z",
    "2020-07-23T00:00:00.012345Z",
    "2020-07-23T00:00:00.0123456Z",
    "2020-07-23T00:00:00.01234567Z",
    "2020-07-23T00:00:00.012345678Z",
]

invalid_datetimes = [
    "/",
    "../..",
    "/..",
    "../",
    "/1984-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z",
    "1984-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z/",
    "/1984-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z/",
    "1985-04-12",  # date only
    "1937-01-01T12:00:27.87+0100",  # invalid TZ format, no sep :
    "37-01-01T12:00:27.87Z",  # invalid year, must be 4 digits
    "1985-12-12T23:20:50.52",  # no TZ
    "21985-12-12T23:20:50.52Z",  # year must be 4 digits
    "1985-13-12T23:20:50.52Z",  # month > 12
    "1985-12-32T23:20:50.52Z",  # day > 31
    "1985-12-01T25:20:50.52Z",  # hour > 24
    "1985-12-01T00:60:50.52Z",  # minute > 59
    "1985-12-01T00:06:61.52Z",  # second > 60
    "1985-04-12T23:20:50.Z",  # fractional sec . but no frac secs
    "1985-04-12T23:20:50,Z",  # fractional sec , but no frac secs
    "1990-12-31T23:59:61Z",  # second > 60 w/o fractional seconds
    "1986-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z",
    "1985-04-12T23:20:50,52Z",  # comma as frac sec sep allowed in ISO8601 but not RFC3339
]


def supports_collections(conforms_to: List[str]) -> bool:
    return supports(conforms_to, cc_collections_regex)


def supports_features(conforms_to: List[str]) -> bool:
    return supports(conforms_to, cc_features_regex)


def supports(conforms_to: List[str], pattern: Pattern[str]) -> bool:
    return any(pattern.fullmatch(x) for x in conforms_to)


def is_json_type(maybe_type: Optional[str]) -> bool:
    return maybe_type is not None and (
        maybe_type == "application/json" or maybe_type.startswith("application/json;")
    )


def is_geojson_type(maybe_type: Optional[str]) -> bool:
    return maybe_type is not None and (
        maybe_type == "application/geo+json"
        or maybe_type.startswith("application/geo+json;")
    )


# def is_json_or_geojson_type(maybe_type: Optional[str]) -> bool:
#     return maybe_type and (is_json_type(maybe_type) or is_geojson_type(maybe_type))


def has_content_type(headers: Mapping[str, str], content_type: str) -> bool:
    return headers.get("content-type", "").split(";")[0] == content_type


def has_json_content_type(headers: Mapping[str, str]) -> bool:
    return is_json_type(headers.get("content-type"))


def has_geojson_content_type(headers: Mapping[str, str]) -> bool:
    return is_geojson_type(headers.get("content-type"))


def stac_validate(
    url: str,
    body: Optional[Dict[str, Any]],
    errors: Errors,
    context: Context,
    method: Method = Method.GET,
) -> None:
    if not body:
        errors += f"[{context}] : {method} {url} body was empty when running stac-validate and stac-check"
    else:
        if _type := body.get("type"):
            try:
                match _type:
                    case "Collection":
                        Collection.from_dict(body)
                    case "FeatureCollection":
                        ItemCollection.from_dict(body)
                    case "Feature":
                        Item.from_dict(body)
                    case _:
                        errors += f"[{context}] : {method} {url} object with type '{_type}' could not be hydrated with pystac"
            except Exception as e:
                errors += f"[{context}] : {method} {url} '{body.get('id')}' failed pystac hydration: {e}"

            if _type in ["Collection", "Feature"]:
                if not (
                    stac_validator := StacValidate(links=True, assets=True)
                ).validate_dict(body):
                    errors += f"[{context}] : {method} {url} failed stac-validator validation: {stac_validator.message}"

        else:
            errors += f"[{context}] : {method} {url} missing 'type' attribute"


def stac_check(
    url: str,
    errors: Errors,
    warnings: Warnings,
    context: Context,
    method: Method = Method.GET,
) -> None:
    try:
        linter = Linter(url)
        if not linter.valid_stac:
            errors += f"[{context}] : {method} {url} is not a valid STAC object: {linter.error_msg}"
        if msgs := linter.best_practices_msg[1:]:  # first msg is a header, so skip
            warnings += f"[{context}] : {method} {url} has these stac-check recommendations: {','.join([x.strip() for x in msgs])}"
    except KeyError as e:
        # see https://github.com/stac-utils/stac-check/issues/104
        errors += f"[{Context.CORE}] Error running stac-check, probably because an item doesn't have a bbox defined, which is okay!: {e} "
    except Exception as e:
        errors += f"[{Context.CORE}] Error while running stac-check: {e} "


def retrieve(
    method: Method,
    url: str,
    errors: Errors,
    context: Context,
    r_session: Session,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    status_code: int = 200,
    body: Optional[Dict[str, Any]] = None,
    additional: Optional[str] = "",
    content_type: Optional[str] = None,
) -> Tuple[int, Optional[Dict[str, Any]], Optional[Mapping[str, str]]]:
    resp = r_session.send(
        Request(method.value, url, headers=headers, params=params, json=body).prepare()
    )

    # todo: handle connection exception, etc.
    # todo: handle timeout

    if resp.status_code != status_code:
        errors += (
            f"[{context}] : {method} {url} params={params} body={json.dumps(body) if body else ''}"
            f" had unexpected status code {resp.status_code} instead of {status_code}: {additional}"
        )

    elif status_code < 400:
        if not content_type:
            if url.endswith("/search") or url.endswith("/items"):
                if not has_content_type(resp.headers, geojson_mt):
                    errors += f"[{context}] : {method} {url} params={params} body={body} content-type header is {resp.headers.get('content-type')} instead of '{geojson_mt}'"
            elif not has_content_type(resp.headers, "application/json"):
                errors += f"[{context}] : {method} {url} params={params} body={body} content-type header is {resp.headers.get('content-type')} instead of 'application/json'"
        elif content_type == "undefined":
            if resp.headers.get("content-type"):
                errors += f"[{context}] : {method} {url} params={params} body={body} content-type header is {resp.headers.get('content-type')} instead of undefined"
        elif not has_content_type(resp.headers, content_type):
            errors += f"[{context}] : {method} {url} params={params} body={body} content-type header is {resp.headers.get('content-type')} instead of '{content_type}'"

        if has_json_content_type(resp.headers) or has_geojson_content_type(
            resp.headers
        ):
            try:
                return resp.status_code, resp.json(), resp.headers
            except json.decoder.JSONDecodeError:
                errors += f"[{context}] : {method} {url} returned non-JSON value"

    return resp.status_code, None, resp.headers


def validate_core_landing_page_body(
    body: Dict[str, Any],
    headers: Mapping[str, str],
    errors: Errors,
    warnings: Warnings,
    conformance_classes: List[str],
    collection: Optional[str],
    geometry: Optional[str],
) -> bool:
    if not has_json_content_type(headers):
        errors += (
            "CORE-1",
            "[Core] : Landing Page (/) response Content-Type header is not application/json",
        )

    if not body.get("links"):
        errors += ("CORE-3", "/ : 'links' field must be defined and non-empty.")

    conforms_to = body.get("conformsTo", [])
    if not conforms_to:
        errors += (
            "CORE-2",
            "[Core] : Landing Page (/) 'conformsTo' field must be defined and non-empty."
            "This field is required as of STAC 1.0.0",
        )
    else:
        if any(
            x
            for x in conforms_to
            if re.match(
                r"https://api\.stacspec\.org/v1\.0\.0.*/(core|item-search|ogcapi-features|collections)",
                x,
            )
            and not x.startswith(LATEST_STAC_API_FOUNDATION_VERSION)
        ):
            warnings += f"STAC API Specification {LATEST_STAC_API_FOUNDATION_VERSION} is the latest version, but API advertises an older version or older versions."

    if not supports(conforms_to, cc_core_regex):
        errors += ("CORE-4", "/: STAC API - Core not contained in 'conformsTo'")

    if "browseable" in conformance_classes and not any(
        cc_browseable_regex.fullmatch(x) for x in conforms_to
    ):
        errors += (
            "CORE-5",
            "/: Browseable configured for validation, but not contained in 'conformsTo'",
        )

    if "children" in conformance_classes and not any(
        cc_children_regex.fullmatch(x) for x in conforms_to
    ):
        errors += (
            "CORE-6",
            "/: Children configured for validation, but not contained in 'conformsTo'",
        )

    if "collections" in conformance_classes:
        if not supports_collections(conforms_to):
            errors += (
                "CORE-7",
                "/: Collections configured for validation, but not contained in 'conformsTo'",
            )
        if collection is None:
            logger.fatal(
                "Collections configured for validation, but `--collection` parameter not specified"
            )
            return False

    if "features" in conformance_classes:
        if not supports_features(conforms_to):
            errors += (
                "CORE-8",
                "/: Features configured for validation, but not contained in 'conformsTo'",
            )
        if collection is None:
            logger.fatal(
                "Features configured for validation, but `--collection` parameter not specified"
            )
            return False

    if "item-search" in conformance_classes:
        if not supports(conforms_to, cc_item_search_regex):
            errors += (
                "CORE-9",
                "/: Item Search configured for validation, but not contained in 'conformsTo'",
            )
        if collection is None:
            logger.fatal(
                "Item Search configured for validation, but `--collection` parameter not specified"
            )
            return False
        if geometry is None:
            logger.fatal(
                " Item Search configured for validation, but `--geometry` parameter not specified"
            )
            return False

    if "children" in conformance_classes and not any(
        cc_children_regex.fullmatch(x) for x in conforms_to
    ):
        errors += (
            "CORE-6",
            "/: Children configured for validation, but not contained in 'conformsTo'",
        )

    return True


def validate_api(
    root_url: str,
    ccs_to_validate: List[str],
    collection: Optional[str],
    geometry: Optional[str],
    auth_bearer_token: Optional[str],
    auth_query_parameter: Optional[str],
    fields_nested_property: Optional[str],
    validate_pagination: bool,
    query_config: QueryConfig,
    transaction_collection: Optional[str],
) -> Tuple[Warnings, Errors]:
    warnings = Warnings()
    errors = Errors()

    r_session = Session()
    if auth_bearer_token:
        r_session.headers.update({"Authorization": f"Bearer {auth_bearer_token}"})

    if auth_query_parameter and (xs := auth_query_parameter.split("=", 1)):
        r_session.params = {xs[0]: xs[1]}

    _, landing_page_body, landing_page_headers = retrieve(
        Method.GET, root_url, errors, Context.CORE, r_session
    )

    if not landing_page_body:
        return warnings, errors

    assert landing_page_body is not None
    assert landing_page_headers is not None

    if "core" in ccs_to_validate:
        # fail fast if there are errors with conformance or links so far
        if not validate_core_landing_page_body(
            landing_page_body,
            landing_page_headers,
            errors,
            warnings,
            ccs_to_validate,
            collection,
            geometry,
        ):
            return warnings, errors

        logger.info("Validating STAC API - Core conformance class.")
        validate_core(landing_page_body, errors, warnings, r_session)

    if "browseable" in ccs_to_validate:
        logger.info("Validating STAC API - Browseable conformance class.")
        validate_browseable(landing_page_body, errors, warnings, r_session)

    if "children" in ccs_to_validate:
        logger.info("Validating STAC API - Children conformance class.")
        validate_children(landing_page_body, errors, warnings, r_session)

    if "collections" in ccs_to_validate:
        logger.info("Validating STAC API - Collections conformance class.")
        validate_collections(landing_page_body, collection, errors, warnings, r_session)

    conforms_to = landing_page_body.get("conformsTo", [])

    if "features" in ccs_to_validate:
        logger.info("Validating STAC API - Features conformance class.")
        validate_collections(landing_page_body, collection, errors, warnings, r_session)
        validate_features(
            landing_page_body,
            conforms_to,
            collection,
            geometry,
            warnings,
            errors,
            r_session,
            validate_pagination=validate_pagination,
        )

    if "transaction" in ccs_to_validate:
        logger.info(
            "STAC API - Features - Transaction extension conformance class found."
        )
        validate_transaction(
            context=Context.FEATURES_TXN,
            landing_page_body=landing_page_body,
            collection=collection,
            errors=errors,
            warnings=warnings,
            r_session=r_session,
            transaction_collection=transaction_collection,
        )

    if "features#fields" in ccs_to_validate:
        logger.info("STAC API - Features - Fields extension conformance class found.")
        logger.info("STAC API - Features - Fields extension is not yet supported.")

    if "features#sort" in ccs_to_validate:
        logger.info("STAC API - Features - Sort extension conformance class found.")
        logger.info("STAC API - Features - Sort extension is not yet supported.")

    if "features#query" in ccs_to_validate:
        logger.info("STAC API - Features - Query extension conformance class found.")
        logger.info("STAC API - Features - Query extension is not yet supported.")

    if "features#filter" in ccs_to_validate:
        logger.info("STAC API - Features - Filter Extension conformance class found.")
        validate_features_filter(
            root_body=landing_page_body,
            collection=collection,
            errors=errors,
            r_session=r_session,
        )

    if "item-search" in ccs_to_validate:
        logger.info("Validating STAC API - Item Search conformance class.")
        validate_item_search(
            root_url=root_url,
            root_body=landing_page_body,
            collection=collection,  # type:ignore
            conforms_to=conforms_to,
            warnings=warnings,
            errors=errors,
            geometry=geometry,  # type:ignore
            conformance_classes=ccs_to_validate,
            r_session=r_session,
            validate_pagination=validate_pagination,
        )

    if "item-search#fields" in ccs_to_validate:
        logger.info(
            "STAC API - Item Search - Fields extension conformance class found."
        )
        validate_fields(
            context=Context.ITEM_SEARCH_FIELDS,
            landing_page_body=landing_page_body,
            collection=collection,
            errors=errors,
            warnings=warnings,
            r_session=r_session,
            fields_nested_property=fields_nested_property,
        )

    if "item-search#sort" in ccs_to_validate:
        logger.info("STAC API - Item Search - Sort extension conformance class found.")
        validate_sort(
            context=Context.ITEM_SEARCH_SORT,
            landing_page_body=landing_page_body,
            collection=collection,
            errors=errors,
            warnings=warnings,
            r_session=r_session,
            query_config=query_config,
        )

    if "item-search#query" in ccs_to_validate:
        logger.info("STAC API - Item Search - Query extension conformance class found.")
        validate_query(
            context=Context.ITEM_SEARCH_QUERY,
            landing_page_body=landing_page_body,
            collection=collection,
            errors=errors,
            warnings=warnings,
            r_session=r_session,
            query_config=query_config,
        )

    if "item-search#filter" in ccs_to_validate:
        logger.info(
            "STAC API - Item Search - Filter Extension conformance class found."
        )
        validate_item_search_filter(
            root_url=root_url,
            root_body=landing_page_body,
            collection=collection,
            errors=errors,
            r_session=r_session,
        )

    if not errors:
        try:
            catalog = Client.open(root_url)
            catalog.validate()
            for child in catalog.get_children():
                child.validate()
        except STACValidationError as e:
            errors += f"pystac validation error: {e}"
        except Exception as e:
            errors += f"Error with  pystac: {e}"

    return warnings, errors


def link_by_rel(
    links: Optional[List[Dict[str, Any]]], rel: str
) -> Optional[Dict[str, Any]]:
    if not links:
        return None
    else:
        return next(iter(links_by_rel(links, rel)), None)


def links_by_rel(
    links: Optional[List[Dict[str, Any]]], rel: str
) -> List[Dict[str, Any]]:
    if not links:
        return []
    else:
        return [link for link in links if link.get("rel") == rel]


def validate_core(
    root_body: Dict[str, Any], errors: Errors, warnings: Warnings, r_session: Session
) -> None:
    links = root_body.get("links")

    if links is None:
        errors += "/ : 'links' attribute missing"

    if not (root := link_by_rel(links, "root")):
        errors += "/ : Link[rel=root] must exist"
    else:
        if not is_json_type(root.get("type")):
            errors += f"/ : Link[rel=root] type is not application/geo+json, instead {root.get('type')}"

    if not (_self := link_by_rel(links, "self")):
        warnings += "/ : Link[rel=self] must exist"
    else:
        if not is_json_type(_self.get("type")):
            errors += f"/ : Link[rel=self] type is not application/geo+json, instead {_self.get('type')}"

    if not (service_desc := link_by_rel(links, "service-desc")):
        errors += "/ : Link[rel=service-desc] must exist"
    else:
        if not (service_desc_type := service_desc.get("type")):
            errors += "/ : Link[rel=service-desc] must have a type defined"
        else:
            r_service_desc = r_session.send(
                Request(
                    "GET", service_desc["href"], headers={"Accept": service_desc_type}
                ).prepare()
            )

            if not r_service_desc.status_code == 200:
                errors += "/ : Link[service-desc] must return 200"
            else:
                content_type = r_service_desc.headers.get("content-type", "")
                if content_type in ["application/yaml", "application/vnd.oai.openapi"]:
                    pass
                    # openapi_spec = r_service_desc.json()
                    # todo: verify limits exist and test them
                elif content_type in [
                    "application/json",
                    "application/vnd.oai.openapi+json",
                    "application/vnd.oai.openapi+json;version=3.0",
                    "application/vnd.oai.openapi+json;version=3.1",
                ]:
                    yaml.safe_load(r_service_desc.text)

            if (
                (ct := r_service_desc.headers.get("content-type", ""))
                == service_desc_type
            ) or (
                (";" in ct or ";" in service_desc_type)
                and (ct.split(";", 1)[0] == service_desc_type.split(";", 1)[0])
            ):
                pass
            else:
                errors += f"service-desc ({service_desc}): media type used in Accept header must get response with same Content-Type header: used '{service_desc_type}', got '{ct}'"

    if not (service_doc := link_by_rel(links, "service-doc")):
        warnings += "/ : Link[rel=service-doc] should exist"
    else:
        if service_doc.get("type") != "text/html":
            errors += "service-doc type is not text/html"

        retrieve(
            Method.GET,
            service_doc["href"],
            errors,
            Context.CORE,
            content_type="text/html",
            r_session=r_session,
        )

    # this validates, among other things, that the child and item link relations reference
    # valid STAC Catalogs, Collections, and/or Items
    try:
        list(take(1000, Catalog.from_dict(root_body).get_all_items()))
    except pystac.errors.STACTypeError as e:
        errors += (
            f"[{Context.CORE}] Error while traversing Catalog child/item links to find Items: {e} "
            "This can be reproduced with 'list(pystac.Catalog.from_file(root_url).get_all_items())'"
        )
    except UnicodeEncodeError as e:
        # see https://github.com/jjrom/resto/issues/356#issuecomment-1443818163
        errors += f"[{Context.CORE}] Error while traversing Catalog, a non-ascii character is encoded incorrectly somewhere: {e} "
    except Exception as e:
        errors += f"[{Context.CORE}] Error while traversing Catalog with pystac: {e} "


def validate_browseable(
    root_body: Dict[str, Any],
    errors: Errors,
    warnings: Warnings,
    r_session: Session,
) -> None:
    # child or item links exist in the root
    child_links = links_by_rel(root_body.get("links"), "child")
    item_links = links_by_rel(root_body.get("links"), "item")
    if not (child_links or item_links):
        errors += f"[{Context.BROWSEABLE}] /: Root catalog does not contain any child or item link relations"

    # check that at least a few of the items that can be reached from child/item link relations
    # can be found through search
    try:
        for item in take(10, Catalog.from_dict(root_body).get_all_items()):
            if link := link_by_rel(root_body.get("links"), "search"):
                _, body, _ = retrieve(
                    Method.GET,
                    link["href"],
                    errors,
                    Context.BROWSEABLE,
                    params={"ids": item.id, "collections": item.collection},
                    r_session=r_session,
                )
                if body and len(body.get("features", [])) != 1:
                    errors += f"[{Context.BROWSEABLE}] /: Link[rel=children] must href /children"
            else:
                errors += (
                    f"[{Context.BROWSEABLE}] /: Link[rel=search] could not be found"
                )
    except pystac.errors.STACTypeError as e:
        errors += (
            f"[{Context.BROWSEABLE}] Error while traversing Catalog child/item links to find Items: {e}. "
            "This can be reproduced with 'pystac.Catalog.from_file(root_url).get_all_items()'"
        )


def validate_children(
    root_body: Dict[str, Any],
    errors: Errors,
    warnings: Warnings,
    r_session: Session,
) -> None:
    children_link = link_by_rel(root_body.get("links"), "children")
    if (
        not children_link
        or not children_link.get("href", "").endswith("/children")
        or not is_json_type(children_link.get("type"))
    ):
        errors += f"[{Context.CHILDREN}] /: Link[rel=children] must href /children"
        return

    if not (children_href := children_link.get("href")):
        errors += f"[{Context.CHILDREN}] /: Link[rel=children] missing href"
    else:
        _, children_body, resp_headers = retrieve(
            Method.GET,
            children_href,
            errors,
            Context.CHILDREN,
            r_session=r_session,
        )
        if not children_body:
            errors += f"[{Context.CHILDREN}] /children body was empty"
            return

        if not resp_headers or not has_json_content_type(resp_headers):
            errors += f"[{Context.CHILDREN}] /children content-type header was not application/json"

        if not (self_link := link_by_rel(children_body.get("links", []), "self")):
            errors += f"[{Context.CHILDREN}] /children does not have self link"
        elif children_link.get("href") != self_link.get("href"):
            errors += (
                f"[{Context.CHILDREN}] /children self link does not match requested url"
            )

        if not link_by_rel(children_body.get("links", []), "root"):
            errors += f"[{Context.CHILDREN}] /children does not have root link"

        # each child link in Landing Page must have an entry in children
        child_links = links_by_rel(root_body.get("links"), "child")

        child_link_bodies = []
        for child_link in child_links:
            if child_href := child_link.get("href"):
                _, child_body, child_resp_headers = retrieve(
                    Method.GET,
                    child_href,
                    errors,
                    Context.CHILDREN,
                    r_session=r_session,
                )
                child_link_bodies.append(child_body)
            else:
                errors += f"[{Context.CHILDREN}] child link {json.dumps(child_link)} missing href field"

        child_links_vs_children_diff = DeepDiff(
            child_link_bodies, children_body.get("children"), ignore_order=True
        )
        if iterable_item_removed := child_links_vs_children_diff.get(
            "iterable_item_removed"
        ):
            errors += (
                f"[{Context.CHILDREN}] /: child links contained these objects that /children does not: "
                f"{json.dumps(iterable_item_removed)}"
            )

        if iterable_item_added := child_links_vs_children_diff.get(
            "iterable_item_added"
        ):
            errors += (
                f"[{Context.CHILDREN}] /: child links missing these objects that /children contains: "
                f"{json.dumps(iterable_item_added)}"
            )


def validate_collections(
    root_body: Dict[str, Any],
    collection: Optional[str],
    errors: Errors,
    warnings: Warnings,
    r_session: Session,
) -> None:
    if not (data_link := link_by_rel(root_body["links"], "data")):
        errors += f"[{Context.COLLECTIONS}] /: Link[rel=data] must href /collections"
    else:
        retrieve(
            Method.GET,
            f"{data_link['href']}/non-existent-collection",
            errors,
            Context.COLLECTIONS,
            status_code=404,
            r_session=r_session,
            additional="non-existent collection",
        )

        collections_url = f"{data_link['href']}"
        _, body, resp_headers = retrieve(
            Method.GET,
            collections_url,
            errors,
            Context.COLLECTIONS,
            r_session=r_session,
        )

        if not body:
            errors += f"[{Context.COLLECTIONS}] /collections body was empty"
        else:
            if not resp_headers or not has_json_content_type(resp_headers):
                errors += f"[{Context.COLLECTIONS}] /collections content-type header was not application/json"

            if not (self_link := link_by_rel(body.get("links", []), "self")):
                errors += (
                    f"[{Context.COLLECTIONS}] /collections does not have self link"
                )
            elif collections_url != self_link.get("href"):
                errors += f"[{Context.COLLECTIONS}] /collections self link does not match requested url"

            if not link_by_rel(body.get("links", []), "root"):
                errors += (
                    f"[{Context.COLLECTIONS}] /collections does not have root link"
                )

            if collections_type := body.get("type"):
                warnings += (
                    f"[{Context.COLLECTIONS}] /collections entity has a field 'type: {collections_type}', "
                    "but the STAC API entity schema does not define this field"
                )

            if body.get("collections") is None:
                errors += f"[{Context.COLLECTIONS}] /collections does not have 'collections' field"

            if not (collections_list := body.get("collections")):
                errors += (
                    f"[{Context.COLLECTIONS}] /collections 'collections' field is empty"
                )
            else:
                for body in collections_list:
                    stac_validate(collections_url, body, errors, Context.COLLECTIONS)

            collection_url = f"{data_link['href']}/{collection}"
            _, body, resp_headers = retrieve(
                Method.GET,
                collection_url,
                errors,
                Context.COLLECTIONS,
                r_session=r_session,
            )

            if not body:
                errors += f"[{Context.COLLECTIONS}] : {collection_url} body was empty"
            else:
                if not resp_headers or not has_json_content_type(resp_headers):
                    errors += f"[{Context.COLLECTIONS}] : {collection_url} content-type header was not application/json"

                if not (self_link := link_by_rel(body.get("links", []), "self")):
                    errors += f"[{Context.COLLECTIONS}] : {collection_url} does not have self link"
                elif collection_url != self_link.get("href"):
                    errors += f"[{Context.COLLECTIONS}] : {collection_url} self link does not match requested url"

                if not link_by_rel(body.get("links", []), "root"):
                    errors += f"[{Context.COLLECTIONS}] : {collection_url} does not have root link"

                if not link_by_rel(body.get("links", []), "parent"):
                    errors += f"[{Context.COLLECTIONS}] : {collection_url} does not have parent link"

                stac_validate(collection_url, body, errors, Context.COLLECTIONS)
                stac_check(collection_url, errors, warnings, Context.COLLECTIONS)

        # todo: collection pagination


def validate_features(
    root_body: Dict[str, Any],
    conforms_to: List[str],
    collection: Optional[str],
    geometry: Optional[str],
    warnings: Warnings,
    errors: Errors,
    r_session: Session,
    validate_pagination: bool,
) -> None:
    if not geometry:
        errors += f"[{Context.FEATURES}] Geometry parameter required for running Features validations."
        return

    if not collection:
        errors += f"[{Context.FEATURES}] Collection parameter required for running Features validations."
        return

    if conforms_to and (
        req_ccs := [
            x
            for x in conforms_to
            if x.startswith("http://www.opengis.net/spec/ogcapi-features-1/1.0/req/")
        ]
    ):
        warnings += f"[{Context.FEATURES}] / : 'conformsTo' contains OGC API conformance classes using 'req' instead of 'conf': {req_ccs}."

    if "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core" not in conforms_to:
        warnings += f"[{Context.FEATURES}] STAC APIs conforming to the Features conformance class may also advertise the OGC API - Features Part 1 conformance class 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core'"

    if (
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
        not in conforms_to
    ):
        warnings += f"[{Context.FEATURES}] STAC APIs conforming to the Features conformance class may also advertise the OGC API - Features Part 1 conformance class 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson'"

    # todo: add this one somewhere
    # if service-desc type is the OAS 3.0 one, add a warning that this can be used also
    # "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",

    root_links = root_body.get("links")
    conformance = link_by_rel(root_links, "conformance")
    if conformance is None:
        errors += f"[{Context.FEATURES}] /: Landing page missing Link[rel=conformance]"
    elif not conformance.get("href", "").endswith("/conformance"):
        errors += f"[{Context.FEATURES}] /: Landing page Link[rel=conformance] must href /conformance"

    if conformance:
        _, body, _ = retrieve(
            Method.GET,
            conformance["href"],
            errors,
            Context.FEATURES,
            r_session=r_session,
        )

        if body and not (
            set(root_body.get("conformsTo", [])) == set(body.get("conformsTo", []))
        ):
            warnings += f"[{Context.FEATURES}] Landing Page conforms to and conformance conformsTo must be the same"

    # This is likely a mistake, but most apis can't undo it for backwards-compat reasons, so only warn
    if not (link_by_rel(root_links, "collections") is None):
        warnings += f"[{Context.FEATURES}] /: Link[rel=collections] is a non-standard relation. Use Link[rel=data instead]"

    # todo: validate items exists in the collection
    if collections_url := link_by_rel(root_links, "data"):
        collection_items_url = f"{collections_url['href']}/{collection}/items"
        _, body, _ = retrieve(
            Method.GET,
            collection_items_url,
            errors,
            Context.FEATURES,
            r_session=r_session,
        )

        if not body:
            errors += f"[{Context.FEATURES}] GET {collection_items_url} returned an empty body"
        else:
            stac_validate(collection_items_url, body, errors, Context.FEATURES)

            item_url = link_by_rel(body.get("features", [])[0]["links"], "self")[
                "href"
            ]  # type:ignore

            _, body, _ = retrieve(
                Method.GET,
                item_url,
                errors,
                Context.FEATURES,
                content_type=geojson_mt,
                r_session=r_session,
            )

            stac_validate(item_url, body, errors, Context.FEATURES)
            stac_check(item_url, errors, warnings, Context.FEATURES)

    # Validate Features non-existent item
    if not (collections_link := link_by_rel(root_links, "data")):
        errors += "/: Link[rel=data] must href /collections"
    else:
        collection_url = f"{collections_link['href']}/{collection}"
        _, body, _ = retrieve(
            Method.GET,
            collection_url,
            errors,
            Context.FEATURES,
            r_session=r_session,
        )
        if body:
            if not (collection_items_link := link_by_rel(body.get("links"), "items")):
                errors += f"[{Context.FEATURES}] : {collection_url} does not have Link[rel=items]"
            else:
                collection_items_url = collection_items_link["href"]

                retrieve(
                    Method.GET,
                    f"{collection_items_url}/non-existent-item",
                    errors,
                    Context.FEATURES,
                    status_code=404,
                    r_session=r_session,
                )

                _, body, _ = retrieve(
                    Method.GET,
                    collection_items_url,
                    errors,
                    Context.FEATURES,
                    content_type=geojson_mt,
                    r_session=r_session,
                )

                if body:
                    if not (self_link := link_by_rel(body.get("links", []), "self")):
                        errors += f"[{Context.FEATURES}] GET {collection_items_url} does not have self link"
                    elif collection_items_link["href"] != self_link.get("href"):
                        errors += f"[{Context.FEATURES}] GET {collection_items_url} self link does not match requested url"

                    if not link_by_rel(body.get("links", []), "root"):
                        errors += f"[{Context.FEATURES}] GET {collection_items_url} does not have root link"

                    stac_validate(collection_items_url, body, errors, Context.FEATURES)

                    item = next(iter(body.get("features", [])), None)

                    if not item:
                        errors += f"[{Context.FEATURES}] : {collection_items_url} features array was empty"
                    else:
                        if not (
                            item_self_link := link_by_rel(item.get("links", []), "self")
                        ):
                            errors += f"[{Context.FEATURES}] : {collection_items_url} first item does not have self link"
                        else:
                            item_url = item_self_link["href"]
                            _, body, _ = retrieve(
                                Method.GET,
                                item_url,
                                errors,
                                Context.FEATURES,
                                content_type=geojson_mt,
                                r_session=r_session,
                            )

                            if body:
                                if not (
                                    self_link := link_by_rel(
                                        body.get("links", []), "self"
                                    )
                                ):
                                    errors += f"[{Context.FEATURES}] GET {item_url} does not have self link"
                                elif item_url != self_link.get("href"):
                                    errors += f"[{Context.FEATURES}] GET {item_url} self link does not match requested url"

                                if not link_by_rel(body.get("links", []), "root"):
                                    errors += f"[{Context.FEATURES}] GET {item_url} does not have root link"

                                if not link_by_rel(body.get("links", []), "parent"):
                                    errors += f"[{Context.FEATURES}] GET {item_url} does not have parent link"

                                stac_validate(item_url, body, errors, Context.FEATURES)
                                stac_check(item_url, errors, warnings, Context.FEATURES)

    if validate_pagination:
        # Items pagination validation
        if not (collections_url := link_by_rel(root_links, "data")):
            errors += (
                "/: Link[rel=data] must href /collections, cannot run pagination test"
            )
        else:
            if not (self_link := link_by_rel(root_links, "self")):
                errors += "/: Link[rel=self] missing"
            else:
                validate_item_pagination(
                    root_url=self_link.get("href", ""),
                    search_url=f"{collections_url['href']}/{collection}/items",
                    collection=None,
                    geometry=geometry,
                    methods={Method.GET},
                    errors=errors,
                    use_pystac_client=False,
                    context=Context.FEATURES,
                    r_session=r_session,
                )


def validate_item_search(
    root_url: str,
    root_body: Dict[str, Any],
    collection: str,
    conforms_to: List[str],
    warnings: Warnings,
    errors: Errors,
    geometry: str,
    conformance_classes: List[str],
    r_session: Session,
    validate_pagination: bool,
) -> None:
    links = root_body.get("links")

    search_links = links_by_rel(links, "search")

    if not search_links:
        errors += "/: Link[rel=search] must exist when Item Search is implemented"
        return
    elif len(search_links) > 2:
        errors += "/: More than 2 Link[rel=search] exist"

    if len(search_links) == 2:
        if (
            len([link for link in search_links if link.get("method", None) == "GET"])
            != 1
        ):
            errors += "/: More than one Link[rel=search] with method GET exists"
        if (
            len([link for link in search_links if link.get("method", None) == "POST"])
            != 1
        ):
            errors += "/: More than one Link[rel=search] with method POST exists"
        if (sl0_href := search_links[0].get("href")) and sl0_href != search_links[
            1
        ].get("href"):
            errors += "/: Link[rel=search] relations have different URLs"

    methods: Set[Method] = {Method[sl.get("method", "GET")] for sl in search_links}

    # Collections may not be implemented, so set to None
    # and later get some collection ids another way
    if links and (collections := link_by_rel(links, "data")):
        collections_url = collections.get("href")
    else:
        collections_url = None

    search_url = search_links[0]["href"]
    _, body, _ = retrieve(
        Method.GET,
        search_url,
        errors,
        Context.ITEM_SEARCH,
        content_type=geojson_mt,
        r_session=r_session,
    )

    if body:
        stac_validate(search_url, body, errors, Context.ITEM_SEARCH)

    validate_item_search_limit(search_url, methods, errors, r_session)
    validate_item_search_bbox_xor_intersects(search_url, methods, errors, r_session)
    validate_item_search_bbox(search_url, methods, errors, r_session)
    validate_item_search_datetime(search_url, methods, warnings, errors, r_session)
    validate_item_search_ids(search_url, methods, warnings, errors, r_session)
    validate_item_search_ids_does_not_override_all_other_params(
        search_url, methods, collection, warnings, errors, r_session
    )
    validate_item_search_collections(
        search_url, collections_url, methods, errors, r_session
    )
    validate_item_search_intersects(
        search_url=search_url,
        collection=collection,
        methods=methods,
        errors=errors,
        geometry=geometry,
        r_session=r_session,
    )

    if validate_pagination:
        validate_item_pagination(
            root_url=root_url,
            search_url=search_url,
            collection=collection,
            geometry=geometry,
            methods=methods,
            errors=errors,
            use_pystac_client=True,
            context=Context.ITEM_SEARCH,
            r_session=r_session,
        )

    if supports(conforms_to, cc_item_search_fields_regex):
        logger.info(
            "STAC API - Item Search - Fields extension conformance class found."
        )

    if supports(conforms_to, cc_item_search_sort_regex):
        logger.info("STAC API - Item Search - Sort extension conformance class found.")

    if supports(conforms_to, cc_item_search_query_regex):
        logger.info("STAC API - Item Search - Query extension conformance class found.")

    if any(
        x.endswith("item-search#filter:basic-cql")
        or x.endswith("item-search#filter:cql-json")
        or x.endswith("item-search#filter:cql-text")
        or x.endswith("item-search#filter:filter")
        for x in conforms_to
    ):
        warnings += "[Filter Ext] /: pre-1.0.0-rc.1 Filter Extension conformance classes are advertised."

    if "filter" in conformance_classes and any(
        cc_item_search_filter_regex.fullmatch(x)
        or x.endswith("item-search#filter:filter")
        for x in conforms_to
    ):
        logger.info(
            "Validating STAC API - Item Search - Filter Extension conformance class."
        )
        validate_item_search_filter(
            root_url=root_url,
            root_body=root_body,
            collection=collection,
            errors=errors,
            r_session=r_session,
        )


def validate_filter_queryables(
    queryables_url: str, context: Context, errors: Errors, r_session: Session
) -> None:
    _, queryables_schema, _ = retrieve(
        Method.GET,
        queryables_url,
        errors,
        context,
        content_type="application/schema+json",
        r_session=r_session,
        headers={"Accept": "application/schema+json"},
    )

    if queryables_schema:
        json_schemas = [
            "https://json-schema.org/draft/2019-09/schema",
            "http://json-schema.org/draft-07/schema#",
        ]
        if queryables_schema.get("$schema") not in json_schemas:
            errors += (
                f"[{context} - Filter Ext] Queryables '{queryables_url}' "
                f"'$schema' value invalid, must be one of: '{','.join(json_schemas)}'"
            )

        if queryables_schema.get("$id") != queryables_url:
            errors += f"[{context} - Filter Ext] Queryables '{queryables_url}' '$id' value invalid, must be same as queryables url"

        if queryables_schema.get("type") != "object":
            errors += f"[{context} Filter Ext] Queryables '{queryables_url}' 'type' value invalid, must be 'object'"


def validate_default_fields(
    item: Optional[dict[str, Any]], desc: str, context: Context, errors: Errors
) -> None:
    if not item:
        errors += f"[{context}] : response had not items in response for '{desc}'"
        return

    for field in ["type", "stac_version", "id", "geometry", "bbox", "links", "assets"]:
        if not item.get(field):
            errors += f"[{context}] : {desc} response missing '{field}'"
    if not (
        item.get("properties", {}).get("datetime")
        or (
            item.get("properties", {}).get("start_datetime")
            and item.get("properties", {}).get("end_datetime")
        )
    ):
        errors += (
            f"[{context}] : GET with empty 'fields' value response does not have either"
            + "'properties.datetime' or (properties.start_datetime and properties.end_datetime)"
        )


def validate_query(
    landing_page_body: Dict[str, Any],
    collection: str,
    errors: Errors,
    warnings: Warnings,
    r_session: Session,
    context: Context,
    query_config: QueryConfig,
) -> None:
    # todo: validate that all the fields are configured
    # if not query_config [all the fields]:
    #     errors += f"[{context}] : cannot validate Query Extension because some configuration is not present"
    #     return

    limit = 20

    search_method_to_url: dict[Method, str] = {
        Method[x.get("method", "GET")]: x.get("href")
        for x in links_by_rel(landing_page_body.get("links"), "search")
    }

    # eq
    query = {query_config.query_comparison_field: {"eq": query_config.query_eq_value}}

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            == float(query_config.query_eq_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            == float(query_config.query_eq_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    # neq
    query = {query_config.query_comparison_field: {"neq": query_config.query_neq_value}}

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            != float(query_config.query_neq_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            != float(query_config.query_neq_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    # lt
    query = {query_config.query_comparison_field: {"lt": query_config.query_lt_value}}

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            < float(query_config.query_lt_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            < float(query_config.query_lt_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    # lte
    query = {query_config.query_comparison_field: {"lte": query_config.query_lte_value}}

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            <= float(query_config.query_lte_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            <= float(query_config.query_lte_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    # gt
    query = {query_config.query_comparison_field: {"gt": query_config.query_gt_value}}

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            > float(query_config.query_gt_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            > float(query_config.query_gt_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    # gte
    query = {query_config.query_comparison_field: {"gte": query_config.query_gte_value}}

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            >= float(query_config.query_gte_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            f["properties"][query_config.query_comparison_field]
            >= float(query_config.query_gte_value)
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_comparison_field] for f in body['features']]}"

    # startsWith
    query = {
        query_config.query_substring_field: {
            "startsWith": query_config.query_starts_with_value
        }
    }

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            str(f["properties"][query_config.query_substring_field]).startswith(
                str(query_config.query_starts_with_value)
            )
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_substring_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            str(f["properties"][query_config.query_substring_field]).startswith(
                str(query_config.query_starts_with_value)
            )
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_substring_field] for f in body['features']]}"

    # endsWith
    query = {
        query_config.query_substring_field: {
            "endsWith": query_config.query_ends_with_value
        }
    }

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            str(f["properties"][query_config.query_substring_field]).endswith(
                str(query_config.query_ends_with_value)
            )
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_substring_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            str(f["properties"][query_config.query_substring_field]).endswith(
                str(query_config.query_ends_with_value)
            )
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_substring_field] for f in body['features']]}"

    # contains
    query = {
        query_config.query_substring_field: {
            "contains": query_config.query_contains_value
        }
    }

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if not all(
            str(query_config.query_contains_value)
            in str(f["properties"][query_config.query_substring_field])
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_substring_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if not all(
            str(query_config.query_contains_value)
            in str(f["properties"][query_config.query_substring_field])
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_substring_field] for f in body['features']]}"

    # in
    query_in_values_array = query_config.query_in_values.split(",")
    query = {query_config.query_in_field: {"in": query_in_values_array}}

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "query": json.dumps(query),
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had no results"

        if any(
            set(query_in_values_array).isdisjoint(
                set(f["properties"][query_config.query_in_field])
            )
            for f in body["features"]
        ):
            errors += f"[{context}] : GET search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_in_field] for f in body['features']]}"

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "query": query,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had no results"

        if any(
            set(query_in_values_array).isdisjoint(
                set(f["properties"][query_config.query_in_field])
            )
            for f in body["features"]
        ):
            errors += f"[{context}] : POST search with Query '{json.dumps(query)}' had non-matching results: got {[f['properties'][query_config.query_in_field] for f in body['features']]}"


def validate_fields(
    landing_page_body: Dict[str, Any],
    collection: str,
    errors: Errors,
    warnings: Warnings,
    r_session: Session,
    context: Context,
    fields_nested_property: Optional[str],
) -> None:
    if not fields_nested_property:
        errors += f"[{context}] : cannot validate Fields Extension because --fields-nested-property is not set"
        return

    # 1. If `fields` attribute is specified as an empty object (for POST requests),
    # an empty string (for GET requests),
    # or with both `include` and `exclude` set to null or an
    # empty array, then the recommended behavior is to include only fields
    # `type`, `stac_version`, `id`, `geometry`, `bbox`, `links`, `assets`, and `properties.datetime`.

    search_method_to_url: dict[Method, str] = {
        Method[x.get("method", "GET")]: x.get("href")
        for x in links_by_rel(landing_page_body.get("links"), "search")
    }

    def first_item(body: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        if body:
            return next(iter(body.get("features", [])), None)
        else:
            return None

    def validate_include_field(
        desc: str,
        body: dict[str, Any],
        field: str,
        errors: Errors,
        warnings: Warnings,
        allow_extra: bool = False,
    ):
        if not body or not (item := first_item(body)):
            errors += f"[{context}] : response had no items in response for {desc}"
        else:
            field = field if not field.startswith("+") else field[1:]
            # todo: rewrite this to arbitrarily deep
            if "." in field:
                parts = field.split(".")
                value = item.get(parts[0], {}).get(parts[1])
            else:
                value = item.get(field)

            if not value:
                errors += f"[{context}] : {desc} response missing '{field}'"

            if not allow_extra:
                if len(item) > 5:
                    errors += f"[{context}] : {desc} response contained more than 5 extra fields {list(item.keys())}"

                item.pop(field, None)
                if item:
                    warnings += f"[{context}] : {desc} response contained extra fields {list(item.keys())}"

    def validate_exclude_field(
        desc: str,
        body: dict[str, Any],
        field: str,
        errors: Errors,
        warnings: Warnings,
        disallow_extra: bool = True,
    ):
        if not body or not (item := first_item(body)):
            errors += f"[{context}] : response had no items in response for {desc}"
        else:
            # todo: rewrite this to arbitrarily deep
            if "." in field:
                parts = field.split(".")
                value = item.get(parts[0], {}).get(parts[1])
            else:
                value = item.get(field)

            if value:
                errors += f"[{context}] : {desc} response contained '{field}', but should have been excluded"

            if disallow_extra:
                if len(item) < 5:
                    errors += f"[{context}] : {desc} response contained fewer than 5 fields {list(item.keys())}"

    if Method.GET in search_method_to_url:
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={"fields": "", "limit": 1, "collections": collection},
            errors=errors,
            context=context,
            r_session=r_session,
        )

        validate_default_fields(
            first_item(body), "GET with empty 'fields' value", context, errors
        )

    if Method.POST in search_method_to_url:
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={"fields": None},
            status_code=400,
            errors=errors,
            context=context,
            r_session=r_session,
        )

        def validate_post_case(fields: Any, msg: str):
            _, body, _ = retrieve(
                Method.POST,
                search_method_to_url[Method.POST],
                body={"fields": fields, "limit": 1, "collections": [collection]},
                errors=errors,
                context=context,
                r_session=r_session,
            )
            validate_default_fields(
                first_item(body), f"POST with {msg}", context, errors
            )

        validate_post_case({}, "empty 'fields' object value")
        validate_post_case(
            {"include": None, "exclude": None}, "null values for include and exclude"
        )
        validate_post_case(
            {"include": [], "exclude": []}, "empty arrays for include and exclude"
        )

    # 2. include

    fields_for_include = [
        "type",
        "stac_version",
        "id",
        "geometry",
        "bbox",
        "links",
        "assets",
    ]
    # tbd: properties.datetime
    # test GET with both including field name with and without the leading '+'
    all_fields_for_include = fields_for_include + list(
        map(lambda x: f"+{x}", fields_for_include)
    )
    if Method.GET in search_method_to_url:
        for field in all_fields_for_include:
            _, body, _ = retrieve(
                Method.GET,
                search_method_to_url[Method.GET],
                params={"fields": field, "limit": 1, "collections": collection},
                errors=errors,
                context=context,
                r_session=r_session,
            )
            desc = f"GET fields='{field}'"
            validate_include_field(desc, body, field, errors, warnings)

    # test POST only with the field name
    if Method.POST in search_method_to_url:
        for field in fields_for_include:
            body_with_only_fields = {"fields": {"include": [field]}}
            _, body, _ = retrieve(
                Method.POST,
                search_method_to_url[Method.POST],
                body={**body_with_only_fields, "limit": 1, "collections": [collection]},
                errors=errors,
                context=context,
                r_session=r_session,
            )

            desc = f"POST {body_with_only_fields}"
            validate_include_field(desc, body, field, errors, warnings)

    # 3. If only exclude is specified, the specified fields should not be included,
    # but every other field available for the Item should be included.
    # TODO: this is ambiguous for GET
    if Method.GET in search_method_to_url:
        field = "-geometry"
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={"fields": field, "limit": 1, "collections": collection},
            errors=errors,
            context=context,
            r_session=r_session,
        )
        desc = f"GET fields='{field}'"
        validate_exclude_field(desc, body, "geometry", errors, warnings)
        validate_include_field(desc, body, "id", errors, warnings, True)
        validate_include_field(desc, body, "assets", errors, warnings, True)

    if Method.POST in search_method_to_url:
        body_with_only_fields = {"fields": {"exclude": ["geometry"]}}

        _, body, _ = retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={**body_with_only_fields, "limit": 1, "collections": [collection]},
            errors=errors,
            context=context,
            r_session=r_session,
        )

        desc = f"POST {body_with_only_fields}"
        validate_exclude_field(desc, body, "geometry", errors, warnings)
        validate_include_field(desc, body, "id", errors, warnings, True)
        validate_include_field(desc, body, "assets", errors, warnings, True)
        validate_include_field(
            desc, body, fields_nested_property, errors, warnings, True
        )

    # 4. If `exclude` is specified and `include` is null or an empty
    # array, then the `exclude` fields should be excluded from the default set.
    # TODO: this is ambiguous for GET
    if Method.GET in search_method_to_url:
        field = "-geometry"
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={"fields": field, "limit": 1, "collections": collection},
            errors=errors,
            context=context,
            r_session=r_session,
        )
        desc = f"GET fields='{field}'"
        validate_exclude_field(desc, body, "geometry", errors, warnings)
        validate_include_field(desc, body, "id", errors, warnings, True)
        validate_include_field(desc, body, "assets", errors, warnings, True)

    if Method.POST in search_method_to_url:
        for include in [[], None]:
            body_with_only_fields = {
                "fields": {"exclude": ["geometry"], "include": include}
            }
            _, body, _ = retrieve(
                Method.POST,
                search_method_to_url[Method.POST],
                body={**body_with_only_fields, "limit": 1, "collections": [collection]},
                errors=errors,
                context=context,
                r_session=r_session,
            )

            desc = f"POST {body_with_only_fields}"
            validate_exclude_field(desc, body, "geometry", errors, warnings)
            validate_exclude_field(desc, body, fields_nested_property, errors, warnings)
            validate_include_field(desc, body, "id", errors, warnings, True)
            validate_include_field(desc, body, "assets", errors, warnings, True)

    # 5. Nested
    # todo: add more of these, as they can get very complicated!
    if Method.GET in search_method_to_url:
        field = f"-properties,+{fields_nested_property}"
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={"fields": field, "limit": 1, "collections": collection},
            errors=errors,
            context=context,
            r_session=r_session,
        )
        desc = f"GET fields='{field}'"
        validate_exclude_field(desc, body, "geometry", errors, warnings, False)
        validate_include_field(
            desc, body, fields_nested_property, errors, warnings, True
        )

    if Method.POST in search_method_to_url:
        body_with_only_fields = {
            "fields": {"exclude": ["properties"], "include": [fields_nested_property]}
        }

        _, body, _ = retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={**body_with_only_fields, "limit": 1, "collections": [collection]},
            errors=errors,
            context=context,
            r_session=r_session,
        )

        desc = f"POST {body_with_only_fields}"
        validate_exclude_field(desc, body, "geometry", errors, warnings)
        validate_include_field(
            desc, body, fields_nested_property, errors, warnings, False
        )

    # 6. If the same field is present in both `include` and `exclude`, it should be included.
    if Method.GET in search_method_to_url:
        field = "+geometry,-geometry"
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={"fields": field, "limit": 1, "collections": collection},
            errors=errors,
            context=context,
            r_session=r_session,
        )
        desc = f"GET fields='{field}'"
        validate_include_field(desc, body, "geometry", errors, warnings)

    if Method.POST in search_method_to_url:
        body_with_only_fields = {
            "fields": {"exclude": ["geometry"], "include": ["geometry"]}
        }
        _, body, _ = retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={**body_with_only_fields, "limit": 1, "collections": [collection]},
            errors=errors,
            context=context,
            r_session=r_session,
        )

        desc = f"POST {body_with_only_fields}"
        validate_include_field(desc, body, "geometry", errors, warnings)


def validate_features_filter(
    root_body: Dict[str, Any], collection: str, errors: Errors, r_session: Session
) -> None:
    logger.info(
        "WARNING: Features - Filter Ext validation is not yet fully implemented."
    )

    if not (collections_link := link_by_rel(root_body["links"], "data")):
        errors += f"[{Context.FEATURES}] / : 'data' link relation missing"
    else:
        collection_url = f"{collections_link['href']}/{collection}"
        _, body, _ = retrieve(
            Method.GET, collection_url, errors, Context.FEATURES, r_session=r_session
        )
        assert body

        if not (
            queryables_link := link_by_rel(
                body["links"], "http://www.opengis.net/def/rel/ogc/1.0/queryables"
            )
        ):
            errors += f"[Features - Filter Ext] GET {collection_url} : 'http://www.opengis.net/def/rel/ogc/1.0/queryables' (Queryables) link relation missing"

        validate_filter_queryables(
            queryables_url=(queryables_link and queryables_link["href"])
            or f"{collection_url}/queryables",
            context=Context.FEATURES,
            errors=errors,
            r_session=r_session,
        )


# Assumes id, collection, geometry, and datetime are available
def validate_item_search_filter(
    root_url: str,
    root_body: Dict[str, Any],
    collection: str,
    errors: Errors,
    r_session: Session,
) -> None:
    search_links = links_by_rel(root_body["links"], "search")
    search_url = search_links[0]["href"]
    if not (
        queryables_link := link_by_rel(
            root_body["links"], "http://www.opengis.net/def/rel/ogc/1.0/queryables"
        )
    ):
        errors += "[Item Search - Filter Ext] / : 'http://www.opengis.net/def/rel/ogc/1.0/queryables' (Queryables) link relation missing"

    validate_filter_queryables(
        queryables_url=(queryables_link and queryables_link["href"])
        or f"{root_url}/queryables",
        context=Context.ITEM_SEARCH,
        errors=errors,
        r_session=r_session,
    )

    conforms_to = root_body.get("conformsTo", [])

    cql2_text_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/cql2-text" in conforms_to
    ) or (
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter:cql-text"
        in conforms_to
    )

    if cql2_text_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - CQL2-Text conformance class."
        )

    cql2_json_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/cql2-json" in conforms_to
    ) or (
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter:cql-json"
        in conforms_to
    )

    if cql2_json_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - CQL2-JSON conformance class."
        )

    basic_cql2_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/basic-cql2" in conforms_to
    ) or (
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter:basic-cql"
        in conforms_to
    )

    if basic_cql2_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - Basic CQL2 conformance class."
        )

    advanced_comparison_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/advanced-comparison-operators"
        in conforms_to
    )

    if advanced_comparison_operators_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - Advanced Comparison Operators conformance class."
        )

    basic_spatial_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/basic-spatial-operators"
        in conforms_to
    )

    if basic_spatial_operators_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - Basic Spatial Operators conformance class."
        )

    temporal_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/temporal-operators" in conforms_to
    )

    if temporal_operators_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - Temporal Operators conformance class."
        )

    # todo: validate these
    # Spatial Operators: http://www.opengis.net/spec/cql2/1.0/conf/spatial-operators
    # Custom Functions: http://www.opengis.net/spec/cql2/1.0/conf/functions
    # Arithmetic Expressions: http://www.opengis.net/spec/cql2/1.0/conf/arithmetic
    # Array Operators: http://www.opengis.net/spec/cql2/1.0/conf/array-operators
    # Property-Property Comparisons: http://www.opengis.net/spec/cql2/1.0/conf/property-property
    # Accent and Case-insensitive Comparison: http://www.opengis.net/spec/cql2/1.0/conf/accent-case-insensitive-comparison

    filter_texts: List[str] = []
    filter_jsons: List[Dict[str, Any]] = []

    if basic_cql2_supported:
        # todo: better error handling when the wrong collection name is given, so 0 results
        _, body, _ = retrieve(
            Method.GET,
            f"{search_url}?collections={collection}",
            context=Context.ITEM_SEARCH_FILTER,
            r_session=r_session,
            content_type=geojson_mt,
            errors=errors,
        )

        assert body
        item = body["features"][0]

        if cql2_text_supported:
            filter_texts.append(cql2_text_ex_3)
            filter_texts.append(cql2_text_ex_4)
            filter_texts.append(cql2_text_ex_9)
            filter_texts.append(cql2_text_and(item["id"], collection))
            filter_texts.append(cql2_text_or(item["id"], collection))
            filter_texts.append(cql2_text_not(item["id"]))
            filter_texts.extend(cql2_text_string_comparisons(collection))
            filter_texts.extend(cql2_text_numeric_comparisons)
            filter_texts.extend(cql2_text_timestamp_comparisons)

            # todo boolean and date

        if cql2_json_supported:
            filter_jsons.append(cql2_json_ex_3)
            filter_jsons.append(cql2_json_ex_4)
            filter_jsons.append(cql2_json_ex_9)
            filter_jsons.append(cql2_json_and(item["id"], collection))
            filter_jsons.append(cql2_json_or(item["id"], collection))
            filter_jsons.append(cql2_json_not(item["id"]))
            filter_jsons.extend(cql2_json_string_comparisons(collection))
            filter_jsons.extend(cql2_json_numeric_comparisons)
            filter_jsons.extend(cql2_json_timestamp_comparisons)

            # todo boolean and date

    if advanced_comparison_operators_supported:
        if cql2_text_supported:
            filter_texts.append(cql2_text_between)
            filter_texts.append(cql2_text_not_between)
            filter_texts.append(cql2_text_like)
            filter_texts.append(cql2_text_not_like)

        if cql2_json_supported:
            filter_jsons.append(cql2_json_between)
            filter_jsons.append(cql2_json_not_between)
            filter_jsons.append(cql2_json_like)
            filter_jsons.append(cql2_json_not_like)

    if basic_spatial_operators_supported:
        if cql2_text_supported:
            filter_texts.append(cql2_text_s_intersects)
            filter_texts.append(cql2_text_ex_2(collection))
            filter_texts.append(cql2_text_ex_8)

        if cql2_json_supported:
            filter_jsons.append(cql2_json_s_intersects)
            filter_jsons.append(cql2_json_ex_2(collection))
            filter_jsons.append(cql2_json_ex_8)

    if temporal_operators_supported:
        if cql2_text_supported:
            filter_texts.append(cql2_text_ex_6)

        if cql2_json_supported:
            filter_jsons.append(cql2_json_ex_6)

    if basic_spatial_operators_supported and temporal_operators_supported:
        if cql2_json_supported:
            filter_jsons.append(cql2_json_common_1)

    # todo: use terms not in queryables
    # todo: how to support all 4 combos of GET|POST & Text|JSON ?

    for f_text in filter_texts:
        retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH_FILTER,
            content_type=geojson_mt,
            r_session=r_session,
            params={"limit": 1, "filter-lang": "cql2-text", "filter": f_text},
        )

    for f_json in filter_jsons:
        retrieve(
            Method.POST,
            search_url,
            body={"limit": 1, "filter-lang": "cql2-json", "filter": f_json},
            errors=errors,
            context=Context.ITEM_SEARCH_FILTER,
            content_type=geojson_mt,
            r_session=r_session,
        )


def validate_item_search_datetime(
    search_url: str,
    methods: Set[Method],
    warnings: Warnings,
    errors: Errors,
    r_session: Session,
) -> None:
    # find an Item and try to use its datetime value in a query
    _, body, _ = retrieve(
        Method.GET,
        search_url,
        errors,
        Context.ITEM_SEARCH,
        r_session=r_session,
        content_type=geojson_mt,
    )
    if not body:
        return
    else:
        if len(body["features"]) == 0:
            errors += f"[{Context.ITEM_SEARCH}] GET Search returned no results."
            return
        dt = body["features"][0]["properties"]["datetime"]

    _, body, _ = retrieve(
        Method.GET,
        search_url,
        errors,
        Context.ITEM_SEARCH,
        r_session,
        content_type=geojson_mt,
        params={"datetime": dt},
        additional=f"with datetime={dt} extracted from an Item",
    )
    if body and len(body["features"]) == 0:
        errors += f"[{Context.ITEM_SEARCH}] GET Search with datetime={dt} extracted from an Item returned no results."

    for dt in valid_datetimes:
        retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            r_session,
            content_type=geojson_mt,
            params={"datetime": dt},
            additional=f"with datetime={dt} extracted from an Item",
        )

    for dt in invalid_datetimes:
        status_code, _, _ = retrieve(
            Method.GET,
            search_url,
            params={"datetime": dt},
            status_code=400,
            r_session=r_session,
            errors=errors,
            context=Context.ITEM_SEARCH,
            additional="invalid datetime returned non-400 status code",
        )

    # todo: POST


def validate_item_search_bbox_xor_intersects(
    search_url: str, methods: Set[Method], errors: Errors, r_session: Session
) -> None:
    if Method.GET in methods:
        retrieve(
            Method.GET,
            search_url,
            errors,
            status_code=400,
            params={"bbox": "0,0,1,1", "intersects": json.dumps(polygon)},
            context=Context.ITEM_SEARCH,
            additional="Search with bbox and intersects",
            r_session=r_session,
        )

    if Method.POST in methods:
        retrieve(
            Method.POST,
            search_url,
            errors,
            status_code=400,
            body={"bbox": [0, 0, 1, 1], "intersects": polygon},
            context=Context.ITEM_SEARCH,
            additional="Search with bbox and intersects",
            r_session=r_session,
        )


def validate_item_pagination(
    root_url: str,
    search_url: str,
    collection: Optional[str],
    geometry: str,
    methods: Set[Method],
    errors: Errors,
    use_pystac_client: bool,
    context: Context,
    r_session: Session,
) -> None:
    url = f"{search_url}?limit=1"
    if collection is not None:
        url = f"{url}&collections={collection}"

    _, first_body, _ = retrieve(
        Method.GET,
        url,
        errors,
        context,
        r_session=r_session,
        content_type=geojson_mt,
        additional="pagination get failed for initial request",
    )
    if first_body:
        if link := link_by_rel(first_body.get("links"), "next"):
            if (method := link.get("method")) and method != "GET":
                errors += f"[{context}] GET pagination first request 'next' link relation has method {method} instead of 'GET'"

            next_url = link.get("href")
            if next_url is None:
                errors += f"[{context}] GET pagination first request 'next' link relation missing href"
            else:
                if url == next_url:
                    errors += f"[{context}] GET pagination next href same as first url"

                retrieve(
                    Method.GET,
                    next_url,
                    errors,
                    context,
                    r_session=r_session,
                    content_type=geojson_mt,
                    additional="pagination get failed for next url",
                )
        else:
            errors += (
                f"[{context}] GET pagination first request had no 'next' link relation"
            )

    max_items = 100

    # todo: how to paginate over items, not just search?

    if use_pystac_client and collection is not None:
        try:
            client = Client.open(root_url)
            search = client.search(
                method="GET", collections=[collection], max_items=max_items, limit=5
            )

            items = list(search.items_as_dicts())

            if len(items) > max_items:
                errors += f"[{context}] GET pagination - more than max items returned from paginating"

            if len(items) > len({item["id"] for item in items}):
                errors += f"[{context}] GET pagination - duplicate items returned from paginating items"
        except Exception as e:
            errors += (
                f"{context} pystac-client threw exception while testing pagination {e}"
            )
    elif use_pystac_client and collection is None:
        errors += f"[{context}] GET pagination - pystac-client tests not run, collection is not defined"

    # GET paging has a problem with intersects https://github.com/stac-utils/pystac-client/issues/335
    # search = client.search(method="GET", collections=[collection], intersects=geometry)
    # if len(list(take(20000, search.items_as_dicts()))) == 20000:
    #     errors +=
    #         f"STAC API - Item Search GET pagination - paged through 20,000 results. This could mean the last page "
    #         f"of results references itself, or your collection and geometry combination has too many results."
    #     )

    if Method.POST in methods:
        initial_json_body = {"limit": 1, "collections": [collection]}

        _, first_body, _ = retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            body=initial_json_body,
            r_session=r_session,
        )

        if first_body and (link := link_by_rel(first_body.get("links"), "next")):
            if (method := link.get("method")) and method != "POST":
                errors += f"STAC API - Item Search POST pagination first request 'next' link relation has method {method} instead of 'POST'"

            next_url = link.get("href")
            if next_url is None:
                errors += "STAC API - Item Search POST pagination first request 'next' link relation missing href"
            else:
                if url == next_url:
                    errors += "STAC API - Item Search POST pagination next href same as first url"

                next_body: Dict[str, Any] = link.get("body", {})
                if not link.get("merge", False):
                    second_json_body = next_body
                else:
                    second_json_body = initial_json_body
                    second_json_body.update(next_body)

                retrieve(
                    Method.POST,
                    next_url,
                    errors,
                    Context.ITEM_SEARCH,
                    body=second_json_body,
                    r_session=r_session,
                )
        else:
            errors += (
                f"[{context}] POST pagination first request had no 'next' link relation"
            )

        if use_pystac_client and collection is not None:
            max_items = 100
            try:
                client = Client.open(root_url)
                search = client.search(
                    method="POST",
                    collections=[collection],
                    max_items=max_items,
                    limit=5,
                )

                items = list(search.items_as_dicts())

                if len(items) > max_items:
                    errors += f"[{context}] POST pagination - more than max items returned from paginating"

                if len(items) > len({item["id"] for item in items}):
                    errors += f"[{context}] POST pagination - duplicate items returned from paginating items"

                search = client.search(
                    method="POST", collections=[collection], intersects=geometry
                )
                if len(list(take(20000, search.items_as_dicts()))) == 20000:
                    errors += (
                        f"[{context}] POST pagination - paged through 20,000 results. This could mean the last page "
                        "of results references itself, or your collection and geometry combination has too many results."
                    )
            except Exception as e:
                errors += f"pystac-client threw exception while testing pagination {e}"
        elif collection is not None:
            errors += f"[{context}] POST pagination - pystac-client tests not run, collection is undefined"


def validate_item_search_intersects(
    search_url: str,
    collection: str,
    methods: Set[Method],
    errors: Errors,
    geometry: str,
    r_session: Session,
) -> None:
    # Validate that these GeoJSON Geometry types are accepted
    intersects_params = [
        point,
        linestring,
        polygon,
        polygon_with_hole,
        multipoint,
        multilinestring,
        multipolygon,
        geometry_collection,
    ]

    for param in intersects_params:
        if Method.GET in methods:
            _, body, resp_headers = retrieve(
                Method.GET,
                search_url,
                errors,
                Context.ITEM_SEARCH,
                r_session=r_session,
                params={"intersects": json.dumps(param)},
            )

        if Method.POST in methods:
            _, body, _ = retrieve(
                Method.POST,
                search_url,
                errors,
                Context.ITEM_SEARCH,
                r_session=r_session,
                body={"intersects": param},
            )

    intersects_shape = shape(json.loads(geometry))

    if Method.GET in methods:
        _, body, _ = retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            params={"collections": collection, "intersects": geometry},
            r_session=r_session,
        )

        if body:
            if not body.get("features"):
                errors += f"[{Context.ITEM_SEARCH}] GET {search_url} Search result for intersects={geometry} returned no results"
            else:
                if any(
                    not intersects_shape.intersects(shape(item.get("geometry", None)))
                    for item in body.get("features", [])
                ):
                    errors += f"[{Context.ITEM_SEARCH}] GET {search_url} Search results for intersects={geometry} do not all intersect"

    if Method.POST in methods:
        _, item_collection, _ = retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            body={"collections": [collection], "intersects": geometry},
            r_session=r_session,
        )
        if not item_collection or not item_collection.get("features"):
            errors += f"[{Context.ITEM_SEARCH}] POST Search result for intersects={geometry} returned no results"
        else:
            for item in item_collection.get("features", []):
                if not intersects_shape.intersects(shape(item.get("geometry"))):
                    errors += f"[{Context.ITEM_SEARCH}] POST Search result for intersects={geometry}, does not intersect {item.get('geometry')}"


def validate_item_search_bbox(
    search_url: str, methods: Set[Method], errors: Errors, r_session: Session
) -> None:
    bbox_list = [100.0, 0.0, 105.0, 1.0]

    if Method.GET in methods:
        _, body, resp_headers = retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            params={"bbox": ",".join([str(x) for x in bbox_list])},
            r_session=r_session,
        )

    if Method.POST in methods:
        # Valid POST query
        _, body, resp_headers = retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            body={"bbox": bbox_list},
            r_session=r_session,
        )

    bbox_list = [100.0, 0.0, 0.0, 105.0, 1.0, 1.0]

    if Method.GET in methods:
        _, body, resp_headers = retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            params={"bbox": ",".join([str(x) for x in bbox_list])},
            r_session=r_session,
        )

    if Method.POST in methods:
        # Valid POST query
        _, body, resp_headers = retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            body={"bbox": bbox_list},
            r_session=r_session,
        )

    if Method.GET in methods:
        retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            status_code=400,
            params={"bbox": "[100.0, 0.0, 105.0, 1.0]"},
            r_session=r_session,
            additional="invalid GET query with coordinates in brackets",
        )

    if Method.POST in methods:
        retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            status_code=400,
            body={"bbox": "100.0, 0.0, 105.0, 1.0"},
            r_session=r_session,
            additional="invalid POST search with CSV string of coordinates",
        )

    if Method.GET in methods:
        retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            status_code=400,
            params={"bbox": "100.0, 1.0, 105.0, 0.0"},
            r_session=r_session,
            additional="bbox (lat 1 > lat 2)",
        )

    if Method.POST in methods:
        retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            status_code=400,
            body={"bbox": [100.0, 1.0, 105.0, 0.0]},
            r_session=r_session,
            additional="bbox (lat 1 > lat 2)",
        )

    # Invalid bbox - 1, 2, 3, 5, and 7 element array
    for bbox in [[0], [0, 0], [0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1]]:
        if Method.GET in methods:
            retrieve(
                Method.GET,
                search_url,
                errors,
                Context.ITEM_SEARCH,
                status_code=400,
                params={"bbox": ",".join(str(c) for c in bbox)},
                r_session=r_session,
                additional="invalid bbox coordinate count",
            )

        if Method.POST in methods:
            retrieve(
                Method.POST,
                search_url,
                errors,
                Context.ITEM_SEARCH,
                status_code=400,
                body={"bbox": bbox},
                r_session=r_session,
                additional="invalid bbox coordinate count",
            )


def validate_item_search_limit(
    search_url: str, methods: Set[Method], errors: Errors, r_session: Session
) -> None:
    valid_limits = [1, 2, 10, 10000, 100000, 1000000]
    for limit in valid_limits:
        params = {"limit": limit}
        if Method.GET in methods:
            _, body, _ = retrieve(
                Method.GET,
                search_url,
                errors,
                Context.ITEM_SEARCH,
                params=params,
                r_session=r_session,
            )
            if body:
                items = body.get("items")
                if items and len(items) <= 1:
                    errors += f"[{Context.ITEM_SEARCH}] POST Search with {params} returned fewer than 1 result"

        if Method.POST in methods:
            _, body, _ = retrieve(
                Method.POST,
                search_url,
                errors,
                Context.ITEM_SEARCH,
                body=params,
                r_session=r_session,
            )
            if body:
                items = body.get("items")
                if items and len(items) <= 1:
                    errors += f"[{Context.ITEM_SEARCH}] POST Search with {params} returned fewer than 1 result"

    invalid_limits = [-1]
    for limit in invalid_limits:
        params = {"limit": limit}
        if Method.GET in methods:
            _, body, _ = retrieve(
                Method.GET,
                search_url,
                errors,
                Context.ITEM_SEARCH,
                status_code=400,
                params=params,
                r_session=r_session,
            )

        if Method.POST in methods:
            _, body, _ = retrieve(
                Method.POST,
                search_url,
                errors,
                Context.ITEM_SEARCH,
                status_code=400,
                body=params,
                r_session=r_session,
            )

    # todo: pull actual limits from service desc and test them


def _validate_search_ids_request(
    body: Optional[Dict[str, Any]],
    item_ids: List[str],
    method: Method,
    params: Dict[str, Any],
    errors: Errors,
) -> None:
    if items := body.get("features"):  # type: ignore
        if len(items) != len(list(filter(lambda x: x.get("id") in item_ids, items))):
            errors += f"{method} Search with {params} returned items with ids other than specified one"
    else:
        errors += f"{method} Search with {params} returned no 'features' attribute"


def _validate_search_ids_with_ids(
    search_url: str,
    item_ids: List[str],
    methods: Set[Method],
    errors: Errors,
    r_session: Session,
) -> None:
    get_params = {"ids": ",".join(item_ids)}

    if Method.GET in methods:
        _, body, _ = retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            params=get_params,
            r_session=r_session,
        )

        _validate_search_ids_request(
            body,
            item_ids=item_ids,
            method=Method.GET,
            params=get_params,
            errors=errors,
        )

    if Method.POST in methods:
        post_params = {"ids": item_ids}
        _, body, _ = retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            body=post_params,
            r_session=r_session,
        )
        _validate_search_ids_request(
            body,
            item_ids=item_ids,
            method=Method.POST,
            params=post_params,
            errors=errors,
        )


def _validate_search_ids_with_ids_no_override(
    search_url: str,
    item: Dict[str, Any],
    methods: Set[Method],
    errors: Errors,
    r_session: Session,
) -> None:
    bbox = item["bbox"]
    get_params = {
        "ids": item["id"],
        "collections": item["collection"],
        "bbox": f"{bbox[2] + 1},{bbox[3] + 1},{bbox[2] + 2},{bbox[3] + 2}",
    }

    if Method.GET in methods:
        _, body, _ = retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            params=get_params,
            r_session=r_session,
        )
        if body:
            if len(body.get("features", [])) > 0:
                errors += (
                    f"[{Context.ITEM_SEARCH}] GET Search with ids and non-intersecting bbox returned results, indicating "
                    "the ids parameter is overriding the bbox parameter. All parameters are applied equally since "
                    "STAC API 1.0.0-beta.1"
                )

    if Method.POST in methods:
        post_params = {
            "ids": [item["id"]],
            "collections": [item["collection"]],
            "bbox": [bbox[2] + 1, bbox[3] + 1, bbox[2] + 2, bbox[3] + 2],
        }

        _, body, _ = retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            body=post_params,
            r_session=r_session,
        )

        if body and body.get("features", []):
            errors += (
                f"[{Context.ITEM_SEARCH}] POST Search with ids and non-intersecting bbox returned results, indicating "
                "the ids parameter is overriding the bbox parameter. All parameters are applied equally since "
                "STAC API 1.0.0-beta.1"
            )


def validate_item_search_ids(
    search_url: str,
    methods: Set[Method],
    warnings: Warnings,
    errors: Errors,
    r_session: Session,
) -> None:
    _, body, _ = retrieve(
        Method.GET,
        search_url,
        errors,
        Context.ITEM_SEARCH,
        params={"limit": 2},
        r_session=r_session,
    )

    items = body.get("features")  # type: ignore
    if items and len(items) >= 2:
        _validate_search_ids_with_ids(
            search_url, [items[0].get("id")], methods, errors, r_session
        )
        _validate_search_ids_with_ids(
            search_url,
            [items[0].get("id"), items[1].get("id")],
            methods,
            errors,
            r_session,
        )
        _validate_search_ids_with_ids(
            search_url, [i["id"] for i in items], methods, errors, r_session
        )
    else:
        warnings += f"[{Context.ITEM_SEARCH}] GET Search with no parameters returned < 2 results"


def validate_item_search_ids_does_not_override_all_other_params(
    search_url: str,
    methods: Set[Method],
    collection: str,
    warnings: Warnings,
    errors: Errors,
    r_session: Session,
) -> None:
    # find one item that we can then query by id and a non-intersecting bbox to see if
    # we still get the item as a result
    _, body, _ = retrieve(
        Method.GET,
        f"{search_url}?limit=1&bbox=20,20,21,21&collections={collection}",
        errors,
        Context.ITEM_SEARCH,
        content_type=geojson_mt,
        r_session=r_session,
    )
    if body.get("features"):  # type: ignore
        _validate_search_ids_with_ids_no_override(
            search_url, body["features"][0], methods, errors, r_session  # type: ignore
        )
    else:
        warnings += (
            f"[{Context.ITEM_SEARCH}] GET Search within bbox=20,20,21,21 to validate ids does not override "
            "all other parameters returned 0 results"
        )


def _validate_search_collections_request(
    body: Optional[Dict[str, Any]],
    coll_ids: List[str],
    method: Method,
    params: Dict[str, Any],
    errors: Errors,
) -> None:
    if body:
        items = body.get("features", [])
        if len(items) != len(
            list(filter(lambda x: x.get("collection") in coll_ids, items))
        ):
            errors += f"{method} Search with {params} returned items with ids other than specified one"


def _validate_search_collections_with_ids(
    search_url: str,
    coll_ids: List[str],
    methods: Set[Method],
    errors: Errors,
    r_session: Session,
) -> None:
    if Method.GET in methods:
        get_params = {"collections": ",".join(coll_ids)}
        _, body, _ = retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            params=get_params,
            r_session=r_session,
        )
        _validate_search_collections_request(
            body,
            coll_ids=coll_ids,
            method=Method.GET,
            params=get_params,
            errors=errors,
        )

    if Method.POST in methods:
        post_params = {"collections": coll_ids}
        _, body, _ = retrieve(
            Method.POST,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            body=post_params,
            r_session=r_session,
        )
        _validate_search_collections_request(
            body,
            coll_ids=coll_ids,
            method=Method.POST,
            params=post_params,
            errors=errors,
        )


def validate_item_search_collections(
    search_url: str,
    collections_url: Optional[str],
    methods: Set[Method],
    errors: Errors,
    r_session: Session,
) -> None:
    collection_ids = None
    if collections_url:
        _, collections_entity, _ = retrieve(
            Method.GET,
            collections_url,
            errors,
            Context.ITEM_SEARCH,
            r_session=r_session,
        )

        if not (
            collections_entity
            and (collections := collections_entity.get("collections"))
        ):
            errors += "/collections entity does not contain a 'collections' attribute"
        else:
            collection_ids = [x["id"] for x in collections]
    else:  # if Collections is not implemented, get some from search
        _, body, _ = retrieve(
            Method.GET,
            search_url,
            errors,
            Context.ITEM_SEARCH,
            r_session=r_session,
        )
        if body:
            collection_ids = list({i["collection"] for i in body.get("features", [])})

    if not collection_ids:
        errors += "Not running search validations with collections because could not get collection ids"
    else:
        _validate_search_collections_with_ids(
            search_url, collection_ids, methods, errors, r_session
        )

        for cid in collection_ids:
            _validate_search_collections_with_ids(
                search_url, [cid], methods, errors, r_session
            )

        _validate_search_collections_with_ids(
            search_url,
            list(itertools.islice(collection_ids, 3)),
            methods,
            errors,
            r_session,
        )


def validate_transaction(
    landing_page_body: Dict[str, Any],
    collection: str,
    errors: Errors,
    warnings: Warnings,
    r_session: Session,
    context: Context,
    transaction_collection: Optional[str],
) -> None:
    if not transaction_collection:
        errors += f"[{context}] : cannot validate Transaction Extension because -- transaction-collection is not set"
        return

    # todo: spec should advertise this rather than it just being known

    collections_url = [
        x.get("href") for x in links_by_rel(landing_page_body.get("links"), "data")
    ][0]

    create_url = f"{collections_url}/{transaction_collection}/items"

    item = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "S2A_47XNF_20230423_0_L2A",
        "properties": {
            "eo:cloud_cover": 0.142999,
            "datetime": "2023-04-23T06:47:03.048000Z",
            "remove_me": "x",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [98.99921502683155, 77.47731704519707],
                    [103.52623455002798, 77.4393697038252],
                    [103.28971588368059, 76.73571563595313],
                    [102.04264523308017, 76.47502013800678],
                    [98.99927124149437, 76.4933939950606],
                    [98.99921502683155, 77.47731704519707],
                ]
            ],
        },
        "assets": {
            "aot": {
                "href": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/47/X/NF/2023/4/S2A_47XNF_20230423_0_L2A/AOT.tif",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "title": "Aerosol optical thickness (AOT)",
                "roles": ["data", "reflectance"],
            },
        },
        "bbox": [
            98.99921502683155,
            76.47502013800678,
            103.52623455002798,
            77.47731704519707,
        ],
        "stac_extensions": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
        ],
        "collection": transaction_collection,
    }

    item_url = f"{create_url}/{item['id']}"

    # DELETE the item if it exists
    retrieve(
        Method.DELETE,
        item_url,
        status_code=204,
        content_type="undefined",
        errors=errors,
        context=context,
        r_session=r_session,
    )

    # POST create
    # todo: test ItemCollection creation
    retrieve(
        Method.POST,
        create_url,
        body=item,
        status_code=201,
        errors=errors,
        context=context,
        r_session=r_session,
    )

    time.sleep(2)

    retrieve(
        Method.GET,
        item_url,
        errors=errors,
        context=context,
        r_session=r_session,
        content_type=geojson_mt,
    )

    # PUT - change and add a field
    item_put = copy.deepcopy(item)
    item_put["properties"]["eo:cloud_cover"] = "3.14"
    item_put["properties"]["foo"] = "bar"
    item_put["properties"].pop("remove_me")

    retrieve(
        Method.PUT,
        item_url,
        body=item_put,
        errors=errors,
        context=context,
        r_session=r_session,
        status_code=204,
        content_type="undefined",
    )

    time.sleep(2)

    _, body, _ = retrieve(
        Method.GET,
        item_url,
        errors=errors,
        context=context,
        r_session=r_session,
        content_type=geojson_mt,
    )

    if body.get("properties", {}).get("datetime") != item["properties"]["datetime"]:
        errors += f"[{context}] : PUT - datetime value did not match"

    if body["properties"]["eo:cloud_cover"] != item_put["properties"]["eo:cloud_cover"]:
        errors += f"[{context}] : PUT - eo:cloud_cover value did not match"

    if body["properties"]["foo"] != item_put["properties"]["foo"]:
        errors += f"[{context}] : PUT - property 'foo' was not added"

    if body["properties"].get("remove_me"):
        errors += f"[{context}] : PUT - field 'remove_me' was not removed"

    # PATCH - add one field, modify another field
    item_patch = {"properties": {"eo:cloud_cover": "12.4", "a_patch_field": "bar"}}

    retrieve(
        Method.PATCH,
        item_url,
        body=item_patch,
        errors=errors,
        context=context,
        r_session=r_session,
        status_code=204,
        content_type="undefined",
    )

    time.sleep(2)

    _, body, _ = retrieve(
        Method.GET,
        item_url,
        errors=errors,
        context=context,
        r_session=r_session,
        content_type=geojson_mt,
    )

    if body["properties"]["datetime"] != item["properties"]["datetime"]:
        errors += f"[{context}] : PUT - datetime value did not match"

    if (
        body["properties"]["eo:cloud_cover"]
        != item_patch["properties"]["eo:cloud_cover"]
    ):
        errors += f"[{context}] : PUT - eo:cloud_cover value did not match"

    if body["properties"]["a_patch_field"] != item_patch["properties"]["a_patch_field"]:
        errors += f"[{context}] : PUT - property 'foo' was not added"

    # DELETE

    retrieve(
        Method.DELETE,
        item_url,
        status_code=204,
        errors=errors,
        context=context,
        r_session=r_session,
        content_type="undefined",
    )

    time.sleep(2)

    retrieve(
        Method.GET,
        item_url,
        status_code=404,
        errors=errors,
        context=context,
        r_session=r_session,
    )


def validate_sort(
    landing_page_body: Dict[str, Any],
    collection: str,
    errors: Errors,
    warnings: Warnings,
    r_session: Session,
    context: Context,
    query_config: QueryConfig,
) -> None:
    limit = 100

    search_method_to_url: dict[Method, str] = {
        Method[x.get("method", "GET")]: x.get("href")
        for x in links_by_rel(landing_page_body.get("links"), "search")
    }

    # ascending
    if Method.GET in search_method_to_url:
        for sortby in ["properties.datetime", "+properties.datetime"]:
            _, body, _ = retrieve(
                Method.GET,
                search_method_to_url[Method.GET],
                params={
                    "sortby": sortby,
                    "limit": limit,
                    "collections": collection,
                },
                errors=errors,
                context=context,
                r_session=r_session,
            )

            if not len(body["features"]):
                errors += (
                    f"[{context}] : GET search with Sort '{sortby}' had no results"
                )

            datetimes = [f["properties"]["datetime"] for f in body["features"]]
            sorted_datetimes = copy.deepcopy(datetimes)
            sorted_datetimes.sort()

            if datetimes != sorted_datetimes:
                errors += f"[{context}] : GET search with Sort '{sortby}' was not sorted in ascending order {datetimes} {sorted_datetimes}"

    if Method.POST in search_method_to_url:
        sortby_json = [{"field": "properties.datetime", "direction": "asc"}]
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "sortby": sortby_json,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Sort '{json.dumps(sortby_json)}' had no results"

        datetimes = [f["properties"]["datetime"] for f in body["features"]]
        sorted_datetimes = copy.deepcopy(datetimes)
        sorted_datetimes.sort()

        if datetimes != sorted_datetimes:
            errors += f"[{context}] : POST search with Sort '{json.dumps(sortby_json)}' was not sorted in ascending order"

    # descending
    if Method.GET in search_method_to_url:
        sortby = "-properties.datetime"
        _, body, _ = retrieve(
            Method.GET,
            search_method_to_url[Method.GET],
            params={
                "sortby": sortby,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : GET search with Sort '{sortby}' had no results"

        datetimes = [f["properties"]["datetime"] for f in body["features"]]
        sorted_datetimes = copy.deepcopy(datetimes)
        sorted_datetimes.sort(reverse=True)

        if datetimes != sorted_datetimes:
            errors += f"[{context}] : GET search with Sort '{sortby}' was not sorted in descending order {datetimes} {sorted_datetimes}"

    if Method.POST in search_method_to_url:
        sortby_json = [{"field": "properties.datetime", "direction": "desc"}]
        retrieve(
            Method.POST,
            search_method_to_url[Method.POST],
            body={
                "sortby": sortby_json,
                "limit": limit,
                "collections": collection,
            },
            errors=errors,
            context=context,
            r_session=r_session,
        )

        if not len(body["features"]):
            errors += f"[{context}] : POST search with Sort '{json.dumps(sortby_json)}' had no results"

        datetimes = [f["properties"]["datetime"] for f in body["features"]]
        sorted_datetimes = copy.deepcopy(datetimes)
        sorted_datetimes.sort(reverse=True)

        if datetimes != sorted_datetimes:
            errors += f"[{context}] : POST search with Sort '{json.dumps(sortby_json)}' was not sorted in descending order"
