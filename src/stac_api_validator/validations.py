"""Validations module."""
import itertools
import json
import logging
import re
from enum import Enum
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional
from typing import Pattern
from typing import Tuple
from typing import Union

import requests
import yaml
from more_itertools import take
from pystac import Collection
from pystac import Item
from pystac import ItemCollection
from pystac import STACValidationError
from pystac_client import Client
from requests import Request
from requests import Session
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


logger = logging.getLogger(__name__)


class Method(Enum):
    GET = "GET"
    POST = "POST"


# todo: maybe merge these?

POST = "POST"
GET = "GET"


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


FEATURES = "Features"
ITEM_SEARCH = "Item Search"

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


def retrieve(
    url: str,
    errors: Errors,
    context: str,
    method: Method = Method.GET,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    status_code: int = 200,
    body: Optional[Dict[str, Any]] = None,
    r_session: Optional[Session] = None,
    additional: Optional[str] = "",
    content_type: Optional[str] = None,
) -> Tuple[int, Optional[Dict[str, Any]], Optional[Mapping[str, str]]]:
    if not r_session:
        r_session = Session()

    resp = r_session.send(
        Request(method.value, url, headers=headers, params=params, json=body).prepare()
    )

    # todo: handle connection exception, etc.
    # todo: handle timeout

    if resp.status_code != status_code:
        errors += (
            f"[{context}] method={method.value} url={url} params={params} body={body}"
            f" had unexpected status code {resp.status_code} instead of {status_code}: {additional}"
        )

    elif status_code < 400:
        if not content_type:
            if (
                url.endswith("/search") or url.endswith("/items")
            ) and not has_content_type(resp.headers, geojson_mt):
                errors += f"[{context}] {method.value} {url} content-type header is not '{geojson_mt}'"
            elif not has_content_type(resp.headers, "application/json"):
                errors += f"[{context}] {method.value} {url} content-type header is not 'application/json'"
        elif not has_content_type(resp.headers, content_type):
            errors += f"[{context}] {method.value} {url} content-type header is not '{content_type}'"

        if resp.headers.get("content-type", "").split(";")[0].endswith("json"):
            try:
                return resp.status_code, resp.json(), resp.headers
            except json.decoder.JSONDecodeError:
                errors += f"[{context}] {method.value} {url} returned non-JSON value"

    return resp.status_code, None, resp.headers


def validate_core_landing_page_body(
    body: Dict[str, Any],
    headers: Mapping[str, str],
    errors: Errors,
    conformance_classes: List[str],
    collection: Optional[str],
    geometry: Optional[str],
) -> bool:
    if not has_content_type(headers, "application/json"):
        errors += (
            "CORE-1",
            "[Core] : Landing Page (/) response Content-Type header is not application/json",
        )

    conforms_to = body.get("conformsTo", [])
    if not conforms_to:
        errors += (
            "CORE-2",
            "[Core] : Landing Page (/) 'conformsTo' field must be defined and non-empty."
            "This field is required as of 1.0.0.",
        )

    if not body.get("links"):
        errors += ("CORE-3", "/ : 'links' field must be defined and non-empty.")

    if not any(cc_core_regex.fullmatch(x) for x in conforms_to):
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
        if not any(cc_item_search_regex.fullmatch(x) for x in conforms_to):
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

    return True


def has_content_type(headers: Mapping[str, str], content_type: str) -> bool:
    return headers.get("content-type", "").split(";")[0] == content_type


def validate_api(
    root_url: str,
    conformance_classes: List[str],
    collection: Optional[str],
    geometry: Optional[str],
) -> Tuple[Warnings, Errors]:
    warnings = Warnings()
    errors = Errors()

    r_session = Session()

    _, landing_page_body, landing_page_headers = retrieve(root_url, errors, "Core")

    if not landing_page_body:
        return warnings, errors

    assert landing_page_body is not None
    assert landing_page_headers is not None

    # fail fast if there are errors with conformance or links so far
    if not validate_core_landing_page_body(
        landing_page_body,
        landing_page_headers,
        errors,
        conformance_classes,
        collection,
        geometry,
    ):
        return warnings, errors

    logger.info("Validating STAC API - Core conformance class.")
    validate_core(landing_page_body, warnings, errors, Session())

    if "browseable" in conformance_classes:
        logger.info("Validating STAC API - Browseable conformance class.")
        validate_browseable(landing_page_body, warnings, errors)
    else:
        logger.info("Skipping STAC API - Browseable conformance class.")

    if "children" in conformance_classes:
        logger.info("Validating STAC API - Children conformance class.")
        validate_children(landing_page_body, warnings, errors)
    else:
        logger.info("Skipping STAC API - Children conformance class.")

    if "collections" in conformance_classes:
        logger.info("Validating STAC API - Collections conformance class.")
        validate_collections(landing_page_body, collection, errors, r_session)
    else:
        logger.info("Skipping STAC API - Collections conformance class.")

    conforms_to = landing_page_body.get("conformsTo", [])

    if "features" in conformance_classes:
        logger.info("Validating STAC API - Features conformance class.")
        validate_collections(landing_page_body, collection, errors, r_session)
        validate_features(
            landing_page_body,
            conforms_to,
            collection,
            geometry,
            warnings,
            errors,
            r_session,
        )
    else:
        logger.info("Skipping STAC API - Features conformance class.")

    if "item-search" in conformance_classes:
        logger.info("Validating STAC API - Item Search conformance class.")
        validate_item_search(
            root_url=root_url,
            root_body=landing_page_body,
            collection=collection,  # type:ignore
            conforms_to=conforms_to,
            warnings=warnings,
            errors=errors,
            geometry=geometry,  # type:ignore
            conformance_classes=conformance_classes,
            r_session=r_session,
        )
    else:
        logger.info("Skipping STAC API - Item Search conformance class.")

    if not errors:
        try:
            catalog = Client.open(root_url)
            catalog.validate()
            for child in catalog.get_children():
                child.validate()
        except STACValidationError as e:
            errors += f"pystac error: {str(e)}"

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
    root_body: Dict[str, Any], warnings: Warnings, errors: Errors, r_session: Session
) -> None:
    links = root_body.get("links")

    if links is None:
        errors += "/ : 'links' attribute missing"

    if not (root := link_by_rel(links, "root")):
        errors += "/ : Link[rel=root] must exist"
    else:
        if root.get("type") != "application/json":
            errors += "/ : Link[rel=root] type is not application/json"

    if not (_self := link_by_rel(links, "self")):
        warnings += "/ : Link[rel=self] must exist"
    else:
        if _self.get("type") != "application/json":
            errors += "/ : Link[rel=self] type is not application/json"

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
            service_doc["href"],
            errors,
            "Core",
            content_type="text/html",
            r_session=r_session,
        )


