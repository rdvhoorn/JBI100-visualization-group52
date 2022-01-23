import pandas as pd
from dash.dependencies import Input, Output
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
        if chart_dropdown == "show_accidents_per_time":
            return accidents_per_time(dff, year, df_full_data)
        if chart_dropdown == "show_accidents_per_propulsion_code":
            return accidents_per_propulsion_code(dff, year, df_full_data)
        if chart_dropdown == "show_accidents_per_sex_of_driver":
            return accidents_per_sex_of_driver(dff, year, df_full_data)
        if chart_dropdown == "show_accidents_per_urban_or_rural_area":
            return accidents_per_urban_or_rural_area(dff, year, df_full_data)

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
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['green','crimson','black'])
    #rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['light','moderate','severe'])
    #color_discrete_map = {'light' : 'green' , 'moderate' : 'red', 'severe' : 'black'}
    #fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title, 
    #             color_discrete_map = color_discrete_map, category_orders={"accident_severity": ["light", "moderate", "severe"]})
    
    # total UK data added - add data description
    df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
    df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age_fulldata.reset_index()
    rate_per_age_fulldata.drop([0,1,2], inplace=True)
    rate_per_age_fulldata['accident_severity'] = rate_per_age_fulldata['accident_severity'].replace([1,2,3], ['green','crimson','black'])

    
    # total UK data added - create the figure with total of UK shown as well
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                name='Selected countries', marker_color=rate_per_age[AGGREGATE_BY2],
                ))
    fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                name='Total UK', marker_color=rate_per_age_fulldata[AGGREGATE_BY2]
                ))
    

    # figure of selected countries (without total UK data)
    #fig = rate_per_age.iplot(
    #    kind="bar", x='age_of_driver', y='count', title=title, asFigure=True
    #)
    
    # layout figure
    fig.update_layout(xaxis_title = "Age of driver (years)")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')
    #fig.update_layout(color=AGGREGATE_BY2)


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
    fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title, 
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
    fig = px.histogram(rate_per_age, x=AGGREGATE_BY, y="count", title=title, color=AGGREGATE_BY2, nbins=100, 
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

def accidents_per_time(dff, year, df_full_data):
    """
    This function generates the right side figure displaying accidents per time of day
    """
    if year == 2021:
        title = "Accidents per time of day for 2016-2020"
    else: 
        title = "Accidents per time of day for {0}".format(year)

    AGGREGATE_BY = "time"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24']
    #x_labels = ['01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00','24:00']

    # data selected countries
    dff[AGGREGATE_BY] = dff[AGGREGATE_BY].str.slice(0,2)  #change from (HH:MM) to (HH), for bin sizes
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    #rate_per_age.drop([0,1,2], inplace=True)
    
    rate_per_age[AGGREGATE_BY] = rate_per_age[AGGREGATE_BY].replace([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24], x_labels ) # correct x label values
    #rate_per_age = pd.cut(rate_per_age, bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17 ,18, 19, 20, 21, 22, 23, 24], include_lowest=True)
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['green','crimson','black'])
    #rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['light','moderate','severe'])
    #color_discrete_map = {'light' : 'green' , 'moderate' : 'red', 'severe' : 'black'}
    #fig = px.bar(rate_per_age, x=AGGREGATE_BY, y="count", color=AGGREGATE_BY2, title=title, 
    #             color_discrete_map = color_discrete_map, category_orders={"accident_severity": ["light", "moderate", "severe"]})
    
    # total UK data added - add data description
    df_full_data[AGGREGATE_BY] = df_full_data[AGGREGATE_BY].str.slice(0,2)  #change from (HH:MM) to (HH), for bin sizes
    df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
    df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age_fulldata.reset_index()
    #rate_per_age_fulldata.drop([0,1,2], inplace=True)

    rate_per_age_fulldata[AGGREGATE_BY] = rate_per_age_fulldata[AGGREGATE_BY].replace([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24], x_labels ) # correct x label values
    rate_per_age_fulldata['accident_severity'] = rate_per_age_fulldata['accident_severity'].replace([1,2,3], ['green','crimson','black'])

    
    # total UK data added - create the figure with total of UK shown as well
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                name='Selected countries', marker_color=rate_per_age[AGGREGATE_BY2],
                ))
    fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                name='Total UK', marker_color=rate_per_age_fulldata[AGGREGATE_BY2]
                ))
    

    # figure of selected countries (without total UK data)
    #fig = rate_per_age.iplot(
    #    kind="bar", x='age_of_driver', y='count', title=title, asFigure=True
    #)
    
    # layout figure
    fig.update_layout(xaxis_title = "Time of day (hours)")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')
    #fig.update_layout(color=AGGREGATE_BY2)


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

    #propulsion code
