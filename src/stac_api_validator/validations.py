"""Validations module."""
import itertools
import json
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Pattern
from typing import Tuple

import requests
import yaml
from pystac import STACValidationError
from pystac_client import Client
from shapely.geometry import shape

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


cc_core_regex = re.compile(r"https://api\.stacspec\.org/.+/core")
cc_browseable_regex = re.compile(r"https://api\.stacspec\.org/.+/browseable")
cc_children_regex = re.compile(r"https://api\.stacspec\.org/.+/children")

cc_collections_regex = re.compile(r"https://api\.stacspec\.org/.+/collections")

cc_features_regex = re.compile(r"https://api\.stacspec\.org/.+/ogcapi-features")
cc_features_transaction_regex = re.compile(
    r"https://api\.stacspec\.org/.+/ogcapi-features/extensions/transaction"
)
cc_features_fields_regex = re.compile(
    r"https://api\.stacspec\.org/.+/ogcapi-features#fields"
)
cc_features_context_regex = re.compile(
    r"https://api\.stacspec\.org/.+/ogcapi-features#context"
)
cc_features_sort_regex = re.compile(
    r"https://api\.stacspec\.org/.+/ogcapi-features#sort"
)
cc_features_query_regex = re.compile(
    r"https://api\.stacspec\.org/.+/ogcapi-features#query"
)
cc_features_filter_regex = re.compile(
    r"https://api\.stacspec\.org/.+/ogcapi-features#filter"
)

cc_item_search_regex = re.compile(r"https://api\.stacspec\.org/.+/item-search")

