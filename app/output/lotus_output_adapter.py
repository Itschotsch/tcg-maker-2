from fastapi import Request, Response
import io
import os
import pandas as pd
import shutil
import zipfile

from output.output_adapter import OutputAdapter
from output.zip_download_output_adapter import zip_directory, zip_files

class LotusOutputAdapter(OutputAdapter):

    def __init__(self) -> None:
        pass

    def get_display_name(self) -> str:
        return f"Lotus ZIP Download"

    async def write(self, process_dir: str, configuration: dict) -> Response:
        print(f"Writing to Lotus: {process_dir}")

        # Load the process_dir/csv/data.csv as a DF
        data = pd.read_csv(os.path.join(process_dir, "csv", "data.csv"))

        # # Get the content of the zip file
        # zip_buffer = zip_directory(process_dir)

        # response = Response(
        #     content=zip_buffer.getvalue(),
        #     media_type="application/zip",
        #     headers={"Content-Disposition": "attachment; filename=lotus_output.zip"}
        # )
        # zip_buffer.close()
        
        # Group all cards by 1. set_release and 2. rarity
        # For each group, zip only these cards (process_dir/png/{id}.png) to process_dir/zip/{set_release}_{rarity}.zip
        # Finally, zip those zips (the entire dir) and return it as the response

        output_zip_dir = os.path.join(process_dir, "zip")
        os.makedirs(output_zip_dir, exist_ok=True)
        grouped = data.groupby(["set_release", "rarity"])
        all_zip_files = []

        for (set_release, rarity), group in grouped:
            # Clean up set_release and rarity for filename
            clean_set_release = str(set_release).lower().replace(" ", "_").replace("/", "_")
            clean_rarity = str(rarity).lower().replace(" ", "_").replace("/", "_")

            zip_filename = f"{clean_set_release}_{clean_rarity}.zip"
            zip_filepath = os.path.join(output_zip_dir, zip_filename)

            card_image_paths = []
            for _, row in group.iterrows():
                card_id = row["ID"]
                image_path = os.path.join(process_dir, "png", f"{card_id}.png")
                if os.path.exists(image_path):
                    card_image_paths.append(image_path)
                else:
                    print(f"Warning: Image not found for card ID {card_id} at {image_path}")

            if card_image_paths:
                with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for img_path in card_image_paths:
                        zipf.write(img_path, arcname=os.path.basename(img_path))
                all_zip_files.append(zip_filepath)
                print(f"Created {zip_filepath} with {len(card_image_paths)} images.")
            else:
                print(f"No images found for set_release: {set_release}, rarity: {rarity}. Skipping zip creation.")

        # Finally, zip all the created zip files into one main zip
        if all_zip_files:
            final_zip_buffer = zip_files(all_zip_files, zip_name="lotus_output")
            response = Response(            content=final_zip_buffer.getvalue(),
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=lotus_output.zip"}
            )
            final_zip_buffer.close()
        else:
            # If no zip files were created, return an empty zip or an error
            print("No card images were processed to create any zip files.")
            response = Response(
                content=b'',
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=lotus_output.zip"}
            )

        return response
