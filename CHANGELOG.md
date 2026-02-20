# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.8](https://github.com/stac-utils/stac-api-validator/compare/v0.6.7...v0.6.8) (2026-02-20)


### Bug Fixes

* issue a warning when validate_collections is called without collection ([#761](https://github.com/stac-utils/stac-api-validator/issues/761)) ([bafdf12](https://github.com/stac-utils/stac-api-validator/commit/bafdf127b709a422f3b44ba63a250e629fd99911))

## [Unreleased]

## [0.6.7] - 2025-08-11

- Support stac-check config_file ([#687](https://github.com/stac-utils/stac-api-validator/pull/687))

## [0.6.6] - 2025-07-29

Dependency updates.

## [0.6.5] - 2025-03-25

### Fixed

- Allow items without a bbox ([#639](https://github.com/stac-utils/stac-api-validator/pull/639))

## [0.6.4] - 2025-01-17

### Added

- Ability to configure whether to open assets ([#595](https://github.com/stac-utils/stac-api-validator/pull/595))

### Fixed

- HTTP headers to **stac-validator** ([#595](https://github.com/stac-utils/stac-api-validator/pull/595))

## [0.6.3] - 2024-10-07

### Added

- Allow generic auth headers ([#392](https://github.com/stac-utils/stac-api-validator/pull/392))

## [0.6.2] - 2024-04-29

### Fixed

- Don't warn about old versions for extensions ([#365](https://github.com/stac-utils/stac-api-validator/pull/365))
- Convert intersects geometry to dictionary for POST ([#390](https://github.com/stac-utils/stac-api-validator/pull/390))

## [0.6.1] - 2023-04-24

### Changed

- Changed version upgrade warning to 1.0.0

## [0.6.0] - 2023-04-23

### Added

- Added support for Fields Extension validation of Item Search
- Add parameter set `--validate-pagination/--no-validate-pagination` to conditionally run the pagination tests, which may take a while to run.
- Added support for Query Extension validation of Item Search
- Added support for Transaction Extension validation
- Added support for Sort Extension validation of Item Search

## [0.5.0] - 2023-02-21

### Added

- Added validation for Children Extension with `--conformance children`
- Added validation for Browseable Extension with `--conformance browseable`
- Added validation for traversal of Core child and item link relations with pystac Catalog

## [0.4.3] - 2023-02-10

### Fixed

- Fixed check of landing page link rels for self and root. These were incorrectly
  checked for having a type of geojson, but they should just be json.

## [0.4.2] - 2023-01-20

### Fixed

- Fixed unhandled exception when POST intersects query had no matching features.
- Fixed several false positives on incorrect link types.

## [0.4.1] - 2023-01-10

### Changed

- main now returns exit code 0 for success or 1 failure

## [0.4.0] - 2022-11-16

### Added

- Add support for running stac-validator and stac-check on the objects returned from the API
- Add support for Authorization Bearer and arbitrary query parameter authentication (experimental)
- Add warning about upgrading to 1.0.0-rc.2

### Fixed

- Handle pystac-client exceptions #152

### Changed

- Significant internal refactoring for invocation of HTTP requests

## [0.3.0] - 2022-10-25

### Removed

- Removed the `--post/--no-post` parameter in favor of looking in the landing page for the `method` field of the
  search link relation

### Added

- Completed Features conformance class validation
- Completed Collections conformance class validation
- Added unit tests for part of Core validations

### Changed

- Significant refactoring to support unit testing

## [0.2.0] - 2022-10-16

### Added

- Validate Item Search and Features pagination

### Changed

- More explicit reporting of which conformance classes validations are run or not run.

## [0.1.1] - 2022-10-11

Release is primarily to publish to Read the Docs as a version.

### Changed

- Upgraded several minor dependency versions.
- Fixed copyright holder in the License to Radiant Earth Foundation.

## [0.1.0] - 2022-10-06

### Added

- Validation for Filter Extension
- Validation that using the `ids` parameter does not override all other parameters, as was the behavior
  prior to v1.0.0-beta.1.
- Add validation that the footprint of each Item returned from Item Search intersects the AOI provided
  through the intersect parameter
- Add validation that Collection has items link relation
- Add validation that requests for non-existent collections and items returns 404

### Changed

### Deprecated

### Removed

### Fixed

- Fixed failure when POST validations were run but server did not support POST.
- Fixed validation of `service-desc` link rel type and use in Accept and Content-Type header.

## [0.0.3] - 2022-09-30

### Added

- Validate items link rel

### Fixed

- Checks for some limits were incorrect, so removing these until they can be properly implemented

## [0.0.2] - 2022-09-26

### Added

- Validation for Links
- Validation for datetime query parameter
- Validation for bbox query parameter

### Changed

### Deprecated

### Removed

### Fixed

- Fixed issue with item-search validation relying on collections behavior

[unreleased]: https://github.com/stac-utils/stac-api-validator/compare/v0.6.7...main
[0.6.7]: https://github.com/stac-utils/stac-api-validator/compare/v0.6.6..v0.6.7
[0.6.6]: https://github.com/stac-utils/stac-api-validator/compare/v0.6.5..v0.6.6
[0.6.5]: https://github.com/stac-utils/stac-api-validator/compare/v0.6.4..v0.6.5
[0.6.4]: https://github.com/stac-utils/stac-api-validator/compare/v0.6.3..v0.6.4
[0.6.3]: https://github.com/stac-utils/stac-api-validator/compare/v0.6.2..v0.6.3
[0.6.2]: https://github.com/stac-utils/stac-api-validator/tree/v0.6.2
[0.6.1]: https://github.com/stac-utils/stac-api-validator/tree/v0.6.1
[0.6.0]: https://github.com/stac-utils/stac-api-validator/tree/v0.6.0
[0.5.0]: https://github.com/stac-utils/stac-api-validator/tree/v0.5.0
[0.4.3]: https://github.com/stac-utils/stac-api-validator/tree/v0.4.3
[0.4.2]: https://github.com/stac-utils/stac-api-validator/tree/v0.4.2
[0.4.1]: https://github.com/stac-utils/stac-api-validator/tree/v0.4.1
[0.4.0]: https://github.com/stac-utils/stac-api-validator/tree/v0.4.0
[0.3.0]: https://github.com/stac-utils/stac-api-validator/tree/v0.3.0
[0.2.0]: https://github.com/stac-utils/stac-api-validator/tree/v0.2.0
[0.1.1]: https://github.com/stac-utils/stac-api-validator/tree/v0.1.1
[0.1.0]: https://github.com/stac-utils/stac-api-validator/tree/v0.1.0
[0.0.3]: https://github.com/stac-utils/stac-api-validator/tree/v0.0.3
[0.0.2]: https://github.com/stac-utils/stac-api-validator/tree/v0.0.2
