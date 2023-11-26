################################################################################
# Importing relevant packages
################################################################################
import sys
import os
from pathlib import Path
from typing import List, Dict
import json
import openai
import neo4j
from configparser import ConfigParser
from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.graphs.neo4j_graph import Neo4jGraph
import getpass

################################################################################
# Execute Graph Operations
################################################################################
def execute_graph_operations(config_path: str, user_query: str, network_choice: str) -> Dict:
    """
    Summary: This function connects to the Neo4j DB, creates Cypher
    Queries using LangChain and executes it on Neo4j DB
    ----------------------------------------------------------------------
    Extra args:
    file_path: Is a Path object which points to the file with data
    ----------------------------------------------------------------------
    """

    # Get configuration
    configur = ConfigParser()
    configur.read(config_path)

    try:
        uri = None
        username = None
        password = None
        if network_choice == "EU Communication Network":
            # Get neo4j credentials
            uri = configur.get('eu-neo4j-graph', 'uri')
            username = configur.get('eu-neo4j-graph', 'username')
            password = configur.get('eu-neo4j-graph', 'password')
    except Exception as err:
        print("Error in getting Graph DB credentials")
        print(err)
        return {'statusCode': 400,
                'body': json.dumps(err)}
    
    print(uri)
    print(username)
    print(password)

    # Connecting to Graph DB
    try:
        graph = Neo4jGraph(
                url=uri,
                username=username,
                password=password
            )
    except Exception as err:
        print("Error in connecting to Graph DB")
        print(err)
        return {'statusCode': 400,
                'body': json.dumps(err)}

    # Set Up OpenAI API and get response
    try:
        api_key = configur.get('openai-api', 'api-key')
        name = 'OPENAI_API_KEY'
        os.environ[name] = api_key

        # To check schema
        print(graph.schema)
    
        # Setting up ChatGPT integration with Graph Database
        chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(temperature=0), graph=graph, verbose=True,
        )

        return {'statusCode': 200, 'body': json.dumps(chain.run(user_query))}
    except Exception as err:
        print("Error in executing Graph Operation with LangChain.")
        return {'statusCode': 400,
                'body': json.dumps(err)}
        

