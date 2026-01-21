from fastapi import Response
import io
import os
import shutil

from output.output_adapter import OutputAdapter

class ZIPDownloadOutputAdapter(OutputAdapter):

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        return f"ZIP Download"

    async def write(self, process_dir: str, configuration: dict) -> Response:
        print(f"Writing to ZIP: {process_dir}")

        zip_buffer = zip(process_dir)
        response = Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=data.zip"}
        )
        zip_buffer.close()

        return response

def zip(zip_dir: str) -> io.BytesIO:
    """
    Zip the given directory and return the zip file as a BytesIO object, which needs to be closed later.
    """

    # Create a BytesIO object to store the zip file in memory
    zip_buffer = io.BytesIO()

    # Create a zip archive of the process_dir
    shutil.make_archive(
        os.path.join(os.getcwd(), "data"),
        "zip",
        zip_dir
    )

    # Read the created zip file into the buffer
    with open(os.path.join(os.getcwd(), "data.zip"), "rb") as f:
        zip_buffer.write(f.read())

    # Clean up the created zip file
    os.remove(os.path.join(os.getcwd(), "data.zip"))

    return zip_buffer
