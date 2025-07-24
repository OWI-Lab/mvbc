"""
mvbc objects
------------

This module provides classes to interact with the Meetnet Vlaamse Banken (mvbc) API using the mvbc package.
It allows you to access the full catalog of available data, including locations, parameters, and available data points, 
as well as to retrieve the most recent and historical data from the API.

The module contains the following key classes:
- `Catalog`: Retrieves and parses the metadata catalog from the API, including locations and parameters.
- `Data`: Extends the functionality of `Catalog` to allow querying and retrieving current and historical data.

Usage:
------

1. Initialize the `Catalog` class to retrieve details about available locations and parameters.
   Example:
   >>> catalog = Catalog()
   >>> locations = catalog.locations()

2. Use the `Data` class to fetch real-time or historical data.
   Example:
   >>> data = Data()
   >>> current_data = data.get_latest()
   >>> historical_data = data.get(ids=["parameter_id"], start_time="2024-01-01", end_time="2024-01-07")

Note:
-----
This module relies on the mvbc library to handle authentication and API interactions.

Authors:
--------
Daan Wilders
Maximillian Weil
"""

from datetime import datetime, timedelta
from typing import List, Optional
import warnings
import pandas as pd
import requests
from mvbc.client import Base


class Catalog(Base):
    """The catalog contains a description of all the data.

        This descriptions contains, customer details, a list of locations with details,
        a list of parameters with details and a list of available data (Location - Parameter Combinations).
        The CurrentInterval property in the Parameter description shows the current interval in minutes of the Data.
        This can change over time ,although this does not happen a lot.
        In the ProjectionWKT property the projection is defined of the geographical information used in the API.
        This uses the WKT (Well Known Text) Definitions.

    Args:
        Base (Base): Implements authentication and API systems verification (ping).
    """

    def __init__(self, culture: str = "en-GB", *args, **kwargs):
        """Initialise the Catalog.

        Args:
            culture (optional): Language to use from available cultures. Defaults to :code:`en-GB`.
                The other culture currently available is :code:`nl-BE`

        Attributes:
            catalog: The raw catlog in JSON format
            culture: Language chosen from available cultures. Possible values are :code:`en-GB`
                and :code:`nl-BE`
        """
        super().__init__(*args, **kwargs)
        self.catalog: str = self.get_catalog()
        self.culture: str = culture
        self.points: pd.DataFrame = None  # type: ignore

    def get_catalog(self) -> str:
        """Request catalog from API

        Download the complete catalog as raw JSON data
        - customer details
        - a list of locations with details
        - a list of parameters with details
        - a list of available data (Location - Parameter Combinations)

        Returns
            The complete catalog in raw JSON format.
        """
        url = self.url + "/V2/catalog"
        self.login()
        response = requests.get(url, auth=self.auth)
        if response.status_code != 200:
            raise Exception("Get Catalog failed")
        return response.json()

    def _unpack_culture(self, cultures):
        """Extract the message for the specified culture from a list of culture dictionaries.

        Args:
            cultures (list): List of dictionaries, each containing culture-specific messages.

        Returns:
            str: The message corresponding to the selected culture.
        """
        code = self.culture
        msg = next((c["Message"] for c in cultures if c["Culture"] == code), None)
        return msg

    def parameters(self) -> pd.DataFrame:
        """Retrieve a DataFrame containing details about available parameters.

        Returns:
            pd.DataFrame: A DataFrame with parameter details (e.g., name, type).
        """
        df = pd.DataFrame(self.catalog["Parameters"])  # type: ignore
        df["Name"] = df.Name.apply(self._unpack_culture)  # type: ignore
        df.drop(columns=["MinValue", "MaxValue"], inplace=True)
        df.rename(columns={"ParameterTypeID": "Type"}, inplace=True)
        df.set_index("ID", inplace=True)
        return df

    def locations(self) -> pd.DataFrame:
        """Retrieve a DataFrame containing details about available locations.

        Returns:
            pd.DataFrame: A DataFrame with location details (e.g., name, description).
        """
        df = pd.DataFrame(self.catalog["Locations"])  # type: ignore
        df["Name"] = df.Name.apply(self._unpack_culture)  # type: ignore
        df["Description"] = df.Description.apply(self._unpack_culture)  # type: ignore
        df.set_index("ID", inplace=True)
        return df

    def parameter_types(self) -> pd.DataFrame:
        """Retrieve a DataFrame containing different types of parameters.

        Returns:
            pd.DataFrame: A DataFrame listing parameter types.
        """
        df = pd.DataFrame(self.catalog["ParameterTypes"]).T  # type: ignore
        df.set_index("ID", inplace=True)
        df["Name"] = df.Name.apply(self._unpack_culture)  # type: ignore
        return df

    def available_data(self) -> pd.DataFrame:
        """Retrieve a DataFrame containing available data for different location-parameter combinations.

        Returns:
            pd.DataFrame: A DataFrame with available data combinations (Location and Parameter).
        """
        df = pd.DataFrame(self.catalog["AvailableData"])  # type: ignore
        df.set_index("ID", inplace=True)
        df.drop(columns=["Publications"], inplace=True)
        return df

    def data_points(self) -> pd.DataFrame:
        """Combines location, parameter, and available data into a single DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the combined information of locations, 
                          parameters, and available data.
        """
        if self.points:
            return self.points

        locations = self.locations()
        data = self.available_data()
        parameters = self.parameters()
        locations["Location"] = locations.index
        data["ID"] = data.index
        parameters = parameters.add_prefix("Parameter")
        parameters["Parameter"] = parameters.index
        df = locations.merge(data, on="Location")
        df = df.merge(parameters, on="Parameter")
        df.set_index("ID", inplace=True)
        # Store for reuse
        self.points = df
        return df

    def filter_parameter(
        self,
        type_=None,
        name=None,
    ) -> pd.DataFrame:
        """Filters data points by parameter type or name.

        Args:
            type_ (str, optional): The type of parameter to filter by.
            name (str, optional): The name of the parameter to filter by.

        Returns:
            pd.DataFrame: A DataFrame with the filtered data points.
        """
        df = self.points
        if df is None:
            df = self.data_points()
        if type_ is not None and name is not None:
            print(
                f"'type_' and 'name' filter passed together, using most specific -> '{name}'"
            )
        # Most specific first
        if name:
            return df[df.Parameter.eq(name)]  # type: ignore
        if type_:
            return df[df.ParameterType.eq(type_)]  # type: ignore
        print("Nothing filtered")
        return df


