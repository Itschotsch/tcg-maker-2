from fastapi import FastAPI
import uvicorn

app: FastAPI = FastAPI()
app_settings: dict = {}

@app.get("/")
def index():
    return {"message": "Hello World"}

class WebServer:

    def __init__(self, host: str="0.0.0.0", port: int=8000):
        global app, app_settings
        app_settings = {
            "host": host,
            "port": port,
        }

    def run(self, reload: bool = False):
        if reload:
            uvicorn.run(
                "web.web_server:app",
                host=app_settings["host"],
                port=app_settings["port"],
                reload=True,
            )
        else:
            uvicorn.run(
                app,
                host=app_settings["host"],
                port=app_settings["port"],
                reload=False,
            )
