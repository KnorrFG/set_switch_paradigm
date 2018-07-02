import pygame

import config as c

def fixcross(surface):
    half_len = c.Fixcross.length // 2
    center = c.Screen.center
    pygame.draw.line(surface, c.Fixcross.color, 
        (center[0] - half_len, center[1]),
        (center[0] + half_len, center[1]), 
        c.Fixcross.width)
    pygame.draw.line(surface, c.Fixcross.color, 
        (center[0], center[1] - half_len),
        (center[0], center[1] + half_len),
        c.Fixcross.width)