#########################################################################
# Importing packages
#########################################################################
import streamlit as st
import sys

#########################################################################
# main
#########################################################################
st.title('** Welcome to BGP Networking Data Analysis **')

st.write('Welcome to our cutting-edge data exploration platform powered by LangChain!')
st.write('Dive deep into the dynamic world of network data stored in Neo4j as we leverage the language-driven capabilities of LangChain to generate Cypher queries effortlessly. Uncover and analyze intricate changes within your network, gaining valuable insights that drive informed decision-making. Whether you\'re a seasoned data scientist or a curious explorer, our intuitive interface and powerful tools make studying network dynamics an engaging and insightful experience. Explore the evolution of your data on this one-year anniversary of our journey into the realm of innovative data analysis.')

print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0
