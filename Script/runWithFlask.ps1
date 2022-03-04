# Configurable
$venvPath = "venv";
$configFilePath = "config.yaml";
# ##############################


# Ensures python output is send straight to terminal without first being buffered
$Env:PYTHONUNBUFFERED = 1;

# Add the Python root to the PYTHON path relative to project root
$Env:PYTHONPATH += ";.\Source\Python";

# Flask environment type
$Env:FLASK_ENV = "development";
#$Env:FLASK_ENV = "production";

# Activate the python virtual environment
if (Test-Path -Path "$venvPath" -Type "Container") {
    .\venv\Scripts\Activate.ps1;
}

# Ensure data is up to date
Write-Host "    ==================== Updating persisted data ====================";
python .\Script\data_migration.py --config $configFilePath;
$migrationExitCode = $LASTEXITCODE;
if ($migrationExitCode -ne 0) {
    Write-Host "Failed to update persisted data (exit code $migrationExitCode). Aborting application launch.";
    exit 1;
}

# Actually run the app
Write-Host "    ====================   Running Application   ====================";
python .\Source\Python\adapter\runners\flask_app.py $configFilePath;