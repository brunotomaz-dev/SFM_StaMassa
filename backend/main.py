"""
Módulo principal da aplicação. Define as rotas da API.
CreatedAT: 09/08/2024
CreatedBy: Bruno Tomaz
"""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

# pylint: disable=E0401
from src.controller.maquina_ihm_controller import MaquinaIHMController

app = FastAPI()

maquina_ihm_controller = MaquinaIHMController()


# ================================================================================================ #
#                                               ROTAS                                              #
# ================================================================================================ #
@app.get("/")
def read_root():
    """Rota principal da API."""
    return {"Hello": "World"}


# ========================================= Automação DB ========================================= #
@app.get("/maquina_ihm")
def get_maquina_ihm(first_day: str, last_day: str):
    """
    Retorna os dados da máquina IHM no intervalo de datas especificado.
    Parâmetros:
    - first_day (str): Data de início do intervalo no formato 'YYYY-MM-DD'.
    - last_day (str): Data de término do intervalo no formato 'YYYY-MM-DD'.
    Retorna:
    - JSONResponse: Resposta JSON contendo os dados da máquina IHM no formato ISO.
    Exemplo:
    >>> get_maquina_ihm('2022-01-01', '2022-01-31')
    {
        "data": [
            {
                "timestamp": "2022-01-01T00:00:00",
                "valor1": 10,
                "valor2": 20
            },
            {
                "timestamp": "2022-01-02T00:00:00",
                "valor1": 15,
                "valor2": 25
            },
            ...
        ]
    }
    """

    data = maquina_ihm_controller.get_data((first_day, last_day))
    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "Data not found."}
        )
    return data.to_json(date_format="iso", orient="split")