def validate_browseable(
    root_body: Dict[str, Any], warnings: Warnings, errors: Errors
) -> None:
    logger.info("Browseable validation is not yet implemented.")


def validate_children(
    root_body: Dict[str, Any], warnings: Warnings, errors: Errors
) -> None:
    logger.info("Children validation is not yet implemented.")


def validate_collections(
    root_body: Dict[str, Any],
    collection: Optional[str],
    errors: Errors,
    r_session: Session,
) -> None:
    if not (data_link := link_by_rel(root_body["links"], "data")):
        errors += "[Collections] /: Link[rel=data] must href /collections"
    else:
        retrieve(
            f"{data_link['href']}/non-existent-collection",
            errors,
            "Collections",
            status_code=404,
            r_session=r_session,
            additional="non-existent collection",
        )

        collections_url = f"{data_link['href']}"
        _, body, resp_headers = retrieve(
            collections_url,
            errors,
            "Collections",
            r_session=r_session,
        )

        if not body:
            errors += "[Collections] /collections body was empty"
        else:
            if (
                not resp_headers
                or resp_headers.get("content-type", "").split(";")[0]
                != "application/json"
            ):
                errors += "[Collections] /collections content-type header was not application/json"

            if not (self_link := link_by_rel(body.get("links", []), "self")):
                errors += "[Collections] /collections does not have self link"
            elif collections_url != self_link.get("href"):
                errors += (
                    "[Collections] /collections self link does not match requested url"
                )

            if not link_by_rel(body.get("links", []), "root"):
                errors += "[Collections] /collections does not have root link"

            if body.get("collections") is None:
                errors += "[Collections] /collections does not have 'collections' field"

            if not (collections_list := body.get("collections")):
                errors += "[Collections] /collections 'collections' field is empty"
            else:
                try:
                    for c in collections_list:
                        Collection.from_dict(c)
                except Exception as e:
                    errors += f"[Collections] /collections Collection '{c['id']}' failed pystac hydration: {e}"

            collection_url = f"{data_link['href']}/{collection}"
            _, body, resp_headers = retrieve(
                collection_url,
                errors,
                "Collections",
                r_session=r_session,
            )

            if not body:
                errors += f"[Collections] /collections/{collection} body was empty"
            else:
                if (
                    not resp_headers
                    or resp_headers.get("content-type", "").split(";")[0]
                    != "application/json"
                ):
                    errors += f"[Collections] /collections/{collection} content-type header was not application/json"

                if not (self_link := link_by_rel(body.get("links", []), "self")):
                    errors += f"[Collections] /collections/{collection} does not have self link"
                elif collection_url != self_link.get("href"):
                    errors += f"[Collections] /collections/{collection} self link does not match requested url"

                if not link_by_rel(body.get("links", []), "root"):
                    errors += f"[Collections] /collections/{collection} does not have root link"

                if not link_by_rel(body.get("links", []), "parent"):
                    errors += f"[Collections] /collections/{collection} does not have parent link"

                try:
                    Collection.from_dict(body)
                except Exception as e:
                    errors += f"[Collections] /collections/{collection} failed pystac hydration: {e}"

        # todo: collection pagination