cc_item_search_fields_regex = re.compile(
    r"https://api\.stacspec\.org/.+/item-search#fields"
)
cc_item_search_context_regex = re.compile(
    r"https://api\.stacspec\.org/.+/item-search#context"
)
cc_item_search_sort_regex = re.compile(
    r"https://api\.stacspec\.org/.+/item-search#sort"
)
cc_item_search_query_regex = re.compile(
    r"https://api\.stacspec\.org/.+/item-search#query"
)
cc_item_search_filter_regex = re.compile(
    r"https://api\.stacspec\.org/.+/item-search#filter"
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


def validate_api(
    root_url: str,
    post: bool,
    conformance_classes: List[str],
    collection: Optional[str],
    geometry: Optional[str],
) -> Tuple[List[str], List[str]]:
    warnings: List[str] = []
    errors: List[str] = []

    root = requests.get(root_url)

    # todo: handle connection exception, etc.
    if root.status_code != 200:
        errors.append(f"root URL {root_url} returned status code {root.status_code}")
        return warnings, errors

    root_body = root.json()

    conforms_to = root_body.get("conformsTo", [])
    if not conforms_to:
        errors.append(
            "/ : 'conformsTo' field must be defined and non-empty. This field is required as of 1.0.0."
        )

    if not root_body.get("links"):
        errors.append("/ : 'links' field must be defined and non-empty.")

    if "core" in conformance_classes and not any(
        cc_core_regex.fullmatch(x) for x in conforms_to
    ):
        errors.append(
            "/: Core configured for validation, but not contained in 'conformsTo'"
        )

    if "browseable" in conformance_classes and not any(
        cc_browseable_regex.fullmatch(x) for x in conforms_to
    ):
        errors.append(
            "/: Browseable configured for validation, but not contained in 'conformsTo'"
        )

    if "children" in conformance_classes and not any(
        cc_children_regex.fullmatch(x) for x in conforms_to
    ):
        errors.append(
            "/: Children configured for validation, but not contained in 'conformsTo'"
        )

    if "collections" in conformance_classes and not supports_collections(conforms_to):
        errors.append(
            "/: Collections configured for validation, but not contained in 'conformsTo'"
        )

        if collection is None:
            errors.append(
                "/: Collections configured for validation, but `--collection` parameter not specified"
            )

    if "features" in conformance_classes and not supports_features(conforms_to):
        errors.append(
            "/: Features configured for validation, but not contained in 'conformsTo'"
        )
        if collection is None:
            errors.append(
                "/: Features configured for validation, but `--collection` parameter not specified"
            )

    if "item-search" in conformance_classes:
        if not any(cc_item_search_regex.fullmatch(x) for x in conforms_to):
            errors.append(
                "/: Item Search configured for validation, but not contained in 'conformsTo'"
            )
        if collection is None:
            errors.append(
                "/: Item Search configured for validation, but `--collection` parameter not specified"
            )
        if geometry is None:
            errors.append(
                "/: Item Search configured for validation, but `--geometry` parameter not specified"
            )

    # fail fast if there are errors with conformance or links so far
    if errors:
        return warnings, errors

    print("STAC API - Core conformance class found.")
    validate_core(root_body, warnings, errors)

    if "browseable" in conformance_classes:
        print("STAC API - Browseable conformance class found.")
        validate_browseable(root_body, warnings, errors)

    if "children" in conformance_classes:
        print("STAC API - Children conformance class found.")
        validate_children(root_body, warnings, errors)

    if "collections" in conformance_classes:
        print("STAC API - Collections conformance class found.")
        validate_collections(root_body, collection, warnings, errors)  # type:ignore

    if "features" in conformance_classes:
        print("STAC API - Features conformance class found.")
        validate_collections(root_body, collection, warnings, errors)  # type:ignore
        validate_features(
            root_body, conforms_to, collection, warnings, errors  # type:ignore
        )

    if "item-search" in conformance_classes:
        print("STAC API - Item Search conformance class found.")
        validate_item_search(
            root_url=root_url,
            root_body=root_body,
            post=post,
            collection=collection,  # type:ignore
            conforms_to=conforms_to,
            warnings=warnings,
            errors=errors,
            geometry=geometry,  # type:ignore
            conformance_classes=conformance_classes,
        )

    if not errors:
        try:
            catalog = Client.open(root_url)
            catalog.validate()
            for child in catalog.get_children():
                child.validate()
        except STACValidationError as e:
            errors.append(f"pystac error: {str(e)}")

    return warnings, errors


def link_by_rel(
    links: Optional[List[Dict[str, str]]], rel: str
) -> Optional[Dict[str, str]]:
    if not links:
        return None
    else:
        return next((link for link in links if link.get("rel") == rel), None)


def validate_core(
    root_body: Dict[str, Any], warnings: List[str], errors: List[str]
) -> None:
    links = root_body.get("links")

    if not (root := link_by_rel(links, "root")):
        errors.append("/ : Link[rel=root] must exist")
    else:
        if root.get("type") != "application/json":
            errors.append("root type is not application/json")

    if not (_self := link_by_rel(links, "self")):
        warnings.append("/ : Link[rel=self] must exist")
    else:
        if _self.get("type") != "application/json":
            errors.append("self type is not application/json")

    if not (service_desc := link_by_rel(links, "service-desc")):
        errors.append("/ : Link[rel=service-desc] must exist")
    else:
        if not (service_desc_type := service_desc.get("type")):
            errors.append("/ : Link[rel=service-desc] must have a type defined")
        else:
            r_service_desc = requests.get(
                service_desc["href"], headers={"Accept": service_desc_type}
            )

            if not r_service_desc.status_code == 200:
                errors.append("/ : Link[service-desc] must return 200")
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
                errors.append(
                    f"service-desc ({service_desc}): media type used in Accept header must get response with same "
                    f"Content-Type header: used '{service_desc_type}', got '{ct}'"
                )

    if not (service_doc := link_by_rel(links, "service-doc")):
        warnings.append("/ : Link[rel=service-doc] should exist")
    else:
        if service_doc.get("type") != "text/html":
            errors.append("service-doc type is not text/html")

        r_service_doc = requests.get(service_doc["href"])

        if not (r_service_doc.status_code == 200):
            errors.append("/ : Link[service-doc] must return 200")

        if (ct := r_service_doc.headers.get("content-type", "")).startswith(
            "text/html"
        ):
            pass
        else:
            errors.append(
                f"service-doc ({service_doc}): must have content-type header 'text/html', actually '{ct}'"
            )


def validate_browseable(
    root_body: Dict[str, Any], warnings: List[str], errors: List[str]
) -> None:
    print("Browseable validation is not yet implemented.")


def validate_children(
    root_body: Dict[str, Any], warnings: List[str], errors: List[str]
) -> None:
    print("Children validation is not yet implemented.")


def validate_collections(
    root_body: Dict[str, Any], collection: str, warnings: List[str], errors: List[str]
) -> None:
    print("WARNING: Collections validation is not yet fully implemented.")

    if not (data_link := link_by_rel(root_body["links"], "data")):
        errors.append("[Collections] /: Link[rel=data] must href /collections")
    else:
        collection_url = f"{data_link['href']}/{collection}"
        r = requests.get(collection_url)
        if r.status_code != 200:
            errors.append(
                f"[Collections] GET {collection_url} failed with status code {r.status_code}"
            )
        else:
            try:
                r.json()
                # todo: validate this
            except json.decoder.JSONDecodeError:
                errors.append(
                    f"[Collections] GET {collection_url} returned non-JSON value"
                )

        collection_url = f"{data_link['href']}/non-existent-collection"
        r = requests.get(collection_url)
        if r.status_code != 404:
            errors.append(
                f"[Collections] GET {collection_url} (non-existent collection) returned status code {r.status_code} instead of 404"
            )


def validate_features(
    root_body: Dict[str, Any],
    conforms_to: List[str],
    collection: str,
    warnings: List[str],
    errors: List[str],
) -> None:
    print("WARNING: Features validation is not yet fully implemented.")

    if conforms_to and (
        req_ccs := [
            x
            for x in conforms_to
            if x.startswith("http://www.opengis.net/spec/ogcapi-features-1/1.0/req/")
        ]
    ):
        warnings.append(
            f"/ : 'conformsTo' contains OGC API conformance classes using 'req' instead of 'conf': {req_ccs}."
        )

    if "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core" not in conforms_to:
        warnings.append(
            "STAC APIs conforming to the Features conformance class may also advertise the OGC API - Features Part 1 conformance class 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core'"
        )

    if (
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
        not in conforms_to
    ):
        warnings.append(
            "STAC APIs conforming to the Features conformance class may also advertise the OGC API - Features Part 1 conformance class 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson'"
        )

    # todo: add this one somewhere
    #  "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",

    root_links = root_body.get("links")
    conformance = link_by_rel(root_links, "conformance")
    if not (
        conformance is not None and conformance.get("href", "").endswith("/conformance")
    ):
        errors.append("/ Link[rel=conformance] must href /conformance")

    if conformance:
        r_conformance = requests.get(conformance["href"])

        if not (r_conformance.status_code == 200):
            errors.append("conformance must return 200")

        if (ct := r_conformance.headers.get("content-type", "")).split(";")[
            0
        ] == "application/json":
            pass
        else:
            errors.append(
                f"conformance ({conformance}): must have content-type header 'application/json', actually '{ct}'"
            )

        try:
            conformance_json = r_conformance.json()
            if not (
                set(root_body.get("conformsTo", []))
                == set(conformance_json["conformsTo"])
            ):
                warnings.append(
                    "Landing Page conforms to and conformance conformsTo must be the same",
                )
        except json.decoder.JSONDecodeError:
            errors.append(
                f"service-desc ({conformance}): must return JSON, instead got non-JSON text"
            )

        # this is hard to figure out, since it's likely a mistake, but most apis can't undo it for
        # backwards-compat reasons
        if not (link_by_rel(root_links, "collections") is None):
            warnings.append(
                "/ Link[rel=collections] is a non-standard relation. Use Link[rel=data instead]"
            )

        # todo: validate items exists

        if not (collections_url := link_by_rel(root_links, "data")):
            errors.append("/: Link[rel=data] must href /collections")
        else:
            item_url = f"{collections_url['href']}/{collection}/items/non-existent-item"
            r = requests.get(item_url)
            if r.status_code != 404:
                errors.append(
                    f"[Features] GET {item_url} (non-existent item) returned status code {r.status_code} instead of 404"
                )

    # if any(cc_features_fields_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Features - Fields extension conformance class found.")
    #
    # if any(cc_features_context_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Features - Context extension conformance class found.")
    #
    # if any(cc_features_sort_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Features - Sort extension conformance class found.")
    #
    # if any(cc_features_query_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Features - Query extension conformance class found.")
    #
    # if any(cc_features_filter_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Features - Filter extension conformance class found.")

    if any(cc_features_filter_regex.fullmatch(x) for x in conforms_to):
        print("STAC API - Features - Filter extension conformance class found.")
        validate_features_filter(
            root_body=root_body,
            collection=collection,
            errors=errors,
        )


def validate_item_search(
    root_url: str,
    root_body: Dict[str, Any],
    post: bool,
    collection: str,
    conforms_to: List[str],
    warnings: List[str],
    errors: List[str],
    geometry: str,
    conformance_classes: List[str],
) -> None:
    links = root_body.get("links")
    search = link_by_rel(links, "search")
    if not search:
        errors.append("/: Link[rel=search] must exist when Item Search is implemented")
        return

    # Collections may not be implemented, so set to None
    # and later get some collection ids another way
    if links and (collections := link_by_rel(links, "data")):
        collections_url = collections.get("href")
    else:
        collections_url = None

    search_url = search["href"]
    r = requests.get(search_url)
    content_type = r.headers.get("content-type")
    if content_type == geojson_mt or content_type == geojson_charset_mt:
        pass
    else:
        errors.append(
            f"Search ({search_url}): must have content-type header '{geojson_mt}', actually '{content_type}'"
        )

    if not (r.status_code == 200):
        errors.append(f"Search({search_url}): must return 200")

    # todo: validate geojson, not just json
    try:
        r.json()
    except json.decoder.JSONDecodeError:
        errors.append(
            f"Search ({search_url}): must return JSON, instead got non-JSON text"
        )

    validate_item_search_limit(search_url, post, errors)
    validate_item_search_bbox_xor_intersects(search_url, post, errors)
    validate_item_search_bbox(search_url, post, errors)
    validate_item_search_datetime(search_url, warnings, errors)
    validate_item_search_ids(search_url, post, warnings, errors)
    validate_item_search_ids_does_not_override_all_other_params(
        search_url, post, collection, warnings, errors
    )
    validate_item_search_collections(search_url, collections_url, post, errors)
    validate_item_search_intersects(
        search_url=search_url,
        collection=collection,
        post=post,
        errors=errors,
        geometry=geometry,
    )

    # if any(cc_item_search_fields_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Item Search - Fields extension conformance class found.")
    #
    # if any(cc_item_search_context_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Item Search - Context extension conformance class found.")
    #
    # if any(cc_item_search_sort_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Item Search - Sort extension conformance class found.")
    #
    # if any(cc_item_search_query_regex.fullmatch(x) for x in conforms_to):
    #     print("STAC API - Item Search - Query extension conformance class found.")
    #

    if any(
        x.endswith("item-search#filter:basic-cql")
        or x.endswith("item-search#filter:cql-json")
        or x.endswith("item-search#filter:cql-text")
        or x.endswith("item-search#filter:filter")
        for x in conforms_to
    ):
        warnings.append(
            "[Filter Ext] /: pre-1.0.0-rc.1 Filter Extension conformance classes are advertised."
        )

    if "filter" in conformance_classes and any(
        cc_item_search_filter_regex.fullmatch(x)
        or x.endswith("item-search#filter:filter")
        for x in conforms_to
    ):
        print("STAC API - Item Search - Filter extension conformance class found.")

        validate_item_search_filter(
            root_url=root_url,
            root_body=root_body,
            search_url=search_url,
            collection=collection,
            warnings=warnings,
            errors=errors,
        )


def validate_filter_queryables(
    queryables_url: str,
    conformance_class: str,
    errors: List[str],
) -> None:
    r = requests.get(queryables_url, headers={"Accept": "application/schema+json"})

    if r.status_code != 200:
        errors.append(
            f"[{conformance_class} - Filter Ext] Queryables '{queryables_url}' returned status code {r.status_code}"
        )
    else:
        if (ct := r.headers.get("Content-Type")) != "application/schema+json":
            errors.append(
                f"[{conformance_class} - Filter Ext] Queryables '{queryables_url}' returned Content-Type header '{ct}', must return 'application/schema+json'"
            )
        try:
            json_schemas = [
                "https://json-schema.org/draft/2019-09/schema",
                "http://json-schema.org/draft-07/schema#",
            ]
            queryables_schema = r.json()
            if queryables_schema.get("$schema") not in json_schemas:
                errors.append(
                    f"[{conformance_class} - Filter Ext] Queryables '{queryables_url}' '$schema' value invalid, must be one of: '{','.join(json_schemas)}'"
                )

            if queryables_schema.get("$id") != queryables_url:
                errors.append(
                    f"[{conformance_class} - Filter Ext] Queryables '{queryables_url}' '$id' value invalid, must be same as queryables url"
                )

            if queryables_schema.get("type") != "object":
                errors.append(
                    f"[{conformance_class} Filter Ext] Queryables '{queryables_url}' 'type' value invalid, must be 'object'"
                )
        except json.decoder.JSONDecodeError:
            errors.append(
                f"[{conformance_class} Filter Ext] Queryables '{queryables_url}' returned non-JSON response"
            )


def validate_features_filter(
    root_body: Dict[str, Any],
    collection: str,
    errors: List[str],
) -> None:
    print("WARNING: Features - Filter Ext validation is not yet fully implemented.")

    if not (collections_link := link_by_rel(root_body["links"], "data")):
        errors.append("[Features] / : 'data' link relation missing")
    else:
        collection_url = f"{collections_link['href']}/{collection}"

        r = requests.get(collection_url)
        if r.status_code != 200:
            errors.append(
                f"[Featues - Filter Ext] GET {collection_url} returned status code {r.status_code}"
            )

        if not (
            queryables_link := link_by_rel(
                r.json()["links"], "http://www.opengis.net/def/rel/ogc/1.0/queryables"
            )
        ):
            errors.append(
                f"[Features - Filter Ext] {collection_url} : 'http://www.opengis.net/def/rel/ogc/1.0/queryables' (Queryables) link relation missing"
            )

        validate_filter_queryables(
            queryables_url=(queryables_link and queryables_link["href"])
            or f"{collection_url}/queryables",
            conformance_class="Features",
            errors=errors,
        )


# Assumes id, collection, geometry, and datetime are available
def validate_item_search_filter(
    root_url: str,
    root_body: Dict[str, Any],
    search_url: str,
    collection: str,
    warnings: List[str],
    errors: List[str],
) -> None:
    if not (
        queryables_link := link_by_rel(
            root_body["links"], "http://www.opengis.net/def/rel/ogc/1.0/queryables"
        )
    ):
        errors.append(
            "[Item Search Filter Ext] / : 'http://www.opengis.net/def/rel/ogc/1.0/queryables' (Queryables) link relation missing"
        )

    validate_filter_queryables(
        queryables_url=(queryables_link and queryables_link["href"])
        or f"{root_url}/queryables",
        conformance_class="Item Search",
        errors=errors,
    )

    conforms_to = root_body["conformsTo"]

    cql2_text_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/cql2-text" in conforms_to
    ) or (
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter:cql-text"
        in conforms_to
    )

    if cql2_text_supported:
        print("CQL2 - CQL2-Text conformance class found.")

    cql2_json_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/cql2-json" in conforms_to
    ) or (
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter:cql-json"
        in conforms_to
    )

    if cql2_json_supported:
        print("CQL2 - CQL2-JSON conformance class found.")

    basic_cql2_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/basic-cql2" in conforms_to
    ) or (
        "https://api.stacspec.org/v1.0.0-rc.1/item-search#filter:basic-cql"
        in conforms_to
    )

    if basic_cql2_supported:
        print("CQL2 - Basic CQL2 conformance class found.")

    advanced_comparison_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/advanced-comparison-operators"
        in conforms_to
    )
    if advanced_comparison_operators_supported:
        print("CQL2 - Advanced Comparison Operators conformance class found.")

    basic_spatial_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/basic-spatial-operators"
        in conforms_to
    )

    if basic_spatial_operators_supported:
        print("CQL2 - Basic Spatial Operators conformance class found.")

    temporal_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/temporal-operators" in conforms_to
    )

    if temporal_operators_supported:
        print("CQL2 - Temporal Operators conformance class found.")

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
        item = requests.get(f"{search_url}?collections={collection}").json()[
            "features"
        ][0]

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
        r = requests.get(
            search_url,
            params={"limit": 1, "filter-lang": "cql2-text", "filter": f_text},  # type: ignore
        )
        if not (r.status_code == 200):
            errors.append(
                f"[Item Search Filter Ext] GET {f_text} returned status code {r.status_code}"
            )

    for f_json in filter_jsons:
        r = requests.post(
            search_url, json={"limit": 1, "filter-lang": "cql2-json", "filter": f_json}
        )
        if r.status_code != 200:
            errors.append(
                f"[Item Search Filter Ext] POST {f_json} returned status code {r.status_code}"
            )


