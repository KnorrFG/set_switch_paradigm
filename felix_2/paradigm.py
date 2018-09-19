import argparse
import json
import os
import pathlib
import random
import statistics
import sys
import time
from configparser import ConfigParser
from enum import Enum
from operator import eq

import pygame
from toolz import compose, curry, partial, pipe
from toolz.curried import map, take

import config as c
import render
import resources as res
from pyparadigm.eventlistener import *
from pyparadigm.misc import *


# =====================================================================
# Types
# =====================================================================
class BlockTarget(Enum):
    FACE = 1
    HOUSE = 2
    UNCLEAR = 3


# =====================================================================
# Helpers
# =====================================================================
key_by_orientation = lambda orientation: c.Keys.key_left \
        if orientation == res.Orientation.LEFT else c.Keys.key_right

clamp = lambda diff, max_diff: max(-max_diff, min(max_diff, diff))
flip_if = lambda cond, two_tuple: (two_tuple[1], two_tuple[0]) if cond else two_tuple
lmap = compose(list, map)

def random_elem(pool):
    while True:
        yield random.choice(pool)

    
def until_n_correct(n, func):      
    counter = 0
    while counter < n:
        if func(): counter += 1
        else: counter = 0

# =====================================================================
# Main-Script
# =====================================================================
def pygame_init(display_position):
    os.environ['SDL_VIDEO_WINDOW_POS'] = display_position
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(c.Screen.resolution, pygame.NOFRAME)
    sr = screen.get_rect()
    c.Screen.resolution = (sr.width, sr.height)
    c.Screen.center = (sr.width/2, sr.height/2)
    return screen


def query_subj_id(output_base_path):
    while True:
        subj = input("Enter subject ID: ")
        if len(subj) == 8 and subj.isdigit():
            return subj
        else:
            print("Invalid ID (must have length 8, and be a number)")


@curry
def on_pulse(pulse_log, event):
    if event.type == pygame.KEYDOWN and event.key == c.Keys.pulse:
        pulse_log.append(time.time())
    return EventConsumerInfo.DONT_CARE


def do_train_stimulus(event_listener, face, house, 
                      face_orientation, house_orientation, target):
    event_listener.listen()
    render.stimulus(face[face_orientation], house[house_orientation])
    start = time.time()
    orientation_by_target = lambda target: \
        face_orientation if target == BlockTarget.FACE else house_orientation
    matches_mapping = lambda key: key == key_by_orientation(orientation_by_target(target))
    key = event_listener.wait_for_keys(c.Keys.answer_keys, 
            c.Paradigm.trial_timeout)
    RT = time.time() - start
    render.fixcross()
    event_listener.wait_for_seconds(max((
        c.Paradigm.prefered_trial_length - RT,
        c.Paradigm.min_iti)))
    return key and matches_mapping(key)
    

def do_train_block(event_listener, target):
    assert target != BlockTarget.UNCLEAR
    orientations = random_elem(tuple(res.Orientation))
    faces = random_elem(res.faces())
    houses = random_elem(res.houses())
    func = lambda: do_train_stimulus(event_listener, 
        next(faces), next(houses), 
        next(orientations), next(orientations), target)
    until_n_correct(c.Training.required_corrects, func)


def do_training(event_listener):
    render.multi_page_text(event_listener, [c.Text.train_run_instruction_faces])
    do_train_block(event_listener, BlockTarget.FACE)
    render.multi_page_text(event_listener, [c.Text.train_run_instruction_houses])
    do_train_block(event_listener, BlockTarget.HOUSE)
    render.multi_page_text(event_listener, [c.Text.train_run_end_text])


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


def get_stim_1_orientations():
    fac1 = c.Paradigm.trials_per_block // 2
    fac2 = c.Paradigm.trials_per_block - fac1

    if fac1 != fac2 and random.random() > 0.5: 
        (fac1, fac2) = (fac2, fac1)

    orients = [res.Orientation.LEFT] * fac1 + [res.Orientation.RIGHT] * fac2
    random.shuffle(orients)
    return orients


def do_trials(event_listener, face_list, house_list):
    display_onsets = []
    decisions = []
    decision_onsets = []
    RTs = []
    ITIs = []
    last_iteration = len(face_list) - 1

    for i, (face, house) in enumerate(zip(face_list, house_list)):
        #to empty the q
        event_listener.listen()
        render.stimulus(face, house)
        display_onsets.append(time.time())
        key = event_listener.wait_for_keys(c.Keys.answer_keys, 
            c.Paradigm.trial_timeout)

        if key:
            decision_onsets.append(time.time())
            decisions.append(res.Orientation.LEFT if key == c.Keys.key_left 
                else res.Orientation.RIGHT)
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
            render.fixcross()
            event_listener.wait_for_seconds(ITI)

        ITIs.append(ITI)

    return display_onsets, decisions, decision_onsets, RTs, ITIs


