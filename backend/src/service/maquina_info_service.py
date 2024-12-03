"""Módulo responsável por tratar os dados da máquina"""

from datetime import time

import numpy as np
import pandas as pd

# pylint: disable=import-error
from src.model.maquina_info_model import MaquinaInfoModel
from src.service.functions.clean_data import CleanData
from src.service.maquina_qualidade_service import MaquinaQualidadeService


class MaquinaInfoService:
    """Classe responsável por tratar os dados da máquina"""

    def __init__(self) -> None:
        self.__maquina_info = MaquinaInfoModel()
        self.__clean_data = CleanData()
        self.__maquina_qualidade = MaquinaQualidadeService()

    def get_data(self, period: tuple):
        """Método responsável por tratar os dados da máquina"""

        # Consulta os dados da máquina
        data = self.__maquina_info.get_data(period)

        if data is not None:

            # Limpa os dados de forma básica
            data = self.__clean_data.clean_data(data)

            # Faz ajustes nos dados
            data = self.__data_adjustment(data)

        return data

    def get_production_data(self, period: tuple):
        """Método responsável por tratar os dados da máquina"""

        # Consulta os dados da máquina
        data = self.__maquina_info.get_production_data(period)

        # Verifica se a consulta retornou dados
        if data is not None:

            # Limpa os dados de forma básica
            data = self.__clean_data.clean_data(data)

            # Faz ajustes nos dados
            data = self.__data_adjustment_production(data)

        return data

    def get_production_data_by_period(self, period: str):
        """Método responsável por tratar os dados da máquina"""

        # Consulta os dados da máquina
        data = self.__maquina_info.get_production_data_by_period(period)
        qual = self.__maquina_qualidade.get_data((period, period))

        # Ajusta os dados - Data de registro
        data.data_registro = pd.to_datetime(data.data_registro)
        qual.data_registro = pd.to_datetime(qual.data_registro)

        # Classificar os dados
        data = data.sort_values(by=["linha", "turno"])
        qual = qual.sort_values(by=["linha", "turno"])

        # Junta os DataFrames pela data e turno
        df = pd.merge(data, qual, on=["linha", "maquina_id", "data_registro", "turno"], how="left")

        # Preenche os dados faltantes
        df = df.fillna(0)

        # Calcula produção caso haja diferença no sensor
        mask = (df.total_ciclos - df.total_produzido_sensor) / df.total_ciclos < 0.05
        ciclos = df.total_ciclos - df.bdj_vazias - df.bdj_retrabalho
        sensor = df.total_produzido_sensor - df.bdj_retrabalho
        df["total_produzido"] = np.where(mask, sensor, ciclos)

        # Garantir que seja inteiro
        df.total_produzido = df.total_produzido.astype(int)

        # Manter apenas as colunas necessárias
        df = df[
            [
                "linha",
                "maquina_id",
                "data_registro",
                "turno",
                "total_produzido",
                "produto",
            ]
        ]

        return df

    # ==================================== Funções Auxiliares ==================================== #
    @staticmethod
    def __data_adjustment(df: pd.DataFrame):
        """Método responsável por ajustar os dados da máquina"""
        # Ajusta a nomenclatura do status
        df.status = np.where(df.status == "true", "rodando", "parada")

        # Reordenar o dataframe
        df = df.sort_values(by=["maquina_id", "data_registro", "hora_registro"])

        # Correção caso a primeira entrada seja do turno 'VES'
        mask = (df.turno == "VES") & (df.maquina_id != df.maquina_id.shift())
        df = df[~mask]

        # Ajustar caso o turno "VES" passe de 00:00, para o dia anterior 23:59
        mask = (
            (df.turno == "VES")
            & (df.hora_registro < time(0, 5, 0))
            & (df.hora_registro > time(0, 0, 0))
        )

        df.loc[mask, "data_registro"] = df.loc[mask, "data_registro"] - pd.Timedelta(days=1)
        df.loc[mask, "hora_registro"] = time(23, 59, 59)

        # Reordenar o dataframe
        df = df.sort_values(by=["linha", "data_registro", "hora_registro"])

        # Reiniciar o index
        df = df.reset_index(drop=True)

        return df

    @staticmethod
    def __data_adjustment_production(df: pd.DataFrame):
        """Método responsável por ajustar os dados da máquina"""
        # Cria uma coluna para ordenar pelos turnos
        df["turno_order"] = df.turno.map({"MAT": 2, "VES": 3, "NOT": 1})

        # Ordenar o dataframe
        df = df.sort_values(by=["linha", "data_registro", "turno_order"])

        # Remover a coluna criada
        df = df.drop(columns=["turno_order", "rn"])

        # Reiniciar o index
        df = df.reset_index(drop=True)

        return df
