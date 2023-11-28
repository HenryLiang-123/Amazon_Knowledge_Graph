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
import matplotlib.pyplot as plt
import matplotlib.image as img
from PIL import Image

import streamlit as st

# adding src to the system path
sys.path.insert(0, os.getcwd())

########################################
# main
########################################

print(os.getcwd())

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

network_choice = st.selectbox("Please select the network you would like to analyse?", ["EU Communication Network", "BGP Networking Data"])

try:
    num_records = int(st.number_input("How many records do you want to visualize? Limit to 100.", step=1, format="%d"))
    if st.button("Visualize the network."):
        # Prepare data packet for request
        data = {"num_records": num_records,
                "network_choice": network_choice}
        
        # Get url
        baseurl = configur.get('client', 'web-server')
        api = '/visualize_network'
        url = baseurl + api

        res = requests.post(url, json=data)

        response = res.json()
        # print(res)
        # print(response)

        if response['statusCode'] == 200:
            print("Response was successful.")
            st.write("You have successfully received the image.")
            img_encoded = base64.b64decode(response["body"])

            # Writing the file locally
            try:
                with open(Path("plots") / f"neo4j_graph_{network_choice}_{num_records}.png", "wb") as outfile:
                    outfile.write(img_encoded)
            except Exception as err:
                print("Error while trying to save image locally.")
                print(err)

            # Displaying the image
            image = Image.open(Path("plots") / f"neo4j_graph_{network_choice}_{num_records}.png")
            st.image(image, caption=f"Visualisation of network: {network_choice}")
        else:
            st.write(response["body"])
        
    else:
        print("You have gotten an error while trying to study network.")
        st.write("You have gotten an error while trying to study network.")
except Exception as err:
    print("Error in Visualization at Client.")
    print(err)