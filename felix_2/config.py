import pygame

class Scanner(object):
    num_pulses_till_start = 10


class Screen(object):
    resolution = (0, 0)
    center = None
    background = 0xFFFFFF


class Fixcross(object):
    color = pygame.Color(0, 0, 0)
    length = 100
    factor = 0.1
    width = 10


class Keys(object):
    pulse = pygame.K_t
    key_left = pygame.K_LEFT
    key_right = pygame.K_RIGHT
    answer_keys = (key_left, key_right)


class Paradigm(object):
    seconds_before_start = 2

    num_runs = 2

    blocks_per_run = 16
    inter_block_interval = (12, 18)
    ibi_mean = (inter_block_interval[0] + inter_block_interval[1]) / 2
    ibi_mean_error_tollerance = 0.05 * ibi_mean

    trials_per_block = 18
    instruction_duration = 2
    allowed_errors_per_block = 2
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
        drücken sie 'Enter' um zur nächsten Seite zu gelangen.
        
        Drücken sie jetzt 'Enter'.""", 

        """Während des Experiments werden immer gleichzeitig Zeichnungen
        eines Gesichts und eines Hauses gezeigt, die in einem 45° Winkel 
        nach links oder rechts geneigt sind.""",

        """ Sie müssen dann die Neigungsrichtung von einer der beiden Zeichnungen 
        angeben.""",

        """Das Experiment ist in Blöcke aufgeteilt, und in einem Block werden
        {} Paare gezeigt""".format(Paradigm.trials_per_block),

        """Vor jedem Block wird der Text '{}' angezeigt
        Dann müssen Sie sich entweder für 'Gesichter' oder 'Häuser'
        entscheiden.""".format(block_instruction),

        "Sie haben die freie Wahl und dürfen sich für jeden Block neu entscheiden.",
        
        """Allerdings ist es für uns wichtig, dass ihre Entscheidungen ausgewogen 
        sind. Deshalb wird ihnen nach jedem Block eine Skala angezeigt, an der
        Sie ablesen können, ob sie sich bisher öfter für 'Gesichter' oder
        Häuser' entschieden haben und wie stark das Ungleichgewicht ist.""",

        """Bitte versuchen sie, den gelben Bereich nicht zu verlassen 
        und den Block im grünen Bereich zu beenden.""",

        """Immer wenn während eines Blocks ein Paar angezeigt wird, ist es Ihre 
        Aufgabe die linke oder rechte äußere Taste (mit dem jeweiligen
        Zeigefinger) zu nutzen, um die Richtung anzuzeigen, in die die
        Zeichnung, die Ihrer gewählten Kategorie entspricht, geneigt ist.""" ]
    
    run_over_text = "Der Run ist vorrüber, 'ENTER' drücken um fortzufahren."
    instruction_example = [line.strip() for line in """
        Haben sie sich für 'Gesichter' entschieden, würden sie hier die linke 
        Pfeiltaste drücken. Im Fall 'Häuser' die rechte.

        Wenn Sie Fragen haben, wenden Sie sich bitte an den/die 
        Versuchsleiter(in), ansonsten drücken sie 'Enter' um fortzufahren."""
            .split("\n")]

    font = "Arial"
    font_size = 30
    text_color = pygame.Color(0, 0, 0)

    train_run_instruction_faces = \
        """Es beginnt nun ein Testdurchlauf. 
        
        Handeln sie so, als hätten Sie sich für 'Gesichter' entschieden.

        Drücken sie 'Enter' um fortzufahren.
        """
    
    train_run_instruction_houses = \
        """Danke.

        Bitte handeln sie nun so, als hätten sie sich für 'Häuser' entschieden.

        Drücken sie 'Enter' um fortzufahren."""

    train_run_end_text = \
        """Vielen Dank.

        Wir beginnen nun mit dem Experiment. 
        Bitte drücken Sie 'Enter' um fortzufahren."""

    class Localizer:
        intro = [
            """Vielen Dank, dass sie an diesem Experiment teilnehmen.
            Drücken sie während ihnen Text angezeigt wird, 'Enter' zum
            fortfahren.
            
            Drücken sie jetzt 'Enter'""",

            """Bevor wir zur eigentlich Aufgabe kommen müssen wir die für uns 
            entscheidenden Regionen in ihrem Gehrin lokalisieren. Dafür 
            werden ihnen zunächst Zeichnungen von Gesichtern präsentiert, die
            entweder nach links oder rechts geneigt sind.""",
            
            """Drücken sie bitte auf dem Gamepad mit dem linken Zeigefinger 
            die linke äußere Taste, wenn die Zeichnung nach links geneigt ist, und 
            mit dem rechten Zeigefinger die rechte äußere Taste, 
            wenn die Zeichnung nach rechts geneigt ist.""",

            f"""Nachdem ihnen {Paradigm.trials_per_block} Gesichter gezeigt wurden
            wird das ganze nochmal mit Zeichnungen von Häusern wiederholt""",

            "Drücken sie 'Enter' um zu beginnen"
        ]

        post_first_block = "Vielen Dank, wir beginnen nun mit den Häusern"
        end = "Vielen Dank, wir beginnen nur mit dem Experiment"



class Stimuli(object):
    color_key = pygame.Color(255, 255, 255)
    house_prefix = "h"
    face_prefix = "f"
    path = "img"
    background = pygame.Color(255, 255, 255)
    width = 311
    height = 233
    scale = 0.35 #stimsize = screensize * scale


class Feedback(object):
    cell_height_percent = 0.05
    percentual_display_width = 0.75
    green_abs_diff = 2
    yellow_abs_diff = 4
    green_prop = 4
    yellow_prop = 2
    max_diff = green_prop + yellow_prop // 2

    text_margin = 10
    indicator_color = 0x000000
    indicator_thickness = 2

    color_table = {
        "G": 0x00FF00,
        "Y": 0xFFD700,
        "R": 0xFF00000
    }

    num_cells = (yellow_abs_diff + 1) * 2 + 1
    cell_width_percent = percentual_display_width / num_cells
