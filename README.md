# Welcome to Intelligent Search

Intelligent Search is a search engine that uses machine learning to improve search results. It is built using Haystack Framework.

## Installation

### ElasticSearch Docker:
-   ```bash
    docker pull docker.elastic.co/elasticsearch/elasticsearch:7.5.2
    docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.5.2
    ```