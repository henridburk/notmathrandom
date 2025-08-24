from elasticsearch import Elasticsearch, helpers, ApiError
import logging

# Configuration Variables
OLD_INDEX_NAME = "card_sequences"
NEW_INDEX_NAME = "card_sequences_v2"  # New index name with updated mapping
ALIAS_NAME = "card_sequences"          # Alias to point to the new index
NUM_SHARDS = 4                         # Number of shards for the new index
NUM_REPLICAS = 1                       # Number of replicas for fault tolerance

# Elasticsearch Configuration
def get_elasticsearch_client():
    """Create and return an Elasticsearch client."""
    return Elasticsearch(
        hosts=["http://192.168.10.192:9200"],
        basic_auth=("elastic", "Maarsseveen1!"),
        verify_certs=False,
        request_timeout=60
    )

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_new_index(client, new_index_name):
    """Create a new index with a whitespace analyzer."""
    index_body = {
        "settings": {
            "number_of_shards": NUM_SHARDS,
            "number_of_replicas": NUM_REPLICAS,
            "analysis": {
                "analyzer": {
                    "whitespace_analyzer": {
                        "type": "whitespace"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "seed_key": {"type": "keyword"},
                "card_sequence": {
                    "type": "text",
                    "analyzer": "whitespace"  # Apply the whitespace analyzer
                },
                "timestamp": {"type": "date"}
            }
        }
    }

    try:
        if not client.indices.exists(index=new_index_name):
            client.indices.create(index=new_index_name, body=index_body)
            logger.info(f"New index '{new_index_name}' created successfully with whitespace analyzer.")
        else:
            logger.info(f"Index '{new_index_name}' already exists.")
    except ApiError as e:
        logger.error(f"Error creating new index: {e}")

def reindex_data(client, old_index_name, new_index_name):
    """Reindex data from the old index to the new index."""
    try:
        reindex_body = {
            "source": {"index": old_index_name},
            "dest": {"index": new_index_name}
        }
        response = client.reindex(body=reindex_body, wait_for_completion=True, request_timeout=3600)
        logger.info(f"Reindexing completed: {response}")
    except ApiError as e:
        logger.error(f"Error during reindexing: {e}")

def delete_old_index(client, old_index_name):
    """Delete the old index."""
    try:
        client.indices.delete(index=old_index_name)
        logger.info(f"Old index '{old_index_name}' deleted successfully.")
    except ApiError as e:
        logger.error(f"Error deleting old index: {e}")

def update_alias(client, new_index_name, alias_name):
    """Update alias to point to the new index."""
    try:
        actions = [
            {"remove": {"index": "*", "alias": alias_name}},
            {"add": {"index": new_index_name, "alias": alias_name}}
        ]
        client.indices.update_aliases({"actions": actions})
        logger.info(f"Alias '{alias_name}' now points to '{new_index_name}'.")
    except ApiError as e:
        logger.error(f"Error updating alias: {e}")

def main():
    client = get_elasticsearch_client()
    
    # Step 1: Create a new index with the whitespace analyzer
    create_new_index(client, NEW_INDEX_NAME)
    
    # Step 2: Reindex data from the old index to the new index
    reindex_data(client, OLD_INDEX_NAME, NEW_INDEX_NAME)
    
    # Step 3: Delete the old index
    delete_old_index(client, OLD_INDEX_NAME)
    
    # Step 4: Update alias to point to the new index
    update_alias(client, NEW_INDEX_NAME, ALIAS_NAME)

if __name__ == "__main__":
    main()
