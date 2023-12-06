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

### Assumptions

1. There are 91 tokens for 1 graph schema as output from Neo4j
2. To detect routing anomalies and hijacking incidents between timestamps, we store 100 snapshots of the BPG graph at all times in the database
3. On average, the length of a Cypher query output from GPT-4 is 23 tokens
4. The feedback loop for incorrect Cypher queries runs once and only once
5. The total length of all custom prompts is 340 tokens
6. The average length of a user's question is 20 tokens
7. The final output of the LLM has a length of 15 tokens
8. We run the system between the most recent snapshot with all previous snapshots

### Relevant Calculations

1. Total input tokens: 91 &times; 100 + 23 + 340 + 20 = 9483 tokens
2. Total output tokens: 23 + 23 + 340 + 20 + 15 = 421 tokens
3. Number of times run: 99 times.

### Cost for Service

According to [OpenAI](https://openai.com/pricing#language-models) and the usage of GPT-4, the total costs will be:

1. Input: 99 &times; 9483 &divide; 1000 &times; 0.03 = $28.16 per new snapshot
2. Output: 99 &times; 421 &divide; 1000 &times; 0.06 = $2.5 per new snapshot
3. **Total: $30.66 per new snapshot**

## AWS ECS

### Assumptions

1. Ten tasks are run per day.
2. The average length of the session is 1 hour. This factors in idle times, OpenAI API call times, question formulation times, and feedback loop.
3. Each task uses 2 vCPU and 6GB memory.
4. The application takes 20GB of ephemeral storage.
5. 
