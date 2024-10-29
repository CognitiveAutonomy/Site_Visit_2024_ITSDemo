import pyautogui
screen_width, screen_height= pyautogui.size()
# center_x = int(screen_width / 2 - window_width / 2)
# center_y = int(screen_height / 2 - window_height / 2)


RECORD_PATH = '../assets/records/'
MATLAB_PATH = '../assets/MATLAB_scripts/'
WEIGHT_PATH = '../assets/weights/'
IMAGE_PATH = '../assets/images/'
ALGORITHM_PATH = '../algorithms/'
FONT = 'Helvetica'
FONT2 = 'Helvetica:bold'
FONT_SIZE = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255,0)
SEE = (0, 119, 190)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Game setting
# WINDOW_X = 1600
# WINDOW_Y = 900
# BOUND_X_MIN = 1920/2 - WINDOW_X/2
# BOUND_X_MAX = BOUND_X_MIN + WINDOW_X
# BOUND_Y_MIN = 1080/2 - WINDOW_Y/2
# BOUND_Y_MAX = BOUND_Y_MIN + WINDOW_Y
# WALL = 0

BOUND_X_MAX = 1600
BOUND_X_MIN = 0
BOUND_Y_MAX = 900
BOUND_Y_MIN = 0
WALL = 20
REAL_DIM_RATIO = 60 / BOUND_X_MAX
BOUND_REAL_X = BOUND_X_MAX * REAL_DIM_RATIO
BOUND_REAL_Y = BOUND_Y_MAX * REAL_DIM_RATIO

# Quadrotor dynamics
MASS = 0.25
GRAV = 9.8
GAINS = [-0.1, -1, -30]
IXX = 0.01
DELTAT = 0.05
