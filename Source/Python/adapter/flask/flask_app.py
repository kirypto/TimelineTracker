from pathlib import Path

from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint


# File Paths
_PROJECT_ROOT = Path(__file__).parents[4]
_RESOURCE_FOLDER = _PROJECT_ROOT.joinpath("Source", "Resources")

# Web Paths
_SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
_API_SPECIFICATION_URL = '/static/apiSpecification.json'  # Our API url (can of course be a local resource)

# Construct Flask web service
flask_web_app = Flask(
    __name__,
    root_path=_RESOURCE_FOLDER.joinpath("FlaskWebAppRoot").as_posix(),
    static_folder=_RESOURCE_FOLDER.joinpath("StaticallyServedFiles").as_posix(),
    static_url_path="/static",
)


# Setup web path root
@flask_web_app.route('/')
def hello_world():
    return 'It Works!'


# Call flask_swagger_ui blueprint factory function
swagger_ui_blueprint = get_swaggerui_blueprint(
    _SWAGGER_URL,
    _API_SPECIFICATION_URL,
)

# Register blueprint at URL
# (URL must match the one given to factory function above)
flask_web_app.register_blueprint(swagger_ui_blueprint, url_prefix=_SWAGGER_URL)

if __name__ == '__main__':
    flask_web_app.run()
