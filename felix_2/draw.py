import pygame
from toolz import memoize, partial, compose, concat, pipe
from toolz.curried import map, accumulate

from resources import Resources
from simple_types import *
import config as c

from operator import add
import itertools as itt


tmap = compose(tuple, map)

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

def _blit_h_centered(src, target, x):
    h_target = _surface_height(target)
    h_src = _surface_height(src)
    assert h_target >= h_src
    target.blit(src, (x, (h_target - h_src) // 2))

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


_conv_string_to_surface = memoize(lambda s:
    Resources().font.render(s, False, c.Text.text_color))
_surface_height = lambda s: s.get_rect().height
_surface_width = lambda s: s.get_rect().width
_add_margin = lambda x: x + c.Feedback.text_margin


@memoize
def _make_filled_surface(color, size):
    surface = pygame.Surface(size)
    surface. fill(color)
    return surface


def render_text(surface, text):
    """text must be an array of pygame.Surfaces"""
    #import ipdb; ipdb.set_trace()
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
    text = _conv_string_to_surface(c.Text.block_instruction)
    screen.blit(text, _get_top_left_to_center_on(text, c.Screen.center))


def example_screen(screen):
    res = Resources()
    sr = screen.get_rect()
    stim = pygame.Surface(res.stim_background.get_rect().size)
    text = pygame.Surface((sr.width, int(sr.height * 0.33)))
    stimulus(stim, res.faces[0][Orientation.LEFT], res.houses[0][Orientation.RIGHT])
    text.fill(c.Screen.background)
    render_text(text, [_conv_string_to_surface(s) for s in c.Text.instruction_example])

    x = sr.width / 2
    target_center_stim = (x , int(0.33 * sr.height))
    target_center_text = (x, int(0.67 * sr.height))

    screen.blit(stim, _get_top_left_to_center_on(stim, target_center_stim))
    screen.blit(text, _get_top_left_to_center_on(text, target_center_text))


def session_instruction(screen):
    render_text(screen, Resources().session_instruction)


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



@memoize
def _make_feedback_display_surface(cell_size):
    def index_to_color(i):
        if i < c.Feedback.green_abs_diff: return "G"
        elif i < c.Feedback.yellow_abs_diff: return "Y"
        else: return "R"

    cell_surface = partial(_make_filled_surface, size=cell_size)
    cell_colors_right = tmap(index_to_color, range(c.Feedback.yellow_abs_diff + 1))
    cell_colors = tuple(reversed(cell_colors_right)) + ("G",) + cell_colors_right
    display_size = (len(cell_colors) * cell_size[0], cell_size[1])
    display_surface = pygame.Surface(display_size)
    for i, cell_color in enumerate(cell_colors):
        display_surface.blit(cell_surface(
            c.Feedback.color_table[cell_color]), 
            (i * cell_size[0], 0))
    
    return display_surface


def _compose_feedback_screen(disp_bg, face_text, house_text, cell_size, diff):
    pointer_pos = disp_bg.get_rect().width / 2 \
                    + diff * cell_size[0] \
                    + face_text.get_rect().width \
                    + c.Feedback.text_margin
    surfaces = (face_text, disp_bg, house_text)
    feed_back_surface = _make_filled_surface(c.Screen.background, (
        sum(map(_surface_width, surfaces)) + 2 * c.Feedback.text_margin,
        max(map(_surface_height, surfaces))
    ))   
    x_offsets = itt.chain((0,), pipe(surfaces[:-1], map(_surface_width), 
                                                 map(_add_margin), 
                                                 accumulate(add)))
    for offset, surf in zip(x_offsets, surfaces):
        _blit_h_centered(surf, feed_back_surface, offset)
    pygame.draw.line(feed_back_surface, c.Feedback.indicator_color, 
        (pointer_pos, 0), (pointer_pos, _surface_height(feed_back_surface)),
        c.Feedback.indicator_thickness)
    return feed_back_surface


def feedback(screen, target_counter):
    sr = screen.get_rect()
    cell_size = (int(sr.width * c.Feedback.cell_width_percent),
                 int(sr.height * c.Feedback.cell_height_percent))

    max_diff = c.Feedback.yellow_abs_diff + 1
    clamp = lambda diff: max(-max_diff, min(max_diff, diff))
    _blit_to_center(_compose_feedback_screen(
        _make_feedback_display_surface(cell_size), 
        _conv_string_to_surface("Gesicht"),
        _conv_string_to_surface("Haus"),
        cell_size, 
        clamp(target_counter[BlockTarget.HOUSE] - target_counter[BlockTarget.FACE])
    ), screen)



def run_over(screen):
    res = Resources()
    run_over_text = res.font.render(c.Text.run_over_text,
        False, c.Text.text_color)
    screen.blit(run_over_text, _get_top_left_to_center_on(run_over_text, c.Screen.center))
    