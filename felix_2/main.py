import pygame

import config as c
from eventlistener import EventListener, EventConsumerInfo
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


def on_pulse(event, pulse_log):
    if event.type == pygame.KEYDOWN and event.key == c.Keys.pulse:
        pulse_log.append(time.time())
    return EventConsumerInfo.DONT_CARE


def wait_for_pulse(screen, listener):
    display(screen, draw.fixcross)
    listener.wait_for_keypress(c.Keys.pulse)


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
        if is_satisfying(IBIs): return IBIs + (0,)


def exec_block(screen, event_listener, resources):
    pass

def exec_run(screen, resources):
    start = time.time()
    pulses = []
    blocks = []
    add_pulse = lambda ev: on_pulse(ev, pulses)
    event_listener = EventListener((add_pulse,))
    inter_block_intervals = get_inter_block_intervals(c.Paradigm.blocks_per_run)
    wait_for_pulse(screen, event_listener)

    for ibi in inter_block_intervals:
        blocks.append(exec_block(screen, event_listener, resources))

        if ibi > 0:
        # the last ibi will be zero, therefore we can skip this
            display(screen, draw.fixcross)
            event_listener.wait_for_seconds(ibi)

    return {
        "pulses": pulses, 
        "blocks": block,
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
    args = parser.parse_args()

    pygame.init()
    screen = pygame.display.set_mode(c.Screen.resolution, pygame.NOFRAME)
    resources = load_resources()
    run_results = [exec_run(screen, resources) for _ in range(args.num_runs)]
    save_results(run_results, args.output)
    pygame.quit()

if __name__ == '__main__':
    main()