import random


def create() -> list:
    """Creates a 52 card deck and returns it as a list of tuples."""
    deck = []
    for s in ['h', 'd', 'c', 's']:
        for n in range(2, 11 ):
            deck.append((n, s))
        for f in ['J', 'Q', 'K', 'A']:
            deck.append((f, s))
    return deck


def shuffle(deck: list) -> list:
    """Shuffles a supplied deck of cards."""
    random.shuffle(deck)
    return deck


def create_and_shuffle() -> list:
    """Return a shuffled 52 card deck."""
    return shuffle(create())


def draw_card(deck: list) -> tuple:
    """Draws a card from the deck(removing it from the list) and returns the drawn card."""
    return deck.pop()
