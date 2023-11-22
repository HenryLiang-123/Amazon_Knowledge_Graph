########################################
# Importing relevant packages
########################################
import os
import pathlib
import logging
import sys
import base64
import neo4j
from configparser import ConfigParser

import streamlit as st
from src.create_database import get_data, create_graph

########################################
# main
########################################

# Setting config file 
config_file = 'config/config.ini'
configur = ConfigParser()
configur.read(config_file)

print("Let's create the database.")

st.title("Let's create the database.")
st.write("Please ensure that your data is in the repository.")
st.write("Please ensure that your data path is set correctly in the configuration.")

file_path = configur.get('create_database', 'file_path')

if st.button("Create database."):
    # Get data from source
    data = get_data(file_path=file_path)

    # Getting neo4j credentials
    uri = configur.get('neo4j-graph', 'uri')
    username = configur.get('neo4j-graph', 'username')
    password = configur.get('neo4j-graph', 'password')

    # Connect to neo4j database
    driver = neo4j.GraphDatabase.driver(uri, auth=(username, password))

    # Create database
    with driver.session() as session:
        for line in data:
            from_node_id, to_node_id = map(int, line)
            session.write_transaction(create_graph, from_node_id, to_node_id)
    st.write("You have successfully loaded your dataset.")
    print("You have successfully loaded your dataset.")
    driver.close()
else:
    print("You have gotten an error while trying to create database.")
    st.write("You have gotten an error while trying to create database.")

