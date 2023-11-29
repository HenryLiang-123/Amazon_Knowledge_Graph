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
from neo4j import GraphDatabase
from openai import OpenAI

from custom_langchain import refine_query,lang_chain_custom
################################################################################
# Execute Graph Operations
################################################################################
def execute_graph_operations(config_path: str, user_query: str, network_choice: str) -> Dict:
    """
    Summary: This function connects to the Neo4j DB, creates Cypher
    Queries and executes it on Neo4j DB
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
            uri = configur.get('eu-comm-graph', 'uri')
            username = configur.get('eu-comm-graph', 'username')
            password = configur.get('eu-comm-graph', 'password')
        elif network_choice == "Internet Networking":
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
                'body': json.dumps(err)}
    
    print(uri)
    print(username)
    print(password)

    # Connecting to Graph DB
    try:
        # graph = Neo4jGraph(
        #         url=uri,
        #         username=username,
        #         password=password
        #     )

        driver = GraphDatabase.driver(uri, auth=(username, password))

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
        
        ## Updating the user query        
        refined_output = refine_query(user_query=user_query)
        
        if(refined_output['statusCode']==400):
            return refined_output
        else:
            updated_user_query = refined_output["updated_user_prompt"]

        ################### Custom Langchain ######################

        client = OpenAI()

        # Setting up ChatGPT integration with Graph Database
        # chain = GraphCypherQAChain.from_llm(
        #     ChatOpenAI(temperature=0), graph=graph, verbose=True,
        # )

        response = lang_chain_custom(question=updated_user_query,
                                     client=client,
                                     driver=driver,
                                     model="gpt-4")

        return response
    
    except Exception as err:
        print("Error in executing Graph Operation.")
        return {'statusCode': 400,
                'body': json.dumps(err)}
        