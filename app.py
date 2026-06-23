from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from scanner import get_competitions
import threading
import time

app = FastAPI()

templates = Jinja2Templates(directory="templates")

cached_data = []
last_updated = None


def update_loop():
    global cached_data, last_updated

    while True:
        try:
            print("Running background scrape...")
            cached_data = get_competitions()
            last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("Scrape failed:", e)

        time.sleep(300)


@app.on_event("startup")
def start_background_thread():
    thread = threading.Thread(
        target=update_loop,
        daemon=True
    )
    thread.start()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "competitions": cached_data,
            "last_updated": last_updated
        }
    )


@app.get("/api/competitions")
def api_competitions():

    return JSONResponse(
        {
            "competitions": cached_data,
            "last_updated": last_updated
        }
    )