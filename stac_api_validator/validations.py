from typing import List, Tuple
from pystac.link import Link
from pystac_client import Client
import logging
import requests
from typing import Callable
import re
import json

# https://github.com/stac-utils/pystac/blob/4c7c775a6d0ca49d83dbec714855a189be759c8a/docs/concepts.rst#using-your-own-validator

# resolve_stac_object

core_cc_regex = re.compile('https://api\.stacspec\.org/.+/core')
oaf_cc_regex = re.compile(
    'https://api\.stacspec\.org/.+/ogcapi-features')
search_cc_regex = re.compile('https://api\.stacspec\.org/.+/item-search')

openapi_media_type = "application/vnd.oai.openapi+json;version=3.0"
geojson_mt = 'application/geo+json'
geojson_charset_mt = 'application/geo+json; charset=utf-8'

valid_datetimes = [
        "1985-04-12T23:20:50.52Z",
        "1985-04-12T23:20:50,52Z",
        "1996-12-19T16:39:57-00:00",
        "1996-12-19T16:39:57+00:00",
        "1996-12-19T16:39:57-08:00",
        "1996-12-19T16:39:57+08:00",
        "../1985-04-12T23:20:50.52Z",
        "1985-04-12T23:20:50.52Z/..",
        "/1985-04-12T23:20:50.52Z",
        "1985-04-12T23:20:50.52Z/",
        "1985-04-12T23:20:50.52Z/1986-04-12T23:20:50.52Z",
        "1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52Z+01:00",
        "1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52Z-01:00",

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
    ]

def validate_api(root_uri: str) -> Tuple[List[str], List[str]]:
    logger = logging.getLogger(__name__)

    warnings: List[str] = []
    errors: List[str] = []

    catalog: Client = Client.open(root_uri)

    if not catalog.conformance:
        errors.append("/ : 'conformsTo' field must be defined and non-empty. This field is required as of 1.0.0.")

    if not catalog.links:
        errors.append("/ : 'links' field must be defined and non-empty.")

    if catalog.conformance and \
       not any(core_cc_regex.match(x) for x in catalog.conformance) and \
       not any(oaf_cc_regex.match(x) for x in catalog.conformance) and \
       not any(search_cc_regex.match(x) for x in catalog.conformance):
        errors.append(
            "/ : 'conformsTo' must contain at least one STAC API conformance class.")

    # fail fast if there are errors with conformance or links so far
    if errors:
        return (warnings, errors)

    # todo: option to force validation and warn about non-existence of CC
    # todo: allow deprecated conformance classes, and warn
    # http://stacspec.org/spec/api/1.0.0-beta.1/core
    # http://stacspec.org/spec/api/1.0.0-beta.1/req/stac-search

    if any(core_cc_regex.match(x) for x in catalog.conformance):
        print("STAC API - Core conformance class found.")
        validate_core(catalog, warnings, errors)
    else:
        errors.append(
            "/ : 'conformsTo' must contain STAC API - Core conformance class.")

    if any(oaf_cc_regex.match(x) for x in catalog.conformance):
        print("STAC API - Features conformance class found.")
        validate_oaf(catalog, warnings, errors)

    if any(search_cc_regex.match(x) for x in catalog.conformance):
        print("STAC API - Item Search conformance class found.")
        validate_search(catalog, warnings, errors)

    catalog.validate()
    for collection in catalog.get_children():
        collection.validate()

    return (warnings, errors)


