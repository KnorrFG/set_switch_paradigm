import pygame

from resources import Resources
from simple_types import *
import config as c


def _get_top_left_to_center_on(surface, coords):
    rect = surface.get_rect()
    return (
        coords[0] - rect.width / 2,
        coords[1] - rect.height / 2
    )


def fixcross(surface):
    half_len = c.Fixcross.length // 2
    center = c.Screen.center
    pygame.draw.line(surface, c.Fixcross.color, 
        (center[0] - half_len, center[1]),
        (center[0] + half_len, center[1]), 
        c.Fixcross.width)
    pygame.draw.line(surface, c.Fixcross.color, 
        (center[0], center[1] - half_len),
        (center[0], center[1] + half_len),
        c.Fixcross.width)


def instruction_text(screen):
    text = Resources().instruction_text
    screen.blit(text, _get_top_left_to_center_on(text, c.Screen.center))


def stimulus(screen, face, house, face_ori, house_ori):
    screen.blit(face[face_ori], c.Stimuli.plot_coord)
    screen.blit(house[house_ori], c.Stimuli.plot_coord)


def _text_number_combo(res, name, val):
    number = res.font.render(str(val), False, c.Text.text_color)
    string = res.font.render(name, False, c.Text.text_color)
    bg_size = (
        max(number.get_rect().width, string.get_rect().width),
        number.get_rect().height + string.get_rect().height 
            + c.Feedback.inner_margin
    )
    bg = pygame.Surface(bg_size)
    h_center = bg_size[0] / 2
    bg.fill(c.Screen.background)
    bg.blit(string, (0, 0))
    bg.blit(number, (h_center - number.get_rect().width/2, 
        string.get_rect().height + c.Feedback.inner_margin))
    return bg
    

def feedback(screen, target_counter):
    res = Resources()
    house_counter = _text_number_combo(res, "House", target_counter[BlockTarget.HOUSE])
    face_counter = _text_number_combo(res, "Face", target_counter[BlockTarget.FACE])
    horizontal_offset = (c.Feedback.outer_margin + house_counter.get_rect().width) / 2
    house_center = (c.Screen.center[0] - horizontal_offset, c.Screen.center[1])
    face_center = (c.Screen.center[0] + horizontal_offset, c.Screen.center[1])
    screen.blit(house_counter, _get_top_left_to_center_on(house_counter, house_center))
    screen.blit(face_counter, _get_top_left_to_center_on(face_counter, face_center))


def run_over(screen):
    res = Resources()
    run_over_text = res.font.render("The run is over, press Return to continue",
        False, c.Text.text_color)
    screen.blit(run_over_text, _get_top_left_to_center_on(run_over_text, c.Screen.center))