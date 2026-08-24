from __future__ import annotations

import dash
from dash import Input, Output, callback, dash_table, dcc, html
import plotly.graph_objects as go

from db import DashboardDatabaseError, airport_metrics, parse_filter_store
from pages.common import COLORS, empty_figure, error_banner, graph, loading_figure, page_header, panel, style_figure


dash.register_page(__name__, path="/airports", name="Airports", order=2)

layout = html.Div(
    [
        page_header(
            "AIRPORT PRESSURE",
            "Where does delay accumulate?",
            "Rank origin or destination performance and separate high-volume operational problems from small-station noise.",
        ),
        html.Div(
            [
                html.Div(
                    [html.Label("Airport role"), dcc.RadioItems(
                        id="airport-role",
                        options=[
                            {"label": "Origin", "value": "origin"},
                            {"label": "Destination", "value": "destination"},
                        ],
                        value="origin",
                        inline=True,
                        className="segmented-control",
                    )],
                    className="inline-filter",
                ),
                html.Div(
                    [html.Label("Minimum flight volume"), dcc.Slider(
                        id="airport-minimum-flights",
                        min=100, max=2000, step=100, value=500,
                        marks={100: "100", 500: "500", 1000: "1k", 2000: "2k"},
                        tooltip={"placement": "bottom", "always_visible": False},
                    )],
                    className="inline-filter slider-filter",
                ),
            ],
            className="page-toolbar",
        ),
        html.Div(id="airport-status"),
        html.Div(
            [
                panel("Worst average delay", graph(loading_figure(), "airport-delay", height=500), "Top 20 qualifying airports"),
                panel("Highest cancellation rate", graph(loading_figure(), "airport-cancel", height=500), "Top 20 qualifying airports"),
                panel(
                    "Sortable airport table",
                    dash_table.DataTable(
                        id="airport-table",
                        sort_action="native",
                        filter_action="native",
                        page_action="native",
                        page_size=15,
                        style_table={"overflowX": "auto"},
                        style_header={"backgroundColor": COLORS["panel"], "color": COLORS["text"], "fontWeight": 600, "border": f"1px solid {COLORS['border']}", "fontFamily": "Space Grotesk, sans-serif"},
                        style_cell={"backgroundColor": COLORS["panel"], "color": COLORS["text"], "border": "none", "borderBottom": f"1px solid {COLORS['border']}", "padding": "12px", "fontFamily": "IBM Plex Mono, monospace"},
                        style_filter={"backgroundColor": COLORS["background"], "color": COLORS["text"], "border": "none"},
                    ),
                    "Use the built-in filters to find a specific airport",
                    "panel-wide",
                ),
            ],
            className="dashboard-grid overview-grid",
        ),
    ]
)


@callback(
    Output("airport-status", "children"),
    Output("airport-delay", "figure"),
    Output("airport-cancel", "figure"),
    Output("airport-table", "data"),
    Output("airport-table", "columns"),
    Input("global-filter-store", "data"),
    Input("airport-role", "value"),
    Input("airport-minimum-flights", "value"),
)
def update_airports(filter_data, role, minimum_flights):
    start_date, end_date, airlines = parse_filter_store(filter_data)
    role = role if role in {"origin", "destination"} else "origin"
    try:
        minimum_flights = max(0, int(minimum_flights))
    except (TypeError, ValueError):
        minimum_flights = 500
    try:
        frame = airport_metrics(start_date, end_date, airlines, role, minimum_flights)
    except DashboardDatabaseError as exc:
        blank = empty_figure("Connect PostgreSQL to load airport analytics")
        return error_banner(str(exc)), blank, blank, [], []

    if frame.empty:
        blank = empty_figure(
            f"No airports meet the {minimum_flights:,}-flight threshold"
        )
        return "", blank, blank, [], []

    def rank(column, color, title):
        top = frame.nlargest(20, column).sort_values(column)
        fig = go.Figure(go.Bar(
            x=top[column], y=top["airport"], orientation="h",
            marker_color=color,
            customdata=top[["total_flights"]],
            hovertemplate="%{y}<br>%{x:.2f}" + ("%" if "rate" in column else " min") + "<br>%{customdata[0]:,.0f} flights<extra></extra>",
        ))
        fig.update_layout(xaxis_title=title, yaxis_title=None)
        return style_figure(fig, height=500)

    table = frame.copy()
    for column in ["avg_delay", "cancellation_rate", "on_time_pct"]:
        table[column] = table[column].round(2)
    columns = [
        {"name": "Airport", "id": "airport"},
        {"name": "Flights", "id": "total_flights", "type": "numeric"},
        {"name": "Avg delay (min)", "id": "avg_delay", "type": "numeric"},
        {"name": "Cancellation %", "id": "cancellation_rate", "type": "numeric"},
        {"name": "On-time %", "id": "on_time_pct", "type": "numeric"},
    ]
    return (
        "",
        rank("avg_delay", COLORS["warning"], "Average delay (minutes)"),
        rank("cancellation_rate", COLORS["severe"], "Cancellation rate (%)"),
        table.to_dict("records"),
        columns,
    )