def validate_features(
    root_body: Dict[str, Any],
    conforms_to: List[str],
    collection: Optional[str],
    geometry: Optional[str],
    warnings: Warnings,
    errors: Errors,
    r_session: Session,
) -> None:
    if not geometry:
        errors += (
            "[Features] Geometry parameter required for running Features validations."
        )
        return

    if not collection:
        errors += (
            "[Features] Collection parameter required for running Features validations."
        )
        return

    if conforms_to and (
        req_ccs := [
            x
            for x in conforms_to
            if x.startswith("http://www.opengis.net/spec/ogcapi-features-1/1.0/req/")
        ]
    ):
        warnings += f"[Features] / : 'conformsTo' contains OGC API conformance classes using 'req' instead of 'conf': {req_ccs}."

    if "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core" not in conforms_to:
        warnings += "[Features] STAC APIs conforming to the Features conformance class may also advertise the OGC API - Features Part 1 conformance class 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core'"

    if (
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
        not in conforms_to
    ):
        warnings += "[Features] STAC APIs conforming to the Features conformance class may also advertise the OGC API - Features Part 1 conformance class 'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson'"

    # todo: add this one somewhere
    # if service-desc type is the OAS 3.0 one, add a warning that this can be used also
    # "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",

    root_links = root_body.get("links")
    conformance = link_by_rel(root_links, "conformance")
    if conformance is None:
        errors += "[Features] /: Landing page missing Link[rel=conformance]"
    elif not conformance.get("href", "").endswith("/conformance"):
        errors += (
            "[Features] /: Landing page Link[rel=conformance] must href /conformance"
        )

    if conformance:
        _, body, _ = retrieve(
            conformance["href"], errors, "Features", r_session=r_session
        )

        if body and not (
            set(root_body.get("conformsTo", [])) == set(body.get("conformsTo", []))
        ):
            warnings += "[Features] Landing Page conforms to and conformance conformsTo must be the same"

    # This is likely a mistake, but most apis can't undo it for backwards-compat reasons, so only warn
    if not (link_by_rel(root_links, "collections") is None):
        warnings += "[Features] /: Link[rel=collections] is a non-standard relation. Use Link[rel=data instead]"

    if not (collections_link := link_by_rel(root_links, "data")):
        errors += "[Features] /: Link[rel=data] must href /collections"
    else:
        collection_url = f"{collections_link['href']}/{collection}"
        _, body, _ = retrieve(
            collection_url,
            errors,
            FEATURES,
            r_session=r_session,
        )
        if body:
            if not (collection_items_link := link_by_rel(body.get("links"), "items")):
                errors += f"[Features] /collections/{collection} does not have Link[rel=items]"
            else:
                collection_items_url = collection_items_link["href"]

                retrieve(
                    f"{collection_items_url}/non-existent-item",
                    errors,
                    FEATURES,
                    status_code=404,
                    r_session=r_session,
                )

                _, body, _ = retrieve(
                    collection_items_url,
                    errors,
                    FEATURES,
                    content_type=geojson_mt,
                    r_session=r_session,
                )

                if body:
                    if not (self_link := link_by_rel(body.get("links", []), "self")):
                        errors += (
                            f"[Features] {collection_items_url} does not have self link"
                        )
                    elif collection_items_link["href"] != self_link.get("href"):
                        errors += f"[Features] {collection_items_url} self link does not match requested url"

                    if not link_by_rel(body.get("links", []), "root"):
                        errors += (
                            f"[Features] {collection_items_url} does not have root link"
                        )

                    if not link_by_rel(body.get("links", []), "parent"):
                        errors += f"[Features] {collection_items_url} does not have parent link"

                    try:
                        ItemCollection.from_dict(body)
                    except Exception as e:
                        errors += f"[Features] {collection_items_url} failed pystac hydration to ItemCollection: {e}"

                    item = next(iter(body.get("features", [])), None)

                    if not item:
                        errors += f"[Features] /collections/{collection}/items features array was empty"
                    else:
                        if not (
                            item_self_link := link_by_rel(item.get("links", []), "self")
                        ):
                            errors += f"[Features] /collections/{collection}/items first item does not have self link"
                        else:
                            item_url = item_self_link["href"]
                            _, body, _ = retrieve(
                                item_url,
                                errors,
                                FEATURES,
                                content_type=geojson_mt,
                                r_session=r_session,
                            )

                            if body:
                                if not (
                                    self_link := link_by_rel(
                                        body.get("links", []), "self"
                                    )
                                ):
                                    errors += (
                                        f"[Features] {item_url} does not have self link"
                                    )
                                elif item_url != self_link.get("href"):
                                    errors += f"[Features] {item_url} self link does not match requested url"

                                if not link_by_rel(body.get("links", []), "root"):
                                    errors += (
                                        f"[Features] {item_url} does not have root link"
                                    )

                                if not link_by_rel(body.get("links", []), "parent"):
                                    errors += f"[Features] {item_url} does not have parent link"

                                try:
                                    Item.from_dict(body)
                                except Exception as e:
                                    errors += f"[Features] {item_url} failed pystac hydration to Item: {e}"

    # Items pagination validation
    if not (collections_url := link_by_rel(root_links, "data")):
        errors += "/: Link[rel=data] must href /collections, cannot run pagination test"
    else:
        if not (self_link := link_by_rel(root_links, "self")):
            errors += "/: Link[rel=self] missing"
        else:
            validate_item_pagination(
                root_url=self_link.get("href", ""),
                search_url=f"{collections_url['href']}/{collection}/items",
                collection=None,
                geometry=geometry,
                methods=["GET"],
                errors=errors,
                use_pystac_client=False,
            )

    # if any(cc_features_fields_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Features - Fields extension conformance class found.")
    #
    # if any(cc_features_context_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Features - Context extension conformance class found.")
    #
    # if any(cc_features_sort_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Features - Sort extension conformance class found.")
    #
    # if any(cc_features_query_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Features - Query extension conformance class found.")
    #
    # if any(cc_features_filter_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Features - Filter extension conformance class found.")

    if any(cc_features_filter_regex.fullmatch(x) for x in conforms_to):
        logger.info("STAC API - Features - Filter Extension conformance class found.")
        validate_features_filter(
            root_body=root_body,
            collection=collection,
            errors=errors,
            r_session=r_session,
        )
    else:
        logger.info(
            "Skipping STAC API - Features - Filter Extension conformance class."
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

    methods = [sl.get("method", None) for sl in search_links]
    if not methods:
        methods = [GET]

    # Collections may not be implemented, so set to None
    # and later get some collection ids another way
    if links and (collections := link_by_rel(links, "data")):
        collections_url = collections.get("href")
    else:
        collections_url = None

    search_url = search_links[0]["href"]
    _, body, _ = retrieve(
        search_url, errors, "Item Search", content_type=geojson_mt, r_session=r_session
    )

    if body:
        try:
            ItemCollection.from_dict(body)
        except Exception as e:
            errors += f"[Item Search] {search_url} failed pystac hydration to ItemCollection: {e}"

    validate_item_search_limit(search_url, methods, errors)
    validate_item_search_bbox_xor_intersects(search_url, methods, errors)
    validate_item_search_bbox(search_url, methods, errors)
    validate_item_search_datetime(search_url, methods, warnings, errors, r_session)
    validate_item_search_ids(search_url, methods, warnings, errors)
    validate_item_search_ids_does_not_override_all_other_params(
        search_url, methods, collection, warnings, errors
    )
    validate_item_search_collections(search_url, collections_url, methods, errors)
    validate_item_search_intersects(
        search_url=search_url,
        collection=collection,
        methods=methods,
        errors=errors,
        geometry=geometry,
    )

    validate_item_pagination(
        root_url=root_url,
        search_url=search_url,
        collection=collection,
        geometry=geometry,
        methods=methods,
        errors=errors,
    )

    # if any(cc_item_search_fields_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Item Search - Fields extension conformance class found.")
    #
    # if any(cc_item_search_context_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Item Search - Context extension conformance class found.")
    #
    # if any(cc_item_search_sort_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Item Search - Sort extension conformance class found.")
    #
    # if any(cc_item_search_query_regex.fullmatch(x) for x in conforms_to):
    #     logger.info("STAC API - Item Search - Query extension conformance class found.")
    #

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
            search_url=search_url,
            collection=collection,
            errors=errors,
            r_session=r_session,
        )
    else:
        logger.info(
            "Skipping STAC API - Item Search - Filter Extension conformance class."
        )


