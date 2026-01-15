import pandas as pd

class ProcessAdapter:
    name: str

    def __init__(self) -> None:
        pass

    def process(self, data: pd.DataFrame) -> str:
        raise NotImplementedError("ProcessAdapter subclasses must implement the process method.")
