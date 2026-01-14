from httpcore import Request, Response
from output.output_adapter import OutputAdapter

class LotusOutputAdapter(OutputAdapter):
    name: str = "Lotus"

    def __init__(self) -> None:
        pass

    def write(self, request: Request, data: dict) -> Response:
        print(f"Writing to Lotus: {data}")
        response = Response()
        return response