"""
Módulo principal da aplicação.
Criado em: 09/08/2024
Criado por: Bruno Tomaz
"""

import uvicorn
from fastapi import FastAPI
from src.helpers.scheduler_tasks import start_scheduler

# pylint: disable=import-error
from src.router import (
    local_route,
    machine_route,
    protheus_cyv_route,
    protheus_sb1_route,
    protheus_sb2_route,
    protheus_sd3_route,
)

app = FastAPI()

app.include_router(machine_route.machine_router, prefix="/machine", tags=["Maquinas"])
app.include_router(local_route.local_router, prefix="/local", tags=["Local"])
app.include_router(
    protheus_cyv_route.protheus_cyv_router, prefix="/protheus_cyv", tags=["Protheus CYV"]
)
app.include_router(
    protheus_sb1_route.protheus_sb1_router, prefix="/protheus_sb1", tags=["Protheus SB1"]
)
app.include_router(
    protheus_sb2_route.protheus_sb2_router, prefix="/protheus_sb2", tags=["Protheus SB2"]
)
app.include_router(
    protheus_sd3_route.protheus_sd3_router, prefix="/protheus_sd3", tags=["Protheus SD3"]
)


@app.get("/", tags=["Rota Principal da API"], summary="Rota principal da API.")
def read_root():
    """Rota principal da API."""
    return {
        "API SFM": "Rota principal da API. Seja bem-vindo!",
        "DOCS": "Para documentação, acesse: /docs",
        "REDOC": "Para documentação, acesse: /redoc",
        "OPENAPI": "Para documentação, acesse: /openapi.json",
    }


start_scheduler()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
