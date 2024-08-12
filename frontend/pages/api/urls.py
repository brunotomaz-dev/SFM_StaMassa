"""Módulo com urls da API."""

from enum import Enum


class APIUrl(Enum):
    """
    Enum com as urls da API.

    Attributes:
    - URL_MAQ_IHM (str): URL da API que retorna os dados da máquina IHM.
        Precisa de dois parâmetros: start (str) e end (str).
    - URL_MAQ_INFO (str): URL da API que retorna os dados da máquina Info.
        Precisa de dois parâmetros: start (str) e end (str).
    - URL_MAQ_PROD (str): URL da API que retorna os dados de produção da máquina Info.
        Precisa de dois parâmetros: start (str) e end (str).

    Exemplo de URL:
    http://localhost:8000/maquina_ihm?start=2022-01-01&end=2022-01-31

    Exemplo de Uso:
    >>> f"{APIUrl.URL_MAQ_IHM.value}?start=2022-01-01&end=2022-01-31"
    "http://localhost:8000/maquina_ihm?start=2022-01-01&end=2022-01-31"
    """

    URL_MAQ_INFO = "http://localhost:8000/maquina_info"
    URL_MAQ_IHM = "http://localhost:8000/maquina_ihm"
    URL_MAQ_PROD = "http://localhost:8000/maquina_info/production"
    URL_MAQ_QUALIDADE = "http://localhost:8000/maquina_qualidade"
