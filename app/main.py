from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .core.helpers import getpathrow
from .core.stac import stac_test



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})

@app.get("/getpathrow")
async def get_path_row(lon: float, lat: float):
    return getpathrow(lon, lat)
    
@app.get("/stac")
async def stac():
    return {"result": stac_test()}