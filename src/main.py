import os
import gdown
import json
import zipfile
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from api.tryon.router import router as tryon_router
from api.upscale.router import router as upscale_router 

from api.retrieval import service
from api.retrieval.router import router as retrieval_router


FILE = Path(__file__).resolve()
ROOT = FILE.parent
STATIC_PATH = ROOT / "static"
LOGGED_IPS_PATH = './logged_ips.json'
LOGGED_IPs = {}

app = FastAPI(
    title='Smart Fashion API', 
    version='1.1.0',
    docs_url=None,
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=STATIC_PATH))


if not (STATIC_PATH / "images").exists():
    STATIC_PATH.mkdir(parents=True, exist_ok=True)
    out = str(STATIC_PATH / "images.zip")
    gdown.download("https://drive.google.com/uc?id=1pNIbQcflAlyUAYypASSy7UfevI4sFcMC", out)
    with zipfile.ZipFile(out, 'r') as zip_ref:
        zip_ref.extractall(str(STATIC_PATH))
    os.remove(out)  

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_headers=settings.CORS_HEADERS,
    allow_credentials=True,
    allow_methods=["*"],
)

# Preload model, data, ...
@app.on_event('startup')
async def startup_event():
    global LOGGED_IPs
    app.state.static_files = { "directory": str(ROOT / "static"), "prefix": "/static" }
    app.state.retrieval_content = service.preload("cuda:0")

    # load logged ips file:
    if Path(LOGGED_IPS_PATH).is_file():
        with open(LOGGED_IPS_PATH) as f:
            LOGGED_IPs = json.load(f)
    print("Finish startup")


@app.on_event("shutdown")
def shutdown_event():
    global LOGGED_IPs
    with open(LOGGED_IPS_PATH, 'w') as f:
        json.dump(LOGGED_IPs, f)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get the original 'detail' list of errors
    details = exc.errors()
    error_details = []

    for error in details:
        error_details.append({'error': error['msg'] + " " + str(error['loc'])})
    return JSONResponse(content={"message": error_details})


@app.get('/health', status_code=status.HTTP_200_OK, tags=['health'])
def perform_healthcheck() -> None:
    return JSONResponse(content={'message': 'success'})


@app.get('/log-ips', status_code=status.HTTP_200_OK, tags=['log'])
def perform_log_ips() -> None:
    global LOGGED_IPs
    with open(LOGGED_IPS_PATH, 'w') as f:
        json.dump(LOGGED_IPs, f)
    return JSONResponse(content={'message': 'success'})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Log ip
    global LOGGED_IPs
    cip = str(request.client.host)
    if LOGGED_IPs.get(cip) == None:
        LOGGED_IPs[cip] = 1
    else:
        LOGGED_IPs[cip] += 1

    with open(ROOT / "templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


app.include_router(tryon_router, prefix="/try-on")
app.include_router(retrieval_router, prefix="/retrieval")
app.include_router(upscale_router, prefix="/upscale")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host=settings.HOST, port=settings.PORT, reload=False)
