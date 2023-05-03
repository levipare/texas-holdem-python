import deck


def generate_hand(d: list) -> list:
    """Generates 2 card hand."""
    return [deck.draw_card(d), deck.draw_card(d)]


def convert_suite(s: str) -> str:
    return {'s': '♠', 'c': '♣', 'd': '♦', 'h': '♥'}[s]


def display_hand(hand: tuple, name: str = "Anon"):
    print('\033[92m' + f"{name}'s Hand:" + '\033[0m', 
    hand[0][0], convert_suite(hand[0][1]), hand[1][0], 
    convert_suite(hand[1][1]))

def evaluate_hand(h: list, c: list ) -> dict[str, list]:
    hand = h + c
    for i, card in enumerate(hand):
        if card[0] in ['J', 'Q', 'K', 'A']:
            face_values = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
            hand[i] = (face_values[card[0]], card[1])
    hand.sort(key=lambda c: c[0], reverse=True)
    hand_values = list(map(lambda c: c[0], hand))
    result = {'hand_rank': None, 'high_card': hand_values[0:5]}

    # Royal Flush
    for suite in ['h', 's', 'c', 'd']:
        if ((14, suite) in hand
            and (10, suite) in hand
            and (11, suite) in hand
            and (12, suite) in hand
            and (13, suite) in hand):
                result['hand_rank'] = 'Royal Flush'
                return result


    # Straight Flush
    for card in hand:
        v = card[0]
        s = card[1]
        if ((v + 1, s) in hand
        and (v + 2, s) in hand
        and (v + 3, s) in hand
        and (v + 4, s) in hand):
            result['hand_rank'] = 'Straight Flush'
            result['high_card'] = [v]
            return result
        elif (v == 14
        and (2, s) in hand
        and (3, s) in hand
        and (4, s) in hand
        and (5, s) in hand):
            result['hand_rank'] = 'Straight Flush'
            result['high_card'] = [1]
            return result

    # Four of a kind
    for card in hand:
        if(len(list(filter(lambda c: c[0] == card[0], hand))) == 4):
            b = list(filter(lambda v: v != card[0], map(lambda c: c[0], hand)))
            result['hand_rank'] = 'Four of a kind'
            result['high_card'] = [card[0], max(b)]
            return result

    # Full House
    for card in hand:
        if len(list(filter(lambda c: c[0] == card[0], hand))) == 3: 
            for kard in hand:
                if len(list(filter(lambda c: c[0] == kard[0] and card[0] != kard[0], hand))) >= 2: 
                    result['hand_rank'] = 'Full House'
                    result['high_card'] = [card[0], kard[0]]
                    return result 

    # Flush
    for suite in ['h', 's', 'c', 'd']:
        f = list(filter(lambda c: c[1] == suite, hand)) # All same suit cards
        if len(f) >= 5:   
            result['hand_rank'] = 'Flush'
            result['high_card'] = [max(list(map(lambda c: c[0], f)))]
            return result 


    # Straight
    for v in hand_values:
        if (v + 1 in hand_values
        and v + 2 in hand_values
        and v + 3 in hand_values
        and v + 4 in hand_values):
            result['hand_rank'] = 'Straight'
            result['high_card'] = [v]
            return result
        elif (v == 14
        and 2 in hand_values
        and 3 in hand_values
        and 4 in hand_values
        and 5 in hand_values):
            result['hand_rank'] = 'Straight'
            result['high_card'] = [1]
            return result


    # Three of a kind
    for card in hand:
        if(len(list(filter(lambda c: c[0] == card[0], hand))) == 3):
            b = list(filter(lambda v: v != card[0] , map(lambda c: c[0], hand)))
            result['hand_rank'] = 'Three of a kind'
            result['high_card'] = [card[0], b[0], b[1]]  
            return result


    # Two Pair
    for card in hand:
        if len(list(filter(lambda c: c[0] == card[0], hand))) == 2: 
            for kard in hand:
                if len(list(filter(lambda c: c[0] == kard[0] and card[0] != kard[0], hand))) == 2:
                    b = list(filter(lambda v: v != card[0] and v != kard[0] , map(lambda c: c[0], hand))) 
                    result['hand_rank'] = 'Two Pair'
                    result['high_card'] = [max(card[0], kard[0]), min(card[0], kard[0]), max(b)]
                    return result

    
    # Pair
    for card in hand:
        if len(list(filter(lambda c: c[0] == card[0], hand))) == 2: 
                b = list(filter(lambda v: v != card[0], map(lambda c: c[0], hand)))
                result['hand_rank'] = 'Pair'
                result['high_card'] = [card[0], b[0], b[1], b[2]]
                return result
    
    return result


def compare_hands(hand_1: dict[str, list], hand_2: dict[str, list]) -> bool | None:
    """
    Takes in the evaluation of two hands and returns:\n
    True if the first hand beats the second.\n
    False if the first loses\n
    None if they tie
    """
    look_up = {
        'Royal Flush': 9,
        'Straight Flush': 8,
        'Four of a kind': 7,
        'Full House': 6,
        'Flush': 5,
        'Straight': 4,
        'Three of a kind': 3,
        'Two Pair': 2,
        'Pair': 1,
        None: 0
    }

    if look_up[hand_1['hand_rank']] > look_up[hand_2['hand_rank']]:
        return True
    elif look_up[hand_1['hand_rank']] < look_up[hand_2['hand_rank']]:
        return False

    for i, e in enumerate(hand_1['high_card']):
        if e > hand_2['high_card'][i]: # [card[0], b[0], b[1], b[2]]
            return True
        elif e < hand_2['high_card'][i]:
            return False

if __name__ == '__main__':
    d = deck.create_and_shuffle()
    p1 = [(2, 'd'), (3, 'h')]
    co = [(4, 'h'), (5, 'h'), ('A', 'h'), (8, 'd'), (7, 's')]

    for card in p1 + co: d.remove(card)
    p2 = generate_hand(d)

    p1e = evaluate_hand(p1, co)
    p2e = evaluate_hand(p2, co)
    print(p1)
    print(p2)
    print(co)
    print(p1e)
    print(p2e)
    print(compare_hands(p1e, p2e))


