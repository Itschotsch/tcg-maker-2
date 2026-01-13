from fastapi import APIRouter, Request

from web import web_server

router = APIRouter()

@router.get("/")
def main(request: Request):
    return web_server.templates.TemplateResponse("main_page.jinja", {"request": request})
