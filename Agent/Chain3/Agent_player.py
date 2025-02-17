import numpy as np
from numba import njit
import sys
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


from numba.typed import List


def DataAgent():
    if getActionSize() < 150:
        perx_Chain3 = List(
            [
                np.zeros((getActionSize() ** 2, getActionSize())),
                np.argsort(
                    np.argsort(
                        np.random.rand(getActionSize() ** 2, getActionSize()), axis=1
                    ),
                    axis=1,
                )
                * 1.0
                + 1.0,
                np.zeros((1, 2)) - 1.0,
                np.zeros((1, 1)),
            ]
        )
    else:
        perx_Chain3 = List(
            [
                np.zeros((150**2, 150)),
                np.argsort(np.argsort(np.random.rand(150**2, 150), axis=1), axis=1)
                * 1.0
                + 1.0,
                np.zeros((1, 2)) - 1.0,
                np.zeros((1, 1)),
                np.zeros((1, getActionSize())),
                np.zeros((1, 150)),
                np.full((150**2, 150), np.arange(1, 151)).astype(np.float64),
            ]
        )
    return perx_Chain3


@njit
def argSortSpecial(w):
    indexTable = np.empty_like(w)
    indexTable2 = np.empty_like(w)
    for j in range(indexTable.shape[0]):
        indexTable[j, :] = np.argsort(w[j, :])
    for k in range(indexTable.shape[0]):
        indexTable2[k, :] = np.argsort(indexTable[k, :])
    return indexTable2 * 1.0


@njit
def generateArr(w):
    for i in range(w.shape[0]):
        np.random.shuffle(w[i, :])
    return w


@njit
def Train(state, per):
    #  if getReward(state)!=-1:
    #      if per[3][0][0]%100==0:
    #          print(per[3][0][0])
    if getActionSize() < 150:
        if per[2][0][0] == -1 or per[2][0][1] == -1:
            action = np.random.choice(np.where(getValidActions(state) == 1)[0])
            if per[2][0][0] == -1:
                per[2][0][0] = action
            elif per[2][0][1] == -1:
                per[2][0][1] = action
        else:
            weight = per[1][int(per[2][0][0] * getActionSize() + per[2][0][1])]
            action = np.argmax(weight * getValidActions(state))
            per[2][0][0] = per[2][0][1]
            per[2][0][1] = action
        if getReward(state) != -1:
            per[3][0][0] += 1
            if getReward(state) == 1:
                per[0] += per[1] * 1.0
            else:
                per[1] = (
                    argSortSpecial(
                        np.random.rand(getActionSize() ** 2, getActionSize())
                    )
                    * 1.0
                    + 1.0
                )

        return int(action), per
    else:
        if per[3][0][0] < 10000:
            action = np.random.choice(np.where(getValidActions(state) == 1)[0])
            per[4][0][int(action)] += 1
            if getReward(state) != -1:
                per[3][0][0] += 1
                if per[3][0][0] == 10000:
                    per[5][0] = np.arange(getActionSize())[np.argsort(per[4][0, :])][
                        -150:
                    ]
        else:
            if per[2][0][0] == -1 or per[2][0][1] == -1:
                action = np.random.choice(np.where(getValidActions(state) == 1)[0])
                if per[2][0][0] == -1:
                    per[2][0][0] = action
                elif per[2][0][1] == -1:
                    per[2][0][1] = action
            else:
                if (
                    np.where(per[5][0] == per[2][0][0])[0].shape[0] == 0
                    or np.where(per[5][0] == per[2][0][1])[0].shape[0] == 0
                ):
                    action = np.random.choice(np.where(getValidActions(state) == 1)[0])
                    per[2][0][0] = per[2][0][1]
                    per[2][0][1] = action
                else:
                    id1 = np.where(per[5][0] == per[2][0][0])[0][0]
                    id2 = np.where(per[5][0] == per[2][0][1])[0][0]
                    idx = int(id1 * getActionSize() + id2)
                    if idx >= 0 and idx <= 150**2:
                        weight = per[1][int(id1 * 150 + id2)]
                        list_action = (
                            weight * getValidActions(state)[per[5][0].astype(np.int64)]
                        )
                        action = per[5][0][np.argmax(list_action)]
                        if getValidActions(state)[int(action)] == 0:
                            action = np.random.choice(
                                np.where(getValidActions(state) == 1)[0]
                            )
                        per[2][0][0] = per[2][0][1]
                        per[2][0][1] = action
                    else:
                        action = np.random.choice(
                            np.where(getValidActions(state) == 1)[0]
                        )
                        per[2][0][0] = per[2][0][1]
                        per[2][0][1] = action
            if getReward(state) != -1:
                per[3][0][0] += 1
                if getReward(state) == 1:
                    per[0] += per[1] * 1.0
                else:
                    per[1] = generateArr(per[6])
        return int(action), per


@njit
def Test(state, per):
    validActions = getValidActions(state)
    actions = np.where(validActions == 1)[0]
    actionSize = getActionSize()
    if actionSize < 150:
        if per[1][0][0] == -1 or per[1][0][1] == -1:
            action = actions[np.random.randint(0, actions.shape[0])]
            if per[1][0][0] == -1:
                per[1][0][0] = action
            elif per[1][0][1] == -1:
                per[1][0][1] = action
        else:
            weight = per[0][int(per[1][0][0] * actionSize + per[1][0][1])]
            action = np.argmax(weight * validActions + validActions)
            per[1][0][0] = per[1][0][1]
            per[1][0][1] = action
        return action, per
    else:
        if per[1][0][0] == -1 or per[1][0][1] == -1:
            action = actions[np.random.randint(0, actions.shape[0])]
            if per[1][0][0] == -1:
                per[1][0][0] = action
            elif per[1][0][1] == -1:
                per[1][0][1] = action
        else:
            if per[1][0][0] == -1 or per[1][0][1] == -1:
                action = actions[np.random.randint(0, actions.shape[0])]
                if per[1][0][0] == -1:
                    per[1][0][0] = action
                elif per[1][0][1] == -1:
                    per[1][0][1] = action
            else:
                id1_ = np.where(per[2][0] == per[1][0][0])[0]
                id2_ = np.where(per[2][0] == per[1][0][1])[0]
                if id1_.shape[0] == 0 or id2_.shape[0] == 0:
                    action = actions[np.random.randint(0, actions.shape[0])]
                    per[1][0][0] = per[1][0][1]
                    per[1][0][1] = action
                else:
                    id1 = id1_[0]
                    id2 = id2_[0]
                    idx = id1 * actionSize + id2
                    if idx >= 0 and idx <= 150**2:
                        weight = per[0][int(id1 * 150 + id2)]
                        list_action = weight * validActions[per[2][0].astype(np.int64)]
                        action = per[2][0][np.argmax(list_action)]
                        if validActions[int(action)] == 0:
                            action = actions[np.random.randint(0, actions.shape[0])]
                        per[1][0][0] = per[1][0][1]
                        per[1][0][1] = action
                    else:
                        action = actions[np.random.randint(0, actions.shape[0])]
                        per[1][0][0] = per[1][0][1]
                        per[1][0][1] = action
        return int(action), per


def convert_to_save(perData):
    data = List()
    if getActionSize() < 150:
        if len(perData) == 2:
            raise Exception("Data này đã được convert rồi.")
        data.append(perData[0])
        data.append(perData[2])
    else:
        if len(perData) == 3:
            raise Exception("Data này đã được convert rồi.")
        data.append(perData[0])
        data.append(perData[2])
        data.append(perData[5])

    return data


def convert_to_test(perData):
    return List(perData)
