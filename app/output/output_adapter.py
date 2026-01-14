import pandas as pd

from httpcore import Request, Response

class OutputAdapter:
    name: str

    def __init__(self) -> None:
        pass

    def write(self, request: Request, data: pd.DataFrame) -> Response:
        raise NotImplementedError("OutputAdapter subclasses must implement the write method.")
