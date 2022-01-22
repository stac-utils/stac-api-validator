# Compliance Report

This document shows how well several popular STAC API implementations conform to STAC API.

Many (if not all) of these API are in production use, so the fact that they have validation problems 
should not be seen as a significant concern.  This validation suite is quite strict, so it finds 
many obscure issues that can usually be worked around. Many of the defects are around the 
correct advertisement of conformance classes and links to support hypermedia, and these more "advanced" 
capabilities are only now starting to be fully used in tools like pystac-client. 

## Open Source

### stac-fastapi - sqlalchemy 

URL: http://0.0.0.0:8081

Date: 19-Jan-2022

Output:
```
Validating http://0.0.0.0:8081
STAC API - Core conformance class found.
STAC API - Features conformance class found.
STAC API - Item Search conformance class found.
warnings:
- Search with datetime=1937-01-01T12:00:27.87+0100 returned status code 200 instead of 400
- Search with datetime=1985-12-12T23:20:50.52 returned status code 200 instead of 400
errors:
- Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- Search with datetime=1985-04-12t23:20:50.000z returned status code 400
```

### stac-fastapi - pgstac 

URL: http://0.0.0.0:8082

Date: 19-Jan-2022

Output:
```
Validating http://0.0.0.0:8082
STAC API - Core conformance class found.
STAC API - Features conformance class found.
STAC API - Item Search conformance class found.
warnings:
- Search with datetime=1937-01-01T12:00:27.87+0100 returned status code 200 instead of 400
- Search with datetime=1985-12-12T23:20:50.52 returned status code 200 instead of 400
errors:
- Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- Search with datetime=1985-04-12t23:20:50.000z returned status code 400
- GET Search with {'ids': 'fe916452-ba6f-4631-9154-c249924a122d'} returned items with ids other than specified one
- POST Search with {'ids': ['fe916452-ba6f-4631-9154-c249924a122d']} returned items with ids other than specified one
- GET Search with {'ids': 'fe916452-ba6f-4631-9154-c249924a122d,f7f164c9-cfdf-436d-a3f0-69864c38ba2a'} returned items with ids other than specified one
- POST Search with {'ids': ['fe916452-ba6f-4631-9154-c249924a122d', 'f7f164c9-cfdf-436d-a3f0-69864c38ba2a']} returned items with ids other than specified one
```

### stac-fastapi - Planetary Computer

based on stac-fastapi

URL: https://planetarycomputer.microsoft.com/api/stac/v1/

Date: 19-Jan-2022

Output:
```
Validating https://planetarycomputer.microsoft.com/api/stac/v1/
STAC API - Core conformance class found.
STAC API - Features conformance class found.
STAC API - Item Search conformance class found.
warnings:
- Search with datetime=1985-04-12 returned status code 200 instead of 400
- Search with datetime=1937-01-01T12:00:27.87+0100 returned status code 200 instead of 400
- Search with datetime=1985-12-12T23:20:50.52 returned status code 200 instead of 400
- Search with datetime=1985-04-12T23:20:50,Z returned status code 200 instead of 400
errors:
- GET Search with {'limit': 10000} returned status code 400
- POST Search with {'limit': 10000} returned status code 400
- GET Search with bbox=100.0,0.0,0.0,105.0,1.0,1.0 returned status code 500
- POST Search with bbox:[100.0, 0.0, 0.0, 105.0, 1.0, 1.0] returned status code 500
- Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- Search with datetime=37-01-01T12:00:27.87Z returned status code 500 instead of 400
```

# stac-cmr

URL: https://cmr.earthdata.nasa.gov/stac/USGS_EROS

Date: 19-Jan-2022

Output:
```
Validating https://cmr.earthdata.nasa.gov/stac/USGS_EROS
STAC API - Core conformance class found.
STAC API - Item Search conformance class found.
STAC API - Item Search Fields extension conformance class found.
warnings:
- Search with datetime=1985-04-12 returned status code 200 instead of 400
errors:
- / : Link[rel=service-desc] should have media_type 'application/vnd.oai.openapi+json;version=3.0', actually 'application/vnd.oai.openapi;version=3.0'
- service-desc ({'rel': 'service-desc', 'href': 'https://api.stacspec.org/v1.0.0-beta.1/openapi.yaml', 'title': 'OpenAPI Doc', 'type': 'application/vnd.oai.openapi;version=3.0'}): should have content-type header 'application/vnd.oai.openapi+json;version=3.0', actually 'text/yaml'
- service-desc ({'rel': 'service-desc', 'href': 'https://api.stacspec.org/v1.0.0-beta.1/openapi.yaml', 'title': 'OpenAPI Doc', 'type': 'application/vnd.oai.openapi;version=3.0'}): should return JSON, instead got non-JSON text
- GET Search with {'limit': 10000} returned status code 400
- POST Search with {'limit': 10000} returned status code 400
- GET Search with {'limit': 0} returned status code 200, should be 400
- POST Search with {'limit': 0} returned status code 200, should be 400
- GET Search with bbox=100.0,0.0,105.0,1.0 returned status code 400
- GET Search with bbox=100.0,0.0,0.0,105.0,1.0,1.0 returned status code 400
- POST Search with bbox:[100.0, 0.0, 0.0, 105.0, 1.0, 1.0] returned status code 400
- Search with datetime=1972-07-25T00:00:00.000Z extracted from an Item returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1996-12-19T16:39:57-00:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57+00:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57-08:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57+08:00 returned status code 400
- Search with datetime=../1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/.. returned status code 400
- Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/1986-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52+01:00 returned status code 400
- Search with datetime=1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52-01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.87+01:00 returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1937-01-01T12:00:27.8710+01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.8+01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.8Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.000+03:00 returned status code 400
- Search with datetime=2020-07-23T00:00:00+03:00 returned status code 400
- Search with datetime=1985-04-12t23:20:50.000z returned status code 400
- Search with datetime=2020-07-23T00:00:00Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.0Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.01Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.012Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.0123Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.01234Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.012345Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.0123456Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.01234567Z returned status code 400
- Search with datetime=2020-07-23T00:00:00.012345678Z returned status code 400
```

