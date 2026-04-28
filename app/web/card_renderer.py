from datetime import datetime
from fastapi import APIRouter, Request, Response
import os
import pandas as pd
import uuid

from input import input_manager
from output import output_manager
from process import process_manager
from web import web_server

router = APIRouter()

@router.get("/card_renderer")
async def main(request: Request):
    return web_server.templates.TemplateResponse(
        request,
        "card_renderer.jinja",
        {
            "request": request,
            "title": "TCG Maker 2",
            "author": "Aetherlab",
            "input_adapters": input_manager.adapters,
            "output_adapters": output_manager.adapters,
            "process_adapters": process_manager.adapters,
            "now": datetime.now(),
        }
    )

@router.post("/card_renderer")
async def render_cards(request: Request):
    form_data = await request.form()
    input_adapter_name = form_data.get("input_adapter")
    output_adapter_name = form_data.get("output_adapter")
    process_adapter_name = form_data.get("process_adapter")
    card_ids_str = form_data.get("card_ids")
    release_label = form_data.get("release_label")
    commit_to_repo = form_data.get("commit_to_repo") == "true"
    internal_edition_label = form_data.get("internal_edition_label")

    # Find the selected input adapter
    input_adapter: input_manager.InputAdapter
    try:
         input_adapter = input_manager.get_adapter_by_name(input_adapter_name)
    except ValueError:
        return {"error": f"Input adapter '{input_adapter_name}' not found."}

    # Find the selected output adapter
    output_adapter: output_manager.OutputAdapter
    try:
        output_adapter = output_manager.get_adapter_by_name(output_adapter_name)
    except ValueError:
        return {"error": f"Output adapter '{output_adapter_name}' not found."}

    # Find the selected process adapter
    process_adapter: process_manager.ProcessAdapter
    try:
        process_adapter = process_manager.get_adapter_by_name(process_adapter_name)
    except ValueError:
        return {"error": f"Process adapter '{process_adapter_name}' not found."}

    # Prepare configuration
    _task_id = str(uuid.uuid4())
    _bleed_mm: float = 3
    _dpi: int = 300
    _dpmm: float = _dpi / 25.426829268
    _card_width_no_bleed_mm: float = 63.5
    _card_height_no_bleed_mm: float = 88.9
    _card_border_radius_mm: float = 3

    configuration: dict = {
        "meta": {
            "task_id": _task_id,
            "input_path": os.path.join(os.getcwd(), "input"),
            "process_path": os.path.join(os.getcwd(), "process", _task_id),
            "output_path": os.path.join(os.getcwd(), "output"),
            "commit_to_repo": commit_to_repo,
            "internal_edition_label": internal_edition_label,
        },
        "card": {
            "bleed": {
                "mm": _bleed_mm,
                "px": round(_bleed_mm * _dpmm),
            },
            "dpi": {
                "in": _dpi,
                "mm": _dpmm,
            },
            "width": {
                "no_bleed": {
                    "mm": _card_width_no_bleed_mm,
                    "px": round(_card_width_no_bleed_mm * _dpmm),
                },
                "bleed": {
                    "mm": _card_width_no_bleed_mm + _bleed_mm * 2,
                    "px": round((_card_width_no_bleed_mm + _bleed_mm * 2) * _dpmm),
                },
            },
            "height": {
                "no_bleed": {
                    "mm": _card_height_no_bleed_mm,
                    "px": round(_card_height_no_bleed_mm * _dpmm),
                },
                "bleed": {
                    "mm": _card_height_no_bleed_mm + _bleed_mm * 2,
                    "px": round((_card_height_no_bleed_mm + _bleed_mm * 2) * _dpmm),
                },
            },
            "border_radius": {
                "mm": _card_border_radius_mm,
                "px": round(_card_border_radius_mm * _dpmm),
            },
        },
        "release": {
            "label": {
                "display": release_label if release_label else None
            }
        },
    }

    # Read data using the input adapter
    print(f"Reading data from {input_adapter} / {input_adapter.get_display_name()}...")
    data: pd.DataFrame = await input_adapter.read(
        configuration=configuration
    )

    if card_ids_str is not None and card_ids_str.strip() != "":
        try:
            card_ids = [int(id.strip()) for id in card_ids_str.split(',')]
            data = data[data["ID"].isin(card_ids)]
        except ValueError:
            return {"error": "Invalid card IDs provided. Please enter a comma-separated list of integers."}

    # DEBUG: Only render few cards
    # data = data[data["ID"].isin(range(509, 512 + 1))]

    # Process data using the process adapter
    process_dir: str = await process_adapter.process(
        data=data,
        configuration=configuration
    )

    # Render cards using the output adapter
    response: Response = await output_adapter.write(
        process_dir=process_dir,
        configuration=configuration,
    )

    return response

def render(data: dict) -> dict:
    # Placeholder render function
    return {"rendered_data": data}
