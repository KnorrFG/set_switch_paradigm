import pygame

import config as c
from eventlistener import EventListener, EventConsumerInfo
from resources import Resources
from simple_types import *
import draw

import argparse
import time
import json
import random
import statistics
import math
import pathlib


def display(screen, func, *args):
    screen.fill(c.Screen.background)
    func(screen, *args)
    pygame.display.flip()


def on_pulse(event, pulse_log):
    if event.type == pygame.KEYDOWN and event.key == c.Keys.pulse:
        pulse_log.append(time.time())
    return EventConsumerInfo.DONT_CARE


def wait_for_pulse(screen, listener, scanner_mode):
    display(screen, draw.fixcross)
    listener.wait_for_keypress(c.Keys.pulse, 
        c.Scanner.num_pulses_till_start if scanner_mode else 1)
    if not scanner_mode:
        listener.wait_for_seconds(c.Paradigm.seconds_before_start)


def get_inter_block_intervals(n):
    """ takes n IBIs from a uniform dist and ensures the mean 
    error is smaller than what ever is defined in config.py 
    also adds a 0 in the end."""
    is_satisfying = lambda IBIs: abs(
        (statistics.mean(IBIs) - c.Paradigm.ibi_mean)) < \
            c.Paradigm.ibi_mean_error_tollerance

    while True:
        IBIs = tuple(random.uniform(*c.Paradigm.inter_block_interval) 
            for _ in range(n - 1))
        if is_satisfying(IBIs): 
            return IBIs + (0,)


def show_instruction_screen(screen, event_listener):
    display(screen, draw.instruction_text)
    event_listener.wait_for_seconds(c.Paradigm.instruction_duration)


def get_concurency_list():
    """returns a list of booleans which indicate whether trial n is congruent
    or not"""
    concurrency_list = [True] * c.Paradigm.num_congruent_trials \
        + [False] * c.Paradigm.num_incongruent_trials
    random.shuffle(concurrency_list)
    return concurrency_list


def get_stim_1_orientations():
    fac1 = c.Paradigm.trials_per_block // 2
    fac2 = c.Paradigm.trials_per_block - fac1

    if fac1 != fac2 and random.random() > 0.5: 
        (fac1, fac2) = (fac2, fac1)

    orients = [Orientation.LEFT] * fac1 + [Orientation.RIGHT] * fac2
    random.shuffle(orients)
    return orients


def choose_stims(stim_list):
    return [random.choice(stim_list) for _ in range(c.Paradigm.trials_per_block)]


def exec_trials(screen, event_listener, face_list, house_list):
    display_onsets = []
    decisions = []
    decision_onsets = []
    RTs = []
    ITIs = []
    last_iteration = len(face_list) - 1

    for i, (face, house) in enumerate(zip(face_list, house_list)):
        display(screen, draw.stimulus, face, house)
        display_onsets.append(time.time())
        key = event_listener.wait_for_keys_timed_out(c.Keys.answer_keys, 
            c.Paradigm.trial_timeout)

        if key:
            decision_onsets.append(time.time())
            decisions.append(Orientation.LEFT if key == c.Keys.key_left 
                else Orientation.RIGHT)
            RTs.append(decision_onsets[-1] - display_onsets[-1])
            ITI = max(c.Paradigm.min_iti, c.Paradigm.prefered_trial_length - RTs[-1])
        else:
            decision_onsets.append(None)
            decisions.append(None)
            RTs.append(None)
            ITI = c.Paradigm.min_iti

        if i == last_iteration:
            ITI = 0
        else:
            display(screen, draw.fixcross)
            event_listener.wait_for_seconds(ITI)

        ITIs.append(ITI)

    return display_onsets, decisions, decision_onsets, RTs, ITIs


def get_block_target(decisions, face_orientations, house_orientations):
    face_errors = 0; house_errors = 0
    for dec, face_ori, house_ori in zip(decisions, 
            face_orientations, house_orientations):
        if dec != face_ori: face_errors += 1
        if dec != house_ori: house_errors += 1

    if face_errors <= c.Paradigm.allowed_errors_per_block:
        return BlockTarget.FACE
    elif house_errors <= c.Paradigm.allowed_errors_per_block:
        return BlockTarget.HOUSE
    else:
        return BlockTarget.UNCLEAR