def validate_item_search_datetime(
    search_url: str, warnings: List[str], errors: List[str]
) -> None:
    # find an Item and try to use its datetime value in a query
    r = requests.get(search_url)
    dt = r.json()["features"][0]["properties"]["datetime"]  # todo: if no results, fail
    r = requests.get(search_url, params={"datetime": dt})
    if r.status_code != 200:
        errors.append(
            f"GET Search with datetime={dt} extracted from an Item returned status code {r.status_code}"
        )
    elif len(r.json()["features"]) == 0:
        errors.append(
            f"GET Search with datetime={dt} extracted from an Item returned no results."
        )

    for dt in valid_datetimes:
        r = requests.get(search_url, params={"datetime": dt})
        if r.status_code != 200:
            errors.append(
                f"GET Search with datetime={dt} returned status code {r.status_code}"
            )
            continue
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors.append(f"GET Search with datetime={dt} returned non-json response")

    for dt in invalid_datetimes:
        r = requests.get(search_url, params={"datetime": dt})
        if r.status_code == 200:
            warnings.append(
                f"GET Search with datetime={dt} returned status code 200 instead of 400"
            )
            continue
        if r.status_code != 400:
            errors.append(
                f"GET Search with datetime={dt} returned status code {r.status_code} instead of 400"
            )
            continue

    # todo: POST


