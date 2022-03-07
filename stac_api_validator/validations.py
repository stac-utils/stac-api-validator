from typing import List, Tuple, Dict
from pystac_client import Client
import requests
from typing import Callable
import re
import json
import itertools
from geometries import (
    point,
    linestring,
    polygon,
    polygon_with_hole,
    multipoint,
    multilinestring,
    multipolygon,
    geometry_collection,
)

# https://github.com/stac-utils/pystac/blob/4c7c775a6d0ca49d83dbec714855a189be759c8a/docs/concepts.rst#using-your-own-validator

# resolve_stac_object

core_cc_regex = re.compile(r"https://api\.stacspec\.org/.+/core")

oaf_cc_regex = re.compile(r"https://api\.stacspec\.org/.+/ogcapi-features")
oaf_transaction_cc_regex = re.compile(
    r"https://api\.stacspec\.org/.+/ogcapi-features/extensions/transaction"
)
oaf_version_cc_regex = re.compile(
    r"https://api\.stacspec\.org/.+/ogcapi-features/extensions/version"
)

search_cc_regex = re.compile(r"https://api\.stacspec\.org/.+/item-search")
search_fields_cc_regex = re.compile(r"https://api\.stacspec\.org/.+/item-search#fields")
search_contextsearch_fields_cc_regex_cc_regex = re.compile(
    r"https://api\.stacspec\.org/.+/item-search#context"
)
search_sort_cc_regex = re.compile(r"https://api\.stacspec\.org/.+/item-search#sort")
search_query_cc_regex = re.compile(r"https://api\.stacspec\.org/.+/item-search#query")

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


def validate_api(root_url: str, post: bool) -> Tuple[List[str], List[str]]:
    warnings: List[str] = []
    errors: List[str] = []

    root = requests.get(root_url)

    # todo: handle connection exception, etc.
    if root.status_code != 200:
        errors.append(f"root URL {root_url} returned status code {root.status_code}")
        return warnings, errors

    root_body = root.json()

    conforms_to = root_body.get("conformsTo")
    if not conforms_to:
        errors.append(
            "/ : 'conformsTo' field must be defined and non-empty. This field is required as of 1.0.0."
        )

    if not root_body.get("links"):
        errors.append("/ : 'links' field must be defined and non-empty.")

    if (
        conforms_to
        and not any(core_cc_regex.fullmatch(x) for x in conforms_to)
        and not any(oaf_cc_regex.fullmatch(x) for x in conforms_to)
        and not any(search_cc_regex.fullmatch(x) for x in conforms_to)
    ):
        errors.append(
            "/ : 'conformsTo' must contain at least one STAC API conformance class."
        )

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

    # fail fast if there are errors with conformance or links so far
    if errors:
        return warnings, errors

    if any(core_cc_regex.fullmatch(x) for x in conforms_to):
        print("STAC API - Core conformance class found.")
        validate_core(root_body, warnings, errors)
    else:
        errors.append(
            "/ : 'conformsTo' must contain STAC API - Core conformance class."
        )

    if any(oaf_cc_regex.fullmatch(x) for x in conforms_to):
        print("STAC API - Features conformance class found.")
        validate_oaf(root_body, warnings, errors)

    if any(search_cc_regex.fullmatch(x) for x in conforms_to):
        print("STAC API - Item Search conformance class found.")
        validate_search(root_body, post, conforms_to, warnings, errors)

    if not errors:
        try:
            catalog = Client.open(root_url)
            catalog.validate()
            for collection in catalog.get_children():
                collection.validate()
        except Exception as e:
            errors.append(str(e))

    return warnings, errors


def href_for(links: List, key: str) -> Dict[str, str]:
    return next((link for link in links if link.get("rel") == key), None)


