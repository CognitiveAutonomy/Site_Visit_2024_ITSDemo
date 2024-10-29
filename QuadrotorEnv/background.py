import pygame
import numpy as np
from game import *

background_speed = 6
pathway_width = 50
mid = 534


class Background:
    def __init__(self, file_name, moving_name, bound_x_min, bound_x_max, bound_y_min, bound_y_max):
        self.figure = pygame.image.load(file_name)
        self.surface = self.figure
        self.surface = pygame.transform.scale(self.surface, (bound_x_max, bound_y_max))
        self.rect = self.surface.get_rect()
        self.min_bound = np.array([bound_x_min, bound_y_min])
        self.max_bound = np.array([bound_x_max, bound_y_max])