class Data(Catalog):
    """ Data class extends the Catalog to retrieve real-time or historical data points 
    from the mvbc API.

    Attributes:
        latest (str): Cached latest data from the API.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the Data class and fetch the latest data.
        """
        super().__init__(*args, **kwargs)
        self.latest: str = self.get_latest()

    def get_latest(self, ids: Optional[List[str]] = None):
        """Fetches the latest data for the given parameter IDs.

        Args:
            ids (Optional[List[str]]): List of parameter IDs to get data for. If None, 
                                       fetches all available data.

        Returns:
            dict: The latest data in JSON format.
        """
        url = self.url + "/V2/currentData"
        self.login()
        if ids is None:
            return requests.get(url, auth=self.auth).json()
        # Build request data
        data = {"IDs": ids}
        return requests.get(url, json=data, auth=self.auth).json()

    def get(self, ids, start_time=None, end_time=None):
        """Fetches historical data for the given parameter IDs within the specified time range.

        Args:
            ids (List[str]): List of parameter IDs to retrieve data for.
            start_time (datetime, optional): Start of the time range. Defaults to one week ago.
            end_time (datetime, optional): End of the time range. Defaults to current time.

        Returns:
            dict: Historical data in JSON format.

        Raises:
            Warning: If some IDs cannot retrieve data, a warning is issued.
        """
        # TODO: implement start, end and timedelta optional arguments
        url = self.url + "/V2/getData"
        if not start_time and not end_time:
            end_time = datetime.now()
            start_time = end_time - timedelta(weeks=1)
        data = {"IDs": ids, "StartTime": start_time, "EndTime": end_time}
        dict_data = requests.post(url, data, auth=self.auth).json()
        if "Values" not in dict_data:
            final_ids = []
            pop_ids = ids.copy()
            for count, value in enumerate(ids):
                test_ids = pop_ids.pop(count)
                pop_ids = ids.copy()
                data_test = {
                    "IDs": test_ids,
                    "StartTime": start_time,
                    "EndTime": end_time,
                }
                test_dict_data = requests.post(url, data_test, auth=self.auth).json()
                if "Values" in test_dict_data:
                    final_ids.append(value)
                else:
                    warnings.warn(f"Can't get data from {value}")  # type: ignore
            data = {"IDs": final_ids, "StartTime": start_time, "EndTime": end_time}
            dict_data = requests.post(url, data, auth=self.auth).json()
        return dict_data
