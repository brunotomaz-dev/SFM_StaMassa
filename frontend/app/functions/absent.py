""" Módulo com funções de suporte para registro de absenteísmo. """

from datetime import datetime
from typing import Literal

import pandas as pd
import streamlit as st


# cspell: words absenteismo
class RegistroAbsenteismo:
    """
    Classe para gerenciar registros de absenteísmo.
    Métodos
    -------
    __init__():
        Inicializa a classe com um DataFrame vazio e define o caminho do arquivo CSV.
    adicionar_registro(setor, turno, nome, tipo, motivo):
        Adiciona um novo registro de absenteísmo ao DataFrame.
    salvar_csv():
        Salva o DataFrame atual em um arquivo CSV.
    ler_csv():
        Lê os dados de um arquivo CSV e retorna um DataFrame.
    """

    def __init__(self):
        self.__absenteismo_file = "./assets/absenteismo.csv"
        self.__registro_presenca_file = "./assets/registro_presenca.csv"
        if "absenteismo_df" not in st.session_state:
            st.session_state["absenteismo_df"] = pd.DataFrame(
                columns=["Setor", "Turno", "Nome", "Tipo", "Motivo", "Data", "Hora", "Usuario"]
            )

    def registrar_presenca(self, d: dict) -> pd.DataFrame:
        """
        Registra presença em uma seção.

        Args:
            d (dict): Dicionário com as seguintes chaves:
                - Panificação (bool): Seção Panificação.
                - Forno (bool): Seção Forno.
                - Pasta (bool): Seção Pasta.
                - Recheio (bool): Seção Recheio.
                - Embalagem (bool): Seção Embalagem.
                - Pães Diversos (bool): Seção Pães Diversos.
                - Turno (str): Turno da presença.
                - Usuario (str): Usuário que registrou a presença.

        Returns:
            pd.DataFrame: DataFrame com os dados registrados.
        """
        data_atual = datetime.now()
        data = data_atual.strftime("%Y-%m-%d")
        hora = data_atual.strftime("%H:%M:%S")

        new_data = pd.DataFrame(
            [
                {
                    "Panificação": d["Panificação"],
                    "Forno": d["Forno"],
                    "Pasta": d["Pasta"],
                    "Recheio": d["Recheio"],
                    "Embalagem": d["Embalagem"],
                    "Pães Diversos": d["Pães Diversos"],
                    "Data": data,
                    "Hora": hora,
                    "Turno": d["Turno"],
                    "Usuario": d["Usuario"],
                }
            ]
        )

        presentes = st.session_state["df_reg_pres"]
        df = pd.concat([presentes, new_data], ignore_index=True)
        st.session_state["df_reg_pres"] = df

        return df

    def adicionar_registro(self, setor, turno, nome, tipo, motivo, user) -> pd.DataFrame:
        """
        Adiciona um novo registro ao DataFrame filtrado pelo setor e turno atuais.
        Args:
            setor (str): O setor onde o registro será adicionado.
            turno (str): O turno onde o registro será adicionado.
            nome (str): O nome da pessoa a ser registrada.
            tipo (str): O tipo de registro (por exemplo, presença, ausência).
            motivo (str): O motivo do registro.
        Returns:
            pandas.DataFrame: O DataFrame atualizado com o novo registro adicionado.
        """
        turn = {
            "Matutino": "MAT",
            "Vespertino": "VES",
            "Noturno": "NOT",
        }[turno]

        data_atual = datetime.now()
        data = data_atual.strftime("%Y-%m-%d")
        hora = data_atual.strftime("%H:%M:%S")

        novo_registro = pd.DataFrame(
            [
                {
                    "Setor": setor,
                    "Turno": turn,
                    "Nome": nome,
                    "Tipo": tipo,
                    "Motivo": motivo,
                    "Data": data,
                    "Hora": hora,
                    "Usuario": user,
                }
            ]
        )
        abs_df = st.session_state["absenteismo_df"]
        df = pd.concat([abs_df, novo_registro], ignore_index=True)
        st.session_state["absenteismo_df"] = df

        return df

    def salvar_csv(self, path: Literal["Absent", "Presence"]) -> None:
        """
        Salva o DataFrame atual em um arquivo CSV no caminho especificado.
        O arquivo CSV será salvo sem o índice.
        Raises:
            IOError: Se houver um erro ao salvar o arquivo CSV.
        """
        file_path = {
            "Absent": self.__absenteismo_file,
            "Presence": self.__registro_presenca_file,
        }[path]

        df = (
            st.session_state["absenteismo_df"]
            if path == "Absent"
            else st.session_state["df_reg_pres"]
        )
        df_file = self.ler_csv(path)

        if not df_file.empty:
            df = pd.concat([df_file, df], ignore_index=True)

        df.to_csv(file_path, index=False)
        if path == "Absent":
            st.session_state["absenteismo_df"] = pd.DataFrame()
        else:
            st.session_state["df_reg_pres"] = pd.DataFrame()

    def ler_csv(self, path: Literal["Absent", "Presence"]) -> pd.DataFrame:
        """
        Lê um arquivo CSV a partir do caminho especificado e retorna um DataFrame.
        Returns:
            pd.DataFrame: DataFrame contendo os dados do arquivo CSV.
        """
        try:
            file_path = {
                "Absent": self.__absenteismo_file,
                "Presence": self.__registro_presenca_file,
            }[path]
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            return pd.DataFrame()

        return df
