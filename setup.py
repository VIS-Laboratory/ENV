game_name = "Splendor"
time_run_game = 100
N_AGENT = 5
N_GAME = 15
PASS_LEVEL = 2500
COUNT_TRAIN = 10000
COUNT_TEST = 1000

#  path = "C:\AutomaticTrain\State.xlsx"
#  SHOT_PATH = 'A:/AutoTrain/GAME/'
DRIVE_FOLDER = "G:/My Drive/AutomaticColab/"


SHORT_PATH = ""
#  DRIVE_FOLDER = 'H:/Drive của tôi/AutomaticColab/'

import sys, os
from setup import SHORT_PATH
import importlib.util

game_name = "Catan"


def make(game_name):
    def add_game_to_syspath(game_name):
        if len(sys.argv) >= 2:
            sys.argv = [sys.argv[0]]
        sys.argv.append(game_name)

    def setup_game(game_name):
        spec = importlib.util.spec_from_file_location(
            "env", f"{SHORT_PATH}Base/{game_name}/env.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    add_game_to_syspath(game_name)
    env = setup_game(game_name)

    return env


def setup_game(game_name):
    spec = importlib.util.spec_from_file_location(
        "env", f"{SHORT_PATH}Base/{game_name}/env.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
