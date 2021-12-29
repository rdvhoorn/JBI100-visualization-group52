from dash.dependencies import Input, Output, State
import cufflinks as cf
import json
from colormap import rgb2hex

mapbox_access_token = "pk.eyJ1IjoicnZkaG9vcm4iLCJhIjoiY2t3eGVtbGNrMGRwNzJ3bnJucWp4emoweiJ9.5P0vCt-6KnIubabETLsymA"
mapbox_style = "mapbox://styles/rvdhoorn/ckx1u7m3v3k0o14pam2buej1s"

DEFAULT_OPACITY = 0.8

def initialize_left_side_functionality(app, df_lat_lon):
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