# STAC API Validator

**Work in Progress** -- this currently only validates a subset of behavior, notably conformance classes, links, 
and datetime and bbox parameters

This validation suite focuses on validating STAC API interactions.  Tools such as pystac and stac4s do a 
good job of validating STAC objects (Catalog, Collection, Item). This suite focuses on the API aspects. 

The three key concepts within a STAC API are:
1. Conformance classes advertising the capabilities of the API
2. Link relations between resources within the API (hypermedia)
3. Parameters that filter search results

The conformance classes, as defined in the `conformsTo` field of the Landing Page (root, `/`), advertise to 
clients which capabilities are available in the API. Without this field, a client would not even be able to tell that a
root URI was a STAC API. 

The link relations define how to navigate a STAC catalog through parent-child links and find resources such as the OpenAPI specification. While many OGC API and STAC API endpoint have a fixed value (e.g., `/collections`), it is preferable for clients discover the paths via hypermedia. 

The parameters that filter results apply to the Items resource and Item Search endpoints.

The current validity status of several popular STAC API implementations can be found [here](COMPLIANCE_REPORT.md).

## Validating STAC API conformance

Create new venv with python >= 3.9:

```
python3.9 -m venv --prompt stac-api-validator .venv
source ./.venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Run:

```
python stac_api_validator/validate.py --root https://cmr.earthdata.nasa.gov/stac/LARC_ASDC 
```

Example output:

```
Validating https://cmr.earthdata.nasa.gov/stac/LARC_ASDC ...
STAC API - Core conformance class found.
STAC API - Item Search conformance class found.
warnings: none
errors:
- service-desc (https://api.stacspec.org/v1.0.0-beta.1/openapi.yaml): should have content-type header 'application/vnd.oai.openapi+json;version=3.0'', actually 'text/yaml'
- service-desc (https://api.stacspec.org/v1.0.0-beta.1/openapi.yaml): should return JSON, instead got non-JSON text
- GET Search with bbox=100.0, 0.0, 105.0, 1.0 returned status code 400
- POST Search with bbox:[100.0, 0.0, 105.0, 1.0] returned status code 502
- GET Search with bbox=100.0,0.0,0.0,105.0,1.0,1.0 returned status code 400
- POST Search with bbox:[100.0, 0.0, 0.0, 105.0, 1.0, 1.0] returned status code 400
```

## Validating OGC API Features - Part 1 compliance

A STAC API that conforms to the "STAC API - Features" conformance class will also be a valid implementation 
of OGC API Features - Part 1. In general, this validator focuses on those aspects of API behavior that are
different between STAC and OGC. It is recommended that implementers also use the [OGC API Features - Part 1 
validation test suite](https://cite.opengeospatial.org/teamengine/about/ogcapi-features-1.0/1.0/site/) to
validate conformance. 

Full instructions are available at the link above, but the simplest way to run this is with:

```
docker run -p 8081:8080 ogccite/ets-ogcapi-features10
```

Then, open [http://localhost:8081/teamengine/](http://localhost:8081/teamengine/) and login with the 
username and password `ogctest`, `Create a new session`, with Organization `OGC`, Specification `OGC API - Features`, `Start a new test session`, input he root URL for the service, and `Start`.

## Common Mistakes

- incorrect `conformsTo` in the Landing Page. This was added between STAC API 0.9 and 1.0. It should be the same as the value in the `conformsTo` in the OAFeat `/conformance` endpoint.
- OGC API Features uses `data` relation link relation at the root to point to the Collections endpoint (`/collections`), not `collections` relation
- media type for link relation `service-desc` and endpoint is `application/vnd.oai.openapi+json;version=3.0` (not `application/json`) and link relation `search` and endpoint is `application/geo+json` (not `application/json`)
- Use of OCG API "req" urls instead of "conf" urls, e.g. `http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core` should be used, not `http://www.opengis.net/spec/ogcapi-features-1/1.0/req/core`
