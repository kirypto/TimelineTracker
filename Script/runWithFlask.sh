# Ensures python output is send straight to terminal without first being buffered
export PYTHONUNBUFFERED=1

# Add the Python root to the PYTHON path relative to project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)/Source/Python"

# Flask environment type ('production' or 'development')
export FLASK_ENV="production"

# Actually run the app (assuming configuration is in a 'config.yaml' file in the project root)
python "$(pwd)/Source/Python/adapter/runners/flask/flask_app.py" ./config.yaml