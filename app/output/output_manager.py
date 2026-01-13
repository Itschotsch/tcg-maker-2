from typing import List

from output.output_adapter import OutputAdapter
from output.lotus_output_adapter import LotusOutputAdapter

adapters: List[OutputAdapter] = [
    LotusOutputAdapter(),
]
