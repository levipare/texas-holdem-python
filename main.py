import math
import random

import cpu_utils
import deck
import user
from display import *
from hand_utils import *

STARTING_BALANCE = 1000
TABLE_SIZE = 7



table_seats = [n for n in range(TABLE_SIZE)]


player_data = {
    'name': "You",
    'hand': [],
    'table_position': table_seats.pop(random.randrange(len(table_seats))),
    'balance': STARTING_BALANCE,
    'total_bet': 0,
    'current_round_bet': 0,
    'last_action': None,
    'folded': False,
    'all_in': False,
    'active': False,
    'winner': False,
}

cpus = cpu_utils.generate_cpu(table_seats, STARTING_BALANCE)

while True:
    game_deck = deck.create_and_shuffle()

    # Initial Dealing
    player_data["hand"] = generate_hand(game_deck)
    for cpu in cpus: cpu['hand'] = generate_hand(game_deck)

    all_pots = []
    community_cards = []
    bet_data = {
        'current_bet': 0,
        'last_raise': 0
        }

    finished_game = False


    def decision_loop(round_: int):
        def d(x):
            if x == 0: display_pre_flop(cpus, player_data, bet_data, total_bets)
            elif x == 1: display_flop(cpus, player_data, community_cards, bet_data, total_bets)
            elif x == 2: display_turn(cpus, player_data, community_cards, bet_data, total_bets)
            elif x == 3: display_river(cpus, player_data, community_cards, bet_data, total_bets)
        
        total_bets = 0
        for pot in all_pots: total_bets += pot[0] * len(pot[1])
        pots = []
        while True:
            active_players = list(filter(lambda c: not c['folded'] and not c['all_in'], cpus))
            if not player_data['folded'] and not player_data['all_in']: active_players.append(player_data)
            active_players.sort(key=lambda p: p['table_position'])
            for player in active_players:
                    action = ''
                    player_count = len(list(filter(lambda p: not p['folded'], active_players)))
                    if player['current_round_bet'] == bet_data['current_bet'] and player['last_action']: continue
                    player['active'] = True
                    d(round_)
                    if player['table_position'] == player_data['table_position']:
                        action = user.parse_action(bet_data, player_data)
                    else:
                        action = cpu_utils.update_cpu_bet(player, community_cards, bet_data, player_count)
                    player['active'] = False

                    # Handles pots
                    if action == 'bet':
                        pots.append([player['current_round_bet'], [player['name']]])
                    if action == 'call':
                        for pot in pots:
                            if player['name'] not in pot[1]: pot[1].append(player['name'])
                    elif action == 'raise':
                        for pot in pots:
                            if player['name'] not in pot[1]: pot[1].append(player['name'])
                        pots.append([bet_data['last_raise'], [player['name']]])
                    elif action == 'all_in':
                        all_in_amount = player['current_round_bet']

                        # pots = [pot, pot, pot]
                        # pot = [[bet, [A, B, C]]
                        for i, pot in enumerate(pots):
                            if pot[0] > all_in_amount:
                                pots.insert(i + 1, [pot[0] - all_in_amount, [player['name']]])
                                for name in pot[1]:
                                    pots[i + 1][1].append(name)
                                pot[0] = all_in_amount

                    sum_ = 0
                    for pot in pots: sum_ += pot[0] * len(pot[1])
                    for pot in all_pots: sum_ += pot[0] * len(pot[1])
                    total_bets = sum_

                
            # Checks if all players who are still in have met the current bet
            finished_round = True
            for p in active_players: 
                if p['current_round_bet'] != bet_data['current_bet']:
                    finished_round = False

            if finished_round:
                global finished_game
                if len(list(filter(lambda c: not c['folded'], active_players))) == 1: 
                    finished_game = True
        
                if round_ == 3: finished_game = True
                all_pots.extend(pots)
                # Resets temporary data fields for cpus and players
                bet_data.update({'current_bet': 0, 'last_raise': 0})
                for p in active_players:
                    p['total_bet'] += p['current_round_bet']
                    p['current_round_bet'] = 0
                    if not p['folded'] and not p['all_in']: p['last_action'] = None
                break


    ###### PRE-FLOP ######
    # Loop through table seats of table
    decision_loop(0)

    if not finished_game:
        ###### FLOP ######
        # Burn 1 card
        deck.draw_card(game_deck)
        # Turn 3 cards for the community cards
        community_cards = [deck.draw_card(game_deck) for _ in range(3)]

        decision_loop(1)

    if not finished_game:
        ###### TURN ######
        community_cards.append(deck.draw_card(game_deck))
        decision_loop(2)

    if not finished_game:
        ###### RIVER ######
        community_cards.append(deck.draw_card(game_deck))
        decision_loop(3)



    ###### SHOWDOWN ######
    for pot in all_pots:
        pot_players = pot[1]
        not_folded = list(filter(lambda cpu: not cpu['folded'] and cpu['name'] in pot_players, cpus))
        if not player_data['folded'] and player_data['name'] in pot_players: not_folded.append(player_data)

        winners = [not_folded[0]]
        for i in range(len(not_folded) - 1):
            p1 = evaluate_hand(winners[0]['hand'], community_cards)
            p2 = evaluate_hand(not_folded[i + 1]['hand'], community_cards)
            comparison = compare_hands(p1, p2)
            if comparison == False:
                winners = [not_folded[i + 1]]
            elif comparison == None:
                winners.append(not_folded[i + 1])

        # Payouts for winner/winners
        winnings = pot[0] * len(pot[1])
        for winner in winners: 
            winner['winner'] = True
            winner['balance'] += math.floor(winnings / len(winners))

    sum_ = 0
    for pot in all_pots: sum_ += pot[0] * len(pot[1])
    display_showdown(cpus, player_data, community_cards, sum_)

    # Sanitize
    if player_data['balance'] == 0:
        print('YOU SUCK!')
        quit()

    cpus = list(filter(lambda cpu: cpu['balance'] > 0, cpus))
    if len(cpus) == 0: 
        print('YOU WON!')
        quit()

    play_again = input("Keep playing? (y/n) ")
    if play_again.lower() == 'n': quit()

    for player in [player_data] + cpus:
        player.update({
            'hand': [],
            'total_bet': 0,
            'current_round_bet': 0,
            'last_action': None,
            'folded': False,
            'all_in': False,
            'active': False,
            'winner': False})
    

