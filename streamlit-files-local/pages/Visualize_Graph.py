########################################
# Importing relevant packages
########################################
import os
import logging
import sys
import base64
from pathlib import Path
from configparser import ConfigParser
from PIL import Image

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

print("Let's visualize the network.")

st.title("Let's visualize the network.")
st.write("Please ensure that your data is in the repository.")
st.write("Please ensure that your data path is set correctly in the configuration.")

network_choice = st.selectbox("Please select the network you would like to analyse?", ["BGP Networking Data"])

try:
    num_records = int(st.number_input("How many records do you want to visualize?", placeholder="Please enter a non-negative number.", step=1, format="%d"))
    if st.button("Visualize the network."):
        # Send prompt to function
        response = visualize_graph(config_file, network_choice, num_records, Path("plots"))

        if response['statusCode'] == 200:
            st.write(response["body"])
            image = Image.open(Path("plots") / f"neo4j_graph_{network_choice}.png")
            st.image(image, caption=f"Visualisation of network: {network_choice}")
        else:
            st.write(response["body"])
        
    else:
        print("You have gotten an error while trying to study network.")
        st.write("You have gotten an error while trying to study network.")
except Exception as err:
    print("Error in graph operation")
    print(err)