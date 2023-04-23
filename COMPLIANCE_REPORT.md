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

```text
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

```text
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

```text
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

```text
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

URL: <https://planetarycomputer.microsoft.com/api/stac/v1>

Date: 16-Nov-2022

Output:

```text
$ poetry run stac-api-validator --root-url https://planetarycomputer.microsoft.com/api/stac/v1 \
   --conformance features \
   --conformance item-search \
   --conformance filter \
   --conformance item-search#fields \
   --collection sentinel-2-l2a \
   --fields-nested-property properties.eo:cloud_cover \
   --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'
INFO:stac_api_validator.validations:Validating STAC API - Core conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Browseable conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Children conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Collections conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Features conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Features - Filter Extension conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search - Filter Extension conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search - Filter Extension - CQL2-Text conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search - Filter Extension - CQL2-JSON conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search - Filter Extension - Basic CQL2 conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension - Advanced Comparison Operators conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension - Basic Spatial Operators conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension - Temporal Operators conformance class.
Warnings:
- STAC API Specification v1.0.0-rc.2 is the latest version, but API advertises an older version or older versions.
- [Collections] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a has these stac-check recommendations: ['STAC Best Practices: ', "    Object should be called 'collection.json' not 'sentinel-2-l2a.json'", '', "    Links in catalogs and collections should always have a 'title' field", '']
- [Features] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20221116T051959_R119_T43MHN_20221116T182922 has these stac-check recommendations: ['STAC Best Practices: ', "    Item name 'S2B_MSIL2A_20221116T051959_R119_T43MHN_20221116T182922' should only contain Searchable identifiers", "    Identifiers should consist of only lowercase characters, numbers, '_', and '-'", '', '    You have 33 properties. Please consider using links to avoid bloated metadata', '']
- [Features] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20221116T051959_R119_T43MHN_20221116T182922 has these stac-check recommendations: ['STAC Best Practices: ', "    Item name 'S2B_MSIL2A_20221116T051959_R119_T43MHN_20221116T182922' should only contain Searchable identifiers", "    Identifiers should consist of only lowercase characters, numbers, '_', and '-'", '', '    You have 33 properties. Please consider using links to avoid bloated metadata', '']
- [Filter Ext] /: pre-1.0.0-rc.1 Filter Extension conformance classes are advertised.
Errors:
- [Features] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items content-type header is not 'application/geo+json'
- [Features] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items content-type header is not 'application/geo+json'
- [Features] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items self link does not match requested url
- [Features] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20221116T051959_R119_T43MHN_20221116T182922 content-type header is not 'application/geo+json'
- [Features] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items?limit=1 content-type header is not 'application/geo+json'
- [Features] GET https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items?limit=1&token=next:S2B_MSIL2A_20221116T051959_R119_T43MHN_20221116T182922 content-type header is not 'application/geo+json'
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'limit': 10000} body=None had unexpected status code 400 instead of 200:
- [Item Search] POST https://planetarycomputer.microsoft.com/api/stac/v1/search params=None body={'limit': 10000} had unexpected status code 400 instead of 200:
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'limit': 100000} body=None had unexpected status code 400 instead of 200:
- [Item Search] POST https://planetarycomputer.microsoft.com/api/stac/v1/search params=None body={'limit': 100000} had unexpected status code 400 instead of 200:
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'limit': 1000000} body=None had unexpected status code 400 instead of 200:
- [Item Search] POST https://planetarycomputer.microsoft.com/api/stac/v1/search params=None body={'limit': 1000000} had unexpected status code 400 instead of 200:
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'bbox': '0,0,1,1', 'intersects': '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'} body=None had unexpected status code 200 instead of 400: Search with bbox and intersects
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'bbox': '100.0,0.0,0.0,105.0,1.0,1.0'} body=None had unexpected status code 500 instead of 200:
- [Item Search] POST https://planetarycomputer.microsoft.com/api/stac/v1/search params=None body={'bbox': [100.0, 0.0, 0.0, 105.0, 1.0, 1.0]} had unexpected status code 500 instead of 200:
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'datetime': '/1985-04-12T23:20:50.52Z'} body=None had unexpected status code 400 instead of 200: with datetime=/1985-04-12T23:20:50.52Z extracted from an Item
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'datetime': '1985-04-12T23:20:50.52Z/'} body=None had unexpected status code 400 instead of 200: with datetime=1985-04-12T23:20:50.52Z/ extracted from an Item
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'datetime': '1985-04-12'} body=None had unexpected status code 200 instead of 400: invalid datetime returned non-400 status code
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'datetime': '1937-01-01T12:00:27.87+0100'} body=None had unexpected status code 200 instead of 400: invalid datetime returned non-400 status code
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search params={'datetime': '1985-12-12T23:20:50.52'} body=None had unexpected status code 200 instead of 400: invalid datetime returned non-400 status code
- [Item Search] GET Search with ids and non-intersecting bbox returned results, indicating the ids parameter is overriding the bbox parameter. All parameters are applied equally since STAC API 1.0.0-beta.1
- [Item Search] POST Search with ids and non-intersecting bbox returned results, indicating the ids parameter is overriding the bbox parameter. All parameters are applied equally since STAC API 1.0.0-beta.1
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/search Search results for intersects={"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]} do not all intersect
- [Item Search - Filter Ext] / : 'http://www.opengis.net/def/rel/ogc/1.0/queryables' (Queryables) link relation missing
- [Item Search] GET https://planetarycomputer.microsoft.com/api/stac/v1/queryables content-type header is not 'application/schema+json'
- [Item Search - Filter Ext] Queryables 'https://planetarycomputer.microsoft.com/api/stac/v1/queryables' '$id' value invalid, must be same as queryables url

```

