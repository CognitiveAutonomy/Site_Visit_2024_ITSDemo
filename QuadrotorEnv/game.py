import numpy as np
import pygame
import random
import os
import control.matlab as cnt
from pygame.locals import *

import quadrotor
from config import *
from quadrotor import *
from background import *
from font import *
from main import *
from pynput.keyboard import Key, Controller

obstacle_spawn = pygame.USEREVENT+1
record_Sign = pygame.USEREVENT+2
obstacle_clock = 80
time_delta = 30
record_sign_interval = 5
keyboard = Controller()

# game manager object
class GameMgr:
    # def __init__(self, mode=1, control='joystick', trial=0, control_mode='HSC'):
    def __init__(self, mode=1, control='joystick', trial=0, control_mode='HSC', init_positions = np.array([15,28])):
        random.seed()

        # mode initialization
        self.initial = True
        self.mode = mode
        self.record = True
        self.record_sign = record_Sign
        self.t0 = 0
        self.control = control
        self.final_time_record = 0
        self.trial = trial
        self.time = 0.0
        self.time_prev = 0.0
        self.c_mode = control_mode
        self.landing = 0
        self.start_trial = 0

        # For visual feedback
        self.visual_code = 0

        # For the hybrid shared control
        A = np.eye(6) + DELTAT * np.array(
            [[0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1], [0, 0, 9.8, 0, 0, 0],
             [0, 0, 0, 0, GAINS[0], 0], [0, 0, GAINS[1], 0, 0, GAINS[2]]])
        B = DELTAT * np.array([[0, 0], [0, 0], [0, 0], [0, 0], [0, 1 / MASS], [1 / IXX, 0]])
        # 1st set
        Q = np.diag([3, 0.5, 500, 2, 0.5, 300])
        R = 30 * np.array([[10, -1], [-1, 30]])
        # 2nd set
        # Q = np.diag([0.3, 1, 700, 1, 2, 300])
        # R = 30 * np.array([[10, -1], [-1, 30]])
        _, _, Ke = cnt.dare(A, B, Q, R)
        self.Ke = np.squeeze(np.array(Ke))
        # self.Ke = -np.array([[-0.0276, -0.0000, -0.7404, -0.0693, 0.0000, -0.0191],
        #                      [-0.0009, -0.0331, -0.0202, -0.0022, -0.1107, -0.0005]])
        self.A = A
        self.B = B
        self.Q = Q
        self.R = R
        self.authority = 1
        self.loss = 0
        self.loss_baseline = 0
        self.task_obj = 0
        self.accumulated_authority = 0

        self.max_u = 1.0
        self.min_u = -1.0

        # Online DMD
        self.P = 1e64 * np.eye(6)
        self.gamma = 0
        self.A_DMD = np.zeros((6, 6))
        self.Xk = np.zeros(6)
        self.Yk = np.zeros(6)
        self.sigma = 0.9
        self.k = 0

        # Collision dynamics
        # self.collide_consecutive = 0
        # self.collide_angle = 0
        # self.previous_angle = 0
        self.collision = False
        self.land = False

        # Controller dynamics
        self.prev_angle = 0
        self.cycle = 0

        # game screen initialization
        pygame.init()
        pygame.font.init()
        # Joystick initialization
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        # initial window position
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (10,50)
        if self.mode != 100:
            self.screen = pygame.display.set_mode((BOUND_X_MAX, BOUND_Y_MAX), DOUBLEBUF)

        # Game title on the window
        pygame.display.set_caption('Quadrotor Landing')

        # game clock initialization
        self.clock = pygame.time.Clock()
        self.obstacle_counter = 0
        pygame.time.set_timer(record_Sign, time_delta*25)

        # object queue initialization
        self.objects = []
        self.collideds = []

        # (x_init_pixel, y_init_pixel) ==> pixel
        # (x_init_meter, y_init_meter) ==> SI unit
        # x_init_real = np.random.uniform(-20, 20)
        # y_init_real = np.random.uniform(25, 30)

        x_init_real = init_positions[0]
        y_init_real = init_positions[1]
        init_pixel = quadrotor.position_meter_to_pixel(np.array([x_init_real, y_init_real]))
        x_init_pixel = init_pixel[0]
        y_init_pixel = init_pixel[1]

        main_drone = Quadrotor(file_name=IMAGE_PATH + 'drone.png', sc=0.20, rt=0.0,
                               pos_x=x_init_pixel, pos_y=y_init_pixel, is_drag=False)
        self.objects.append(main_drone)

        # Background and text interface init
        self.background = Background(file_name=IMAGE_PATH + 'Purdue_blurred.png', moving_name=IMAGE_PATH + 'road.png',
                                     bound_x_min=BOUND_X_MIN, bound_x_max=BOUND_X_MAX, bound_y_min=BOUND_Y_MIN,
                                     bound_y_max=BOUND_Y_MAX)
        self.status = Font(FONT, FONT_SIZE, (BOUND_X_MAX/2 - 700, 800))
        self.instruction = Font(FONT2, int(FONT_SIZE*1.9), (BOUND_X_MAX/2 - 400, BOUND_Y_MAX/2 - 100))
        self.time_font = Font(FONT, int(FONT_SIZE*1.5), (BOUND_X_MAX/2 - 700, 20))
        self.mode_font = Font(FONT2, int(FONT_SIZE*2.0), (BOUND_X_MAX/2 - 300, 20))
        # self.instruction.update2("Click Any Joystick Button to Start Trial %d" % (self.trial + 1), WHITE)
        # self.instruction.update("SIMULATION INSTRUCTION")
        # self.instruction.update("Input device: %s" % control)

        # Event message
        self.events = []
        self.action = None

        # Putting obstacles
        yc = self.background.max_bound[1] / 2
        self.events.append(obstacle_spawn)

        # Position of objects
        # Target
        target_meter = np.array([0, 0.3])
        target_pixel = quadrotor.position_meter_to_pixel(target_meter)

        target = Quadrotor(file_name=IMAGE_PATH + 'touchpad2____.png', pos_x=target_pixel[0],
                         pos_y=target_pixel[1]-40, sc=0.2)
        self.objects.append(target)

        # Mouse input
        if control == 'mouse':
            self.mouse_pos = []

        # Joystick input
        if control == 'joystick':
            self.joystick_axis = []

        # ps4 input
        if control == 'ps4':
            self.joystick_axis = []

        # sbox input
        if control == 'xbox':
            self.joystick_axis = []

        # switch input
        if control == 'switch':
            self.joystick_axis = []

        # Keyboard input (not used)
        # self.x_acc = 1
        # self.y_acc = 0

    def input(self, action=None):

        # game clock
        if self.mode != 100:
            self.clock.tick(time_delta)

        # Event handling
        for event in pygame.event.get():
            # Timer event
            if event.type == record_Sign:
                self.events.append(record_Sign)

            # Input event
            elif event.type == KEYDOWN:
                if not hasattr(event, 'key'):
                    continue
                elif event.key == K_ESCAPE:
                    self.mode = 0
                elif event.key == K_SPACE:
                    if self.mode == 1:
                        self.mode = 2
                    elif self.mode == 2:
                        self.mode = 3
                    elif self.mode == 3:
                        self.mode = 1
                elif event.key == K_r:
                    self.record = not self.record
                else:
                    self.events.append(event.key)
            elif event.type == KEYUP:
                if not hasattr(event, 'key'):
                    continue
                if event.key in self.events:
                    self.events.remove(event.key)
            # Mouse
            if self.control == 'mouse':
                self.mouse_pos = pygame.mouse.get_pos()

            # Joystick
            if self.control == 'joystick':
                self.joystick_axis = [self.joystick.get_axis(0), self.joystick.get_axis(2)]
            elif self.control == 'ps4':
                self.joystick_axis = [self.joystick.get_axis(2), self.joystick.get_axis(1)]
            elif self.control == 'switch':
                self.joystick_axis = [self.joystick.get_axis(2), self.joystick.get_axis(1)]
            elif self.control == 'xbox':
                self.joystick_axis = [self.joystick.get_axis(0), self.joystick.get_axis(3)]

        # auto-driving mode
        if self.mode == 100 or 3:
            if action == 0:
                self.events.append(pygame.K_a)
                self.action = pygame.K_a
            elif action == 1:
                self.events.append(pygame.K_s)
                self.action = pygame.K_s
            elif action == 2:
                self.events.append(pygame.K_d)
                self.action = pygame.K_d
            elif action == 3:
                self.events.append(pygame.K_f)
                self.action = pygame.K_f
            elif action == 4:
                self.events.append(pygame.K_g)
                self.action = pygame.K_g

        # Return game state
        return self.mode

    def update(self):

        # Update message handling
        self.status.clear()
        self.time_font.clear()
        self.mode_font.clear()
        self.record_sign -= 1

        # Key event (not used except for record)
        for key in self.events:
            if key == record_Sign:
                self.record_sign = record_sign_interval
            # if key == pygame.K_DOWN:
            #     self.y_acc += 0.1
            #     if self.y_acc > 1.0:
            #         self.y_acc = 1.0
            # if key == pygame.K_UP:
            #     self.y_acc -= 0.1
            #     if self.y_acc < -1.0:
            #         self.y_acc = -1.0
            # if key == pygame.K_RIGHT:
            #     self.x_acc += 0.1
            #     if self.x_acc > 1.0:
            #         self.x_acc = 1.0
            # if key == pygame.K_LEFT:
            #     self.x_acc -= 0.1
            #     if self.x_acc < -1.0:
            #         self.x_acc = -1.0

        # Update timer and action
        if obstacle_spawn in self.events:
            self.events.remove(obstacle_spawn)
        if record_Sign in self.events:
            self.events.remove(record_Sign)
        if (self.mode == 100 or 3) and self.action in self.events:
            self.events.remove(self.action)

        # Update other objects status
        while self.collideds:
            # self.collideds[-1].load(IMAGE_PATH + 'obstacle_long.png')
            self.collideds.pop()
        remove_id = []
        main = self.objects[0]
        for i, obj in enumerate(self.objects):
            obj.update()
            x, y = obj.position
            rect = obj.surface.get_rect()
            if i == 0:
                if x < self.background.min_bound[0]:
                    x = self.background.min_bound[0]
                    self.collision = True
                    self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                    self.mode = 0
                if y < self.background.min_bound[1]:
                    y = self.background.min_bound[1]
                    self.collision = True
                    self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                    self.mode = 0
                if x > self.background.max_bound[0]:
                    x = self.background.max_bound[0]
                    self.collision = True
                    self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                    self.mode = 0
                if y > self.background.max_bound[1] - 10:
                    y = self.background.max_bound[1] - 10
                    self.collision = True
                    self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                    self.mode = 0
                obj.position = np.array([x, y])
            if i != 0:
                if y > self.background.max_bound[1] + 200:
                    remove_id.append(i)
                if main.rect.colliderect(obj.rect):
                    self.collideds.append(obj)
                    # Conditions for a successful landing
                    final_angle = abs(self.objects[0].attitude) * 180.0 / np.pi
                    final_speed = REAL_DIM_RATIO * np.linalg.norm(self.objects[0].speed)
                    final_x_pos = self.objects[0].position[0]
                    landing_flag = final_angle < 10.0 and final_speed < 5.0
                    position_flag = final_x_pos > 625 and final_x_pos < 972
                    # print('Final speed and attitude: %.2f %.2f' % (final_speed, final_angle))
                    if self.collideds[-1].classification == 'touchpad2____.png' and landing_flag and position_flag:
                        self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                        # print('Time record: %.2f sec' % self.final_time_record)
                        self.mode = 0
                        self.landing = 1
                    else:
                        if self.collideds[-1].classification == 'touchpad2____.png' and position_flag:
                            self.land = True
                            self.landing = 2
                        else:
                            self.collision = True
                            self.landing = 0
                        self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                        self.mode = 0
                        #self.landing = 0

                    # print('Task Objective function: %.2f' % self.task_obj)
                    # print('Averaged control authority: %.2f' % (self.accumulated_authority / (self.k - 1)))

        # System noise (uncertainty)
        # angle_noise = np.random.normal(loc=0.0, scale=0.0)
        angle_noise = 0

        # Quadrotor states
        pos = main.position
        spd = main.speed
        att = main.attitude
        ang_vel = main.angular_vel

        # Mouse/Joystick input
        if self.control == 'mouse':
            # pointing = np.array((self.mouse_pos[0] - pos[0], self.mouse_pos[1] - pos[1]))
            pointing = np.array([0, 0])
            # if pointing[1] > 0:
            #     angle = np.arccos(pointing[0] / np.linalg.norm(pointing))
            # else:
            #     angle = -np.arccos(pointing[0] / np.linalg.norm(pointing))
            angle = 0.0
        else:
            pointing = np.array(self.joystick_axis)
            norm_pointing = np.linalg.norm(pointing)
            if norm_pointing < 0.0:   # HW calibration problem...
                # angle = np.random.uniform(-np.pi, np.pi)
                angle = 0.0
            elif pointing[1] > 0:
                angle = np.arccos(pointing[0] / norm_pointing)
            else:
                angle = -np.arccos(pointing[0] / (norm_pointing + 1e-32))
            pointing[1] = -pointing[1]


        # Recording human input
        human_input = np.copy(pointing)

        # Singular point
        if angle * self.prev_angle < 0 and abs(angle - self.prev_angle) > np.pi:
            if self.prev_angle < 0:
                self.cycle -= 1
            elif self.prev_angle > 0:
                self.cycle += 1

        # Angle considering cycle...
        angle = 2 * np.pi * self.cycle + angle

        # Collision dynamics
        # if collision_flag:
        #     self.collide_consecutive += 1
        #     if self.collide_consecutive == 1:
        #         self.collide_angle = self.previous_angle
        #     angle = self.collide_angle
        #     if abs(angle - np.pi/2) < 1.e-3:
        #         angle = -np.pi/2 - 1.e-3
        #     elif abs(angle + np.pi/2) < 1.e-3:
        #         angle = np.pi/2 + 1.e-3
        #     elif angle >= 0.0:
        #         angle = angle - np.pi
        #     elif angle < 0.0:
        #         angle = angle + np.pi
        # else:
        #     self.collide_consecutive = 0
        #     self.collide_angle = 0

        # Final control angle w/ noise
        # self.objects[0].speed_control(angle + angle_noise)

        # Drone control test
        # self.objects[0].quadrotor_dynamics(pointing[0], pointing[1])
        # self.objects[0].linearized_quadrotor_dynamics(pointing[0], pointing[1])

        # States for control
        # Controller states
        # pos_c = np.array([pos[0] - BOUND_X_MAX / 2, BOUND_Y_MAX - pos[1]])
        # spd_c = np.array([spd[0], -spd[1]])
        # att_c = -att
        # ang_vel_c = -ang_vel
        # state_meter = np.array([pos_c[0], pos_c[1], att_c, spd_c[0], spd_c[1], ang_vel_c])
        state_pixel = np.hstack((pos, att, spd, ang_vel))
        state_meter = quadrotor.state_pixel_to_meter(state_pixel)
        # Ad-hoc: the constant should be removed
        # state_meter[0:2] = 1 / REAL_DIM_RATIO * state_meter[0:2]
        # state_meter[3:5] = 1 / REAL_DIM_RATIO * state_meter[3:5]

        # Automation's control
        input_automation = -np.matmul(self.Ke, state_meter)
        # Control constraints
        input_automation[0] = max(min(input_automation[0], self.max_u), self.min_u)
        input_automation[1] = max(min(input_automation[1], self.max_u), self.min_u)

        # Variability
        # if c_mode == 'optimal':
        #     T_mat = [[np.cos(state_meter[2]), np.sin(state_meter[2])], [-np.sin(state_meter[2]), np.cos(state_meter[2])]]
        #     mean = T_mat @ np.array([0.02, -0.02])
        #     vc = 0.985 ** self.k
        #     cov = 0.05 * vc * np.array([[0.005, 0.001], [0.001, 0.005]])
        #     w = np.random.multivariate_normal(mean, cov)
        #     input_automation[0] = input_automation[0] + w[0]
        #     input_automation[1] = input_automation[1] + w[1]

        # For testing
        # at = 0.6
        # if c_mode == 'manual':
        #     pointing[0] = max(min(at * pointing[0] + (1 - at) * input_automation[0], self.max_u), self.min_u)
        #     pointing[1] = max(min(at * pointing[1] + (1 - at) * input_automation[1], self.max_u), self.min_u)

        # Assistance penalty
        penalty = 10

        # Numerical example start ------------------------------------------------------------------------------------
        # if state_meter[1] > 500:
        #     # dummy_gain = self.Ke
        #     # dummy_gain[0][0] = 1.00 * dummy_gain[0][0]
        #     # Original Q = np.diag([1, 0.8, 100, 1, 1, 100])
        #     # Q_dummy = np.diag([20, 10, 0, 0, 0, 0])
        #     # Q_dummy = np.diag([10000, 0.1, 0, 0, 0, 0])
        #     # Q_dummy = np.diag([100, 0.1, 10, 1, 1, 10])
        #     Q_dummy = np.diag([1, 0.5, 50, 1, 1, 100])
        #     _, _, K_dummy = cnt.dare(self.A, self.B, Q_dummy, self.R)
        #     K_dummy = np.squeeze(np.array(K_dummy))
        #     dummy_input = -1.0 * K_dummy @ state_meter
        #     pointing[0] = max(min(dummy_input[0] + 0.0, self.max_u), self.min_u)
        #     pointing[1] = max(min(dummy_input[1] + 0.0, self.max_u), self.min_u)
        # elif state_meter[1] > 400:
        #     # dummy_gain = 2.0 * self.Ke
        #     # dummy_input = -1.0 * dummy_gain @ state_meter
        #     # Q_dummy = np.diag([15, 5, 100, 1, 1, 100])
        #     Q_dummy = np.diag([0.01, 0.01, 100, 0, 0, 100])
        #     # Q_dummy = np.diag([15, 5, 0.1, 0.1, 0.1, 0.1])
        #     _, _, K_dummy = cnt.dare(self.A, self.B, Q_dummy, self.R)
        #     K_dummy = np.squeeze(np.array(K_dummy))
        #     dummy_input = -1.0 * K_dummy @ state_meter
        #     pointing[0] = max(min(dummy_input[0], self.max_u), self.min_u)
        #     pointing[1] = max(min(dummy_input[1], self.max_u), self.min_u)
        # else:
        #     # Q_dummy = np.diag([4, 2, 100, 1, 1, 100])
        #     Q_dummy = np.diag([1, 0.8, 100, 1, 1, 100])
        #     _, _, K_dummy = cnt.dare(self.A, self.B, Q_dummy, self.R)
        #     K_dummy = np.squeeze(np.array(K_dummy))
        #     dummy_input = -1.0 * K_dummy @ state_meter
        #     pointing[0] = max(min(dummy_input[0], self.max_u), self.min_u)
        #     pointing[1] = max(min(dummy_input[1], self.max_u), self.min_u)
        #     # pointing[0] = 0.0
        #     # pointing[1] = 0.0
        # Numerical example end --------------------------------------------------------------------------------------

        # State copy
        self.Xk = np.copy(state_meter)

        # Optimal human input test
        # test_input = -1.0 * self.Ke @ state_meter + 0.0 * np.random.randn()
        # pointing[0] = max(min(0.5 * test_input[0] + 0.5 * pointing[0], 1.0), -1.0)
        # pointing[1] = max(min(0.5 * test_input[1] + 0.5 * pointing[1], 1.0), -1.0)

        if self.c_mode == 'HSC':
            # Online DMD
            p_prev = np.copy(self.P)
            self.Yk = self.A @ self.Xk + self.B @ pointing
            self.gamma = 1 / (1 + np.dot(self.Xk, self.P @ self.Xk))
            self.P = (1 / self.sigma ** 2) * (self.P - self.gamma * self.P @ np.outer(self.Xk, self.Xk) @ self.P)
            self.A_DMD = self.A_DMD + self.gamma * np.outer(self.Yk - self.A_DMD @ self.Xk, self.Xk) @ p_prev
            k_est = np.linalg.pinv(self.B) @ (self.A - self.A_DMD)

            # Guard condition with DMD
            # final_step = 450
            final_step = 200
            # if self.k < final_step and self.mode != 0:
            if self.mode != 0:
                # xx1 = np.zeros((final_step - self.k + 1, 6))
                # xx2 = np.zeros((final_step - self.k + 1, 6))
                # xx3 = np.zeros((final_step - self.k + 1, 6))
                xx1 = np.zeros((final_step + 1, 6))
                xx2 = np.zeros((final_step + 1, 6))
                xx3 = np.zeros((final_step + 1, 6))
                xx1[0] = np.copy(self.Xk)
                xx2[0] = np.copy(self.Xk)
                xx3[0] = np.copy(self.Xk)
                l1, l2, l3 = 0, 0, 0

                if self.k > 58:
                    # for i in range(0, final_step - self.k):
                    for i in range(0, final_step):
                        u_user = -k_est @ xx1[i]
                        u_auto = -self.Ke @ xx3[i]
                        u_shared_user = -k_est @ xx2[i]
                        u_shared_auto = -self.Ke @ xx2[i]
                        u_shared_user[0] = max(min(u_shared_user[0], self.max_u), self.min_u)
                        u_shared_user[1] = max(min(u_shared_user[1], self.max_u), self.min_u)
                        u_shared_auto[0] = max(min(u_shared_auto[0], self.max_u), self.min_u)
                        u_shared_auto[1] = max(min(u_shared_auto[1], self.max_u), self.min_u)
                        u_shared = 0.5 * u_shared_user + 0.5 * u_shared_auto

                        # Control constraints
                        u_user[0] = max(min(u_user[0], self.max_u), self.min_u)
                        u_user[1] = max(min(u_user[1], self.max_u), self.min_u)
                        u_auto[0] = max(min(u_auto[0], self.max_u), self.min_u)
                        u_auto[1] = max(min(u_auto[1], self.max_u), self.min_u)

                        xx1[i + 1] = self.A @ xx1[i] + self.B @ u_user
                        xx2[i + 1] = self.A @ xx2[i] + self.B @ u_shared
                        xx3[i + 1] = self.A @ xx3[i] + self.B @ u_auto

                        loss_constant = 1e-8
                        l1 = l1 + loss_constant * (np.dot(xx1[i], self.Q @ xx1[i]) + np.dot(u_user, self.R @ u_user))
                        l2 = l2 + loss_constant * (np.dot(xx2[i], self.Q @ xx2[i]) +
                                                   np.dot(u_shared, self.R @ u_shared) +
                                                   penalty * 0.5 ** 2 * np.dot(u_shared_auto, self.R @ u_shared_auto))
                        l3 = l3 + loss_constant * (np.dot(xx3[i], self.Q @ xx3[i]) +
                                                   (1 + penalty) * np.dot(u_auto, self.R @ u_auto))

                if np.isnan(l1):
                    l1 = np.inf
                if np.isnan(l2):
                    l2 = np.inf
                # print([l1, l2, l3])
                hsc_mode = np.argmin([l1, l2, l3])
                if hsc_mode == 0:
                    self.mode = 1
                elif hsc_mode == 1:
                    self.mode = 2
                elif hsc_mode == 2:
                    self.mode = 3
            else:
                if self.mode == 0:
                    pass
                else:
                    self.mode = 3

            # Control authority handover
            if self.mode == 1:
                control_status = 'Human'
                self.objects[0].linearized_quadrotor_dynamics(pointing[0], -pointing[1])
                self.authority = 1
                self.visual_code = BLUE
                self.accumulated_authority = self.accumulated_authority + 1
            elif self.mode == 2:
                control_status = 'Shared control'
                pointing = 0.95 * pointing + 0.05 * input_automation
                self.objects[0].linearized_quadrotor_dynamics(pointing[0], -pointing[1])
                self.authority = 0.5
                self.visual_code = YELLOW
                self.accumulated_authority = self.accumulated_authority + 0.5
            else:
                control_status = 'Automation'
                pointing = input_automation
                self.objects[0].linearized_quadrotor_dynamics(pointing[0], -pointing[1])
                self.authority = 0
                self.visual_code = RED

            # Evaluating the loss function
            self.loss = self.loss + np.dot(self.Xk, self.Q @ self.Xk) + np.dot(pointing,
                                                                               self.R @ pointing) + penalty * (
                                1 - self.authority) ** 2 * np.dot(
            input_automation, self.R @ input_automation)

            # Evaluating the task objective function
            self.task_obj = self.task_obj + np.dot(self.Xk, self.Q @ self.Xk) + np.dot(pointing, self.R @ pointing)

        elif self.c_mode == 'OCIP':
            gamma_angle = 90.0 * np.pi / 180.0
            if np.linalg.norm(pointing) > 1e-16:
                unit_vector_1 = pointing / np.linalg.norm(pointing)
                unit_vector_2 = input_automation / np.linalg.norm(input_automation)
                dot_product = np.dot(unit_vector_1, unit_vector_2)
            else:
                dot_product = 0.0
            # error handling
            dot_product = max(min(dot_product, 1.0), -1.0)
            angle_dot = np.arccos(dot_product)
            if self.mode != 0:
                if self.k < 58:
                    self.mode = 1
                elif abs(angle_dot) < gamma_angle:
                    self.mode = 1
                else:
                    self.mode = 3
            else:
                if self.mode == 0:
                    pass
                else:
                    self.mode = 3
            if self.mode == 1:
                control_status = 'Human (baseline)'
                self.objects[0].linearized_quadrotor_dynamics(human_input[0], -human_input[1])
                self.authority = 1
                self.loss_baseline = self.loss_baseline + np.dot(self.Xk, self.Q @ self.Xk) \
                                     + np.dot(human_input, self.R @ human_input)
                self.visual_code = BLUE
                self.accumulated_authority = self.accumulated_authority + 1

                # Evaluating the task objective function
                self.task_obj = self.task_obj + np.dot(self.Xk, self.Q @ self.Xk) + np.dot(human_input,
                                                                                           self.R @ human_input)
            else:
                control_status = 'Automation (baseline)'
                self.objects[0].linearized_quadrotor_dynamics(0.0, 0.0)
                self.authority = 0
                input_automation = -human_input
                self.loss_baseline = self.loss_baseline + np.dot(self.Xk, self.Q @ self.Xk)
                # self.loss_baseline = self.loss_baseline + np.dot(self.Xk, self.Q @ self.Xk) \
                #                      + penalty * 0.5 ** 2 * np.dot(input_automation, self.R @ input_automation)
                pointing = np.array((0.0, 0.0))
                self.visual_code = RED

                # Evaluating the task objective function
                self.task_obj = self.task_obj + np.dot(self.Xk, self.Q @ self.Xk)

            self.loss = self.loss_baseline
            angle_deg = angle_dot * 180 / np.pi
            # self.status.update('Angle difference: %.1f deg' % angle_deg)
        elif self.c_mode == 'manual':
            control_status = 'OFF'
            self.objects[0].linearized_quadrotor_dynamics(pointing[0], -pointing[1])
            self.loss = self.loss + np.dot(self.Xk, self.Q @ self.Xk) + np.dot(human_input, self.R @ human_input)
            self.visual_code = BLUE
            self.accumulated_authority = self.accumulated_authority + 1

            # Evaluating the task objective function
            self.task_obj = self.task_obj + np.dot(self.Xk, self.Q @ self.Xk) + np.dot(pointing, self.R @ pointing)
        elif self.c_mode == 'optimal':
            pointing = np.copy(input_automation)
            control_status = 'Optimal test'
            self.objects[0].linearized_quadrotor_dynamics(pointing[0], -pointing[1])
            self.loss = self.loss + np.dot(self.Xk, self.Q @ self.Xk) + np.dot(input_automation,
                                                                               self.R @ input_automation)
            self.visual_code = RED

            # Evaluating the task objective function
            self.task_obj = self.task_obj + np.dot(self.Xk, self.Q @ self.Xk) + np.dot(pointing, self.R @ pointing)
        elif self.c_mode == 'shared':
            if self.start_trial == 0:
                if np.array_equal(pointing, np.array([0, 0])) == False:
                    self.start_trial = 1
                else:
                    input_automation = np.array([0, 0])

            pointing = 0.6 * pointing + 0.4 * input_automation #0.5 * (pointing + input_automation)
            control_status = 'ON'
            self.objects[0].linearized_quadrotor_dynamics(pointing[0], -pointing[1])
            self.loss = 0
            self.visual_code = YELLOW
        else:
            pass

        # Time step update
        self.k = self.k + 1

        # Displaying states
        # display_pos = 1.0 / BOUND_Y_MAX * np.array([pos[0] - BOUND_X_MAX / 2, BOUND_Y_MAX - pos[1]])
        # spd_const = 1
        # display_spd = 1.0 / BOUND_Y_MAX * np.array([spd_const * spd[0], -spd_const * spd[1]])
        # display_att = -att * 180 / np.pi
        # if self.initial:
        #     self.t0 = pygame.time.get_ticks()
        # self.status.update('Position: %.3f, %.3f' % (display_pos[0], display_pos[1]))
        # self.status.update('Speed: %.3f, %.3f' % (display_spd[0], display_spd[1]))
        # self.status.update('Attitude: %.2f deg' % display_att)
        # self.status.update('Input: %.2f, %.2f' % (pointing[0], pointing[1]))
        # self.status.update('Human Input: %.2f, %.2f' % (human_input[0], human_input[1]))
        # time_display = (pygame.time.get_ticks() - self.t0) / 1000
        # self.status.update('Time: %.1f sec' % time_display)
        # self.status.update('Mode: %s' % control_status)
        if self.initial:
            self.t0 = pygame.time.get_ticks()
        # self.status.update('Position: x: %.3f m, y: %.3f m' % (state_meter[0], state_meter[1]))
        self.status.update('Speed: %.3f m/s' % np.linalg.norm([state_meter[3], state_meter[4]]))
        #self.status.update('Speed:   x: %.3f m/s, y: %.3f m/s' %(state_meter[3], state_meter[4]))
        self.status.update('Attitude: %.2f deg' % (state_meter[2]*180/np.pi))
        # self.status.update('Input: %.2f, %.2f' % (pointing[0], pointing[1]))
        # self.status.update('Human Input: %.2f, %.2f' % (human_input[0], human_input[1]))
        time_display = (pygame.time.get_ticks() - self.t0) / 1000
        self.time_font.update('Time: %.1f s' % time_display)
        if control_status == 'OFF':
            self.mode_font.update2('Automation Assistance: %s' % control_status, RED)
        else:
            self.mode_font.update2('Automation Assistance: %s' % control_status, GREEN)


        # Remove redundant objects
        for inx in remove_id:
            obj = self.objects[inx]
            self.objects.pop(inx)
            del obj

        # Collision
        for collider in self.collideds:
            if collider.classification == 'obstacle_long.png':
                collider.load(IMAGE_PATH + 'obstacle_long_touch.png')

        # Time modulation
        curr_time = [pygame.time.get_ticks() - self.t0]
        time_gap = curr_time[0] - self.time_prev
        time_standard = int(1000*DELTAT)
        if not self.initial:
            if time_gap < time_standard:
                pygame.time.delay(time_standard - time_gap)
        curr_time = [pygame.time.get_ticks() - self.t0]

        # Record
        state = [state_meter[0], state_meter[1], state_meter[2], state_meter[3], state_meter[4], state_meter[5]]
        # action = [input_automation[0], input_automation[1], human_input[0], human_input[1]]
        action = [input_automation[0], input_automation[1], pointing[0], pointing[1]]

        # Previous angle (for collision dynamics)
        # self.previous_angle = angle

        # Previous angle (for angle input dynamics)
        self.prev_angle = angle - 2 * np.pi * self.cycle

        # Previous time
        self.time_prev = curr_time[0]

        test_time = (pygame.time.get_ticks() - self.t0) / 1000
        if test_time > 120.0:
            self.collision = True
            self.final_time_record = test_time
            self.mode = 0

        return curr_time, state, action, [self.authority], [self.loss]

    def render(self):

        # Background
        self.screen.fill(WHITE)
        self.screen.blit(self.background.surface, self.background.rect)

        # Visual feedback
        # pygame.draw.rect(self.screen, self.visual_code, (0, BOUND_Y_MAX-100, 100, 100))

        # Rotate
        self.objects[0].rt = self.objects[0].attitude * 180.0 / np.pi
        self.objects[0].load(IMAGE_PATH + 'drone.png')

        # Objects
        for i, obj in enumerate(self.objects):
            self.screen.blit(obj.surface, obj.rect)

        # font interface
        for text in self.instruction.texts:
            self.screen.blit(text[0], text[1])
        for text in self.status.texts:
            self.screen.blit(text[0], text[1])
        for text in self.time_font.texts:
            self.screen.blit(text[0], text[1])
        for text in self.mode_font.texts:
            self.screen.blit(text[0], text[1])

        # record sign
        if self.record and self.record_sign > 0:
            pygame.draw.circle(self.screen, RED, (20, 20), 10)

        # double buffer update
        pygame.display.flip()

        # Pausing
        # if self.initial:
        #     # Wait time (mil-sec)
        #     pygame.time.delay(2500)
        #     self.initial = False
        #     self.t0 = pygame.time.get_ticks()
        while self.initial:
            pygame.joystick.init()
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            pygame.draw.rect(self.screen, BLACK, pygame.Rect(BOUND_X_MIN, BOUND_Y_MIN, BOUND_X_MAX, BOUND_Y_MAX))
            font = pygame.font.Font('freesansbold.ttf', 32)
            if self.c_mode == 'shared':
                start_text = font.render("Press any joystick button to start trial %d" % (self.trial + 1), True,  WHITE)
                auto_text = font.render("Automation Assistance: %s" % 'ON', True, GREEN)
                start_text_width = start_text.get_width()
                start_text_height = start_text.get_height()
                auto_text_width = auto_text.get_width()
                auto_text_height = auto_text.get_height()
                self.screen.blit(font.render("Press any joystick button to start trial %d" % (self.trial + 1), True,  WHITE), ((BOUND_X_MAX-BOUND_X_MIN)/2 - start_text_width/2, (BOUND_Y_MAX-BOUND_Y_MIN)/2 - start_text_height/2))           
                self.screen.blit(font.render("Automation Assistance: %s" % 'ON', True, GREEN), ((BOUND_X_MAX-BOUND_X_MIN)/2 - auto_text_width/2, (BOUND_Y_MAX-BOUND_Y_MIN)/2+auto_text_height/2))           

            else:
                start_text = font.render("Press any joystick button to start trial %d" % (self.trial + 1), True,  WHITE)
                auto_text = font.render("Automation Assistance: %s" % 'OFF', True, RED)
                start_text_width = start_text.get_width()
                start_text_height = start_text.get_height()
                auto_text_width = auto_text.get_width()
                auto_text_height = auto_text.get_height()
                self.screen.blit(font.render("Press any joystick button to start trial %d" % (self.trial + 1), True,  WHITE), ((BOUND_X_MAX-BOUND_X_MIN)/2 - start_text_width/2, (BOUND_Y_MAX-BOUND_Y_MIN)/2 - start_text_height/2))           
                self.screen.blit(font.render("Automation Assistance: %s" % 'OFF', True, RED), ((BOUND_X_MAX-BOUND_X_MIN)/2 - auto_text_width/2, (BOUND_Y_MAX-BOUND_Y_MIN)/2+auto_text_height/2))   

            # start_text = font.render("Press any joystick button to start trial %d" % (self.trial + 1), True,  WHITE)
            # start_text_width = start_text.get_width()
            # self.screen.blit(font.render("Press any joystick button to start trial %d" % (self.trial + 1), True,  WHITE), ((BOUND_X_MAX-BOUND_X_MIN)/2 - start_text_width/2, (BOUND_Y_MAX-BOUND_Y_MIN)/2))
            #pygame.display.update()
            pygame.display.flip()
            # self.instruction.update2("Click Any Joystick Button to Start Trial %d" % (self.trial + 1), WHITE)
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                #if event.type == KEYDOWN:
                    #if event.key == K_F1:
                    self.initial = False
                    self.t0 = pygame.time.get_ticks()
                    self.instruction.clear()
                    #string_for_iMotions="E;1;EventSourceId;1;0.0;;;SampleId;" + "Flag" + "\r\n"
                    #string_for_iMotions = "M;1;EventSourceId;1;0.0;;;SampleId;" + str(1) + "\r\n"
                    string_for_iMotions = "M;2;;;Trial"+str(self.trial+1)+";TrialStart;S;V\r\n"  # assuming this starts trial
                    sendudp(string_for_iMotions)
                    self.start_trial = 0


        # Text info
        if not self.mode and self.landing == 1:#not self.collision and not self.land:
            #string_for_iMotions = "E;1;EventSourceId;1;0.0;;;SampleId;" + "Flag" + "\r\n"
            #string_for_iMotions = "M;1;EventSourceId;1;0.0;;;SampleId;" + str(1) + "\r\n"
            # string_for_iMotions = "M;2;;;Trial" + str(self.trial + 1) + ";;E;\r\n"  # assuming this ends trial
            # sendudp(string_for_iMotions)
            self.trial += 1
            display_surface = pygame.display.set_mode((BOUND_X_MAX, BOUND_Y_MAX))
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('Trial %d: Safe landing at %.2f sec' % (self.trial, self.final_time_record), True, WHITE, BLACK)
            textrect = text.get_rect()
            textrect.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2)
            # Self-confidence text
            # text_sc = font.render('Press any joystick button to continue to the survey.', True, WHITE, BLACK)
            # textrect_sc = text_sc.get_rect()
            # textrect_sc.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2 + 100)
            display_surface.fill(BLACK)
            display_surface.blit(text, textrect)
            # display_surface.blit(text_sc, textrect_sc)
            pygame.display.update()
            #pygame.time.delay(2500)

        elif not self.mode and not self.collision and self.landing == 2: #self.land:
            #string_for_iMotions = "E;1;EventSourceId;1;0.0;;;SampleId;" + "Flag" + "\r\n"
            #string_for_iMotions = "M;1;EventSourceId;1;0.0;;;SampleId;" + str(1) + "\r\n"
            # string_for_iMotions = "M;2;;;Trial" + str(self.trial + 1) + ";;E;\r\n"  # assuming this ends trial
            # sendudp(string_for_iMotions)
            self.trial += 1
            display_surface = pygame.display.set_mode((BOUND_X_MAX, BOUND_Y_MAX))
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('Trial %d: Unsafe landing at %.2f sec' % (self.trial, self.final_time_record), True, WHITE, BLACK)
            textrect = text.get_rect()
            textrect.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2)
            # Self-confidence text
            # text_sc = font.render('Press any joystick button to continue to the survey.', True, WHITE, BLACK)
            # textrect_sc = text_sc.get_rect()
            # textrect_sc.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2 + 100)
            display_surface.fill(BLACK)
            display_surface.blit(text, textrect)
            # display_surface.blit(text_sc, textrect_sc)
            # input("Press Enter to continue...")
            pygame.display.update()
            #pygame.time.delay(2500)
        elif not self.mode and self.collision:
            #string_for_iMotions = "E;1;EventSourceId;1;0.0;;;SampleId;" + "Flag" + "\r\n"
            # string_for_iMotions = "M;2;;;Trial" + str(self.trial + 1) + ";;E;\r\n"  # assuming this ends trial
            # sendudp(string_for_iMotions)
            self.trial += 1
            display_surface = pygame.display.set_mode((BOUND_X_MAX, BOUND_Y_MAX))
            font = pygame.font.Font('freesansbold.ttf', 32)

            if self.final_time_record < 120.0:
                text = font.render('Trial %d: Unsuccessful landing at %.2f sec' % (self.trial, self.final_time_record), True,
                                WHITE, BLACK)
            else:
                text = font.render('Trial %d: Battery died. Unsuccessful landing at %.2f sec' % (self.trial, self.final_time_record), True,
                                   WHITE, BLACK)
            textrect = text.get_rect()
            textrect.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2)
            # Self-confidence text
            # text_sc = font.render('Press any joystick button to continue to the survey.', True, WHITE, BLACK)
            # textrect_sc = text_sc.get_rect()
            # textrect_sc.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2 + 100)
            display_surface.fill(BLACK)
            display_surface.blit(text, textrect)
            # display_surface.blit(text_sc, textrect_sc)
            pygame.display.update()
            #pygame.time.delay(2500)
