from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

try:
    from routers.menus import router
except ImportError:
    from menus import router

app = FastAPI(title="Menumatch + Encinitas Coffee Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/encinitas.html")
def encinitas_guide():
    return FileResponse(Path(__file__).parent / "encinitas.html")


@app.get("/")
def root():
    return {"message": "Menumatch + Encinitas Coffee Guide API is ready"}