def validate_core(root_body: Dict, warnings: List[str], errors: List[str]) -> None:
    links = root_body.get("links")

    # Link rel=root
    root = href_for(links, "root")
    if root is not None:
        if root.get("type") != "application/json":
            errors.append("root type is not application/json")
    else:
        errors.append("/ : Link[rel=root] must exist")

    # Link rel=self
    _self = href_for(links, "self")
    if _self is not None:
        if _self.get("type") != "application/json":
            errors.append("self type is not application/json")
    else:
        warnings.append("/ : Link[rel=self] must exist")

    # Link rel=service-desc
    service_desc = href_for(links, "service-desc")
    if not service_desc:
        errors.append("/ : Link[rel=service-desc] must exist")
    else:
        r_service_desc = requests.get(service_desc["href"])

        errors += validate(
            "/ : Link[service-desc] must return 200",
            lambda: r_service_desc.status_code == 200,
        )

        service_desc_type = service_desc.get("type")
        if (
            (ct := r_service_desc.headers.get("content-type")) == service_desc_type
        ) or (
            (";" in ct or ";" in service_desc_type)
            and (ct.split(";", 1)[0] == service_desc_type.split(";", 1)[0])
        ):
            pass
        else:
            errors.append(
                f"service-desc ({service_desc}): link must advertise same type as endpoint content-type header, "
                f"advertised '{service_desc_type}', actually '{ct}'"
            )

    # Link rel=service-doc
    service_doc = href_for(links, "service-doc")
    if not service_doc:
        warnings.append("/ : Link[rel=service-doc] must exist")
    else:
        if service_doc.get("type") != "text/html":
            errors.append("service-doc type is not text/html")

        r_service_doc = requests.get(service_doc["href"])

        errors += validate(
            "/ : Link[service-doc] must return 200",
            lambda: r_service_doc.status_code == 200,
        )

        if (ct := r_service_doc.headers.get("content-type")).startswith("text/html"):
            pass
        else:
            errors.append(
                f"service-doc ({service_doc}): must have content-type header 'text/html', actually '{ct}'"
            )


def validate_oaf(root_body: Dict, warnings: List[str], errors: List[str]) -> None:
    links = root_body.get("links")
    conformance = href_for(links, "conformance")
    errors += validate(
        "/ Link[rel=conformance] must href /conformance",
        lambda: conformance and conformance["href"].endswith("/conformance"),
    )

    r_conformance = requests.get(conformance["href"])
    errors += validate(
        "conformance must return 200", lambda: r_conformance.status_code == 200
    )

    if (ct := r_conformance.headers.get("content-type")).split(";")[
        0
    ] == "application/json":
        pass
    else:
        errors.append(
            f"conformance ({conformance}): must have content-type header 'application/json', actually '{ct}'"
        )

    try:
        conformance_json = r_conformance.json()
        warnings += validate(
            "Landing Page conforms to and conformance conformsTo must be the same",
            lambda: set(root_body.get("conformsTo"))
            == set(conformance_json["conformsTo"]),
        )
    except json.decoder.JSONDecodeError:
        errors.append(
            f"service-desc ({conformance}): must return JSON, instead got non-JSON text"
        )

    errors += validate(
        "/: Link[rel=data] must href /collections",
        lambda: href_for(links, "data") is not None,
    )

    # this is hard to figure out, since it's likely a mistake, but most apis can't undo it for
    # backwards-compat reasons
    warnings += validate(
        "/ Link[rel=collections] is a non-standard relation. Use Link[rel=data instead]",
        lambda: href_for(links, "collections") is None,
    )


