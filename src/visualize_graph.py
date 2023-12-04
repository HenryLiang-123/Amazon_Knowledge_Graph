################################################################################
# Importing relevant packages
################################################################################
import sys
from pathlib import Path
from typing import Dict
import json
from configparser import ConfigParser
import matplotlib.pyplot as plt
import networkx as nx
from py2neo import Graph

################################################################################
# Visualize graph
################################################################################
def visualize_graph(config_path: str, network_choice: str, \
    output_path: Path) -> Dict[str, object]:
    """
    Summary: This function collects the data from Neo4j DB and returns the visualization
    ----------------------------------------------------------------------
    Extra args:
    config_path: Path to Config File
    num_records: Number of records to query from Neo4J DB
    output_path: Path to save visualization
    ----------------------------------------------------------------------
    """

    # Get configuration
    configur = ConfigParser()
    configur.read(config_path)

    try:
        uri = None
        username = None
        password = None
        if network_choice == "BGP Networking Data":
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
    
    # Define
    cypher_query = f"""
    MATCH (n)-[r]->(m)
    RETURN n, r, m;
    """

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
        plt.title("Graph Visualization from Neo4j")
        plt.savefig(output_path / f"neo4j_graph_{network_choice}.png")
        plt.close()
        return {"statusCode": 200,
                "body": "You have successfully uploaded the image to local repository."}
    except Exception as err:
        print("You have encountered an error while creating the graph visualization.")
        return {"statusCode": 400,
                "body": str(err)}