# resto

URL: https://tamn.snapplanet.io/

Date: 19-Jan-2022

Output
```
Validating https://tamn.snapplanet.io/
STAC API - Core conformance class found.
STAC API - Features conformance class found.
STAC API - Item Search conformance class found.
warnings:
- Search with datetime=1985-04-12T23:20:50,52Z returned status code 200 instead of 400
errors:
- GET Search with {'limit': 10000} returned status code 400
```

# Franklin

URL: https://franklin.nasa-hsi.azavea.com/

Date: 19-Jan-2022

```
STAC API - Core conformance class found.
STAC API - Features conformance class found.
STAC API - Item Search conformance class found.
warnings:
- / : 'conformsTo' contains OGC API conformance classes using 'req' instead of 'conf': ['http://www.opengis.net/spec/ogcapi-features-1/1.0/req/core', 'http://www.opengis.net/spec/ogcapi-features-1/1.0/req/oas30', 'http://www.opengis.net/spec/ogcapi-features-1/1.0/req/geojson'].
- / : Link[rel=service-doc] should exist
- Search with datetime=1985-04-12T23:20:50.Z returned status code 200 instead of 400
- Search with datetime=1986-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z returned status code 200 instead of 400
errors:
- / : Link[rel=root] should exist
- service-desc ({'href': 'https://franklin.nasa-hsi.azavea.com/open-api/spec.yaml', 'rel': 'service-desc', 'type': 'application/vnd.oai.openapi+json;version=3.0', 'title': 'Open API 3 Documentation'}): should have content-type header 'application/vnd.oai.openapi+json;version=3.0', actually 'text/plain; charset=UTF-8'
- service-desc ({'href': 'https://franklin.nasa-hsi.azavea.com/open-api/spec.yaml', 'rel': 'service-desc', 'type': 'application/vnd.oai.openapi+json;version=3.0', 'title': 'Open API 3 Documentation'}): should return JSON, instead got non-JSON text
- Search (https://franklin.nasa-hsi.azavea.com/search): should have content-type header 'application/geo+json', actually 'application/json'
- GET Search with {'limit': 10000} returned status code 503
- POST Search with {'limit': 10000} returned status code 503
- GET Search with {'limit': 0} returned status code 200, should be 400
- POST Search with {'limit': 0} returned status code 200, should be 400
- GET Search with {'limit': 10001} returned status code 503, should be 400
- POST Search with {'limit': 10001} returned status code 503, should be 400
- GET Search with bbox=param (lat 1 > lat 2) returned status code 200, instead of 400
- POST Search with bbox: [100.0, 1.0, 105.0, 0.0] (lat 1 > lat 2) returned status code 200, instead of 400
- GET Search with bbox=0,0,0,1,1 returned status code 200, instead of 400
- GET Search with bbox=0,0,0,1,1,1,1 returned status code 200, instead of 400
- Search with datetime=1996-12-19T16:39:57-00:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57+00:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57-08:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57+08:00 returned status code 400
- Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- Search with datetime=1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52+01:00 returned status code 400
- Search with datetime=1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52-01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.87+01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.8710+01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.8+01:00 returned status code 400
- Search with datetime=2020-07-23T00:00:00.000+03:00 returned status code 400
- Search with datetime=2020-07-23T00:00:00+03:00 returned status code 400
```

# Staccato

URL: https://staccato.space/

Date: 2-Jul-2021

Output:
```
Validating https://staccato.space/
warnings: none
errors:
- / : 'conformsTo' must contain at least one STAC API conformance class.
```

## Proprietary

### Earth OnDemand 

URL: https://eod-catalog-svc-prod.astraea.earth/

Date: 2-Jul-2021

```
Validating https://eod-catalog-svc-prod.astraea.earth/
warnings: none
errors:
- / : 'conformsTo' must contain at least one STAC API conformance class.
```