import os
import logging
import pandas as pd

from input.input_adapter import InputAdapter

class CSVInputAdapter(InputAdapter):

    file_name: str | None

    def __init__(self, file_name: str | None = None):
        self.file_name = file_name

    def get_identifier(self) -> str:
        return f"csv_import_{self.file_name}"

    def get_display_name(self) -> str:
        if self.file_name:
            return f"CSV Import ({self.file_name})"
        else:
            return f"CSV Import"

    async def read(self, sanitise = True) -> pd.DataFrame:
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
                return sanitise_dataframe(pd.read_csv(file_path)) if sanitise else pd.read_csv(file_path)
            else:
                log.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")
        else:
            csv_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".csv")])
            log.debug(f"CSV files: {csv_files}")
            if len(csv_files) == 0:
                log.error("No CSV files found in input directory")
                raise FileNotFoundError("No CSV files found in input directory")
            
            if len(csv_files) == 1:
                file_path = os.path.join(input_dir, csv_files[0])
                log.info(f"Reading from file: {file_path}")
                return sanitise_dataframe(pd.read_csv(file_path)) if sanitise else pd.read_csv(file_path)
            
            if len(csv_files) > 1:
                log.info(f"Found multiple files: {csv_files}")
                for file in csv_files:
                    if file == "data.csv":
                        file_path = os.path.join(input_dir, file)
                        log.info(f"Reading from file: {file_path}")
                        return sanitise_dataframe(pd.read_csv(file_path)) if sanitise else pd.read_csv(file_path)
                
                file_path = os.path.join(input_dir, csv_files[0])
                log.info(f"Reading from file: {file_path}")
                return sanitise_dataframe(pd.read_csv(file_path)) if sanitise else pd.read_csv(file_path)
            
            raise ValueError("Multiple CSV files found in input directory")

def sanitise_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    df["cost_terra"] = df["cost_terra"].apply(sanitise_value_as_string)
    df["cost_aqua"] = df["cost_aqua"].apply(sanitise_value_as_string)
    df["cost_aeris"] = df["cost_aeris"].apply(sanitise_value_as_string)
    df["cost_ignis"] = df["cost_ignis"].apply(sanitise_value_as_string)
    df["cost_magica"] = df["cost_magica"].apply(sanitise_value_as_string)
    df["cost_unshaped"] = df["cost_unshaped"].apply(sanitise_value_as_string)

    df["stats_offensive_strength"] = df["stats_offensive_strength"].apply(sanitise_value_as_string)
    df["stats_offensive_toughness"] = df["stats_offensive_toughness"].apply(sanitise_value_as_string)

    df["stats_defensive_strength"] = df["stats_defensive_strength"].apply(sanitise_value_as_string)
    df["stats_defensive_toughness"] = df["stats_defensive_toughness"].apply(sanitise_value_as_string)

    df["stats_barriers"] = df["stats_barriers"].apply(sanitise_value_as_string)

    return df

def sanitise_value_as_string(x: any) -> any:
    # Keep NaN/None as is.
    if pd.isna(x):
        return x
    
    # If it is a number (float or int), convert to int.
    if isinstance(x, (float, int)):
        return str(int(x))
        
    # If it is a string (like "Foo"), return it as is.
    return str(x)
