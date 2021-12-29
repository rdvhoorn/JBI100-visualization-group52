import pandas as pd
from dash.dependencies import Input, Output
import cufflinks as cf

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