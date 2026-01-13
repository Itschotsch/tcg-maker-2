class InputAdapter:
    name: str

    def read(self, source: str) -> dict:
        raise NotImplementedError("InputAdapter subclasses must implement the read method.")
