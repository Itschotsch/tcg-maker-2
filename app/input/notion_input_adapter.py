import os
import logging
import pandas as pd

from notion2pandas import Notion2PandasClient

from input.input_adapter import InputAdapter

class NotionInputAdapter(InputAdapter):
    name: str = "Notion"
    database_id: str

    def __init__(self, database_id: str):
        """
        Create the adapter, storing the Notion database ID.
        """
        self.database_id = database_id

    def get_identifier(self) -> str:
        return f"{self.name}_{self.database_id}"

    def read(self) -> pd.DataFrame:
        """
        Read all rows from the Notion database into a pandas DataFrame using
        notion2pandas, automatically handling pagination and parsing.
        """
        log = logging.getLogger(__name__)

        # Ensure the token is present
        token = os.getenv("NOTION_TOKEN")
        if not token:
            raise ValueError("NOTION_TOKEN environment variable is not set")

        log.info(f"Reading from Notion database with ID: {self.database_id}")

        # Initialise the notion2pandas client
        client: Notion2PandasClient
        try:
            client = Notion2PandasClient(auth=token)
            log.info("Successfully created Notion2PandasClient")
        except Exception as e:
            log.error(f"Failed to initialize Notion2PandasClient: {e}")
            raise

        # Fetch the data as a DataFrame
        try:
            log.debug("Fetching data from Notion...")
            df: pd.DataFrame = client.from_notion_DB_to_dataframe(self.database_id)
            log.info(f"Successfully loaded {len(df)} rows from Notion")
        except Exception as e:
            log.error(f"Error while fetching Notion DB to DataFrame: {e}")
            raise

        return df
