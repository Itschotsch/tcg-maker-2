from typing import List

from input.input_adapter import InputAdapter
from input.notion_input_adapter import NotionInputAdapter

adapters: List[InputAdapter] = [
    NotionInputAdapter(),
]
