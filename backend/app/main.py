from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router

app = FastAPI(
    title="STRATUM API",
    description=(
        "Agentic Enterprise Transformation Platform — анализ документов, "
        "карта покрытия методологии, целевая модель, ROI и регуляторный скрининг РФ."
    ),
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {
        "product": "STRATUM",
        "tagline": "Agentic Enterprise Transformation Platform",
        "version": __version__,
        "docs": "/docs",
    }
