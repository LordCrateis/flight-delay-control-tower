from __future__ import annotations

import dash
from dash import Input, Output, callback, html
import plotly.graph_objects as go

from db import DashboardDatabaseError, parse_filter_store, time_metrics
from pages.common import COLORS, empty_figure, error_banner, graph, loading_figure, page_header, panel, style_figure


dash.register_page(__name__, path="/time-patterns", name="Time Patterns", order=3)

layout = html.Div(
    [
        page_header(
            "TEMPORAL SIGNALS",
            "Delay builds across the operating day",
            "Scheduled hour is the cleanest pattern in the EDA: morning reliability erodes steadily toward the evening peak.",
        ),
        html.Div(id="time-status"),
        html.Div(
            [
                panel(
                    "Delay by scheduled departure hour",
                    graph(loading_figure(), "time-hourly", height=420),
                    "Average departure delay; 05:00–21:00 typically shows the strongest climb",
                    "panel-wide",
                ),
                panel("Day-of-week pattern", graph(loading_figure(), "time-weekday", height=360), "Average departure delay"),
                panel("Seasonality", graph(loading_figure(), "time-monthly", height=360), "Monthly delay and cancellation pressure"),
            ],
            className="dashboard-grid overview-grid",
        ),
    ]
)


@callback(
    Output("time-status", "children"),
    Output("time-hourly", "figure"),
    Output("time-weekday", "figure"),
    Output("time-monthly", "figure"),
    Input("global-filter-store", "data"),
)
def update_time_patterns(filter_data):
    start_date, end_date, airlines = parse_filter_store(filter_data)
    try:
        hourly, weekday, monthly = time_metrics(start_date, end_date, airlines)
    except DashboardDatabaseError as exc:
        blank = empty_figure("Connect PostgreSQL to load time-pattern analytics")
        return error_banner(str(exc)), blank, blank, blank

    if hourly.empty or weekday.empty or monthly.empty:
        blank = empty_figure("No data for the selected filters")
        return "", blank, blank, blank

    hourly_fig = go.Figure()
    hourly_fig.add_trace(go.Scatter(
        x=hourly["hour"], y=hourly["avg_delay"],
        mode="lines+markers",
        line={"color": COLORS["warning"], "width": 3},
        marker={"color": COLORS["warning"], "size": 7},
        customdata=hourly[["flights"]],
        hovertemplate="%{x:02.0f}:00<br>%{y:.1f} min delay<br>%{customdata[0]:,.0f} flights<extra></extra>",
    ))
    hourly_fig.update_layout(xaxis_title="Scheduled departure hour", yaxis_title="Average delay (minutes)")
    hourly_fig.update_xaxes(dtick=1, tickformat="02d")
    style_figure(hourly_fig, height=420)

    weekday_fig = go.Figure(go.Bar(
        x=weekday["day_name"], y=weekday["avg_delay"],
        marker_color=COLORS["accent"],
        customdata=weekday[["flights"]],
        hovertemplate="%{x}<br>%{y:.1f} min delay<br>%{customdata[0]:,.0f} flights<extra></extra>",
    ))
    weekday_fig.update_layout(xaxis_title=None, yaxis_title="Average delay (minutes)")
    style_figure(weekday_fig, height=360)

    monthly_fig = go.Figure()
    monthly_fig.add_trace(go.Bar(
        x=monthly["month_name"], y=monthly["avg_delay"],
        name="Avg delay", marker_color=COLORS["warning"],
        hovertemplate="%{x}<br>%{y:.1f} min avg delay<extra></extra>",
    ))
    monthly_fig.add_trace(go.Scatter(
        x=monthly["month_name"], y=monthly["cancellation_rate"],
        name="Cancellation %", yaxis="y2", mode="lines+markers",
        line={"color": COLORS["severe"], "width": 2},
        hovertemplate="%{x}<br>%{y:.2f}% cancelled<extra></extra>",
    ))
    monthly_fig.update_layout(
        yaxis={"title": "Delay (min)"},
        yaxis2={"title": "Cancellation %", "overlaying": "y", "side": "right", "showgrid": False},
    )
    style_figure(monthly_fig, height=360)
    return "", hourly_fig, weekday_fig, monthly_fig
