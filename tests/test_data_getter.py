# tests/test_data_getter.py

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from mvbc.data_getter import (
    get_weather_data,
    get_longterm_weather_data,
    prefered_in_description,
    weatherstations_with_pref,
    get_weatherstation_information,
    get_latitude_longitude,
    get_closest_weatherstation,
    separate_by_parameter,
    get_closest_weatherstation_by_param,
    get_unavailable,
    get_closest_availbale_weatherstation_by_param,
    get_data_by_weatherstation,
)
from mvbc.config import Credentials
from mvbc.objects import Data

def test_get_weather_data(sample_dict_data, sample_df_weatherstations):
    df_weather = get_weather_data(sample_dict_data, sample_df_weatherstations)
    assert isinstance(df_weather, pd.DataFrame)
    assert "mvbc_ThorntonbankStationA_Temp" in df_weather.columns
    assert "mvbc_WandelaarStationB_Humidity" not in df_weather.columns  # WS2 has no data

def test_get_weather_data_no_values():
    dict_data = {
        "Values": [
            {"ID": "WS1", "Values": [{"Timestamp": "2023-01-01T00:00:00", "Value": 5}]},
            {"ID": "WS2", "Values": []}  # This should trigger a warning
        ]
    }
    df = pd.DataFrame({
        "Name": ["Weather Station 1", "Weather Station 2"],
        "ParameterName": ["Temperature", "Wind Speed"]
    }, index=["WS1", "WS2"])

    # Capture the warning using pytest.warns
    with pytest.warns(UserWarning, match="No values available for weatherstation: WS2"):
        get_weather_data(dict_data, df)

def test_prefered_in_description():
    import pandas as pd
    row_prefered = pd.Series({"Name": "Thorntonbank Station A"})
    row_non_prefered = pd.Series({"Name": "Random Station X"})
    assert prefered_in_description(row_prefered) is True
    assert prefered_in_description(row_non_prefered) is False

def test_get_latitude_longitude():
    pos_str = "POINT (52.0 4.0)"
    lat, lon = get_latitude_longitude(pos_str)
    assert lat == 52.0
    assert lon == 4.0

def test_get_closest_weatherstation():
    # Test data for weather stations
    df = pd.DataFrame({
        "ID": ["WS1", "WS2"],
        "PositionWKT": ["POINT (51.0 4.0)", "POINT (50.5 4.5)"]  # These are lat/lon for WS1 and WS2
    }).set_index("ID")
    
    # Offshore wind turbine position (should be closer to WS1)
    owt_position = [51.0, 4.0]

    # Call the function
    closest_station = get_closest_weatherstation(df, owt_position)

    # Check if WS1 is closest
    assert closest_station == "WS1"

def test_separate_by_parameter():
    # Create a DataFrame with 'Parameter' and other columns
    df = pd.DataFrame({
        "Name": ["Thorntonbank - Station A", "Wandelaar - Station B", "Westhinder - Station C"],
        "Parameter": ["GH1", "GHA", "GTZ"],  # These are the unique parameters
        "ParameterName": ["10% highest waves", "Wave height", "Average wave period"],
        "Description": ["Thorntonbank Station A", "Wandelaar Station B", "Westhinder Station C"],
        "ParameterUnit": ["cm", "cm", "s"],
        "PositionWKT": ["POINT (52.0 4.0)", "POINT (53.0 5.0)", "POINT (54.0 6.0)"]
    })

    # Call the function to separate the DataFrame by 'Parameter'
    result = separate_by_parameter(df)

    # Verify that the result is a dictionary with expected keys (parameters)
    expected_parameters = ["GH1", "GHA", "GTZ"]
    assert set(result.keys()) == set(expected_parameters)

    # Check the contents of one of the resulting DataFrames for a specific Parameter
    param_df = result["GH1"]
    assert len(param_df) == 1  # Should contain 1 row for "GH1"
    assert param_df["Name"].iloc[0] == "Thorntonbank - Station A"

    # Another check for the 'GHA' parameter
    gha_df = result["GHA"]
    assert len(gha_df) == 1  # Should contain 1 row for "GHA"
    assert gha_df["Name"].iloc[0] == "Wandelaar - Station B"


def test_get_closest_weatherstation_by_param(
    sample_df_weatherstations
):
    owt_position = [52.5, 4.5]
    closest = get_closest_weatherstation_by_param(
        sample_df_weatherstations, owt_position
    )
    assert isinstance(closest, dict)
    assert "P1" in closest
    assert closest["P1"] == "WS1"


def test_get_unavailable(sample_dict_data):
    unavailable = get_unavailable(sample_dict_data)
    assert unavailable == ["WS2"]


def test_get_weatherstation_information(sample_df_weatherstations):
    dict_closest = {"Temp": "WS1", "Humidity": "WS3"}
    information = ["ParameterName", "Name"]
    info_df = get_weatherstation_information(sample_df_weatherstations, dict_closest, information=information)
    assert isinstance(info_df, pd.DataFrame)
    assert list(info_df.columns) == information
    assert "WS1" in info_df.index
    assert "WS3" in info_df.index
