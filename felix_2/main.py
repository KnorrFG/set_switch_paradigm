import pygame

import config as c
from eventlistener import EventListener, EventConsumerInfo
from resources import Resources
from simple_types import Orientation
import draw

import argparse
import time
import pickle
import random
import statistics
import math


def display(screen, func, *args):
    screen.fill(c.Screen.background)
    func(screen, *args)
    pygame.display.flip()


def get_top_left_to_center_on(surface, coords):
    rect = surface.get_rect()
    return (
        coords[0] - rect.width / 2,
        coords[1] - rect.height / 2
    )


def on_pulse(event, pulse_log):
    if event.type == pygame.KEYDOWN and event.key == c.Keys.pulse:
        pulse_log.append(time.time())
    return EventConsumerInfo.DONT_CARE


def wait_for_pulse(screen, listener, scanner_mode):
    display(screen, draw.fixcross)
    listener.wait_for_keypress(c.Keys.pulse, 
        c.Scanner.num_pulses_till_start if scanner_mode else 1)


def get_inter_block_intervals(n):
    """ takes n IBIs from a uniform dist and ensures the mean 
    error is smaller than what ever is defined in config.py 
    also adds a 0 in the end."""
    is_satisfying = lambda IBIs: abs(
        (statistics.mean(IBIs) - c.Paradigm.ibi_mean)) < \
            c.Paradigm.ibi_mean_error_tollerance

    while True:
        IBIs = tuple(random.uniform(*c.Paradigm.inter_block_interval) 
            for _ in range(n))
        if is_satisfying(IBIs): 
            return IBIs + (0,)


def draw_instruction_text(screen):
    text = Resources().instruction_text
    screen.blit(text, get_top_left_to_center_on(text, c.Screen.center))


def show_instruction_screen(screen, event_listener):
    display(screen, draw_instruction_text)
    event_listener.wait_for_seconds(c.Paradigm.instruction_duration)


def exec_trial(screen, event_listener):
    pass


def get_concurency_list():
    """returns a list of booleans which indicate whether trial n is congruent
    or not"""
    concurrency_list = [True] * c.Paradigm.num_congruent_trials \
        + [False] * c.Paradigm.num_incongruent_trials
    random.shuffle(concurrency_list)
    return concurrency_list


def get_stim_1_orientations():
    tbp = c.Paradigm.trials_per_block
    fac1 = tbp // 2
    if tbp % 2 == 0:
        fac2 = fac1
    else:
        fac2 = tbp - fac1
        if random.random() > 0.5: 
            (fac1, fac2) = (fac2, fac1)

    orients = [Orientation.LEFT] * fac1 + [Orientation.RIGHT] * fac2
    random.shuffle(orients)
    return orients


def exec_block(screen, event_listener):
    start = time.time()
    concurrency_list = get_concurency_list()
    stim_1_orientations = get_stim_1_orientations()
    stim_2_orientations = [ori if cong else ori.inverted()
        for ori, cong in zip(stim_1_orientations, concurrency_list)]

    show_instruction_screen(screen, event_listener)
    trials = [exec_trial(screen, event_listener) 
        for _ in range(c.Paradigm.trials_per_block)]
    return {
        "trials": trials,
        "time": (start, time.time())
    }


def exec_run(screen, scanner_mode):
    start = time.time()
    pulses = []
    blocks = []
    add_pulse = lambda ev: on_pulse(ev, pulses)
    event_listener = EventListener((add_pulse,))

    inter_block_intervals = get_inter_block_intervals(c.Paradigm.blocks_per_run)
    wait_for_pulse(screen, event_listener, scanner_mode)

    for ibi in inter_block_intervals:
        blocks.append(exec_block(screen, event_listener))

        if ibi > 0:
        # the last ibi will be zero, therefore we can skip this
            display(screen, draw.fixcross)
            event_listener.wait_for_seconds(ibi)

    return {
        "pulses": pulses, 
        "blocks": block,
        "inter_block_intervals": inter_block_intervals,
        "time": (start, time.time())
    }


def save_results(results, savepath):
    with open(savepath, 'wb') as file:
        pickle.dump(results, file)


def load_resources():
    return {}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-runs", "-n", type=int, default="1")
    parser.add_argument("--output", "-o", default="results.pkl")
    parser.add_argument("--scanner-mode", "-s", action="store_true")
    args = parser.parse_args()

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(c.Screen.resolution, pygame.NOFRAME)
    Resources().load_all()
    run_results = [exec_run(screen, args.scanner_mode) for _ in range(args.num_runs)]
    save_results(run_results, args.output)
    pygame.quit()

if __name__ == '__main__':
    main()