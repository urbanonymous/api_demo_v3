from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", name="index")
def index():
    return templates.TemplateResponse("index.html")
