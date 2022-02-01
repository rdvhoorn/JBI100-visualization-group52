import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go


def initilize_right_side_functionality(app, df_full_data, df_lat_lon):
    @app.callback(
        Output("selected-data", "figure"),
        [
            Input("selected-districts", "children"),
            Input("chart-dropdown", "value"),
            Input("years-dropdown", "value"),
            Input("avUK", "value")
        ],
    )
    def display_selected_data(district_list, chart_dropdown, year, avUK):
        districts = []
        for district in district_list:
            if "lasso tool" not in district['props']['children']:
                districts.append(district['props']['children'])

        if len(districts) == 0:
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

        # Select all data of the counties that were included in the lasso
        dff = df_full_data[df_full_data["district_name"].isin(districts)]

        # District normalization
        district_total_pop = 0

        for i in districts:
            district_total_pop += df_lat_lon.loc[df_lat_lon["County"] == i, "Population"].iloc[0]
        district_ratio = (district_total_pop / 100000)

        # Total UK normalization
        UK_total_pop = df_lat_lon['Population'].sum()
        UK_ratio = (UK_total_pop / 100000)

        # Sort data on accident year
        dff = dff.sort_values("accident_year")

        if chart_dropdown == "show_accidents_per_age":
            return accidents_per_age(dff, year, df_full_data, avUK, district_ratio, UK_ratio)
        if chart_dropdown == "show_accidents_per_vehicle_age":
            return accidents_per_vehicle_age(dff, year, df_full_data, avUK, district_ratio, UK_ratio)
        if chart_dropdown == "show_accidents_per_engine_capacity":
            return accidents_per_engine_capacity(dff, year, df_full_data, avUK, district_ratio, UK_ratio)
        if chart_dropdown == "show_accidents_per_time":
            return accidents_per_time(dff, year, df_full_data, avUK, district_ratio, UK_ratio)
        if chart_dropdown == "show_accidents_per_propulsion_code":
            return accidents_per_propulsion_code(dff, year, df_full_data, avUK, district_ratio, UK_ratio)
        if chart_dropdown == "show_accidents_per_sex_of_driver":
            return accidents_per_sex_of_driver(dff, year, df_full_data, avUK, district_ratio, UK_ratio)
        if chart_dropdown == "show_accidents_per_urban_or_rural_area":
            return accidents_per_urban_or_rural_area(dff, year, df_full_data, avUK, district_ratio, UK_ratio)
        if chart_dropdown == "show_accidents_per_left_right_hand":
            return accidents_per_left_right_hand(dff, year, df_full_data, avUK, district_ratio, UK_ratio)


def accidents_per_age(dff, year, df_full_data, avUK, district_ratio, UK_ratio):
    """
    This function generates the right side figure displaying accidents per age
    """
    if year == 'sum':
        title = "Accidents per age of driver for 2016-2020 per 100.000 people"
    else:
        title = "Accidents per age of driver for {0} per 100.000 people".format(year)

    AGGREGATE_BY = "age_of_driver"
    AGGREGATE_BY2 = "accident_severity"

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age.drop([0, 1, 2], inplace=True)
    rate_per_age['count'] = (rate_per_age['count'] / district_ratio)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1, 2, 3],
                                                                                  ['Light', 'Moderate', 'Severe'])
    color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

    if avUK == "yes":
        # total UK data added - add data description
        df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
        df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
        rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
        rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age_fulldata.reset_index()
        rate_per_age_fulldata.drop([0, 1, 2], inplace=True)
        rate_per_age_fulldata['count'] = (rate_per_age_fulldata['count'] / UK_ratio)
        rate_per_age_fulldata['accident_severity'] = rate_per_age_fulldata['accident_severity'].replace([1, 2, 3],
                                                                                                        ['Light',
                                                                                                         'Moderate',
                                                                                                         'Severe'])
        color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

        fig = go.Figure()
        fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                             name='Selected districts', marker_color="blue",
                             ))
        fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                             name='Total UK', marker_color="red"
                             ))

    if avUK == "no":
        fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title,
                     color_discrete_map=color_discrete_map,
                     category_orders={"accident_severity": ["Severe", "Moderate", "Light"]})

    # fig.update_layout(color=AGGREGATE_BY2)
    fig.update_layout(xaxis_title="Age of driver (years)")
    fig.update_layout(yaxis_title="Number of accidents")
    fig.update_layout(legend_title_text='Accident Severity')

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    fig_data, fig_layout = get_graph_layout(fig_layout, fig_data)
    return fig


