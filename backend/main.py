"""
Módulo principal da aplicação. Define as rotas da API.
CreatedAT: 09/08/2024
CreatedBy: Bruno Tomaz
"""

from fastapi import FastAPI

app = FastAPI()


# ================================================================================================ #
#                                               ROTAS                                              #
# ================================================================================================ #
@app.get("/")
def read_root():
    """Rota principal da API."""
    return {"Hello": "World"}
