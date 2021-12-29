import os
import pathlib
import re
import json
import random

import dash
from dash import html
from dash import dcc
import pandas as pd
from dash.dependencies import Input, Output, State
from colormap import rgb2hex
import cufflinks as cf

r = lambda: random.randint(0, 255)

# Initialize app
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "Visualization assignment"
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

YEARS = [2016, 2017, 2018, 2019, 2020, 2021]

DEFAULT_OPACITY = 0.8

mapbox_access_token = "pk.eyJ1IjoicnZkaG9vcm4iLCJhIjoiY2t3eGVtbGNrMGRwNzJ3bnJucWp4emoweiJ9.5P0vCt-6KnIubabETLsymA"
mapbox_style = "mapbox://styles/rvdhoorn/ckx1u7m3v3k0o14pam2buej1s"

# App layout
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
                                    marks={
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
                                    "label": "Accidents per age",
                                    "value": "show_accidents_per_age",
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


@app.callback(
    Output("county-choropleth", "figure"),
    [Input("years-slider", "value")],
    [State("county-choropleth", "figure")],
)
def display_map(year, figure):
    variable_name = "number_of_accidents_" + str(year)

    if year == 2021:
        variable_name = "number_of_accidents"

    with open("./assets/data/lad.json") as infile:
        json_data = json.load(infile)

    def color(x, max):
        max_val = 255
        if x <= 0:
            return rgb2hex(191, 191, 191)

        val = int((x / max) * max_val)

        return rgb2hex(255, max_val - val, max_val - val)

    accidents_per_100000 = []
    names = ["number_of_accidents_2016", "number_of_accidents_2017", "number_of_accidents_2018",
             "number_of_accidents_2019", "number_of_accidents_2020"]
    if variable_name in names:
        for name in names:
            for feature in json_data['features']:
                accidents_per_100000.append(
                    int(feature['properties'][name] / feature['properties']['population'] * 100000))

    else:
        for feature in json_data['features']:
            accidents_per_100000.append(
                int(feature['properties'][variable_name] / feature['properties']['population'] * 100000))

    maximum = max(accidents_per_100000)

    data = [
        dict(
            lat=df_lat_lon["Latitude"],
            lon=df_lat_lon["Longitude"],
            text=df_lat_lon["Hover"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]

    annotations = [
        dict(
            showarrow=False,
            align="right",
            text="<b>Number of car accidents<br>per 100.000 people</b>",
            font=dict(color="#000000"),
            x=0.95,
            y=0.95,
        )
    ]

    binsize = int(maximum / 5)

    for i in range(1, maximum, binsize - 1):
        col = color(i, maximum)
        annotations.append(
            dict(
                arrowcolor=col,
                text=str(i),
                x=0.95,
                y=0.85 - ((i / (binsize - 1)) / 20),
                ax=-60,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                font=dict(color="#000000"),
            )
        )

    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = 38.72490
        lon = -95.61446
        zoom = 3.5

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
    )

    for feature in json_data['features']:
        geo_layer = dict(
            sourcetype="geojson",
            source=feature,
            type="fill",
            color=color(feature['properties'][variable_name] / feature['properties']['population'] * 100000,
                        maximum),
            opacity=DEFAULT_OPACITY,
            fill=dict(outlinecolor="#afafaf")
        )

        layout["mapbox"]["layers"].append(geo_layer)

    fig = dict(data=data, layout=layout)
    return fig


@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
def update_map_title(year):
    if year == 2021:
        return "heatmap of population adjusted accident rate of last 5 years"

    return "Heatmap of population adjusted accident rate per district for {0}".format(
        year
    )


@app.callback(
    Output("selected-data", "figure"),
    [
        Input("county-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
    ],
)
def display_selected_data(selectedData, chart_dropdown, year):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click-drag on the map to select counties",
                paper_bgcolor=(227, 227, 227),
                plot_bgcolor=(227, 227, 227),
                font=dict(color="#000000"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )

    pts = selectedData["points"]
    counties = [str(pt["text"].split("<br>")[0]) for pt in pts]
    dff = df_full_data[df_full_data["district_name"].isin(counties)]
    dff = dff.sort_values("accident_year")

    if chart_dropdown == "show_accidents_per_age":
        title = "Accidents per age, <b>2016-2020</b>"
        AGGREGATE_BY = "age_of_driver"

        dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
        dff = dff[["accident_index", AGGREGATE_BY]]
        rate_per_age = dff.groupby(AGGREGATE_BY, as_index=False).count()
        rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age.reset_index()
        rate_per_age.drop([0], inplace=True)
        fig = rate_per_age.iplot(
            kind="bar", y='count', title=title, asFigure=True
        )

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_data[0]["text"] = rate_per_age.values.tolist()
        fig_data[0]["marker"]["color"] = (227, 227, 227)
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#e3e3e3"
        fig_layout["plot_bgcolor"] = "#e3e3e3"
        fig_layout["font"]["color"] = "#000000"
        fig_layout["title"]["font"]["color"] = "#000000"
        fig_layout["xaxis"]["tickfont"]["color"] = "#000000"
        fig_layout["yaxis"]["tickfont"]["color"] = "#000000"
        fig_layout["xaxis"]["gridcolor"] = "#787878"
        fig_layout["yaxis"]["gridcolor"] = "#787878"
        fig_layout["margin"]["t"] = 75
        fig_layout["margin"]["r"] = 50
        fig_layout["margin"]["b"] = 100
        fig_layout["margin"]["l"] = 50

        return fig


if __name__ == "__main__":
    app.run_server(debug=True)
