from neo4j import GraphDatabase

# Help Function

# Function to fetch all IDs
def fetch_all_ids(driver):
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n.id AS id")
        return ["AS" + record["id"] for record in result]

# Update the Neo4j Aura database
def update_node(driver,attributes):
    with driver.session() as session:
        session.run(
            """
            MATCH (n) WHERE n.id = $ASN
            SET n.as_name = $as_name, n.org_name = $org_name, n.country = $country,
                n.city = $city, n.state = $state,n.upstream = $upstream,
                n.downstream = $downstream, n.rank = $rank
            """,
            **attributes
        )

def add_attributes(data, uri,username, password):
# Neo4j Aura DB credentials
    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        for _, row in data.iterrows():
            update_node(driver, row.to_dict())
    finally:
        driver.close()
