import os
import pathlib
import re
import random

import dash
from dash import html
from dash import dcc
import pandas as pd
import cufflinks as cf
from dash.dependencies import Input, Output, State

from right_side_plots import initilize_right_side_functionality
from left_side_plots import initialize_left_side_functionality

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
                                    marks={  # Here the labels of the slider are set, so 2021 is changed to 'sum'
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
                    children=[
                        dcc.Tabs(
                            id='tabs',
                            value='graphs',
                            children=[
                                dcc.Tab(
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

                                dcc.Tab(
                                    label="Selected Districts",
                                    value="sel-dist",
                                    className="tab",
                                    children=[
                                        html.Div(
                                            id="selected-districts",
                                        )
                                    ]
                                ),

                                dcc.Tab(
                                    label="General info",
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


@app.callback(
    Output("selected-districts", "children"),
    [
        Input("county-choropleth", "selectedData"),
    ]
)
def listSelectedDistricts(selectedData):
    if selectedData is None or not selectedData["points"]:
        return [html.P("No districts are currently selected. Use the lasso tool to select districts")]

    pts = selectedData["points"]
    districts = [str(pt["text"].split("<br>")[0]) for pt in pts]
    ps = []
    for district in districts:
        ps.append(html.P(district))

    return ps


@app.callback(
    Output("general-info", "children"),
    [
        Input("county-choropleth", "selectedData"),
        Input("years-slider", "value")
    ]
)
def construct_general_info(selectedData, year):
    if selectedData is None or not selectedData["points"]:
        return [html.P("No districts are currently selected. Use the lasso tool to select districts")]

    pts = selectedData["points"]
    districts = [str(pt["text"].split("<br>")[0]) for pt in pts]
    ps = []
    for district in districts:
        ps.append(html.P(district))

    messages = []

    dff = df_full_data[df_full_data["district_name"].isin(districts)]
    dff = dff.sort_values("accident_year")

    total_number_of_accidents_in_districts = dff.shape[0]
    total_number_of_accidents = df_full_data.shape[0]
    percentage_accidents = total_number_of_accidents_in_districts / (total_number_of_accidents / 100)

    number_male_drivers_districts = dff[dff["sex_of_driver"] == 1].shape[0]
    number_male_drivers = df_full_data[df_full_data["sex_of_driver"] == 1].shape[0]
    percentage_male_districts = number_male_drivers_districts / (total_number_of_accidents_in_districts / 100)
    percentage_male = number_male_drivers / (total_number_of_accidents / 100)

    number_female_drivers_districts = dff[dff["sex_of_driver"] == 2].shape[0]
    number_female_drivers = df_full_data[df_full_data["sex_of_driver"] == 2].shape[0]
    percentage_female_districts = number_female_drivers_districts / (total_number_of_accidents_in_districts / 100)
    percentage_female = number_female_drivers / (total_number_of_accidents / 100)

    average_age_of_driver_district = dff['age_of_driver'].mean()
    average_age_of_driver = df_full_data['age_of_driver'].mean()

    average_age_of_car_district = dff['age_of_vehicle'].mean()
    average_age_of_car = df_full_data['age_of_vehicle'].mean()

    tab = html.Table(
        children=[
            html.Tr(children=[
                html.Th(),
                html.Th("Selected countries"),
                html.Th("UK")
            ]),
            html.Tr(children=[
                html.Td("Number of accidents"),
                html.Td(str(total_number_of_accidents_in_districts) + " ({:.2f}%)".format(percentage_accidents)),
                html.Td(total_number_of_accidents)
            ]),
            html.Tr(children=[
                html.Td("Male driving during accident"),
                html.Td("{:.2f}%".format(percentage_male_districts)),
                html.Td("{:.2f}%".format(percentage_male))
            ]),
            html.Tr(children=[
                html.Td("Female driving during accident"),
                html.Td("{:.2f}%".format(percentage_female_districts)),
                html.Td("{:.2f}%".format(percentage_female))
            ]),
            html.Tr(children=[
                html.Td("Average age of driver in accident"),
                html.Td("{:.2f}".format(average_age_of_driver_district)),
                html.Td("{:.2f}".format(average_age_of_driver))
            ]),
            html.Tr(children=[
                html.Td("Average age of car in accident"),
                html.Td("{:.2f}".format(average_age_of_car_district)),
                html.Td("{:.2f}".format(average_age_of_car))
            ])
        ])

    messages.append(tab)

    return messages


initialize_left_side_functionality(app, df_lat_lon)
initilize_right_side_functionality(app, df_full_data)

if __name__ == "__main__":
    app.run_server(debug=True)
