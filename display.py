from functools import reduce

import cpu_utils
import deck
from hand_utils import *

DISPLAY_WIDTH = 140
DISPLAY_HEIGHT = 30

"""
ANSI Escape sequences were found here:
https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""

print(f"\033[8;{DISPLAY_HEIGHT+2};{DISPLAY_WIDTH}t")

def create_card(card: tuple) -> list[str]:
    return ["┏━━━━━━━━━━━┓",
            f"┃ {card[0]}       {'' if card[0] == 10 else ' '} ┃",
            "┃           ┃",
            "┃           ┃",
            f"┃     {convert_suite(card[1])}     ┃",
            "┃           ┃",
            "┃           ┃",
            f"┃       {'' if card[0] == 10 else ' '} {card[0]} ┃",
            "┗━━━━━━━━━━━┛"]

def create_blank_card() -> list[str]:
    return ["┏━━━━━━━━━━━┓",
            "┃ ▒▒▒▒▒▒▒▒▒ ┃",
            "┃ ▒▒▒▒▒▒▒▒▒ ┃",
            "┃ ▒▒▒▒▒▒▒▒▒ ┃",
            "┃ ▒▒▒▒▒▒▒▒▒ ┃",
            "┃ ▒▒▒▒▒▒▒▒▒ ┃",
            "┃ ▒▒▒▒▒▒▒▒▒ ┃",
            "┃ ▒▒▒▒▒▒▒▒▒ ┃",
            "┗━━━━━━━━━━━┛"]


def create_cpu_card(card: tuple) -> list[str]:
    return [
        "╭─────╮",
        f"│{card[0]}  {'' if card[0] == 10 else ' '} │",
        f"│  {convert_suite(card[1])}  │",
        f"│  {'' if card[0] == 10 else ' '} {card[0]}│",
        "╰─────╯"]

def create_blank_cpu_card():
    return [
        "╭─────╮",
        "│▒▒▒▒▒│",
        "│▒▒▒▒▒│",
        "│▒▒▒▒▒│",
        "╰─────╯"]
            

def create_board() -> list[str]:
    width = DISPLAY_WIDTH
    height = DISPLAY_HEIGHT
    box = []
    for row in range(height):
        row_str = ""
        for column in range(width):
            if row == 0 and column == 0: row_str += '╔'
            elif row == 0 and column == width - 1: row_str += '╗'
            elif row == height - 1 and column == 0: row_str += '╚'
            elif row == height - 1 and column == width - 1: row_str += '╝'
            elif row == 0 or row == height - 1: row_str += '═'
            elif column == 0 or column == width - 1: row_str += '║'
            else: row_str += ' '
        box.append(row_str)
    return {'board': box, 'styles': []}


def draw_object(obj_: list[str], board_dict: dict, x: int, y: int, style = False, center = False):
    """
    Positions object's top left corner at the given (x, y) coordinates.
    Takes in optional style arguments which are seperated by "+" ex. "red+bold+underline"
    """
    board = board_dict['board']
    X = x

    for row in range(len(board)):
        if y <= row < y + len(obj_):
            if center:
                x = X - len(obj_[row - y]) // 2
    
            row_str = board[row]
            board[row] = row_str[:x] + obj_[row - y] + row_str[len(obj_[row - y]) + x:]
            if style:
                board_dict['styles'].append([row, x, len(obj_[row - y]) + x, style])

def apply_colors(board_dict: dict):
    applied = list(board_dict['board'])
    style_look_up = {
        'red': "31",
        'blue': "34",
        'green': "32",
        'underline': "4",
        'bold': "1",
        'dim': "2",
        'invert': "7"
    }

    for row in range(len(applied)):
        row_styles = list(filter(lambda c: c[0] == row, board_dict['styles']))
        if not row_styles: continue

        for i, style in enumerate(row_styles):
            style_list = style[3].split('+')
            style_str = "\033["
            for i_, n in enumerate(style_list):
                if n in style_look_up:
                    style_str += style_look_up[n] + (';' if i_ < len(style_list) - 1 else '')
            row_styles[i][3] = style_str + 'm'
    
        row_list = list(applied[row])
    
        row_styles.sort(key=lambda c: c[1])
        for i, c in enumerate(row_styles):
            row_list.insert(c[1] + 2 * i, c[3])
            row_list.insert(c[2] + 1 + 2 * i, "\033[0m")
        applied[row] = ''.join(row_list)
    return applied

def display_board(b: dict):
    draw_object([" River Bumpas & Levi Pare @ 2022 "], b, 102, 29)
    for line in apply_colors(b): print(line)

def clear_display():
    print('\033[2J\033[3J\033[H')
    return


def draw_cpus(cpus, board, reveal=False):
    coords = [
            [(110, 5), (18, 5)], 
            [(110, 10), (18, 10)], 
            [(110, 15), (18, 15)], 
            [(110, 20), (18, 20)]
            ]
    
    coords = sorted(reduce(lambda x,y : x+y, coords[:(len(cpus) + 1) // 2]), key=lambda t: t[0], reverse=True)
    for i, cpu in enumerate(cpus):
        coord = coords[i]
        action = cpu['last_action'] or ''
        if cpu['folded']:
            draw_object([f"{cpu['name']} ({action.capitalize()})"], board, coord[0], coord[1], "bold+underline+dim")  
            draw_object([f"Balance: {cpu['balance']}"], board, coord[0], coord[1] + 1, "dim")
            draw_object([f"Total Bet: {cpu['total_bet']}"], board, coord[0], coord[1] + 2, "dim")
            draw_object([f"Bet: {cpu['current_round_bet']}"], board, coord[0], coord[1] + 3, "dim")

            draw_object(create_blank_cpu_card(), board, 2 if coord[0] == 18 else 124, coord[1] - 1, "dim+red")
            draw_object(create_blank_cpu_card(), board, 9 if coord[0] == 18 else 131, coord[1] - 1, "dim+red" )
        elif reveal:
            style = ""
            if cpu['winner']:
                style = "+green+invert"

            draw_object([f"{cpu['name']} ({action.capitalize()})"], board, coord[0], coord[1], "bold+underline" + style)  
            draw_object([f"Balance: {cpu['balance']}"], board, coord[0], coord[1] + 1)
            draw_object([f"Total Bet: {cpu['total_bet']}"], board, coord[0], coord[1] + 2)
            draw_object([f"Bet: {cpu['current_round_bet']}"], board, coord[0], coord[1] + 3)

            draw_object(create_cpu_card(cpu['hand'][0]), board, 2 if coord[0] == 18 else 124, coord[1] - 1)
            draw_object(create_cpu_card(cpu['hand'][1]), board, 9 if coord[0] == 18 else 131, coord[1] - 1 )
        else:
            style = ""
            if cpu['active']:
                style = "+invert"

            draw_object([f"{cpu['name']} ({action.capitalize()})"], board, coord[0], coord[1], "bold+underline" + style)  
            draw_object([f"Balance: {cpu['balance']}"], board, coord[0], coord[1] + 1)
            draw_object([f"Total Bet: {cpu['total_bet']}"], board, coord[0], coord[1] + 2)
            draw_object([f"Bet: {cpu['current_round_bet']}"], board, coord[0], coord[1] + 3)

            draw_object(create_blank_cpu_card(), board, 2 if coord[0] == 18 else 124, coord[1] - 1, "red")
            draw_object(create_blank_cpu_card(), board, 9 if coord[0] == 18 else 131, coord[1] - 1, "red")

def draw_player(player_data, board):
    style = ""
    if player_data['active']:
        style = "+invert"
    elif player_data['winner']:
        style = "+green+invert"

    action = player_data['last_action'] or ''
    
    draw_object(create_card(player_data['hand'][0]), board, 56, 20, "dim" if player_data['folded'] else "")
    draw_object(create_card(player_data['hand'][1]), board, 71, 20, "dim" if player_data['folded'] else "")
    draw_object([f"{player_data['name']} ({action.capitalize()})"], board, 40, 21, "bold+underline" + style)  
    draw_object([f"Balance: {player_data['balance']}"], board, 40, 22)
    draw_object([f"Total Bet: {player_data['total_bet']}"], board, 40, 23)
    draw_object([f"Bet: {player_data['current_round_bet']}"], board, 40, 24)

def draw_game_data(board, main_pot, bet_data=False):
    if bet_data: draw_object([f"Current Bet: {bet_data['current_bet']}"], board, 70, 14, center=True)
    draw_object([f"Total Bets: {main_pot}"], board, 70, 16, 'bold', center=True)

def display_pre_flop(cpus, player_data, bet_data, main_pot):
    clear_display()
    board = create_board()
    draw_object(["======= TEXAS HOLD'EM POKER ======"], board, 70, 2, "bold", center=True)
    draw_game_data(board, main_pot, bet_data)
    draw_player(player_data, board)
    draw_cpus(cpus, board)

    draw_object(create_blank_card(), board, 50, 5, 'red')
    draw_object(create_blank_card(), board, 64, 5, 'red')
    draw_object(create_blank_card(), board, 78, 5, 'red')
    display_board(board)

def display_flop(cpus, player_data, community_cards, bet_data, main_pot):
    clear_display()
    board = create_board()
    draw_object(["======= TEXAS HOLD'EM POKER ======"], board, 70, 2, "bold", center=True)
    draw_object(["FLOP"], board, 70, 4, "bold", center=True)
    draw_game_data(board, main_pot, bet_data)
    draw_player(player_data, board)
    draw_cpus(cpus, board)

    draw_object(create_card(community_cards[0]), board, 50, 5)
    draw_object(create_card(community_cards[1]), board, 64, 5)
    draw_object(create_card(community_cards[2]), board, 78, 5)
    display_board(board)

def display_turn(cpus, player_data, community_cards, bet_data, main_pot):
    clear_display()
    board = create_board()
    draw_object(["======= TEXAS HOLD'EM POKER ======"], board, 70, 2, "bold", center=True)
    draw_object(["TURN"], board, 70, 4, "bold", center=True)
    draw_game_data(board, main_pot, bet_data)
    draw_player(player_data, board)
    draw_cpus(cpus, board)

    draw_object(create_card(community_cards[0]), board, 41, 5)
    draw_object(create_card(community_cards[1]), board, 56, 5)
    draw_object(create_card(community_cards[2]), board, 71, 5)
    draw_object(create_card(community_cards[3]), board, 86, 5)
    display_board(board)

def display_river(cpus, player_data, community_cards, bet_data, main_pot):
    clear_display()
    board = create_board()
    draw_object(["======= TEXAS HOLD'EM POKER ======"], board, 70, 2, "bold", center=True)
    draw_object(["RIVER"], board, 70, 4, "bold", center=True)
    draw_game_data(board, main_pot, bet_data)
    draw_player(player_data, board)
    draw_cpus(cpus, board)

    draw_object(create_card(community_cards[0]), board, 35, 5)
    draw_object(create_card(community_cards[1]), board, 50, 5)
    draw_object(create_card(community_cards[2]), board, 64, 5)
    draw_object(create_card(community_cards[3]), board, 78, 5)
    draw_object(create_card(community_cards[4]), board, 93, 5)
    display_board(board)

def display_showdown(cpus, player_data, community_cards, main_pot):
    clear_display()
    board = create_board()
    draw_object(["======= TEXAS HOLD'EM POKER ======"], board, 70, 2, "bold", center=True)
    draw_object(["THE SHOWDOWN"], board, 70, 4, "bold", center=True)
    draw_game_data(board, main_pot)
    draw_player(player_data, board)
    draw_cpus(cpus, board, reveal=True)

    coords = [35, 50, 64, 78, 93]
    for i, card in enumerate(community_cards):
        draw_object(create_card(card), board, coords[i], 5)
    display_board(board)




    


if __name__ == '__main__':

    player_data = {
    "name": "You",
    "hand": [],
    "table_position": 4,
    "balance": 1000,
    "current_round_bet": 0,
    "total_bet": 0,
    "last_action": None,
    "folded": False,
    "active": False,
    "winner": True,
    }

    t_deck = deck.create_and_shuffle()
    player_data["hand"] = generate_hand(t_deck)
    cpus = cpu_utils.generate_cpu(t_deck, [0, 1, 2, 3, 5, 6], 1000)
    community_cards = []
    for n in range(5):
        community_cards.append(deck.draw_card(t_deck))

    display_turn(cpus, player_data, community_cards, {'current_bet': 30})

