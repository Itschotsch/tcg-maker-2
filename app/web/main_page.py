from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/")
def main(request: Request):
    return RedirectResponse(url="/card_renderer")
