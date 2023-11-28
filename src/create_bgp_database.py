################################################################################
# Importing relevant packages
################################################################################
import os
import requests
import gzip
import shutil
import sys
import json
from pathlib import Path
from mrtparse import *
import networkx as nx
from typing import Dict
import matplotlib.pyplot as plt
from neo4j import GraphDatabase
from datetime import datetime

################################################################################
# Extract the data
################################################################################
def get_bgp_data(url: str, zip_file_name: str, filename: str, output_path: Path) -> Dict[str, object]:
    """
    Summary: This function extracts the data from a text file and returns 
    it in a list
    ----------------------------------------------------------------------
    Extra args:
    file_path: Is a Path object which points to the file with data
    ----------------------------------------------------------------------
    """
    r = requests.get(url, allow_redirects=True)

    if(r.status_code==200):

        ## Removing the zip file if it exists
        if os.path.isfile(zip_file_name):
            os.remove(zip_file_name)

        ## Removing content file if it exists
        if os.path.isfile(filename):
            os.remove(filename)

        ## Obtaining the zip file
        with open(output_path / zip_file_name, 'wb') as f:
            f.write(r.content)

        ## Obtaining the content file
        with gzip.open(output_path / zip_file_name, 'rb') as f_in:
            with open(output_path / filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        ## Removing the zip file after extraction
        if os.path.isfile(output_path / zip_file_name):
            os.remove(output_path / zip_file_name)
        print("The BGP File for today has been successfully saved.")
        return {"statusCode": 200,
                "body": "The BGP File for today has been successfully saved."}
    else:
        print("BGP File does not exist in given URL.")
        return {"statusCode": 400,
                "body": "BGP File does not exist in given URL."}

################################################################################
# Add nodes and edges
################################################################################
def add_nodes_edges(tx, from_node_id: int, to_node_id: int) -> None:
    """
    Summary: This function adds the nodes and edges to the graph network 
    in specified database
    ----------------------------------------------------------------------
    Extra args:
    tx: Graph session to create Database in neo4j
    from_node_id: Node from which relationship originates
    to_node_id: Node from which relationship ends
    ----------------------------------------------------------------------
    """
    today_date = datetime.today().strftime(format = "%Y%m%d")
    query = (
        "MERGE (fromNode:Node_$today_date {id: $from_node_id}) "
        "MERGE (toNode:Node_$today_date {id: $to_node_id}) "
        "MERGE (fromNode)-[:CONNECTS]->(toNode)"
    )
    tx.run(query, from_node_id=from_node_id, to_node_id=to_node_id, today_date=today_date)

################################################################################
# Create graph
################################################################################
def create_bgp_graph(bgp_url: str, graph_uri: str, username: str, password: str, output_path: Path) \
                                                    -> Dict[str, object]:
    """
    Summary: This function creates the graph network in specified database
    ----------------------------------------------------------------------
    Extra args:
    uri: Link to neo4j graph
    username: username for neo4j access
    password: password for neo4j access
    ----------------------------------------------------------------------
    """
    try:
        # Connect to neo4j database
        driver = GraphDatabase.driver(graph_uri, auth=(username, password))
    except Exception as err:
        print("Error in connecting to Graph DB.")
        return {"statusCode": 400,
                "body": str(err)}

    # Get today's year, month, date
    today_year = datetime.now().year
    today_month = datetime.now().month
    today_date = datetime.now().date
    today_time = "0800"
    rrc_name = "rrc00"

    # Nomenclature followed on BGP Site
    zip_file_name = "bview.{}{}{}.{}.gz".format(today_year,today_month,today_date,today_time)
    filename = "bview.{}{}{}.{}".format(today_year,today_month,today_date,today_time)

    # Make URL for today
    remote_url = bgp_url + "/" + rrc_name + "/" + today_year + "." + today_month + "/" + zip_file_name

    # Download BGP Data from online
    try:
        response = get_bgp_data(remote_url, zip_file_name, filename, output_path)
        print(response)
        if response["statusCode"] == 200:
            print(response["body"])
        else:
            print("You have encountered an error while trying to access the URL today.")
            print(response["body"])
            return {"statusCode": 400,
                "body": "BGP File does not exist in given URL."}
    except Exception as err:
        print("You have encountered an error while trying to access/download BGP Data.")
        print(err)
        return {"statusCode": 400,
                "body": "BGP File does not exist in given URL."}
    
    # Create database
    try:
        check_list = []
        check_json = []

        with driver.session() as session:
            i = 0
            for entry in Reader(filename):
                curr_json = entry.data
                if list(curr_json['subtype'].values())[0]== "RIB_IPV4_UNICAST":
                    if 'rib_entries' in curr_json.keys():
                        entry_count = curr_json.get('entry_count',0)
                        for j in range(entry_count):
                            curr_list = curr_json['rib_entries'][j]['path_attributes'][1]['value'][0]['value']
                            N = len(curr_list)
                            for k in range(N-1):
                                if(curr_list[k+1]!=curr_list[k]): ## Avoiding same node cycles
                                    session.write_transaction(create_bgp_graph, curr_list[k+1], curr_list[k])
                    else:
                        curr_list = curr_json['path_attributes'][1]['value'][0]['value']
                        N = len(curr_list)
                        for k in range(N-1):
                            if(curr_list[k+1]!=curr_list[k]):
                                session.write_transaction(create_bgp_graph, curr_list[k+1], curr_list[k])
                    i += 1
                if(i==20):
                    break

        ## Removing content file after reading
        if os.path.isfile(filename):
            os.remove(filename)

        return {"statusCode": 200, "body": "You have successfully loaded your dataset."}
    except Exception as err:
        print("You have encountered an error while creating the graph network.")
        return {"statusCode": 400,
                "body": json.dumps(err)}