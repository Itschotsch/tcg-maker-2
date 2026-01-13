from input.input_adapter import InputAdapter

class NotionInputAdapter(InputAdapter):
    name: str = "Notion"

    def read(self, source: str) -> dict:
        print(f"Reading from Notion: {source}")
        return {"data": "from Notion"}
