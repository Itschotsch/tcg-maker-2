from httpcore import Request, Response
import pandas as pd

from output.output_adapter import OutputAdapter

class LotusOutputAdapter(OutputAdapter):
    name: str = "Lotus"

    def __init__(self) -> None:
        pass

    def write(self, request: Request, data: pd.DataFrame) -> Response:
        print(f"Writing to Lotus: {data}")
        response = Response(
            status=200,
        )
        return response