def validate_filter_queryables(
    queryables_url: str, conformance_class: str, errors: Errors, r_session: Session
) -> None:
    _, queryables_schema, _ = retrieve(
        queryables_url,
        errors,
        f"{conformance_class} - Filter Ext",
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
                f"[{conformance_class} - Filter Ext] Queryables '{queryables_url}' "
                f"'$schema' value invalid, must be one of: '{','.join(json_schemas)}'"
            )

        if queryables_schema.get("$id") != queryables_url:
            errors += f"[{conformance_class} - Filter Ext] Queryables '{queryables_url}' '$id' value invalid, must be same as queryables url"

        if queryables_schema.get("type") != "object":
            errors += f"[{conformance_class} Filter Ext] Queryables '{queryables_url}' 'type' value invalid, must be 'object'"


def validate_features_filter(
    root_body: Dict[str, Any], collection: str, errors: Errors, r_session: Session
) -> None:
    logger.info(
        "WARNING: Features - Filter Ext validation is not yet fully implemented."
    )

    if not (collections_link := link_by_rel(root_body["links"], "data")):
        errors += "[Features] / : 'data' link relation missing"
    else:
        collection_url = f"{collections_link['href']}/{collection}"
        _, body, _ = retrieve(collection_url, errors, FEATURES, r_session=r_session)
        assert body

        if not (
            queryables_link := link_by_rel(
                body["links"], "http://www.opengis.net/def/rel/ogc/1.0/queryables"
            )
        ):
            errors += f"[Features - Filter Ext] {collection_url} : 'http://www.opengis.net/def/rel/ogc/1.0/queryables' (Queryables) link relation missing"

        validate_filter_queryables(
            queryables_url=(queryables_link and queryables_link["href"])
            or f"{collection_url}/queryables",
            conformance_class=FEATURES,
            errors=errors,
            r_session=r_session,
        )


