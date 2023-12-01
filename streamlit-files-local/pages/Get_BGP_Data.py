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
print(os.getcwd())

from src.create_bgp_database import create_bgp_graph

########################################
# main
########################################

st.set_page_config(
    page_title="Collect Today's BGP Data",
    page_icon=":bar_chart:",
)
st.sidebar.success("BGP Database Set-Up and Creation.")

# Setting config file 
try:
    config_file = 'config/config.ini'
    configur = ConfigParser()
    configur.read(config_file)
except Exception as err:
    print("Error in reading config file")
    print(err)


print("Let's create the database.")

st.title("Let's create the database.")
st.write("Please ensure that your data is in the repository.")
st.write("Please ensure that your data path is set correctly in the configuration.")

network = st.selectbox("Please select the network you would like to analyse?", ["BGP Networking Data"])

try:
    bgp_url = None
    if network == "BGP Networking Data":
        # Get BGP URL
        bgp_url = configur.get('create_database', 'bgp_url')

        # Get neo4j credentials
        uri = configur.get('bgp-graph', 'uri')
        username = configur.get('bgp-graph', 'username')
        password = configur.get('bgp-graph', 'password')
except Exception as err:
    print("Error in looking at file path")
    print(err)

print(bgp_url)

try:
    if st.button("Create database."):
        # Create database
        db_create = create_bgp_graph(bgp_url=bgp_url, graph_uri=uri, username=username, password=password, output_path=Path("data"))

        if db_create['statusCode'] == 200:
            st.write("You have successfully loaded your dataset.")
        else:
            st.write(db_create["body"])
        
    else:
        print("You have gotten an error while trying to create database.")
        st.write("You have gotten an error while trying to create database.")
except Exception as err:
    print("Error in creating database")
    print(err)

