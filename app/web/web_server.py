from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import os
import uvicorn

from web import card_renderer, main_page, layout_constructor

log: logging.Logger = logging.getLogger(__name__)

# Create FastAPI app instance
app: FastAPI = FastAPI()
log.debug("Created FastAPI app instance.")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
log.debug("Mounted static files: /static")

# Set up templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)
log.debug(f"Templates directory set: {templates_dir}")

app.include_router(card_renderer.router)
app.include_router(main_page.router)
app.include_router(layout_constructor.router)

def run(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False
):
    global app, app_settings
    if reload:
        uvicorn.run(
            "web.web_server:app",
            host=host,
            port=port,
            reload=True,
        )
    else:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
        )