def validate_core(catalog: Client, warnings: List[str],
                  errors: List[str]) -> int:

    # Link rel=root
    root: Link = catalog.get_single_link('root')
    if root is not None:
        if root.media_type != "application/json":
            errors.append("root type is not application/json")
    else:
        warnings.append("root link missing")

    # Link rel=link
    _self: Link = catalog.get_single_link('self')
    if _self is not None:
        if _self.media_type != "application/json":
            errors.append("self type is not application/json")
    else:
        warnings.append("self link missing")

    # Link rel=service-desc
    service_desc: Link = catalog.get_single_link('service-desc')
    if not service_desc:
        warnings.append("/ : Link[rel=service-desc] should exist")
    else:
        if service_desc.media_type != openapi_media_type:
            errors.append(
                f"/ : Link[rel=service-desc] should have media_type '{openapi_media_type}'', actually '{service_desc.media_type}'")

        r_service_desc = requests.get(service_desc.get_absolute_href())

        errors += validate(
            "/ : Link[service-desc] must return 200",
            lambda: r_service_desc.status_code == 200)

        if (ct := r_service_desc.headers.get('content-type')) == openapi_media_type:
            pass
        else:
            errors.append(
                f"service-desc ({service_desc.get_absolute_href()}): should have content-type header '{openapi_media_type}'', actually '{ct}'")

        try:
            r_service_desc.json()
        except json.decoder.JSONDecodeError as e:
            errors.append(
                f"service-desc ({service_desc.get_absolute_href()}): should return JSON, instead got non-JSON text")

    # Link rel=service-doc
    service_doc: Link = catalog.get_single_link('service-doc')
    if not service_doc:
        warnings.append("/ : Link[rel=service-doc] should exist")
    else:
        if service_doc.media_type != "text/html":
            errors.append("service-doc type is not text/html")

        r_service_doc = requests.get(service_doc.get_absolute_href())

        errors += validate(
            "/ : Link[service-doc] must return 200",
            lambda: r_service_doc.status_code == 200)

        if (ct := r_service_doc.headers.get('content-type')).startswith('text/html'):
            pass
        else:
            errors.append(
                f"service-doc ({service_doc.get_absolute_href()}): should have content-type header 'text/html', actually '{ct}'")

    # try:
    #     r_service_doc.html()
    # except json.decoder.JSONDecodeError as e:
    #     errors.append(
    #         f"service-doc ({service_doc.get_absolute_href()}): should return JSON, instead got non-JSON text")


def validate_oaf(catalog: Client, warnings: List[str],
                 errors: List[str]) -> int:

    conformance = catalog.get_single_link('conformance')
    errors += validate(
        "/ Link[rel=conformance] should href /conformance",
        lambda: conformance and conformance.target.endswith("/conformance")
    )

    r_conformance = requests.get(conformance.get_absolute_href())

    errors += validate(
        "conformance must return 200",
        lambda: r_conformance.status_code == 200)

    if (ct := r_conformance.headers.get('content-type')) == 'application/json':
        pass
    else:
        errors.append(
            f"conformance ({conformance.get_absolute_href()}): should have content-type header 'application/json', actually '{ct}'")

    # todo: validate conformance link is properly-formed.
    # currently fails due to a bug in pystac
    # conformance = catalog.get_stac_objects('conformance')
    try:
        conformance_json = r_conformance.json()
        warnings += validate(
            "Landing Page conforms to and conformance conformsTo should be the same",
            lambda: catalog.conformance == conformance_json['conformsTo'])
    except json.decoder.JSONDecodeError as e:
        errors.append(
            f"service-desc ({conformance.get_absolute_href()}): should return JSON, instead got non-JSON text")

    errors += validate(
        "/ Link[rel=data] should href /collections",
        lambda: catalog.get_single_link('data')
    )

    # this is hard to figure out, since it's likely a mistake, but most apis can't undo it for
    # backwards-compat reasons
    warnings += validate(
        "/ Link[rel=collections] is a non-standard relation. Use Link[rel=data instead]",
        lambda: not catalog.get_single_link('collections')
    )

# todo: child and children?


def validate_search(catalog: Client, warnings: List[str],
                    errors: List[str]) -> int:

    search: Link = catalog.get_single_link('search')
    r = requests.get(search.get_absolute_href())
    content_type: str = r.headers.get('content-type')
    if (content_type == geojson_mt or content_type == geojson_charset_mt):
        pass
    else:
        errors.append(
            f"Search ({search.get_absolute_href()}): should have content-type header '{geojson_mt}'', actually '{content_type}'")

    errors += validate(
        f"Search({search.get_absolute_href()}): should return 200",
        lambda: r.status_code == 200)

    # todo: validate geojson, not just json
    try:
        r.json()
    except json.decoder.JSONDecodeError as e:
        errors.append(
            f"Service Description({search.get_absolute_href()}): should return JSON, instead got non-JSON text")

    # todo: run a real query
    mysearch = catalog.search(max_items=1)
    mysearch.items_as_collection

    # validate_search_limit()
    validate_search_bbox(search.get_absolute_href(), warnings, errors)
    validate_search_datetime(search.get_absolute_href(), warnings, errors)
    # validate_search_intersects()
    # validate_search_ids()
    # validate_search_collections(search.get_absolute_href(), warnings, errors)

