import logging
import os
from typing import List

from input.input_adapter import InputAdapter

log: logging.Logger = logging.getLogger(__name__)

adapters: List[InputAdapter] = []

# NotionInputAdapter
from input.notion_input_adapter import NotionInputAdapter
log.info("Adding NotionInputAdapters...")
for id in eval(os.getenv("NOTION_DATABASE_IDS", "[]")):
    log.info(f"Adding NotionInputAdapter with database_id: {id}...")
    adapters.append(NotionInputAdapter(database_id=id))

from input.csv_input_adapter import CSVInputAdapter
for file in sorted(os.listdir(os.path.join(os.getcwd(), "input"))):
    if file.endswith(".csv"):
        log.info(f"Adding CSVInputAdapter with file_name: {file}...")
        adapters.append(CSVInputAdapter(file_name=file))

from input.notion_csv_input_adapter import NotionCSVInputAdapter
for file in sorted(os.listdir(os.path.join(os.getcwd(), "input"))):
    if file.endswith(".csv"):
        log.info(f"Adding NotionCSVInputAdapter with file_name: {file}...")
        adapters.append(NotionCSVInputAdapter(file_name=file))

def get_adapter_by_name(name: str) -> InputAdapter:
    for adapter in adapters:
        if adapter.get_display_name() == name:
            return adapter
    raise ValueError(f"Input adapter with name '{name}' not found.")
