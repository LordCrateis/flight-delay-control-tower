"""Shared page components and Plotly styling."""

from __future__ import annotations

from dash import dcc, html
import plotly.graph_objects as go


COLORS = {
    "background": "#0B0E14",
    "panel": "#12161F",
    "border": "#232838",
    "text": "#E6E9EF",
    "muted": "#8B93A7",
    "good": "#3DDC97",
    "warning": "#F5A623",
    "severe": "#E5484D",
    "accent": "#5EB3F5",
    "grid": "#232838",
}

GRAPH_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


def style_figure(fig: go.Figure, *, height: int = 360, y_suffix: str = "") -> go.Figure:
    fig.update_layout(
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["panel"],
        font={"family": "IBM Plex Mono, monospace", "color": COLORS["text"], "size": 11},
        margin={"l": 58, "r": 24, "t": 30, "b": 64},
        height=height,
        autosize=True,
        hoverlabel={
            "bgcolor": COLORS["panel"],
            "bordercolor": COLORS["grid"],
            "font": {"family": "IBM Plex Mono, monospace", "color": COLORS["text"]},
        },
        legend={"orientation": "h", "y": 1.08, "x": 0},
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=COLORS["grid"],
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLORS["grid"],
        zeroline=False,
        ticksuffix=y_suffix,
        automargin=True,
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
        font={
            "family": "IBM Plex Mono, monospace",
            "color": COLORS["muted"],
            "size": 12,
        },
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style_figure(fig)


def loading_figure() -> go.Figure:
    return empty_figure("Loading analytics...")


def graph(
    figure: go.Figure,
    graph_id: str | None = None,
    class_name: str = "",
    *,
    height: int = 360,
):
    figure.update_layout(height=height)
    return dcc.Graph(
        id=graph_id,
        figure=figure,
        config=GRAPH_CONFIG,
        className=f"chart {class_name}".strip(),
        style={"height": f"{height}px"},
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
            html.Span("●", className=f"kpi-status {tone}"),
            html.P(label, className="kpi-label"),
            html.P(value, className="kpi-value"),
            html.P(detail, className="kpi-detail"),
        ],
        className="kpi-card",
    )
