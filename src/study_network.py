################################################################################
# Importing relevant packages
################################################################################
import sys
import os
from pathlib import Path
from typing import List, Dict
import json
import openai
from configparser import ConfigParser
from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
import getpass

################################################################################
# Execute Graph Operations
################################################################################
def execute_graph_operations(config_path: str, user_query: str) -> str:
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
        # Getting neo4j credentials
        uri = configur.get('neo4j-graph', 'uri')
        username = configur.get('neo4j-graph', 'username')
        password = configur.get('neo4j-graph', 'password')

        # Make Graph Connection
        graph = Neo4jGraph(url=uri, username=username, password=password)
        print("You have successfully connected to Graph DB")
    except Exception as err:
        print("Error in connecting to Graph DB")
        return {'statusCode': 400,
                'body': json.dumps(err)}

    # Set Up OpenAI API
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
        

