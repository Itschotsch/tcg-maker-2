class OutputAdapter:
    name: str

    def write(self, data: dict, destination: str) -> None:
        raise NotImplementedError("OutputAdapter subclasses must implement the write method.")
