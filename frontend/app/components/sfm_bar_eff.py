"""Gráfico de barras de eficiência por linha"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# pylint: disable=import-error
from app.helpers.variables import ColorsSTM


class BarChartEff:
    """
    Classe que cria um gráfico de barras de eficiência por linha.
    """

    def __init__(self):
        self.grey_500_color = "#adb5bd"
        self.grey_600_color = "#6c757d"
        self.grey_900_color = "#212529"

    def create_bar_chart_eff(self, df: pd.DataFrame):
        """
        Cria um gráfico de barras de eficiência por linha.

        Args:
            df (pd.DataFrame): DataFrame contendo os dados para o gráfico.

        Returns:
            go.Figure: O gráfico de barras gerado.
        """

        # Ordem dos turnos
        turn_order = ["NOT", "MAT", "VES"]

        # Converter turno em categórico para ordenar
        df.turno = pd.Categorical(df.turno, categories=turn_order, ordered=True)

        # Agrupar e agregar o dataframe
        df_grouped = (
            df.groupby(["linha", "turno"], observed=True)
            .agg({"eficiencia": "mean", "total_produzido": "sum"})
            .sort_values(by=["linha", "turno"])
            .reset_index()
        )

        # Ajustar a produção de caixas
        df_grouped.total_produzido = (df_grouped.total_produzido / 10).round(0)

        # Opção do hover
        hover = {"total_produzido": True, "linha": False, "eficiencia": False}

        # Label
        label = {"eficiencia": "Eficiência"}

        # Criar o gráfico de barras
        figure = px.bar(
            df_grouped,
            x="eficiencia",
            y="linha",
            orientation="h",
            color="turno",
            barmode="group",
            hover_data=hover,
            color_discrete_map={
                "NOT": self.grey_500_color,
                "MAT": self.grey_600_color,
                "VES": self.grey_900_color,
            },
            labels=label,
        )

        # Customiza hover
        custom_hover = "<b>Produção:</b> %{customdata[0]} caixas<extra></extra>"

        # Ajustar o hover
        figure.update_traces(
            hovertemplate="<b>Linha:</b> %{y}<br>"
            "<b>Eficiência:</b> %{x:.1%}<br>"
            f"{custom_hover}"
        )

        # Ajuste do layout
        figure.update_layout(
            xaxis=dict(
                title="Eficiência",
                tickformat=".0%",
                tickfont=dict(color="gray"),
            ),
            yaxis=dict(
                title="Linha",
                tickfont=dict(color="gray"),
                autorange="reversed",
                tickvals=df_grouped.linha.unique(),
                ticksuffix=" ",
            ),
            legend=dict(title="Turno", traceorder="normal"),
            margin=dict(l=10, r=0, t=25, b=10),
            font=dict(family="Poppins"),
            plot_bgcolor="RGBA(0,0,0,0.01)",
        )

        # media de eficiencia
        media_eficiencia = df_grouped.eficiencia.mean()

        # Adicionar linha de média
        figure.add_trace(
            go.Scatter(
                x=[media_eficiencia] * len(df_grouped.linha),
                y=df_grouped.linha,
                name="Média",
                mode="lines",
                line=dict(color="gold", dash="dash"),
                hovertemplate=f"<b>Média:</b> {media_eficiencia:.1%}<extra></extra>",
            )
        )

        # Adiciona a Meta
        figure.add_trace(
            go.Scatter(
                x=[0.9] * len(df_grouped.linha),
                y=df_grouped.linha,
                name="Meta 90%",
                mode="lines",
                line=dict(color=ColorsSTM.GREEN.value, dash="dash"),
                hovertemplate="<b>Meta:</b> 90%<extra></extra>",
            )
        )

        return figure
