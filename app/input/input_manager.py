import logging
import os
from typing import List

from input.input_adapter import InputAdapter
from input.notion_input_adapter import NotionInputAdapter

log: logging.Logger = logging.getLogger(__name__)

adapters: List[InputAdapter] = []

for id in eval(os.getenv("NOTION_DATABASE_IDS", "[]")):
    log.info(f"Adding NotionInputAdapter with database_id: {id}")
    adapters.append(NotionInputAdapter(database_id=id))

def get_adapter_by_name(name: str) -> InputAdapter:
    for adapter in adapters:
        if adapter.name == name:
            return adapter
    raise ValueError(f"Input adapter with name '{name}' not found.")
