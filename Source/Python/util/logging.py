import logging as _logging
import sys as _sys


def configure_logging(*, console_level: int = _logging.INFO) -> None:
    root = _logging.getLogger()
    root.setLevel(_logging.DEBUG)

    console_handler = _logging.StreamHandler(_sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = _logging.Formatter("%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s")
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)
