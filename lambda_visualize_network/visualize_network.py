################################################################################
# Importing relevant packages
################################################################################
import sys
import io
import base64
from pathlib import Path
import json
from configparser import ConfigParser
import matplotlib.pyplot as plt
import networkx as nx
from py2neo import Graph
from PIL import Image

################################################################################
# Visualize graph
################################################################################
def lambda_handler(event, context):
    """
    Summary: This function collects the data from Neo4j DB and returns the visualization
    ----------------------------------------------------------------------
    Extra args:
    config_path: Path to Config File
    num_records: Number of records to query from Neo4J DB
    output_path: Path to save visualization
    ----------------------------------------------------------------------
    """
    #Collect the body of the request
    try:
        network_choice = event["network_choice"]
        num_records = event["num_records"]
    except Exception as err:
        print("You have encountered an error in extracting the body of the request.")
        return {'statusCode': 400,
                'body': str(err)}
    
    output_path = "/tmp/"

    # Get configuration
    config_path = "config/config.ini"
    configur = ConfigParser()
    configur.read(config_path)

    try:
        uri = None
        username = None
        password = None
        if network_choice == "EU Communication Network":
            # Get neo4j credentials
            uri = configur.get('eu-comm-graph', 'uri')
            username = configur.get('eu-comm-graph', 'username')
            password = configur.get('eu-comm-graph', 'password')
        elif network_choice == "BGP Networking Data":
            # Get neo4j credentials
            uri = configur.get('bgp-graph', 'uri')
            username = configur.get('bgp-graph', 'username')
            password = configur.get('bgp-graph', 'password')
        else:
            # Ask user to input the dataset
            return {'statusCode': 400,
                'body': json.dumps("This dataset is not available. Please use our \"Get Data\" functionality.")}
    except Exception as err:
        print("Error in getting Graph DB credentials")
        print(err)
        return {'statusCode': 400,
                'body': str(err)}
    
    try:
        # Connect to neo4j database
        graph = Graph(uri=uri, auth=(username, password))
    except Exception as err:
        print("Error in connecting to Graph DB.")
        return {"statusCode": 400,
                "body": str(err)}
    
    # Define cypher query
    cypher_query = None
    if isinstance(num_records, (int)):
        cypher_query = f"""
        MATCH (n)-[r]->(m)
        RETURN n, r, m 
        LIMIT {num_records};
        """
    else:
        print("Invalid input. Ensure to pass only integer input for num_records.")
        return {"statusCode": 400,
                "body": "Invalid input. Ensure to pass only integer input for num_records."}

    # Get data from Neo4j
    try:
        data = graph.run(cypher_query)
    except Exception as err:
        print("Error in querying Neo4j DB.")
        print(err)
        return {"statusCode": 400,
                "body": str(err)}

    # Create a directed graph using networkx
    try:
        G = nx.DiGraph()

        for record in data:
            # Add nodes
            G.add_node(record["n"]["id"]) # Assuming nodes have a 'name' property
            G.add_node(record["m"]["id"])

            # Add edge
            G.add_edge(record["n"]["id"], record["m"]["id"], type=type(record["r"]).__name__)
    except Exception as err:
        print("Error in creating NetworkX graph.")
        return {"statusCode": 400,
                "body": str(err)}

    # Draw the graph
    try:
        pos = nx.spring_layout(G)
        plt.figure(figsize=(20, 20))
        nx.draw(G, pos, with_labels=True, node_size=900, node_color="skyblue", font_size=11, width=0.8, edge_color="gray")
        print(output_path + f"neo4j_graph_{network_choice}.png")
        plt.title("Graph Visualization from Neo4j")
        plt.savefig(output_path + f"neo4j_graph_{network_choice}.png")
        plt.close()

        print("You have successfully visualized the network.")
    except Exception as err:
        print("You have encountered an error while creating the graph visualization.")
        print(err)
        return {"statusCode": 400,
                "body": str(err)}
    
    # Read image file
    try:
        img = Image.open(output_path + f"neo4j_graph_{network_choice}.png", mode='r')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        my_encoded_img = base64.encodebytes(img_byte_arr.getvalue()).decode('ascii')
        return {"statusCode": 200,
                "body": my_encoded_img}
    except Exception as err:
        print("You have encountered an error while returning the graph visualization.")
        return {"statusCode": 400,
                "body": str(err)}