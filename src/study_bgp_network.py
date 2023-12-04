################################################################################
# Importing relevant packages
################################################################################
import os
import json
from typing import Any, Dict, List
import re
from configparser import ConfigParser
import neo4j
from neo4j import GraphDatabase
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.graphs.neo4j_graph import Neo4jGraph

################################################################################
# Constants
################################################################################
MODEL_VERSION = "gpt-4"
SCHEMA_FORMAT = """
Node properties are the following:
{}
Relationship properties are the following:
{}
The relationships are the following:
{}
"""

################################################################################
# Functions
################################################################################
def refine_query(client, user_query: str) -> Dict[str, Any]:
    """
    Refines the user query for better coherence.

    Args:
        client: The OpenAI client instance.
        user_query: The query provided by the user.

    Returns:
        A dictionary with status code and the refined query or error message.
    """
    openai.api_key = os.getenv('OPENAI_API_KEY')
    raw_input = user_query
    
    # setting threshold for max tokens
    max_tokens = 100
    if len(raw_input.split()) > 100:
        max_tokens = len(raw_input.split())

    prompt = (f"The following is a plain English user input for querying a graph database: '{raw_input}'. "
              "Rewrite this input into a clearer query format. "
              "However, do not remove any information related to the database or information related to node type which the user provided. "
              "If the input is not clear or relevant, indicate that the user should provide a clearer query."
              "Remember: do not remove any information related to database and node attributes."
              "For example, if the input is 'I want to know how many nodes are in this database', "
              "a better format would be 'Find the number of nodes in the database'.\nRefined Input: ")

    try:
        response = client.completions.create(model=MODEL_VERSION, prompt=prompt, max_tokens=max_tokens)
        refined_prompt = response.choices[0].text.strip()

        if "provide a clearer query" in refined_prompt.lower():
            return {'statusCode': 400, 'body': json.dumps(refined_prompt)}
        else:
            return {'statusCode': 200, 'body': json.dumps(refined_prompt)}

    except Exception as error:
        return {'statusCode': 400, 'body': str(error)}


def neo4j_query(query: str, driver, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Executes a neo4j query and returns the results.

    Args:
        query: Neo4j cypher query.
        driver: Neo4j driver instance.
        params: Additional parameters for the neo4j query.

    Returns:
        List of dictionaries containing the query results.
    """
    if params is None:
        params = {}

    with driver.session(database="neo4j") as session:
        try:
            data = session.run(query, params)
            return [record.data() for record in data]
        except neo4j.exceptions.CypherSyntaxError as error:
            raise ValueError(f"Generated Cypher Statement is not valid\n{error}")


def refresh_schema(driver) -> str:
    """
    Refreshes the Neo4j graph schema information.

    Args:
        driver: Neo4j driver instance.

    Returns:
        A string describing the schema of the graph.
    """
    node_properties_query = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
    WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
    RETURN {labels: nodeLabels, properties: properties} AS output
    """

    rel_properties_query = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
    WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
    RETURN {type: nodeLabels, properties: properties} AS output
    """

    rel_query = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE type = "RELATIONSHIP" AND elementType = "node"
    UNWIND other AS other_node
    RETURN {start: label, type: property, end: toString(other_node)} AS output
    """

    node_properties = [el["output"] for el in neo4j_query(node_properties_query, driver)]
    rel_properties = [el["output"] for el in neo4j_query(rel_properties_query, driver)]
    relationships = [el["output"] for el in neo4j_query(rel_query, driver)]

    return SCHEMA_FORMAT.format(
        node_properties,
        rel_properties,
        [f"(:{el['start']})-[:{el['type']}]->(:{el['end']})" for el in relationships]
    )


def get_gpt3_response(curr_schema: str, question: str, client, model: str = MODEL_VERSION, history=None) -> str:
    """
    Sends a request to the OpenAI Chat API to get a response for a Cypher query.

    Args:
        curr_schema: Current schema of the graph described as a string.
        question: User question.
        client: OpenAI client instance.
        model: Model version to use.
        history: Historical OpenAI chat responses.

    Returns:
        The model's response as a string.
    """
    system_prompt = (f"Human: Task: Generate Cypher statement to query a graph database.\n"
                     "Instructions:\nUse only the provided relationship types and properties in the schema.\n"
                     "Consider directionality of the graph.\n"
                     "The cypher output should have some indication either as variable name to indicate the requirement of the question.\n"
                     "Schema:\n{curr_schema}")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    if history:
        messages.extend(history)

    response = client.chat.completions.create(model=model, messages=messages)

    return response.choices[0].message.content


def lang_chain_custom(question: str, client, driver, model: str = MODEL_VERSION) -> Dict[str, Any]:
    """
    Obtain an answer to the user question based on the graph.

    Args:
        question: User question.
        client: OpenAI client instance.
        driver: Neo4j driver instance.
        model: Model version to use.

    Returns:
        JSON response with the required output or error message.
    """
    try:
        curr_schema = refresh_schema(driver)
        cypher_query = get_gpt3_response(curr_schema, question, client, model)

        cypher_response = neo4j_query(cypher_query, driver)
        cypher_response = cypher_response[:10]  # Limiting to avoid token limits

    except Exception as error:
        return {'statusCode': 400, 'body': str(error)}

    try:
        response = get_gpt3_response(curr_schema, cypher_response, client, model)

    except Exception as error:
        return {'statusCode': 400, 'body': str(error)}

    return {'statusCode': 200, 'body': json.dumps(response)}


def execute_graph_operations(config_path: str, user_query: str, network_choice: str) -> Dict[str, Any]:
    """
    Connects to the Neo4j DB, creates Cypher Queries, and executes them.

    Args:
        config_path: Path to the configuration file.
        user_query: User's query.
        network_choice: Choice of network data.

    Returns:
        Dictionary with the response status and body.
    """
    configur = ConfigParser()
    configur.read(config_path)

    try:
        uri, username, password = None, None, None
        if network_choice == "BGP Networking Data":
            uri = configur.get('bgp-graph', 'uri')
            username = configur.get('bgp-graph', 'username')
            password = configur.get('bgp-graph', 'password')
        else:
            return {'statusCode': 400, 'body': json.dumps("Dataset not available. Please use 'Get Data' functionality.")}

    except Exception as error:
        return {'statusCode': 400, 'body': str(error)}

    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))

    except Exception as error:
        return {'statusCode': 400, 'body': str(error)}

    try:
        api_key = configur.get('openai-api', 'api-key')
        os.environ['OPENAI_API_KEY'] = api_key
        client = OpenAI()

        refined_output = refine_query(client=client, user_query=user_query)

        if refined_output['statusCode'] == 400:
            return refined_output

        updated_user_query = json.loads(refined_output['body'])

        response = lang_chain_custom(question=updated_user_query, client=client, driver=driver, model=MODEL_VERSION)

        return response

    except Exception as error:
        return {'statusCode': 400, 'body': str(error)}
