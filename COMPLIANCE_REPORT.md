# Compliance Report

This document shows how well several popular STAC API implementations conform to STAC API.

Many (if not all) of these APIs are in production use, so the fact that they have validation problems
should not be seen as a significant concern. This validation suite is quite strict, so it finds
many obscure issues that can usually be worked around. Many of the defects are around the
correct advertisement of conformance classes and links to support hypermedia, and these more "advanced"
capabilities are only now starting to be fully used in tools like pystac-client.

## Open Source Implementations

### stac-fastapi - sqlalchemy

<https://github.com/stac-utils/stac-fastapi>

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

<https://github.com/stac-utils/stac-fastapi>

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

### stac-fastapi-elasticsearch

<https://github.com/stac-utils/stac-fastapi-elasticsearch>

URL: http://localhost:8083

Date: 17-Mar-2022

Output:

```
Validating http://localhost:8083
STAC API - Core conformance class found.
STAC API - Features conformance class found.
STAC API - Item Search conformance class found.
warnings:
- GET Search with datetime=../.. returned status code 200 instead of 400
- GET Search with datetime=1937-01-01T12:00:27.87+0100 returned status code 200 instead of 400
- GET Search with datetime=1985-12-12T23:20:50.52 returned status code 200 instead of 400
errors:
- GET Search with bbox and intersects returned status code 200
- GET Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- GET Search with datetime=1985-04-12t23:20:50.000z returned status code 400
- POST Search with intersects:{'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [100.0, 0.0]}, {'type': 'LineString', 'coordinates': [[101.0, 0.0], [102.0, 1.0]]}]} returned status code 400
```

### stac-server

<https://github.com/stac-utils/stac-fastapi-elasticsearch>

URL: http://localhost:8083

Date: 17-Mar-2022

Output:

```
Validating http://localhost:3000
STAC API - Core conformance class found.
STAC API - Features conformance class found.
STAC API - Item Search conformance class found.
STAC API - Item Search Fields extension conformance class found.
warnings: none
errors: none
```

### resto

<https://github.com/jjrom/resto>

TBD.

### Franklin

<https://github.com/azavea/franklin>

TBD.

### stac-cmr

TBD.

### staccato

Non-compliant with 1.0.0-x

## Server Instances

### Microsoft Planetary Computer (stac-fastapi)

URL: https://planetarycomputer.microsoft.com/api/stac/v1

Date: 03-Oct-2022

Output:

```
$ poetry run stac-api-validator --root-url https://planetarycomputer.microsoft.com/api/stac/v1 \
   --conformance features --conformance item-search --collection sentinel-2-l2a \
   --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'

Validating https://planetarycomputer.microsoft.com/api/stac/v1
STAC API - Core conformance class found.
STAC API - Features conformance class found.
WARNING: Collections validation is not yet fully implemented.
WARNING: Features validation is not yet fully implemented.
STAC API - Item Search conformance class found.
STAC API - Item Search - Filter extension conformance class found.
warnings:
- GET Search with datetime=1985-04-12 returned status code 200 instead of 400
- GET Search with datetime=1937-01-01T12:00:27.87+0100 returned status code 200 instead of 400
- GET Search with datetime=1985-12-12T23:20:50.52 returned status code 200 instead of 400
- GET Search with datetime=1985-04-12T23:20:50,Z returned status code 200 instead of 400
- [Filter Ext] /: pre-1.0.0-rc.1 Filter Extension conformance classes are advertised.
errors:
- GET Search with bbox and intersects returned status code 200
- GET Search with bbox=100.0,0.0,0.0,105.0,1.0,1.0 returned status code 500
- POST Search with bbox:[100.0, 0.0, 0.0, 105.0, 1.0, 1.0] returned status code 500
- GET Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- GET Search with datetime=37-01-01T12:00:27.87Z returned status code 500 instead of 400
- GET Search with ids and non-intersecting bbox returned results, indicating the ids parameter is overriding the bbox parameter. All parameters are applied equally since STAC API 1.0.0-beta.1
- POST Search with ids and non-intersecting bbox returned results, indicating the ids parameter is overriding the bbox parameter. All parameters are applied equally since STAC API 1.0.0-beta.1
- [Item Search] GET Search results for intersects={"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]} do not all intersect
- [Item Search Filter Ext] / : 'http://www.opengis.net/def/rel/ogc/1.0/queryables' (Queryables) link relation missing
- [Item Search - Filter Ext] Queryables 'https://planetarycomputer.microsoft.com/api/stac/v1/queryables' returned Content-Type header 'application/json', must return 'application/schema+json'
- [Item Search - Filter Ext] Queryables 'https://planetarycomputer.microsoft.com/api/stac/v1/queryables' '$id' value invalid, must be same as queryables url
- [Item Search Filter Ext] GET datetime = TIMESTAMP('2021-04-08T04:39:23Z') returned status code 500
- [Item Search Filter Ext] POST {'op': '=', 'args': [{'property': 'datetime'}, {'timestamp': '2021-04-08T04:39:23Z'}]} returned status code 500
```

