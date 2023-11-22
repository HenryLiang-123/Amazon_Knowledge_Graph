########################################
# Importing relevant packages
########################################
import neo4j
from pathlib import Path
from typing import List

########################################
# Extract the data
########################################
def get_data(file_path: Path) -> List[List[int]]:
    """
    Summary: This function extracts the data from a text file and returns it in a list
    ----------------------------------------------------------------------
    Extra args:
    file_path: Is a Path object which points to the file with data
    ----------------------------------------------------------------------
    """
    f = open(file_path, 'r')
    lines = f.readlines()
    lines = [line.strip('\n').split('\t') for line in lines]
    return lines

########################################
# Creating the graph
########################################
def create_graph(tx, from_node_id: int, to_node_id: int) -> None:
    """
    Summary: This function creates the graph network in specified database
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
