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

    num_runs = 5

    blocks_per_run = 16
    inter_block_interval = (11, 3)
    ibi_mean = (inter_block_interval[0] + inter_block_interval[1]) / 2
    ibi_mean_error_tollerance = 0.05 * ibi_mean

    trials_per_block = 18
    instruction_duration = 2
    allowed_errors_per_block = 1
    feedback_display_time = 2

    percent_congruent_trials = 0.5
    num_congruent_trials = int(trials_per_block * percent_congruent_trials)
    num_incongruent_trials = trials_per_block - num_congruent_trials

    trial_timeout = 2.5
    prefered_trial_length = 0.825
    min_iti = 0.2


class Training:
    required_corrects = 5


class Text(object):
    block_instruction = "Wähle eine Kategorie"
    session_instruction = [
        """ Es wird Ihnen nun das Experiment erklärt. Wenn sie Alles gelesen haben,
        drücken sie Enter um zur nächsten Seite zu gelangen.
        
        Drücken sie jetzt Enter""", 

        """Während des Experiments werden immer gleichzeitig Zeichnungen
        eines Gesichts und eines Hauses gezeigt, die in einem 45° Winkel 
        nach links oder rechts geneigt sind.""",

        """ Sie müssen dann die Neigungsrichtung von einer der beiden Zeichnungen 
        angeben.""",

        """Das Experiment ist in Blöcke aufgeteilt und in einem Block werden
        {} Paare gezeigt""".format(Paradigm.trials_per_block),

        """Vor jedem Block wird der Text "{}" angezeigt
        Dann müssen Sie sich enweder für eine Kategorie (Gesicht oder Haus) 
        entscheiden.""".format(block_instruction),

        "Sie haben die freie Wahl, und dürfen sich für jeden Block neu entscheiden.",
        
        """Immer wenn während eines Blocks ein Paar angezeigt wird, ist es Ihre 
        Aufgabe die Pfeiltasten (Links/Rechts) zu nutzen, um die Richtung anzuzeigen,
        in die die Zeichnung, die Ihrer gewählten Kategorie entspricht, geneigt
        ist."""]
    
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

    train_run_instruction_faces = \
        """Es beginnt nun ein Testdurchlauf. Handeln sie so, wie sie es tun
        würden, wenn sie sich für "Gesicht" entscheiden.

        Drücken sie Enter um fortzufahren.
        """
    
    train_run_instruction_houses = \
        """Danke.

        Bitte handeln sie nun so, als hätten sie sich für "Haus" entschieden.

        Drücken sie Enter um fortzufahren."""

    train_run_end_text = \
        """Vielen Dank.

        Wir beginnen nun mit dem Experiment, 
        bitte drücken sie Enter um fortzufahren"""


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
    percentual_display_width = 0.5
    green_abs_diff = 1
    yellow_abs_diff = 4
    