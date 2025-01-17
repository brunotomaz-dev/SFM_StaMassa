""" Este módulo é responsável por realizar a junção dos dados de qualidade e produção """

import numpy as np
import pandas as pd


class ProdQualidJoin:
    """
    Essa classe é responsável por juntar os DataFrames de qualidade e produção.

    Parâmetros:
    df_quality (pd.DataFrame): DataFrame de qualidade.
    df_production (pd.DataFrame): DataFrame de produção.
    """

    def __init__(self) -> None:
        pass

    def join_data(
        self, df_quality, df_production, data_products: pd.DataFrame | None = None
    ) -> pd.DataFrame:
        """
        Junta os DataFrames de qualidade e produção.
        """
        quality_dataframe = df_quality.copy()
        production_dataframe = df_production.copy()

        # Garantir que data de registro seja datetime
        quality_dataframe.data_registro = pd.to_datetime(quality_dataframe.data_registro)
        production_dataframe.data_registro = pd.to_datetime(production_dataframe.data_registro)

        # Classifica os DataFrames
        quality_dataframe = quality_dataframe.sort_values(by="data_registro")
        production_dataframe = production_dataframe.sort_values(by="data_registro")

        # Junta os DataFrames pela data e turno
        df = pd.merge(
            production_dataframe,
            quality_dataframe,
            on=["linha", "maquina_id", "data_registro", "turno"],
            how="left",
        )

        # Se houver dados de produtos
        if data_products is not None:
            # Converter o tipo da coluna para string
            df.produto_id = df.produto_id.astype(str)
            data_products.produto_id = data_products.produto_id.astype(str)
            # Trazer a descrição do produto de data_products para o DataFrame
            df = df.merge(data_products, on="produto_id", how="left")
            # Renomear coluna descricao
            # df = df.rename(columns={"descricao": "produto"})
            # Se a coluna produto estiver vazia preenche com a descrição
            df.produto = np.where((df.produto == ""), df.descricao, df.produto)
            df.produto = df.produto.fillna(df.descricao)

        # Renomear coluna total produzido
        df = df.rename(columns={"total_produzido": "total_produzido_sensor"})

        # Preencher valores nulos
        df = df.fillna(0)

        # Calcula produção - caso haja uma diferença maior que 5% entre os valores de produção
        mask = (df.total_ciclos - df.total_produzido_sensor) / df.total_ciclos < 0.05
        ciclos = df.total_ciclos - df.bdj_vazias - df.bdj_retrabalho
        sensor = df.total_produzido_sensor - df.bdj_retrabalho
        df["total_produzido"] = np.where(mask, sensor, ciclos)

        # Ordenar os valores
        df = df.sort_values(by=["data_registro", "turno", "linha"])

        # Reordenar as colunas
        df = df[
            [
                "fabrica",
                "linha",
                "maquina_id",
                "turno",
                "produto",
                "total_ciclos",
                "total_produzido_sensor",
                "bdj_vazias",
                "bdj_retrabalho",
                "total_produzido",
                "data_registro",
                "hora_registro",
            ]
        ]

        # Definir como int
        df.total_produzido = df.total_produzido.astype(int)
        df.total_produzido_sensor = df.total_produzido_sensor.astype(int)
        df.bdj_vazias = df.bdj_vazias.astype(int)
        df.bdj_retrabalho = df.bdj_retrabalho.astype(int)

        return df
