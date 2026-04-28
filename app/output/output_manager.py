from typing import List

from output.output_adapter import OutputAdapter
from output.csv_download_output_adapter import CSVDownloadOutputAdapter
from output.lotus_output_adapter import LotusOutputAdapter
from output.none_output_adapter import NoneOutputAdapter
from output.zip_download_output_adapter import ZIPDownloadOutputAdapter

adapters: List[OutputAdapter] = [
    NoneOutputAdapter(),
    LotusOutputAdapter(),
    CSVDownloadOutputAdapter(),
    ZIPDownloadOutputAdapter(),
]

def get_adapter_by_name(name: str) -> OutputAdapter:
    for adapter in adapters:
        if adapter.get_display_name() == name:
            return adapter
    raise ValueError(f"Output adapter with name '{name}' not found.")
