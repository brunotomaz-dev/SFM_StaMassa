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
    "f"{APIUrl.URL_MAQ_IHM.value}?start=2022-01-01&end=2022-01-31"
    "http://localhost:8000/maquina_ihm?start=2022-01-01&end=2022-01-31"
    """

    URL_MAQ_INFO = "http://localhost:8000/maquina_info"
    URL_MAQ_IHM = "http://localhost:8000/maquina_ihm"
    URL_MAQ_QUALIDADE = "http://localhost:8000/maquina_qualidade"
    URL_PROD = "http://localhost:8000/production"
    URL_INFO_IHM = "http://localhost:8000/info_ihm"
    URL_EFF = "http://localhost:8000/efficiency"
    URL_PERF = "http://localhost:8000/performance"
    URL_REP = "http://localhost:8000/reparo"
    URL_HIST_IND = "http://localhost:8000/historic_ind"
    URL_MASSA = "http://localhost:8000/protheus_cyv/massa"
    URL_MASSA_WEEK = "http://localhost:8000/protheus_cyv/massa_week"
    URL_PASTA = "http://localhost:8000/protheus_cyv/pasta"
    URL_PASTA_WEEK = "http://localhost:8000/protheus_cyv/pasta_week"
    URL_CAIXAS_CF = "http://localhost:8000/protheus_sd3/production"
    URL_PCP_ESTOQUE = "http://localhost:8000/protheus_sd3/pcp_estoque"
    URL_CAIXAS_ESTOQUE = "http://localhost:8000/protheus_sb2/caixas_estoque"
