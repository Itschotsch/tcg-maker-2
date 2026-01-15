import os
import logging
import pandas as pd

from input.input_adapter import InputAdapter

class CSVInputAdapter(InputAdapter):
    name: str = "CSV Import"
    file_name: str | None

    def __init__(self, file_name: str | None = None):
        self.file_name = file_name

    def get_identifier(self) -> str:
        return f"{self.name}_{self.file_name}"

    def read(self) -> pd.DataFrame:
        # From /import (next to /app), read the CSV.
        # If a file called self.file_name exists, choose it.
        # Else, if only one CSV file exists, choose it, no matter the name.
        # Else, if more than one CSV file exists, choose the one called data.csv
        # Else, if any CSV files exist, choose a random .csv file.
        # Else, raise an error.

        log = logging.getLogger(__name__)

        input_dir = os.path.join(os.getcwd(), "input")
        log.debug(f"Input directory: {input_dir}")

        if self.file_name:
            file_path = os.path.join(input_dir, self.file_name)
            log.debug(f"File path: {file_path}")
            if os.path.isfile(file_path):
                log.info(f"Reading from file: {file_path}")
                return pd.read_csv(file_path)
            else:
                log.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")
        else:
            csv_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]
            log.debug(f"CSV files: {csv_files}")
            if len(csv_files) == 0:
                log.error("No CSV files found in input directory")
                raise FileNotFoundError("No CSV files found in input directory")
            
            if len(csv_files) == 1:
                file_path = os.path.join(input_dir, csv_files[0])
                log.info(f"Reading from file: {file_path}")
                return pd.read_csv(file_path)
            
            if len(csv_files) > 1:
                for file in csv_files:
                    if file == "data.csv":
                        file_path = os.path.join(input_dir, file)
                        log.info(f"Reading from file: {file_path}")
                        return pd.read_csv(file_path)
                
                file_path = os.path.join(input_dir, csv_files[0])
                log.info(f"Reading from file: {file_path}")
                return pd.read_csv(file_path)

            raise ValueError("Multiple CSV files found in input directory")