### Snap Planet (resto)

URL: <https://tamn.snapplanet.io/>

Date: 25-Oct-2022

Output

```text
$ poetry run stac-api-validator --root-url https://tamn.snapplanet.io \
    --conformance features \
    --conformance item-search \
    --conformance filter \
    --collection S2 \
    --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'
INFO:stac_api_validator.validations:Validating STAC API - Core conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Browseable conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Children conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Collections conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Features conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Features - Filter Extension conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search - Filter Extension conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search - Filter Extension - CQL2-Text conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension - CQL2-JSON conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search - Filter Extension - Basic CQL2 conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension - Advanced Comparison Operators conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search - Filter Extension - Basic Spatial Operators conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension - Temporal Operators conformance class.
Warnings:
- STAC API Specification v1.0.0-rc.2 is the latest version, but API advertises an older version or older versions.
- [Collections] GET https://tamn.snapplanet.io/collections/S2 has these stac-check recommendations: ['STAC Best Practices: ', "    Object should be called 'collection.json' not 'S2.json'", '', "    Links in catalogs and collections should always have a 'title' field", '']
- [Features] GET https://tamn.snapplanet.io/collections/S2/items/aa6e669e-2cdd-5ad4-bc4e-6729d8fc95df has these stac-check recommendations: ['STAC Best Practices: ', '    You have 30 properties. Please consider using links to avoid bloated metadata', '']
- [Features] GET https://tamn.snapplanet.io/collections/S2/items/aa6e669e-2cdd-5ad4-bc4e-6729d8fc95df has these stac-check recommendations: ['STAC Best Practices: ', '    You have 30 properties. Please consider using links to avoid bloated metadata', '']
Errors:
- [Collections] https://tamn.snapplanet.io/collections/S2 does not have parent link
- [Features] GET https://tamn.snapplanet.io/collections/S2/items does not have root link
- [Features] GET https://tamn.snapplanet.io/collections/S2/items does not have parent link
- [Item Search] GET https://tamn.snapplanet.io/search params={'limit': 10000} body=None had unexpected status code 400 instead of 200:
- [Item Search] GET https://tamn.snapplanet.io/search params={'limit': 100000} body=None had unexpected status code 400 instead of 200:
- [Item Search] GET https://tamn.snapplanet.io/search params={'limit': 1000000} body=None had unexpected status code 400 instead of 200:
- [Item Search] GET https://tamn.snapplanet.io/search?limit=1&bbox=20,20,21,21&collections=S2 params=None body=None content-type header is not 'application/geo+json'
- [Item Search] GET https://tamn.snapplanet.io/search params={'ids': '9a8f0b4a-ccd6-5ea0-8a1d-5bebef7f2703', 'collections': 'S2', 'bbox': '21.13877628790669,21.798042737919523,22.13877628790669,22.798042737919523'} body=None content-type header is not 'application/geo+json'
- [Item Search] GET https://tamn.snapplanet.io/search params={'collections': 'S2'} body=None content-type header is not 'application/geo+json'
- [Item Search] GET https://tamn.snapplanet.io/search params={'collections': 'S2'} body=None content-type header is not 'application/geo+json'
- [Item Search] GET https://tamn.snapplanet.io/search params={'collections': 'S2'} body=None content-type header is not 'application/geo+json'
- [Item Search] GET https://tamn.snapplanet.io/search params={'collections': 'S2', 'intersects': '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'} body=None content-type header is not 'application/geo+json'
- [Item Search] GET https://tamn.snapplanet.io/search?limit=1&collections=S2 params=None body=None content-type header is not 'application/geo+json'
- [Item Search] GET https://tamn.snapplanet.io/search?&limit=1&collections=S2&next=218712159668593652 params=None body=None content-type header is not 'application/geo+json'
- [Item Search - Filter Ext] GET https://tamn.snapplanet.io/search?collections=S2 params=None body=None content-type header is not 'application/geo+json'
- [Item Search - Filter Ext] GET https://tamn.snapplanet.io/search params={'limit': 1, 'filter-lang': 'cql2-text', 'filter': 'eo:cloud_cover > 50 OR eo:cloud_cover < 10'} body=None had unexpected status code 504 instead of 200:
- [Item Search - Filter Ext] GET https://tamn.snapplanet.io/search params={'limit': 1, 'filter-lang': 'cql2-text', 'filter': 'eo:cloud_cover > 50 OR eo:cloud_cover < 10 OR (eo:cloud_cover IS NULL AND eo:cloud_cover IS NULL)'} body=None had unexpected status code 400 instead of 200:
- [Item Search - Filter Ext] GET https://tamn.snapplanet.io/search params={'limit': 1, 'filter-lang': 'cql2-text', 'filter': "collection <> 'S2'"} body=None had unexpected status code 504 instead of 200:
```

