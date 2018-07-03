import pygame

class Scanner(object):
    num_pulses_till_start = 10

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

    trials_per_block = 18
    instruction_duration = 2

    percent_congruent_trials = 0.5
    num_congruent_trials = int(trials_per_block * percent_congruent_trials)
    num_incongruent_trials = trials_per_block - num_congruent_trials


class Instruction(object):
    text = "Choose a category!"
    font = "Arial"
    font_size = 30
    text_color = pygame.Color(255, 255, 255)


class Stimuli(object):
    color_key = pygame.Color(255, 255, 255)
    house_prefix = "h"
    face_prefix = "f"
    path = "img"