# Can LLMs learn Knowledge Graphs?

The objective of the project is to : 

1. Develop efficient prompting to identify differences in two graphs.

2. Apply different prompting techniques such as zero shot learning, few shot learning and chain-of-thought prompting.

3. Understand the current bounds to LLM’s understanding of Graphs.

4. Test final prompting technique on desired dataset.

# Features

- **LangChain Integration:** Utilize the LangChain framework to dynamically generate Cypher queries for Neo4j.
  
- **Graph Operations/Measures:** Explore various social network measures, such as centrality, clustering coefficients, and more, to gain a deeper understanding of your network structure.

- **Neo4j Compatibility:** Seamlessly connect to your Neo4j database and execute complex queries with ease.

- **Visualization:** Develop visualizations to better see your network.

- **Network updates:** Seamlessly update your data with the click of a button.

# Getting Started

### Prerequisites

1. Develop a virtual environment using `python -m venv <name_of_virtual_environment>`

2. Install dependencies needed using the `requirements.txt` file.

3. Create a folder *config* in parent directory with one file *config.ini* with the following structure:

```
[create_database]
file_path=#Enter the file path to the data to be loaded

[bgp-graph]
uri=#URI to Neo4j Graph DB
username=#Enter Username
password =#Enter Password

[openai-api]
api-key=#Enter OpenAI API Key
```

4. Create a folder plots in parent directory.

### Installation

1. Clone the repository: `git clone https://github.com/HenryLiang-123/Amazon_Knowledge_Graph.git`
2. Follow steps in **Prerequisites**.

### Usage

1. Run the application: `streamlit run streamlit-files-local/Welcome.py`

## Acknowledgments

- This repo is the combined work of Hanwei Hu, Sharika Mahadevan, Yuexin Chen, Kiran Sheena Jyothi and Han Wen Liang.