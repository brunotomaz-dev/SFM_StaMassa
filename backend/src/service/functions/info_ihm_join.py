"""Módulo responsável por unir as tabelas info e ihm."""

import numpy as np
import pandas as pd


class InfoIHMJoin:
    """Classe responsável por unir as tabelas info e ihm.

    Args:
        df_ihm (pd.DataFrame): DataFrame contendo os dados da IHM.
        df_info (pd.DataFrame): DataFrame contendo os dados de informações.
    """

    def __init__(self, df_ihm: pd.DataFrame, df_info: pd.DataFrame) -> None:
        self.df_ihm = df_ihm
        self.df_info = df_info

    def __df_join(self) -> pd.DataFrame:
        """Une os DataFrames de info e ihm."""
        # Define os DataFrames
        df_ihm = self.df_ihm.copy()
        df_info = self.df_info.copy()

        # Ajustar os dados - Data de registro
        df_ihm.data_registro = pd.to_datetime(df_ihm.data_registro)
        df_info.data_registro = pd.to_datetime(df_info.data_registro)

        # Ajustar os dados - Hora de registro
        df_ihm.hora_registro = pd.to_datetime(df_ihm.hora_registro, format="%H:%M:%S").dt.time
        df_info.hora_registro = pd.to_datetime(df_info.hora_registro, format="%H:%M:%S").dt.time

        # Criar dados - Coluna de Data e Hora de registro
        df_ihm["data_hora"] = pd.to_datetime(
            df_ihm.data_registro.astype(str) + " " + df_ihm.hora_registro.astype(str)
        )
        df_info["data_hora"] = pd.to_datetime(
            df_info.data_registro.astype(str) + " " + df_info.hora_registro.astype(str)
        )

        # Classificar os dados - Data e Hora de registro
        df_ihm = df_ihm.sort_values(by="data_hora")
        df_info = df_info.sort_values(by="data_hora")

        # Juntar os DataFrames
        df = pd.merge_asof(
            df_info,
            df_ihm,
            on="data_hora",
            by="maquina_id",
            direction="nearest",
            tolerance=pd.Timedelta("2m"),
        )

        return df

    @staticmethod
    def __identify_changes(df: pd.DataFrame, col: list[str]) -> pd.Series:
        return df[col].ne(df[col].shift())

    def __status_change(self, df: pd.DataFrame) -> pd.DataFrame:

        # Verificação de mudança - status, maquina_id e turno
        columns = ["status", "maquina_id", "turno"]
        for col in columns:
            df[f"{col}_change"] = self.__identify_changes(df, col)

        # Criar coluna de mudança
        df["change"] = df[[f"{col}_change" for col in columns]].any(axis=1)

        # Criar grupo de mudança
        df["group"] = df.change.cumsum()

        return df

    @staticmethod
    def __fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:

        # Colunas de interesse
        fill_cols = [
            "motivo",
            "equipamento",
            "problema",
            "causa",
            "os_numero",
            "operador_id",
            "s_backup",
            "data_registro_ihm",
            "hora_registro_ihm",
        ]

        # Preencher os valores
        df[fill_cols] = df.groupby("group")[fill_cols].ffill().bfill()

        # Se os dado de uma coluna for '' ou ' ', substituir por NaN
        df = df.replace(r"^s*$", None, regex=True)
        # O ^ indica o início de uma string, o $ indica o fim de uma string,
        # e s* zero ou mais espaços em branco

        # Ajuste de valores - caso maquina esteja rodando, não há motivo de parada
        mask = df.status == "rodando"
        df.loc[mask, fill_cols] = None

        return df

    @staticmethod
    def __handle_reason_changes(df):

        # Máscara de mudança
        mask = (df.motivo.ne(df.motivo.shift()) & df.motivo.notnull()) | (
            df.causa.ne(df.causa.shift()) & df.causa.notnull()
        )

        # Criar coluna de mudança
        df["motivo_change"] = mask

        # Atualiza o change
        df.change = df.change | df.motivo_change

        # Atualiza o group
        df["group"] = df.change.cumsum()

        return df

    @staticmethod
    def __calculate_time_difference(df):

        # Cria coluna para data e hora de registro
        df["data_hora"] = pd.to_datetime(
            df.data_registro.astype(str) + " " + df.hora_registro.astype(str)
        )

        # Agrupa por grupo e calcula a diferença de tempo
        df = (
            df.groupby(["group"])
            .agg(
                fabrica=("fabrica", "first"),
                linha=("linha", "first"),
                maquina_id=("maquina_id", "first"),
                turno=("turno", "first"),
                status=("status", "first"),
                data_registro=("data_registro", "first"),
                hora_registro=("hora_registro", "first"),
                motivo=("motivo", "first"),
                equipamento=("equipamento", "first"),
                problema=("problema", "first"),
                causa=("causa", "first"),
                os_numero=("os_numero", "first"),
                operador_id=("operador_id", "first"),
                data_registro_ihm=("data_registro_ihm", "first"),
                hora_registro_ihm=("hora_registro_ihm", "first"),
                s_backup=("s_backup", "first"),
                data_hora=("data_hora", "first"),
                change=("change", "first"),
                maquina_id_change=("maquina_id_change", "first"),
                motivo_change=("motivo_change", "first"),
            )
            .reset_index()
        )

        # Coluna com a data e hora 'final'
        df["data_hora_final"] = df.data_hora.shift(-1).where((~df.maquina_id_change).shift(-1))

        # Se a data hora final for nula (último registro), preencher com a data e hora atual
        now = pd.to_datetime("now").floor("s")
        df.data_hora_final = df.data_hora_final.fillna(now)

        # Calcula a diferença de tempo entre data e hora final e inicial
        df["tempo"] = (
            ((df.data_hora_final - df.data_hora).dt.total_seconds() / 60).round().astype(int)
        )

        # Ajustar máximo e mínimo 0, 480
        df.tempo = df.tempo.clip(0, 480)

        # Ajustar caso tempo seja 478
        mask = df.tempo == 478
        df.loc[mask, "tempo"] = 480

        return df

    # ============================================================================================ #
    #                                       MÉTODO PRINCIPAL                                       #
    # ============================================================================================ #
    def join_data(self) -> pd.DataFrame:
        """Método principal para unir e limpar os dados."""

        # ================================================================================== União #
        # Juntar os DataFrames
        df = self.__df_join()

        # Ajustar Tipo - Ciclos e Produção
        df.contagem_total_ciclos = df.contagem_total_ciclos.astype("Int64")
        df.contagem_total_produzido = df.contagem_total_produzido.astype("Int64")

        # Reordenar as colunas
        df = df[
            [
                "fabrica",
                "linha_x",
                "maquina_id",
                "turno",
                "contagem_total_ciclos",
                "contagem_total_produzido",
                "data_registro_x",
                "hora_registro_x",
                "status",
                "data_registro_y",
                "hora_registro_y",
                "motivo",
                "equipamento",
                "problema",
                "causa",
                "os_numero",
                "operador_id",
                "s_backup",
            ]
        ]

        # Renomear as colunas
        df = df.rename(
            columns={
                "linha_x": "linha",
                "data_registro_x": "data_registro",
                "hora_registro_x": "hora_registro",
                "data_registro_y": "data_registro_ihm",
                "hora_registro_y": "hora_registro_ihm",
            }
        )

        # Reordenar
        df = df.sort_values(by=["linha", "data_registro", "hora_registro"])

        # Reiniciar o index
        df = df.reset_index(drop=True)

        # =============================================================================== Mudança #
        # Verificar mudança de status
        df = self.__status_change(df)

        # ====================================================== Preenchimento De Valores Ausentes #
        # Preencher os valores
        df = self.__fill_missing_values(df)

        # Verificar mudança de motivo
        df = self.__handle_reason_changes(df)

        # ======================================================================== Calcula O Tempo #
        df = self.__calculate_time_difference(df)

        # ========================================================================= Ajustes Finais #
        df = df.drop(
            columns=[
                "maquina_id_change",
                "change",
                "maquina_id_change",
                "motivo_change",
                "group",
            ]
        )

        # Ajuste Saída Backup
        mask = df.motivo == "Saída para Backup"

        df.s_backup = df.s_backup.where(mask)
        df.problema = np.where(mask, "Parada Planejada", df.problema)
        df.causa = np.where(mask, "Backup", df.causa)

        return df
