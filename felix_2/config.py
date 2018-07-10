import pygame

class Scanner(object):
    num_pulses_till_start = 10


class Screen(object):
    resolution = (1024, 800)
    center = None
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
    seconds_before_start = 2

    num_runs = 1

    blocks_per_run = 3
    inter_block_interval = (3, 3)
    ibi_mean = (inter_block_interval[0] + inter_block_interval[1]) / 2
    ibi_mean_error_tollerance = 0.05 * ibi_mean

    trials_per_block = 3
    instruction_duration = 2
    allowed_errors_per_block = 0
    feedback_display_time = 2

    percent_congruent_trials = 0.5
    num_congruent_trials = int(trials_per_block * percent_congruent_trials)
    num_incongruent_trials = trials_per_block - num_congruent_trials

    trial_timeout = 2.5
    prefered_trial_length = 1
    min_iti = 0.2


class Text(object):
    block_instruction = "Wähle eine Kategorie"
    session_instruction = [line.strip() for line in """
        Während des Experiments werden immer gleichzeitig Zeichnungen
        eines Gesichts und eines Hauses gezeigt, die in einem 45° Winkel 
        nach links oder rechts geneigt sind. 
        Sie müssen dann die Neigungsrichtung von einer der beiden Zeichnungen angeben. 
        Das Experiment ist in Blöcke aufgeteilt und in einem Block werden
        {} Paare gezeigt

        Vor jedem Block wird der Text "{}" angezeigt
        Dann müssen Sie sich enweder für eine Kategorie (Gesicht oder Haus) entscheiden.
        Sie haben die freie Wahl, und dürfen sich für jeden Block neu entscheiden.
        Immer wenn während eines Blocks ein Paar angezeigt wird, ist es Ihre 
        Aufgabe die Pfeiltasten (Links/Rechts) zu nutzen, um die Richtung anzuzeigen,
        in die die Zeichnung, die Ihrer gewählten Kategorie entspricht, geneigt ist. 
        
        Drücken Sie Enter zum fortfahren."""
            .format(Paradigm.trials_per_block, block_instruction)
            .split("\n")]
    
    run_over_text = "Der Run ist vorrüber, ENTER drücken um fortzufahren."
    instruction_example = [line.strip() for line in """
        Haben sie sich für "Gesicht" entschieden, würden sie hier die linke 
        Pfeiltaste drücken. Im Fall "Haus" die Rechte.

        Wenn Sie Fragen haben, wenden Sie sich bitte an den/die 
        Versuchsleiter(in), ansonsten drücken sie Enter um fortzufahren"""
            .split("\n")]

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
    scale = 0.4 #stimsize = screensize * scale


class Feedback(object):
    inner_margin = 10
    outer_margin = 100