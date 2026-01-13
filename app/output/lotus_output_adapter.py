from output.output_adapter import OutputAdapter

class LotusOutputAdapter(OutputAdapter):
    name: str = "Lotus"

    def write(self, data: dict) -> None:
        print(f"Writing to Lotus: {data}")