### Radiant ML Hub (stac-fastapi)

URL: <https://api.radiant.earth/mlhub/v1>

Date: 31-Oct-2022

Output

```text
$ poetry run stac-api-validator --root-url https://api.radiant.earth/mlhub/v1 \
--conformance core --conformance features --conformance item-search \
--auth-query-parameter 'key=xxx' \
 --collection lacuna_fund_eotg_v1_labels \
--geometry '{ "type": "Polygon", "coordinates": [ [ [ -6.873149632157182, 13.306361128851238 ], [ -6.8729475
45317309, 13.329493867068924 ], [ -6.8965701520705105, 13.329690854131131 ], [ -6.896769998632048, 13.30655776190765 ], [ -6.873149632157182, 13.306361128851238 ] ] ] }'
```

### Sentinel Hub 1.0.0 Catalog

URL: <https://services.sentinel-hub.com/api/v1/catalog/1.0.0/>

Date: 16-Nov-2022

Output

```text
$ poetry run stac-api-validator --root-url https://services.sentinel-hub.com/api/v1/catalog/1.0.0/  --conformance core
INFO:stac_api_validator.validations:Validating STAC API - Core conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Browseable conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Children conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Collections conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Features conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search conformance class.
Warnings:
- STAC API Specification v1.0.0-rc.2 is the latest version, but API advertises an older version or older versions.
- / : Link[rel=service-doc] should exist
Errors:
- / : Link[rel=root] must exist
- / : Link[rel=self] type is not application/json
- / : Link[rel=service-desc] must exist
```

### Earth Search v1 (stac-server)

URL: <https://earth-search.aws.element84.com/v1>

Date: 16-Nov-2022

Output:

