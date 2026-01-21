from typing import List

from process.process_adapter import ProcessAdapter
from process.anor_process_adapter import AnorProcessAdapter
from process.passthrough_process_adapter import PassthroughProcessAdapter

adapters: List[ProcessAdapter] = [
    AnorProcessAdapter(),
    PassthroughProcessAdapter(),
]

def get_adapter_by_name(name: str) -> ProcessAdapter:
    for adapter in adapters:
        if adapter.get_display_name() == name:
            return adapter
    raise ValueError(f"Process adapter with name '{name}' not found.")
