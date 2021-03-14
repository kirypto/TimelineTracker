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
- The following can be used as a `config.yaml` example:

```yaml
---
# Configuration for the Timeline Tracker Application
timeline_tracker_app_config: {
  repositories_config: {
    # Repository type supports 'json' or 'memory', but 'memory' will reset each time the app is run
    # - If 'json' type is specified, the json_repository_directory_root must also be configured
    repository_type: json,
    # json_repositories_directory_root is the location of persisted json files so the app can read and write to the same files when
    # restarted
    json_repositories_directory_root: "/path/to/preferred/repository/location"
  }
}

# Configuration for the Python Flask service running the application
flask_run_config: {
  host: localhost,
  port: 5000,
}

# Configuration for the Flask CORS extension
# Parameters described https://flask-cors.readthedocs.io/en/latest/api.html
flask_cors_config: {
  origins: [
      http://localhost:12345,
      "*",
  ],
}
```

## Running the API

- Read and confirm the settings of the `runWithFlask.ps1`
- Run it from the root TTAPI directory: `./Script/runWithflask.ps1`

[projectReleases]: https://github.com/kirypto/TimelineTracker/releases/latest