### Snap Planet (resto)

URL: https://tamn.snapplanet.io/

Date: 06-Oct-2022

Output

```
$ poetry run stac-api-validator --root-url https://tamn.snapplanet.io  --conformance features --conformance item-search --conformance filter --collection S2 --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'
Validating https://tamn.snapplanet.io
STAC API - Core conformance class found.
STAC API - Features conformance class found.
WARNING: Collections validation is not yet fully implemented.
WARNING: Features validation is not yet fully implemented.
STAC API - Item Search conformance class found.
STAC API - Item Search - Filter extension conformance class found.
CQL2 - CQL2-Text conformance class found.
CQL2 - Basic CQL2 conformance class found.
CQL2 - Basic Spatial Operators conformance class found.
warnings: none
errors:
- [Item Search Filter Ext] GET eo:cloud_cover > 50 OR eo:cloud_cover < 10 returned status code 504
- [Item Search Filter Ext] GET eo:cloud_cover > 50 OR eo:cloud_cover < 10 OR (eo:cloud_cover IS NULL AND eo:cloud_cover IS NULL) returned status code 400
- [Item Search Filter Ext] GET collection <> 'S2' returned status code 504
- [Item Search Filter Ext] GET datetime = TIMESTAMP('2021-04-08T04:39:23Z') returned status code 504
- [Item Search Filter Ext] GET datetime < TIMESTAMP('2021-04-08T04:39:23Z') returned status code 504
- [Item Search Filter Ext] GET datetime <= TIMESTAMP('2021-04-08T04:39:23Z') returned status code 504
- [Item Search Filter Ext] GET collection = 'S2' AND eo:cloud_cover <= 10 AND datetime >= TIMESTAMP('2021-04-08T04:39:23Z') AND S_INTERSECTS(geometry, POLYGON((43.5845 -79.5442, 43.6079 -79.4893, 43.5677 -79.4632, 43.6129 -79.3925, 43.6223 -79.3238, 43.6576 -79.3163, 43.7945 -79.1178, 43.8144 -79.1542, 43.8555 -79.1714, 43.7509 -79.6390, 43.5845 -79.5442))) returned status code 400
```

### EarthData CMR (stac-cmr)

URL: https://cmr.earthdata.nasa.gov/stac/USGS_EROS

Date: 06-Oct-2022

Notes: Features is supported, but not advertised in conformsTo

Output:

