# Compliance Report

This document shows how well several popular STAC API implementations conform to STAC API.

Many (if not all) of these API are in production use, so the fact that they have validation problems 
should not be seen as a significant concern.  This validation suite is quite strict, so it finds 
many obscure issues that can usually be worked around. Many of the defects are around the 
correct advertisement of conformance classes and links to support hypermedia, and these more "advanced" 
capabilities are only now starting to be fully used in tools like pystac-client. 

## Open Source

### stac-fastapi

URL: https://planetarycomputer.microsoft.com/api/stac/v1/

Date: 2-Jul-2021

Output:
```
Validating https://planetarycomputer.microsoft.com/api/stac/v1/ ...
STAC API - Core conformance class found.
STAC API - Item Search conformance class found.
warnings:
- / : Link[rel=service-desc] should exist
- / : Link[rel=service-doc] should exist
errors:
- Search (https://planetarycomputer.microsoft.com/api/stac/v1/search): should have content-type header 'application/geo+json'', actually 'application/json'
- GET Search with bbox=100.0,0.0,0.0,105.0,1.0,1.0 returned status code 500
- POST Search with bbox:[100.0, 0.0, 0.0, 105.0, 1.0, 1.0] returned status code 500
- GET Search with bbox=param (lat 1 > lat 2) returned status code 200, instead of 400
- POST Search with bbox: [100.0, 1.0, 105.0, 0.0] (lat 1 > lat 2) returned status code 200, instead of 400
- Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- Search with datetime=1985-04-12 returned status code 200 instead of 400
- Search with datetime=1937-01-01T12:00:27.87+0100 returned status code 200 instead of 400
- Search with datetime=37-01-01T12:00:27.87Z returned status code 200 instead of 400
- Search with datetime=1985-12-12T23:20:50.52 returned status code 200 instead of 400
- Search with datetime=1985-04-12T23:20:50,Z returned status code 200 instead of 400
```

# stac-cmr

URL: https://cmr.earthdata.nasa.gov/stac/LARC_ASDC 

Date: 2-Jul-2021

Output:
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
- Search with datetime=1978-01-01T00:00:00.000Z extracted from an Item returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50,52Z returned status code 400
- Search with datetime=1996-12-19T16:39:57-00:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57+00:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57-08:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57+08:00 returned status code 400
- Search with datetime=../1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/.. returned status code 400
- Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/1986-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52Z+01:00 returned status code 400
- Search with datetime=1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52Z-01:00 returned status code 400
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
- Search with datetime=1985-04-12 returned status code 200 instead of 400
```

# resto

URL: https://tamn.snapplanet.io/

Date: 2-Jul-2021

Output
```
Validating https://tamn.snapplanet.io/
warnings: none
errors:
- API does not conform to {ConformanceClasses.STAC_API_CORE}. Must contain one of the following URIs to conform (preferably the first):
        https://api.stacspec.org/v1.0.0-beta.1/core
        http://stacspec.org/spec/api/1.0.0-beta.1/core.
```

# Franklin

URL: https://franklin.nasa-hsi.azavea.com/

Date: 2-Jul-2021

```
Validating https://franklin.nasa-hsi.azavea.com/
STAC API - Core conformance class found.
STAC API - Features conformance class found.
STAC API - Item Search conformance class found.
warnings:
- / : Link[rel=service-doc] should exist
errors:
- service-desc (https://franklin.nasa-hsi.azavea.com/open-api/spec.yaml): should have content-type header 'application/vnd.oai.openapi+json;version=3.0'', actually 'text/plain; charset=UTF-8'
- service-desc (https://franklin.nasa-hsi.azavea.com/open-api/spec.yaml): should return JSON, instead got non-JSON text
- Search (https://franklin.nasa-hsi.azavea.com/search): should have content-type header 'application/geo+json'', actually 'application/json'
- GET Search with bbox=param (lat 1 > lat 2) returned status code 200, instead of 400
- POST Search with bbox: [100.0, 1.0, 105.0, 0.0] (lat 1 > lat 2) returned status code 200, instead of 400
- GET Search with bbox=0,0,0,1,1 returned status code 200, instead of 400
- GET Search with bbox=0,0,0,1,1,1,1 returned status code 200, instead of 400
- Search with datetime=1985-04-12T23:20:50,52Z returned status code 400
- Search with datetime=1996-12-19T16:39:57-00:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57+00:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57-08:00 returned status code 400
- Search with datetime=1996-12-19T16:39:57+08:00 returned status code 400
- Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- Search with datetime=1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52Z+01:00 returned status code 400
- Search with datetime=1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52Z-01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.87+01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.8710+01:00 returned status code 400
- Search with datetime=1937-01-01T12:00:27.8+01:00 returned status code 400
- Search with datetime=2020-07-23T00:00:00.000+03:00 returned status code 400
- Search with datetime=2020-07-23T00:00:00+03:00 returned status code 400
- Search with datetime=1985-04-12T23:20:50.Z returned status code 200 instead of 400
- Search with datetime=1986-04-12T23:20:50.52Z/1985-04-12T23:20:50.52Z returned status code 200 instead of 400
```

# Staccato

URL: https://staccato.space/

Date: 2-Jul-2021

Output:
```
Validating https://staccato.space/
warnings: none
errors:
- API does not conform to {ConformanceClasses.STAC_API_CORE}. Must contain one of the following URIs to conform (preferably the first):
        https://api.stacspec.org/v1.0.0-beta.1/core
        http://stacspec.org/spec/api/1.0.0-beta.1/core.
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