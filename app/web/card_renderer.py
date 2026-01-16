from datetime import datetime
from fastapi import APIRouter, Request, Response
import pandas as pd

from input import input_manager
from output import output_manager
from process import process_manager
from web import web_server

router = APIRouter()

@router.get("/card_renderer")
async def main(request: Request):
    return web_server.templates.TemplateResponse(
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

    # Read data using the input adapter
    data: pd.DataFrame = input_adapter.read()

    # Process data using the process adapter
    process_dir: str = process_adapter.process(data)

    # Render cards using the output adapter
    response: Response = output_adapter.write(
        process_dir=process_dir,
    )

    return response

def render(data: dict) -> dict:
    # Placeholder render function
    return {"rendered_data": data}
