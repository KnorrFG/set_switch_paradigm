import pygame

class Scanner(object):
    num_pulses_till_start = 10


class Screen(object):
    resolution = (1920, 1080)
    center = tuple(r/2 for r in resolution)
    background = pygame.Color(255, 255, 255)


class Fixcross(object):
    color = pygame.Color(0, 0, 0)
    length = 100
    width = 10


class Keys(object):
    pulse = pygame.K_t
    key_left = pygame.K_LEFT
    key_right = pygame.K_RIGHT
    answer_keys = (key_left, key_right)


class Paradigm(object):
    blocks_per_run = 3
    inter_block_interval = (7, 10)
    ibi_mean = (inter_block_interval[0] + inter_block_interval[1]) / 2
    ibi_mean_error_tollerance = 0.05 * ibi_mean

    trials_per_block = 5
    instruction_duration = 2
    allowed_errors_per_block = 1
    feedback_display_time = 2

    percent_congruent_trials = 0.5
    num_congruent_trials = int(trials_per_block * percent_congruent_trials)
    num_incongruent_trials = trials_per_block - num_congruent_trials

    trial_timeout = 2.5
    prefered_trial_length = 1
    min_iti = 0.2


class Text(object):
    instruction = "Choose a category!"
    font = "Arial"
    font_size = 30
    text_color = pygame.Color(0, 0, 0)


class Stimuli(object):
    color_key = pygame.Color(255, 255, 255)
    house_prefix = "h"
    face_prefix = "f"
    path = "img"
    background = pygame.Color(255, 255, 255)
    width = 311
    height = 233
    plot_coord = (int(Screen.center[0] - 0.5 * width),
        int(Screen.center[1] - 0.5 * height))


class Feedback(object):
    inner_margin = 10
    outer_margin = 100