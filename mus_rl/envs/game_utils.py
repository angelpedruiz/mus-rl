import random
from collections import Counter

# Define rank and suits
RANKS = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
SUITS = ['oros', 'copas', 'espadas', 'bastos']

Card = tuple[int, str]

def build_deck() -> list[Card]:
    """Builds an ordered deck of cards with the defined ranks and suits."""
    deck = [(rank, suit) for rank in RANKS for suit in SUITS]
    return deck

def deal_cards(num_players: int=4, cards_per_player: int=4) -> list[list[Card]]:
    """
    Shuffle the deck and deal cards to players.

    Args:
        num_players (int): Number of players (default 4).
        cards_per_player (int): Cards dealt per player (default 4).

    Returns:
        List[List[Card]]: List of hands, each a list of Card tuples.
    """
    deck = build_deck()
    random.shuffle(deck)
    
    hands = []
    for _ in range(num_players):
        hand = [deck.pop() for _ in range(cards_per_player)]
        hands.append(hand)
    
    return hands

def card_str(card: Card) -> str:
    """
    Convert card tuple to a human-readable string.

    Args:
        card (Card): The card tuple (rank, suit).

    Returns:
        str: Human-readable string like 'As of oros' or 'Caballo of espadas'.
    """
    rank_names = {
        1: "As",
        10: "Sota",
        11: "Caballo",
        12: "Rey"
    }
    rank = rank_names.get(card[0], str(card[0]))
    return f"{rank} de {card[1]}"

def hand_str(hand: list[Card]) -> str:
    """
    Convert a list of cards to a readable string.

    Args:
        hand (List[Card]): List of cards.

    Returns:
        str: Concatenated human-readable string of cards.
    """
    return ', '.join(card_str(card) for card in hand)

def normalize_card_rank(rank):
    """
    Normalize Mus card values:
    - 3s are treated as 12s
    - 2s are treated as 1s

    Args:
        rank (int): Raw rank of the card (1 to 12)

    Returns:
        int: Normalized value
    """
    if rank == 3:
        return 12
    elif rank == 2:
        return 1
    return rank

def sort_hand_desc(hand):
    """
    Sort a hand from highest to lowest, applying normalization.

    Args:
        hand (List[Tuple[int, str]]): List of (rank, suit)

    Returns:
        List[int]: Sorted normalized ranks (descending)
    """
    normalized = [normalize_card_rank(card[0]) for card in hand]
    return sorted(normalized, reverse=True)

def evaluate_grande(hands, mano_index):
    """
    Evaluate the 'Grande' phase (highest hand wins),
    with tie-breaking based on seating order (mano > postre).

    Args:
        hands (List[List[Card]]): Each player's hand.
        mano_index (int): Index of the 'mano' (first player in round).

    Returns:
        int: Index of the winning player.
    """
    sorted_hands = [sort_hand_desc(hand) for hand in hands]
    best = max(sorted_hands)

    tied_indices = [i for i, h in enumerate(sorted_hands) if h == best]

    # If tie, break by seating order starting from mano
    seating_order = [(mano_index + i) % len(hands) for i in range(len(hands))]
    for idx in seating_order:
        if idx in tied_indices:
            return idx
        
def sort_hand_asc(hand):
    """
    Sort a hand from lowest to highest, applying normalization.

    Args:
        hand (List[Tuple[int, str]]): List of (rank, suit)

    Returns:
        List[int]: Sorted normalized ranks (ascending)
    """
    normalized = [normalize_card_rank(card[0]) for card in hand]
    return sorted(normalized)

def evaluate_chica(hands, mano_index):
    """
    Evaluate the 'Chica' phase (lowest hand wins),
    with tie-breaking based on seating order (mano > postre).

    Args:
        hands (List[List[Card]]): Each player's hand.
        mano_index (int): Index of the 'mano' (first player in round).

    Returns:
        int: Index of the winning player.
    """
    sorted_hands = [sort_hand_asc(hand) for hand in hands]
    best = min(sorted_hands)

    tied_indices = [i for i, h in enumerate(sorted_hands) if h == best]

    # Tie-breaking by seating order
    seating_order = [(mano_index + i) % len(hands) for i in range(len(hands))]
    for idx in seating_order:
        if idx in tied_indices:
            return idx
        
