class InputAdapter:
    name: str

    def get_identifier(self) -> str:
        return self.name

    def read(self, source: str) -> dict:
        raise NotImplementedError("InputAdapter subclasses must implement the read method.")
