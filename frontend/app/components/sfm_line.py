"""Criação de Gráfico de linhas"""

import pandas as pd

# pylint: disable=import-error
from app.helpers.variables import ColorsSTM, IndicatorType
from streamlit_echarts import st_echarts


def create_line_chart(df: pd.DataFrame, indicator: IndicatorType) -> None:
    """Cria um gráfico de linhas."""

    opt_mark = {
        IndicatorType.PERFORMANCE: 4,
        IndicatorType.REPAIR: 4,
        IndicatorType.EFFICIENCY: 90,
    }[indicator]

    # Ajustar valores nulos na coluna do indicador para 0
    df[indicator.value] = df[indicator.value].fillna(0)

    # Agrupar os dados por data de registro
    df = df.groupby("data_registro")[indicator.value].mean().round(2).reset_index()

    return st_echarts(
        options={
            "xAxis": {
                "type": "category",
                "data": df.data_registro.unique().tolist(),
                "show": False,
            },
            "yAxis": {
                "type": "value",
                "show": False,
                "min": 0,
                "max": 120 if indicator == IndicatorType.EFFICIENCY else 20,
            },
            "series": [
                {
                    "data": df[indicator.value].tolist(),
                    "type": "line",
                    "markLine": {
                        "data": [
                            {
                                "yAxis": opt_mark,
                                "label": {
                                    "formatter": f"Meta: {opt_mark}",
                                    "position": "end",
                                    "backgroundColor": "transparent",
                                },
                                "lineStyle": {"color": ColorsSTM.RED.value, "type": "dashed"},
                            }
                        ]
                    },
                },
            ],
            "tooltip": {
                "trigger": "axis",
                "formatter": "{b}: {c}%",
                "axisPointer": {"type": "shadow"},
                "confine": True,
            },
            "grid": {
                "top": "15%",  # Ajuste a margem superior
                "bottom": "10%",  # Ajuste a margem inferior
                "left": "10%",  # Ajuste a margem esquerda
                "right": "10%",  # Ajuste a margem direita
            },
        },
        height="100px",
    )
