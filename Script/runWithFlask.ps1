# Ensures python output is send straight to terminal without first being buffered
$Env:PYTHONUNBUFFERED = 1;

# Add the Python root to the PYTHON path relative to project root
$Env:PYTHONPATH += ";.\Source\Python";

# Flask environment type
$Env:FLASK_ENV = "development";
#$Env:FLASK_ENV = "production";

# Actually run the app (assuming configuration is in a config.yaml file in the project root)
python .\Source\Python\adapter\flask\flask_app.py ./config.yaml