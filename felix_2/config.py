import pygame

class Screen(object):
    resolution = (1024, 768)
    center = tuple(r/2 for r in resolution)
    background = pygame.Color(0, 0, 0)


class Fixcross(object):
    color = pygame.Color(255, 255, 255)
    length = 100
    width = 10


class Keys(object):
    pulse = pygame.K_t


class Paradigm(object):
    blocks_per_run = 18
    inter_block_interval = (7, 10)
    ibi_mean = (inter_block_interval[0] + inter_block_interval[1]) / 2
    ibi_mean_error_tollerance = 0.05 * ibi_mean