def get_block_target(decisions, face_orientations, house_orientations):
    face_errors = 0; house_errors = 0
    for dec, face_ori, house_ori in zip(decisions, 
            face_orientations, house_orientations):
        if face_ori != house_ori:
            if dec != face_ori: face_errors += 1
            if dec != house_ori: house_errors += 1

    if face_errors <= c.Paradigm.allowed_errors_per_block:
        return BlockTarget.FACE
    elif house_errors <= c.Paradigm.allowed_errors_per_block:
        return BlockTarget.HOUSE
    else:
        return BlockTarget.UNCLEAR


def get_concurency_list():
    """returns a list of booleans which indicate whether trial n is congruent
    or not"""
    concurrency_list = [True] * c.Paradigm.num_congruent_trials \
        + [False] * c.Paradigm.num_incongruent_trials
    random.shuffle(concurrency_list)
    return concurrency_list


def do_block(event_listener):
    start = time.time()
    concurrency_list = get_concurency_list()
    face_orientations = get_stim_1_orientations()
    house_orientations = [ori if cong else ori.inverted()
        for ori, cong in zip(face_orientations, concurrency_list)]
    face_list = [random.choice(res.faces()) for _ in range(c.Paradigm.trials_per_block)]
    house_list = [random.choice(res.houses()) for _ in range(c.Paradigm.trials_per_block)]

    display(render.text_page(c.Text.block_instruction))
    event_listener.wait_for_seconds(c.Paradigm.instruction_duration)
    presentation_onsets, decisions, decision_onsets, RTs, ITIs = \
        do_trials(event_listener, 
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
        "following_ITI": ITIs,
        "was_congruent": concurrency_list,
        "face_orientation": [ori.name for ori in face_orientations],
        "house_orientation": [ori.name for ori in house_orientations],
        "face_id": [stim.name for stim in face_list],
        "house_id": [stim.name for stim in house_list]
    }

