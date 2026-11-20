from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router
from app.core.settings import settings

app = FastAPI(
    title="STRATUM API",
    description=(
        "Agentic Enterprise Transformation Platform — анализ документов, "
        "карта покрытия методологии, целевая модель, ROI и регуляторный скрининг РФ."
    ),
    version=__version__,
)

origins = settings.cors_origin_list
allow_credentials = "*" not in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not allow_credentials else origins,
    allow_credentials=allow_credentials,
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
