# Application Setup

## Requirements

- Python >= 3.7
- Python packages as laid out in `requirements.txt`

## App Configuration

- Create a configuration file, the following can be used as an example:

```yaml
---
# Configuration for the Timeline Tracker Application
timeline_tracker_app_config: {
  repositories_config: {
    # Repository type supports 'json' or 'memory'
    # - If 'json' type is specified, the json_repository_directory_root must also be configured
    repository_type: memory,
    #    json_repositories_directory_root: "/path/to/repo/root"
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

__In PyCharm__

- Select `flask_app.py` as the primary script.
- Specify the above configuration file path as the first argument _(parameter)_.
- Set the following environment variables:`PYTHONUNBUFFERED=1;FLASK_ENV=development`

## Running Tests

__In PyCharm__

- Ensure the `Source/Python` directory is marked as a source root
- Select the `Test/Unittest` directory to create the PyCharm Unittest run config
- Modify the working directory parameter to point at the main project root.

## See Also

- For a more in-depth explanation of the domain, its resources, and its locations, see [Domain Design](domainDesign.md).