def get_pares_profile(hand):
    """
    Given a hand, return a profile describing its pairs type and strength.

    Returns:
        (int, List[int]):
            - strength: 0 (no pares), 1 (par), 2 (medias), 3 (duples)
            - values: sorted relevant values to break ties
    """
    counts = Counter([normalize_card_rank(card[0]) for card in hand])
    count_groups = {}
    for val, freq in counts.items():
        count_groups.setdefault(freq, []).append(val)

    if 2 in count_groups and len(count_groups[2]) == 2:
        # Duples: two pairs
        vals = sorted(count_groups[2], reverse=True)
        return 3, vals
    elif 3 in count_groups:
        # Medias: three of a kind
        vals = [max(count_groups[3])]
        return 2, vals
    elif 2 in count_groups:
        # Par simple
        vals = [max(count_groups[2])]
        return 1, vals
    else:
        return 0, []
    
def evaluate_pares(hands, mano_index):
    """
    Evaluate the 'Pares' phase with tie-breaking.

    Args:
        hands (List[List[Card]]): Each player's hand.
        mano_index (int): Player with highest priority in tie.

    Returns:
        int or None: Index of winner, or None if no one has pares
    """
    profiles = [get_pares_profile(hand) for hand in hands]
    strengths = [p[0] for p in profiles]
    best_strength = max(strengths)

    if best_strength == 0:
        return None  # No pares

    # Get all players with best strength
    tied_indices = [
        i for i, (s, _) in enumerate(profiles) if s == best_strength
    ]

    # Among those, get the best tie-break value
    best_value = max([profiles[i][1] for i in tied_indices])
    final_tied = [
        i for i in tied_indices if profiles[i][1] == best_value
    ]

    # Break remaining tie by seating order
    seating_order = [(mano_index + i) % len(hands) for i in range(len(hands))]
    for idx in seating_order:
        if idx in final_tied:
            return idx
        
def juego_points(rank):
    """
    Convert rank to juego value:
    - 10, 11, 12 → 10 points
    - 1–7 → face value (after normalization)

    Args:
        rank (int): Normalized rank (1–12)

    Returns:
        int: Point value (1–10)
    """
    return 10 if rank >= 10 else rank
    
def evaluate_juego(hands, mano_index):
    """
    Evaluate the 'Juego' phase with Mus-specific score ranking.
    Tie-breaking based on seating order.

    Args:
        hands (List[List[Card]]): Player hands.
        mano_index (int): Player with tie-breaking priority.

    Returns:
        int or None: Winner index, or None if no one has juego.
    """
    def hand_total(hand):
        return sum(juego_points(normalize_card_rank(card[0])) for card in hand)

    scores = [hand_total(hand) for hand in hands]
    has_juego = [score >= 31 for score in scores]

    if not any(has_juego):
        return None  # No one has juego

    # Juego ranking: 31 > 32 > 40 > 39 > ... > 33
    juego_ranking = [31, 32] + list(range(40, 32, -1))

    for target_score in juego_ranking:
        tied = [i for i, score in enumerate(scores) if has_juego[i] and score == target_score]
        if tied:
            # Break tie with seating order
            seating_order = [(mano_index + i) % len(hands) for i in range(len(hands))]
            for idx in seating_order:
                if idx in tied:
                    return idx
                
def evaluate_punto(hands, mano_index):
    """
    Evaluate the 'Punto' phase (fallback when no Juego).
    Highest hand total wins. Tie-breaking by seating order.

    Args:
        hands (List[List[Card]]): Player hands.
        mano_index (int): Index of the 'mano'.

    Returns:
        int: Index of the player who wins Punto.
    """
    totals = [
        sum(juego_points(normalize_card_rank(card[0])) for card in hand)
        for hand in hands
    ]

    best_total = max(totals)
    tied_indices = [i for i, t in enumerate(totals) if t == best_total]

    seating_order = [(mano_index + i) % len(hands) for i in range(len(hands))]
    for idx in seating_order:
        if idx in tied_indices:
            return idx
