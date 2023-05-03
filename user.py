def parse_action(bet_data: dict, player: dict):
    """Asks for choice from user and applies the appropiate operation"""
    action = None
    if player['balance'] < bet_data['current_bet'] - player['current_round_bet']:
        while True:
                a = input("All in (a), Fold (f): ").lower()
                if a in ['a', 'f']:
                    action = {'a': 'all in', 'f': 'fold'}[a]
                    break
                else:
                    print("Invalid Input")
    elif bet_data['current_bet'] == 0:
        while True:
            a = input("Check (c), Bet (b), Fold (f): ").lower()
            if a in ['c', 'b', 'f']:
                action = {'c': 'check', 'b': 'bet', 'f': 'fold'}[a]
                break
            else:
                print("Invalid Option")
    elif bet_data['last_raise'] + bet_data['current_bet'] >= player['balance'] + player['current_round_bet']:
        while True:
            a = input("Call (c), Fold (f): ").lower()
            if a in ['c', 'f']:
                action = {'c': 'call', 'f': 'fold'}[a]
                break
            else:
                print("Invalid Option")
    else:
        while True:
            a = input("Call (c), Raise (r), Fold (f): ").lower()
            if a in ['c', 'r', 'f']:
                action = {'c': 'call', 'r': 'raise', 'f': 'fold'}[a]
                break
            else:
                print("Invalid Option")
    
    alt_action = ''
    if action == 'fold':
        player['last_action'] = action
        player['folded'] = True
    elif action == 'check':
        player['last_action'] = action
    elif action == 'bet':
        while True:
            try:
                bet = int(input(f"You have ${player['balance']} | Enter a bet amount: "))
                if 1 <= bet < player['balance']:
                    player['last_action'] = action
                    player['balance'] -= bet
                    player['current_round_bet'] = bet
                    bet_data['current_bet'] = bet
                    bet_data['last_raise'] = bet
                    break
                elif bet > player['balance']:
                    print(f"The max you can bet is {player['balance']}")
                elif bet == player['balance']:
                    bet_data['current_bet'] = player['balance']
                    bet_data['last_raise'] = bet
                    alt_action = 'all in'
                    break
            except ValueError:
                print('Invalid Input')
    elif action == 'raise':
        while True:
            try:
                raise_amount = int(input(f"You have ${player['balance']} | Enter an amount to raise: "))
                available_funds = player['balance'] - bet_data['current_bet'] + player['current_round_bet']
                if bet_data['last_raise'] <= raise_amount < available_funds:
                    player['last_action'] = action
                    player['balance'] -= raise_amount + bet_data['current_bet'] - player['current_round_bet']
                    player['current_round_bet'] = bet_data['current_bet'] + raise_amount
                    bet_data['current_bet'] += raise_amount
                    bet_data['last_raise'] = raise_amount
                    break
                elif bet_data['last_raise'] > raise_amount:
                    print(f"You must raise by atleast {bet_data['last_raise']}")
                elif raise_amount > available_funds: 
                    print(f"The max you can raise is {available_funds}")
                elif raise_amount == available_funds:
                    bet_data['current_bet'] += raise_amount
                    bet_data['last_raise'] = raise_amount
                    alt_action = 'all in'
                    break
            except ValueError:
                print("Invalid Input")
    elif action == 'call':
        while True:
            player['last_action'] = action
            player['balance'] -= bet_data['current_bet'] - player['current_round_bet']
            player['current_round_bet'] = bet_data['current_bet']
            break
    if action == 'all in' or alt_action == 'all in':
        player['last_action'] = 'all_in'
        player['all_in'] = True
        player['current_round_bet'] += player['balance'] 
        player['balance'] = 0

    return action
                    
                    

                    

            


            


