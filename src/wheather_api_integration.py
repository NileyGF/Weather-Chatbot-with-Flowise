import requests
from datetime import datetime
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()
OpenWeatherMap_API = os.getenv('OPEN_WEATHER_MAP_API')

def get_weather(city_name, country_code=None, state_code=None, units='metric'):
    if country_code and state_code:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name},{state_code},{country_code}&appid={OpenWeatherMap_API}&units={units}"
    elif country_code:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name},{country_code}&appid={OpenWeatherMap_API}&units={units}"
    else:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OpenWeatherMap_API}&units={units}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching weather data: {response.status_code} - {response.text}")
    
    return response.json()
    
def create_weather_description(weather_dict, units='metric'):
    if units == "standard":
        temp_unit = "degrees Kelvin"
    elif units == "metric":
        temp_unit = "degrees Celsius"
    elif units == "imperial":
        temp_unit = "degrees Fahrenheit"
    if units == "imperial":
        wind_unit = "mph"
    else:
        wind_unit = "m/s"
    weather_subset = {}
    weather_subset['city'] = weather_dict['name']
    weather_subset['weather description'] = weather_dict['weather'][0]['description']
    weather_subset['temp'] = f"{weather_dict['main']['temp']}  {temp_unit}"
    weather_subset['feels like'] = f"{weather_dict['main']['feels_like']} {temp_unit}"
    weather_subset['humidity'] = f"{weather_dict['main']['humidity']} %"
    weather_subset['clouds'] = f"{weather_dict['clouds']['all']} %"
    weather_subset['wind speed'] = f"{weather_dict['wind']['speed']} {wind_unit}"

    if weather_dict.get('rain'):
        if weather_dict['rain'].get('1h'):
            weather_subset['rain accumulation in 1h'] = f"{weather_dict['rain']['1h']} mm"
        if weather_dict['rain'].get('3h'): 
            weather_subset['rain accumulation in 3h'] = f"{weather_dict['rain']['3h']} mm"
    if weather_dict.get('snow'):
            if weather_dict['snow'].get('1h'):
                weather_subset['snow accumulation in 1h'] = f"{weather_dict['snow']['1h']} mm"
            if weather_dict['snow'].get('3h'):
                weather_subset['snow accumulation in 3h'] = f"{weather_dict['snow']['1h']} mm"

    return str(weather_subset)

def get_forecast(city_name, country_code=None, state_code=None, units='metric', n_records=40):
    if country_code and state_code:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name},{state_code},{country_code}&cnt={n_records}&appid={OpenWeatherMap_API}&units={units}"
    elif country_code:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name},{country_code}&cnt={n_records}&appid={OpenWeatherMap_API}&units={units}"
    else:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&cnt={n_records}&appid={OpenWeatherMap_API}&units={units}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching forecast data: {response.status_code} - {response.text}")
    
    return response.json()

