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

def validate_api(root_uri: str) -> Tuple[List[str], List[str]]:
    logger = logging.getLogger(__name__)

    warnings: List[str] = []
    errors: List[str] = []

    catalog: Client = Client.open(root_uri)

    if not catalog.conformance:
        errors.append("/ : 'conformsTo' field must be defined and non-empty.")

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
                  errors: List[str] = []) -> int:

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
    if service_desc is not None:
        if service_desc.media_type != openapi_media_type:
            errors.append(
                f"/ : Link[rel=service-desc] should have media_type '{openapi_media_type}'', actually '{service_desc.media_type}'")
    else:
        warnings.append("/ : Link[rel=service-desc] should exist")

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
    if service_doc is None:
        warnings.append("/ : Link[rel=service-doc] should exist")
    else:
        if service_doc.media_type != "text/html":
            errors.append("service-doc type is not text/html")

        r_service_doc = requests.get(service_doc.get_absolute_href())

        errors += validate(
            "/ : Link[service-doc] must return 200",
            lambda: r_service_doc.status_code == 200)

        if (ct := r_service_doc.headers.get('content-type')) == 'text/html':
            pass
        else:
            errors.append(
                f"service-doc ({service_doc.get_absolute_href()}): should have content-type header '{openapi_media_type}'', actually '{ct}'")

    # try:
    #     r_service_doc.html()
    # except json.decoder.JSONDecodeError as e:
    #     errors.append(
    #         f"service-doc ({service_doc.get_absolute_href()}): should return JSON, instead got non-JSON text")


def validate_oaf(catalog: Client, warnings: List[str],
                 errors: List[str] = []) -> int:

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
                    errors: List[str] = []) -> int:

    search: Link = catalog.get_single_link('search')
    geojson = 'application/geo+json'
    r = requests.get(search.get_absolute_href())
    if (ct := r.headers.get('content-type')) == geojson:
        pass
    else:
        errors.append(
            f"Search ({search.get_absolute_href()}): should have content-type header '{geojson}'', actually '{ct}'")

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


def validate(error_str: str, p: Callable[[], bool]) -> List[str]:
    if not p():
        return [error_str]
    else:
        return []
