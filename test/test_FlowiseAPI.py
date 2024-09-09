import pytest
from unittest.mock import patch
from dotenv import load_dotenv
from src.main import new_msg
from src.flowise_integration import query

load_dotenv()  # take environment variables from .env

@patch('src.flowise_integration.query')
def test_new_msg_success(mock_query):
    mock_query.return_value = {'text': 'Hello!'}
    history = []
    user_input = "Hi"
    response = new_msg(history, user_input)
    assert response == 'Hello!'

@patch('src.flowise_integration.query')
def test_new_msg_failure(mock_query):
    mock_query.side_effect = Exception("API failure")
    history = []
    user_input = "Hi"
    response = new_msg(history, user_input)
    assert response is None


@patch('requests.post')
def test_query_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'text': 'Hello!'}
    
    payload = {'question': 'Hi'}
    response = query(payload)
    assert response == {'text': 'Hello!'}

@patch('requests.post')
def test_query_failure(mock_post):
    mock_post.return_value.status_code = 500
    payload = {'question': 'Hi'}
    
    with pytest.raises(Exception):
        query(payload)