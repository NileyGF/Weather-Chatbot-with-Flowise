import pytest
from unittest.mock import patch
import streamlit as st
from streamlit.testing.v1 import AppTest
from src.app import *
import os

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(TEST_DIR) 
SRC_DIR = os.path.join(BASE_DIR, 'src')
app_path = os.path.join(SRC_DIR, 'app.py')

def test_reset_conversation_button_clicked():
    # Initialize the simulated app and execute the first script run
    at = AppTest.from_file(app_path).run()
    at.button(key="reset").click().run()
    assert at.session_state.messages == []

# def test_empty_response():
#     # Initialize the simulated app and execute the first script run
#     at = AppTest.from_file(app_path).run()
#     with patch('src.app.new_msg', return_value='') as mock_new_msg:
#         at.chat_input[0].set_value("Hello").run()
#         assert error_msg in at.session_state.messages[-1]['content']

# def test_empty_chat_input_stops_application():
#     at = AppTest.from_file(app_path).run()
#     at.chat_input[0].set_value("").run()
#     # assert at.chat_input[0].called
#     # assert at.stop.called


def test_streamlit_initialization():
    at = AppTest.from_file(app_path).run()
    assert 'messages' in at.session_state
    assert len(at.session_state.messages) == 0
