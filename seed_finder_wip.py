import logging
from elasticsearch import Elasticsearch, exceptions
import traceback

# Configuration Variables
INDEX_NAME = "card_sequences_v2"  # Elasticsearch index name
ES_HOST = "http://192.168.10.192:9200"  # Elasticsearch host
ES_USER = "elastic"  # Elasticsearch username
ES_PASSWORD = "Maarsseveen1!"  # Elasticsearch password

# Logging Configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Elasticsearch Client
def get_elasticsearch_client():
    """Create and return an Elasticsearch client."""
    return Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASSWORD),
        verify_certs=False,
        request_timeout=60
    )

def search_seed_by_card_sequence(client, card_sequence):
    """Search for a seed by matching a 15-card sequence."""
    cards = card_sequence.split()
    query = {
        "size": 5,
        "query": {
            "bool": {
                "filter": [
                    {"terms": {"card_sequence": cards}}
                ]
            }
        }
    }

    try:
        logger.info("Searching for matching seeds...")
        response = client.search(index=INDEX_NAME, body=query)
        hits = response.get("hits", {}).get("hits", [])
        
        if not hits:
            logger.info("No matching seeds found for the given card sequence.")
            return

        for hit in hits:
            seed_key = hit["_source"]["seed_key"]
            full_sequence = hit["_source"]["card_sequence"]
            timestamp = hit["_source"]["timestamp"]

            print(f"\nMatch Found:\nSeed Key: {seed_key}\nTimestamp: {timestamp}\nCard Sequence: {full_sequence[:100]}...")
    except exceptions.ElasticsearchException as e:
        logger.error(f"Error while searching: {e}")
        logger.error(traceback.format_exc())

def main():
    client = get_elasticsearch_client()
    
    # Input the 15-card sequence
    card_sequence = input("Enter the 15-card sequence (space-separated): ")
    search_seed_by_card_sequence(client, card_sequence)

if __name__ == "__main__":
    main()
