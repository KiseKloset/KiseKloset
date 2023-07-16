import os
import gdown
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

app = FastAPI(title='Smart Fashion API', version='1.1.0')
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
    app.state.static_files = { "directory": str(ROOT / "static"), "prefix": "/static" }
    app.state.retrieval_content = service.preload("cuda:0")
    print("Finish startup")


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


@app.get("/", response_class=HTMLResponse)
async def home():
    with open(ROOT / "templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


app.include_router(tryon_router, prefix="/try-on")
app.include_router(retrieval_router, prefix="/retrieval")
app.include_router(upscale_router, prefix="/upscale")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host=settings.HOST, port=settings.PORT, reload=True)
