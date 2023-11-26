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

from src.create_database import get_data, add_nodes_edges, create_graph

########################################
# main
########################################

st.set_page_config(
    page_title="Go To Get Data",
    page_icon=":bar_chart:",
)
st.sidebar.success("Database Set-Up and Creation.")

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

network = st.selectbox("Please select the network you would like to analyse?", ["EU Communication Network"])

try:
    file_path = None
    if network == "EU Communication Network":
        # Get file path
        file_path = configur.get('create_database', 'eu_path')

        # Get neo4j credentials
        uri = configur.get('eu-neo4j-graph', 'uri')
        username = configur.get('eu-neo4j-graph', 'username')
        password = configur.get('eu-neo4j-graph', 'password')
except Exception as err:
    print("Error in looking at file path")
    print(err)

print(file_path)

try:
    if st.button("Create database."):
        # Get data from source
        data = get_data(file_path=Path(file_path))

        # Create database
        db_create = create_graph(uri, username, password, data)

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

