import pandas as pd

from input.csv_input_adapter import CSVInputAdapter, sanitise_dataframe
from input.notion_input_adapter import sanitise_notion_dataframe

class NotionCSVInputAdapter(CSVInputAdapter):

    def __init__(self, file_name: str | None = None):
        super().__init__(file_name)

    def get_identifier(self) -> str:
        return f"notion_csv_input_adapter_{self.file_name}"

    def get_display_name(self) -> str:
        if self.file_name:
            return f"Notion CSV Import ({self.file_name})"
        else:
            return f"Notion CSV Import"

    async def read(self, configuration: dict) -> pd.DataFrame:
        df: pd.DataFrame = await super().read(configuration, sanitise=False)
        return sanitise_dataframe(sanitise_notion_dataframe(df))
