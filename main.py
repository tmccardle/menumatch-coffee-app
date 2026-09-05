from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.menus import router

app = FastAPI(title="Menumatch + Encinitas Coffee Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Menumatch + Encinitas Coffee Guide API is ready"}
