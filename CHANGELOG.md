# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - TBD

### Added

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

- Fixed validation of `service-desc` link rel type and use in Accept and Content-Type header.

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
