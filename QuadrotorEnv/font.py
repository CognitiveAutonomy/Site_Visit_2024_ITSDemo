import pygame
import numpy as np
from config import *

line_width = 1.5


class Font:
    def __init__(self, font_name, size, pos):
        self.font = pygame.font.SysFont(font_name, size)
        self.font_name = font_name
        self.size = size
        self.pos = pos
        self.texts = []

    def update(self, content):
        text = self.font.render(content, True, BLACK)
        posx = self.pos[0]
        posy = self.pos[1] + len(self.texts) * self.size * line_width
        self.texts.append((text, (posx, posy)))

    def update2(self, content, color):
        text = self.font.render(content, True, color)
        posx = self.pos[0]
        posy = self.pos[1] + len(self.texts) * self.size * line_width
        self.texts.append((text, (posx, posy)))

    def clear(self):
        self.texts = []
