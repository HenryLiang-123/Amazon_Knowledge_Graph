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
bgp_url=https://data.ris.ripe.net

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

### Containerizing

**Please ensure that plots directory and config directory with config.ini files is completed as described in Steps 3 and 4 in [Prerequisites](#prerequisites) section**.

Run the following steps in Terminal from the parent directory of the project.

1. Open docker

``` open -a Docker ```

2. Build the Docker image

``` docker build -t <image_name> . ```

3. Run the Container.

``` docker run -p 8501:8501 <image_name> ```

4. Check the website on browser at `http://localhost:8501/`.

# Acknowledgments

- This repo is the combined work of Hanwei Hu, Sharika Mahadevan, Yuexin Chen, Kiran Sheena Jyothi and Han Wen Liang.