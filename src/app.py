import os
import sys
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR) 
sys.path.append(str(SRC_DIR)) # src 
sys.path.append(str(BASE_DIR)) # project


import streamlit as st
from src.main import *

st.title("☁️ Nimb-bot ") # 🌨 💧 ❄️ ☁️ ☀️ 

if st.sidebar.button("Reset conversation", key="reset"):
    # chat_id = None
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state['messages']:
    with st.chat_message(msg['role']):
        st.write(msg['content'])

msg = st.chat_input("Ask your questions here.", key="input")

if not msg:
    st.stop()

def generate_answer():
    response = new_msg(st.session_state['messages'], msg)
    if not response:
        response = error_msg
        print(response)
    # Add chatbot response to messages history
    st.session_state['messages'].append({'role': 'assistant', 'content': response})
    st.write(response)

with st.chat_message("user"):
    st.write(msg)

with st.chat_message("assistant"):
    if msg == "":
        response = error_msg
        st.write(response)
    else:
        st.session_state['messages'].append({'role': 'user', 'content': msg})
        with st.spinner("Generating answer..."):
            generate_answer()

        
