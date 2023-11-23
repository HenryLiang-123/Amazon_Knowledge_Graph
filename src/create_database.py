################################################################################
# Importing relevant packages
################################################################################
from neo4j import GraphDatabase
import sys
from pathlib import Path
from typing import List, Dict
import json

################################################################################
# Extract the data
################################################################################
def get_data(file_path: Path) -> List[List[int]]:
    """
    Summary: This function extracts the data from a text file and returns 
    it in a list
    ----------------------------------------------------------------------
    Extra args:
    file_path: Is a Path object which points to the file with data
    ----------------------------------------------------------------------
    """
    f = open(file_path, 'r')
    lines = f.readlines()
    lines = [line.strip('\n').split(' ') for line in lines]
    return lines

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
    query = (
        "MERGE (fromNode:Node {id: $from_node_id}) "
        "MERGE (toNode:Node {id: $to_node_id}) "
        "MERGE (fromNode)-[: EMAILS_TO]->(toNode)"
    )
    tx.run(query, from_node_id=from_node_id, to_node_id=to_node_id)

################################################################################
# Create graph
################################################################################
def create_graph(uri: str, username: str, password: str, data: List[List[int]]) \
                                                    -> Dict[str]:
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
        driver = GraphDatabase.driver(uri, auth=(username, password))
    except Exception as err:
        print("Error in connecting to Graph DB.")
        return {"statusCode": 400,
                "body": json.dumps(err)}

    try:
        # Create database
        with driver.session() as session:
            for line in data:
                from_node_id, to_node_id = map(int, line)
                session.write_transaction(add_nodes_edges, from_node_id, to_node_id)
        print("You have successfully loaded your dataset.")
        driver.close()
        return {"statusCode": 200,
                "body": "You have successfully loaded your dataset."}
    except Exception as err:
        print("You have encountered an error while creating the graph network.")
        return {"statusCode": 400,
                "body": json.dumps(err)}