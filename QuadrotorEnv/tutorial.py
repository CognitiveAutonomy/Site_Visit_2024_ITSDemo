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

obstacle_spawn = pygame.USEREVENT+1
record_Sign = pygame.USEREVENT+2
obstacle_clock = 80
time_delta = 30
record_sign_interval = 5


# game manager object
class TutorialMgr:
    #def __init__(self, mode=1, control='joystick', time_limit=60.0):
    def __init__(self, mode=1, control='joystick', time_limit=60.0):
        random.seed()

        # mode initialization
        self.initial = True
        self.mode = mode
        self.record = True
        self.record_sign = record_Sign
        self.t0 = 0
        self.control = control
        self.final_time_record = 0
        self.time = 0.0
        self.time_prev = 0.0
        self.landing = 0
        self.k = 0
        self.time_limit = time_limit

        self.max_u = 1.0
        self.min_u = -1.0

        # Collision dynamics
        # self.collide_consecutive = 0
        # self.collide_angle = 0
        # self.previous_angle = 0
        self.collision = False

        # Controller dynamics
        self.prev_angle = 0
        self.cycle = 0

        # game screen initialization
        pygame.init()
        pygame.font.init()
        # Joystick initialization
        if control == 'joystick':
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        # ps4 initialization
        if control == 'ps4':
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        if control == 'switch':
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        # initial window position
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (10, 50)
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
        x_init_real = 0
        y_init_real = 28
        init_pixel = quadrotor.position_meter_to_pixel(np.array([x_init_real, y_init_real]))
        x_init_pixel = init_pixel[0]
        y_init_pixel = init_pixel[1]

        main_drone = Quadrotor(file_name=IMAGE_PATH + 'drone.png', sc=0.20, rt=0.0,
                               pos_x=x_init_pixel, pos_y=y_init_pixel, is_drag=False)
        self.objects.append(main_drone)

        # Background and text interface init
        self.background = Background(file_name=IMAGE_PATH + 'Purdue_tutorial.png', moving_name=IMAGE_PATH + 'road.png',
                                     bound_x_min=BOUND_X_MIN, bound_x_max=BOUND_X_MAX, bound_y_min=BOUND_Y_MIN,
                                     bound_y_max=BOUND_Y_MAX)
        self.status = Font(FONT, FONT_SIZE, (375, 807))
        self.instruction = Font(FONT2, int(FONT_SIZE*1.9), (BOUND_X_MAX/2 - 400, BOUND_Y_MAX/2 - 100))
        self.time_font = Font(FONT, int(FONT_SIZE*1.5), (BOUND_X_MAX/2 - 100, 60))
        self.mode_font = Font(FONT2, int(FONT_SIZE*2.0), (BOUND_X_MAX/2 - 375, 20))
        self.instruction.update("Click Any Joystick Button to Start Tutorial")
        # self.instruction.update("SIMULATION INSTRUCTION")
        # self.instruction.update("Input device: %s" % control)

        # Event message
        self.events = []
        self.action = None

        # Putting obstacles
        yc = self.background.max_bound[1] / 2
        self.events.append(obstacle_spawn)

        # Mouse input
        if control == 'mouse':
            self.mouse_pos = []

        # Joystick input
        if control == 'joystick':
            self.joystick_axis = []

        # ps4 input
        if control == 'ps4':
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
            if self.control == 'ps4':
                self.joystick_axis = [self.joystick.get_axis(2), self.joystick.get_axis(1)]
            if self.control == 'switch':
                self.joystick_axis = [self.joystick.get_axis(2), self.joystick.get_axis(1)]

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
                    self.mode = 4
                if y < self.background.min_bound[1]:
                    y = self.background.min_bound[1]
                    self.collision = True
                    self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                    self.mode = 4
                if x > self.background.max_bound[0]:
                    x = self.background.max_bound[0]
                    self.collision = True
                    self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                    self.mode = 4
                if y > self.background.max_bound[1] - 10:
                    y = self.background.max_bound[1] - 10
                    self.collision = True
                    self.final_time_record = (pygame.time.get_ticks() - self.t0) / 1000
                    self.mode = 4
                obj.position = np.array([x, y])
            if i != 0:
                if y > self.background.max_bound[1] + 200:
                    remove_id.append(i)
                if main.rect.colliderect(obj.rect):
                    self.collideds.append(obj)
                    # Conditions for a successful landing
                    # Deleted

        # System noise (uncertainty)
        # angle_noise = np.random.normal(loc=0.0, scale=0.0)
        angle_noise = 0

        # Penguin states
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
        elif self.control == 'joystick':
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
        elif self.control == 'ps4':
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
        elif self.control == 'switch':
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

        # States for control
        state_pixel = np.hstack((pos, att, spd, ang_vel))
        state_meter = quadrotor.state_pixel_to_meter(state_pixel)

        # manual mode only for this tutorial
        control_status = 'OFF'
        self.objects[0].linearized_quadrotor_dynamics(pointing[0], -pointing[1])

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
        self.status.update('Speed: %.3f m/s' % np.linalg.norm([state_meter[3],state_meter[4]]))
        # self.status.update('Speed:   x: %.3f m/s, y: %.3f m/s' % (state_meter[3], state_meter[4]))
        self.status.update('Attitude: %.2f deg' % (state_meter[2]*180/np.pi))
        # self.status.update('Input: %.2f, %.2f' % (pointing[0], pointing[1]))
        # self.status.update('Human Input: %.2f, %.2f' % (human_input[0], human_input[1]))
        time_display = (pygame.time.get_ticks() - self.t0) / 1000
        self.time_font.update('Time: %.1f s' % time_display)
        self.mode_font.update('Practice Round: Thrust And Attitude')

        # Check time-up
        if time_display > self.time_limit:
            self.mode = 0

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
        action = [pointing[0], pointing[1]]

        # Previous angle (for collision dynamics)
        # self.previous_angle = angle

        # Previous angle (for angle input dynamics)
        self.prev_angle = angle - 2 * np.pi * self.cycle

        # Previous time
        self.time_prev = curr_time[0]

        return curr_time, state, action

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
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    self.initial = False
                    self.t0 = pygame.time.get_ticks()
                    self.instruction.clear()

        # Text info for each event
        if self.mode == 4:
            display_surface = pygame.display.set_mode((BOUND_X_MAX, BOUND_Y_MAX))
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('%.2f sec' % self.final_time_record, True,
                               WHITE, BLACK)
            textrect = text.get_rect()
            textrect.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2)
            # Self-confidence text
            text_sc = font.render('Try Again.', True, WHITE, BLACK)
            textrect_sc = text_sc.get_rect()
            textrect_sc.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2 + 100)
            display_surface.fill(BLACK)
            display_surface.blit(text, textrect)
            display_surface.blit(text_sc, textrect_sc)
            pygame.display.update()
            pygame.time.delay(2500)
            # Re-locate the quadrotor
            init_pixel = quadrotor.position_meter_to_pixel(np.array([0, 28]))
            self.objects[0] = Quadrotor(file_name=IMAGE_PATH + 'drone.png', sc=0.20, rt=0.0, pos_x=init_pixel[0],
                                        pos_y=init_pixel[1], is_drag=False)
            self.mode = 1
        elif self.mode == 0:
            display_surface = pygame.display.set_mode((BOUND_X_MAX, BOUND_Y_MAX))
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render('End of Tutorial: %.2f sec. Starting Experiment.' % self.time_limit, True,
                               WHITE, BLACK)
            textrect = text.get_rect()
            textrect.center = (BOUND_X_MAX // 2, BOUND_Y_MAX // 2)
            display_surface.fill(BLACK)
            display_surface.blit(text, textrect)
            pygame.display.update()
            pygame.time.delay(2500)
