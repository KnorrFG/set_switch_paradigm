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


def _center(x):
    if type(x) in [tuple, list]:
        if len(x) == 2:
            return (x[0] // 2, x[1] // 2)
        if len(x) == 4:
            return (x[3] // 2, x[4] // 2)
    elif type(x) == pygame.Rect:
        return (x.width // 2, x.height // 2)
    elif type(x) == pygame.Surface:
        return _center(x.get_rect())
    else:
        raise ValueError()


def _blit_to_center(src, target):
    target.blit(src, _get_top_left_to_center_on(src, _center(target)))

def _scale_to_target(source, target, smooth=False):
    """target can be a shape tuple or a Surface.
    In the first case a new surface is created, in the second 
    its painted upon, and the returned ref is a ref to target"""
    if type(target) in [tuple, list]:
        target = pygame.Surface(target)

    sr = source.get_rect(); tr = target.get_rect()
    src_factor = min(tr[2 + dim] / sr[2 + dim] for dim in range(2))
    scaled_size = (int(sr.width * src_factor), int(sr.height * src_factor))
    scaled_inner_frame = pygame.transform.scale(source, scaled_size) \
        if not smooth else pygame.transform.smoothscale(source, scaled_size) 
    
    target.fill(c.Screen.background)
    _blit_to_center(scaled_inner_frame, target)
    return target


def _render_text(surface, text):
    size = (max(line.get_rect().width for line in text),
        sum(line.get_rect().height for line in text))
    bg = pygame.Surface(size)
    bg.fill(c.Screen.background)

    get_x = lambda line: (size[0] - line.get_rect().width) * 0.5

    y = 0
    for line in text:
        bg.blit(line, (get_x(line), y))
        y += line.get_rect().height

    sr = surface.get_rect()
    if size[0] > sr.width or size[1] > sr.height:
        _scale_to_target(bg, surface, True)
    else:
        _blit_to_center(bg, surface)


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


def example_screen(screen):
    res = Resources()
    sr = screen.get_rect()
    stim = pygame.Surface(res.stim_background.get_rect().size)
    text = pygame.Surface((sr.width, int(sr.height * 0.33)))
    stimulus(stim, res.faces[0][Orientation.LEFT], res.houses[0][Orientation.RIGHT])
    text.fill(c.Screen.background)
    _render_text(text, res.instruction_example_text)

    x = sr.width / 2
    target_center_stim = (x , int(0.33 * sr.height))
    target_center_text = (x, int(0.67 * sr.height))

    screen.blit(stim, _get_top_left_to_center_on(stim, target_center_stim))
    screen.blit(text, _get_top_left_to_center_on(text, target_center_text))


def session_instruction(screen):
    _render_text(screen, Resources().session_instruction)


def stimulus(screen, face, house):
    res = Resources()
    small_shape = (max(face.get_rect().width, house.get_rect().width),
        max(face.get_rect().height, house.get_rect().height))
    small_shape_center = tuple(x/2 for x in small_shape)

    small_stim_bg = pygame.Surface(small_shape)
    small_stim_bg.fill(c.Screen.background)
    small_stim_bg.blit(face, _get_top_left_to_center_on(face, small_shape_center))
    small_stim_bg.blit(house, _get_top_left_to_center_on(house, small_shape_center))

    big_stim = _scale_to_target(small_stim_bg, res.stim_background)

    sr = screen.get_rect()
    _blit_to_center(big_stim, screen)


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
    house_counter = _text_number_combo(res, "Haus", target_counter[BlockTarget.HOUSE])
    face_counter = _text_number_combo(res, "Gesicht", target_counter[BlockTarget.FACE])
    horizontal_offset = (c.Feedback.outer_margin + house_counter.get_rect().width) / 2
    house_center = (c.Screen.center[0] - horizontal_offset, c.Screen.center[1])
    face_center = (c.Screen.center[0] + horizontal_offset, c.Screen.center[1])
    screen.blit(house_counter, _get_top_left_to_center_on(house_counter, house_center))
    screen.blit(face_counter, _get_top_left_to_center_on(face_counter, face_center))


def run_over(screen):
    res = Resources()
    run_over_text = res.font.render(c.Text.run_over_text,
        False, c.Text.text_color)
    screen.blit(run_over_text, _get_top_left_to_center_on(run_over_text, c.Screen.center))