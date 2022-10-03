from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.services import templates as service

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/", name="index", response_class=HTMLResponse)
async def index(request: Request):
    data = await service.generate_index_data()
    return templates.TemplateResponse("index.html", {"request": request, "data": data})