def create_forecast_description(forecast_dict, units='metric'):
    if units == "standard":
        temp_unit = "degrees Kelvin"
    elif units == "metric":
        temp_unit = "degrees Celsius"
    elif units == "imperial":
        temp_unit = "degrees Fahrenheit"
    if units == "imperial":
        wind_unit = "mph"
    else:
        wind_unit = "m/s"
    weather_subset = {}
    weather_subset['city'] = forecast_dict['city']['name']
    weather_subset['amount of days in forecast'] = forecast_dict['cnt']

    weather_subset['list'] = []
    daily_averages = {}
    for i, day in enumerate(forecast_dict['list']):
        date_str = day['dt_txt'].split(' ')[0]
        time_str = day['dt_txt'].split(' ')[1]
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        if date_obj not in daily_averages:
            daily_averages[date_obj] = {
                # 'day': 0,
                'day': date_obj,
                'temp': [],
                'feels_like': [],
                'humidity': [],
                'clouds': [],
                'wind': [],
                'weather descriptions for the day': []
            }
        # Append the values for averaging
        daily_averages[date_obj]['temp'].append(day['main']['temp'])
        daily_averages[date_obj]['feels_like'].append(day['main']['feels_like'])
        daily_averages[date_obj]['humidity'].append(day['main']['humidity'])
        daily_averages[date_obj]['clouds'].append(day['clouds']['all'])
        daily_averages[date_obj]['wind'].append(day['wind']['speed'])
        daily_averages[date_obj]['weather descriptions for the day'].append(f"{time_str[:-3]}: {day['weather'][0]['description']}")
        
        if day.get('rain'):
            rain = day['rain']
            daily_averages[date_obj]['rain'] = {}
            if rain.get('1h'):
                if not daily_averages[date_obj]['rain'].get('1h'):
                    daily_averages[date_obj]['rain']['1h'] = []
                daily_averages[date_obj]['rain']['1h'].append(rain['1h']) 
            if rain.get('3h'):
                if not daily_averages[date_obj]['rain'].get('3h'):
                    daily_averages[date_obj]['rain']['3h'] = []
                daily_averages[date_obj]['rain']['3h'].append(rain['3h'])   
        if day.get('snow'):
            snow = day['snow']
            daily_averages[date_obj]['snow'] = {}
            if snow.get('1h'):
                if not daily_averages[date_obj]['snow'].get('1h'):
                    daily_averages[date_obj]['snow']['1h'] = []
                daily_averages[date_obj]['snow']['1h'].append(snow['1h'])
            if snow.get('3h'):
                if not daily_averages[date_obj]['snow'].get('3h'):
                    daily_averages[date_obj]['snow']['3h'] = []
                daily_averages[date_obj]['snow']['3h'].append(snow['3h'])
        
    for i, (date, metrics) in enumerate(daily_averages.items()):
        avg = {}
        avg['day'] = (date.date()).strftime('%A %Y-%m-%d')
        avg['weather descriptions for the day'] = ' | '.join(metrics['weather descriptions for the day'])
        avg['avg_temp'] = f"{round(np.mean(metrics['temp']), 1)} {temp_unit}"
        avg['avg_feels_like'] = f"{round(np.mean(metrics['feels_like']), 1)} {temp_unit}"
        avg['avg_humidity'] = f"{round(np.mean(metrics['humidity']), 1)} %"
        avg['avg_clouds'] = f"{round(np.mean(metrics['clouds']), 1)} %"
        avg['avg_wind'] = f"{round(np.mean(metrics['wind']), 1)} {wind_unit}"
        # TODO change the verbose of the rain
        if metrics.get('rain'):
            if metrics['rain'].get('1h'):
                avg['rain accumulation in 1h'] = f"{round(np.mean(metrics['rain']['1h']), 1)} mm"
            if metrics['rain'].get('3h'): 
                avg['rain accumulation in 3h'] = f"{round(np.mean(metrics['rain']['3h']), 1)} mm"
        if metrics.get('snow'):
            if metrics['snow'].get('1h'):
                avg['snow accumulation in 1h'] = f"{round(np.mean(metrics['snow']['1h']), 1)} mm"
            if metrics['snow'].get('3h'):
                avg['snow accumulation in 3h'] = f"{round(np.mean(metrics['snow']['3h']), 1)} mm"
        
        weather_subset['list'].append(avg)

    return str(weather_subset)


def get_current_weather(city_name, country_code, state_code):
    try:
        if city_name == None:
            return "No place provided"
        weather_data = get_weather(city_name, country_code, state_code, 'metric')
        text_weather = create_weather_description(weather_data, 'metric')
        return text_weather
    except Exception as e:
        print(f"An error occurred while consulting OpenWeatherMap API: {e}") 
        return 'No information available'

def get_near_future_forecast(city_name, country_code, state_code, n_records=40):
    try:
        if city_name == None:
            return "No place provided"
        forecast_data = get_forecast(city_name, country_code, state_code, 'metric', n_records)
        text_weather = create_forecast_description(forecast_data, 'metric')
        return text_weather
    except Exception as e:
        print(f"An error occurred while consulting OpenWeatherMap API: {e}") 
        return 'No information available'

def parse_place(place_text:str):
    elements = [element.strip() for element in place_text.split(',')]
    if len(elements) != 3:
        raise ValueError("The input string must contain exactly three elements.")
    parsed_values = [None if element == 'None' else element for element in elements]

    return tuple(parsed_values)

