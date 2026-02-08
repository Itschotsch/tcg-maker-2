from fastapi import Response
import io
import os
import shutil
import zipfile

from output.output_adapter import OutputAdapter

class ZIPDownloadOutputAdapter(OutputAdapter):

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        return f"ZIP Download"

    async def write(self, process_dir: str, configuration: dict) -> Response:
        print(f"Writing to ZIP: {process_dir}")

        zip_buffer = zip_directory(process_dir)
        response = Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=data.zip"}
        )
        zip_buffer.close()

        return response

def zip_directory(directory_path: str, zip_name: str = "data") -> io.BytesIO:
    """
    Zip the given directory and return the zip file as a BytesIO object, which needs to be closed later.
    """

    # Create a BytesIO object to store the zip file in memory
    zip_buffer = io.BytesIO()

    # Create a zip archive of the process_dir
    shutil.make_archive(
        os.path.join(os.getcwd(), zip_name),
        "zip",
        directory_path
    )

    # Read the created zip file into the buffer
    with open(os.path.join(os.getcwd(), f"{zip_name}.zip"), "rb") as f:
        zip_buffer.write(f.read())

    # Clean up the created zip file
    os.remove(os.path.join(os.getcwd(), f"{zip_name}.zip"))

    return zip_buffer

def zip_files(file_paths: list[str], zip_name: str = "data") -> io.BytesIO:
    """
    Zip the given files and return the zip file as a BytesIO object, which needs to be closed later.
    """

    # Create a BytesIO object to store the zip file in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            if os.path.exists(file_path):
                # arcname is the name of the file inside the zip.
                # We want just the filename, not the full path.
                zipf.write(file_path, arcname=os.path.basename(file_path))
            else:
                print(f"Warning: File not found and skipped for zipping: {file_path}")

    zip_buffer.seek(0)
    return zip_buffer
