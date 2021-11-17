# Configurable/
venvPath="venv";
configFilePath="config.yaml";
pythonCommand=python3;
# ##############################


# Ensures python output is send straight to terminal without first being buffered
export PYTHONUNBUFFERED=1

# Add the Python root to the PYTHON path relative to project root
pwd="$(pwd)}"
export PYTHONPATH="${PYTHONPATH}:${pwd}/Source/Python"

# Flask environment type ('production' or 'development')
export FLASK_ENV="production"
#export FLASK_ENV="development"

# Activate the python virtual environment
if [ -d "${venvPath}" ] && [ -d "${venvPath}/bin" ]; then
  source "${venvPath}/bin/activate";
fi

# Ensure data is up to date
echo "    ==================== Updating persisted data ====================";
$pythonCommand ./Script/data_migration.py --config $configFilePath;
migrationExitCode=$?;
if [[ $migrationExitCode -ne 0 ]]; then
    echo "Failed to update persisted data (exit code $migrationExitCode). Aborting application launch.";
    exit 1;
fi

# Actually run the app
echo "    ====================   Running Application   ====================";
$pythonCommand ./Source/Python/adapter/runners/flask/flask_app.py $configFilePath;
