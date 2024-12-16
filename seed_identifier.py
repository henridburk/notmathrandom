import json

# Define the card suits and ranks for mapping
SUITS = {"C": "Clubs", "H": "Hearts", "S": "Spades", "D": "Diamonds"}
RANKS = {
    "A": "Ace", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6",
    "7": "7", "8": "8", "9": "9", "10": "10", "J": "Jack", "Q": "Queen", "K": "King"
}

def card_abbreviation_to_number(abbr):
    """Convert a card abbreviation (e.g., 'AC', '7H') to its corresponding number (1-52)."""
    try:
        rank_part = abbr[:-1]  # All characters except the last one (the suit)
        suit_part = abbr[-1]   # The last character (the suit)

        # Handle cases where rank_part is '10' (because '10' is two characters)
        if rank_part == "10":
            rank = "10"
        else:
            rank = rank_part.upper()

        suit = suit_part.upper()

        if rank not in RANKS or suit not in SUITS:
            raise ValueError(f"Invalid card abbreviation: {abbr}")

        # Determine the suit index and rank index
        suit_index = list(SUITS.keys()).index(suit)
        rank_index = list(RANKS.keys()).index(rank)

        # Calculate the card number
        card_number = suit_index * 13 + rank_index + 1
        return card_number

    except Exception as e:
        print(f"Error: {e}")
        return None

def load_card_sequences(file_path):
    """Load card sequences from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
        return None

def get_observed_cards():
    """Prompt the user to input the first 10 observed cards in abbreviated format."""
    print("Enter the first 10 observed cards in abbreviated format (e.g., 'AC' for Ace of Clubs, '7H' for 7 of Hearts):")
    observed_cards = []
    for i in range(4):
        while True:
            card_abbr = input(f"Card {i + 1}: ").strip()
            card_number = card_abbreviation_to_number(card_abbr)
            if card_number:
                observed_cards.append(card_number)
                break
            else:
                print("Invalid input. Please enter a valid card abbreviation (e.g., 'AC', '7H').")
    return observed_cards

def find_matching_seed(card_sequences, observed_cards):
    """Find the seed whose sequence matches the observed cards."""
    for seed, sequence in card_sequences.items():
        if sequence[:4] == observed_cards:
            return seed
    return None

def main():
    # Load the card sequences
    card_sequences = load_card_sequences('json/card_sequences.json')
    if card_sequences is None:
        return

    # Get the observed cards from the user
    observed_cards = get_observed_cards()
    print(f"Observed card numbers: {observed_cards}")

    # Find the matching seed
    matching_seed = find_matching_seed(card_sequences, observed_cards)

    if matching_seed:
        print(f"Matching seed found: {matching_seed}")
        print("Use this seed for future predictions.")
    else:
        print("No matching seed found. Please check your input and try again.")

if __name__ == "__main__":
    main()
