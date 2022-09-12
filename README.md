# STAC API Validator

[![PyPI](https://img.shields.io/pypi/v/stac-api-validator.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/stac-api-validator.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/stac-api-validator)][python version]
[![License](https://img.shields.io/pypi/l/stac-api-validator)][license]

[![Read the documentation at https://stac-api-validator.readthedocs.io/](https://img.shields.io/readthedocs/stac-api-validator/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/philvarner/stac-api-validator/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/philvarner/stac-api-validator/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/stac-api-validator/
[status]: https://pypi.org/project/stac-api-validator/
[python version]: https://pypi.org/project/stac-api-validator
[read the docs]: https://stac-api-validator.readthedocs.io/
[tests]: https://github.com/philvarner/stac-api-validator/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/philvarner/stac-api-validator
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

Install the package with development requirements:

```console
$ poetry install
```

You can now run the command-line interface:

```console
$ poetry run stac-api-validator
```

**Future Work** You can install _STAC API Validator_ via [pip] from [PyPI]:

```console
$ pip install stac-api-validator
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

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

The current validity status of several popular STAC API implementations can be found [here](../stac-api-validator/COMPLIANCE_REPORT.md).

## Running the validator

Running this requires Python 3.9.5.

Create new venv with python >= 3.9:

```
pyenv local 3.9.5
python -m venv --prompt stac-api-validator .venv
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

Additionally, the `--no-post` option can be specified to only test GET requests, instead of the default of using
both GET and POST.

Usage:

```
usage: validate.py [-h] [--logging LOGGING] [--root ROOT] [--post | --no-post]

STAC API Validation Suite

optional arguments:
  -h, --help         show this help message and exit
  --logging LOGGING  DEBUG, INFO, WARN, ERROR, CRITICAL
  --root ROOT        STAC API Root / Landing Page URL
  --post, --no-post  Also use POST method for requests (default: True)
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
[file an issue]: https://github.com/philvarner/stac-api-validator/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/philvarner/stac-api-validator/blob/main/LICENSE
[contributor guide]: https://github.com/philvarner/stac-api-validator/blob/main/CONTRIBUTING.md
[command-line reference]: https://stac-api-validator.readthedocs.io/en/latest/usage.html
