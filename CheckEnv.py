import numpy as np
from numba import njit

import warnings
from numba.core.errors import (
    NumbaDeprecationWarning,
    NumbaPendingDeprecationWarning,
    NumbaExperimentalFeatureWarning,
    NumbaWarning,
)

warnings.simplefilter("ignore", category=NumbaDeprecationWarning)
warnings.simplefilter("ignore", category=NumbaPendingDeprecationWarning)
warnings.simplefilter("ignore", category=NumbaExperimentalFeatureWarning)
warnings.simplefilter("ignore", category=NumbaWarning)

COUNT_TEST = 10000


def CheckAllFunc(_env_, BOOL_CHECK_ENV, msg):
    for func in [
        "getActionSize",
        "getStateSize",
        "getAgentSize",
        "getReward",
        "getValidActions",
        "numba_main_2",
    ]:
        try:
            getattr(_env_, func)
        except:
            msg.append(f"Không có hàm: {func}")
            BOOL_CHECK_ENV = False
    return BOOL_CHECK_ENV


def CheckReturn(_env_, BOOL_CHECK_ENV, msg):
    for func in ["getActionSize", "getStateSize", "getAgentSize"]:
        try:
            func_ = getattr(_env_, func)
            out = func_()
            if type(out) != int and type(out) != np.int64:
                msg.append(
                    f"ham {func} tra sai dau ra: dau ra yeu cau int, dau ra hien tai: {type(out)}"
                )
                BOOL_CHECK_ENV = False
        except:
            pass
    return BOOL_CHECK_ENV


def RunGame(_env_, BOOL_CHECK_ENV, msg):
    @njit()
    def test_numba(p_state, per_file):
        arr_action = _env_.getValidActions(p_state)

        if _env_.getReward(p_state) != -1:
            per_file[0] += 1
        if _env_.getReward(p_state) == 1:
            per_file[1] += 1
        if np.min(p_state) < 0:
            per_file[2] = 1
        if len(p_state) != _env_.getStateSize():
            per_file[3] = 1
        if len(arr_action) != _env_.getActionSize():
            per_file[4] = 1

        arr_action = np.where(arr_action == 1)[0]
        act_idx = np.random.randint(0, len(arr_action))
        return arr_action[act_idx], per_file

    def test_no_numba(p_state, per_file):
        arr_action = _env_.getValidActions(p_state)
        if p_state.dtype != np.float64:
            per_file[5] = 1
        if arr_action.dtype != np.float64:
            per_file[6] = 1
        arr_action = np.where(arr_action == 1)[0]
        act_idx = np.random.randint(0, len(arr_action))
        return arr_action[act_idx], per_file

    try:
        per = np.array(
            [0, 0, 0, 0, 0, 0, 0]
        )  # end, win end, state âm, state thay đổi, actions thay đổi, type state, type action
        win, per = _env_.numba_main_2(test_numba, COUNT_TEST, per, 0)

        if type(win) != int and type(win) != np.int64:
            msg.append("hàm numba_main_2 trả ra sai đầu ra, yêu cầu int")
            BOOL_CHECK_ENV = False
        if per[0] != COUNT_TEST:
            msg.append(
                f"numba_main_2, Số trận kết thúc khác với số trận test, {per[0]}"
            )
            BOOL_CHECK_ENV = False
        if per[1] != win:
            msg.append(
                f"numba_main_2, Số trận thắng khi kết thúc khác với sô trận check. Thắng khi dùng getReward: {per[1]}, win: {win}"
            )
            BOOL_CHECK_ENV = False
        if per[2] == 1:
            msg.append(f"State đang bị âm")
            BOOL_CHECK_ENV = False
        if per[3] == 1:
            msg.append(f"len STATE đang thay đổi trong quá trình chạy game")
            BOOL_CHECK_ENV = False
        if per[4] == 1:
            msg.append(f"len ACTION đang thay đổi trong quá trình chạy game")
            BOOL_CHECK_ENV = False

        try:
            per = np.array([0, 0, 0, 0, 0, 0, 0])
            win, per = _env_.numba_main_2(test_no_numba, COUNT_TEST, per, 0)
            if per[5] == 1:
                msg.append(f"STATE đang trả ra sai output")
                BOOL_CHECK_ENV = False
            if per[6] == 1:
                msg.append(f"array ACTION đang trả ra sai output")
                BOOL_CHECK_ENV = False
        except:
            msg.append("hàm numba_main_2 không train được với agent không numba")
            BOOL_CHECK_ENV = False

    except:
        msg.append(f"hàm numba_main_2 đang bị lỗi")
        BOOL_CHECK_ENV = False

    return BOOL_CHECK_ENV


def CheckRunGame(_env_, BOOL_CHECK_ENV, msg):
    BOOL_CHECK_ENV = RunGame(_env_, BOOL_CHECK_ENV, msg)
    return BOOL_CHECK_ENV


def CheckRandomState(_env_, BOOL_CHECK_ENV, msg):
    for i in range(10000):
        p_state1 = np.random.randint(-100, 100, _env_.getStateSize())
        p_state2 = np.random.randint(0, 1000, _env_.getStateSize())
        p_state3 = np.random.randn(_env_.getStateSize()) * 100
        try:
            _env_.getValidActions(p_state1)
            _env_.getValidActions(p_state2)
            _env_.getValidActions(p_state3)
        except:
            msg.append(f"hàm getValidActions lỗi khi nhận vào random state")
            BOOL_CHECK_ENV = False
            return BOOL_CHECK_ENV
        try:
            _env_.getReward(p_state1)
            _env_.getReward(p_state2)
            _env_.getReward(p_state3)
        except:
            msg.append(f"hàm getReward lỗi khi nhận vào random state")
            BOOL_CHECK_ENV = False
            return BOOL_CHECK_ENV
    try:
        _env_.getReward(np.full(_env_.getStateSize(), 0))
        _env_.getReward(np.full(_env_.getStateSize(), 0.0))
        _env_.getReward(np.full(_env_.getStateSize(), 1))
    except:
        msg.append(f"hàm getReward lỗi khi nhận vào random state")
        BOOL_CHECK_ENV = False
        return BOOL_CHECK_ENV
    try:
        _env_.getValidActions(np.full(_env_.getStateSize(), 0))
        _env_.getValidActions(np.full(_env_.getStateSize(), 0.0))
        _env_.getValidActions(np.full(_env_.getStateSize(), 1))
    except:
        msg.append(f"hàm getValidActions lỗi khi nhận vào random state")
        BOOL_CHECK_ENV = False
        return BOOL_CHECK_ENV
    return BOOL_CHECK_ENV


def check_env(_env_):
    BOOL_CHECK_ENV = True
    msg = []
    BOOL_CHECK_ENV = CheckAllFunc(_env_, BOOL_CHECK_ENV, msg)
    BOOL_CHECK_ENV = CheckReturn(_env_, BOOL_CHECK_ENV, msg)
    BOOL_CHECK_ENV = CheckRunGame(_env_, BOOL_CHECK_ENV, msg)
    BOOL_CHECK_ENV = CheckRandomState(_env_, BOOL_CHECK_ENV, msg)
    return BOOL_CHECK_ENV, msg
