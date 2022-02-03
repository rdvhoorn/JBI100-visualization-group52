from typing import List

from dash.dependencies import Input, Output, State
from dash import html, callback_context


def initialize_right_side_tabs_functionality(app, df_full_data) -> None:
    """
    This function initializes all callback functionality for the tabs 'General Info' and 'Selected Districts'
    :param app:             The dash app object to link the callbacks to
    :param df_full_data:    The full dataset with accident data
    """

    @app.callback(
        Output("selected-districts", "children"),
        [
            Input("selected-districts", "children"),
            Input("county-choropleth", "selectedData"),
            Input('add-button', 'n_clicks'),
            Input('remove-button', 'n_clicks'),
        ],
        State('input', 'value')
    )
    def listSelectedDistricts(district_list, selectedData, n_clicks1, n_clicks2, value) -> List:
        """
        This callback function generates the list of selected districts given the current list, the input field, the add
        and remove button, and the output of the lasso tool on the choropleth map.
        :param district_list:   The current list
        :param selectedData:    The output of the lasso tool
        :param n_clicks1:       The add button
        :param n_clicks2:       The remove button
        :param value:           The value of the input field
        :return:                A list containing html P elements to be shown in the tab.
        """
        # Initialize default return value
        default_return = [html.P("No districts are currently selected. Use the lasso tool to select districts")]

        # What has caused the callback to be called? changed_id will store whether it was the add button
        # the remove button, or the lasso tool.
        changed_id = [p['prop_id'] for p in callback_context.triggered]

        # If it was the lasso tool, the list of selected districts is reset and a new list is generated based on the
        # selection
        if len(changed_id) == 1 and changed_id[0] == "county-choropleth.selectedData":
            pts = selectedData["points"]
            districts = [str(pt["text"].split("<br>")[0]) for pt in pts]

            if len(districts) == 0:
                return default_return

            ps = []
            for district in districts:
                ps.append(html.P(district))

            return ps

        # If not the lasso tool, we first extract the districts that are currently in the list.
        districts_in_list = []
        for district in district_list:
            if "lasso tool" not in district['props']['children']:
                districts_in_list.append(district['props']['children'])

        # If the add button was clicked, we check if the value in the input field corresponds to a known district
        # which is not in the list. If so, we add it to the list.
        if len(changed_id) == 1 and changed_id[0] == "add-button.n_clicks":
            # add value to list
            added_district = get_name_corresponding_district(value, df_full_data)
            if added_district is not None and added_district not in districts_in_list:
                districts_in_list.append(added_district)

        # If the remove button was clicked, we check if the value in the input field corresponds to a known district
        # which is in the list. If so, we remove it from the list.
        if len(changed_id) == 1 and changed_id[0] == "remove-button.n_clicks":
            # remove value from list
            removed_district = get_name_corresponding_district(value, df_full_data)
            if removed_district is not None and removed_district in districts_in_list:
                districts_in_list.remove(removed_district)

        # From the list of names, create a list of html P elements with the names.
        ps = []
        for district in districts_in_list:
            ps.append(html.P(district))

        # If the final list is of length 0, return the default return.
        if len(ps) == 0:
            return default_return

        return ps

    @app.callback(
        Output("general-info", "children"),
        [
            Input("selected-districts", "children"),
            Input("years-dropdown", "value")
        ]
    )
    def construct_general_info(district_list, year):
        """
        This callback function generates the information presented in the general information tab.
        :param district_list:   A list of the currently selected districts
        :param year:            The year selected in the dropdown menu
        :return:                Html elements to display in the general info tab
        """
        # Given the html element of the district list, determine which districts are actually in there.
        districts = []
        for district in district_list:
            if "lasso tool" not in district['props']['children']:
                districts.append(district['props']['children'])

        # if no districts are selected, return the default text.
        if len(districts) == 0:
            return [html.P("No districts are currently selected. Use the lasso tool to select districts")]

        messages = []

        # Compute statistics about the selected data
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

        # Put computed statistics in a nice table
        tab = html.Table(
            children=[
                html.Tr(children=[
                    html.Th(),
                    html.Th("Selected districts"),
                    html.Th("England")
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


def get_name_corresponding_district(value: str, df_full_data):
    """
    Given a string, this function determines which district is the best match for it and returns the name
    of that district.
    :param value:           The substring for which a district is requested.
    :param df_full_data:    The full dataset containing the names of all districts.
    :return:                The determined district's name.
    """
    for district in df_full_data["district_name"].unique():
        if value in district:
            return district

    return None
