from Base.Catan import _env as __env
from render_template import Render as __Render, import_files as __import_files
from numba.core.errors import (
    NumbaPendingDeprecationWarning as __NumbaPendingDeprecationWarning,
)
import warnings as __warnings

__warnings.simplefilter("ignore", __NumbaPendingDeprecationWarning)


__import_files("Catan")


getValidActions = __env.getValidActions
getActionSize = __env.getActionSize
getAgentSize = __env.getAgentSize
getStateSize = __env.getStateSize
getReward = __env.getReward
numba_main_2 = __env.numba_main_2
POINT_TILE = __env.POINT_TILE
POINT_POINT = __env.POINT_POINT
POINT_ROAD = __env.POINT_ROAD
TILE_TILE = __env.TILE_TILE
ROAD_POINT = __env.ROAD_POINT


def render(Agent, per_data, level, *args, max_temp_frame=100):
    list_agent, list_data = __env.load_agent(level, *args)

    if "__render" not in globals():
        global __render
        __render = __Render(Agent, per_data, list_agent, list_data, max_temp_frame)
    else:
        __render.__init__(Agent, per_data, list_agent, list_data, max_temp_frame)

    return __render.render()


def get_data_from_visualized_match():
    if "__render" not in globals():
        print("Nothing to get, visualize the match before running this function")
        return None

    return {
        "history_state": __render.history_state,
        "history_action": __render.history_action,
    }
