from pathlib import Path

from flask import Flask


# File Paths
_PROJECT_ROOT = Path(__file__).parents[2]
_RESOURCE_FOLDER = _PROJECT_ROOT.joinpath("Source", "Resources")


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


if __name__ == '__main__':
    flask_web_app.run()