```text
poetry run stac-api-validator --root-url https://earth-search.aws.element84.com/v1 \
    --conformance core \
    --conformance features \
    --conformance item-search \
    --conformance item-search#fields \
    --conformance item-search#query \
    --collection sentinel-2-l2a \
    --fields-nested-property properties.eo:cloud_cover \
    --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}' \
    --query-comparison-field eo:cloud_cover \
    --query-eq-value 7.531843 \
    --query-neq-value 7.531843 \
    --query-lt-value 7 \
    --query-lte-value 7.531843 \
    --query-gt-value 75 \
    --query-gte-value 7.531843 \
    --query-substring-field grid:code \
    --query-starts-with-value MGRS-48 \
    --query-ends-with-value UP \
    --query-contains-value 8NU \
    --query-in-field mgrs:latitude_band \
    --query-in-values M,N

INFO:stac_api_validator.validations:Validating STAC API - Core conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Browseable conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Children conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Collections conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Features conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Features - Filter Extension conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension conformance class.
Warnings:
- STAC API Specification v1.0.0-rc.2 is the latest version, but API advertises an older version or older versions.
- [Collections] GET https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a has these stac-check recommendations: ['STAC Best Practices: ', "    Object should be called 'collection.json' not 'sentinel-2-l2a.json'", '', "    Links in catalogs and collections should always have a 'title' field", '']
- [Features] GET https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items/S2B_4UDE_20221116_0_L2A has these stac-check recommendations: ['STAC Best Practices: ', "    Item name 'S2B_4UDE_20221116_0_L2A' should only contain Searchable identifiers", "    Identifiers should consist of only lowercase characters, numbers, '_', and '-'", '', '    You have 41 properties. Please consider using links to avoid bloated metadata', '']
- [Features] GET https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items/S2B_4UDE_20221116_0_L2A has these stac-check recommendations: ['STAC Best Practices: ', "    Item name 'S2B_4UDE_20221116_0_L2A' should only contain Searchable identifiers", "    Identifiers should consist of only lowercase characters, numbers, '_', and '-'", '', '    You have 41 properties. Please consider using links to avoid bloated metadata', '']
Errors:
- [Collections] /collections does not have self link
- [Collections] /collections does not have root link
- [Features] GET https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items does not have self link
- [Features] GET https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items does not have root link
- [Features] GET https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items does not have parent link
- [Item Search] GET https://earth-search.aws.element84.com/v1/search params={'limit': 10000} body=None had unexpected status code 502 instead of 200:
- [Item Search] GET https://earth-search.aws.element84.com/v1/search params={'limit': 100000} body=None had unexpected status code 400 instead of 200:
- [Item Search] GET https://earth-search.aws.element84.com/v1/search params={'limit': 1000000} body=None had unexpected status code 400 instead of 200:
```

### EarthData CMR (stac-cmr)

URL: <https://cmr.earthdata.nasa.gov/stac/USGS_EROS>

Date: 25-Oct-2022

Notes: Features is supported, but not advertised in conformsTo

Output:

