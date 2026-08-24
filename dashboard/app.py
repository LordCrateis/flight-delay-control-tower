"""Application shell for the Flight Delay Analytics Dashboard."""

from __future__ import annotations

import os

from dash import Dash, Input, Output, State, callback, dcc, html, page_container, page_registry
import dash_bootstrap_components as dbc

from db import filter_metadata_safe


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
                [html.Span(page.get("icon", "•"), className="nav-icon"), page["name"]],
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
                        html.Div("FD", className="brand-mark"),
                        html.Div(
                            [
                                html.Strong("FlightScope"),
                                html.Span("Analytics Console"),
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
                        html.Div(
                            [html.Span("1M", className="sample-number"), html.Span("sample rows")],
                            className="sample-badge",
                        ),
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


if __name__ == "__main__":
    app.run(debug=os.getenv("DASH_DEBUG", "false").lower() == "true", port=int(os.getenv("PORT", "8050")))
