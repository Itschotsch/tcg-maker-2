from fastapi import Request, Response
import os
import pandas as pd

from output.output_adapter import OutputAdapter

class CSVDownloadOutputAdapter(OutputAdapter):
    name: str = "CSV Download"

    def __init__(self) -> None:
        pass

    def write(self, request: Request, process_dir: str) -> Response:
        print(f"Writing to CSV Download: {id}")

        # Read the data from the process directory
        data = pd.read_csv(os.path.join(process_dir, "data.csv"))

        # CSV export
        csv_bytes = data.to_csv(index=False).encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data.csv"}
        )
