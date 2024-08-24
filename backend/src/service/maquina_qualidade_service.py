"""Módulo responsável por trabalhar com os dados da qualidade_IHM."""

import pandas as pd

# pylint: disable=import-error
from src.helpers.variables import PESO_BANDEJAS, PESO_SACO
from src.model.maquina_qualidade_model import MaquinaQualidadeModel


class MaquinaQualidadeService:
    """Classe responsável por tratar os dados da qualidade IHM."""

    def __init__(self) -> None:
        self.__maquina_qualidade = MaquinaQualidadeModel()

    def get_data(self, period: tuple) -> pd.DataFrame:
        """Método responsável por tratar os dados da qualidade IHM."""
        # Consulta os dados da qualidade IHM
        data = self.__maquina_qualidade.get_data(period)

        # Verifica se a consulta retornou dados
        if data is not None:
            # Ajusta os dados da qualidade IHM
            data = self.__maquina_qualidade_data_adjustment(data)

        return data

    # ====================================== Função Auxiliar ===================================== #
    @staticmethod
    def __maquina_qualidade_data_adjustment(df: pd.DataFrame) -> pd.DataFrame:
        """Método responsável por ajustar os dados da qualidade IHM."""

        # Descartar coluna recno
        df = df.drop(columns=["recno"])

        # Arredondar valores para float com 3 casas decimais
        df.bdj_vazias = df.bdj_vazias.round(3)
        df.bdj_retrabalho = df.bdj_retrabalho.round(3)
        df.descarte_paes_pasta = df.descarte_paes_pasta.round(3)
        df.descarte_paes = df.descarte_paes.round(3)
        df.descarte_pasta = df.descarte_pasta.round(3)

        # Calcular descarte bandejas, caso o valor seja maior que 0
        df.loc[df.bdj_vazias > 0, "bdj_vazias"] = (
            (df.bdj_vazias - PESO_SACO) / PESO_BANDEJAS
        ).round(0)
        df.loc[df.bdj_retrabalho > 0, "bdj_retrabalho"] = (
            (df.bdj_retrabalho - PESO_SACO) / PESO_BANDEJAS
        ).round(0)

        # Transforma em inteiro
        df.bdj_vazias = df.bdj_vazias.astype(int)
        df.bdj_retrabalho = df.bdj_retrabalho.astype(int)

        # Se o valor for menor que 0, transforma em 0
        df.loc[df.bdj_vazias < 0, "bdj_vazias"] = 0
        df.loc[df.bdj_retrabalho < 0, "bdj_retrabalho"] = 0

        # Definir cria coluna auxiliar com o turno (MAT, VES, NOT) muda a cada 8 horas (8, 16, 0)
        df["turno"] = df.hora_registro.apply(lambda x: x.hour) // 8
        df.turno = df.turno.map({0: "NOT", 1: "MAT", 2: "VES"})
        df = df.drop(columns=["hora_registro"])

        # Agrupar por turno e data e linha
        df = (
            df.groupby(["linha", "maquina_id", "data_registro", "turno"])
            .sum()
            .round(3)
            .reset_index()
        )

        return df
