"""Componente de gráfico de gauge."""

# pylint: disable=import-error
from app.helpers.variables import ColorsSTM, IndicatorType
from streamlit_echarts import st_echarts


def create_gauge_chart(
    indicator: IndicatorType, data: int, key_: str, large: bool = False, pos: str = "up_center"
) -> None:
    """
    Cria o gráfico de gauge.

    Args:
        indicator (IndicatorType): Tipo de indicador.
        data (int): Dados do indicador.
        key_ (str): Chave do gráfico.
        large (bool, optional): Tamanho do gráfico. Defaults to False.
    """
    opt_color = {
        IndicatorType.PERFORMANCE: [
            [0.1, ColorsSTM.GREEN.value],  # 4% e abaixo é verde
            [1, ColorsSTM.RED.value],  # Acima de 4% é vermelho
        ],
        IndicatorType.REPAIR: [
            [0.1, ColorsSTM.GREEN.value],  # 4% e abaixo é verde
            [1, ColorsSTM.RED.value],  # Acima de 4% é vermelho
        ],
        IndicatorType.EFFICIENCY: [
            [0.899, ColorsSTM.RED.value],  # Até 90% é vermelho
            [1, ColorsSTM.GREEN.value],  # Acima de 90% é verde
        ],
    }[indicator]

    opt_range_min = {
        IndicatorType.PERFORMANCE: 0,
        IndicatorType.REPAIR: 0,
        IndicatorType.EFFICIENCY: 0,
    }[indicator]

    opt_range_max = {
        IndicatorType.PERFORMANCE: 40,
        IndicatorType.REPAIR: 40,
        IndicatorType.EFFICIENCY: 100,
    }[indicator]

    # Indicador
    indicator: str = {
        IndicatorType.PERFORMANCE: indicator.value.capitalize(),
        IndicatorType.REPAIR: indicator.value.capitalize(),
        IndicatorType.EFFICIENCY: "Eficiência",
    }[indicator]

    # Ajuste de posição do gauge
    position_y: str = {
        "top": "35%",
        "up_center": "45%",
        "center": "50%",
        "down_center": "55%",
        "bottom": "65%",
    }[pos]

    return st_echarts(
        height="300px",
        options={
            "tooltip": {
                "formatter": "{b} : {c}%",
                "position": "top",
                "shadowColor": "rgba(0, 0, 0, 0.5)",
                "shadowBlur": 10,
            },
            # "backgroundColor": "#fff",
            "series": [
                {
                    "name": indicator,
                    "title": {
                        "show": True,
                        "offsetCenter": [0, "100%" if large else "110%"],
                        "color": "auto",
                        "textStyle": {
                            "fontSize": 24 if large else 14,
                            "fontWeight": "bold",
                            "fontFamily": "Cursive",
                        },
                    },
                    "type": "gauge",
                    "radius": "90%",
                    "center": ["50%", position_y],
                    "detail": {
                        "formatter": "{value}%",
                        "valueAnimation": True,
                        "fontSize": 26 if large else 18,
                        "color": "inherit",
                        "offsetCenter": [0, "60%"] if large else [0, "78%"],
                    },
                    "pointer": {"itemStyle": {"color": "auto"}, "width": 4},
                    "data": [
                        {
                            "value": data,
                            "name": indicator,
                        }
                    ],
                    "startAngle": 220,
                    "endAngle": -40,
                    "min": opt_range_min,
                    "max": opt_range_max,
                    "axisLine": {
                        "lineStyle": {
                            "width": 15,
                            "color": opt_color,
                            "shadowColor": "rgba(0, 0, 0, 0.5)",
                            "shadowBlur": 10,
                        }
                    },
                    "axisTick": {
                        "length": 4,
                        "distance": -15,
                        "lineStyle": {"color": "#fff", "width": 2},
                    },
                    "splitNumber": 4,
                    "splitLine": {
                        "distance": -15,
                        "width": 2,
                        "length": 15,
                        "lineStyle": {"color": "#fff", "width": 2},
                    },
                    "axisLabel": {"distance": -15, "color": "inherit", "fontSize": 8},
                }
            ],
        },
        key=key_,
    )
