import pytest
from unittest.mock import patch
import requests
from src.wheather_api_integration import parse_place, get_weather, create_weather_description, get_current_weather, get_near_future_forecast

def test_parse_place_with_none():
    place_text = 'Boulder, Colorado, None'
    expected_result = ('Boulder', 'Colorado', None)
    result = parse_place(place_text)
    assert result == expected_result

def test_create_weather_description_without_rain_or_snow():
    weather_dict = {
        'weather': [{'description': 'clear sky'}],
        'main': {'temp': 20, 'humidity': 60, 'feels_like':22},
        'wind': {'speed': 2.0},
        'name': 'Boulder',
        'clouds': {'all': 0},
        'wind': {'speed': 0.8}
    }

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = weather_dict

        result = create_weather_description(weather_dict, units='metric')

        assert not 'rain' in result
        assert not 'snow' in result

def test_create_weather_description_with_rain_and_snow():
    weather_dict = {
        'weather': [{'description': 'clear sky'}],
        'main': {'temp': 20, 'humidity': 60, 'feels_like':22},
        'wind': {'speed': 2.0},
        'name': 'Boulder',
        'clouds': {'all': 0},
        'wind': {'speed': 0.8},
        'snow': {'1h':3.5},  # Adding snow data
        'rain': {'1h': 5.5},  # Adding rain data
    }

    result = create_weather_description(weather_dict, units='metric')
    assert 'snow' in result
    assert 'rain' in result

def test_create_weather_description_with_metric_units():
    weather_dict = {
        'weather': [{'description': 'clear sky'}],
        'main': {'temp': 20, 'humidity': 60, 'feels_like':22},
        'wind': {'speed': 2.0},
        'name': 'Boulder',
        'clouds': {'all': 0},
        'wind': {'speed': 0.8}
    }

    result = create_weather_description(weather_dict, units='metric')
    assert 'degrees Celsius' in result

@patch('src.wheather_api_integration.get_weather')
def test_get_current_weather_error(mock_get_weather):
    mock_get_weather.side_effect = Exception('Mock error occurred')
    result = get_current_weather('Havana', 'CU', None)
    mock_get_weather.assert_called_once_with('Havana', 'CU', None, 'metric')
    assert result == 'No information available'

@patch('src.wheather_api_integration.get_forecast')
def test_get_forecast_error(mock_get_forecast):
    mock_get_forecast.side_effect = Exception('Mock error occurred')
    result = get_near_future_forecast('Havana', 'CU', None)
    mock_get_forecast.assert_called_once_with('Havana', 'CU', None, 'metric', 40)
    assert result == 'No information available'

