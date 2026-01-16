from fastapi import Request, Response
import io
import os
import shutil

from output.output_adapter import OutputAdapter
from output.zip_download_output_adapter import zip

class LotusOutputAdapter(OutputAdapter):
    name: str = "Lotus"

    def __init__(self) -> None:
        pass

    def write(self, process_dir: str) -> Response:
        print(f"Writing to Lotus: {process_dir}")

        # Get the content of the zip file
        zip_buffer = zip(process_dir)

        response = Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=lotus_output.zip"}
        )
        zip_buffer.close()

        return response