# Assumes id, collection, geometry, and datetime are available
def validate_item_search_filter(
    root_url: str,
    root_body: Dict[str, Any],
    search_url: str,
    collection: str,
    errors: Errors,
    r_session: Session,
) -> None:
    if not (
        queryables_link := link_by_rel(
            root_body["links"], "http://www.opengis.net/def/rel/ogc/1.0/queryables"
        )
    ):
        errors += "[Item Search - Filter Ext] / : 'http://www.opengis.net/def/rel/ogc/1.0/queryables' (Queryables) link relation missing"

    validate_filter_queryables(
        queryables_url=(queryables_link and queryables_link["href"])
        or f"{root_url}/queryables",
        conformance_class="Item Search",
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
    else:
        logger.info(
            "Skipping STAC API - Item Search - Filter Extension - CQL2-Text conformance class."
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
    else:
        logger.info(
            "Skipping STAC API - Item Search - Filter Extension - CQL2-JSON conformance class."
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
    else:
        logger.info(
            "Skipping STAC API - Item Search - Filter Extension - Basic CQL2 conformance class."
        )

    advanced_comparison_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/advanced-comparison-operators"
        in conforms_to
    )

    if advanced_comparison_operators_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - Advanced Comparison Operators conformance class."
        )
    else:
        logger.info(
            "Skipping STAC API - Item Search - Filter Extension - Advanced Comparison Operators conformance class."
        )

    basic_spatial_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/basic-spatial-operators"
        in conforms_to
    )

    if basic_spatial_operators_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - Basic Spatial Operators conformance class."
        )
    else:
        logger.info(
            "Skipping STAC API - Item Search - Filter Extension - Basic Spatial Operators conformance class."
        )

    temporal_operators_supported = (
        "http://www.opengis.net/spec/cql2/1.0/conf/temporal-operators" in conforms_to
    )

    if temporal_operators_supported:
        logger.info(
            "Validating STAC API - Item Search - Filter Extension - Temporal Operators conformance class."
        )
    else:
        logger.info(
            "Skipping STAC API - Item Search - Filter Extension - Temporal Operators conformance class."
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
            f"{search_url}?collections={collection}",
            context="Item Search - Filter Ext",
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
            search_url,
            errors,
            "Item Search - Filter Ext",
            content_type=geojson_mt,
            r_session=r_session,
            params={"limit": 1, "filter-lang": "cql2-text", "filter": f_text},
        )

    for f_json in filter_jsons:
        retrieve(
            search_url,
            method=Method.POST,
            body={"limit": 1, "filter-lang": "cql2-json", "filter": f_json},
            errors=errors,
            context="Item Search - Filter Ext",
            content_type=geojson_mt,
            r_session=r_session,
        )


def validate_item_search_datetime(
    search_url: str,
    methods: List[str],
    warnings: Warnings,
    errors: Errors,
    r_session: Optional[Session],
) -> None:
    # find an Item and try to use its datetime value in a query
    _, body, _ = retrieve(
        search_url, errors, ITEM_SEARCH, r_session=r_session, content_type=geojson_mt
    )
    if not body:
        return
    else:
        dt = body["features"][0]["properties"]["datetime"]  # todo: if no results, fail

    _, body, _ = retrieve(
        search_url,
        errors,
        ITEM_SEARCH,
        content_type=geojson_mt,
        params={"datetime": dt},
        additional=f"with datetime={dt} extracted from an Item",
    )
    if body and len(body["features"]) == 0:
        errors += f"[Item Search] GET Search with datetime={dt} extracted from an Item returned no results."

    for dt in valid_datetimes:
        if not r_session:
            r_session = Session()

        r = r_session.send(
            Request("GET", search_url, params={"datetime": dt}).prepare()
        )
        if r.status_code != 200:
            errors += f"[Item Search] GET Search with datetime={dt} returned status code {r.status_code}"
            continue
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors += f"[Item Search] GET Search with datetime={dt} returned non-json response"

    for dt in invalid_datetimes:
        status_code, _, _ = retrieve(
            search_url,
            params={"datetime": dt},
            status_code=400,
            r_session=r_session,
            errors=errors,
            context=ITEM_SEARCH,
            additional="invalid datetime returned non-400 status code",
        )
        if status_code == 200:
            warnings += f"[Item Search] GET Search with datetime={dt} returned status code 200 instead of 400"
            continue

    # todo: POST


def validate_item_search_bbox_xor_intersects(
    search_url: str, methods: List[str], errors: Errors
) -> None:
    r = requests.get(
        search_url, params={"bbox": "0,0,1,1", "intersects": json.dumps(polygon)}
    )
    if r.status_code != 400:
        errors += f"[Item Search] GET Search with bbox and intersects returned status code {r.status_code}"

    if POST in methods:
        # Valid POST query
        r = requests.post(
            search_url, json={"bbox": [0, 0, 1, 1], "intersects": polygon}
        )
        if r.status_code != 400:
            errors += f"[Item Search] POST Search with bbox and intersects returned status code {r.status_code}"


