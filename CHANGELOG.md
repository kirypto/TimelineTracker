# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Added a `sampleConfig.md` to replace the configuration samples duplicated in `projectSetup.md` and `projectDeployment.md`.
- Added sample CORS header configuration to `sampleConfig.md`.

### Changed
- Changed project setup and deployment documentation to reference the new `sampleConfig.md`. 

---

## [0.1.2] - 2021-03-14
### Added

- Added support for CORS headers to allow serving returned data in on a web page.
- Added sample CORS configuration to the `projectSetup.md` and `projectDeployment.md` files.
- Added a `runWithFlask.ps1` to simplify the deployment of TTAPI.
- Added instructions for deploying the app to the README file.
- Added instructions for releasing a new version of the app to the `projectSetup.md` file.

### Changed
- Modify json repositories to soft-delete files via adding a `.deleted` suffix instead of removing the file.

### Fixed
- Clarify divergence from RFC 8259 in project standards section of README file.

---

## [0.1.1] - 2021-02-24
### Changed
- Move in-depth explanation of resources into separate markdown file.
- Move project standards to new section in README file.

### Fixed
- Fix PATCH processing issue causing modification of any top level attributes _(ie: `/description`)_ to fail. Affected Location, Traveler,
  and Event routes.
- Fix Traveler DELETE issue causing failure with "Cannot parse location id" message.
- Fix issue causing metadata to clear whenever PATCHing other attributes. Affected Location, Traveler, and Events

---

## [0.1.0] - 2021-01-15
### Added
- Added Location POST route for creation.
- Added Locations GET route for retrieving all existing ids.
- Added Location GET route for retrieval.
- Added Location DELETE route for removal.
- Added Location PATCH route for modification.
- Added Location timeline GET route for retrieving all linked events.

- Added Traveler POST route for creation.
- Added Traveler GET route for retrieving all existing ids.
- Added Traveler GET route for retrieval.
- Added Traveler DELETE route for removal.
- Added Traveler PATCH route for modification.
- Added Traveler journey POST route appending a new positional move.
- Added Traveler timeline GET route for retrieving all linked events.

- Added Event POST route for creation.
- Added Event GET route for retrieving all existing ids.
- Added Event GET route for retrieval.
- Added Event DELETE route for removal.
- Added Event PATCH route for modification.


[Unreleased]: https://github.com/kirypto/TimelineTracker/compare/v0.1.2...HEAD

[0.1.2]: https://github.com/kirypto/TimelineTracker/compare/v0.1.1...v0.1.2

[0.1.1]: https://github.com/kirypto/TimelineTracker/compare/v0.1.0...v0.1.1

[0.1.0]: https://github.com/kirypto/TimelineTracker/releases/tag/v0.1.0
