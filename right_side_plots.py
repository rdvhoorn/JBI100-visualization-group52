from re import A
from turtle import color
import pandas as pd
from dash.dependencies import Input, Output
import cufflinks as cf
import plotly.express as px


def initilize_right_side_functionality(app, df_full_data):
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

        # Select all data of the counties that were included in the lasso
        pts = selectedData["points"]
        counties = [str(pt["text"].split("<br>")[0]) for pt in pts]
        dff = df_full_data[df_full_data["district_name"].isin(counties)]

        # Sort data on accident year
        dff = dff.sort_values("accident_year")

        if chart_dropdown == "show_accidents_per_age":
            return accidents_per_age(dff)
        if chart_dropdown == "show_accidents_per_vehicle_age":
            return accidents_per_vehicle_age(dff)
        if chart_dropdown == "show_accidents_per_engine_capacity":
            return accidents_per_engine_capacity(dff)


def accidents_per_age(dff):
    """
    This function generates the right side figure displaying accidents per age
    """
    title = "Accidents per age of driver, <b>2016-2020</b>"
    AGGREGATE_BY = "age_of_driver"
    AGGREGATE_BY2 = "accident_severity"

    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age.drop([0,1,2], inplace=True)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['light','moderate','severe'])
    color_discrete_map = {'light' : 'green' , 'moderate' : 'red', 'severe' : 'black'}
    fig = px.bar(rate_per_age, x="age_of_driver", y="count", color="accident_severity", title=title, 
                 color_discrete_map = color_discrete_map, legend_title_text='Accident Severity')
    
    
    #fig = rate_per_age.iplot(
    #    kind="bar", x='age_of_driver', y='count', title=title, asFigure=True
    #)
    
    fig.update_layout(xaxis_title = "Age of driver (years)")
    fig.update_layout(yaxis_title = "Number of accidents")

    fig_layout = fig["layout"]
    fig_data = fig["data"]

    """fig_data[0]["text"] = rate_per_age.values.tolist()
    fig_data[0]["marker"]["color"] = (227, 227, 227)
    fig_data[0]["marker"]["opacity"] = 1
    fig_data[0]["marker"]["line"]["width"] = 0
    """
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


def accidents_per_vehicle_age(dff):
    """
    This function generates the right side figure displaying accidents per age
    """
    title = "Accidents per age of vehicle, <b>2016-2020</b>"
    AGGREGATE_BY = "age_of_vehicle"
    AGGREGATE_BY2 = "accident_severity"

    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age.drop([0,1,2], inplace=True)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['light','moderate','severe'])
    color_discrete_map = {'light' : 'green' , 'moderate' : 'red', 'severe' : 'black'}
    fig = px.bar(rate_per_age, x="age_of_vehicle", y="count", color="accident_severity", title=title, color_discrete_map = color_discrete_map)

    #fig = rate_per_age.iplot(
    #    kind="bar", x='age_of_vehicle', y='count', title=title, asFigure=True
    #)
    
    #fig.update_layout(xaxis_title = "Age of vehicle (years)")
    #fig.update_layout(yaxis_title = "Number of accidents")

    #fig_layout = fig["layout"]
    #fig_data = fig["data"]

    #print(fig_data)

    #fig_data[0]["text"] = dff.values.tolist()
    #fig_data[0]["marker"]["color"] = (100,0,0)
    #fig_data[0]['line']['color'] = rate_per_age['accident_severity']
    #fig_data[0]["color"] = "#ffc0cb"
    #fig_data[0]['line']['color'] = 'rgb (00,75,80,1.0)'
    #fig_data[0]["marker"]["opacity"] = 1
    #fig_data[0]["marker"]["line"]["width"] = 0
    #fig_data[0]["textposition"] = "outside"
    #fig_layout["paper_bgcolor"] = "#e3e3e3"
    #fig_layout["plot_bgcolor"] = "#e3e3e3"
    #fig_layout["font"]["color"] = "#000000"
    #fig_layout["title"]["font"]["color"] = "#000000"
    #fig_layout["xaxis"]["tickfont"]["color"] = "#000000"
    #fig_layout["yaxis"]["tickfont"]["color"] = "#000000"
    #fig_layout["xaxis"]["gridcolor"] = "#787878"
    #fig_layout["yaxis"]["gridcolor"] = "#787878"
    #fig_layout["margin"]["t"] = 75
    #fig_layout["margin"]["r"] = 50
    #fig_layout["margin"]["b"] = 100
    #fig_layout["margin"]["l"] = 50

    #print(dff)
    #print(fig_data)

    return fig


def accidents_per_engine_capacity(dff):
    """
    This function generates the right side figure displaying accidents per age
    """
    title = "Accidents per engine capacity, <b>2016-2020</b>"
    
    AGGREGATE_BY = "engine_capacity_cc"
    AGGREGATE_BY2 = "accident_severity"

    #dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    print(dff)
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    print(rate_per_age)
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age.drop([0,1,2], inplace=True)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['light','moderate','severe'])
    #color_discrete_map = {'light' : 'green' , 'moderate' : 'red', 'severe' : 'black'}
    fig = px.line(rate_per_age, x=AGGREGATE_BY, y="count", title=title)
    
    fig.update_layout(xaxis_title = "Engine capacity (cc)")
    fig.update_layout(yaxis_title = "Number of accidents")

    #fig_data[0]["text"] = rate_per_age.values.tolist()
    """fig_data[0]["marker"]["color"] = (227, 227, 227)
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
    fig_layout["margin"]["l"] = 50"""

    return fig