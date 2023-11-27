########################################
# Importing relevant packages
########################################
import os
import logging
import sys
import base64
import requests
from pathlib import Path
from configparser import ConfigParser

import streamlit as st

# adding src to the system path
sys.path.insert(0, os.getcwd())

########################################
# main
########################################

st.set_page_config(
    page_title="Go To Network Analytics",
    page_icon="👍",
)
st.sidebar.success("Let's understand the Social Network.")

# Setting config file 
config_file = None
try:
    config_file = 'config/config.ini'
    configur = ConfigParser()
    configur.read(config_file)
except Exception as err:
    print("Error in reading config file")
    print(err)

print("Let's perform some graph operations.")

st.title("Let's find about more about your social network.")
st.write("Please ensure that your data is in the repository.")
st.write("Please ensure that your data path is set correctly in the configuration.")

network_choice = st.selectbox("Please select the network you would like to analyse?", ["EU Communication Network", "BGP Networking Data"])

try:
    user_prompt = st.text_input("What would you like to know about the network?")
    if st.button("Get your answer."):
        # Prepare data packet for request
        data = {"user_prompt": user_prompt,
                "network_choice": network_choice}

        # Get url
        baseurl = configur.get('client', 'web-server')
        api = '/study_network'
        url = baseurl + api

        res = requests.post(url, json=data)

        response = res.json()
        print(res)
        print(response)

        if response['statusCode'] == 200:
            st.write(response["body"])
        else:
            st.write(response["body"])
        
    else:
        print("You have gotten an error while trying to study network.")
        st.write("You have gotten an error while trying to study network.")
except Exception as err:
    print("Error in graph operation")
    print(err)