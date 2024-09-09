import requests
import time
from datetime import datetime, timedelta
import csv
import os
from dotenv import load_dotenv

csv_filename = "GHCND_from_23-01_Boulder_CO.csv"

load_dotenv()
API_TOKEN = os.getenv('NCEI_API_KEY')
OpenWeatherMap_API = os.getenv('OPEN_WEATHER_MAP_API')
headers = { "token": API_TOKEN }

def get_daily_data():
    LAT = 40.0150
    LON = -105.2705
    for days_ago in range(365):
        date = datetime.now() - timedelta(days=days_ago)
        date_str = date.strftime("%Y-%m-%d")
        # timestamp = int(time.mktime(date.timetuple()))
        
        url = f'https://api.openweathermap.org/data/2.5/onecall/day_summary?lat={LAT}&lon={LON}&date={date_str}&appid={API_TOKEN}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Weather data for {date.strftime('%Y-%m-%d')}:")
            print(data)
        else:
            print(f"Failed to retrieve data for {date.strftime('%Y-%m-%d')}: {response.status_code}")

def get_dataset_id():
    endpoint = "https://www.ncei.noaa.gov/cdo-web/api/v2/datasets"
    params = { }
    response = requests.get(endpoint, headers=headers, params=params)
    datasets = response.json().get('results', [])
    for dataset in datasets:
        get_location_id(dataset['id'])
    #     if 'CO' in location['name']:
    #         print(location)
    # return locations
def get_location_id(datasetid="NEXRAD2"):
    endpoint = "https://www.ncei.noaa.gov/cdo-web/api/v2/locations"
    params = { "datasetid": datasetid, "limit": 1000 }
    response = requests.get(endpoint, headers=headers, params=params)
    locations = response.json().get('results', [])
    for location in locations:
        # print(f"{datasetid} -> Name: {location['name']}")
        if 'Boulder' in location['name']:
            print(datasetid, location)
    return locations

def get_station_id(datasetid="NEXRAD2", locationid="CITY:US080001"):
    endpoint = "https://www.ncdc.noaa.gov/cdo-web/api/v2/stations"
    params = {
        "locationid": locationid,  
        "datasetid": datasetid,
        "limit": 5
    }

    response = requests.get(endpoint, headers=headers, params=params)
    stations = response.json().get('results', [])
    for station in stations:
        print(f"Station ID: {station['id']}, Name: {station['name']}")
        """
        Station ID: GHCND:US1COLP0002, Name: DURANGO 9.0 ESE, CO US
        Station ID: GHCND:US1COLP0004, Name: DURANGO 7.1 E, CO US
        Station ID: GHCND:US1COLP0005, Name: DURANGO 4.1 WSW, CO US
        Station ID: GHCND:US1COLP0006, Name: DURANGO 6.2 SE, CO US
        Station ID: GHCND:US1COLP0008, Name: DURANGO 4.9 ESE, CO US
        """
    return station['id']

def fetch_data(datasetid="GHCND", station_id="GHCND:USC00050848"):
    end_date = datetime.now()
    end_date_str = end_date.strftime("%Y-%m-%d")
    endpoint = f"https://www.ncei.noaa.gov/cdo-web/api/v2/datasets/{datasetid}"
    params = {
        # "datasetid": datasetid,
        "stationid": station_id,
        "startdate": '2023-01-01',
        "enddate": end_date_str,
        'datatypeid': 'PRCP', #['TMAX', 'TMIN', 'PRCP'],
        "limit": 600,  
        "units": "metric"
    }

    response = requests.get(endpoint, headers=headers, params=params)
    # print(response.json())
    if response.status_code == 200:
        weather_data = response.json().get('results', [])
        # print(response.status_code)
        
        for data in weather_data:
            for observation in data:
                date = observation['date']
                tmax = observation['value'] if observation['datatype'] == 'TMAX' else None
                tmin = observation['value'] if observation['datatype'] == 'TMIN' else None
                prcp = observation['value'] if observation['datatype'] == 'PRCP' else None
                print(date, prcp, tmin, tmax)
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=weather_data[0].keys())
            writer.writeheader()
            writer.writerows(weather_data)

        print(f"Data saved to {csv_filename}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# fetch_data()