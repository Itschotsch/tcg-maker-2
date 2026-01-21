from fastapi import Request, Response
import os
import pandas as pd

from output.output_adapter import OutputAdapter

class CSVDownloadOutputAdapter(OutputAdapter):

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        return f"CSV Download"

    async def write(self, process_dir: str, configuration: dict) -> Response:
        print(f"Writing to CSV Download: {process_dir}")

        # Read the data from the process directory
        data = pd.read_csv(os.path.join(process_dir, "csv", "data.csv"))

        # CSV export
        csv_bytes = data.to_csv(index=False).encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data.csv"}
        )