def validate_search_datetime(
    search_url: str,
    warnings: List[str],
    errors: List[str] = []
):
    # find an Item and try to use its datetime value in a query
    r = requests.get(search_url)
    dt = r.json()["features"][0]["properties"]["datetime"]
    r = requests.get(search_url, params={"datetime": dt})
    if r.status_code != 200:
        errors.append(
            f"Search with datetime={dt} extracted from an Item returned status code {r.status_code}")
    elif len(r.json()["features"]) == 0:
        errors.append(
            f"Search with datetime={dt} extracted from an Item returned no results.")

    for dt in valid_datetimes:
        r = requests.get(search_url, params={"datetime": dt})
        if r.status_code != 200:
            errors.append(
                f"Search with datetime={dt} returned status code {r.status_code}")
            continue
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors.append(
                f"Search with datetime={dt} returned non-json response")
    
    for dt in invalid_datetimes:
        r = requests.get(search_url, params={"datetime": dt})
        if r.status_code != 400:
            errors.append(
                f"Search with datetime={dt} returned status code {r.status_code} instead of 400")
            continue


def validate_search_bbox(
    search_url: str,
    warnings: List[str],
    errors: List[str] = []
):
    # Valid GET query
    param = "100.0, 0.0, 105.0, 1.0"
    r = requests.get(search_url, params={"bbox": param })
    if r.status_code != 200:
        errors.append(
            f"GET Search with bbox={param} returned status code {r.status_code}")
    else:
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors.append(
                f"GET Search with bbox={param} returned non-json response: {r.text}")

    # Valid POST query
    param = [100.0, 0.0, 105.0, 1.0]
    r = requests.post(search_url, json={"bbox": param})
    if r.status_code != 200:
        errors.append(
            f"POST Search with bbox:{param} returned status code {r.status_code}")
    else: 
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors.append(
                f"POST Search with bbox:{param} returned non-json response: {r.text}")

    # Valid 3D GET query
    param = "100.0,0.0,0.0,105.0,1.0,1.0"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 200:
        errors.append(
            f"GET Search with bbox={param} returned status code {r.status_code}")
    else:        
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors.append(
                f"GET with bbox={param} returned non-json response: {r.text}")

    # Valid 3D POST query
    param = [100.0, 0.0, 0.0, 105.0, 1.0, 1.0]
    r = requests.post(search_url, json={"bbox": param})
    if r.status_code != 200:
        errors.append(
            f"POST Search with bbox:{param} returned status code {r.status_code}")
    else:
        try:
            r.json()
        except json.decoder.JSONDecodeError:
            errors.append(
                f"POST with bbox:{param} returned non-json response: {r.text}")

    # Invalid GET query with coordinates in brackets
    param = "[100.0, 0.0, 105.0, 1.0]"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 400:
        errors.append(
            f"GET Search with bbox={param} returned status code {r.status_code}, instead of 400")

    # Invalid POST query with CSV string of coordinates
    param = "100.0, 0.0, 105.0, 1.0"
    r = requests.post(search_url, json={"bbox": param})
    if r.status_code != 400:
        errors.append(
            f"POST Search with bbox:\"{param}\" returned status code {r.status_code}, instead of 400")

    # Invalid bbox - lat 1 > lat 2
    param = "100.0, 1.0, 105.0, 0.0"
    r = requests.get(search_url, params={"bbox": param})
    if r.status_code != 400:
        errors.append(
            f"GET Search with bbox=param (lat 1 > lat 2) returned status code {r.status_code}, instead of 400")

    param = [100.0, 1.0, 105.0, 0.0]
    r = requests.post(search_url, json={"bbox": param})
    if r.status_code != 400:
        errors.append(
            f"POST Search with bbox: {param} (lat 1 > lat 2) returned status code {r.status_code}, instead of 400")

    # Invalid bbox - 1, 2, 3, 5, and 7 element array
    bboxes = [ [0], [0, 0], [0, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1] ]

    for bbox in bboxes:
        param = ",".join((str(c) for c in bbox))
        r = requests.get(search_url, params={"bbox": param })
        if r.status_code != 400:
            errors.append(
                f"GET Search with bbox={param} returned status code {r.status_code}, instead of 400")

        r = requests.post(search_url, json={"bbox": bbox})
        if r.status_code != 400:
            errors.append(
                f"POST Search with bbox:{bbox} returned status code {r.status_code}, instead of 400")


def validate(error_str: str, p: Callable[[], bool]) -> List[str]:
    if not p():
        return [error_str]
    else:
        return []