def validate_item_search_bbox_xor_intersects(
    search_url: str, post: bool, errors: List[str]
) -> None:
    r = requests.get(
        search_url, params={"bbox": "0,0,1,1", "intersects": json.dumps(polygon)}
    )
    if r.status_code != 400:
        errors.append(
            f"GET Search with bbox and intersects returned status code {r.status_code}"
        )

    if post:
        # Valid POST query
        r = requests.post(
            search_url, json={"bbox": [0, 0, 1, 1], "intersects": polygon}
        )
        if r.status_code != 400:
            errors.append(
                f"POST Search with bbox and intersects returned status code {r.status_code}"
            )


def validate_item_search_intersects(
    search_url: str, collection: str, post: bool, errors: List[str], geometry: str
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
        # Valid GET query
        r = requests.get(search_url, params={"intersects": json.dumps(param)})
        if r.status_code != 200:
            errors.append(
                f"GET Search with intersects={param} returned status code {r.status_code}"
            )
        else:
            try:
                r.json()
            except json.decoder.JSONDecodeError:
                errors.append(
                    f"GET Search with intersects={param} returned non-json response: {r.text}"
                )
        if post:
            # Valid POST query
            r = requests.post(search_url, json={"intersects": param})
            if r.status_code != 200:
                errors.append(
                    f"POST Search with intersects:{param} returned status code {r.status_code}"
                )
            else:
                try:
                    r.json()
                except json.decoder.JSONDecodeError:
                    errors.append(
                        f"POST Search with intersects:{param} returned non-json response: {r.text}"
                    )

    intersects_shape = shape(json.loads(geometry))

    # Validate GET query
    r = requests.get(
        search_url,
        params={"collections": collection, "intersects": geometry},
    )
    if r.status_code != 200:
        errors.append(
            f"[Item Search] GET Search with collections={collection}&intersects={geometry} returned status code {r.status_code}"
        )
    else:
        try:
            item_collection = r.json()
            if not len(item_collection["features"]):
                errors.append(
                    f"[Item Search] GET Search result for intersects={geometry} returned no results"
                )
            if any(
                not intersects_shape.intersects(shape(item["geometry"]))
                for item in item_collection["features"]
            ):
                errors.append(
                    f"[Item Search] GET Search results for intersects={geometry} do not all intersect"
                )
        except json.decoder.JSONDecodeError:
            errors.append(
                f"[Item Search] GET Search with intersects={geometry} returned non-json response: {r.text}"
            )

    if post:
        # Validate POST query
        r = requests.post(
            search_url, json={"collections": [collection], "intersects": geometry}
        )
        if r.status_code != 200:
            errors.append(
                f"[Item Search] POST Search with intersects={geometry} returned status code {r.status_code}"
            )
        else:
            try:
                item_collection = r.json()
                if not len(item_collection["features"]):
                    errors.append(
                        f"[Item Search] POST Search result for intersects={geometry} returned no results"
                    )
                for item in item_collection["features"]:
                    if not intersects_shape.intersects(shape(item["geometry"])):
                        errors.append(
                            f"[Item Search] POST Search result for intersects={geometry}, does not intersect {item['geometry']}"
                        )
            except json.decoder.JSONDecodeError:
                errors.append(
                    f"[Item Search] POST Search with intersects={geometry} returned non-json response: {r.text}"
                )


def validate_item_search_bbox(search_url: str, post: bool, errors: List[str]) -> None:
    # Valid GET query
    param = "100.0,0.0,105.0,1.0"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 200:
        errors.append(
            f"GET Search with bbox={param} returned status code {r.status_code}"
        )
    else:
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors.append(
                f"GET Search with bbox={param} returned non-json response: {r.text}"
            )

    if post:
        # Valid POST query
        param_list = [100.0, 0.0, 105.0, 1.0]
        r = requests.post(search_url, json={"bbox": param_list})
        if r.status_code != 200:
            errors.append(
                f"POST Search with bbox:{param_list} returned status code {r.status_code}"
            )
        else:
            try:
                r.json()
            except json.decoder.JSONDecodeError:
                errors.append(
                    f"POST Search with bbox:{param_list} returned non-json response: {r.text}"
                )

    # Valid 3D GET query
    param = "100.0,0.0,0.0,105.0,1.0,1.0"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 200:
        errors.append(
            f"GET Search with bbox={param} returned status code {r.status_code}"
        )
    else:
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors.append(f"GET with bbox={param} returned non-json response: {r.text}")

    if post:
        # Valid 3D POST query
        param_list = [100.0, 0.0, 0.0, 105.0, 1.0, 1.0]
        r = requests.post(search_url, json={"bbox": param_list})
        if r.status_code != 200:
            errors.append(
                f"POST Search with bbox:{param_list} returned status code {r.status_code}"
            )
        else:
            try:
                r.json()
            except json.decoder.JSONDecodeError:
                errors.append(
                    f"POST with bbox:{param_list} returned non-json response: {r.text}"
                )

    # Invalid GET query with coordinates in brackets
    param = "[100.0, 0.0, 105.0, 1.0]"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 400:
        errors.append(
            f"GET Search with bbox={param} returned status code {r.status_code}, instead of 400"
        )

    if post:
        # Invalid POST query with CSV string of coordinates
        param = "100.0, 0.0, 105.0, 1.0"
        r = requests.post(search_url, json={"bbox": param})
        if r.status_code != 400:
            errors.append(
                f'POST Search with bbox:"{param}" returned status code {r.status_code}, instead of 400'
            )

    # Invalid bbox - lat 1 > lat 2
    param = "100.0, 1.0, 105.0, 0.0"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 400:
        errors.append(
            f"GET Search with bbox=param (lat 1 > lat 2) returned status code {r.status_code}, instead of 400"
        )

    if post:
        param_list = [100.0, 1.0, 105.0, 0.0]
        r = requests.post(search_url, json={"bbox": param_list})
        if r.status_code != 400:
            errors.append(
                f"POST Search with bbox: {param_list} (lat 1 > lat 2) returned status code {r.status_code}, instead of 400"
            )

    # Invalid bbox - 1, 2, 3, 5, and 7 element array
    bboxes = [[0], [0, 0], [0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1]]

    for bbox in bboxes:
        param = ",".join(str(c) for c in bbox)
        r = requests.get(search_url, params={"bbox": param})
        if r.status_code != 400:
            errors.append(
                f"GET Search with bbox={param} returned status code {r.status_code}, instead of 400"
            )
        if post:
            r = requests.post(search_url, json={"bbox": bbox})
            if r.status_code != 400:
                errors.append(
                    f"POST Search with bbox:{bbox} returned status code {r.status_code}, instead of 400"
                )


def validate_item_search_limit(search_url: str, post: bool, errors: List[str]) -> None:
    valid_limits = [1, 2, 10]  # todo: pull actual limits from service description
    for limit in valid_limits:
        # Valid GET query
        params = {"limit": limit}
        r = requests.get(search_url, params=params)
        if r.status_code != 200:
            errors.append(
                f"GET Search with {params} returned status code {r.status_code}"
            )
        else:
            try:
                body = r.json()
                items = body.get("items")
                if items and len(items) <= 1:
                    errors.append(
                        f"POST Search with {params} returned fewer than 1 result"
                    )

            except json.decoder.JSONDecodeError:
                errors.append(
                    f"GET Search with {params} returned non-json response: {r.text}"
                )

        if post:
            # Valid POST query
            r = requests.post(search_url, json=params)
            if r.status_code != 200:
                errors.append(
                    f"POST Search with {params} returned status code {r.status_code}"
                )
            else:
                try:
                    body = r.json()
                    items = body.get("items")
                    if items and len(items) <= 1:
                        errors.append(
                            f"POST Search with {params} returned fewer than 1 result"
                        )
                except json.decoder.JSONDecodeError:
                    errors.append(
                        f"POST Search with {params} returned non-json response: {r.text}"
                    )

    invalid_limits = [-1]  # todo: pull actual limits from service desc and test them
    for limit in invalid_limits:
        # Valid GET query
        params = {"limit": limit}
        r = requests.get(search_url, params=params)
        if r.status_code != 400:
            errors.append(
                f"GET Search with {params} returned status code {r.status_code}, must be 400"
            )

        if post:
            # Valid POST query
            r = requests.post(search_url, json=params)
            if r.status_code != 400:
                errors.append(
                    f"POST Search with {params} returned status code {r.status_code}, must be 400"
                )


def _validate_search_ids_request(
    r: requests.Response,
    item_ids: List[str],
    method: str,
    params: Dict[str, Any],
    errors: List[str],
) -> None:
    if r.status_code != 200:
        errors.append(
            f"{method} Search with {params} returned status code {r.status_code}"
        )
    else:
        try:
            items = r.json().get("features")
            if len(items) != len(
                list(filter(lambda x: x.get("id") in item_ids, items))
            ):
                errors.append(
                    f"{method} Search with {params} returned items with ids other than specified one"
                )
        except json.decoder.JSONDecodeError:
            errors.append(
                f"{method} Search with {params} returned non-json response: {r.text}"
            )


def _validate_search_ids_with_ids(
    search_url: str, item_ids: List[str], post: bool, errors: List[str]
) -> None:
    get_params = {"ids": ",".join(item_ids)}

    _validate_search_ids_request(
        requests.get(search_url, params=get_params),
        item_ids=item_ids,
        method="GET",
        params=get_params,
        errors=errors,
    )

    if post:
        post_params = {"ids": item_ids}
        _validate_search_ids_request(
            requests.post(search_url, json=post_params),
            item_ids=item_ids,
            method="POST",
            params=post_params,
            errors=errors,
        )


def _validate_search_ids_with_ids_no_override(
    search_url: str, item: Dict[str, Any], post: bool, errors: List[str]
) -> None:
    bbox = item["bbox"]
    get_params = {
        "ids": item["id"],
        "collections": item["collection"],
        "bbox": f"{bbox[2] + 1},{bbox[3] + 1},{bbox[2] + 2},{bbox[3] + 2}",
    }

    r = requests.get(search_url, params=get_params)

    if not (r.status_code == 200):
        errors.append(
            f"GET Search with id and other parameters returned status code {r.status_code}"
        )
    else:

        try:
            if len(r.json().get("features", [])) > 0:
                errors.append(
                    "GET Search with ids and non-intersecting bbox returned results, indicating "
                    "the ids parameter is overriding the bbox parameter. All parameters are applied equally since "
                    "STAC API 1.0.0-beta.1"
                )
        except json.decoder.JSONDecodeError:
            errors.append(
                f"GET Search with {get_params} returned non-json response: {r.text}"
            )

    if post:
        post_params = {
            "ids": [item["id"]],
            "collections": [item["collection"]],
            "bbox": [bbox[2] + 1, bbox[3] + 1, bbox[2] + 2, bbox[3] + 2],
        }

        r = requests.post(search_url, json=post_params)

        if not (r.status_code == 200):
            errors.append(
                f"POST Search with id and other parameters returned status code {r.status_code}"
            )
        else:
            try:
                if len(r.json().get("features", [])) > 0:
                    errors.append(
                        "POST Search with ids and non-intersecting bbox returned results, indicating "
                        "the ids parameter is overriding the bbox parameter. All parameters are applied equally since "
                        "STAC API 1.0.0-beta.1"
                    )
            except json.decoder.JSONDecodeError:
                errors.append(
                    f"POST Search with {get_params} returned non-json response: {r.text}"
                )


def validate_item_search_ids(
    search_url: str, post: bool, warnings: List[str], errors: List[str]
) -> None:
    r = requests.get(f"{search_url}?limit=2")
    items = r.json().get("features")
    if items and len(items) >= 2:
        _validate_search_ids_with_ids(search_url, [items[0].get("id")], post, errors)
        _validate_search_ids_with_ids(
            search_url, [items[0].get("id"), items[1].get("id")], post, errors
        )
        _validate_search_ids_with_ids(
            search_url, [i["id"] for i in items], post, errors
        )
    else:
        warnings.append("Get Search with no parameters returned < 2 results")


def validate_item_search_ids_does_not_override_all_other_params(
    search_url: str, post: bool, collection: str, warnings: List[str], errors: List[str]
) -> None:
    # find one item that we can then query by id and a non-intersecting bbox to see if
    # we still get the item as a result
    if (
        items := requests.get(
            f"{search_url}?limit=1&bbox=20,20,21,21&collections={collection}"
        )
        .json()
        .get("features")
    ):
        _validate_search_ids_with_ids_no_override(search_url, items[0], post, errors)
    else:
        warnings.append("Get Search with no parameters returned 0 results")


def _validate_search_collections_request(
    r: requests.Response,
    coll_ids: List[str],
    method: str,
    params: Dict[str, Any],
    errors: List[str],
) -> None:
    if r.status_code != 200:
        errors.append(
            f"{method} Search with {params} returned status code {r.status_code}"
        )
    else:
        try:
            items = r.json().get("features")
            if len(items) != len(
                list(filter(lambda x: x.get("collection") in coll_ids, items))
            ):
                errors.append(
                    f"{method} Search with {params} returned items with ids other than specified one"
                )
        except json.decoder.JSONDecodeError:
            errors.append(
                f"{method} Search with {params} returned non-json response: {r.text}"
            )


def _validate_search_collections_with_ids(
    search_url: str, coll_ids: List[str], post: bool, errors: List[str]
) -> None:
    get_params = {"collections": ",".join(coll_ids)}
    _validate_search_collections_request(
        requests.get(search_url, params=get_params),
        coll_ids=coll_ids,
        method="GET",
        params=get_params,
        errors=errors,
    )

    if post:
        post_params = {"collections": coll_ids}
        _validate_search_collections_request(
            requests.post(search_url, json=post_params),
            coll_ids=coll_ids,
            method="POST",
            params=post_params,
            errors=errors,
        )


def validate_item_search_collections(
    search_url: str, collections_url: Optional[str], post: bool, errors: List[str]
) -> None:
    if collections_url:
        collections_entity = requests.get(collections_url).json()
        if isinstance(collections_entity, List):
            errors.append("/collections entity is an array rather than an object")
            return
        collections = collections_entity.get("collections")
        if not collections:
            errors.append(
                '/collections entity does not contain a "collections" attribute'
            )
            return

        collection_ids = [x["id"] for x in collections]
    else:  # if Collections is not implemented, get some from search
        r = requests.get(search_url)
        collection_ids = list({i["collection"] for i in r.json().get("features")})

    _validate_search_collections_with_ids(search_url, collection_ids, post, errors)

    for cid in collection_ids:
        _validate_search_collections_with_ids(search_url, [cid], post, errors)

    _validate_search_collections_with_ids(
        search_url, list(itertools.islice(collection_ids, 3)), post, errors
    )
