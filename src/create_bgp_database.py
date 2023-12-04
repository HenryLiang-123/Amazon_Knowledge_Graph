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
from typing import Dict
from neo4j import GraphDatabase
from datetime import datetime
from bs4 import BeautifulSoup
from src.create_bgp_update import create_bgp_update, process_ordered_dict
from src.add_attributes import fetch_all_ids, update_node, add_attributes

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
    try:
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
    except Exception as err:
        print(err)
        return {"statusCode": 400,
                "body": str(err)}

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
    from mrtparse import Reader
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
                "body": str(err)}
    
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
                "body": str(err)}


# # 2 step: Add attributes of each AS Node

# def clean_as_number(as_number):
#     return re.sub(r'\D', '', as_number) if as_number else None

# def extract_attributes(df_filter,base_url):
#     dic = {}
#     for url in df_filter['Link']:
#         cur_url = base_url + url

#         response = requests.get(cur_url)

#         # Check if the request was successful
#         if response.status_code == 200:
#         # Parse the HTML content
#             soup = BeautifulSoup(response.text, 'html.parser')
#             ul_tags = soup.find_all('ul')
#             text = ""
#             for ul in ul_tags:
#                 text += ul.get_text()
#         # Regular expressions to extract the data
#         as_number_pattern = r"ASNumber:\s+(\d+)|aut-num:\s+AS(\d+)"
#         as_name_pattern = r"ASName:\s+(.+)|as-name:\s+(.+)"
#         org_name_pattern = r"OrgName:\s+(.+)|org-name:\s+(.+)"
#         country_pattern = r"(?i)Country:\s+(.+)"
#         city_pattern = r"City:\s+(.+)"
#         state_pattern = r"StateProv:\s+(.+)|State:\s+(.+)"
#         adjacent_asn_pattern = r"Upstream Adjacent AS list\n(.+)"
#         upstream_pattern = r"Upstream:\s+(\d+)"
#         downstream_pattern = r"Downstream:\s+(\d+)"
#         rank_pattern = r"Rank\s+AS\s+Type\s+Originate Addr Space\s+\(pfx\)\s+Transit Addr space\s+\(pfx\)\s+Description\n(\d+)"
#         if re.search(as_number_pattern, text):
#             # Extracting data using regex with checks
#             as_number = re.search(as_number_pattern, text).group()
#             as_number = clean_as_number(as_number)
#             as_name = re.search(as_name_pattern, text).group(1) if re.search(as_name_pattern, text).group(1) else re.search(as_name_pattern, text).group(2)
#             org_name_search = re.search(org_name_pattern, text)
#             if org_name_search:
#                 org_name = org_name_search.group(1) if org_name_search.group(1) else org_name_search.group(2)
#             else:
#                 org_name = None
#             #org_name = re.search(org_name_pattern, text).group(1) if re.search(org_name_pattern, text).group(1) else re.search(org_name_pattern, text).group(2)
#             country = re.search(country_pattern, text).group(1) if re.search(country_pattern, text) else None
#             city = re.search(city_pattern, text).group(1) if re.search(city_pattern, text) else None
#             state = re.search(state_pattern, text).group(1) if re.search(state_pattern, text) else None
#             upstream = re.search(upstream_pattern, text).group(1) if re.search(upstream_pattern, text) else None
#             downstream = re.search(downstream_pattern, text).group(1) if re.search(downstream_pattern, text) else None
#             rank = re.search(rank_pattern, text).group(1) if re.search(rank_pattern, text) else None

#             dic[as_number] = [as_name,org_name, country, city,state,upstream,downstream, rank]

#     data_tuples = [(key, *values) for key, values in dic.items()]
#     df = pd.DataFrame(data_tuples,columns=["ASN","as_name","org_name", "country", "city","state", "upstream","downstream", "rank"] )
#     return df

# def add_as_attributes(graph_uri,username, password):
#     # Fetch and print all IDs
#     driver = GraphDatabase.driver(graph_uri, auth=(username, password))
#     try:
#         ids = fetch_all_ids()
#         # remove the duplicaed ids. There are 2 labels in the graph datbase, which contain duplicated ids
#         ids = list(set(ids))
#     finally:
#         driver.close()
    
#     # Parse ASN report from url
#     RAW_URL = 'https://bgp.potaroo.net/cidr/autnums.html'
#     # Send a GET request to the URL
#     response = requests.get(RAW_URL)

#     # Check if the request was successful
#     if response.status_code == 200:
#         # Parse the HTML content
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Find the <pre> tag
#         pre_tag = soup.find('pre')
#         if pre_tag:
#             # Find all <a> tags within the <pre> tag
#             a_tags = pre_tag.find_all('a')
#             # List to store each row of data
#             data = []

#             # Extract the href attribute and text from each <a> tag
#             for a_tag in a_tags:
#                 href = a_tag.get('href')
#                 text = a_tag.get_text(strip=True)
#                 sibling_text = a_tag.next_sibling

#                 # Append as a tuple to the data list
#                 data.append((href, text, sibling_text))

#             # Create a DataFrame
#             df_url = pd.DataFrame(data, columns=['Link', 'Text', 'Sibling Text'])[1:]

#             # Optionally, save the DataFrame to a file, e.g., CSV
#             # df.to_csv('output.csv', index=False)
#         else:
#             print("<pre> tag not found in the HTML.")
#     else:
#         print("Failed to retrieve the webpage")
    
#     # Filter ASN report which is not in graph database: Save time
#     df_filter = df_url[df_url['Text'].isin(ids)]
#     base_url = 'https://bgp.potaroo.net'
#     df = extract_attributes(df_filter,base_url)
#     # Saved the dataframe if needed
#     # df.to_csv(filename,index = False)

#     # Add the attributes into graph database
#     add_attributes(df,graph_uri,username,password)

# # Create BGP update graph database

# # parsing data from website
# def download_gz_file(url, filename):
#     """
#     Download a .gz file from the given URL and save it as filename.
#     """
#     response = requests.get(url, stream=True)
#     # Check if the response was successful
#     if response.status_code == 200:
#         # Save the file to disk
#         with open(filename, 'wb') as f:
#             f.write(response.content)
#         print(f"Downloaded: {filename}")
#     else:
#         # Print an error message if the download failed
#         print(f"Failed to download. Status code: {response.status_code}")


# def get_update_data_web(graph_uri,username,password):
#     today = datetime.date.today()
#     month = today.month
#     year = today.year
#     rrc_name = "rrc00"
#     base_url = f"https://data.ris.ripe.net/{rrc_name}/"
#     url = base_url + str(year) + "." + str(month)
#     part1 = today.strftime("%Y%m%d")
#     part2 = "0800"
#     url += "/updates." + part1 + "." + part2 + ".gz"

#     download_gz_file(url, f'{today}.gz')
#     with gzip.open(f'{today}.gz', 'rb') as f_in:
#         with open(f'{today}.txt', 'wb') as f_out:
#             shutil.copyfileobj(f_in, f_out)
    
#     # Connect to Neo4j
#     driver = GraphDatabase.driver(graph_uri, auth=(username,password))
#     create_bgp_update(driver,username,password,f'{today}.txt')
    
