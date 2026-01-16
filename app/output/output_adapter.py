import pandas as pd

from fastapi import Request, Response

class OutputAdapter:
    name: str

    def __init__(self) -> None:
        pass

    def write(self, process_dir: str) -> Response:
        raise NotImplementedError("OutputAdapter subclasses must implement the write method.")
