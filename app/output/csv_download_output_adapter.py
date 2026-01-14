from fastapi import Request, Response
import pandas as pd

from output.output_adapter import OutputAdapter

class CSVDownloadOutputAdapter(OutputAdapter):
    name: str = "CSV Download"

    def __init__(self) -> None:
        pass

    def write(self, request: Request, data: pd.DataFrame) -> Response:
        print(f"Writing to CSV Download: {data}")

        # CSV export
        csv_bytes = data.to_csv(index=False).encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data.csv"}
        )
