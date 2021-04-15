### Sample Application Config

```yaml
---
# Configuration for the Timeline Tracker Application
timeline_tracker_app_config: {
  # Absolute path to the 'Resources' folder. Unless moved, this would be '/path/to/project/root/Source/Resources'
  resources_folder_path: "/path/to/project/resources/folder",

  repositories_config: {
    # Repository type supports 'json' or 'memory'
    # - If 'json' type is specified, the json_repository_directory_root must also be configured
    repository_type: memory,
    # repository_type: json,
    # json_repositories_directory_root: "/path/to/repo/root"
  },
}


# Configuration for the Python Flask service running the application
flask_run_config: {
  host: localhost,
  port: 5000,
}


# Configuration for the Flask CORS extension
# Parameters described https://flask-cors.readthedocs.io/en/latest/api.html
flask_cors_config: {
  # Specify trusted origins, such as any front end
  origins: [
    # Use "*" to allow all
      "http://localhost:12345",
  ],
  # Specify allowed headers
  allow_headers: [
    # Use "*" to allow all
    # 'Content-Type' necessary if making any requests with a json body
      "Content-Type",
  ],
}
```