def exec_block(screen, event_listener):
    res = Resources()
    start = time.time()
    concurrency_list = get_concurency_list()
    face_orientations = get_stim_1_orientations()
    house_orientations = [ori if cong else ori.inverted()
        for ori, cong in zip(face_orientations, concurrency_list)]
    face_list = choose_stims(res.faces)
    house_list = choose_stims(res.houses)

    show_instruction_screen(screen, event_listener)
    presentation_onsets, decisions, decision_onsets, RTs, ITIs = \
        exec_trials(screen, event_listener, 
            [face[face_ori] for face, face_ori in zip(face_list, face_orientations)],
            [house[house_ori] for house, house_ori in zip(house_list, house_orientations)])
    target = get_block_target(decisions, face_orientations, house_orientations)
    
    return {
        "time": (start, time.time()),
        "target": target.name
    }, {
        "presentations_onset": presentation_onsets,
        "decision_onset": decision_onsets,
        "decision": [ori.name if ori else "None" for ori in decisions],
        "RT": RTs,
        "follwing ITI": ITIs,
        "was_congruent": concurrency_list,
        "face_orientation": [ori.name for ori in face_orientations],
        "house_orientation": [ori.name for ori in house_orientations],
        "face_id": [stim.name for stim in face_list],
        "house_id": [stim.name for stim in house_list]
    }


def exec_run(screen, scanner_mode):
    start = time.time()
    pulses = []
    blocks = []
    add_pulse = lambda ev: on_pulse(ev, pulses)
    event_listener = EventListener((add_pulse,))
    target_counter = {val: 0 for val in BlockTarget}

    inter_block_intervals = get_inter_block_intervals(c.Paradigm.blocks_per_run)
    wait_for_pulse(screen, event_listener, scanner_mode)

    for ibi in inter_block_intervals:
        blocks.append(exec_block(screen, event_listener))
        target_counter[BlockTarget[blocks[-1][0]["target"]]] += 1
        display(screen, draw.feedback, target_counter)
        event_listener.wait_for_seconds(c.Paradigm.feedback_display_time)
        if ibi > 0:
        # the last ibi will be zero, therefore we can skip this
            display(screen, draw.fixcross)
            event_listener.wait_for_seconds(ibi)

    return {
        "pulses": pulses, 
        "block_target_counter": {key.name: val 
            for key, val in target_counter.items()},
        "inter_block_intervals": inter_block_intervals,
        "time": (start, time.time())
    }, blocks


def save(output, output_path: pathlib.Path):
    with output_path.open('w') as file:
        if type(output) == str:
            print(output, file=file)
        else:
            json.dump(output, file)


def to_tsv(table_dict):
    return "\n".join(["\t".join(table_dict.keys())] \
        + ["\t".join(map(str, line)) for line in zip(*table_dict.values())])


def save_results(results, subj):
    output_base = Resources().output_base_path
    containing_dir = output_base / ("sub-" + str(subj)) / "func" 
    containing_dir.mkdir(parents=True)

    for ind_run, (run_info, blocks) in enumerate(results):
        sub_and_run = "sub-{}_run-{:02d}".format(subj, ind_run)
        save(run_info, containing_dir / (sub_and_run + ".json"))
        for ind_block, (block_info, trial_table) in enumerate(blocks):
            sub_run_and_block = sub_and_run + "_block-{:02d}".format(ind_block)
            save(block_info, containing_dir / (sub_run_and_block + ".json"))
            save(to_tsv(trial_table), containing_dir / (sub_run_and_block + ".tsv"))


def set_screen_infos(screen):
    sr = screen.get_rect()
    c.Screen.resolution = (sr.width, sr.height)
    c.Screen.center = (sr.width/2, sr.height/2)


def castable(obj, target_type):
    try:
        _ = target_type(obj)
        return True
    except:
        return False

def subj_id_valid(subj):
    return type(subj) == str\
        and len(subj) == 8\
        and castable(subj, int)


def query_subj_id():
    res = Resources()
    while True:
        subj = input("Enter subject ID: ")
        if subj_id_valid(subj):
            if (res.output_base_path / ("sub-" + subj)).exists():
                print("This subject ID was already used")
            else:
                return subj
        else:
            print("Invalid ID (must have length 8, and be a number)")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scanner-mode", "-f", action="store_true")
    args = parser.parse_args()

    subj = query_subj_id()

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(c.Screen.resolution, pygame.NOFRAME)
    set_screen_infos(screen)
    Resources().load_all()
    event_listener = EventListener()

    display(screen, draw.session_instruction)
    event_listener.wait_for_keypress(pygame.K_RETURN)

    run_results = []
    for _ in range(c.Paradigm.num_runs):
        run_results.append(exec_run(screen, args.scanner_mode))
        display(screen, draw.run_over)
        event_listener.wait_for_keypress(pygame.K_RETURN)

    save_results(run_results, subj)
    pygame.quit()

if __name__ == '__main__':
    main()