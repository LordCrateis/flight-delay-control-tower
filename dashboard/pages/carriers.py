from __future__ import annotations

import calendar

import dash
from dash import Input, Output, callback, ctx, dcc, html
import plotly.graph_objects as go

from db import DashboardDatabaseError, carrier_metrics, parse_filter_store
from pages.common import COLORS, empty_figure, error_banner, graph, page_header, panel, style_figure


dash.register_page(__name__, path="/carriers", name="Carriers", order=1, icon="✈")

layout = html.Div(
    [
        page_header(
            "CARRIER SCORECARD",
            "Who delivers the most reliable operation?",
            "Compare delay, cancellation, and on-time performance. Click a delay bar to cross-filter the supporting charts.",
        ),
        html.Div(
            [
                html.Div(
                    [html.Label("Month"), dcc.Dropdown(
                        id="carrier-month-filter",
                        options=[{"label": "All months", "value": 0}] + [
                            {"label": calendar.month_name[i], "value": i} for i in range(1, 13)
                        ],
                        value=0,
                        clearable=False,
                        className="dark-dropdown compact-dropdown",
                    )],
                    className="inline-filter",
                ),
                html.Button("Clear carrier focus", id="carrier-clear-focus", className="ghost-button", n_clicks=0),
                html.Div(id="carrier-focus-label", className="selection-label"),
            ],
            className="page-toolbar",
        ),
        dcc.Store(id="carrier-focus-store"),
        html.Div(id="carrier-status"),
        html.Div(
            [
                panel("Average arrival delay", graph(empty_figure(), "carrier-delay"), "Click a carrier to focus the charts below", "panel-wide"),
                panel("Cancellation rate", graph(empty_figure(), "carrier-cancel"), "Cancelled flights as a share of schedules"),
                panel("On-time performance", graph(empty_figure(), "carrier-ontime"), "Arrival no more than 15 minutes late"),
            ],
            className="dashboard-grid overview-grid",
        ),
    ]
)


@callback(
    Output("carrier-focus-store", "data"),
    Input("carrier-delay", "clickData"),
    Input("carrier-clear-focus", "n_clicks"),
    prevent_initial_call=True,
)
def set_carrier_focus(click_data, _clear_clicks):
    if ctx.triggered_id == "carrier-clear-focus":
        return None
    if click_data and click_data.get("points"):
        return click_data["points"][0].get("y")
    return None


@callback(
    Output("carrier-status", "children"),
    Output("carrier-delay", "figure"),
    Output("carrier-cancel", "figure"),
    Output("carrier-ontime", "figure"),
    Output("carrier-focus-label", "children"),
    Input("global-filter-store", "data"),
    Input("carrier-month-filter", "value"),
    Input("carrier-focus-store", "data"),
)
def update_carriers(filter_data, month, focused_airline):
    start_date, end_date, airlines = parse_filter_store(filter_data)
    try:
        frame = carrier_metrics(start_date, end_date, airlines, int(month) or None)
    except DashboardDatabaseError as exc:
        blank = empty_figure("Connect PostgreSQL to load carrier analytics")
        return error_banner(str(exc)), blank, blank, blank, ""

    if frame.empty:
        blank = empty_figure()
        return "", blank, blank, blank, "No carriers match the current filters"

    delay_ordered = frame.sort_values("avg_delay", ascending=True)
    colors = [
        COLORS["accent"] if focused_airline and airline == focused_airline else COLORS["warning"]
        for airline in delay_ordered["airline"]
    ]
    delay_fig = go.Figure(go.Bar(
        x=delay_ordered["avg_delay"], y=delay_ordered["airline"], orientation="h",
        marker_color=colors,
        customdata=delay_ordered[["total_flights"]],
        hovertemplate="%{y}<br>%{x:.1f} min delay<br>%{customdata[0]:,.0f} flights<extra></extra>",
    ))
    delay_fig.update_layout(xaxis_title="Average arrival delay (minutes)", yaxis_title=None)
    style_figure(delay_fig, height=max(420, 31 * len(frame)))

    support = frame[frame["airline"] == focused_airline] if focused_airline else frame

    def metric_bar(column, color, suffix):
        ordered = support.sort_values(column, ascending=True)
        fig = go.Figure(go.Bar(
            x=ordered[column], y=ordered["airline"], orientation="h",
            marker_color=color,
            hovertemplate=f"%{{y}}<br>%{{x:.2f}}{suffix}<extra></extra>",
        ))
        fig.update_layout(xaxis_title=suffix.strip(), yaxis_title=None)
        return style_figure(fig, height=max(320, 31 * len(ordered)), y_suffix="")

    label = f"Focused carrier: {focused_airline}" if focused_airline else "Showing all carriers"
    return (
        "",
        delay_fig,
        metric_bar("cancellation_rate", COLORS["warning"], "%"),
        metric_bar("on_time_pct", COLORS["accent"], "%"),
        label,
    )
