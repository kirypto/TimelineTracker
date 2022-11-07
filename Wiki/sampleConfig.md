### Sample Application Config

```yaml
---
# Application Secret. Generate a string and set it here. 
# Secure Password Generator is useful: https://passwordsgenerator.net/?length=42&symbols=1&numbers=1&lowercase=1&uppercase=1&similar=1&ambiguous=0&client=1&autoselect=0
secret_key: null

# Configuration for the Timeline Tracker Application
timeline_tracker_app_config: {
  # Absolute path to the 'Resources' folder. Unless moved, this would be '/path/to/project/root/Source/Resources'
  resources_folder_path: "/path/to/project/resources/folder",

  repositories_config: {
    # Specify python class path for each repository implementation. Built in repositories are memory and json:
    world_repo_class_path: adapter.persistence.in_memory_repositories.InMemoryWorldRepository,
    location_repo_class_path: adapter.persistence.in_memory_repositories.InMemoryLocationRepository,
    traveler_repo_class_path: adapter.persistence.in_memory_repositories.InMemoryTravelerRepository,
    event_repo_class_path: adapter.persistence.in_memory_repositories.InMemoryEventRepository,
    # world_repo_class_path: adapter.persistence.json_file_repositories.JsonFileWorldRepository,
    # location_repo_class_path: adapter.persistence.json_file_repositories.JsonFileLocationRepository,
    # traveler_repo_class_path: adapter.persistence.json_file_repositories.JsonFileTravelerRepository,
    # event_repo_class_path: adapter.persistence.json_file_repositories.JsonFileEventRepository,

    # - If 'json' type is specified, the json_repository_directory_root must also be configured
    # json_repositories_directory_root: "/path/to/repo/root"
  },
}


# Configuration for the Python Flask service running the application
flask_run_config: {
  host: "127.0.0.1",
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


auth_config: {
  # Can be changed, but must be a unique route and be configured on Auth0.com as a valid callback           
  auth_callback_route: "/auth-callback",
  
  # Settings from Auth0.com. Setup can be found here https://auth0.com/docs/quickstart/webapp/python.
  client_id: "<Auth0.com -> Application -> Client ID>",
  client_secret: "<Auth0.com -> Application -> Client Secret>",
  api_base_url: "<Auth0.com -> Application -> Domain>",
  access_token_url: "<Auth0.com -> Application -> Domain>/oauth/token",
  authorize_url: "<Auth0.com -> Application -> Domain>/authorize",
  client_kwargs: {
    scope: "openid profile email",
  },

  # Setting from Auth0.com for parsing bearer tokens from FE as described here https://auth0.com/docs/quickstart/backend/python/01-authorization.
  domain: "<Auth0.com -> Application -> Domain>",
  api_audience: "<Auth0.com -> Application -> TODO>", # TODO kirypto 2021-Aug-09: Fill in location of this
  algorithms: ["RS256"],
}
```