def do_run(event_listener):
    start = time.time()
    blocks = []
    target_counter = {val: 0 for val in BlockTarget}
    inter_block_intervals = get_inter_block_intervals(c.Paradigm.blocks_per_run)
    display(render.fixcross())
    event_listener.wait_for_n_keypresses(c.Keys.pulse, c.Scanner.num_pulses_till_start)

    for ibi in inter_block_intervals:
        blocks.append(do_block(event_listener))
        target_counter[BlockTarget[blocks[-1][0]["target"]]] += 1
        display(render.feedback(clamp(target_counter[BlockTarget.HOUSE] 
                                - target_counter[BlockTarget.FACE], c.Feedback.max_diff)))
        event_listener.wait_for_seconds(c.Paradigm.feedback_display_time)
        if ibi > 0:
        # the last ibi will be zero, therefore we can skip this
            display(render.fixcross())
            event_listener.wait_for_seconds(ibi)

    return {
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


def get_ses_dir(subj_dir):
    if not subj_dir.exists():
        return "ses-1"
    else:
        return "ses-" + str(len(tuple(subj_dir.glob("ses-*"))) + 1)


def save_results(results, subj, ses, pulses, localizer_results, output_base):
    subj_dir = output_base / ("sub-" + str(subj))
    ses_dir = f"ses-{ses}"
    containing_dir = subj_dir/ ses_dir / "func"
    containing_dir.mkdir(parents=True)

    #save pulses
    save(pulses, containing_dir/ f"sub-{subj}_{ses_dir}_pulses.json")
    #save localizer_results
    def save_loc_blocks(blocks, name):
        for i, block in enumerate(blocks):
            file_name = f"sub-{subj}_localizer-{name}_block-{i}"
            save(block[0], containing_dir / f"{file_name}.json")
            save(to_tsv(block[1]), containing_dir / f"{file_name}.tsv")

    if localizer_results:
        save_loc_blocks(localizer_results[0], "face")
        save_loc_blocks(localizer_results[1], "house")
    #save rest
    for ind_run, (run_info, blocks) in enumerate(results):
        sub_and_run = "sub-{}_{}_run-{:02d}".format(subj, ses_dir, ind_run)
        save(run_info, containing_dir / (sub_and_run + ".json"))
        for ind_block, (block_info, trial_table) in enumerate(blocks):
            sub_run_and_block = sub_and_run + "_block-{:02d}".format(ind_block)
            save(block_info, containing_dir / (sub_run_and_block + ".json"))
            save(to_tsv(trial_table), containing_dir / (sub_run_and_block + ".tsv"))
            

def query_session(output_base, subj):
    while True:
        ses = input("Enter Session number: ")
        if ses in ["1", "2"]:
            if (output_base / f"sub-{subj}" / f"ses-{ses}").exists():
                print("Session folder exists already")
            else:
                return ses
        else:
            print("Session Id must be 1 or 2")


def do_localizer_block(event_listener, target):
    start = time.time()
    target_is_face = target == BlockTarget.FACE
    stim_orientations = get_stim_1_orientations()
    source = res.faces() if target_is_face else res.houses()
    stim_list = pipe(random_elem(source), 
                     take(len(stim_orientations)), 
                     list)
    face_list, house_list = flip_if(not target_is_face, (
                                        lmap(lambda ori, stim: stim[ori], 
                                            stim_orientations,
                                            stim_list), 
                                        [None] * len(stim_list))) 
    display_onsets, decisions, decision_onsets, RTs, ITIs = \
        do_trials(event_listener, face_list, house_list)
    return {
        "time": (start, time.time()),
        "target": target.name
    }, {
        "presentations_onset": display_onsets,
        "decision_onset": decision_onsets,
        "decision": [ori.name if ori else "None" for ori in decisions],
        "RT": RTs,
        "following_ITI": ITIs,
        "stim_orientation": [ori.name for ori in stim_orientations],
        "stim_id": [stim.name for stim in stim_list]
    }


def do_localizer(event_listener):
    render.multi_page_text(event_listener, c.Text.Localizer.intro)
    display(render.fixcross())
    event_listener.wait_for_n_keypresses(c.Keys.pulse, c.Scanner.num_pulses_till_start)
    face_results = []
    house_results = []
    ibis = get_inter_block_intervals(2 * c.Paradigm.localizer_blocks_per_target)

    for i in range(c.Paradigm.localizer_blocks_per_target):
        face_results.append(do_localizer_block(event_listener, BlockTarget.FACE))
        display(render.fixcross())
        event_listener.wait_for_seconds(ibis[2 * i])
        house_results.append(do_localizer_block(event_listener, BlockTarget.HOUSE))
        display(render.fixcross())
        event_listener.wait_for_seconds(ibis[2 * i + 1])
    
    display(render.text_page(c.Text.Localizer.end))
    event_listener.wait_for_seconds(2)
    return face_results, house_results


def init_keys(ini):
    c.Keys.key_left = getattr(pygame, ini["Keys"]["left"])
    c.Keys.key_right = getattr(pygame, ini["Keys"]["right"])
    c.Keys.next_page = getattr(pygame, ini["Keys"]["enter"])
    c.Keys.answer_keys = (c.Keys.key_left, c.Keys.key_right)


def main():
    conf_ini = ConfigParser()
    conf_ini.read("config.ini")
    out_path = pathlib.Path(conf_ini["Path"]["output_base"])
    init_keys(conf_ini)
    subj = "00000000" if len(sys.argv) > 1 else query_subj_id(
        out_path)
    ses = "1" if len(sys.argv) > 1 else query_session(
        out_path, subj)
    pygame_init(conf_ini["Display"]["position"])
    scanner_pulses = []
    event_listener = EventListener((on_pulse(scanner_pulses),))
    bool_from_conf = lambda name: conf_ini["Options"].getboolean(name)
    localizer_results = None

    if bool_from_conf("do_localizer"): 
        localizer_results = do_localizer(event_listener)
    if bool_from_conf("display_instruction"): 
        render.multi_page_text(event_listener, c.Text.session_instruction)
    if bool_from_conf("do_train_run"):
        do_training(event_listener)

    run_results = []
    for i in range(c.Paradigm.num_runs):
        run_results.append(do_run(event_listener))
        if i == c.Paradigm.num_runs - 1:
            save_results(run_results, subj, ses, scanner_pulses, localizer_results, out_path)
            display(render.text_page(c.Text.experiment_over))
            event_listener.wait_for_n_keypresses(c.Keys.next_page)
        else:
            display(render.text_page(c.Text.run_over_text))
            event_listener.wait_for_n_keypresses(c.Keys.next_page)

    pygame.quit()
    

if __name__ == '__main__':
    main()