def accidents_per_vehicle_age(dff, year, df_full_data, avUK, district_ratio, UK_ratio):
    """
    This function generates the right side figure displaying accidents per age
    """
    if year == 'sum':
        title = "Accidents per age of vehicle for 2016-2020 per 100.000 people"
    else:
        title = "Accidents per age of vehicle for {0} per 100.000 people".format(year)

    AGGREGATE_BY = "age_of_vehicle"
    AGGREGATE_BY2 = "accident_severity"

    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]

    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age = rate_per_age[
        rate_per_age[AGGREGATE_BY] < 41]  # remove above 40, because data points are so low, the bars dont show
    rate_per_age.drop([0, 1, 2], inplace=True)
    rate_per_age['count'] = (rate_per_age['count'] / district_ratio)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1, 2, 3],
                                                                                  ['Light', 'Moderate', 'Severe'])
    color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

    if avUK == "yes":
        # total UK data added - add data description
        df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
        df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
        rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
        rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age_fulldata.reset_index()
        rate_per_age_fulldata = rate_per_age_fulldata[rate_per_age_fulldata[
                                                          AGGREGATE_BY] < 41]  # remove above 40, because data points are so low, the bars dont show
        rate_per_age_fulldata.drop([0, 1, 2], inplace=True)
        rate_per_age_fulldata['count'] = (rate_per_age_fulldata['count'] / UK_ratio)
        rate_per_age_fulldata['accident_severity'] = rate_per_age['accident_severity'].replace([1, 2, 3],
                                                                                               ['Light', 'Moderate',
                                                                                                'Severe'])
        color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

        fig = go.Figure()
        fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                             name='Selected districts', marker_color="blue",
                             ))
        fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                             name='Total UK', marker_color="red"
                             ))

    if avUK == "no":
        fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title,
                     color_discrete_map=color_discrete_map,
                     category_orders={"accident_severity": ["Severe", "Moderate", "Light"]})

    fig.update_layout(xaxis_title="Age of vehicle (years)")
    fig.update_layout(yaxis_title="Number of accidents")
    fig.update_layout(legend_title_text='Accident Severity')

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    fig_data, fig_layout = get_graph_layout(fig_layout, fig_data)

    return fig


def accidents_per_engine_capacity(dff, year, df_full_data, avUK, district_ratio, UK_ratio):
    """
    This function generates the right side figure displaying accidents per engine capacity
    """
    if year == 'sum':
        title = "Accidents per engine capacity for 2016-2020 per 100.000 people"
    else:
        title = "Accidents per engine capacity for {0} per 100.000 people".format(year)

    AGGREGATE_BY = "engine_capacity_cc"
    AGGREGATE_BY2 = "accident_severity"

    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age = rate_per_age[
        rate_per_age[AGGREGATE_BY] < 8001]  # remove above 8000, because data points are so low, the bars dont show
    rate_per_age.drop([0, 1, 2], inplace=True)
    rate_per_age['count'] = (rate_per_age['count'] / district_ratio)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1, 2, 3],
                                                                                  ["Light", "Moderate", "Severe"])
    color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

    if avUK == "yes":
        # total UK data added - add data description
        df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
        df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
        rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
        rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age_fulldata.reset_index()
        # remove above 8000, because data points are so low, the bars dont show
        rate_per_age_fulldata = rate_per_age_fulldata[rate_per_age_fulldata[
                                                          AGGREGATE_BY] < 8001]
        rate_per_age_fulldata.drop([0, 1, 2], inplace=True)
        rate_per_age_fulldata['count'] = (rate_per_age_fulldata['count'] / UK_ratio)
        rate_per_age_fulldata["accident_severity"] = rate_per_age["accident_severity"].replace([1, 2, 3],
                                                                                               ["Light", "Moderate",
                                                                                                "Severe"])

        fig = go.Figure()
        fig.add_trace(go.Histogram(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                                   name='Selected districts', marker_color="blue", nbinsx=20
                                   ))
        fig.add_trace(go.Histogram(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                                   name='Total UK', marker_color="red", nbinsx=20
                                   ))

    if avUK == "no":
        fig = px.histogram(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title,
                           color_discrete_map=color_discrete_map,
                           category_orders={"accident_severity": ["Severe", "Moderate", "Light"]}, nbins=80)

    fig.update_layout(xaxis_title="Engine capacity (cc)")
    fig.update_layout(yaxis_title="Number of accidents")
    fig.update_layout(legend_title_text='Accident Severity')

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    get_graph_layout(fig_layout, fig_data)

    return fig


