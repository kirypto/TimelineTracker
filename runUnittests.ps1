# Runs all python unittests for the Timeline Tracker project

$Env:PYTHONPATH += ';./Source/Python';
./venv/Scripts/python -m unittest discover -s .\Test\Unittest\ -t .