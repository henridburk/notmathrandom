import logging
from elasticsearch import Elasticsearch, exceptions
import traceback

# Configuration Variables
ES_HOST = "http://192.168.10.192:9200"  # Elasticsearch host
ES_USER = "elastic"  # Elasticsearch username
ES_PASSWORD = "Maarsseveen1!"  # Elasticsearch password
INDEX_PATTERN = "*"  # Use wildcard to match all indexes

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_elasticsearch_client():
    """Create and return an Elasticsearch client."""
    return Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASSWORD),
        verify_certs=False,
        request_timeout=600  # Increased timeout to 10 minutes
    )

def search_for_partial_sequence(client, partial_sequence):
    """Search for seeds that contain the given partial card sequence across all indexes."""
    sequence_query = " ".join(map(str, partial_sequence))
    query = {
        "query": {
            "match_phrase": {
                "card_sequence": sequence_query
            }
        },
        "size": 100  # Limit to 100 results for efficiency
    }

    try:
        logger.info(f"Searching for partial sequence: {sequence_query}")
        response = client.search(index=INDEX_PATTERN, body=query)

        hits = response['hits']['hits']
        if hits:
            logger.info(f"Found {len(hits)} matching seeds:")
            matching_seeds = []
            for hit in hits:
                index_name = hit['_index']
                seed_key = hit['_source']['seed_key']
                timestamp = hit['_source']['timestamp']
                card_sequence = hit['_source']['card_sequence'][:100]  # Display first 100 characters of sequence
                print(f"\nMatch Found in Index '{index_name}':")
                print(f"Seed Key: {seed_key}")
                print(f"Timestamp: {timestamp}")
                print(f"Card Sequence: {card_sequence}...")
                matching_seeds.append((index_name, seed_key))
            return matching_seeds
        else:
            logger.info("No matching seeds found.")
            return []
    except exceptions.ElasticsearchException as e:
        logger.error(f"Error during search: {e}")
        logger.error(traceback.format_exc())
        return []

def main():
    client = get_elasticsearch_client()
    
    partial_sequence = []
    while len(partial_sequence) < 10:
        next_card = input(f"Enter card {len(partial_sequence) + 1} (need at least 10 cards to start searching, 'q' to quit): ").strip()
        if next_card.lower() == 'q':
            logger.info("Exiting the search.")
            return
        
        try:
            card = int(next_card)
            if card < 1 or card > 52:
                print("Invalid card number. Please enter a number between 1 and 52.")
                continue
        except ValueError:
            print("Invalid input. Please enter a valid number between 1 and 52.")
            continue

        partial_sequence.append(card)

    # Initial search with the first 10 cards
    matching_seeds = search_for_partial_sequence(client, partial_sequence)
    
    if not matching_seeds:
        print("No matches found with the initial 10-card sequence. Exiting.")
        return

    while len(matching_seeds) > 1:
        next_card = input(f"Enter the next card in the sequence (or 'q' to quit): ").strip()
        if next_card.lower() == 'q':
            logger.info("Exiting the search.")
            break

        try:
            card = int(next_card)
            if card < 1 or card > 52:
                print("Invalid card number. Please enter a number between 1 and 52.")
                continue
        except ValueError:
            print("Invalid input. Please enter a valid number between 1 and 52.")
            continue

        partial_sequence.append(card)
        matching_seeds = search_for_partial_sequence(client, partial_sequence)

        if not matching_seeds:
            print("No matches found. Ending search.")
            break
        elif len(matching_seeds) == 1:
            print(f"\nSingle seed found in Index '{matching_seeds[0][0]}': {matching_seeds[0][1]}")
            print("Search complete.")
            break
        else:
            print(f"{len(matching_seeds)} seeds still match. Continue entering cards.")

if __name__ == "__main__":
    main()
