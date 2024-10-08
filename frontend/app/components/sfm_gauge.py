"""Componente de gráfico de gauge."""

# pylint: disable=import-error
from app.helpers.variables import ColorsSTM, IndicatorType
from streamlit_echarts import st_echarts


def create_gauge_chart(month_opt: int, indicator: IndicatorType, data: int, key_: str) -> None:
    """
    Cria o gráfico de gauge.

    Args:
        month_opt (int): Mês de referência. 0 para mês anterior e 1 para mês atual.
        indicator (IndicatorType): Tipo de indicador.
        data (int): Dados do indicador.
        key_ (str): Chave do gráfico.
    """
    # Opt de mês
    month = {
        0: "Mês Anterior",
        1: "Mês Atual",
    }

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
            [0.9, ColorsSTM.RED.value],  # Até 90% é vermelho
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

    return st_echarts(
        options={
            "title": {"text": month[month_opt], "left": "center"},
            "tooltip": {
                "formatter": "{b} : {c}%",
                "position": "top",
                "shadowColor": "rgba(0, 0, 0, 0.5)",
                "shadowBlur": 10,
            },
            "series": [
                {
                    "name": indicator,
                    "title": {"show": False},
                    "type": "gauge",
                    "detail": {
                        "formatter": "{value}%",
                        "valueAnimation": True,
                        "fontSize": 18,
                        "color": "inherit",
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
                    "radius": "85%",
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
                    # "progress": {
                    #     "show": True,
                    #     "overlap": False,
                    #     "itemStyle": {
                    #         "color": "auto",
                    #     },
                    # },
                }
            ],
        },
        key=key_,
    )
