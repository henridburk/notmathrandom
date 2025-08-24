import logging
from elasticsearch import Elasticsearch, exceptions

# Configuration
ES_HOST = "http://192.168.10.192:9200"
ES_USER = "elastic"
ES_PASS = "Maarsseveen1!"

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_elasticsearch_client():
    """Create and return an Elasticsearch client with authentication."""
    return Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        request_timeout=60
    )

def list_indices(client):
    """List all indices in the Elasticsearch cluster."""
    try:
        indices = client.indices.get_alias(index="*")  # Corrected to use 'index' as a keyword argument
        index_list = list(indices.keys())
        return index_list
    except exceptions.ApiError as e:
        logger.error(f"Error fetching indices: {e}")
        return []

def prompt_indices_to_delete(index_list):
    """Prompt the user to select indices to delete."""
    print("\nAvailable Indices:")
    for i, index in enumerate(index_list):
        print(f"{i + 1}. {index}")

    selected_indices = input("\nEnter the numbers of the indices to delete (comma-separated, e.g., 1,3,5): ").strip()
    selected_indices = [int(num.strip()) for num in selected_indices.split(",") if num.strip().isdigit()]

    indices_to_delete = [index_list[i - 1] for i in selected_indices if 0 < i <= len(index_list)]
    return indices_to_delete

def confirm_and_delete_indices(client, indices_to_delete):
    """Confirm and delete the selected indices."""
    if not indices_to_delete:
        print("No indices selected for deletion.")
        return

    print("\nYou have selected the following indices for deletion:")
    for index in indices_to_delete:
        print(f"- {index}")

    confirmation = input("\nAre you sure you want to delete these indices? (yes/no): ").strip().lower()
    if confirmation == "yes":
        for index in indices_to_delete:
            try:
                client.indices.delete(index=index)
                logger.info(f"Index '{index}' deleted successfully.")
            except exceptions.ApiError as e:
                logger.error(f"Error deleting index '{index}': {e}")
    else:
        print("Operation cancelled. No indices were deleted.")

def main():
    client = get_elasticsearch_client()
    indices = list_indices(client)

    if not indices:
        print("No indices found.")
        return

    indices_to_delete = prompt_indices_to_delete(indices)
    confirm_and_delete_indices(client, indices_to_delete)

if __name__ == "__main__":
    main()