def validate_item_pagination(
    root_url: str,
    search_url: str,
    collection: Optional[str],
    geometry: str,
    methods: List[str],
    errors: Errors,
    use_pystac_client: bool = True,
) -> None:
    url = f"{search_url}?limit=1"
    if collection is not None:
        url = f"{url}&collections={collection}"

    r = requests.get(url)
    if not r.status_code == 200:
        errors += "STAC API - Item Search GET pagination get failed for initial request"
    else:
        try:
            first_body = r.json()
            if link := link_by_rel(first_body.get("links"), "next"):
                if (method := link.get("method")) and method != "GET":
                    errors += f"STAC API - Item Search GET pagination first request 'next' link relation has method {method} instead of 'GET'"

                next_url = link.get("href")
                if next_url is None:
                    errors += "STAC API - Item Search GET pagination first request 'next' link relation missing href"
                else:
                    if url == next_url:
                        errors += "STAC API - Item Search GET pagination next href same as first url"

                    r = requests.get(next_url)
                    if not r.status_code == 200:
                        errors += f"STAC API - Item Search GET pagination get failed for next url {next_url}"
            else:
                errors += "STAC API - Item Search GET pagination first request had no 'next' link relation"

        except json.decoder.JSONDecodeError:
            errors += f"STAC API - Item Search GET pagination response failed {url}"

    max_items = 100

    # todo: how to paginate over items, not just search?

    if use_pystac_client and collection is not None:
        client = Client.open(root_url)
        search = client.search(
            method="GET", collections=[collection], max_items=max_items, limit=5
        )

        items = list(search.items_as_dicts())

        if len(items) > max_items:
            errors += "STAC API - Item Search GET pagination - more than max items returned from paginating"

        if len(items) > len({item["id"] for item in items}):
            errors += "STAC API - Item Search GET pagination - duplicate items returned from paginating items"
    elif use_pystac_client and collection is None:
        errors += "STAC API - Item Search GET pagination - pystac-client tests not run, collection is not defined"

    # GET paging has a problem with intersects https://github.com/stac-utils/pystac-client/issues/335
    # search = client.search(method="GET", collections=[collection], intersects=geometry)
    # if len(list(take(20000, search.items_as_dicts()))) == 20000:
    #     errors +=
    #         f"STAC API - Item Search GET pagination - paged through 20,000 results. This could mean the last page "
    #         f"of results references itself, or your collection and geometry combination has too many results."
    #     )

    if POST in methods:
        initial_json_body = {"limit": 1, "collections": [collection]}
        r = requests.post(search_url, json=initial_json_body)
        if not r.status_code == 200:
            errors += (
                "STAC API - Item Search POST pagination get failed for initial request"
            )
        else:
            try:
                first_body = r.json()
                if link := link_by_rel(first_body.get("links"), "next"):
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

                        r = requests.post(next_url, json=second_json_body)
                        if not r.status_code == 200:
                            errors += f"STAC API - Item Search POST pagination get failed for next url {next_url} with body {second_json_body}"
                        else:
                            r.json()
                else:
                    errors += "STAC API - Item Search POST pagination first request had no 'next' link relation"

            except json.decoder.JSONDecodeError:
                errors += "STAC API - Item Search POST pagination response failed"

        if use_pystac_client and collection is not None:
            max_items = 100
            client = Client.open(root_url)
            search = client.search(
                method="POST", collections=[collection], max_items=max_items, limit=5
            )

            items = list(search.items_as_dicts())

            if len(items) > max_items:
                errors += "STAC API - Item Search POST pagination - more than max items returned from paginating"

            if len(items) > len({item["id"] for item in items}):
                errors += "STAC API - Item Search POST pagination - duplicate items returned from paginating items"

            search = client.search(
                method="POST", collections=[collection], intersects=geometry
            )
            if len(list(take(20000, search.items_as_dicts()))) == 20000:
                errors += (
                    "STAC API - Item Search POST pagination - paged through 20,000 results. This could mean the last page "
                    "of results references itself, or your collection and geometry combination has too many results."
                )
        elif collection is not None:
            errors += "STAC API - Item Search POST pagination - pystac-client tests not run, collection is undefined"