```text
$  poetry run stac-api-validator --root-url https://cmr.earthdata.nasa.gov/stac/USGS_EROS --conformance item-search --collection Landsat1-5_MSS_C1.v1 --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'

INFO:stac_api_validator.validations:Validating STAC API - Core conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Browseable conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Children conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Collections conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Features conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension conformance class.
warnings:
- [Item Search] GET Search with datetime=1985-04-12 returned status code 200 instead of 400
errors:
- service-desc ({'rel': 'service-desc', 'href': 'https://api.stacspec.org/v1.0.0-beta.1/openapi.yaml', 'title': 'OpenAPI Doc', 'type': 'application/vnd.oai.openapi;version=3.0'}): media type used in Accept header must get response with same Content-Type header: used 'application/vnd.oai.openapi;version=3.0', got 'text/yaml'
- [Item Search] POST Search with bbox and intersects returned status code 200
- [Item Search] GET Search with bbox=100.0,0.0,105.0,1.0 returned status code 400
- [Item Search] GET Search with bbox=100.0,0.0,0.0,105.0,1.0,1.0 returned status code 400
- [Item Search] POST Search with bbox:[100.0, 0.0, 0.0, 105.0, 1.0, 1.0] returned status code 400
- [Item Search] method=GET url=https://cmr.earthdata.nasa.gov/stac/USGS_EROS/search params={'datetime': '1972-07-25T00:00:00.000Z'} body=None had unexpected status code 400 instead of 200: with datetime=1972-07-25T00:00:00.000Z extracted from an Item
- [Item Search] GET Search with datetime=1985-04-12T23:20:50.52Z returned status code 400
- [Item Search] GET Search with datetime=1996-12-19T16:39:57-00:00 returned status code 400
- [Item Search] GET Search with datetime=1996-12-19T16:39:57+00:00 returned status code 400
- [Item Search] GET Search with datetime=1996-12-19T16:39:57-08:00 returned status code 400
- [Item Search] GET Search with datetime=1996-12-19T16:39:57+08:00 returned status code 400
- [Item Search] GET Search with datetime=../1985-04-12T23:20:50.52Z returned status code 400
- [Item Search] GET Search with datetime=1985-04-12T23:20:50.52Z/.. returned status code 400
- [Item Search] GET Search with datetime=/1985-04-12T23:20:50.52Z returned status code 400
- [Item Search] GET Search with datetime=1985-04-12T23:20:50.52Z/ returned status code 400
- [Item Search] GET Search with datetime=1985-04-12T23:20:50.52Z/1986-04-12T23:20:50.52Z returned status code 400
- [Item Search] GET Search with datetime=1985-04-12T23:20:50.52+01:00/1986-04-12T23:20:50.52+01:00 returned status code 400
- [Item Search] GET Search with datetime=1985-04-12T23:20:50.52-01:00/1986-04-12T23:20:50.52-01:00 returned status code 400
- [Item Search] GET Search with datetime=1937-01-01T12:00:27.87+01:00 returned status code 400
- [Item Search] GET Search with datetime=1985-04-12T23:20:50.52Z returned status code 400
- [Item Search] GET Search with datetime=1937-01-01T12:00:27.8710+01:00 returned status code 400
- [Item Search] GET Search with datetime=1937-01-01T12:00:27.8+01:00 returned status code 400
- [Item Search] GET Search with datetime=1937-01-01T12:00:27.8Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.000+03:00 returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00+03:00 returned status code 400
- [Item Search] GET Search with datetime=1985-04-12t23:20:50.000z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.0Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.01Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.012Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.0123Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.01234Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.012345Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.0123456Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.01234567Z returned status code 400
- [Item Search] GET Search with datetime=2020-07-23T00:00:00.012345678Z returned status code 400
- [Item Search] method=GET url=https://cmr.earthdata.nasa.gov/stac/USGS_EROS/search params={'datetime': '1985-04-12'} body=None had unexpected status code 200 instead of 400: invalid datetime returned non-400 status code
- [Item Search]  GET Search with id and other parameters returned status code 400
- [Item Search] GET Search with intersects={'type': 'Point', 'coordinates': [100.0, 0.0]} returned status code 400
- [Item Search] GET Search with intersects={'type': 'LineString', 'coordinates': [[100.0, 0.0], [101.0, 1.0]]} returned status code 400
- [Item Search] GET Search with intersects={'type': 'Polygon', 'coordinates': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]} returned status code 400
- [Item Search] GET Search with intersects={'type': 'Polygon', 'coordinates': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.8, 0.8], [100.8, 0.2], [100.2, 0.2], [100.2, 0.8], [100.8, 0.8]]]} returned status code 400
- [Item Search] POST Search with intersects:{'type': 'Polygon', 'coordinates': [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.8, 0.8], [100.8, 0.2], [100.2, 0.2], [100.2, 0.8], [100.8, 0.8]]]} returned status code 400
- [Item Search] GET Search with intersects={'type': 'MultiPoint', 'coordinates': [[100.0, 0.0], [101.0, 1.0]]} returned status code 400
- [Item Search] GET Search with intersects={'type': 'MultiLineString', 'coordinates': [[[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]]]} returned status code 400
- [Item Search] GET Search with intersects={'type': 'MultiPolygon', 'coordinates': [[[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]], [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.2, 0.2], [100.2, 0.8], [100.8, 0.8], [100.8, 0.2], [100.2, 0.2]]]]} returned status code 400
- [Item Search] POST Search with intersects:{'type': 'MultiPolygon', 'coordinates': [[[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]], [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.2, 0.2], [100.2, 0.8], [100.8, 0.8], [100.8, 0.2], [100.2, 0.2]]]]} returned status code 400
- [Item Search] GET Search with intersects={'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [100.0, 0.0]}, {'type': 'LineString', 'coordinates': [[101.0, 0.0], [102.0, 1.0]]}]} returned status code 400
- [Item Search] POST Search with intersects:{'type': 'GeometryCollection', 'geometries': [{'type': 'Point', 'coordinates': [100.0, 0.0]}, {'type': 'LineString', 'coordinates': [[101.0, 0.0], [102.0, 1.0]]}]} returned status code 400
- [Item Search] GET Search result for intersects={"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]} returned no results
- [Item Search] POST Search result for intersects={"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]} returned no results
```

### Landsat Look (stac-server)

URL: <https://landsatlook.usgs.gov/stac-server>

Date: 25-Oct-2022

```text
$ poetry run stac-api-validator --root-url https://landsatlook.usgs.gov/stac-server --conformance features --conformance item-search \
∙ --collection landsat-c2l2-sr --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'
INFO:stac_api_validator.validations:Validating STAC API - Core conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Browseable conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Children conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Collections conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Features conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Features - Filter Extension conformance class.
INFO:stac_api_validator.validations:Validating STAC API - Item Search conformance class.
INFO:stac_api_validator.validations:Skipping STAC API - Item Search - Filter Extension conformance class.
warnings: none
errors:
- [Collections] /collections does not have self link
- [Collections] /collections does not have root link
- [Features] https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l2-sr/items does not have self link
- [Features] https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l2-sr/items does not have root link
- [Features] https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l2-sr/items does not have parent link
```

### Franklin NASA HSI

URL: <https://franklin.nasa-hsi.azavea.com>

Date: 19-Jan-2022

```text
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
