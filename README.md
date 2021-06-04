# STAC API Validator

This validation suite focuses on validating STAC API interactions.  Tools such as pystac and stac4s do a 
good job of validating STAC objects (Catalog, Collection, Item). This suite focuses on the API aspects. 

The two key concepts within a STAC API are:
1. Conformance classes defining the capabilities of the API
2. Link relations between resources within the API

The conformance classes, as defined in the `conformsTo` field of the Landing Page (root, `/`), advertise to 
clients which capabilities are available in the API. Without this field, a client would not even be able to tell that a
root URI was a STAC API. 

The link relations define how to navigate a STAC catalog through parent-child links and find resources such as the OpenAPI specification. While many OGC API and STAC API endpoint have a fixed value (e.g., `/collections`), it is preferable for clients discover the paths via hypermedia. 

## Running

`validate.py` expects a single argument pointing to the root of a STAC API.

`validate_all.py` runs validation against several public STAC API endpoints.

## List of Public STAC API URLs

* https://earth-search.aws.element84.com/v0
* https://planetarycomputer.microsoft.com/api/stac/v1/
* https://eod-catalog-svc-prod.astraea.earth/
* https://services.sentinel-hub.com/api/v1/catalog/
* https://api.radiant.earth/mlhub/v1/
* https://earthengine.openeo.org/v1.0
* https://cmr.earthdata.nasa.gov/stac -- a catalog that links to other STAC API roots
* https://cmr.earthdata.nasa.gov/stac/LARC_ASDC
* https://franklin.nasa-hsi.azavea.com/
* https://tamn.snapplanet.io/
* https://data.geo.admin.ch/api/stac/v0.9/

## Common Mistakes

* incorrect `conformsTo` in the Landing Page. This was added between STAC API 0.9 and 1.0. It should be the same as the value in the `conformsTo` in the OAFeat `/conformance` endpoint.
* OGC API Features uses `data` relation link relation at the root to point to the Collections endpoint (`/collections`), not `collections` relation
* media type for link relation `service-desc` and endpoint is `application/vnd.oai.openapi+json;version=3.0` (not `application/json`) and link relation `search` and endpoint is `application/geo+json` (not `application/json`)
