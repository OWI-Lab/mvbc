
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

# If you are using environmental variables
mvbc_username = os.getenv('MEETNET_USERNAME') # Replace with your usernam
mvbc_password = os.getenv('MEETNET_PASSWORD') # Replace with your password

# Use the credentials
creds = Credentials(username=mvbc_username, password=mvbc_password)
b=Base(creds)
b.ping()

# Specify the timeframe of interest
dt_start = datetime(2022,9,30,tzinfo=utc) # timestamp with timezone
dt_end = datetime(2022,10,1,tzinfo=utc)

# Get the information about the avialble data points
c = Catalog(credentials=creds)
df_unfiltered = c.data_points()
print(df_unfiltered)
```

The `df_unfiltered` DataFrame contains the information about the available data and the weather stations.

There are two main ways to retrieve data:

1. **By Weather Station Name**: You can directly specify the name of the weather station to get data.

```python
weather_station = 'Wandelaar'
df_weather = \
    dg.get_data_by_weatherstation(
        weather_station,
        dt_start,
        dt_end,
        creds,
        df_unfiltered
    )
```

2. **By Asset Location**: You can provide the location (latitude, longitude) of your asset (e.g., an offshore wind turbine) at sea, and the package will fetch data from the closest weather station.

```python
# Replace this with location of interest in the from of [Latitude, Longitude]

location_of_interest = [2.81555595289144, 51.6918319416294]   
df_weather, weatherstation_information, all_wetaherstations = dg.get_longterm_weather_data(location_of_interest, dt_start, dt_end, df=df_unfiltered, credentials=creds)
# Data comes in for every 30min, but you can resample to the time you want (e.g. 10 minutes)
df_weather = df_weather.resample('10T', axis=0).interpolate(method='linear', axis=0, limit=12)
```

### 5. Available Data Format

The weather data is returned as a **pandas DataFrame** (`df_weather`) with the timestamps in the rows and columns in the format:

```text
mvbc_<weather station>_<Parameter Name>
```

For example, you might see columns such as:

```text
mvbc_Thorntonbank_Wind_speed
mvbc_Wandelaar_Temperature
mvbc_Westhinder_Wave_height
```

### 6. Data and Weather Stations

The additional information about available weather stations and data can be accessed via the `df_unfiltered` DataFrame. This provides you with metadata about the stations and available parameters.

### 7. Using Preferred Weather Stations

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