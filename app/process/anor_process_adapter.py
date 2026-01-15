import os
import pandas as pd
import uuid

from process.process_adapter import ProcessAdapter

class AnorProcessAdapter(ProcessAdapter):
    name: str = "Anor"

    def __init__(self) -> None:
        pass

    def process(self, data: pd.DataFrame) -> str:
        print(f"Writing to Anor: {data}")

        id: uuid = uuid.uuid4()
        print(f"UUID: {id}")

        process_dir = os.path.join(os.getcwd(), "process", "anor", str(id))
        print(f"Process directory: {process_dir}")

        os.makedirs(process_dir, exist_ok=True)
        data.to_csv(os.path.join(process_dir, "data.csv"), index=False)

        return process_dir
