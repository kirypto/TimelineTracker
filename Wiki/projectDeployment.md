# Application Setup

- Locate and download the `Deployable` zip from [the releases page][projectReleases].

## Requirements

- Install Python _(version >= 3.7)_ and pip.
- Install the required packages _(`pip install -r requirements.txt`)_.

## App Configuration

- Create a configuration file in the root TTAPI directory for project configuration. _(Recommended name is `config.yaml`, as that is the
  expected name by the script below)_
- If intending to run the API on anything other than `http://localhost:5000`, it is recommended to change the `servers` list in the
  `apiSpecification.json` file. This will allow the Swagger docs page to interact with your API.
- See the [Sample Config](sampleConfig.md) for an example.


## Running the API

- Read and confirm the settings of the `runWithFlask.ps1`
- Run it from the root TTAPI directory: `./Script/runWithflask.ps1`

[projectReleases]: https://github.com/kirypto/TimelineTracker/releases/latest