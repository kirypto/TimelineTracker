# Timeline Tracker API

## Summary

Timeline Tracker is a tool developed to assist in planning and organizing TTRPG campaigns, fictional narratives, or any other creative
writing project. This tool can help you manage the people, places, items, events, and lore of constructed worlds. The initial motivation for
this project came from my need to track and manage the plenitude of ideas that I have for a TTRPG campaign that I am running.

See [Resource Details](Wiki/resourceDetails.md) for in-depth explanation on how information can be stored and retrieved using Timeline
Tracker API.

## Deploying / Using

[Instructions for deploying Timeline Tracker API to use can be found here](Wiki/projectDeployment.md).

## Contributing / Developing

[Instructions for setting up for Timeline Tracker API development can be found here](Wiki/projectSetup.md).

## API Specification

The Timeline Tracker API specification is written making use of SwaggerHub web tool and can be viewed here:
[Timeline Tracker API Specification v0.1.0][swaggerHubTimelineTrackerSpec].

## Project Standards

This project conforms to the following standards:

- [Semantic Versioning 2.0.0][semver2.0.0]
- [Keep A Changelog 1.0.0][changelog1.0.0]
- [YAML Ain’t Markup Language (YAML™) Version 1.2][yaml1.2]
- [OpenAPI Specification Version 3.0.3][openAPI3.0.3]
- [RFC 6902 JavaScript Object Notation (JSON) Patch][rfc6902]
- [RFC 7231 Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content][rfc7231]
- [RFC 8259 The JavaScript Object Notation (JSON) Data Interchange Format][rfc8259]
  - __Exception:__ JSON responses from this API may include the numeric symbols `Infinity`, `-Infinity`, and `NaN`. 

[swaggerHubTimelineTrackerSpec]: https://app.swaggerhub.com/apis-docs/kirypto/TimelineTracker/0.1.0

[rfc6902]: https://tools.ietf.org/html/rfc6902

[rfc8259]: https://tools.ietf.org/html/rfc8259

[rfc7231]: https://tools.ietf.org/html/rfc7231#section-4.2.2

[yaml1.2]: https://yaml.org/spec/1.2/spec.html

[openAPI3.0.3]: https://swagger.io/specification/

[semver2.0.0]: https://semver.org/spec/v2.0.0.html

[changelog1.0.0]: https://keepachangelog.com/en/1.0.0/
