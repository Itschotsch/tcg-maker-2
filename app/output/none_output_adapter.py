from fastapi import Response

from output.output_adapter import OutputAdapter

class NoneOutputAdapter(OutputAdapter):

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        return f"None"

    async def write(self, process_dir: str, configuration: dict) -> Response:
        print(f"Doing nothing...")

        # 204 No Content: 
        return Response(status_code=204)
