from re import A
from turtle import color
import pandas as pd
from dash.dependencies import Input, Output
import cufflinks as cf
from colormap import rgb2hex
import json
import plotly.express as px
import plotly.graph_objects as go #for showing total & selected countries in same barchart

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
            return accidents_per_age(dff, year, df_full_data)
        if chart_dropdown == "show_accidents_per_vehicle_age":
            return accidents_per_vehicle_age(dff, year, df_full_data)
        if chart_dropdown == "show_accidents_per_engine_capacity":
            return accidents_per_engine_capacity(dff, year)


def accidents_per_age(dff, year, df_full_data):
    """
    This function generates the right side figure displaying accidents per age
    """
    if year == 2021:
        title = "Accidents per age of driver for 2016-2020"
    else: 
        title = "Accidents per age of driver for {0}".format(year)

    AGGREGATE_BY = "age_of_driver"
    AGGREGATE_BY2 = "accident_severity"

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age.drop([0,1,2], inplace=True)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['light','moderate','severe'])
    color_discrete_map = {'light' : 'green' , 'moderate' : 'red', 'severe' : 'black'}
    fig = px.bar(rate_per_age, x="age_of_driver", y="count", color="accident_severity", title=title, 
                 color_discrete_map = color_discrete_map, category_orders={"accident_severity": ["light", "moderate", "severe"]})
    
    # total UK data added - add data description
    df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
    df_full_data = df_full_data[["accident_index", AGGREGATE_BY]]
    rate_per_age_fulldata = df_full_data.groupby(AGGREGATE_BY, as_index=False).count()
    rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age_fulldata.reset_index()
    rate_per_age_fulldata.drop([0], inplace=True)

    """
    # total UK data added - create the figure with total of UK shown as well
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                name='Selected countries',
                marker_color='rgb(26, 118, 255)'
                ))
    fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                name='Total UK',
                marker_color='rgb(55, 83, 109)'
                ))
    """

    # figure of selected countries (without total UK data)
    #fig = rate_per_age.iplot(
    #    kind="bar", x='age_of_driver', y='count', title=title, asFigure=True
    #)
    
    # layout figure
    fig.update_layout(xaxis_title = "Age of driver (years)")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')


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

    return fig

"""
def accidents_per_vehicle_age(dff, year):
    
    
    #This function generates the right side figure displaying accidents per age
    
    if year == 2021:
        title = "Accidents per age of vehicle for 2016-2020"   
    else: 
        title = "Accidents per age of vehicle for {0}".format(year)

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
    fig = px.bar(rate_per_age, x="age_of_vehicle", y="count", color="accident_severity", title=title, 
                 color_discrete_map = color_discrete_map, category_orders={"accident_severity": ["light", "moderate", "severe"]})

    fig.update_layout(xaxis_title = "Age of Vehicle (years)")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')
    
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

    return fig
"""

#try to visualize the total as well here
def accidents_per_vehicle_age(dff, year, df_full_data):
    """
    This function generates the right side figure displaying accidents per age
    """
    if year == 2021:
        title = "Accidents per age of vehicle for 2016-2020"   
    else: 
        title = "Accidents per age of vehicle for {0}".format(year)

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
    fig = px.bar(rate_per_age, x="age_of_vehicle", y="count", color="accident_severity", title=title, 
                 color_discrete_map = color_discrete_map, category_orders={"accident_severity": ["light", "moderate", "severe"]})
   
    # total UK data added - add data description
    df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
    df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age_fulldata.reset_index()
    rate_per_age_fulldata.drop([0,1,2], inplace=True)
    rate_per_age_fulldata['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['light','moderate','severe'])

    """
    # total UK data added - create the figure with total of UK shown as well
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                names='Selected countries',
                marker_color='rgb(26, 118, 255)'
                ))
    fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                names='Total UK',
                marker_color='rgb(55, 83, 109)'
                ))
    """

    # figure of selected countries (without total UK data)
    #fig = px.bar(rate_per_age, x="age_of_vehicle", y="count", color="accident_severity", title=title, color_discrete_map = color_discrete_map)

    #figure layour
    fig.update_layout(xaxis_title = "Age of vehicle (years)")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')

    #rate_per_age['count']["marker"]["color"] = (123, 123, 123)
    #rate_per_age['count']["marker"]["color"] = (321, 0, 0)
    #rate_per_age['count']["marker"]["color"] = (0, 0, 123)

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

    return fig

    #color_discrete_map = {'light' : 'green' , 'moderate' : 'red', 'severe' : 'black'}
    #fig = px.bar(rate_per_age, x="age_of_vehicle", y="count", color="accident_severity", title=title, color_discrete_map = color_discrete_map)
    
    #return fig

def accidents_per_engine_capacity(dff, year):
    """
    This function generates the right side figure displaying accidents per engine capacity
    """
    if year == 2021:
        title = "Accidents per engine capacity for 2016-2020"
    else: 
        title = "Accidents per engine capacity for {0}".format(year)
    
    AGGREGATE_BY = "engine_capacity_cc"
    AGGREGATE_BY2 = "accident_severity"

    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    rate_per_age.drop([0,1,2], inplace=True)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['light','moderate','severe'])
    color_discrete_map = {'light' : 'green' , 'moderate' : 'red', 'severe' : 'black'}
    fig = px.histogram(rate_per_age, x=AGGREGATE_BY, y="count", title=title, color="accident_severity", nbins=200, 
                       color_discrete_map=color_discrete_map, category_orders={"accident_severity": ["light", "moderate", "severe"]})
    
    fig.update_layout(xaxis_title = "Engine capacity (cc)")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')

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

    return fig