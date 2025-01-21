"""Módulo responsável por unir as tabelas info e ihm."""

import numpy as np
import pandas as pd

# pylint: disable=E0401
from src.helpers.variables import TEMPO_AJUSTE


class InfoIHMJoin:
    """
    Essa classe é responsável por juntar os DataFrames de info e ihm.

    Parâmetros:
    df_info (pd.DataFrame): DataFrame de info.
    df_ihm (pd.DataFrame): DataFrame de ihm.
    """

    def __init__(self, df_ihm: pd.DataFrame, df_info: pd.DataFrame) -> None:
        self.df_ihm = df_ihm
        self.df_info = df_info

    def join_data(self) -> pd.DataFrame:
        """Une os DataFrames de info e ihm."""

        df_ihm = self.df_ihm
        df_info = self.df_info

        # Cria coluna com união de data e hora para df_ihm
        df_ihm["data_hora"] = pd.to_datetime(
            df_ihm.data_registro.astype(str) + " " + df_ihm.hora_registro.astype(str)
        )

        # Cria coluna com união de data e hora para df_info
        df_info["data_hora"] = pd.to_datetime(
            df_info.data_registro.astype(str) + " " + df_info.hora_registro.astype(str)
        )

        # Classifica os dataframes por data_hora
        df_ihm = df_ihm.sort_values(by="data_hora")
        df_info = df_info.sort_values(by="data_hora")

        # Realiza o merge dos dataframes
        df = pd.merge_asof(
            df_info,
            df_ihm,
            on="data_hora",
            by="maquina_id",
            direction="nearest",
            tolerance=pd.Timedelta("3 min 30 s"),
        )

        # Define o tipo para colunas de ciclos e produção
        df.contagem_total_ciclos = df.contagem_total_ciclos.astype("Int64")
        df.contagem_total_produzido = df.contagem_total_produzido.astype("Int64")

        # Reordenar as colunas, mantendo só as necessárias
        df = df[
            [
                "fabrica",
                "linha_x",
                "maquina_id",
                "turno",
                "status",
                "contagem_total_ciclos",
                "contagem_total_produzido",
                "data_registro_x",
                "hora_registro_x",
                "motivo",
                "equipamento",
                "problema",
                "causa",
                "os_numero",
                "operador_id",
                "data_registro_y",
                "hora_registro_y",
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

        # Reordenar o dataframe
        df = df.sort_values(by=["linha", "data_registro", "hora_registro"])

        # Reiniciar o index
        df = df.reset_index(drop=True)

        # ========= Ajustes Na Posição Das Paradas E Soma Dos Tempos De Parada E Rodando ========= #
        df = self.get_info_ihm_adjusted(df)

        # Se a data hora final for menor que a data hora, ajustar para data hora final para agora
        now = pd.Timestamp.now()
        df.data_hora_final = np.where(
            df.data_hora_final < df.data_hora, now.round("s"), df.data_hora_final
        )
        df.data_hora_final = pd.to_datetime(df.data_hora_final)

        return df

    # ================================== Métodos Complementares ================================== #
    @staticmethod
    def __identify_changes(df: pd.DataFrame, column: str) -> pd.Series:
        return df[column].ne(df[column].shift())

    def __status_change(self, df: pd.DataFrame) -> pd.DataFrame:
        # Checa se houve mudança de status, maquina_id e turno
        columns_to_check = ["status", "maquina_id", "turno"]
        for column in columns_to_check:
            df[f"{column}_change"] = self.__identify_changes(df, column)

        # Coluna auxiliar que identifica se houve alguma mudança
        df["change"] = df[["status_change", "maquina_id_change", "turno_change"]].any(axis=1)

        return df

    @staticmethod
    def __fill_occ(df: pd.DataFrame) -> pd.DataFrame:
        # Preenche os valores nulos de paradas
        fill_columns = [
            "motivo",
            "equipamento",
            "problema",
            "causa",
            "os_numero",
            "operador_id",
            "data_registro_ihm",
            "hora_registro_ihm",
            "s_backup",
        ]
        for col in fill_columns:
            df[col] = df.groupby("group")[col].transform(lambda x: x.ffill().bfill())
            df = df.infer_objects(copy=False)

        # Se os dado de uma coluna for '' ou ' ', substituir por NaN
        df = df.replace(r"^s*$", None, regex=True)
        # O ^ indica o início de uma string, o $ indica o fim de uma string,
        # e s* zero ou mais espaços em branco

        return df

    @staticmethod
    def __group_and_calc_time(df: pd.DataFrame) -> pd.DataFrame:
        # Agrupa as mudanças
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
                change_date=("change_date", "first"),
                motivo_change=("motivo_change", "first"),
            )
            .reset_index()
        )

        # Nova coluna com a data_hora_final do status/parada
        df["data_hora_final"] = (
            df.groupby("maquina_id")["data_hora"].shift(-1).where(~df["maquina_id_change"])
        )

        # Atualiza a hora final caso mude a máquina
        mask = df["maquina_id_change"]
        df.data_hora_final = np.where(
            mask,
            df.change_date.shift(-1),
            df.data_hora_final,
        )

        # =============== Atualização Para Hora Final No Caso De Mudança De Turno =============== #
        # Dicionário com o horário de término de cada turno
        turno_end_time = {
            "NOT": pd.to_timedelta("08:01:00"),
            "MAT": pd.to_timedelta("16:01:00"),
            "VES": pd.to_timedelta("00:01:00"),
        }

        # Nova coluna com o horário de término do turno
        df["turno_end_time"] = df.turno.map(turno_end_time)

        # Determina a data e hora atual
        now = pd.Timestamp.now()

        # Nova coluna para indicar se a data é a mesma do dia atual
        df["is_today"] = pd.to_datetime(df.data_hora).dt.date == now.date()

        # Determina o turno atual com base na hora atual
        if now.hour in range(0, 8):
            current_shift = "NOT"
        elif now.hour in range(8, 16):
            current_shift = "MAT"
        else:
            current_shift = "VES"

        # Atualiza a hora final caso haja mudança de turno e o turno não seja o turno atual
        mask = (df.turno != df.turno.shift(-1)) & ~((df["is_today"]) & (df.turno == current_shift))

        df.data_hora_final = np.where(
            mask & (df.turno == "VES"),
            (df.data_hora.dt.normalize() + pd.DateOffset(days=1)) + df.turno_end_time,
            np.where(
                mask,
                df.data_hora.dt.normalize() + df.turno_end_time,
                df.data_hora_final,
            ),
        )

        # Se a data_hora_final for nula, atualiza com a data_hora + 1 minuto
        df.data_hora_final = df.data_hora_final.fillna(df.data_hora + pd.Timedelta("1m"))

        # Remove coluna auxiliar
        df = df.drop(columns=["turno_end_time", "is_today"])

        # Caso a data_hora_final seja nula, remove a linha
        df = df.dropna(subset=["data_hora_final"]).reset_index(drop=True)

        # Calcula o tempo de cada status
        df["tempo"] = (
            pd.to_datetime(df.data_hora_final) - pd.to_datetime(df.data_hora)
        ).dt.total_seconds() / 60

        # Arredondar e converter para inteiro
        df.tempo = df.tempo.round().astype(int)

        # Se o tempo for maior que 478, e o motivo for parada programada ou limpeza ajustar para 480
        mask = (df.tempo > 478) & (df.motivo.isin(["Parada Programada", "Limpeza"]))
        df.tempo = np.where(mask, 480, df.tempo)

        return df

    def get_info_ihm_adjusted(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Retrieves adjusted information from the IHM (Interface Homem-Máquina).

        This method performs data reading, cleaning, and joining operations to retrieve adjusted
        information from the IHM.
        It identifies status changes, fills null values for stops, calculates stop or running times,
        and performs other adjustments.

        Returns:
            pd.DataFrame: The adjusted information from the IHM.
        """

        # Realiza a leitura, limpeza e junção dos dados
        df_joined = dataframe

        # ========================= Identifica Onde Há Mudança De Status ========================= #

        df_joined = self.__status_change(df_joined)

        # ========================= Preenchendo Valores Nulos De Paradas ========================= #

        # Cria um grupo para cada mudança de status
        df_joined["group"] = df_joined.change.cumsum()

        # Preenche os valores nulos de paradas
        df_joined = self.__fill_occ(df_joined)

        # Coluna auxiliar para identificar mudança na coluna motivo, se não for nula
        mask = (df_joined.motivo.ne(df_joined.motivo.shift())) | (
            df_joined.causa.ne(df_joined.causa.shift())
        )
        df_joined["motivo_change"] = mask & df_joined.motivo.notnull()

        # Atualiza o change
        df_joined.change = df_joined.change | df_joined.motivo_change

        # Refaz o grupo para considerar a mudança na coluna motivo
        df_joined.group = df_joined.change.cumsum()

        # Coluna auxiliar para unir data e hora
        df_joined["data_hora"] = pd.to_datetime(
            df_joined.data_registro.astype(str) + " " + df_joined.hora_registro.astype(str)
        )

        # Coluna auxiliar para identificar a data/hora da mudança
        df_joined["change_date"] = (
            df_joined.groupby("maquina_id")["data_hora"].shift(0).where(df_joined.change)
        )

        # =========================== Calcula O Tempo Parada Ou Rodando ========================== #

        # Calcula os tempos
        df_joined = self.__group_and_calc_time(df_joined)

        # Ajustar status para levar em conta testes
        mask = (
            (df_joined.status == "rodando")
            & (df_joined.tempo <= TEMPO_AJUSTE)
            & (df_joined.turno.eq(df_joined.turno.shift(-1)))
            & (df_joined.motivo.shift() != "Parada Programada")
        )

        df_joined.status = np.where(mask, "parada", df_joined.status)

        # Ajustando o motivo change
        df_joined.motivo_change = np.where(mask, False, df_joined.motivo_change.shift(-1))

        mask = (
            (df_joined.status == "rodando")
            & (df_joined.tempo <= TEMPO_AJUSTE)
            & (df_joined.turno.eq(df_joined.turno.shift(-1)))
        )

        df_joined.status = np.where(mask, "parada", df_joined.status)

        # Ajuste em change para refletir alterações
        df_joined = self.__status_change(df_joined)
        df_joined.change = df_joined.change | df_joined.motivo_change

        # Refaz o group
        df_joined.group = df_joined.change.cumsum()

        # Preenche os valores nulos de paradas
        df_joined = self.__fill_occ(df_joined)

        # Recalcula os tempos
        df_joined = self.__group_and_calc_time(df_joined)

        # Se o tempo for negativo, ajustar para 0
        df_joined.tempo = df_joined.tempo.clip(lower=0)

        # Se o tempo for maior que 480 minutos, ajustar para 480
        df_joined.tempo = df_joined.tempo.clip(upper=480)

        # Se o tempo for maior que 478, ajustar para 480
        mask = df_joined.tempo > 478
        df_joined.tempo = np.where(mask, 480, df_joined.tempo)

        # Se o motivo não for saída para backup, ajustar s_backup para null
        mask = df_joined.motivo != "Saída para Backup"
        df_joined.s_backup = np.where(mask, np.nan, df_joined.s_backup)

        # Remove colunas auxiliares
        df_joined = df_joined.drop(
            columns=[
                "maquina_id_change",
                "change",
                "maquina_id_change",
                "change_date",
                "motivo_change",
                "group",
            ]
        )

        # Remove dados de parada caso a máquina esteja rodando
        columns_to_adj = [
            "motivo",
            "equipamento",
            "problema",
            "causa",
            "operador_id",
            "data_registro_ihm",
            "hora_registro_ihm",
        ]
        df_joined.loc[df_joined.status == "rodando", columns_to_adj] = None

        return df_joined