def accidents_per_propulsion_code(dff, year, df_full_data):
    """
    This function generates the right side figure displaying accidents per propulsion code
    """
    if year == 2021:
        title = "Accidents per propulsion code for 2016-2020"
    else: 
        title = "Accidents per propulsion code for {0}".format(year)

    AGGREGATE_BY = "propulsion_code"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ['Petrol', 'Heavy oil', 'Electric', 'Steam', 'Gas', 'Petrol/Gas (LPG)', 'Gas/Bi-fuel', 'Hybrid electric', 'Gas Diesel', 'New fuel technology', 'Fuel cells', 'Electric diesel']

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    #rate_per_age.drop([0,1,2], inplace=True)
    rate_per_age = rate_per_age[rate_per_age[AGGREGATE_BY] != -1] #remove -1 missing value
    rate_per_age[AGGREGATE_BY] = rate_per_age[AGGREGATE_BY].replace([1,2,3,4,5,6,7,8,9,10,11,12], x_labels ) # correct x label values
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['green','crimson','black'])

    # total UK data added - add data description
    df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
    df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age_fulldata.reset_index()
    #rate_per_age_fulldata.drop([0,1,2], inplace=True)
    rate_per_age_fulldata = rate_per_age_fulldata[rate_per_age_fulldata[AGGREGATE_BY] != -1] #remove -1 missing value
    rate_per_age_fulldata[AGGREGATE_BY] = rate_per_age_fulldata[AGGREGATE_BY].replace([1,2,3,4,5,6,7,8,9,10,11,12], x_labels ) # correct x label values
    rate_per_age_fulldata['accident_severity'] = rate_per_age_fulldata['accident_severity'].replace([1,2,3], ['green','crimson','black'])

    
    # total UK data added - create the figure with total of UK shown as well
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                name='Selected countries', marker_color=rate_per_age[AGGREGATE_BY2],
                ))
    fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                name='Total UK', marker_color=rate_per_age_fulldata[AGGREGATE_BY2]
                ))
    

    # figure of selected countries (without total UK data)
    #fig = rate_per_age.iplot(
    #    kind="bar", x='age_of_driver', y='count', title=title, asFigure=True
    #)
    
    # layout figure
    fig.update_layout(xaxis_title = "Propulsion code")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')
    #fig.update_layout(color=AGGREGATE_BY2)


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

    #sex driver DONE
def accidents_per_sex_of_driver(dff, year, df_full_data):
    """
    This function generates the right side figure displaying accidents per sex of driver
    """
    if year == 2021:
        title = "Accidents per sex of driver for 2016-2020"
    else: 
        title = "Accidents per sex of driver for {0}".format(year)

    AGGREGATE_BY = "sex_of_driver"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ['Male', 'Female', 'Not known']

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    #rate_per_age.drop([0,1,2], inplace=True)
    rate_per_age = rate_per_age[rate_per_age[AGGREGATE_BY] != -1] #remove -1 missing value
    rate_per_age[AGGREGATE_BY] = rate_per_age[AGGREGATE_BY].replace([1,2,3], x_labels ) # correct x label values
    rate_per_age['accident_severity'] = rate_per_age['accident_severity'].replace([1,2,3], ['green','crimson','black'])
  
    # total UK data added - add data description
    df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
    df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age_fulldata.reset_index()
    #rate_per_age_fulldata.drop([0,1,2], inplace=True)
    rate_per_age_fulldata = rate_per_age_fulldata[rate_per_age_fulldata[AGGREGATE_BY] != -1] #remove -1 missing value
    rate_per_age_fulldata[AGGREGATE_BY] = rate_per_age_fulldata[AGGREGATE_BY].replace([1,2,3], x_labels ) # correct x label values
    rate_per_age_fulldata['accident_severity'] = rate_per_age_fulldata['accident_severity'].replace([1,2,3], ['green','crimson','black'])

    
    # total UK data added - create the figure with total of UK shown as well
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                name='Selected countries', marker_color=rate_per_age[AGGREGATE_BY2],
                ))
    fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                name='Total UK', marker_color=rate_per_age_fulldata[AGGREGATE_BY2]
                ))
    

    # figure of selected countries (without total UK data)
    #fig = rate_per_age.iplot(
    #    kind="bar", x='age_of_driver', y='count', title=title, asFigure=True
    #)
    
    # layout figure
    fig.update_layout(xaxis_title = "Sex of driver")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')
    #fig.update_layout(color=AGGREGATE_BY2)


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

    #urban or rural DONE
