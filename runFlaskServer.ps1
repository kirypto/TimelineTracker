# Runs the Timeline Tracker REST API via Flask microservice

$env:FLASK_APP = './Source/Python/adapter/flask/flask_app:construct_flask_app';
$env:FLASK_ENV = 'development';
./venv/Scripts/python -m flask run;