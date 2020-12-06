## Project Setup

### Requirements

- Python
- Flask (python)
- venv

### Running the API

- Setup a python `venv`.
- Install python Flask.
- Set `FLASK_APP` env var to point at `./Source/Adapter/flask_app.py`.
- Run `./venv/Scripts/python -m flask run`.
- Alternatively, run `./runFlaskServer.ps1` which sets the env var and runs the
flask command above.

### Running Tests

- Tests are written using `unittest` and are located in `Test > unittest`
- The `./Source/Python` directory must be added to the `PYTHONPATH` environment
variable.
   - In PyCharm, right click the folder and select _'mark directory as -> source
   root'_.
   - In PowerShell, run `$Env:PYTHONPATH += ./Source/Python`.
- To run the tests:
   - From PyCharm, right click the test folder and select _'create unittests in
   unittests'_ and change the working directory to the project root.
   - From PowerShell, run `python -m unittest discover -s .\Test\unittest\ 
   -t .`.
