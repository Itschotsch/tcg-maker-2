import pandas as pd

from fastapi import Request, Response

class OutputAdapter:
    name: str

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        raise NotImplementedError("OutputAdapter subclasses must implement the get_display_name method.")

    async def write(self, process_dir: str, configuration: dict) -> Response:
        raise NotImplementedError("OutputAdapter subclasses must implement the write method.")
