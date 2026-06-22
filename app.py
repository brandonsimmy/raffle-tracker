from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from scanner import get_competitions

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    competitions = get_competitions()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "competitions": competitions
        }
    )