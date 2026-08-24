"""Shared page components and Plotly styling."""

from __future__ import annotations

from dash import dcc, html
import plotly.graph_objects as go


COLORS = {
    "background": "#0f1117",
    "panel": "#171b26",
    "panel_alt": "#1d2230",
    "text": "#f4f7fb",
    "muted": "#929bad",
    "accent": "#4cc9f0",
    "warning": "#ffb547",
    "grid": "rgba(146, 155, 173, 0.12)",
}

GRAPH_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


def style_figure(fig: go.Figure, *, height: int = 360, y_suffix: str = "") -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "color": COLORS["text"], "size": 12},
        margin={"l": 44, "r": 18, "t": 22, "b": 44},
        height=height,
        hoverlabel={
            "bgcolor": COLORS["panel_alt"],
            "bordercolor": COLORS["grid"],
            "font": {"family": "Inter, sans-serif", "color": COLORS["text"]},
        },
        legend={"orientation": "h", "y": 1.08, "x": 0},
        transition={"duration": 250},
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=COLORS["grid"])
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLORS["grid"],
        zeroline=False,
        ticksuffix=y_suffix,
    )
    return fig


def empty_figure(message: str = "No data for the selected filters") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"color": COLORS["muted"], "size": 14},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style_figure(fig)


def graph(figure: go.Figure, graph_id: str | None = None, class_name: str = ""):
    return dcc.Graph(
        id=graph_id,
        figure=figure,
        config=GRAPH_CONFIG,
        className=f"chart {class_name}".strip(),
    )


def page_header(eyebrow: str, title: str, description: str):
    return html.Div(
        [
            html.P(eyebrow, className="eyebrow"),
            html.H1(title),
            html.P(description, className="page-description"),
        ],
        className="page-header",
    )


def panel(title: str, child, subtitle: str | None = None, class_name: str = ""):
    heading = [html.H3(title)]
    if subtitle:
        heading.append(html.P(subtitle, className="panel-subtitle"))
    return html.Section(
        [html.Div(heading, className="panel-heading"), child],
        className=f"panel {class_name}".strip(),
    )


def error_banner(message: str):
    return html.Div(
        [html.Span("Database connection required", className="error-title"), html.Span(message)],
        className="error-banner",
    )


def kpi_card(label: str, value: str, detail: str, tone: str = "accent"):
    return html.Article(
        [
            html.Div(className=f"kpi-marker {tone}"),
            html.P(label, className="kpi-label"),
            html.P(value, className="kpi-value"),
            html.P(detail, className="kpi-detail"),
        ],
        className="kpi-card",
    )
