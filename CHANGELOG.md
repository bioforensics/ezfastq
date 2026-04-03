# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Fixed
- Fixed bug involving reading and writing empty lines from `samples.txt` file (#12)

## [0.2] 2025-12-15

### Added
- Support for renaming samples while copying (#6)
- Support for symbolic linking instead of copying (#9)
- SHA256 checksums to ensure integrity of copied files (#10)


## [0.1.3] 2025-12-03

### Added
- Option to add source and destination paths to the copy log with a `--verbose` flag (#5)


## [0.1.2] 2025-11-05

### Changed
- User can now configure subdirectory structure for copy destination (#4)


## [0.1.1] 2025-05-30

### Changed
- Updated Python API to return copier object from `ezfastq.api.copy` function (#3)


## [0.1] 2025-05-27

Initial release!
