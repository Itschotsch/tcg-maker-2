class InputAdapter:

    def get_identifier(self) -> str:
        raise NotImplementedError("InputAdapter subclasses must implement the get_identifier method.")

    def get_display_name(self) -> str:
        raise NotImplementedError("InputAdapter subclasses must implement the get_display_name method.")

    async def read(self, source: str) -> dict:
        raise NotImplementedError("InputAdapter subclasses must implement the read method.")
