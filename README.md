# STAC API Validator

[![PyPI](https://img.shields.io/pypi/v/stac-api-validator.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/stac-api-validator.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/stac-api-validator)][python version]
[![License](https://img.shields.io/pypi/l/stac-api-validator)][license]

[![Read the documentation at https://stac-api-validator.readthedocs.io/](https://img.shields.io/readthedocs/stac-api-validator/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/stac-utils/stac-api-validator/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/stac-utils/stac-api-validator/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/stac-api-validator/
[status]: https://pypi.org/project/stac-api-validator/
[python version]: https://pypi.org/project/stac-api-validator
[read the docs]: https://stac-api-validator.readthedocs.io/en/latest
[tests]: https://github.com/stac-utils/stac-api-validator/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/stac-utils/stac-api-validator
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Introduction

The STAC API Validator is the official validation suite for the
[STAC API](https://github.com/radiantearth/stac-api-spec/) family of specifications.

## Documentation

See the [stable](https://stac-api-validator.readthedocs.io/en/stable/) or
[latest](https://stac-api-validator.readthedocs.io/en/latest) documentation pages.

## Installation

STAC API Validator requires Python 3.10.

You can install _STAC API Validator_ via [pip] from [PyPI]:

```console
pip install stac-api-validator
```

and then run it:

```console
stac-api-validator \
    --root-url https://planetarycomputer.microsoft.com/api/stac/v1/ \
    --conformance core \
    --conformance features \
    --conformance item-search \
    --collection sentinel-2-l2a \
    --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## Usage

Please see the [Command-line Reference] for details.

The conformance class validations to run are selected with the `--conformance` parameters. This parameter
can be used more than once to specify multiple conformance classes to validate. The `STAC API - Core` conformance
class will always be validated, even if not specified.

If `item-search`, `collections`, and/or `features` are specified, the `--collection` and `--geometry` parameters must also
be specified. The `--collection` parameter specifies the name of a collection to use for some of the validations.
The `--geometry` should specify an AOI over which there are between 100 and 20,000 results for the collection (more
results means longer time to run).

## Features

**Work in Progress** -- this currently only validates a subset of behavior

This validation suite focuses on validating STAC API interactions. Tools such as
[pystac](https://github.com/stac-utils/pystac) and [stac4s](https://github.com/azavea/stac4s) do a
good job of validating STAC objects (Catalog, Collection, Item). This suite focuses on the STAC API behavior
validation.

The three key concepts within a STAC API are:

1. _Conformance classes_ advertising the capabilities of the API
2. _Link relations_ between resources within the web API (hypermedia)
3. _Parameters_ that filter search results

The conformance classes, as defined in the `conformsTo` field of the Landing Page (root, `/`), advertise to
clients which capabilities are available in the API. Without this field, a client would not even be able to tell that a
root URI was a STAC API.

The link relations define how to navigate a STAC catalog through parent-child links and find resources such as the OpenAPI specification. While many OGC API and STAC API endpoint have a fixed value (e.g., `/collections`), it is preferable for clients discover the paths via hypermedia.

The parameters that filter results apply to the Items resource and Item Search endpoints.

The current validity status of several popular STAC API implementations can be found [here](COMPLIANCE_REPORT.md).

## Command-line Reference

Usage:

```
Usage: stac-api-validator [OPTIONS]

  STAC API Validator.

Options:
  --version                       Show the version and exit.
  --log-level TEXT                Logging level, one of DEBUG, INFO, WARN,
                                  ERROR, CRITICAL
  --root-url TEXT                 STAC API Root / Landing Page URL  [required]
  --collection TEXT               The name of the collection to use for item-
                                  search, collections, and features tests.
  --geometry TEXT                 The GeoJSON geometry to use for intersection
                                  tests.
  --conformance [core|browseable|item-search|features|collections|children|filter]
                                  The conformance classes to validate.
                                  [required]
  --auth-bearer-token TEXT        Authorization Bearer token value to append
                                  to all requests.
  --auth-query-parameter TEXT     Query pararmeter key and value to pass for
                                  authorization, e.g., 'key=xyz'.
  --help                          Show this message and exit.
```

Conformance classes item-search, features, and collections require the `--collection` parameter with the id of a
collection to run some tests on.

Conformance class `item-search` requires `--geometry` with a GeoJSON geometry that returns some items for
the specified collection.

Example:

```
stac-api-validator \
    --root-url https://planetarycomputer.microsoft.com/api/stac/v1/ \
    --conformance core \
    --conformance item-search \
    --conformance features \
    --collection sentinel-2-l2a \
    --geometry '{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}'
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

Example with authorization using parameters:

```
stac-api-validator --root-url https://api.radiant.earth/mlhub/v1 --conformance core --auth-query-parameter 'key=xxx'
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

## License

Distributed under the terms of the [Apache 2.0 license][license],
_STAC API Validator_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/stac-utils/stac-api-validator/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/stac-utils/stac-api-validator/blob/main/LICENSE
[contributor guide]: https://github.com/stac-utils/stac-api-validator/blob/main/CONTRIBUTING.md
[command-line reference]: https://stac-api-validator.readthedocs.io/en/latest/usage.html