def accidents_per_time(dff, year, df_full_data, avUK, district_ratio, UK_ratio):
    """
    This function generates the right side figure displaying accidents per time of day
    """
    if year == 'sum':
        title = "Accidents per time of day for 2016-2020 per 100.000 people"
    else:
        title = "Accidents per time of day for {0} per 100.000 people".format(year)

    AGGREGATE_BY = "time"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17',
                '18', '19', '20', '21', '22', '23', '24']

    # data selected countries
    dff[AGGREGATE_BY] = dff[AGGREGATE_BY].str.slice(0, 2)  # change from (HH:MM) to (HH), for bin sizes
    #dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age['count'] = (rate_per_age['count'] / district_ratio)
    # rate_per_age.drop([0,1,2], inplace=True)

    rate_per_age_2 = rate_per_age.copy()
    rate_per_age_2[AGGREGATE_BY] = rate_per_age_2[AGGREGATE_BY].replace(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
        x_labels)  # correct x label values
    rate_per_age_2['accident_severity'] = rate_per_age_2['accident_severity'].replace([1, 2, 3],
                                                                                  ["Light", "Moderate", "Severe"])

    color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

    if avUK == "yes":
        # total UK data added - add data description
        df_full_data[AGGREGATE_BY] = df_full_data[AGGREGATE_BY].str.slice(0,2)  # change from (HH:MM) to (HH), for bin sizes
        #df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
        df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
        rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
        rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age_fulldata.reset_index()
        rate_per_age_fulldata['count'] = (rate_per_age_fulldata['count'] / UK_ratio)
        color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

        rate_per_age_fulldata_2 = rate_per_age_fulldata.copy()
        rate_per_age_fulldata_2[AGGREGATE_BY] = rate_per_age_fulldata_2[AGGREGATE_BY].replace(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            x_labels)  # correct x label values
        rate_per_age_fulldata_2['accident_severity'] = rate_per_age_fulldata_2['accident_severity'].replace([1, 2, 3],
                                                                                                        ["Light",
                                                                                                         "Moderate",
                                                                                                         "Severe"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=rate_per_age_2[AGGREGATE_BY], y=rate_per_age_2['count'],
                             name='Selected districts', marker_color="blue",
                             ))
        fig.add_trace(go.Bar(x=rate_per_age_fulldata_2[AGGREGATE_BY], y=rate_per_age_fulldata_2['count'],
                             name='Total UK', marker_color="red"
                             ))

    if avUK == "no":
        fig = px.bar(rate_per_age_2, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title,
                     color_discrete_map=color_discrete_map,
                     category_orders={"accident_severity": ["Severe", "Moderate", "Light"]})

    # layout figure
    fig.update_layout(xaxis_title="Time of day (hours)")
    fig.update_layout(yaxis_title="Number of accidents")
    fig.update_layout(legend_title_text='Accident Severity')

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    fig_data, fig_layout = get_graph_layout(fig_layout, fig_data)

    return fig


def accidents_per_propulsion_code(dff, year, df_full_data, avUK, district_ratio, UK_ratio):
    """
    This function generates the right side figure displaying accidents per propulsion code
    """
    if year == 'sum':
        title = "Accidents per propulsion code for 2016-2020 per 100.000 people"
    else:
        title = "Accidents per propulsion code for {0} per 100.000 people".format(year)

    AGGREGATE_BY = "propulsion_code"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ['Petrol', 'Heavy oil', 'Electric', 'Steam', 'Gas', 'Petrol/Gas (LPG)', 'Gas/Bi-fuel', 'Hybrid electric',
                'Gas Diesel', 'New fuel technology', 'Fuel cells', 'Electric diesel']

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age['count'] = (rate_per_age['count'] / district_ratio)
    rate_per_age = rate_per_age[rate_per_age[AGGREGATE_BY] != -1]  # remove -1 missing value
    rate_per_age[AGGREGATE_BY] = rate_per_age[AGGREGATE_BY].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                                                    x_labels)  # correct x label values
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1, 2, 3],
                                                                                  ["Light", "Moderate", "Severe"])
    color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

    if avUK == "yes":
        # total UK data added - add data description
        df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
        df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
        rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
        rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age_fulldata.reset_index()
        rate_per_age_fulldata['count'] = (rate_per_age_fulldata['count'] / UK_ratio)
        rate_per_age_fulldata = rate_per_age_fulldata[
            rate_per_age_fulldata[AGGREGATE_BY] != -1]  # remove -1 missing value
        rate_per_age_fulldata[AGGREGATE_BY] = rate_per_age_fulldata[AGGREGATE_BY].replace(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], x_labels)  # correct x label values
        rate_per_age_fulldata['accident_severity'] = rate_per_age_fulldata['accident_severity'].replace([1, 2, 3],
                                                                                                        ["Light",
                                                                                                         "Moderate",
                                                                                                         "Severe"])

        fig = go.Figure()
        fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                             name='Selected districts', marker_color="blue",
                             ))
        fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                             name='Total UK', marker_color="red"
                             ))

    if avUK == "no":
        fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title,
                     color_discrete_map=color_discrete_map,
                     category_orders={"accident_severity": ["Severe", "Moderate", "Light"]})

    # layout figure
    fig.update_layout(xaxis_title="Propulsion code")
    fig.update_layout(yaxis_title="Number of accidents")
    fig.update_layout(legend_title_text='Accident Severity')

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    fig_data, fig_layout = get_graph_layout(fig_layout, fig_data)

    return fig


