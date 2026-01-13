from datetime import datetime
from fastapi import APIRouter, Request
from input import input_manager
from output import output_manager

from web import web_server

router = APIRouter()

@router.get("/")
def main(request: Request):
    return web_server.templates.TemplateResponse(
        "main_page.jinja",
        {
            "request": request,
            "title": "TCG Maker 2",
            "author": "Aetherlab",
            "input_adapters": input_manager.adapters,
            "output_adapters": output_manager.adapters,
            "now": datetime.now(),
        }
    )
