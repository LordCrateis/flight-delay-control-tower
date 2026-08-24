from __future__ import annotations

import dash
from dash import Input, Output, callback, html
import plotly.graph_objects as go

from db import DashboardDatabaseError, overview_data, parse_filter_store
from pages.common import COLORS, empty_figure, error_banner, graph, kpi_card, page_header, panel, style_figure


dash.register_page(__name__, path="/", name="Overview", order=0, icon="⌂")

layout = html.Div(
    [
        page_header(
            "NETWORK PULSE",
            "Flight performance at a glance",
            "A fast read on reliability, disruption, and the carriers and airports driving delay.",
        ),
        html.Div(id="overview-status"),
        html.Div(id="overview-kpis", className="kpi-grid"),
        html.Div(
            [
                panel(
                    "Monthly reliability",
                    graph(empty_figure(), "overview-trend"),
                    "Average arrival delay with on-time performance",
                    "panel-wide",
                ),
                panel(
                    "Worst carriers",
                    graph(empty_figure(), "overview-airlines"),
                    "Top five by average arrival delay",
                ),
                panel(
                    "Problem origins",
                    graph(empty_figure(), "overview-airports"),
                    "Top five by average departure delay",
                ),
            ],
            className="dashboard-grid overview-grid",
        ),
    ]
)


@callback(
    Output("overview-status", "children"),
    Output("overview-kpis", "children"),
    Output("overview-trend", "figure"),
    Output("overview-airlines", "figure"),
    Output("overview-airports", "figure"),
    Input("global-filter-store", "data"),
)
def update_overview(filter_data):
    start_date, end_date, airlines = parse_filter_store(filter_data)
    try:
        kpis, trend, carriers, airports = overview_data(start_date, end_date, airlines)
    except DashboardDatabaseError as exc:
        cards = [
            kpi_card("Total flights", "—", "Waiting for database"),
            kpi_card("On-time", "—", "Arrival within 15 min"),
            kpi_card("Avg delay", "—", "Arrival minutes", "warning"),
            kpi_card("Cancelled", "—", "Share of scheduled flights", "warning"),
        ]
        blank = empty_figure("Connect PostgreSQL to load analytics")
        return error_banner(str(exc)), cards, blank, blank, blank

    row = kpis.iloc[0]
    cards = [
        kpi_card("Total flights", f"{int(row.total_flights):,}", f"{start_date} → {end_date}"),
        kpi_card("On-time", f"{row.on_time_pct:.1f}%", "Arrival within 15 minutes"),
        kpi_card("Avg arrival delay", f"{row.avg_arr_delay:.1f} min", "Completed flights", "warning"),
        kpi_card("Cancellation rate", f"{row.cancellation_rate:.2f}%", "All scheduled flights", "warning"),
    ]

    trend_fig = go.Figure()
    trend_fig.add_trace(go.Scatter(
        x=trend["month"], y=trend["avg_arr_delay"],
        name="Avg delay", mode="lines+markers",
        line={"color": COLORS["warning"], "width": 3},
        marker={"size": 7},
        hovertemplate="%{x|%b %Y}<br>%{y:.1f} min avg delay<extra></extra>",
    ))
    trend_fig.add_trace(go.Scatter(
        x=trend["month"], y=trend["on_time_pct"],
        name="On-time %", mode="lines+markers", yaxis="y2",
        line={"color": COLORS["accent"], "width": 2},
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}% on-time<extra></extra>",
    ))
    trend_fig.update_layout(
        yaxis={"title": "Delay (min)"},
        yaxis2={"title": "On-time %", "overlaying": "y", "side": "right", "showgrid": False},
        hovermode="x unified",
    )
    style_figure(trend_fig, height=370)

    def ranking_figure(frame):
        ordered = frame.sort_values("avg_delay", ascending=True)
        fig = go.Figure(go.Bar(
            x=ordered["avg_delay"], y=ordered["label"], orientation="h",
            marker_color=COLORS["warning"],
            customdata=ordered[["flights"]],
            hovertemplate="%{y}<br>%{x:.1f} min<br>%{customdata[0]:,.0f} flights<extra></extra>",
        ))
        fig.update_layout(xaxis_title="Average delay (minutes)", yaxis_title=None)
        return style_figure(fig, height=330)

    return "", cards, trend_fig, ranking_figure(carriers), ranking_figure(airports)
