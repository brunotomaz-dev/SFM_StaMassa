""" Módulo com as variáveis do sistema e classes auxiliares. """

from enum import Enum

# cSpell: words eficiencia, manutencao, producao


class LocalTables(Enum):
    """Local tables"""

    EFFICIENCY = "eficiencia"
    PERFORMANCE = "performance"
    REPAIR = "reparo"
    PRODUCTION = "producao"
    INFO_IHM = "info_ihm"
    HISTORIC_IND = "historic_info"


class IndicatorType(Enum):
    """
    Enum para os tipos de indicadores.
    """

    EFFICIENCY = "eficiencia"
    PERFORMANCE = "performance"
    REPAIR = "reparo"
    QUALITY = "qualidade"
    MAINTENANCE = "manutencao"


CICLOS_ESPERADOS = 10.6
TEMPO_AJUSTE = 10
PESO_BANDEJAS = 0.028
PESO_SACO = 0.080

# Dict de Descontos
DESC_EFF = {
    "Troca de Sabor": 15,
    "Troca de Produto": 35,
    "Refeição": 60,
    "Café e Ginástica Laboral": 10,
    "Treinamento": 60,
}
DESC_PERF = {
    "Troca de Sabor": 15,
    "Troca de Produto": 35,
    "Refeição": 60,
    "Café e Ginástica Laboral": 10,
    "Treinamento": 60,
}
DESC_REP = {"Troca de Produto": 35}

# List que não afeta ou afeta
NOT_EFF = ["Sem Produção", "Backup"]
NOT_PERF = [
    "Sem Produção",
    "Backup",
    "Limpeza para parada de Fábrica",
    "Risco de Contaminação",
    "Parâmetros de Qualidade",
    "Manutenção",
]
AF_REP = ["Manutenção", "Troca de Produtos"]
