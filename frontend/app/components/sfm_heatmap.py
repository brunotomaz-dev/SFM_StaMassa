"""Componente Heatmap para o dashboard SFM."""

import pandas as pd

# pylint: disable=import-error
from app.helpers.variables import ColorsSTM, IndicatorType
from streamlit_echarts import st_echarts


def create_heatmap_chart(
    data: pd.DataFrame, indicator: IndicatorType, days: list, choice: list, h_label: bool, key_: str
) -> None:
    """Cria o gráfico de heatmap."""

    is_lines = "NOT" not in choice

    max_piece = 120 if is_lines else 100

    # Peças do heatmap - Cores
    pieces = {
        IndicatorType.PERFORMANCE: [
            {"min": 0, "max": 4, "color": ColorsSTM.GREEN.value},
            {"min": 4, "max": max_piece, "color": ColorsSTM.RED.value},
        ],
        IndicatorType.REPAIR: [
            {"min": 0, "max": 4, "color": ColorsSTM.GREEN.value},
            {"min": 4, "max": max_piece, "color": ColorsSTM.RED.value},
        ],
        IndicatorType.EFFICIENCY: [
            {"min": 0, "max": 89.99, "color": ColorsSTM.RED.value},
            {"min": 90, "max": max_piece, "color": ColorsSTM.GREEN.value},
        ],
    }[indicator]

    # Meta do indicador
    meta = {
        IndicatorType.PERFORMANCE: 4,
        IndicatorType.REPAIR: 4,
        IndicatorType.EFFICIENCY: 90,
    }[indicator]

    # Indicador
    indicator: str = {
        IndicatorType.PERFORMANCE: indicator.value.capitalize(),
        IndicatorType.REPAIR: indicator.value.capitalize(),
        IndicatorType.EFFICIENCY: "Eficiência",
    }[indicator]

    return st_echarts(
        options={
            "title": {
                "text": f"{indicator} - Meta {meta}%",
                "left": "center",
            },
            "tooltip": {
                "position": "top",
                "shadowColor": "rgba(0, 0, 0, 0.5)",
                "shadowBlur": 10,
            },
            "grid": {
                "height": "83%" if is_lines else "60%",
                "top": "10%" if is_lines else "23%",
            },
            "xAxis": {"type": "category", "data": days, "splitArea": {"show": True}},
            "yAxis": {"type": "category", "data": choice, "splitArea": {"show": True}},
            "visualMap": {
                "min": 0,
                "max": 100,
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "range": [0, 100],
                "type": "piecewise",
                "pieces": pieces,
                "show": not is_lines,
            },
            "series": [
                {
                    "name": indicator,
                    "type": "heatmap",
                    "data": data,
                    "label": {"show": h_label},
                    "emphasis": {
                        "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}
                    },
                    "radius": "90%",
                }
            ],
        },
        key=key_,
    )
