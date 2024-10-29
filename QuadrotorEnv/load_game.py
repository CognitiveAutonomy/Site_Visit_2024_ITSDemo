import pygame
import numpy as np
import game


def load_drone_landing(device='joystick', name='no_name', c_mode='HSC', s_confidence=0):
    trajectory = []

    # Game load
    print('Simulator loaded')

    game_mgr = game.GameMgr(mode=1, control=device, control_mode=c_mode, self_confidence=s_confidence)
    mode = game_mgr.input()
    _, _, _, _, _ = game_mgr.update()

    while game_mgr.mode:
        mode = game_mgr.input()
        curr_time, state, action, authority, loss = game_mgr.update()
        game_mgr.render()
        if game_mgr.record:
            trajectory.append(curr_time + state + action + authority + loss)

    if trajectory:
        np_trajectory = np.array(trajectory, float)

    return np_trajectory
