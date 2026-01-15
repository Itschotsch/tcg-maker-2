from typing import List

from process.process_adapter import ProcessAdapter
from process.anor_process_adapter import AnorProcessAdapter

adapters: List[ProcessAdapter] = [
    AnorProcessAdapter(),
]

def get_adapter_by_name(name: str) -> ProcessAdapter:
    for adapter in adapters:
        if adapter.name == name:
            return adapter
    raise ValueError(f"Process adapter with name '{name}' not found.")
