import src.wheather_api_integration as weather
import src.flowise_integration as flowise
from datetime import datetime
today = datetime.now().strftime('%A %Y-%m-%d')
"""You are a helpful AI assistant named Nimb-bot. You can access a variety of information about the historical weather in Boulder since last year 2023. You can also provide information about the current weather and the forecast for the upcoming days for any city in the world. If the user asks about an activity provide the weather information and analyse whether it can be done with said weather. 

Please attend the following user, according to the input.

user input: {{question}}

When you have the answer, create a text with it and return the result to the user."""
system_prompt = "You are a helpful AI assistant named Nimb-bot. You can access a variety of information about the historical weather in Boulder since last year 2023. You can also provide information about the current weather and the forecast for the upcoming days for any city in the world."+\
                f"\nIf the user asks about an activity provide the weather information and analyse whether it can be done with said weather."+\
                f"\nToday is {today}.\n\n" + "Please attend the following user, according to the input.\n\nuser input: {{question}}\n\nWhen you have the answer, create a text with it and return the result to the user."
# system_prompt = f"You are a helpful AI assistant named Nimb-bot. You can access a variety of information about the weather in Boulder. Today is {today}"
error_msg = 'Sorry, I am unable to process your request at the moment.'
def new_msg(history:list, user_input):
    try:
        change_role_history = []
        for msg_dict in history:
            role_change = {}
            if msg_dict['role'] == 'user':
                role_change['role'] = 'userMessage'
            if msg_dict['role'] == 'assistant':
                role_change['role'] = 'apiMessage'
            role_change['content'] = msg_dict['content']
            change_role_history.append(role_change)
        change_role_history = change_role_history[-4:] if len(change_role_history) >= 4 else change_role_history

        place = flowise.identify_place(user_input, change_role_history)
        print('place =', place)
        city_name, country_code, state_code = weather.parse_place(place)
        current_weather = get_current_weather_prompt(user_input, city_name, country_code, state_code)
        weather_forecast = get_weather_forecast_prompt(user_input, city_name, country_code, state_code)
        default_chat = get_default_chat_prompt(user_input)
        payload = { "question": user_input,
                    "history": change_role_history,
                    "overrideConfig": {
                        # "googleGenerativeAPIKey": flowise.GEMINI_API_KEY,
                        # "modelName": "gemini-1.5-flash-latest",
                        "temperature": 0.9,
                        "systemMessage": system_prompt,
                        "promptValues": {
                            "promptTemplate_0": default_chat[1],
                            "promptTemplate_1": current_weather[1],
                            "promptTemplate_2": weather_forecast[1],
                        },
                        "template": {
                            "promptTemplate_0": default_chat[0],
                            "promptTemplate_1": current_weather[0],
                            "promptTemplate_2": weather_forecast[0],
                        },
                        }
                    }
        print('request : ',current_weather, '\n')
        response = flowise.query(payload)
        print(response)
        return response['text']
    except Exception as e:
        print(f"An error occurred while consulting Flowise chatflows: {e}") 
        return None

def get_current_weather_prompt(user_input, city_name, country_code, state_code):
    try:
        current_weather = weather.get_current_weather(city_name, country_code, state_code)
        current_weather_prompt = "Weather information right now (today is {today}): \n```\n{current_weather}\n```\n"+\
            "Please attend the following user, according to the input and the information provided.\n\nuser input: {question}"
        template = {"current_weather": current_weather, "today": today, "question": user_input}
        # current_weather_prompt = current_weather_prompt.format(current_weather = current_weather, today = today, question = user_input)
        return current_weather_prompt, template
    except Exception as e:
        print(f"An error occurred while getting the info for current_weather: {e}") 
        return 'No information available', dict()
    
def get_weather_forecast_prompt(user_input, city_name, country_code, state_code):
    try:
        forecast = weather.get_near_future_forecast(city_name, country_code, state_code)
        forecast_prompt = "Weather information until the next days: \n```\n{forecast}\n```\n"+\
            "Please attend the following user, according to the input and the information provided.\n\nuser input: {question}"
        template = {"forecast": forecast, "question": user_input}
        # forecast_prompt = forecast_prompt.format(forecast = forecast, question = user_input)
        
        return forecast_prompt, template
    except Exception as e:
        print(f"An error occurred while getting the info for forecast: {e}") 
        return 'No information available', dict()

def get_default_chat_prompt(user_input):
    try:
        """Only provide the information that they ask you. 
        If the topic is not related to the weather, explain politely that you are Nimb-bot, a weather assistant for Boulder. 
        If you don't have enough information to answer, ask the user for more details that can help you answer better."""
        prompt = "Please attend the following user, according to the input. \n\nuser input: {question}"
        template = {"question": user_input } # "{{question}}"}
        return prompt, template 
    except Exception as e:
        print(f"An error occurred while getting the info for default chat: {e}") 
        return 'No information available', dict()
