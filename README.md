
# MVBC (Meetnet Vlaamse Banken Client)

The `mvbc` package is a Python client to interact with the **Meetnet Vlaamse Banken API**. This package provides easy access to public weather data from the Belgian North Sea directly, and it returns the data in a pandas DataFrame format, making it convenient for further analysis.

## Getting Started

### 1. Create an Account

To use the Meetnet Vlaamse Banken API, you first need to create an account and get credentials:

1. Go to the [Meetnet Vlaamse Banken registration page](https://meetnetvlaamsebanken.be/account/register?signin=37ffaa0bfd8682563a8290c0d73f7f95).
2. Once registered, you will obtain your `MEETNET_USERNAME` and `MEETNET_PASSWORD`.

### 2. Set Credentials as Environment Variables

For best security practices, store your credentials in environment variables. You can set them as follows in your terminal:

```bash
export MEETNET_USERNAME="your_username"
export MEETNET_PASSWORD="your_password"
```

### 3. Install the Package

You can install the `mvbc` package via pip:

```bash
pip install mvbc
```

### 4. Using the Package

Once you have the package installed, you can start using it to retrieve weather data. Below is an example on how to use the package to fetch data.

```python
import mvbc

# Initialize the client
client = mvbc.Client(username="MEETNET_USERNAME", password="MEETNET_PASSWORD")

# Get weather data
df_weather = client.get_weather_data()

# Display the weather data
print(df_weather)

# You can also retrieve unfiltered data and weather station information
df_unfiltered = client.get_weather_station_info()
print(df_unfiltered)
```

### 5. Available Data Format

The weather data is returned as a **pandas DataFrame** (`df_weather`) with the timestamps in the rows and columns in the format:

```text
mvbc_<weather station>_<Parameter Name>
```

For example, you might see columns such as:

```text
mvbc_Thorntonbank_WindSpeed
mvbc_Wandelaar_Temperature
mvbc_Westhinder_WaveHeight
```

### 6. Data and Weather Stations

The additional information about available weather stations and data can be accessed via the `df_unfiltered` DataFrame. This provides you with metadata about the stations and available parameters.

### 7. Getting Data by Weather Station or Location

There are two main ways to retrieve data:

1. **By Weather Station Name**: You can directly specify the name of the weather station to get data.
   
2. **By Asset Location**: You can provide the location (latitude, longitude) of your asset (e.g., an offshore wind turbine) at sea, and the package will fetch data from the closest weather station.

Example of getting data by location:

```python
# Specify the latitude and longitude of your asset (e.g., offshore wind turbine)
latitude = 51.5
longitude = 2.5

# Get weather data for the closest station to this location
df_weather_closest = client.get_weather_data_by_location(latitude, longitude)
print(df_weather_closest)
```

### 8. Using Preferred Weather Stations

You can also set a list of **preferred** weather stations to prioritize fetching data from. The default preferred stations are:

- Thorntonbank
- Wandelaar
- Westhinder

You can provide your own list of preferred stations as follows:

```python
preferred_stations = ["Westhinder", "Nieuwpoort"]
df_preferred = client.get_weather_data(preferred_stations=preferred_stations)
print(df_preferred)
```

## Example Usage

For a full usage example, check out the provided Jupyter notebook (`mvbc_tutorial.ipynb`) which showcases different ways of fetching data, including using preferred weather stations and fetching data by location.