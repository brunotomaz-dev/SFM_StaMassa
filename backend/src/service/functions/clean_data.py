"""Este módulo é responsável por limpeza de dados."""

import pandas as pd


class CleanData:
    """Helper class for data cleaning."""

    def __init__(self) -> None:
        pass

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the basic data in the given DataFrame.

        Parameters:
        df (pd.DataFrame): The DataFrame containing the data to be cleaned.

        Returns:
        pd.DataFrame: The cleaned DataFrame.

        Steps:
        1. Remove duplicate values from the DataFrame.
        2. Remove rows with missing values in specific columns.
        3. Remove milliseconds from the 'hora_registro' column.
        4. Convert 'data_registro' and 'hora_registro' columns to the correct data types.
        5. Replace NaN values in the 'linha' column with 0 and convert it to integer.
        6. Remove rows where 'linha' is 0.

        """

        # Remove valores duplicados, caso existam
        df = df.drop_duplicates()

        # Remove as linha com valores nulos que não podem faltar
        df = df.dropna(subset=["maquina_id", "data_registro", "hora_registro"])

        # Remover os milissegundos da coluna hora_registro
        df.hora_registro = df.hora_registro.astype(str).str.split(".").str[0]

        # Garantir que as colunas de data e hora sejam do tipo correto
        df.data_registro = pd.to_datetime(df.data_registro)
        df.hora_registro = pd.to_datetime(df.hora_registro, format="%H:%M:%S").dt.time

        # Substitui os valores NaN por 0 e depois converte para inteiro
        df.linha = df.linha.fillna(0).astype(int)

        # Se existir remove a coluna recno
        if "recno" in df.columns:
            df = df.drop(columns=["recno"])

        # Remover onde a linha for 0
        df = df[df.linha != 0]

        return df
