import os
import pathlib
import re
import random

import dash
from dash import html
from dash import dcc
import pandas as pd
import cufflinks as cf

from right_side_plots import initilize_right_side_functionality
from left_side_plots import initialize_left_side_functionality

r = lambda: random.randint(0, 255)

# Initialize app
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# Some settings
app.title = "Insurance data exploration"
server = app.server

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_lat_lon = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("data", "lat_lon_counties_uk.csv"))
)

df_full_data = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "merged (only cars).csv")
    )
)

# Dont remove 2021, it is the 'sum' year
YEARS = [2016, 2017, 2018, 2019, 2020, 2021]

mapbox_access_token = "pk.eyJ1IjoicnZkaG9vcm4iLCJhIjoiY2t3eGVtbGNrMGRwNzJ3bnJucWp4emoweiJ9.5P0vCt-6KnIubabETLsymA"
mapbox_style = "mapbox://styles/rvdhoorn/ckx1u7m3v3k0o14pam2buej1s"

# Here we define the main layout of the visualization
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(children="Car accident visualization"),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=min(YEARS),
                                    marks={ # Here the labels of the slider are set, so 2021 is changed to 'sum'
                                        str(year): {
                                            "label": "sum" if year == 2021 else str(year),
                                            "style": {"color": "#000"},
                                        }
                                        for year in YEARS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap",
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=55, lon=-3.9
                                                ),
                                                pitch=0,
                                                zoom=5.3,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Accidents per age of driver",
                                    "value": "show_accidents_per_age",
                                },
                                {   "label": "Accidents per age of vehicle",
                                    "value": "show_accidents_per_vehicle_age",
                                },
                                {   "label": "Accidents per engine capacity",
                                    "value": "show_accidents_per_engine_capacity",
                                },
                            ],
                            value="show_accidents_per_age",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor=(227, 227, 227),
                                    plot_bgcolor=(227, 227, 227),
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)

initialize_left_side_functionality(app, df_lat_lon)
initilize_right_side_functionality(app, df_full_data)


if __name__ == "__main__":
    app.run_server(debug=True)
