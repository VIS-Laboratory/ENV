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


def DataAgent():
    per = []
    per.append(np.zeros(1))
    return per


def Test(state, per):
    validActions = getValidActions(state)
    actions = np.where(validActions)[0]

    monster = np.where(state[28:36])[0]
    if state[13] > 4:
        if 0 in actions:
            return 0, per

    if 1 in actions:
        return 1, per

    for i in np.array([6, 7, 5, 8, 4, 3, 12, 13, 11, 14, 10, 9]):
        if i in actions:
            return i, per

    act = np.random.choice(actions)
    return act, per
