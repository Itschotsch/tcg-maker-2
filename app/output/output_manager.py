from typing import List

from output.output_adapter import OutputAdapter
from output.lotus_output_adapter import LotusOutputAdapter

adapters: List[OutputAdapter] = [
    LotusOutputAdapter(),
]

def get_adapter_by_name(name: str) -> OutputAdapter:
    for adapter in adapters:
        if adapter.name == name:
            return adapter
    raise ValueError(f"Output adapter with name '{name}' not found.")
