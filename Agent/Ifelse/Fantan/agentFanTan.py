import numpy as np
from numba import njit
from numba.typed import List
import sys, os
from setup import SHORT_PATH
import importlib.util

game_name = sys.argv[1]


def setup_game(game_name):
    spec = importlib.util.spec_from_file_location(
        "env", f"{SHORT_PATH}Base/{game_name}/env.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


env = setup_game(game_name)

getActionSize = env.getActionSize
getStateSize = env.getStateSize
getAgentSize = env.getAgentSize

getValidActions = env.getValidActions
getReward = env.getReward


@njit()
def DataAgent():
    return np.array([0.0])


@njit()
def CountTypeCard(state):
    arr_return = [0, 0, 0, 0]
    player_cards = state[0:52]
    player_cards = np.where(player_cards == 1)[0]
    for i in range(len(player_cards)):
        arr_return[player_cards[i] // 13] += 1
    return arr_return


@njit()
def Test(state, per):
    actions = getValidActions(state)
    actions = np.where(actions == 1)[0]
    player_cards = state[0:52]
    player_cards = np.where(player_cards == 1)[0]
    player_cards_len = len(player_cards)
    arr_card_type_count = np.array(CountTypeCard(state))
    type_sort = np.argsort(-arr_card_type_count)
    if player_cards_len == 12:
        per[0] = 0
    for action in actions:
        if action // 13 == type_sort[0]:
            return action, per
    for action in actions:
        if action // 13 == type_sort[1]:
            return action, per
    for action in actions:
        if arr_card_type_count[type_sort[2]] < 3:
            if per[0] < 2:
                return 52, per
        if arr_card_type_count[type_sort[3]] < 3:
            if per[0] < 2:
                return 52, per
        if action // 13 == type_sort[2]:
            return action, per

    return np.random.choice(actions), per
