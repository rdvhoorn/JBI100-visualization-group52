import os
import pathlib
import re
import random

import dash
from dash import html, dcc
import pandas as pd
import cufflinks as cf


from right_side_plots import initialize_right_side_functionality
from left_side_plots import initialize_left_side_functionality
from right_side_tabs import initialize_right_side_tabs_functionality

r = lambda: random.randint(0, 255)

# Initialize app
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)

# Some settings
app.title = "Insurance data exploration"
server = app.server

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_lat_lon = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("assets/data", "lat_lon_districts_uk.csv"))
)

df_full_data = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("assets/data", "merged (only cars).csv")
    )
)

# Mapbox api access tokens and stylesheet for the choropleth map
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
                        html.Div(  # contains the explanation and drop-down menu
                            id="slider-container",
                            children=[
                                html.Div(
                                    id="explanation-div",
                                    children=[
                                        html.P(
                                            children=[
                                                "This visualization tool is aimed at helping insurance companies to explore " +
                                                "information about car accidents in England on a wide scale. Through "
                                                "using this tool, districts can be found that might differ from the "
                                                "average values for England for certain metrics which can prompt "
                                                "further in-depth investigation. First, select a year to inspect in the"
                                                " dropdown to the right of this text (or 'Aggregate' for the"
                                                " aggregation of all data). You can look at the data that appears on "
                                                "the map now! You can use the lasso tool to select a set of districts. "
                                                " After selecting the districts, various graphs will show on the right-hand side."]
                                        )
                                    ]
                                ),
                                html.Div(
                                    id="dropdown-div",
                                    children=[
                                        html.P(
                                            id="dropdown-text",
                                            children="Select the year of interest:",
                                        ),
                                        dcc.Dropdown(
                                            id="years-dropdown",
                                            options=[
                                                {'label': '2016', 'value': 2016},
                                                {'label': '2017', 'value': 2017},
                                                {'label': '2018', 'value': 2018},
                                                {'label': '2019', 'value': 2019},
                                                {'label': '2020', 'value': 2020},
                                                {'label': 'Aggregate', 'value': 'sum'},
                                            ],
                                            value='2016',
                                            clearable=False
                                        )
                                    ]
                                ),

                            ],
                        ),
                        html.Div(  # contains the choropleth map
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
                                                    lat=52.9, lon=-3.9
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
                    id='control-tabs',
                    className='control-tabs',
                    children=[  # Here the 3 different tabs are defined
                        dcc.Tabs(
                            id='tabs',
                            value='graphs',
                            children=[
                                dcc.Tab(  # The first tab regards the graphs, and includes the dropdown as well.
                                    label="Graphs",
                                    className="tab",
                                    value='graphs',
                                    children=[
                                        html.P(id="chart-selector", children="Select chart:"),
                                        dcc.Dropdown(
                                            options=[
                                                {"label": "Accidents per age of driver",
                                                 "value": "show_accidents_per_age",
                                                 },
                                                {"label": "Accidents per age of vehicle",
                                                 "value": "show_accidents_per_vehicle_age",
                                                 },
                                                {"label": "Accidents per engine capacity",
                                                 "value": "show_accidents_per_engine_capacity",
                                                 },
                                                {"label": "Accidents per time",
                                                 "value": "show_accidents_per_time",
                                                 },
                                                {"label": "Accidents per propulsion code",
                                                 "value": "show_accidents_per_propulsion_code",
                                                 },
                                                {"label": "Accidents per sex of driver",
                                                 "value": "show_accidents_per_sex_of_driver",
                                                 },
                                                {"label": "Accidents per urban or rural area",
                                                 "value": "show_accidents_per_urban_or_rural_area",
                                                 },
                                                {"label": "Accidents per left- or righthand driver",
                                                 "value": "show_accidents_per_left_right_hand",
                                                 },
                                            ],
                                            value="show_accidents_per_age",
                                            id="chart-dropdown",
                                        ),
                                        html.P(id="avUK_radio_item", children="Show graph of total England to compare:"),
                                        dcc.RadioItems(
                                            options=[
                                                {'label': 'Yes', 'value': 'yes'},
                                                {'label': 'No', 'value': 'no'}
                                            ],
                                            value='no',
                                            id='avUK',
                                            labelStyle={'display': 'inline-block'}
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

                                dcc.Tab(  # Tab that shows selected districts and buttons for customization of that list
                                    label="Selected Districts",
                                    value="sel-dist",
                                    className="tab",
                                    children=[
                                        html.Div(
                                            children=[
                                                dcc.Input(id='input', placeholder='Enter district', type="text"),
                                                html.Button('Add to list', id='add-button', n_clicks=0),
                                                html.Button('Remove from list', id='remove-button', n_clicks=0),
                                            ]
                                        ),
                                        html.Div(
                                            id="selected-districts",
                                            children=[]
                                        )
                                    ]
                                ),

                                dcc.Tab(  # Tab showing general information (generated by callback)
                                    label="General Info",
                                    value="gen-info",
                                    className="tab",
                                    children=[
                                        html.Div(
                                            id="general-info",
                                        )
                                    ]
                                )
                            ]
                        ),
                    ]
                ),
            ],
        ),
    ],
)


# Various functions for initializing all callback functionalities
initialize_left_side_functionality(app, df_lat_lon)
initialize_right_side_functionality(app, df_full_data, df_lat_lon)
initialize_right_side_tabs_functionality(app, df_full_data)

if __name__ == "__main__":
    app.run_server(debug=True)
