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
    log.info(f"Added NotionInputAdapter with database_id: {id}.")

# CSVInputAdapter
from input.csv_input_adapter import CSVInputAdapter
adapters.append(CSVInputAdapter())

def get_adapter_by_name(name: str) -> InputAdapter:
    for adapter in adapters:
        if adapter.name == name:
            return adapter
    raise ValueError(f"Input adapter with name '{name}' not found.")
