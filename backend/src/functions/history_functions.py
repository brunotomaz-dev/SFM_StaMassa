"""Modulo com funções de histórico"""

import numpy as np
import pandas as pd


def create_hist_ind(
    info: pd.DataFrame,
    prod: pd.DataFrame,
    eff: pd.DataFrame,
    perf: pd.DataFrame,
    repair: pd.DataFrame,
) -> pd.DataFrame:
    """
    Função para criar o histórico de indicadores.

    Returns:
        df_history (pd.DataFrame): DataFrame com os dados do histórico.
    """
    # Data de registro
    data_registro = prod.data_registro.iloc[0].strftime("%Y-%m")

    # Total de caixas produzidas
    total_caixas = int(np.floor((prod.total_produzido.sum()) / 10))

    # Eficiência
    eff_media = round(eff.eficiencia.mean(), 3)

    # Performance
    perf_media = round(perf.performance.mean(), 3)

    # Reparos
    repair_media = round(repair.reparo.mean(), 3)

    # Parada Programada
    df_info_programada = info[info.causa.isin(["Sem Produção", "Backup"])]
    parada_programada = df_info_programada.tempo.sum()

    # Criação do DataFrame
    df_history = pd.DataFrame(
        {
            "data_registro": [data_registro],
            "total_caixas": [total_caixas],
            "eficiencia": [eff_media],
            "performance": [perf_media],
            "reparo": [repair_media],
            "parada_programada": [parada_programada],
        }
    )

    return df_history
