import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

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

THEME_FILE = Path(__file__).parent / "active_theme.json"


@app.get("/api/theme")
def get_active_theme():
    if THEME_FILE.exists():
        try:
            return json.loads(THEME_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


@app.post("/api/theme")
async def set_active_theme(request: Request):
    try:
        data = await request.json()
        if isinstance(data, dict):
            THEME_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return {"status": "ok", "saved_keys": len(data)}
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)})
    return JSONResponse(status_code=400, content={"status": "bad_request"})


ROOT = Path(__file__).parent
NO_STORE = {"Cache-Control": "no-store, max-age=0"}


@app.get("/card-dots.png")
def card_dots():
    return FileResponse(ROOT / "card-dots.png")


@app.get("/polka-dots.png")
def polka_dots():
    return FileResponse(ROOT / "polka-dots.png")


@app.get("/tessellation.png")
def tessellation():
    return FileResponse(ROOT / "tessellation.png")


@app.get("/encinitas.html")
def encinitas_guide():
    return FileResponse(ROOT / "encinitas.html", headers=NO_STORE)


@app.get("/theme-studio.html")
def theme_studio():
    return FileResponse(ROOT / "theme-studio.html", headers=NO_STORE)


@app.get("/")
def root():
    return FileResponse(ROOT / "encinitas.html", headers=NO_STORE)


@app.get("/api")
def api_ready():
    return {"message": "Menumatch + Encinitas Coffee Guide API is ready"}
