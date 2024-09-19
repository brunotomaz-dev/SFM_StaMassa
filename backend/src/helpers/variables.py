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


CICLOS_ESPERADOS = 11.2
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

MASSADA_CHEIA = 153
MASSADA_REPROCESSO = 114.75
MASSADA_BOLINHA = 77
MASSADA_BOLINHA_ATUALIZADA = 118
RENDIMENTO_CHEIA = 2240
RENDIMENTO_REPROCESSO = 1680
RENDIMENTO_BOLINHA = 4000
RENDIMENTO_BOLINHA_ATUALIZADO = 5900

RENDIMENTO_PASTA_BISNAGA_5UN = 5.05
RENDIMENTO_PASTA_BISNAGA_10UN = 10.1

RENDIMENTO_PASTA_CX = {
    "PAO ALHO TRD 10B/400GR": 1.7,
    "PAO ALHO PIC 10B/400GR": 1.7,
    "PAO CEBOLA 10B/400GR": 1.8,
    "PAO ALHO TRD 10B/240GR": 1.08,
    "PAO ALHO PIC 10B/240GR": 1.08,
    "PAO ALHO SWIFT TRD 10B/400GR": 1.7,
    "PAO ALHO SWIFT PIC 10B/400GR": 1.7,
    "PAO DOCE LEITE 10B/300GR SWIFT": 1.62,
    "PAO ALHO BOL TRD 10B/300GR": 1.44,
    "PAO DOCE BOLINHA 10B/300GR": 1.44,
    "PAO CEBOLA BOL 10B/300GR": 1.44,
}

PAO_POR_BANDEJA = {
    "PAO ALHO TRD 10B/400GR": 5,
    "PAO ALHO PIC 10B/400GR": 5,
    "PAO CEBOLA 10B/400GR": 5,
    "PAO ALHO TRD 10B/240GR": 3,
    "PAO ALHO PIC 10B/240GR": 3,
    "PAO ALHO SWIFT TRD 10B/400GR": 5,
    "PAO ALHO SWIFT PIC 10B/400GR": 5,
    "PAO DOCE LEITE 10B/300GR SWIFT": 3,
    "PAO ALHO BOL TRD 10B/300GR": 12,
    "PAO DOCE BOLINHA 10B/300GR": 12,
    "PAO CEBOLA BOL 10B/300GR": 12,
}

RENDIMENTO_PASTA_PAO = {}

# Calcular o rendimento de pasta por pão
for produto, rendimento_cx in RENDIMENTO_PASTA_CX.items():
    PAO_POR_BDJ = PAO_POR_BANDEJA[produto]
    RENDIMENTO_POR_BDJ = rendimento_cx / 10  # Cada caixa tem 10 bandejas
    rendimento_pao = RENDIMENTO_POR_BDJ / PAO_POR_BDJ
    RENDIMENTO_PASTA_PAO[produto] = rendimento_pao

# Caso queira visualizar o dicionário remova os comentários abaixo
# for produto, rendimento in RENDIMENTO_PASTA_PAO.items():
#     print(f"{produto}: {rendimento:.3f} kg/pão")

