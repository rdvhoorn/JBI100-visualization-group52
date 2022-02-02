import math

from dash.dependencies import Input, Output, State
import cufflinks as cf
import json
from colormap import rgb2hex

mapbox_access_token = "pk.eyJ1IjoicnZkaG9vcm4iLCJhIjoiY2t3eGVtbGNrMGRwNzJ3bnJucWp4emoweiJ9.5P0vCt-6KnIubabETLsymA"
mapbox_style = "mapbox://styles/rvdhoorn/ckx1u7m3v3k0o14pam2buej1s"

DEFAULT_OPACITY = 0.8


def initialize_left_side_functionality(app, df_lat_lon):
    with open("./assets/data/lad.json") as infile:
        json_data = json.load(infile)

    @app.callback(
        Output("county-choropleth", "figure"),
        [
            Input("selected-districts", "children"),
            Input("years-dropdown", "value")
        ],
        [State("county-choropleth", "figure")],
    )
    def display_map(district_list, year, figure):
        """
        This function generates what is shown on the map on the left side of the visualiztion
        :param district_list:   The list of selected districts.
        :param year:            The year of the dropdown.
        :param figure:          The figure itself
        :return:                The figure to be shown
        """

        districts = []
        for district in district_list:
            if "lasso tool" not in district['props']['children']:
                districts.append(district['props']['children'])

        # Based on the year in the slider, a different variable of the dataset is shown. Here the name of that
        # variable is set.
        if year == 'sum':
            variable_name = "number_of_accidents"
        else:
            variable_name = "number_of_accidents_" + str(year)

        def color(x, max_of_scope, district_name):
            """
            A local function to generate a color for the overlay for all the data.
            :param x:               The value for which a color needs to be generated
            :param max_of_scope:    The max value of the scale
            :param district_name:   Name of county to check whether it is in the list of selected counties.
            :return:                An rgb color value
            """
            max_val = 255
            if x <= 0:
                return rgb2hex(191, 191, 191)

            val = int((x / max_of_scope) * max_val)

            if districts is not None and district_name in districts:
                return rgb2hex(230, max_val - val, max_val - val)

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

        maximum = math.ceil(max(accidents_per_100000)/500)*500

        # Make up hover text
        hover_text_df = df_lat_lon["Hover"].to_frame()
        title = "Number of Accidents"
        if year != 'sum':
            title += " in " + str(year) + ": "
        else:
            title += ": "

        # Loop over all counties to set the hover text specifically
        for feature in json_data['features']:
            county_name = feature['properties']["LAD13NM"]
            variable_number = feature['properties'][variable_name]
            hover_text_df.loc[hover_text_df.Hover.str.split("<br>").str.get(0) == county_name] += "<br>" + title + str(variable_number)

        data = [
            dict(
                lat=df_lat_lon["Latitude"],     # The latitude of the hover points
                lon=df_lat_lon["Longitude"],    # The longitude of the hover points
                text=hover_text_df["Hover"],       # The text to be shown when hovering near the points
                type="scattermapbox",
                hoverinfo="text",
                marker=dict(size=5, color="white", opacity=0),
            )
        ]

        # Here the legend of the graph is created
        # First, we make the title
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

        # Then the little bars
        bin_size = 500
        for i in range(0, maximum, bin_size):
            col = color(i+1, maximum+1, "dkdkkd")
            annotations.append(
                dict(
                    arrowcolor=col,
                    text=str(i),
                    x=0.95,
                    y=0.85 - ((i / (bin_size - 1)) / 20),
                    ax=-60,
                    ay=0,
                    arrowwidth=5,
                    arrowhead=0,
                    font=dict(color="#000000"),
                )
            )

        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]

        # Here we use the mapbox api to get the map
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

        # Load the geojson data for the district layout, and give each district a color using the color function
        for feature in json_data['features']:
            geo_layer = dict(
                sourcetype="geojson",
                source=feature,
                type="fill",
                color=color(feature['properties'][variable_name] / feature['properties']['population'] * 100000,
                            maximum, feature['properties']["LAD13NM"]),
                opacity=DEFAULT_OPACITY,
                fill=dict(outlinecolor="#afafaf")
            )

            layout["mapbox"]["layers"].append(geo_layer)

        fig = dict(data=data, layout=layout)
        return fig

    @app.callback(
        Output("heatmap-title", "children"),
        [Input("years-dropdown", "value")]
    )
    def update_map_title(year):
        """
        Callback function that determines the title of the heatmap
        :param year:    The selected year
        :return:        The title of the figure
        """
        if year == 'sum':
            return "Choropleth map of population adjusted accident rate of last 5 years"

        return "Choropleth map of population adjusted accident rate per district for {0}".format(year)
