# Cost Estimate

## Neo4j (AuraDB)

### Assumptions

1. Estimated number of ASes globally (number of nodes): 60,000
2. Estimated number of peering relationships (number of edges), asuming 50 peering relationships between ASes: 3,000,000
3. To detect routing anomalies and hijacking incidents between timestamps, we store 100 snapshots of the BPG graph at all times in the database
4. 1 node (AS) takes up 100 bytes of space
5. 1 edge (peering relationship) takes up 150 bytes of space
6. 20% of database space is reserved for overhead, indexes, metadata.
7. 1GB = 10<sup>9</sup> bytes

### Relevant Calculations

1. Storage needed for nodes = 60,000 nodes &times; 100 snapshots &times; 100 bytes/node &times;10<sup>-9</sup> GB/byte = 6GB
2. Storage needed for edges = 3,000,000 edges &times; 100 snapshots &times; 150 bytes/edge &times;10<sup>-9</sup> GB/byte = 45GB
3. Total for graph: 6 + 45 = 51GB
4. Total needed: 51 &divide; 0.8 = 63.75GB

### Cost for Service

According to [Neo4j](https://neo4j.com/pricing/?utm_medium=PaidSearch&utm_source=google&utm_campaign=GDB&utm_content=AMS-X-Conversion-GDB-Text&utm_term=neo4j%20graph%20database&gclid=Cj0KCQiAsburBhCIARIsAExmsu6MbrXhQvJOv2hz5mbDA8fHGmujqaOozeHM9sfBurHle1ik7R7R8OwaAvj0EALw_wcB#graph-database), the application will require the following configuation:

- Memory: 32GB
- CPU: 6CPU
- Storage: 64GB

Monthly cost: **$2073.60**

## OpenAI

## AWS ECS
