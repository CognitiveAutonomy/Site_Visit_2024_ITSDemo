from config import *
import pygame
import math
import numpy as np

speed_scale_factor = 0.4
angular_scale_factor = 0.003
acceleration_scale_factor = 3.0
drag_scale_factor = 0.0
speed_max = 10
target_buffer = 0  # target tolerance
dt = DELTAT


class Quadrotor:
    """
    methods:
    attributes:
    """

    def __init__(self, file_name, pos_x=512, pos_y=384, spd_x=0, spd_y=0, acc_x=0, acc_y=0, sc=1, rt=0, is_drag=True,
                 control_parameter=[0.0, 0.0]):
        self.sc = sc
        self.rt = rt
        self.position = np.array([pos_x, pos_y])
        self.load(file_name)
        self.speed = np.array([spd_x, spd_y])
        self.acc = np.array([0.0, 0.0])
        self.accelerate(np.array([acc_x, acc_y]))
        # Attitude
        self.attitude = 0.0
        self.angular_vel = 0.0
        self.angular_acc = 0.0
        self.phi = np.array([0.0, 0.0, 0.0])
        self.phi_dot = np.array([0.0, 0.0, 0.0])
        self.theta = 0
        self.is_drag = is_drag
        self.is_targeting = False
        self.control_parameter = control_parameter
        self.figure = []
        # self.surface = []
        self.rect = []
        self.target = []
        if len(file_name) > 17:
            self.classification = file_name[-17:]
        # print(BOUND_X_MAX)

    def load(self, file_name):
        self.figure = pygame.image.load(file_name)
        self.surface = self.figure
        self.scale(self.sc)
        self.rotate(self.rt)
        self.rect = self.surface.get_rect()
        self.rect.center = tuple(self.position)

    def update(self):
        if self.is_drag:
            self.drag()
        if self.is_targeting:
            self.target_move()
        self.move()
        self.rect = self.surface.get_rect()
        self.rect.center = tuple(self.position)

    def set_target(self, pos):
        self.is_targeting = True
        self.target = pos

    def target_move(self):
        if np.all(np.abs(self.position - self.target) < target_buffer):
            self.is_targeting = False
            self.speedup(np.array([0, 0]))
        else:
            acc = self.target - self.position
            self.accelerate(acc / np.linalg.norm(acc))

    def move(self):
        self.speed = self.speed + self.acc * dt
        self.position = self.position + self.speed * dt
        self.angular_vel = self.angular_vel + self.angular_acc * dt
        self.attitude = self.attitude + self.angular_vel * dt

    def drag(self):
        sp_norm = np.linalg.norm(self.speed)
        if sp_norm > 0:
            drag_speed = self.speed - self.speed * (drag_scale_factor / sp_norm)
            over = drag_speed * self.speed > 0
            self.speed = drag_speed * over

    def speedup(self, spd):
        self.speed = spd
        sp_norm = np.linalg.norm(self.speed)
        if sp_norm > speed_max:
            self.speed *= speed_max / sp_norm

    def accelerate(self, acc):
        self.speedup(self.speed + np.array(acc) * angular_scale_factor)

    def scale(self, sc):
        w = int(self.surface.get_width() * sc)
        h = int(self.surface.get_height() * sc)
        self.surface = pygame.transform.scale(self.surface, (w, h))
        self.rect = self.surface.get_rect()

    def rotate(self, rt):
        self.surface = pygame.transform.rotate(self.surface, rt)
        self.rect = self.surface.get_rect()

    def speed_control(self, theta):
        # Directly control the heading angle
        self.phi[0] = self.control_parameter[0] * theta + self.control_parameter[1]

        # Smoothed heading angle by 2nd order system
        # self.phi_dot[0] = self.phi[1]
        # self.phi_dot[1] = -2 * DAMP * WN * self.phi[1] - (WN ** 2) * self.phi[0] + self.control_parameter * (
        #         WN ** 2) * theta

        self.speed[0] = speed_max * math.cos(self.phi[0])
        self.speed[1] = speed_max * math.sin(self.phi[0])

    def pid_control(self, theta):
        self.phi_dot[0] = self.phi[1]
        self.phi_dot[1] = self.phi[2]
        self.phi_dot[2] = -WN ** 2 * Ki * self.phi[0] - WN ** 2 * (1 + Kp) * self.phi[1] - WN * (
                2 * DAMP + WN * Kd) * self.phi[2] + theta

        self.theta = C.dot(self.phi)

        self.speed[0] = speed_max * math.cos(self.theta)
        self.speed[1] = speed_max * math.sin(self.theta)

    def quadrotor_dynamics(self, ux, uy):
        cp = self.control_parameter

        thrust_diff_human = 60.0 * ux
        thrust_diff_machine = 60.0 * self.attitude + 30.0 * self.angular_vel + cp[0] * self.speed[0]  # -0.1
        thrust_total_human = 60.0 * uy
        thrust_total_machine = -60.0 + cp[1] * self.speed[1]  # -0.5

        # Control constraints
        thrust_total = max(-200.0, thrust_total_human + thrust_total_machine)
        thrust_diff = thrust_diff_human + thrust_diff_machine
        if thrust_diff > 100.0:
            thrust_diff = 100.0
        elif thrust_diff < -100.0:
            thrust_diff = -100.0

        self.acc[0] = thrust_total * np.sin(self.attitude)
        self.acc[1] = thrust_total * np.cos(self.attitude) + 8.0 * 9.8    # ( = m*g)
        self.angular_acc = -0.2/2 * thrust_diff     # length/2 at the front

        # Temp
        self.acc = 1 * self.acc
        self.angular_acc = 1 * self.angular_acc

    def linearized_quadrotor_dynamics(self, ux, uy):
        g = 9.8
        m = 0.35
        Ixx = 0.050
        uy = -uy
        # self.acc[0] = -15.0 * g * self.attitude
        # self.acc[1] = 30.0 * uy / m - 0.1 * self.speed[1]
        # self.angular_acc = -ux / Ixx - 1.0 * self.attitude - 1.0 * self.angular_vel
        state_pixel = np.hstack((self.position, self.attitude, self.speed, self.angular_vel))
        state_meter = state_pixel_to_meter(state_pixel)
        acc_x = g * state_meter[2]
        acc_y = -0.1 * state_meter[4] + uy / m
        ang_acc = ux / Ixx - 1.0 * state_meter[2] - 30.0 * state_meter[5]
        acc_meter = np.hstack((acc_x, acc_y, ang_acc))
        acc_pixel = acc_meter_to_pixel(acc_meter)
        self.acc[0] = acc_pixel[0]
        self.acc[1] = acc_pixel[1]
        self.angular_acc = acc_pixel[2]