def accidents_per_sex_of_driver(dff, year, df_full_data, avUK, district_ratio, UK_ratio):
    """
    This function generates the right side figure displaying accidents per sex of driver
    """
    if year == 'sum':
        title = "Accidents per sex of driver for 2016-2020 per 100.000 people"
    else:
        title = "Accidents per sex of driver for {0} per 100.000 people".format(year)

    AGGREGATE_BY = "sex_of_driver"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ['Male', 'Female', 'Not known']

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age['count'] = (rate_per_age['count'] / district_ratio)
    # rate_per_age.drop([0,1,2], inplace=True)
    rate_per_age = rate_per_age[rate_per_age[AGGREGATE_BY] != -1]  # remove -1 missing value
    rate_per_age[AGGREGATE_BY] = rate_per_age[AGGREGATE_BY].replace([1, 2, 3], x_labels)  # correct x label values
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1, 2, 3],
                                                                                  ["Light", "Moderate", "Severe"])
    color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

    if avUK == "yes":
        # total UK data added - add data description
        df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
        df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
        rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
        rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age_fulldata.reset_index()
        # rate_per_age_fulldata.drop([0,1,2], inplace=True)
        rate_per_age_fulldata['count'] = (rate_per_age_fulldata['count'] / UK_ratio)
        rate_per_age_fulldata = rate_per_age_fulldata[
            rate_per_age_fulldata[AGGREGATE_BY] != -1]  # remove -1 missing value
        rate_per_age_fulldata[AGGREGATE_BY] = rate_per_age_fulldata[AGGREGATE_BY].replace([1, 2, 3],
                                                                                          x_labels)  # correct x label values
        rate_per_age_fulldata['accident_severity'] = rate_per_age_fulldata['accident_severity'].replace([1, 2, 3],
                                                                                                        ["Light",
                                                                                                         "Moderate",
                                                                                                         "Severe"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                             name='Selected districts', marker_color="blue",
                             ))
        fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                             name='Total UK', marker_color="red"
                             ))

    if avUK == "no":
        fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title,
                     color_discrete_map=color_discrete_map,
                     category_orders={"accident_severity": ["Severe", "Moderate", "Light"]})

    fig.update_layout(xaxis_title="Sex of driver")
    fig.update_layout(yaxis_title="Number of accidents")
    fig.update_layout(legend_title_text='Accident Severity')

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    fig_data, fig_layout = get_graph_layout(fig_layout, fig_data)

    return fig


