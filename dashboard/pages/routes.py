from __future__ import annotations

import dash
from dash import Input, Output, callback, dcc, html
import plotly.graph_objects as go

from db import DashboardDatabaseError, parse_filter_store, route_metrics
from pages.common import COLORS, empty_figure, error_banner, graph, loading_figure, page_header, panel, style_figure


dash.register_page(__name__, path="/routes", name="Routes", order=4)

layout = html.Div(
    [
        page_header(
            "CORRIDOR ANALYSIS",
            "Route volume and disruption hotspots",
            "Separate heavily travelled corridors from routes with persistent delay and cancellation exposure.",
        ),
        html.Div(
            [
                html.Div(
                    [html.Label("Minimum route volume"), dcc.Slider(
                        id="route-minimum-flights",
                        min=50, max=1000, step=50, value=200,
                        marks={50: "50", 200: "200", 500: "500", 1000: "1k"},
                        tooltip={"placement": "bottom", "always_visible": False},
                    )],
                    className="inline-filter slider-filter",
                ),
            ],
            className="page-toolbar",
        ),
        html.Div(id="route-status"),
        html.Div(
            [
                html.Div(
                    [
                        html.Span("EWR", className="callout-code"),
                        html.Div([
                            html.Strong("Recurring pressure point"),
                            html.P("Newark appears repeatedly across high-delay and high-cancellation route rankings. Amber bars identify EWR-involved corridors."),
                        ]),
                    ],
                    className="insight-callout",
                ),
                panel("Busiest routes", graph(loading_figure(), "route-busiest", height=470), "Top 15 by scheduled flight volume"),
                panel("Worst-delay routes", graph(loading_figure(), "route-delay", height=470), "Top 15 qualifying routes by departure delay"),
                panel("Highest cancellation routes", graph(loading_figure(), "route-cancel", height=470), "Top 15 qualifying routes by cancellation rate", "panel-wide"),
            ],
            className="dashboard-grid routes-grid",
        ),
    ]
)


@callback(
    Output("route-status", "children"),
    Output("route-busiest", "figure"),
    Output("route-delay", "figure"),
    Output("route-cancel", "figure"),
    Input("global-filter-store", "data"),
    Input("route-minimum-flights", "value"),
)
def update_routes(filter_data, minimum_flights):
    start_date, end_date, airlines = parse_filter_store(filter_data)
    try:
        minimum_flights = max(0, int(minimum_flights))
    except (TypeError, ValueError):
        minimum_flights = 200
    try:
        frame = route_metrics(start_date, end_date, airlines, minimum_flights)
    except DashboardDatabaseError as exc:
        blank = empty_figure("Connect PostgreSQL to load route analytics")
        return error_banner(str(exc)), blank, blank, blank

    if frame.empty:
        blank = empty_figure(
            f"No routes meet the {minimum_flights:,}-flight threshold"
        )
        return "", blank, blank, blank

    def rank(column, title, limit=15):
        ordered = frame.nlargest(limit, column).sort_values(column)
        colors = [COLORS["warning"] if flag else COLORS["accent"] for flag in ordered["involves_ewr"]]
        suffix = "%" if "rate" in column else (" min" if column == "avg_delay" else "")
        fig = go.Figure(go.Bar(
            x=ordered[column], y=ordered["route"], orientation="h",
            marker_color=colors,
            customdata=ordered[["total_flights", "involves_ewr"]],
            hovertemplate=f"%{{y}}<br>%{{x:.2f}}{suffix}<br>%{{customdata[0]:,.0f}} flights<extra></extra>",
        ))
        fig.update_layout(xaxis_title=title, yaxis_title=None)
        return style_figure(fig, height=470)

    return (
        "",
        rank("total_flights", "Scheduled flights"),
        rank("avg_delay", "Average departure delay (minutes)"),
        rank("cancellation_rate", "Cancellation rate (%)"),
    )
