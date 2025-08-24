import random
from collections import namedtuple
from elasticsearch import Elasticsearch, exceptions
import logging

# Configuration
MAX_PLAYERS = 4  # Number of players
ES_HOST = "http://192.168.10.192:9200"
ES_USER = "elastic"
ES_PASS = "Maarsseveen1!"
INDEX_NAME = "card_sequences_v3"


# Logging Configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Named tuple to represent a player's hand
Hand = namedtuple("Hand", ["cards", "total"])

# Card values in blackjack
CARD_VALUES = {
    **{str(i): i for i in range(2, 11)},  # 2 to 10
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 11,  # Ace can be 11 or 1
}

# Generate the deck (1-52 mapped to card faces)
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
FACES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def generate_deck():
    deck = []
    for suit in SUITS:
        for face in FACES:
            deck.append(f"{face} of {suit}")
    return deck

deck = generate_deck()

def get_card_value(card):
    face = card.split(" ")[0]
    return CARD_VALUES[face]

def calculate_hand_total(cards):
    total = sum(get_card_value(card) for card in cards)
    # Adjust for Aces if total exceeds 21
    num_aces = sum(1 for card in cards if card.startswith("A"))
    while total > 21 and num_aces:
        total -= 10
        num_aces -= 1
    return total

def get_elasticsearch_client():
    """Create and return an Elasticsearch client with authentication."""
    return Elasticsearch(
        hosts=[ES_HOST],
        basic_auth=(ES_USER, ES_PASS),
        verify_certs=False,
        request_timeout=60
    )

def get_card_sequence_from_es(seed_key):
    """Retrieve the card sequence from Elasticsearch based on the seed key."""
    client = get_elasticsearch_client()
    try:
        response = client.search(
            index=INDEX_NAME,
            body={
                "query": {
                    "term": {"seed_key": f"{seed_key:.6f}"}
                },
                "_source": ["card_sequence"]
            },
            size=1
        )
        if response["hits"]["hits"]:
            sequence = response["hits"]["hits"][0]["_source"]["card_sequence"]
            return [int(card) for card in sequence.split()]
        else:
            logger.error(f"No sequence found for seed key: {seed_key}")
            return None
    except exceptions.ApiError as e:
        logger.error(f"Error querying Elasticsearch: {e}")
        return None

def synchronize_sequence(card_sequence):
    """Synchronize the sequence by matching the last 10 cards dealt."""
    last_10_cards = input("\nEnter the last 10 cards you've seen dealt (as numbers 1-52, separated by spaces): ").strip().split()
    last_10_cards = [int(card) for card in last_10_cards]
    
    start_index = -1
    for i in range(len(card_sequence) - len(last_10_cards)):
        if card_sequence[i:i + len(last_10_cards)] == last_10_cards:
            start_index = i + len(last_10_cards)
            break

    if start_index == -1:
        logger.error("Error: Could not synchronize with the card sequence. Please check the input.")
        return None
    else:
        print(f"Synchronization successful. Starting index in the sequence: {start_index}")
        return start_index

def deal_initial_hands(card_sequence, index):
    """Deal initial two-card hands to players and the dealer."""
    hands = []
    for _ in range(MAX_PLAYERS):
        player_cards = [deck[card_sequence[index] - 1], deck[card_sequence[index + 1] - 1]]
        hands.append(Hand(cards=player_cards, total=calculate_hand_total(player_cards)))
        index += 2
    
    dealer_cards = [deck[card_sequence[index] - 1], deck[card_sequence[index + 1] - 1]]
    dealer_hand = Hand(cards=dealer_cards, total=calculate_hand_total(dealer_cards))
    index += 2
    
    return hands, dealer_hand, index

def simulate_dealer_play(card_sequence, index, dealer_hand):
    """Simulate the dealer's play based on the standard blackjack rules."""
    while dealer_hand.total < 17:
        next_card = deck[card_sequence[index] - 1]
        dealer_hand.cards.append(next_card)
        dealer_hand = Hand(cards=dealer_hand.cards, total=calculate_hand_total(dealer_hand.cards))
        index += 1
    return dealer_hand, index

def predict_winners(hands, dealer_hand):
    """Determine which players win, lose, or push based on the dealer's final hand."""
    results = []
    for i, hand in enumerate(hands):
        if dealer_hand.total > 21:
            results.append((i + 1, "Win"))  # Dealer busts, player wins
        elif hand.total > dealer_hand.total:
            results.append((i + 1, "Win"))
        elif hand.total == dealer_hand.total:
            results.append((i + 1, "Push"))
        else:
            results.append((i + 1, "Lose"))
    return results

def main():
    # Input the seed key
    seed_key = float(input("Enter seed key: "))
    card_sequence = get_card_sequence_from_es(seed_key)
    
    if not card_sequence:
        return
    
    # Synchronize the sequence
    start_index = synchronize_sequence(card_sequence)
    if start_index is None:
        return

    index = start_index

    while True:
        # Deal initial hands
        hands, dealer_hand, index = deal_initial_hands(card_sequence, index)
        
        # Display initial hands
        print("\n--- Initial Hands ---")
        for i, hand in enumerate(hands):
            print(f"Player {i + 1} Hand: {hand.cards} (Total: {hand.total})")
        print(f"Dealer Initial Hand: {dealer_hand.cards} (Total: {dealer_hand.total})")

        # Simulate dealer play
        dealer_hand, index = simulate_dealer_play(card_sequence, index, dealer_hand)
        print(f"\nDealer Final Hand: {dealer_hand.cards} (Total: {dealer_hand.total})")

        # Predict winners
        results = predict_winners(hands, dealer_hand)
        for player, result in results:
            print(f"Player {player}: {result}")

        # Prompt for the next round or quit
        user_input = input("\nType 'done' to generate the next hand or 'q' to quit: ").strip().lower()
        if user_input == 'q':
            break

if __name__ == "__main__":
    main()
