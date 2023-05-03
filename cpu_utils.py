import random
import time

import deck
from hand_utils import *


def generate_cpu(seats: list, b: int = 100) -> list[dict]:
    """
    Generates (n) number of cpu users.
    Requires deck (d) of cards.
    Can supply a starting balance (b).
    """
    names = ['Walter', 'Gus', 'Mike', 'Skyler', 'Jesse', 'Saul', 'Hank', 'Marie', 'Tuco', 'Jane', 'Chuck', 'Kim', 'Howard']

    cpu_users = []
    for _ in range(len(seats)):
        cpu_users.append({
            'name': names.pop(random.randrange(len(names))),
            'hand': [],
            'table_position': seats.pop(0),
            'balance': b,
            'total_bet': 0,
            'current_round_bet': 0,
            'last_action': None,
            'folded': False,
            'all_in': False,
            'active': False,
            'winner': False
        })
    return cpu_users

def win_simulation(hand: list, community_cards: list, player_count: int) -> float:
    num = 10000
    wins = 0
    for _ in range(num):
        d = deck.create_and_shuffle()
        cc = list(community_cards)
        for _ in range(5 - len(community_cards)):
            cc.append(deck.draw_card(d))
        players = [generate_hand(d) for _ in range(player_count - 1)]
        players.append(hand)
        w = [players[0]]
        for i in range(len(players) - 1):
            p1 = evaluate_hand(w[0], cc)
            p2 = evaluate_hand(players[i + 1], cc)
            comparison = compare_hands(p1, p2)
            if comparison == False:
                w = [players[i + 1]]
            elif comparison == None:
                w.append(players[i + 1])

        if hand in w and len(w) == 1: wins += 1
    return wins / num


def update_cpu_bet(cpu: dict, community_cards: list, bet_data: dict, player_count: int):
    start_time = time.time()
    win_percentage = win_simulation(cpu['hand'], community_cards, player_count)
    time_elapsed = time.time() - start_time
    if time_elapsed < 3:
        time.sleep(3 - time_elapsed)
    decision_eval = win_percentage > 1 / player_count / 2

    action = ''
    if bet_data['current_bet'] == 0 and not decision_eval:
        # Check if bad hand but no bets
        cpu['last_action'] = 'check'
        action = 'check'
    elif decision_eval: 
        raise_amount = bet_data['last_raise'] or 10
        bet = 10
        # Bet
        if bet_data['current_bet'] == 0 and cpu['balance'] >= bet:
            cpu['last_action'] = "bet"
            cpu['balance'] -= bet
            bet_data['current_bet'] = bet
            bet_data['last_raise'] = bet
            cpu['current_round_bet'] = bet
            action = 'bet'
        # Raise
        elif (win_percentage > 1 / player_count
            and cpu['balance'] >= raise_amount + bet_data['current_bet'] - cpu['current_round_bet']
            and cpu['last_action'] != "raise"):
            cpu['last_action'] = "raise"
            cpu['balance'] -= raise_amount + bet_data['current_bet'] - cpu['current_round_bet']
            bet_data['current_bet'] += raise_amount
            cpu['current_round_bet'] = bet_data['current_bet'] 
            action = 'raise'

        # Call
        elif cpu['balance'] > bet_data['current_bet'] - cpu['current_round_bet'] and cpu['balance'] > 3 * (bet_data['current_bet'] - cpu['current_round_bet']):
            cpu['last_action'] = "call"
            cpu['balance'] -= bet_data['current_bet'] - cpu['current_round_bet']
            cpu['current_round_bet'] = bet_data['current_bet']
            action = 'call'
        else:
            # All in if very good hand
            if win_percentage > 1 / player_count * 2:
                cpu['last_action'] = 'all_in'
                cpu['all_in'] = True
                cpu['current_round_bet'] += cpu['balance'] 
                cpu['balance'] = 0
                action = 'all_in'
            # Fold if good hand but can't afford
            else:
                cpu['last_action'] = "fold"
                cpu['folded'] = True
                action = 'fold'
    else:
        # Fold if bad hand
        cpu['last_action'] = "fold"
        cpu['folded'] = True
        action = 'fold'
    
    return action

    

if __name__ == '__main__':
    
    d = deck.create_and_shuffle()
    hand = [(2, 'd'), (3, 'h')]
    co = [(4, 'h'), (5, 'h'), ('A', 'h'), (8, 'd'), (7, 's')]
    for card in hand: d.remove(card)
    for card in co: d.remove(card)

    other_players = 4

    num = 10000
    wins = 0
    for _ in range(num):
        temp_d = list(d)
        deck.shuffle(temp_d)
        co_copy = list(co)
        for _ in range(5 - len(co)): co_copy.append(deck.draw_card(temp_d))
        players = [generate_hand(temp_d) for _ in range(other_players)]
        players.append(hand)
        winners = [players[0]]
        for i in range(len(players) - 1):
            p1 = evaluate_hand(winners[0], co_copy)
            p2 = evaluate_hand(players[i + 1], co_copy)
            comparison = compare_hands(p1, p2)
            if comparison == False:
                winners = [players[i + 1]]
            elif comparison == None:
                winners.append(players[i + 1])

        if hand in winners and len(winners) == 1: wins += 1
    print(f"{wins / num * 100:.2f}", f"{1 / (other_players + 1) / 2 * 100:2f}",  hand, co)
    
