from output.output_adapter import OutputAdapter

class LotusOutputAdapter(OutputAdapter):
    name: str = "Lotus"

    def write(self, data: dict, destination: str) -> None:
        print(f"Writing to Lotus: {destination}")