def accidents_per_urban_or_rural_area(dff, year, df_full_data):
    """
    This function generates the right side figure displaying accidents per urban or rural area
    """
    if year == 2021:
        title = "Accidents per urban or rural area for 2016-2020"
    else: 
        title = "Accidents per urban or rural area for {0}".format(year)

    AGGREGATE_BY = "urban_or_rural_area"
    AGGREGATE_BY2 = "accident_severity"
    x_labels = ["Urban", "Rural",""]

    # data selected countries
    dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
    dff = dff[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age = dff.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age.reset_index()
    #rate_per_age = rate_per_age[rate_per_age[AGGREGATE_BY] != 3]
    rate_per_age[AGGREGATE_BY] = rate_per_age[AGGREGATE_BY].replace([1,2,3], x_labels) # correct x label values to urban and rural
    rate_per_age[AGGREGATE_BY2] = rate_per_age[AGGREGATE_BY2].replace([1,2,3], ['green','crimson','black']) #colors of severity

    # total UK data added - add data description
    df_full_data[AGGREGATE_BY] = pd.to_numeric(df_full_data[AGGREGATE_BY], errors="coerce")
    df_full_data = df_full_data[["accident_index", AGGREGATE_BY, AGGREGATE_BY2]]
    rate_per_age_fulldata = df_full_data.groupby([AGGREGATE_BY, AGGREGATE_BY2], as_index=False).count()
    rate_per_age_fulldata.rename(columns={"accident_index": "count"}, inplace=True)
    rate_per_age_fulldata.reset_index()
    #rate_per_age_fulldata = rate_per_age_fulldata[rate_per_age_fulldata[AGGREGATE_BY] != 3]
    rate_per_age_fulldata[AGGREGATE_BY] = rate_per_age_fulldata[AGGREGATE_BY].replace([1,2,3], x_labels) # correct x label values to urban and rural
    rate_per_age_fulldata[AGGREGATE_BY2] = rate_per_age_fulldata[AGGREGATE_BY2].replace([1,2,3], ['green','crimson','black']) #colors of severity

    
    # total UK data added - create the figure with total of UK shown as well
    fig = go.Figure()
    fig.add_trace(go.Bar(x=rate_per_age[AGGREGATE_BY], y=rate_per_age['count'],
                name='Selected countries', marker_color=rate_per_age[AGGREGATE_BY2],
                ))
    fig.add_trace(go.Bar(x=rate_per_age_fulldata[AGGREGATE_BY], y=rate_per_age_fulldata['count'],
                name='Total UK', marker_color=rate_per_age_fulldata[AGGREGATE_BY2]
                ))
    

    # figure of selected countries (without total UK data)
    #fig = rate_per_age.iplot(
    #    kind="bar", x='age_of_driver', y='count', title=title, asFigure=True
    #)
    
    # layout figure
    fig.update_layout(xaxis_title = "Urban or rural area")
    fig.update_layout(yaxis_title = "Number of accidents")
    fig.update_layout(legend_title_text = 'Accident Severity')
    #fig.update_layout(color=AGGREGATE_BY2)


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
    # wrong fig_layout["xaxis"]["categoryorder"] = ["", "urban", "rural", "unallocated"]

    return fig