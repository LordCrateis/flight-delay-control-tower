"""Application shell for the Flight Delay Analytics Dashboard."""

from __future__ import annotations

import os

from dash import Dash, Input, Output, State, callback, dcc, html, page_container, page_registry
import dash_bootstrap_components as dbc

from db import DashboardDatabaseError, filter_metadata_safe, overview_data, parse_filter_store


metadata, database_available = filter_metadata_safe()

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
    title="Flight Delay Analytics",
    update_title=None,
)
server = app.server


def navigation():
    links = []
    for page in sorted(page_registry.values(), key=lambda item: item.get("order", 99)):
        links.append(
            dbc.NavLink(
                page["name"],
                href=page["relative_path"],
                className="nav-link",
                active="exact",
            )
        )
    return links


app.layout = html.Div(
    [
        dcc.Store(
            id="global-filter-store",
            data={
                "start_date": metadata["min_date"],
                "end_date": metadata["max_date"],
                "airlines": [],
            },
        ),
        html.Aside(
            [
                html.Div(
                    [
                        html.Div("FIDS", className="brand-mark"),
                        html.Div(
                            [
                                html.Strong("FLIGHT OPS"),
                                html.Span("ANALYTICS DISPLAY"),
                            ],
                            className="brand-copy",
                        ),
                    ],
                    className="brand",
                ),
                html.Nav(navigation(), className="nav-list"),
                html.Div(
                    [
                        html.Span(className=f"status-dot {'online' if database_available else 'offline'}"),
                        html.Div(
                            [
                                html.Strong("PostgreSQL"),
                                html.Span("Connected" if database_available else "Configuration needed"),
                            ]
                        ),
                    ],
                    className="db-status",
                ),
            ],
            className="sidebar",
        ),
        html.Main(
            [
                html.Div(
                    [
                        html.Div(
                            [html.Span("●", className="board-dot accent"), html.Span("FLIGHTS", className="board-label"), html.Strong("—", id="board-flights", className="board-value")],
                            className="board-metric",
                        ),
                        html.Div(
                            [html.Span("●", className="board-dot good"), html.Span("ON TIME", className="board-label"), html.Strong("—", id="board-ontime", className="board-value")],
                            className="board-metric",
                        ),
                        html.Div(
                            [html.Span("●", className="board-dot warning"), html.Span("AVG DELAY", className="board-label"), html.Strong("—", id="board-delay", className="board-value")],
                            className="board-metric",
                        ),
                        html.Div(
                            [html.Span("●", className="board-dot severe"), html.Span("CANCELLED", className="board-label"), html.Strong("—", id="board-cancel", className="board-value")],
                            className="board-metric",
                        ),
                        html.Div("LIVE NETWORK SUMMARY", className="board-caption"),
                    ],
                    className="departure-strip",
                ),
                html.Header(
                    [
                        html.Div(
                            [
                                html.Label("Flight window", htmlFor="global-date-range"),
                                dcc.DatePickerRange(
                                    id="global-date-range",
                                    min_date_allowed=metadata["min_date"],
                                    max_date_allowed=metadata["max_date"],
                                    start_date=metadata["min_date"],
                                    end_date=metadata["max_date"],
                                    display_format="DD MMM YYYY",
                                    clearable=False,
                                ),
                            ],
                            className="filter-control date-control",
                        ),
                        html.Div(
                            [
                                html.Label("Airlines", htmlFor="global-airline-filter"),
                                dcc.Dropdown(
                                    id="global-airline-filter",
                                    options=[{"label": a, "value": a} for a in metadata["airlines"]],
                                    value=[],
                                    multi=True,
                                    placeholder="All airlines",
                                    className="dark-dropdown",
                                ),
                            ],
                            className="filter-control airline-control",
                        ),
                        html.Div("BTS · 2022 SAMPLE", className="dataset-label"),
                    ],
                    className="topbar",
                ),
                html.Div(page_container, className="page-container"),
            ],
            className="main-content",
        ),
    ],
    className="app-shell",
)


@callback(
    Output("global-filter-store", "data"),
    Input("global-date-range", "start_date"),
    Input("global-date-range", "end_date"),
    Input("global-airline-filter", "value"),
    State("global-filter-store", "data"),
)
def sync_global_filters(start_date, end_date, airlines, current):
    current = current or {}
    return {
        **current,
        "start_date": start_date or metadata["min_date"],
        "end_date": end_date or metadata["max_date"],
        "airlines": airlines or [],
    }


@callback(
    Output("board-flights", "children"),
    Output("board-ontime", "children"),
    Output("board-delay", "children"),
    Output("board-cancel", "children"),
    Input("global-filter-store", "data"),
)
def update_departure_strip(filter_data):
    start_date, end_date, airlines = parse_filter_store(filter_data)
    try:
        kpis, *_ = overview_data(start_date, end_date, airlines)
    except DashboardDatabaseError:
        return "—", "—", "—", "—"

    row = kpis.iloc[0]
    return (
        f"{int(row.total_flights):,}",
        f"{row.on_time_pct:.1f}%",
        f"{row.avg_arr_delay:.1f} MIN",
        f"{row.cancellation_rate:.2f}%",
    )


if __name__ == "__main__":
    app.run(debug=os.getenv("DASH_DEBUG", "false").lower() == "true", port=int(os.getenv("PORT", "8050")))