def validate_item_search_intersects(
    search_url: str, collection: str, methods: List[str], errors: Errors, geometry: str
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
            errors += f"[Item Search] GET Search with intersects={param} returned status code {r.status_code}"
        else:
            try:
                r.json()
            except json.decoder.JSONDecodeError:
                errors += f"[Item Search] GET Search with intersects={param} returned non-json response: {r.text}"
        if POST in methods:
            # Valid POST query
            r = requests.post(search_url, json={"intersects": param})
            if r.status_code != 200:
                errors += f"[Item Search] POST Search with intersects:{param} returned status code {r.status_code}"
            else:
                try:
                    r.json()
                except json.decoder.JSONDecodeError:
                    errors += f"[Item Search] POST Search with intersects:{param} returned non-json response: {r.text}"

    intersects_shape = shape(json.loads(geometry))

    # Validate GET query
    r = requests.get(
        search_url,
        params={"collections": collection, "intersects": geometry},
    )
    if r.status_code != 200:
        errors += f"[Item Search] GET Search with collections={collection}&intersects={geometry} returned status code {r.status_code}"
    else:
        try:
            item_collection = r.json()
            if not len(item_collection["features"]):
                errors += f"[Item Search] GET Search result for intersects={geometry} returned no results"
            if any(
                not intersects_shape.intersects(shape(item["geometry"]))
                for item in item_collection["features"]
            ):
                errors += f"[Item Search] GET Search results for intersects={geometry} do not all intersect"
        except json.decoder.JSONDecodeError:
            errors += f"[Item Search] GET Search with intersects={geometry} returned non-json response: {r.text}"

    if POST in methods:
        # Validate POST query
        r = requests.post(
            search_url, json={"collections": [collection], "intersects": geometry}
        )
        if r.status_code != 200:
            errors += f"[Item Search] POST Search with intersects={geometry} returned status code {r.status_code}"
        else:
            try:
                item_collection = r.json()
                if not len(item_collection["features"]):
                    errors += f"[Item Search] POST Search result for intersects={geometry} returned no results"
                for item in item_collection["features"]:
                    if not intersects_shape.intersects(shape(item["geometry"])):
                        errors += f"[Item Search] POST Search result for intersects={geometry}, does not intersect {item['geometry']}"
            except json.decoder.JSONDecodeError:
                errors += f"[Item Search] POST Search with intersects={geometry} returned non-json response: {r.text}"


def validate_item_search_bbox(
    search_url: str, methods: List[str], errors: Errors
) -> None:
    # Valid GET query
    param = "100.0,0.0,105.0,1.0"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 200:
        errors += f"[Item Search] GET Search with bbox={param} returned status code {r.status_code}"
    else:
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors += f"[Item Search] GET Search with bbox={param} returned non-json response: {r.text}"

    if POST in methods:
        # Valid POST query
        param_list = [100.0, 0.0, 105.0, 1.0]
        r = requests.post(search_url, json={"bbox": param_list})
        if r.status_code != 200:
            errors += f"[Item Search] POST Search with bbox:{param_list} returned status code {r.status_code}"
        else:
            try:
                r.json()
            except json.decoder.JSONDecodeError:
                errors += f"[Item Search] POST Search with bbox:{param_list} returned non-json response: {r.text}"

    # Valid 3D GET query
    param = "100.0,0.0,0.0,105.0,1.0,1.0"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 200:
        errors += f"[Item Search] GET Search with bbox={param} returned status code {r.status_code}"
    else:
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors += f"[Item Search] GET with bbox={param} returned non-json response: {r.text}"

    if POST in methods:
        # Valid 3D POST query
        param_list = [100.0, 0.0, 0.0, 105.0, 1.0, 1.0]
        r = requests.post(search_url, json={"bbox": param_list})
        if r.status_code != 200:
            errors += f"[Item Search] POST Search with bbox:{param_list} returned status code {r.status_code}"
        else:
            try:
                r.json()
            except json.decoder.JSONDecodeError:
                errors += f"[Item Search] POST with bbox:{param_list} returned non-json response: {r.text}"

    # Invalid GET query with coordinates in brackets
    param = "[100.0, 0.0, 105.0, 1.0]"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 400:
        errors += f"[Item Search] GET Search with bbox={param} returned status code {r.status_code}, instead of 400"

    if POST in methods:
        # Invalid POST query with CSV string of coordinates
        param = "100.0, 0.0, 105.0, 1.0"
        r = requests.post(search_url, json={"bbox": param})
        if r.status_code != 400:
            errors += f"[Item Search] POST Search with bbox:'{param}' returned status code {r.status_code}, instead of 400"

    # Invalid bbox - lat 1 > lat 2
    param = "100.0, 1.0, 105.0, 0.0"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 400:
        errors += f"[Item Search] GET Search with bbox=param (lat 1 > lat 2) returned status code {r.status_code}, instead of 400"

    if POST in methods:
        param_list = [100.0, 1.0, 105.0, 0.0]
        r = requests.post(search_url, json={"bbox": param_list})
        if r.status_code != 400:
            errors += f"[Item Search] POST Search with bbox: {param_list} (lat 1 > lat 2) returned status code {r.status_code}, instead of 400"

    # Invalid bbox - 1, 2, 3, 5, and 7 element array
    bboxes = [[0], [0, 0], [0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1]]

    for bbox in bboxes:
        param = ",".join(str(c) for c in bbox)
        r = requests.get(search_url, params={"bbox": param})
        if r.status_code != 400:
            errors += f"[Item Search] GET Search with bbox={param} returned status code {r.status_code}, instead of 400"
        if POST in methods:
            r = requests.post(search_url, json={"bbox": bbox})
            if r.status_code != 400:
                errors += f"[Item Search] POST Search with bbox:{bbox} returned status code {r.status_code}, instead of 400"


def validate_item_search_limit(
    search_url: str, methods: List[str], errors: Errors
) -> None:
    valid_limits = [1, 2, 10]  # todo: pull actual limits from service description
    for limit in valid_limits:
        # Valid GET query
        params = {"limit": limit}
        r = requests.get(search_url, params=params)
        if r.status_code != 200:
            errors += f"[Item Search] GET Search with {params} returned status code {r.status_code}"
        else:
            try:
                body = r.json()
                items = body.get("items")
                if items and len(items) <= 1:
                    errors += f"[Item Search] POST Search with {params} returned fewer than 1 result"

            except json.decoder.JSONDecodeError:
                errors += f"[Item Search] GET Search with {params} returned non-json response: {r.text}"

        if POST in methods:
            # Valid POST query
            r = requests.post(search_url, json=params)
            if r.status_code != 200:
                errors += f"[Item Search] POST Search with {params} returned status code {r.status_code}"
            else:
                try:
                    body = r.json()
                    items = body.get("items")
                    if items and len(items) <= 1:
                        errors += f"[Item Search] POST Search with {params} returned fewer than 1 result"
                except json.decoder.JSONDecodeError:
                    errors += f"[Item Search] POST Search with {params} returned non-json response: {r.text}"

    invalid_limits = [-1]  # todo: pull actual limits from service desc and test them
    for limit in invalid_limits:
        # Valid GET query
        params = {"limit": limit}
        r = requests.get(search_url, params=params)
        if r.status_code != 400:
            errors += f"[Item Search] GET Search with {params} returned status code {r.status_code}, must be 400"

        if POST in methods:
            # Valid POST query
            r = requests.post(search_url, json=params)
            if r.status_code != 400:
                errors += f"[Item Search] POST Search with {params} returned status code {r.status_code}, must be 400"


def _validate_search_ids_request(
    r: requests.Response,
    item_ids: List[str],
    method: str,
    params: Dict[str, Any],
    errors: Errors,
) -> None:
    if r.status_code != 200:
        errors += f"{method} Search with {params} returned status code {r.status_code}"
    else:
        try:
            items = r.json().get("features")
            if len(items) != len(
                list(filter(lambda x: x.get("id") in item_ids, items))
            ):
                errors += f"{method} Search with {params} returned items with ids other than specified one"
        except json.decoder.JSONDecodeError:
            errors += (
                f"{method} Search with {params} returned non-json response: {r.text}"
            )


def _validate_search_ids_with_ids(
    search_url: str, item_ids: List[str], methods: List[str], errors: Errors
) -> None:
    get_params = {"ids": ",".join(item_ids)}

    _validate_search_ids_request(
        requests.get(search_url, params=get_params),
        item_ids=item_ids,
        method="GET",
        params=get_params,
        errors=errors,
    )

    if POST in methods:
        post_params = {"ids": item_ids}
        _validate_search_ids_request(
            requests.post(search_url, json=post_params),
            item_ids=item_ids,
            method="POST",
            params=post_params,
            errors=errors,
        )


def _validate_search_ids_with_ids_no_override(
    search_url: str, item: Dict[str, Any], methods: List[str], errors: Errors
) -> None:
    bbox = item["bbox"]
    get_params = {
        "ids": item["id"],
        "collections": item["collection"],
        "bbox": f"{bbox[2] + 1},{bbox[3] + 1},{bbox[2] + 2},{bbox[3] + 2}",
    }

    r = requests.get(search_url, params=get_params)

    if not (r.status_code == 200):
        errors += f"[Item Search]  GET Search with id and other parameters returned status code {r.status_code}"
    else:

        try:
            if len(r.json().get("features", [])) > 0:
                errors += (
                    "[Item Search] GET Search with ids and non-intersecting bbox returned results, indicating "
                    "the ids parameter is overriding the bbox parameter. All parameters are applied equally since "
                    "STAC API 1.0.0-beta.1"
                )
        except json.decoder.JSONDecodeError:
            errors += f"[Item Search] GET Search with {get_params} returned non-json response: {r.text}"

    if POST in methods:
        post_params = {
            "ids": [item["id"]],
            "collections": [item["collection"]],
            "bbox": [bbox[2] + 1, bbox[3] + 1, bbox[2] + 2, bbox[3] + 2],
        }

        r = requests.post(search_url, json=post_params)

        if not (r.status_code == 200):
            errors += f"[Item Search] POST Search with id and other parameters returned status code {r.status_code}"
        else:
            try:
                if len(r.json().get("features", [])) > 0:
                    errors += (
                        "[Item Search] POST Search with ids and non-intersecting bbox returned results, indicating "
                        "the ids parameter is overriding the bbox parameter. All parameters are applied equally since "
                        "STAC API 1.0.0-beta.1"
                    )
            except json.decoder.JSONDecodeError:
                errors += f"[Item Search] POST Search with {get_params} returned non-json response: {r.text}"


def validate_item_search_ids(
    search_url: str, methods: List[str], warnings: Warnings, errors: Errors
) -> None:
    r = requests.get(f"{search_url}?limit=2")
    items = r.json().get("features")
    if items and len(items) >= 2:
        _validate_search_ids_with_ids(search_url, [items[0].get("id")], methods, errors)
        _validate_search_ids_with_ids(
            search_url, [items[0].get("id"), items[1].get("id")], methods, errors
        )
        _validate_search_ids_with_ids(
            search_url, [i["id"] for i in items], methods, errors
        )
    else:
        warnings += "[Item Search] GET Search with no parameters returned < 2 results"


def validate_item_search_ids_does_not_override_all_other_params(
    search_url: str,
    methods: List[str],
    collection: str,
    warnings: Warnings,
    errors: Errors,
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
        _validate_search_ids_with_ids_no_override(search_url, items[0], methods, errors)
    else:
        warnings += "[Item Search] GET Search with no parameters returned 0 results"


def _validate_search_collections_request(
    r: requests.Response,
    coll_ids: List[str],
    method: str,
    params: Dict[str, Any],
    errors: Errors,
) -> None:
    if r.status_code != 200:
        errors += f"{method} Search with {params} returned status code {r.status_code}"
    else:
        try:
            items = r.json().get("features")
            if len(items) != len(
                list(filter(lambda x: x.get("collection") in coll_ids, items))
            ):
                errors += f"{method} Search with {params} returned items with ids other than specified one"
        except json.decoder.JSONDecodeError:
            errors += (
                f"{method} Search with {params} returned non-json response: {r.text}"
            )


def _validate_search_collections_with_ids(
    search_url: str, coll_ids: List[str], methods: List[str], errors: Errors
) -> None:
    get_params = {"collections": ",".join(coll_ids)}
    _validate_search_collections_request(
        requests.get(search_url, params=get_params),
        coll_ids=coll_ids,
        method="GET",
        params=get_params,
        errors=errors,
    )

    if POST in methods:
        post_params = {"collections": coll_ids}
        _validate_search_collections_request(
            requests.post(search_url, json=post_params),
            coll_ids=coll_ids,
            method="POST",
            params=post_params,
            errors=errors,
        )


def validate_item_search_collections(
    search_url: str, collections_url: Optional[str], methods: List[str], errors: Errors
) -> None:
    if collections_url:
        collections_entity = requests.get(collections_url).json()
        if isinstance(collections_entity, List):
            errors += "/collections entity is an array rather than an object"
            return
        collections = collections_entity.get("collections")
        if not collections:
            errors += "/collections entity does not contain a 'collections' attribute"
            return

        collection_ids = [x["id"] for x in collections]
    else:  # if Collections is not implemented, get some from search
        r = requests.get(search_url)
        collection_ids = list({i["collection"] for i in r.json().get("features")})

    _validate_search_collections_with_ids(search_url, collection_ids, methods, errors)

    for cid in collection_ids:
        _validate_search_collections_with_ids(search_url, [cid], methods, errors)

    _validate_search_collections_with_ids(
        search_url, list(itertools.islice(collection_ids, 3)), methods, errors
    )
