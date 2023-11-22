#
# Client-side python app for Final Project, this time working with
# web service, which in turn uses AWS S3 ato implement
# a simple ML Model for rental price prediction and apartment description generation.
#
# Final Project for CS 310
#
# Authors:
#   YOUR NAME
#   Sharika Mahadevan, Hye Won Hwang, Alejandra Lelo de Larrea Ibarra
#   Northwestern University
#   CS 310
#

###################################################################
#
# Importing packages
#

import os
import pathlib
import logging
import sys
import base64
from configparser import ConfigParser

import requests  # calling web service
# import json  # relational-object mapping

# import matplotlib.pyplot as plt
# import matplotlib.image as img

import streamlit as st

#########################################################################
# main
#
st.title('** Welcome to SocialPulse Insights **')
st.header('Who are we?')
st.write('Unlock the Power of Social Influence with SocialPulse Insights, the Premier Social Network Analytics Solution!')
st.write('In the ever-evolving landscape of digital interactions, SocialPulse Insights stands as the forefront solution for companies seeking to harness the full potential of their social network presence. Our cutting-edge analytics platform provides a comprehensive and insightful view of your company\'s social media performance, allowing you to make data-driven decisions that propel your brand to new heights.')
st.write('Why Choose SocialPulse Insights?')
st.write('SocialPulse Insights is more than just a social network analytics tool; it\'s your strategic ally in navigating the dynamic world of social media. Elevate your brand, engage your audience, and drive business success with the unparalleled insights delivered by SocialPulse Insights.')
st.write('Take control of your social narrative. Choose SocialPulse Insights today!')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#
# what config file should we use for this session?
#
config_file = 'config/config.ini'

#
# setup base URL to web service:
#
configur = ConfigParser()
configur.read(config_file)
baseurl = configur.get('client', 'webservice')


