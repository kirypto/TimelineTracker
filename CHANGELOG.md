# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

_Nothing to see here_

## [0.4.0] - 2022-11-07

### Added
- Added a new `World` resource that all other entities will be associated with.
- Added new `/api/world...` routes to interact with `World` entities. See updated API Specification.
- Added an application `secret_key` field to the configuration yaml to protect client-side connections.
- Added authorization (supported by Auth0.com) to the application.
- Added documentation to `projectDeployment.md` to show how to integrate Auth0.com with the application.
- Added a `/home` page to be shown when the client is not logged in with a Login button.
- Added a `/dashboard` page to be shown when the client is logged in with a Logout button and link to documentation.

### Changed
- **Significant Change**: Reworked data migration. Existing json data will need to be updated to version 0.3.0 before attempting to update
  to version 0.4.0
- Updated API Specification to include new `World` resource.
- All existing entity routes are now prefixed with `/api/world/:worldId/...`. See updated API Specification.
- Modified the data migration to be triggered by run scripts prior to launching the application proper.
- Corrected minor formatting in CHANGELOG _(added periods, fixed indentations)_.
- Modified the `sampleConfig.md` to show the required configurations for Auth0.com.
    - Added configurations for `domain`, `api_audience`, and `algorithms` as necessary for parsing bearer tokens.
- Modified `/` page to navigate to the `/home` page.
- Modify api endpoints to enforce authorization.
- Rework internal logic for REST request handling to improve code flow and simplicity.
- Change default `host` in `sampleConfig.md` and `apiSpecification.json` from `localhost` to `127.0.0.1`.
- Modify entity descriptions to append a single new-line character once whitespace is stripped.
- Change repository config to accept python class path to allow custom implementations to be used.
    - Update config examples accordingly.
- Renamed `metadata` field to `attributes` for all entities
- Replaced `Infinity` and `-Infinity` with `1.7976931348623157e+308` and `-1.7976931348623157e+308` respectively for each entities' `span`.
- Modified `Location` and `Event` resources to reject `+/-infinity` as span range values.
---

## [0.3.0] - 2021-09-08
### Added
- Added requirement on `waitress>=2.0.0`.
- Added a `runWithFlask.sh` script for running on Unix.
- Added missing documentation for `spanIncludes` query param of `/api/events` route in API specification.
- Added missing documentation for `spanIntersects` query param of `/api/events` route in API specification.

### Changed
- Upgraded `Flask` dependency to `>=2.0.1`.
- Upgraded `jsonpatch` dependency to `>=1.32`.
- Upgraded `ruamel.yaml` dependency to `>=0.17.16`.
- Upgraded `flask-cors` dependency to `>=3.0.10`.
- Modified flask app to serve api with `waitress`.
- Modified name-based entity filtering to be case-insensitive.
- Modified `projectDeployment.md` to include instructions for running from bash.
- Corrected example for `spanIntersects` query param of `/api/locations` route in API specification.

---

## [0.2.1] - 2021-04-15
### Changed
- Changed required python version listed in `projectSetup.py` and `projectDeployment.py` to be 3.9.
- Changed Json data migrations to default to v0.1.3 when a repository_version.metadata file does not exist.

---

## [0.2.0] - 2021-04-14
### Added
- Added a requirement to include the Resources directory path as part of the application configuration.
- Added a metadata file to track the version of data stored in the Json repository.
- Added a Json data migration system for updating persisted data to a newer application version.

### Changed
- Changed the `reality` component of Locations' and Events' `span` attribute to be a set of integers instead of a range.
- Changed served Json representation of `reality` to be a sorted integer array.
- Updated API Spec to align with integer array changes.
- Changed metadata attribute to reject empty strings for either keys or values.

---

## [0.1.3] - 2021-04-05
### Added
- Added a `sampleConfig.md` to replace the configuration samples duplicated in `projectSetup.md` and `projectDeployment.md`.
- Added sample CORS header configuration to `sampleConfig.md`.

### Changed
- Changed project setup and deployment documentation to reference the new `sampleConfig.md`.
- Changed tags to be served alphabetically sorted.
- Changed description attributes to automatically remove whitespace from edges.
- Changed metadata attributes to automatically remove whitespace from edges of given metadata keys and values.
- Changed tags attributes to automatically remove whitespace from edges of each tag.

### Fixed
- Fixed Json PATCH issues causing `move` operations to fail.
- Fixed API Spec to use `{"low":-Infinity,"high":Infinity}` instead of `"ALL"` for fully spanning ranges.
- Fixed Json parsing of ranges to support passing a single int or float value.

---

## [0.1.2] - 2021-03-14
### Added
- Added support for CORS headers to allow serving returned data in on a web page.
- Added sample CORS configuration to the `projectSetup.md` and `projectDeployment.md` files.
- Added a `runWithFlask.ps1` to simplify the deployment of TTAPI.
- Added instructions for deploying the app to the README file.
- Added instructions for releasing a new version of the app to the `projectSetup.md` file.

### Changed
- Modify Json repositories to soft-delete files via adding a `.deleted` suffix instead of removing the file.

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
- Fix issue causing metadata to clear whenever PATCHing other attributes. Affected Location, Traveler, and Events.

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


[Unreleased]: https://github.com/kirypto/TimelineTracker/compare/v0.4.0...HEAD

[0.4.0]: https://github.com/kirypto/TimelineTracker/compare/v0.3.0...v0.4.0

[0.3.0]: https://github.com/kirypto/TimelineTracker/compare/v0.2.1...v0.3.0

[0.2.0]: https://github.com/kirypto/TimelineTracker/compare/v0.2.0...v0.2.1

[0.2.0]: https://github.com/kirypto/TimelineTracker/compare/v0.1.3...v0.2.0

[0.1.3]: https://github.com/kirypto/TimelineTracker/compare/v0.1.2...v0.1.3

[0.1.2]: https://github.com/kirypto/TimelineTracker/compare/v0.1.1...v0.1.2

[0.1.1]: https://github.com/kirypto/TimelineTracker/compare/v0.1.0...v0.1.1

[0.1.0]: https://github.com/kirypto/TimelineTracker/releases/tag/v0.1.0
