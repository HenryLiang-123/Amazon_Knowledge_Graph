from mrtparse import *
from tqdm import tqdm
from neo4j import GraphDatabase

# Help Function to process each OrderedDict in bgp update data
def process_ordered_dict(tx, bgp_data,message_id):
    # Convert all keys to strings and check for 'bgp_message'
    bgp_data = {str(key): value for key, value in bgp_data.items()}
    if 'bgp_message' not in bgp_data:
        # Skip this row if 'bgp_message' is not present
        return

    local_as = bgp_data.get('local_as')
    peer_as = bgp_data.get('peer_as')
    timestamp = list(bgp_data['timestamp'].values())[0]

    bgp_message = bgp_data['bgp_message']
    message_type = list(bgp_message['type'].values())[0]
    message_length = bgp_message.get('length')

    # Create or merge Local AS and Peer AS nodes
    tx.run("MERGE (localAS:AS {id: $local_as})", local_as=local_as)
    tx.run("MERGE (peerAS:AS {id: $peer_as})", peer_as=peer_as)

    if message_type == 'UPDATE':
      withdrawn_routes_length = len(bgp_message.get('withdrawn_routes', []))
      nlri_length = len(bgp_message.get('nlri', []))
      is_withdrawal = withdrawn_routes_length > 0
      is_announcement = nlri_length > 0

      announcements_history = {}
      # Create relationship based on message type
      if is_withdrawal:
        withdrawn_list = [x['prefix'] for x in bgp_message['withdrawn_routes']]
        tx.run("""
              MATCH (localAS:AS {id: $local_as}), (peerAS:AS {id: $peer_as})
              CREATE (localAS)-[r:WITHDRAWS_ROUTE_TO {m_id: $message_id}]->(peerAS)
              SET r.timestamp = $timestamp, r.message_type = $message_type, r.message_length = $message_length, r.routes_length = $withdrawn_routes_length, r.withdrawn_list = $withdrawn_list
              """, local_as=local_as, peer_as=peer_as,timestamp=timestamp, 
               message_type=message_type, message_length=message_length, 
               withdrawn_routes_length=withdrawn_routes_length,message_id=message_id, withdrawn_list=withdrawn_list)
      if is_announcement:
        path_seq = list(bgp_message['path_attributes'][1]['value'][0]['value'])
        prefix = bgp_message['nlri'][0]['prefix']
        announcement_key = (local_as, peer_as, prefix)
        attributes = [str(x) for x in list(bgp_message.get('path_attributes',[]))]
        # Check for new, duplicate, or implicit withdrawal
        if announcement_key not in announcements_history:
            category = 'new_announcement'
        elif announcements_history[announcement_key] == attributes:
            category = 'duplicate_announcement'
        else:
            category = 'implicit_withdrawal'
        tx.run("""
              MATCH (localAS:AS {id: $local_as}), (peerAS:AS {id: $peer_as})
              CREATE (localAS)-[r:ANNOUNCES_ROUTE_TO {m_id: $message_id, category:$category}]->(peerAS)
              SET r.timestamp = $timestamp, r.message_type = $message_type, r.message_length = $message_length, 
              r.routes_length = $nlri_length, r.path_seq = $path_seq
              """, local_as=local_as, peer_as=peer_as, timestamp=timestamp, 
               message_type=message_type, message_length=message_length, 
               nlri_length=nlri_length,message_id=message_id, path_seq=path_seq, category=category)
    elif message_type == 'OPEN':
      # Create relationship based on message type
      open_version = bgp_message.get('version')
      open_local_as = bgp_message.get('local_as')
      open_holdtime = bgp_message.get('holdtime')
      open_bgp_id = bgp_message.get('bgp_id')
      # Handle OPEN message
      tx.run("""
            MATCH (localAS:AS {id: $local_as}), (peerAS:AS {id: $peer_as})
            CREATE (localAS)-[r:OPENS_CONNECTION_TO {m_id: $message_id}]->(peerAS)
            SET r.timestamp = $timestamp, r.message_length = $message_length,
                r.version = $version, r.open_local_as = $open_local_as,
                r.holdtime = $holdtime, r.bgp_id = $bgp_id
            """, local_as=local_as, peer_as=peer_as, timestamp=timestamp,
                message_length=message_length, version=open_version,
                open_local_as=open_local_as, holdtime=open_holdtime, bgp_id=open_bgp_id,message_id=message_id)
    elif message_type == 'NOTIFICATION':
      # Handle NOTIFICATION message
      error_code = list(bgp_message['error_code'].values())[0]
      error_subcode = list(bgp_message.get('error_subcode'))[0]
      # Handle NOTIFICATION message
      tx.run("""
            MATCH (localAS:AS {id: $local_as}), (peerAS:AS {id: $peer_as})
            CREATE (localAS)-[r:SENDS_NOTIFICATION_TO {m_id: $message_id}]->(peerAS)
            SET r.timestamp = $timestamp, r.message_length = $message_length,
                r.error_code = $error_code, r.error_subcode = $error_subcode
            """, local_as=local_as, peer_as=peer_as, timestamp=timestamp,
                message_length=message_length, error_code=error_code,
                error_subcode=error_subcode,message_id=message_id)
    elif message_type == 'KEEPALIVE':
      # Handle KEEPALIVE message
      tx.run("""
            MATCH (localAS:AS {id: $local_as}), (peerAS:AS {id: $peer_as})
            CREATE (localAS)-[r:SENDS_KEEPALIVE_TO {m_id: $message_id}]->(peerAS)
            SET r.timestamp = $timestamp, r.message_length = $message_length
            """, local_as=local_as, peer_as=peer_as, timestamp=timestamp, message_length=message_length,message_id=message_id)

def create_bgp_update(driver, username, password, bgp_data_txt):

    # Reader the bgp update data from txt file and saved as a list
    message_list = []
    for entry in Reader(bgp_data_txt):
        message_list.append(entry.data)

        # Connect to Neo4j
    driver = GraphDatabase.driver("neo4j+s://896675cf.databases.neo4j.io", auth=(username, password))

    # Process each OrderedDict
    with driver.session() as session:
        for i, bgp_dict in enumerate(tqdm(message_list, desc="Processing BGP Messages")):
                session.execute_write(process_ordered_dict, bgp_dict, message_id=i)
    driver.close()
    