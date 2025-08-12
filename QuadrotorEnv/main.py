import sys
from parser_ import parser
from config import *
from load_game import *
from datamodule_quadrotor import *
from multigame import *

# Control mode: HSC / OCIP / manual / optimal / shared
c_mode = 'shared'
# Player Name
name = 'testing'#'G1P32'
#'Intro' + '_' + c_mode

# User input device (joystick,ps4,xbox,switch)
input_device = 'joystick'
# No. of games (positive integer)
n_game = 5


def main(argv):
    # import gui_tutorial
    # print('Quadrotor landing simulator')

    # print('Thrust Tutorial\n')
    # import gui_thrust_tutorial
    # thrust_tutorial_mgr = thrust_tutorial.ThrustTutorialMgr(mode=1, control=input_device, time_limit=60.0)
    # _ = thrust_tutorial_mgr.input()
    # _, _, _ = thrust_tutorial_mgr.update()

    # while thrust_tutorial_mgr.mode:
    #     _ = thrust_tutorial_mgr.input()
    #     _, _, _ = thrust_tutorial_mgr.update()
    #     thrust_tutorial_mgr.render()

    # print('Attitude Tutorial\n')
    # import gui_controller_tutorial
    # tutorial_mgr = tutorial.TutorialMgr(mode=1, control=input_device, time_limit=60.0)
    # _ = tutorial_mgr.input()
    # _, _, _ = tutorial_mgr.update()

    # while tutorial_mgr.mode:
    #     _ = tutorial_mgr.input()
    #     _, _, _ = tutorial_mgr.update()
    #     tutorial_mgr.render()

    # command parser
    game_mode, max_iteration = parser(argv)

    # Simulation environment
    np_trajectory = load_multi_game(device=input_device, name=name, control_mode=c_mode, self_confidence=0, n=n_game, Pauses = True)

    # Data module
    save_trajectory(np_trajectory, player_name=name)

if __name__ == '__main__':
    main(sys.argv[1:])
