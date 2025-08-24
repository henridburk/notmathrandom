import subprocess
import tempfile
import os
import time
import logging
from datetime import datetime, timezone
from elasticsearch import Elasticsearch, helpers, ApiError
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

# Configuration Variables
START = 0.000        # Start of the os.clock range (in seconds)
END = 0.999          # End of the os.clock range (in seconds)
STEP = 1e-3             # Step size (microseconds)
MAX_CARDS = 200         # Maximum number of cards to generate per seed
INDEX_NAME = "card_sequences_7d2"  # Elasticsearch index name
BATCH_SIZE = 2000       # Number of documents to send to Elasticsearch in a single batch
MAX_WORKERS = 4         # Number of threads for parallel execution
SEEDS_PER_LUA_RUN = 10  # Number of seeds to process in a single iteration
NUM_SHARDS = 4          # Number of shards for the Elasticsearch index

# Logging Configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Elasticsearch Configuration
def get_elasticsearch_client():
    """Create and return an Elasticsearch client."""
    return Elasticsearch(
        hosts=["http://192.168.10.192:9200"],
        basic_auth=("elastic", "Maarsseveen1!"),
        verify_certs=False,
        request_timeout=60
    )

def create_index(client, index_name):
    """Create the index with appropriate settings and mappings, including whitespace analyzer for card_sequence."""
    index_body = {
        "settings": {
            "number_of_shards": NUM_SHARDS,
            "number_of_replicas": 1,
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
                    "analyzer": "whitespace_analyzer"
                },
                "timestamp": {"type": "date"}
            }
        }
    }

    try:
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, body=index_body)
            logger.info(f"Index '{index_name}' created successfully with {NUM_SHARDS} shards and whitespace analyzer.")
        else:
            logger.info(f"Index '{index_name}' already exists.")
    except ApiError as e:
        logger.error(f"Error creating index: {e}")

def generate_card_sequences(start, end, step, num_cards=MAX_CARDS):
    """Generate sequences of random cards using clock values and seeds directly in Lua."""
    lua_script_content = f"""
    local start = {start}
    local end_time = {end}
    local step = {step}
    local num_cards = {num_cards}

    local clock_values = {{}}
    local current = start
    while current <= end_time do
        table.insert(clock_values, current)
        current = current + step
    end

    for _, clock in ipairs(clock_values) do
        local seed = clock * 100000000000
        math.randomseed(seed)

        local card_sequence = {{}}
        for i = 1, num_cards do
            table.insert(card_sequence, math.random(1, 52))
        end

        io.write(string.format("%.12f", clock), ": ")
        for i, card in ipairs(card_sequence) do
            io.write(card)
            if i < #card_sequence then
                io.write(" ")
            end
        end
        io.write("\\n")
    end
    """

    with tempfile.NamedTemporaryFile(suffix=".lua", mode="w", delete=False) as tmp_lua:
        tmp_lua.write(lua_script_content)
        tmp_lua_path = tmp_lua.name

    logger.debug("Lua script content:\n" + lua_script_content)

    try:
        logger.debug("Generating card sequences with clock values in Lua")
        result = subprocess.run(
            ["lua", tmp_lua_path],
            capture_output=True,
            text=True,
            check=True
        )
        output_lines = result.stdout.strip().split("\n")
        sequences = []
        for line in output_lines:
            clock, card_sequence = line.split(": ")
            sequences.append((float(clock), card_sequence))
        return sequences
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating card sequences: {e}\n{e.stderr}")
        logger.error(traceback.format_exc())
        return []
    finally:
        os.remove(tmp_lua_path)

def process_seeds(client):
    """Process seeds generated in Lua and write to Elasticsearch incrementally."""
    logger.info("Generating clock values and card sequences in Lua")
    seed_card_pairs = generate_card_sequences(START, END, STEP, MAX_CARDS)

    documents = []
    for clock_value, card_sequence in seed_card_pairs:
        documents.append({
            "_index": INDEX_NAME,
            "_source": {
                "seed_key": f"{clock_value:.12f}",
                "card_sequence": card_sequence,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec='seconds')
            }
        })

        # Batch indexing every BATCH_SIZE documents
        if len(documents) >= BATCH_SIZE:
            helpers.bulk(client, documents)
            logger.info(f"Indexed batch of {len(documents)} documents.")
            documents.clear()

    # Index any remaining documents
    if documents:
        helpers.bulk(client, documents)
        logger.info(f"Indexed final batch of {len(documents)} documents.")

def main():
    logger.info("Starting the seed generation process.")
    client = get_elasticsearch_client()
    create_index(client, INDEX_NAME)

    process_seeds(client)
    logger.info("Seed generation process completed.")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    logger.info(f"Execution Time: {end_time - start_time:.2f} seconds")
