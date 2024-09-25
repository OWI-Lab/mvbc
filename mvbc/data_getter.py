"""
mvbc data_getter
---------

Code to fetch the data of the closest weather station (part of my personal package).
-
Maximillian Weil
..
"""

from datetime import datetime, timedelta
from typing import Any

import geopy.distance
import pandas as pd
import warnings

from mvbc.config import Credentials
from mvbc.objects import Data


def get_weather_data(dict_data: dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    """Extracts and formats weather data for the specified weather stations based on the 
    `dict_data` provided by the mvbc API.

    Args:
        dict_data (dict[str, Any]): The raw data extracted from the mvbc API for the given weather station IDs.
        df (pd.DataFrame): DataFrame containing weather station details from `mvbc.Catalog.filter_parameter()`.

    Raises:
        Warning: When a weather station has no data available, a warning is issued.

    Returns:
        pd.DataFrame: A DataFrame containing weather data for the weather stations specified in dict_data.
    """
    df_weather = pd.DataFrame()
    for values in dict_data["Values"]:
        id_ = values["ID"]
        if values["Values"]:
            df_ = (
                pd.DataFrame(values["Values"])
                .set_index("Timestamp")
                .rename(columns={"Value": id_})
            )
            param_name = "_".join(
                [
                    "mvbc",
                    df["Name"][df.index == id_][0].replace(" - ", "").replace(" ", ""),
                    df["ParameterName"][df.index == id_][0]
                    .replace(" - ", " ")
                    .replace(" ", "_"),
                ]
            )
            df_weather[param_name] = df_[id_]
        else:
            warnings.warn(f"No values available for weatherstation: {id_}", UserWarning)
    df_weather.set_index(pd.to_datetime(df_weather.index), inplace=True)
    return df_weather


def get_longterm_weather_data(
    owt_location: list[float],
    dt_start: datetime,
    dt_end: datetime,
    df: pd.DataFrame,
    credentials: Credentials,
    prefered: list[str] = ["Thorntonbank", "Wandelaar", "Westhinder"],
    information: list[str] = ["ParameterName", "Name", "Description", "ParameterUnit"],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetches long-term weather data for the time period between `dt_start` and `dt_end` 
    for the closest weather station to the specified offshore wind turbine (OWT) location.
    Prioritizes the weather stations in the `prefered` list if available.

    Args:
        owt_location (list[float]): The geographical coordinates of the offshore wind turbine.
        dt_start (datetime): The start of the data collection period.
        dt_end (datetime): The end of the data collection period.
        df (pd.DataFrame): DataFrame containing metadata about available weather data points.
        credentials (Credentials): User credentials to access the mvbc API.
        prefered (list[str], optional): List of preferred weather stations. 
            Defaults to ["Thorntonbank", "Wandelaar", "Westhinder"].
        information (list[str], optional): Fields of information to retrieve about the weather station. 
            Defaults to ["ParameterName", "Name", "Description", "ParameterUnit"].

    Returns:
        pd.DataFrame: The weather data for the specified time period.
        pd.DataFrame: Information about the weather station for the last 3-month period.
            This is only valid for the last 3 month period!!! FIXME
        dict: A dictionary containing weather station data for each 3-month period.
            This clearly has to be optimized!!! FIXME
    """
    data = Data(credentials=credentials)
    dt_middle = dt_start + timedelta(days=+365)
    df_weather = pd.DataFrame()
    all_wetaherstations = {}
    while dt_middle < dt_end:
        dict_closest = weatherstations_with_pref(
            df,
            owt_location,
            credentials=credentials,
            start_time=dt_start,
            end_time=dt_middle,
            prefered=prefered,
        )
        ids = list(dict_closest.values())
        dict_data = data.get(ids=ids, start_time=dt_start, end_time=dt_middle)
        df_weather = pd.concat([df_weather, get_weather_data(dict_data, df)])
        all_wetaherstations[dt_start] = get_weatherstation_information(
            df, dict_closest, information=information
        )
        dt_start = dt_middle
        dt_middle = dt_start + timedelta(days=+365)

    dict_closest = weatherstations_with_pref(
        df,
        owt_location,
        credentials=credentials,
        start_time=dt_start,
        end_time=dt_end,
        prefered=prefered,
    )
    weatherstation_information = get_weatherstation_information(
        df, dict_closest, information=information
    )
    ids = list(dict_closest.values())
    dict_data = data.get(ids=ids, start_time=dt_start, end_time=dt_end)
    df_weather = pd.concat([df_weather, get_weather_data(dict_data, df)])
    df_weather = df_weather[~df_weather.index.duplicated()]
    return df_weather, weatherstation_information, all_wetaherstations  # type: ignore


def prefered_in_description(
    row: pd.Series, prefered: list[str] = ["Thorntonbank", "Wandelaar", "Westhinder"]
):
    """Checks if a row's description contains any of the preferred weather station names.

    Args:
        row (pd.Series): A row from a DataFrame containing weather station data.
        prefered (list[str], optional): A list of preferred weather stations to check against.
            Defaults to ["Thorntonbank", "Wandelaar", "Westhinder"].

    Returns:
        bool: True if the weather station is in the preferred list, False otherwise.
    """
    for weatherstation in prefered:
        if weatherstation in row["Name"]:
            return True
    return False


def weatherstations_with_pref(
    df_unfiltered: pd.DataFrame,
    owt_location: list[float],
    credentials: Credentials,
    start_time: datetime,
    end_time: datetime,
    prefered: list[str] = ["Thorntonbank", "Wandelaar", "Westhinder"],
):
    """Filters weather stations based on proximity to the offshore wind turbine (OWT) location, 
    prioritizing preferred stations if they are available. Returns the closest station IDs for each parameter type.

    Args:
        df_unfiltered (pd.DataFrame): Unfiltered DataFrame of weather stations and parameters.
        owt_location (list[float]): The geographical coordinates of the offshore wind turbine.
        credentials (Credentials): User credentials to access the mvbc API.
        start_time (datetime): Start of the data collection period.
        end_time (datetime): End of the data collection period.
        prefered (list[str], optional): List of preferred weather stations. 
            Defaults to ["Thorntonbank", "Wandelaar", "Westhinder"].

    Returns:
        dict: A dictionary of the closest weather stations by parameter type.
    """
    prefered_idx = df_unfiltered.apply(
        lambda row: prefered_in_description(row, prefered=prefered),
        axis=1,
    )
    df_unfiltered_prefered = df_unfiltered[prefered_idx]
    df_unfiltered_prefered_other = df_unfiltered[~prefered_idx]

    dict_closest_prefered = get_closest_availbale_weatherstation_by_param(
        df_unfiltered_prefered, owt_location, credentials, start_time, end_time
    )
    dict_closest_other = get_closest_availbale_weatherstation_by_param(
        df_unfiltered_prefered_other, owt_location, credentials, start_time, end_time
    )
    dict_closest = {**dict_closest_other, **dict_closest_prefered}
    return dict_closest


def get_weatherstation_information(
    df_unfiltered: pd.DataFrame,
    dict_closest: dict[str, str],
    information=["ParameterName", "Name", "Description", "ParameterUnit"],
):
    """Retrieves detailed information about the weather stations closest to the offshore wind turbine (OWT) 
    based on the specified parameter types.

    Args:
        df_unfiltered (pd.DataFrame): DataFrame containing weather station metadata.
        dict_closest (dict[str, str]): Dictionary mapping parameter types to the closest weather station IDs.
        information (list, optional): List of information fields to retrieve.
            Defaults to ["ParameterName", "Name", "Description", "ParameterUnit"].

    Returns:
        pd.DataFrame: A DataFrame containing the requested information about the closest weather stations.
    """
    weatherstation_information = df_unfiltered.loc[list(dict_closest.values())][
        information
    ]
    return weatherstation_information


def get_latitude_longitude(point_pos: str) -> tuple[float, float]:
    """Parses a position string from the mvbc API into latitude and longitude coordinates.

    Args:
        point_pos (str): A string containing the position in the format "POINT (Latitude Longitude)".

    Returns:
        tuple[float, float]: A tuple containing the latitude and longitude as floats.
    """
    # Clean up the string by removing parentheses and splitting by space
    clean_str = point_pos.replace("(", "").replace(")", "").strip()
    # Split the cleaned string into latitude and longitude
    _ , lat_str, lon_str = clean_str.split(" ")
    # Convert the strings to floats and return as a tuple
    return (float(lat_str), float(lon_str))


def get_closest_weatherstation(df: pd.DataFrame, owt_position: list[float]) -> str:
    """Identifies the closest weather station to a given offshore wind turbine (OWT) location.

    Args:
        df (pd.DataFrame): DataFrame of weather stations and their geographical positions.
        owt_position (list[float]): The coordinates of the offshore wind turbine (Latitude, Longitude).

    Returns:
        str: The ID of the closest weather station.
    """
    owt_position_calc = owt_position[0], owt_position[1]
    df_dist = df.apply(
        lambda row: geopy.distance.geodesic(
            owt_position_calc, get_latitude_longitude(row["PositionWKT"])
        ).km,
        axis=1,
    )
    closest = df_dist.idxmin()
    return closest  # type: ignore


def separate_by_parameter(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Separates the weather station data into different groups based on parameter types.

    Args:
        df (pd.DataFrame): DataFrame of weather station data.

    Returns:
        dict[str, pd.DataFrame]: A dictionary where the keys are parameter types and 
            the values are DataFrames containing data for each parameter type.
    """
    dict_df = {}
    for param in df["Parameter"].unique():
        dict_df[param] = df[df["Parameter"] == param]
    return dict_df


def get_closest_weatherstation_by_param(
    df: pd.DataFrame, owt_position: list[float]
) -> dict[str, str]:
    """Finds the closest weather station for each parameter type based on proximity to the 
    offshore wind turbine (OWT) location.

    Args:
        df (pd.DataFrame): DataFrame of weather stations grouped by parameter types.
        owt_position (list[float]): The coordinates of the offshore wind turbine (Latitude, Longitude).

    Returns:
        dict[str, str]: A dictionary mapping parameter types to the IDs of the closest weather stations.
    """
    dict_closest_by_param = {}
    dict_df = separate_by_parameter(df)
    for key, value in dict_df.items():
        dict_closest_by_param[key] = get_closest_weatherstation(value, owt_position)
    return dict_closest_by_param


def get_unavailable(dict_data: dict[str, Any]) -> list[str]:
    """Identifies weather stations for which no data is available.

    Args:
        dict_data (dict[str, Any]): The raw data extracted from the mvbc API for a single weather station ID.

    Returns:
        list[str]: A list of weather station IDs for which no data is available.
    """
    unavailable = []
    for values in dict_data["Values"]:
        if not values["Values"]:
            id_ = values["ID"]
            unavailable.append(id_)
    return unavailable


def get_closest_availbale_weatherstation_by_param(
    df: pd.DataFrame,
    owt_location: list[float],
    credentials: Credentials,
    start_time: datetime,
    end_time: datetime,
) -> dict[str, str]:
    """Identifies the closest weather station for each parameter type that has available data 
    in the specified time period.

    Args:
        df (pd.DataFrame): DataFrame of weather stations grouped by parameter types.
        owt_location (list[float]): The coordinates of the offshore wind turbine (Latitude, Longitude).
        credentials (Credentials): User credentials for accessing the mvbc API.
        start_time (datetime): The start of the data collection period.
        end_time (datetime): The end of the data collection period.

    Returns:
        dict[str, str]: A dictionary mapping parameter types to the IDs of the closest weather stations with available data.
    """
    dict_closest = get_closest_weatherstation_by_param(df, owt_location)
    data = Data(credentials=credentials)
    ids = list(dict_closest.values())
    dict_data = data.get(ids=ids, start_time=start_time, end_time=end_time)
    unavailable = get_unavailable(dict_data)
    while len(unavailable) > 0:
        unavailable_param = df["Parameter"][df.index.isin(unavailable)].tolist()
        for param in unavailable_param:
            dict_closest.pop(param)
        df = df[df["Parameter"].isin(list(unavailable_param))].drop(unavailable)
        dict_closest_unavailable = get_closest_weatherstation_by_param(df, owt_location)
        new_ids = list(dict_closest_unavailable.values())
        dict_data_unavailable = data.get(
            ids=new_ids, start_time=start_time, end_time=end_time
        )
        if dict_data_unavailable["Values"]:
            unavailable = get_unavailable(dict_data_unavailable)
        else:
            unavailable = []
        dict_closest.update(dict_closest_unavailable)
    return dict_closest


def get_data_by_weatherstation(
    weather_station: str,
    dt_start: datetime,
    dt_end: datetime,
    credentials: Credentials,
    df_unfiltered: pd.DataFrame,
):
    """Retrieves weather data for a specific weather station over the given time period.

    Args:
        weather_station (str): The name of the weather station (e.g., "Wandelaar").
        dt_start (datetime): The start of the data collection period.
        dt_end (datetime): The end of the data collection period.
        credentials (Credentials): User credentials for accessing the mvbc API.
        df_unfiltered (pd.DataFrame): DataFrame containing metadata about available weather data points.

    Returns:
        pd.DataFrame: A DataFrame containing the weather data for the specified weather station.
    """
    data = Data(credentials=credentials)
    dt_middle = dt_start + timedelta(days=+365)
    df_weather = pd.DataFrame()

    weather_station_ids = list(
        df_unfiltered[df_unfiltered["Name"].str.contains(weather_station)].index
    )
    while dt_middle < dt_end:
        dict_data = data.get(
            ids=weather_station_ids, start_time=dt_start, end_time=dt_middle
        )
        df_weather = pd.concat([df_weather, get_weather_data(dict_data, df_unfiltered)])
        dt_start = dt_middle
        dt_middle = dt_start + timedelta(days=+365)

    dict_data = data.get(ids=weather_station_ids, start_time=dt_start, end_time=dt_end)
    df_weather = pd.concat([df_weather, get_weather_data(dict_data, df_unfiltered)])
    df_weather = df_weather[~df_weather.index.duplicated()]
    return df_weather
