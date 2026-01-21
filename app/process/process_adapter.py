import pandas as pd

class ProcessAdapter:
    name: str

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        raise NotImplementedError("ProcessAdapter subclasses must implement the get_display_name method.")

    async def process(self, data: pd.DataFrame, configuration: dict) -> str:
        raise NotImplementedError("ProcessAdapter subclasses must implement the process method.")
