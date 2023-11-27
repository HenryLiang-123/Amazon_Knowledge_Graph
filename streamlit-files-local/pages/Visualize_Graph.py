########################################
# Importing relevant packages
########################################
import os
import logging
import sys
import base64
from pathlib import Path
from configparser import ConfigParser

import streamlit as st

# adding src to the system path
sys.path.insert(0, os.getcwd())

from src.visualize_graph import visualize_graph

########################################
# main
########################################

st.set_page_config(
    page_title="Visualize your Social Network.",
    page_icon="📈",
)
st.sidebar.success("Let's visualize your Social Network.")

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
        # Send prompt to function
        response = execute_graph_operations(config_file, user_prompt, network_choice)

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