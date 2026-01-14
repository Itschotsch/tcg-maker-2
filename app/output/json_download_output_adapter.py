from fastapi import Request, Response
import json

from output.output_adapter import OutputAdapter

class JSONDownloadOutputAdapter(OutputAdapter):
    name: str = "JSON Download"

    def __init__(self) -> None:
        pass

    def write(self, request: Request, data: dict) -> Response:
        print(f"Writing to JSON Download: {data}")

        # 1. Serialize the dictionary to a JSON string, then encode to bytes
        # default=str helps handle datetime objects (common in Notion data)
        json_bytes = json.dumps(data, default=str, indent=2).encode("utf-8")

        # 2. Pass content immediately to the constructor
        return Response(
            content=json_bytes,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=data.json"}
        )