def validate_search(
    root_body: Dict,
    post: bool,
    conforms_to: List,
    warnings: List[str],
    errors: List[str],
) -> None:
    links = root_body.get("links")
    root = href_for(links, "self")["href"]
    search = href_for(links, "search")
    if not search:
        errors.append("/: Link[rel=search] must exist when Item Search is implemented")
        return

    collections = href_for(links, "data")
    if collections:
        collections_url = collections.get("href")
    else:
        collections_url = f"{root}/collections"

    search_url = search["href"]
    r = requests.get(search_url)
    content_type: str = r.headers.get("content-type")
    if content_type == geojson_mt or content_type == geojson_charset_mt:
        pass
    else:
        errors.append(
            f"Search ({search_url}): must have content-type header '{geojson_mt}', actually '{content_type}'"
        )

    errors += validate(
        f"Search({search_url}): must return 200", lambda: r.status_code == 200
    )

    # todo: validate geojson, not just json
    try:
        r.json()
    except json.decoder.JSONDecodeError:
        errors.append(
            f"Search ({search_url}): must return JSON, instead got non-JSON text"
        )

    if any(search_fields_cc_regex.fullmatch(x) for x in conforms_to):
        print("STAC API - Item Search Fields extension conformance class found.")

    validate_search_limit(search_url, post, errors)
    validate_search_bbox_xor_intersects(search_url, post, errors)
    validate_search_bbox(search_url, post, errors)
    validate_search_datetime(search_url, warnings, errors)
    validate_search_ids(search_url, post, warnings, errors)
    validate_search_collections(search_url, collections_url, post, errors)
    validate_search_intersects(search_url, post, errors)


def validate_search_datetime(search_url: str, warnings: List[str], errors: List[str]):
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


def validate_search_bbox_xor_intersects(search_url: str, post: bool, errors: List[str]):
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


def validate_search_intersects(search_url: str, post: bool, errors: List[str]):
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


def validate_search_bbox(search_url: str, post: bool, errors: List[str]):
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
        param = [100.0, 0.0, 105.0, 1.0]
        r = requests.post(search_url, json={"bbox": param})
        if r.status_code != 200:
            errors.append(
                f"POST Search with bbox:{param} returned status code {r.status_code}"
            )
        else:
            try:
                r.json()
            except json.decoder.JSONDecodeError:
                errors.append(
                    f"POST Search with bbox:{param} returned non-json response: {r.text}"
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
        param = [100.0, 0.0, 0.0, 105.0, 1.0, 1.0]
        r = requests.post(search_url, json={"bbox": param})
        if r.status_code != 200:
            errors.append(
                f"POST Search with bbox:{param} returned status code {r.status_code}"
            )
        else:
            try:
                r.json()
            except json.decoder.JSONDecodeError:
                errors.append(
                    f"POST with bbox:{param} returned non-json response: {r.text}"
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
        param = [100.0, 1.0, 105.0, 0.0]
        r = requests.post(search_url, json={"bbox": param})
        if r.status_code != 400:
            errors.append(
                f"POST Search with bbox: {param} (lat 1 > lat 2) returned status code {r.status_code}, instead of 400"
            )

    # Invalid bbox - 1, 2, 3, 5, and 7 element array
    bboxes = [[0], [0, 0], [0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1]]

    for bbox in bboxes:
        param = ",".join((str(c) for c in bbox))
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


def validate_search_limit(search_url: str, post: bool, errors: List[str]):
    valid_limits = [1, 2, 10, 10000]
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

    invalid_limits = [-1, 0, 10001]
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
    r, item_ids: List[str], method: str, params: Dict, errors: List[str]
):
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
    search_url, item_ids: List[str], post: bool, errors: List[str]
):
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


def validate_search_ids(
    search_url: str, post: bool, warnings: List[str], errors: List[str]
):
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


def _validate_search_collections_request(
    r, coll_ids: List[str], method: str, params: Dict, errors: List[str]
):
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
    search_url, coll_ids: List[str], post: bool, errors: List[str]
):
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


def validate_search_collections(
    search_url: str, collections_url: str, post: bool, errors: List[str]
):
    collections_entity = requests.get(collections_url).json()
    if isinstance(collections_entity, List):
        errors.append("/collections entity is an array rather than an object")
        return
    collections = collections_entity.get("collections")
    if not collections:
        errors.append('/collections entity does not contain a "collections" attribute')
        return

    collection_ids = [x["id"] for x in collections]

    _validate_search_collections_with_ids(search_url, collection_ids, post, errors)

    for cid in collection_ids:
        _validate_search_collections_with_ids(search_url, [cid], post, errors)

    _validate_search_collections_with_ids(
        search_url, list(itertools.islice(collection_ids, 3)), post, errors
    )


def validate(error_str: str, p: Callable[[], bool]) -> List[str]:
    if not p():
        return [error_str]
    else:
        return []
