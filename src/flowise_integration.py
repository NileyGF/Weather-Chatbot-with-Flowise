# from flowise import Flowise, PredictionData
# from flowise.client import FlowiseClientOptions
import requests
import os
from dotenv import load_dotenv
load_dotenv()
HF_API_KEY = os.getenv('HF_TOKEN') # Flowise-chatbot
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR) 
DATA_DIR = os.path.join(BASE_DIR, 'data')
historical_data_json = os.path.join(DATA_DIR, "GHCN-Daily-descriptions.json")

GEMINI_API_URL = "https://nileygf-flowise-for-weather-forecast-chatbot.hf.space/api/v1/prediction/ee45c6a2-ed3f-43c4-b0d9-a8e408e97e29"
OPENAI_API_URL = "https://nileygf-flowise-for-weather-forecast-chatbot.hf.space/api/v1/prediction/4afc5ec5-32aa-420c-8904-a23ed234c849"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}
# form_data = {
#     "files": ("GHCN-Daily-descriptions.json", open(historical_data_json, 'rb'))
# }


def query(payload, model='openai'):
    if model == 'openai':
        api_url = OPENAI_API_URL
    else:
        api_url = GEMINI_API_URL
    response = requests.post(api_url, headers=headers, json=payload) # files=form_data, headers=headers, 
    if response.status_code != 200:
        raise Exception(f"Error accessing Flowise chatflows: {response.status_code} - {response.text}")
    # print(response, response.status_code, response.text)
    return response.json()

def identify_place(user_input, history, model='openai'):
    if model == 'openai':
        api_url = "https://nileygf-flowise-for-weather-forecast-chatbot.hf.space/api/v1/prediction/4c7bce72-4dc5-4111-b649-aca9fe0b9f00"
    else:
        api_url = "https://nileygf-flowise-for-weather-forecast-chatbot.hf.space/api/v1/prediction/ef49a6a5-2774-4bf4-9aaf-2fa4f97595fc"
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    place_prompt = """The expected output is a comma separated list with the values for `city_name`, `country_code` and `state_code` in that order. Please note that searching by states is available only for the USA locations.

Example for user input = Is raining today in Paris?:
Paris, None, None
or
Paris, FR, None
Example for user input = How's the humidity in Boulder, CO?:
Boulder, USA, CO

If the information contains a country, but not the city then the value of  `city_name` must be the capital of the country.
Example, if they mention Cuba, the answer can be:
Havana, CU, None

If the are not cities mentioned, then `city_name` must be `None`. 
Example:
None, None, None

Given the following conversation and a follow up question, determine the place the user is refering to in the user input. If none is found just use the latest place in the chat history.
-------------
Chat History:
{history}
-----------
user input: {question}
-----------

place list:"""
    chat_history = ""
    for msg_dict in history:
        if msg_dict['role'] == 'userMessage':
            chat_history += f"userMessage: {msg_dict['content']}" 
        if msg_dict['role'] == 'apiMessage':
            chat_history += f"assistantMessage: {msg_dict['content']}"     
    place_prompt = place_prompt.format(history=chat_history, question=user_input)
    print("identify_place payload: ", place_prompt)

    payload = { "question": user_input,
                # "history": history,
                "overrideConfig": {
                    "temperature": 0.4,
                    "template": place_prompt,
                    # "promptValues": {
                    #     "history": history, 
                    #     "question": user_input
                    #     },
                    }
                }
    response = requests.post(api_url, headers=headers, json=payload) # files=form_data, headers=headers, 
    if response.status_code != 200:
        raise Exception(f"Error accessing Flowise chatflows: {response.status_code} - {response.text}")
    return response.json()['text']

def query_non_streaming(payload):
    client = Flowise(FlowiseClientOptions("https://nileygf-flowise-for-weather-forecast-chatbot.hf.space"))
    completion = client.create_prediction(
        PredictionData(
            chatflowId = "ee45c6a2-ed3f-43c4-b0d9-a8e408e97e29",
            streaming=False,
            **payload
        )
    )
    # Process and print the response
    for response in completion:
        # print("Non-streaming response:", response)
        return response