def position_pixel_to_meter(pixel):
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    b1 = -BOUND_REAL_X / 2
    b2 = REAL_DIM_RATIO * BOUND_Y_MAX
    b = np.array([b1, b2])
    meter = trans @ pixel + b
    return meter


def position_meter_to_pixel(meter):
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    trans = np.linalg.inv(trans)
    b1 = -BOUND_REAL_X / 2
    b2 = REAL_DIM_RATIO * BOUND_Y_MAX
    b = np.array([b1, b2])
    pixel = trans @ (meter - b)
    return pixel


def state_pixel_to_meter(pixel):
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    b1 = -BOUND_REAL_X / 2
    b2 = REAL_DIM_RATIO * BOUND_Y_MAX
    b = np.array([b1, b2])
    meter_pos = trans @ pixel[0:2] + b
    meter_vel = trans @ pixel[3:5]
    meter_ang = -pixel[2]
    meter_ang_rate = -pixel[5]
    meter = np.hstack((meter_pos, meter_ang, meter_vel, meter_ang_rate))
    return meter


def state_meter_to_pixel(meter):
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    trans = np.linalg.inv(trans)
    b1 = -BOUND_REAL_X / 2
    b2 = REAL_DIM_RATIO * BOUND_Y_MAX
    b = np.array([b1, b2])
    pixel_pos = trans @ (meter[0:2] - b)
    pixel_vel = trans @ meter[3:5]
    pixel_ang = -meter[2]
    pixel_ang_rate = -meter[5]
    pixel = np.hstack((pixel_pos, pixel_ang, pixel_vel, pixel_ang_rate))
    return pixel


def acc_meter_to_pixel(meter):
    trans = REAL_DIM_RATIO * np.array([[1, 0], [0, -1]])
    trans = np.linalg.inv(trans)
    pixel_acc = trans @ meter[0:2]
    pixel_ang_acc = - meter[2]
    pixel = np.hstack((pixel_acc, pixel_ang_acc))
    return pixel
