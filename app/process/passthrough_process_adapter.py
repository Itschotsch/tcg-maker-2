import os
import pandas as pd
from util import git_util
import uuid

from process.process_adapter import ProcessAdapter

class PassthroughProcessAdapter(ProcessAdapter):

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        return f"Passthrough"

    async def process(self, data: pd.DataFrame, configuration: dict) -> str:
        """
        Processes the given data and returns the path to the process directory.
        """
        print(f"Writing to Anor: {data}")

        id: uuid = uuid.uuid4()
        print(f"UUID: {id}")

        process_dir: str = configuration["meta"]["process_path"]
        print(f"Process directory: {process_dir}")

        os.makedirs(os.path.join(process_dir, "csv"), exist_ok=True)
        data.to_csv(os.path.join(process_dir, "csv", "data.csv"), index=False)

        return process_dir