def accidents_per_urban_or_rural_area(dff, year, df_full_data, avUK, district_ratio, UK_ratio):
    """
    This function generates the right side figure displaying accidents per urban or rural area
    """
    if year == 'sum':
        title = "Accidents per urban or rural area for 2016-2020 per 100.000 people"
    else:
        title = "Accidents per urban or rural area for {0} per 100.000 people".format(year)

    AGGREGATE_BY = "urban_or_rural_area"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ["Urban", "Rural", " "]

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age['count'] = (rate_per_age['count'] / district_ratio)
    rate_per_age[AGGREGATE_BY] = rate_per_age[AGGREGATE_BY].replace([1, 2, 3],
                                                                    x_labels)  # correct x label values to urban and rural
    rate_per_age[AGGREGATE_BY2] = rate_per_age[AGGREGATE_BY2].replace([1, 2, 3], ["Light", "Moderate",
                                                                                  "Severe"])  # colors of severity
    color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

    if avUK == "yes":
        # total UK data added - add data description
        df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
        df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
        rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
        rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age_fulldata.reset_index()
        rate_per_age_fulldata['count'] = (rate_per_age_fulldata['count'] / UK_ratio)
        # rate_per_age_fulldata = rate_per_age_fulldata[rate_per_age_fulldata[AGGREGATE_BY] != 3]
        rate_per_age_fulldata[AGGREGATE_BY] = rate_per_age_fulldata[AGGREGATE_BY].replace([1, 2, 3],
                                                                                          x_labels)  # correct x label values to urban and rural
        rate_per_age_fulldata[AGGREGATE_BY2] = rate_per_age_fulldata[AGGREGATE_BY2].replace([1, 2, 3],
                                                                                            ["Light", "Moderate",
                                                                                             "Severe"])  # colors of severity

        fig = go.Figure()
        fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                             name='Selected districts', marker_color="blue",
                             ))
        fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                             name='Total UK', marker_color="red"
                             ))

    if avUK == "no":
        fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title,
                     color_discrete_map=color_discrete_map,
                     category_orders={"accident_severity": ["Severe", "Moderate", "Light"]})

    fig.update_layout(xaxis_title="Urban or rural area")
    fig.update_layout(yaxis_title="Number of accidents")
    fig.update_layout(legend_title_text='Accident Severity')
    fig_layout = fig["layout"]
    fig_data = fig["data"]
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

def accidents_per_left_right_hand(dff, year, df_full_data, avUK, district_ratio, UK_ratio):
    """
    This function generates the right side figure displaying accidents per left- or righthand driver
    """
    if year == 'sum':
        title = "Accidents per left- or righthand driver for 2016-2020 per 100.000 people"
    else:
        title = "Accidents per left- or righthand driver for {0} per 100.000 people".format(year)

    AGGREGATE_BY = "vehicle_left_hand_drive"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ["Right", "Left"]

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age['count'] = (rate_per_age['count'] / district_ratio)
    rate_per_age = rate_per_age[rate_per_age[AGGREGATE_BY] != -1]  # drop missing values
    rate_per_age = rate_per_age[rate_per_age[AGGREGATE_BY] != 9]  # drop missing values
    rate_per_age[AGGREGATE_BY] = rate_per_age[AGGREGATE_BY].replace([1, 2],
                                                                    x_labels)  # correct x label values to urban and rural
    rate_per_age[AGGREGATE_BY2] = rate_per_age[AGGREGATE_BY2].replace([1, 2, 3], ["Light", "Moderate",
                                                                                  "Severe"])  # colors of severity
    color_discrete_map = {'Light': '#FFC400', 'Moderate': '#FF7700', 'Severe': '#FF0000'}

    if avUK == "yes":
        # total UK data added - add data description
        df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
        df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
        rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
        rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
        rate_per_age_fulldata.reset_index()
        rate_per_age_fulldata['count'] = (rate_per_age_fulldata['count'] / UK_ratio)
        rate_per_age_fulldata = rate_per_age_fulldata[rate_per_age_fulldata[AGGREGATE_BY] != -1]  # drop missing values
        rate_per_age_fulldata = rate_per_age_fulldata[rate_per_age_fulldata[AGGREGATE_BY] != 9]  # drop missing values
        rate_per_age_fulldata[AGGREGATE_BY] = rate_per_age_fulldata[AGGREGATE_BY].replace([1, 2],
                                                                                          x_labels)  # correct x label values to urban and rural
        rate_per_age_fulldata[AGGREGATE_BY2] = rate_per_age_fulldata[AGGREGATE_BY2].replace([1, 2, 3],
                                                                                            ["Light", "Moderate",
                                                                                             "Severe"])  # colors of severity
        fig = go.Figure()
        fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                             name='Selected districts', marker_color="blue",
                             ))
        fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                             name='Total UK', marker_color="red"
                             ))

    if avUK == "no":
        fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title,
                     color_discrete_map=color_discrete_map,
                     category_orders={"accident_severity": ["Severe", "Moderate", "Light"]})

    # layout figure
    fig.update_layout(xaxis_title="Left- or righthand driver")
    fig.update_layout(yaxis_title="Number of accidents")
    fig.update_layout(legend_title_text='Accident Severity')

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    fig_data, fig_layout = get_graph_layout(fig_layout, fig_data)

    return fig


def get_graph_layout(fig_layout, fig_data):
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
    return fig_data, fig_layout
