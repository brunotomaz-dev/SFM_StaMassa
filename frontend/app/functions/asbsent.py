""" Módulo com funções de suporte para registro de absenteísmo. """

from datetime import datetime

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
        if "absenteismo_df" not in st.session_state:
            st.session_state["absenteismo_df"] = pd.DataFrame(
                columns=["Setor", "Turno", "Nome", "Tipo", "Motivo", "Data", "Hora", "Usuario"]
            )

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

    def salvar_csv(self) -> None:
        """
        Salva o DataFrame atual em um arquivo CSV no caminho especificado.
        O arquivo CSV será salvo sem o índice.
        Raises:
            IOError: Se houver um erro ao salvar o arquivo CSV.
        """
        df = st.session_state["absenteismo_df"]
        df_file = self.ler_csv()

        if not df_file.empty:
            df = pd.concat([df_file, df], ignore_index=True)

        df.to_csv(self.__absenteismo_file, index=False)
        st.session_state["absenteismo_df"] = pd.DataFrame()

    def ler_csv(self) -> pd.DataFrame:
        """
        Lê um arquivo CSV a partir do caminho especificado e retorna um DataFrame.
        Returns:
            pd.DataFrame: DataFrame contendo os dados do arquivo CSV.
        """
        try:
            df = pd.read_csv(self.__absenteismo_file)
        except FileNotFoundError:
            return pd.DataFrame()

        return df