```
$ poetry run stac-api-validator --root-url https://cmr.earthdata.nasa.gov/stac/USGS_EROS --conformance item-search --collection Landsat1-5_MSS_C1.v1 --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'

Validating https://cmr.earthdata.nasa.gov/stac/USGS_EROS
STAC API - Core conformance class found.
STAC API - Item Search conformance class found.
warnings:
- GET Search with datetime=1985-04-12 returned status code 200 instead of 400
errors:
- service-desc ({'rel': 'service-desc', 'href': 'https://api.stacspec.org/v1.0.0-beta.1/openapi.yaml', 'title': 'OpenAPI Doc', 'type': 'application/vnd.oai.openapi;version=3.0'}): media type used in Accept header must get response with same Content-Type header: used 'application/vnd.oai.openapi;version=3.0', got 'text/yaml'
- POST Search with bbox and intersects returned status code 200
- GET Search with bbox=100.0,0.0,105.0,1.0 returned status code 400
- GET Search with bbox=100.0,0.0,0.0,105.0,1.0,1.0 returned status code 400
- POST Search with bbox:[100.0, 0.0, 0.0, 105.0, 1.0, 1.0] returned status code 400
- GET Search with datetime=1972-07-25T00:00:00.000Z extracted from an Item returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52Z returned status code 400
- GET Search with datetime=1996-12-19T16:39:57-00:00 returned status code 400
- GET Search with datetime=1996-12-19T16:39:57+00:00 returned status code 400
- GET Search with datetime=1996-12-19T16:39:57-08:00 returned status code 400
- GET Search with datetime=1996-12-19T16:39:57+08:00 returned status code 400
- GET Search with datetime=../1985-04-12T23:20:50.52Z returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52Z/.. returned status code 400
- GET Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52Z/1986-04-12T23:20:50.52Z returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52+01:00 returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52-01:00 returned status code 400
- GET Search with datetime=1937-01-01T12:00:27.87+01:00 returned status code 400
- GET Search with datetime=1985-04-12T23:20:50.52Z returned status code 400
- GET Search with datetime=1937-01-01T12:00:27.8710+01:00 returned status code 400
- GET Search with datetime=1937-01-01T12:00:27.8+01:00 returned status code 400
- GET Search with datetime=1937-01-01T12:00:27.8Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.000+03:00 returned status code 400
- GET Search with datetime=2020-07-23T00:00:00+03:00 returned status code 400
- GET Search with datetime=1985-04-12t23:20:50.000z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.0Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.01Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.012Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.0123Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.01234Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.012345Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.0123456Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.01234567Z returned status code 400
- GET Search with datetime=2020-07-23T00:00:00.012345678Z returned status code 400
- GET Search with id and other parameters returned status code 400
- GET Search with intersects={'type': 'Point', 'coordinates': [100.0, 0.0]} returned status code 400
- GET Search with intersects={'type': 'LineString', 'coordinates': [[100.0, 0.0], [101.0, 1.0]]} returned status code 400
- GET Search with intersects={'type': 'Polygon', 'coordinates': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]} returned status code 400
- GET Search with intersects={'type': 'Polygon', 'coordinates': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.8, 0.8], [100.8, 0.2], [100.2, 0.2], [100.2, 0.8], [100.8, 0.8]]]} returned status code 400
- POST Search with intersects:{'type': 'Polygon', 'coordinates': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.8, 0.8], [100.8, 0.2], [100.2, 0.2], [100.2, 0.8], [100.8, 0.8]]]} returned status code 400
- GET Search with intersects={'type': 'MultiPoint', 'coordinates': [[100.0, 0.0], [101.0, 1.0]]} returned status code 400
- GET Search with intersects={'type': 'MultiLineString', 'coordinates': [[[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]]]} returned status code 400
- GET Search with intersects={'type': 'MultiPolygon', 'coordinates': [[[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]], [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.2, 0.2], [100.2, 0.8], [100.8, 0.8], [100.8, 0.2], [100.2, 0.2]]]]} returned status code 400
- POST Search with intersects:{'type': 'MultiPolygon', 'coordinates': [[[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]], [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.2, 0.2], [100.2, 0.8], [100.8, 0.8], [100.8, 0.2], [100.2, 0.2]]]]} returned status code 400
- GET Search with intersects={'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [100.0, 0.0]}, {'type': 'LineString', 'coordinates': [[101.0, 0.0], [102.0, 1.0]]}]} returned status code 400
- POST Search with intersects:{'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [100.0, 0.0]}, {'type': 'LineString', 'coordinates': [[101.0, 0.0], [102.0, 1.0]]}]} returned status code 400
- [Item Search] GET Search result for intersects={"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]} returned no results
- [Item Search] POST Search result for intersects={"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]} returned no results
```

### Landsat Look (stac-server)

URL: https://landsatlook.usgs.gov/stac-server

Date: 06-Oct-2022

```
poetry run stac-api-validator --root-url https://landsatlook.usgs.gov/stac-server --conformance features --conformance item-search \
--collection landsat-c2l2-sr --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'

Validating https://landsatlook.usgs.gov/stac-server
STAC API - Core conformance class found.
STAC API - Features conformance class found.
WARNING: Collections validation is not yet fully implemented.
WARNING: Features validation is not yet fully implemented.
STAC API - Item Search conformance class found.
warnings: none
errors:
- POST Search with {'limit': 1} returned status code 403
- POST Search with {'limit': 2} returned status code 403
- POST Search with {'limit': 10} returned status code 403
- POST Search with {'limit': -1} returned status code 403, must be 400
```

### Franklin NASA HSI

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

### EarthAI OnDemand

URL: https://eod-catalog-svc-prod.astraea.earth/

Date: 2-Jul-2021

```
Validating https://eod-catalog-svc-prod.astraea.earth/
warnings: none
errors:
- / : 'conformsTo' must contain at least one STAC API conformance class.
```
