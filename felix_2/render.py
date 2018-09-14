import time
import random

import pygame

from pyparadigm.surface_composition import *
from pyparadigm.misc import *

from toolz import partial, memoize, pipe
from toolz import compose as t_compose
from toolz.curried import map

import config as c

lmap = t_compose(list, map)
text_to_surface = memoize(lambda text: Text(text, 
                                    Font(c.Text.font, size=c.Text.font_size), 
                                    color=c.Text.text_color))

surface_to_screen = memoize(lambda s_text: 
        compose(_bg())(
            Surface(Margin(bottom=2))(s_text)))

_bg = partial(empty_surface, c.Screen.background)
_font = lambda: Font(c.Text.font, size=c.Text.font_size)


def shuffled(iterable):
    l = list(iterable)
    random.shuffle(l)
    return l


def multi_page_text(event_listener, text_array):
    screen_rect = pygame.display.get_surface().get_rect()
    screens = pipe(text_array, 
        map(text_to_surface), 
        map(surface_to_screen))
    slide_show(screens, partial(event_listener.wait_for_n_keypresses, pygame.K_RETURN))
    

def stimulus(face, house):
    screen = compose(_bg())(
        Padding.from_scale(c.Stimuli.scale)(
            Overlay(*shuffled([
                Surface(scale=1)(face), 
                Surface(scale=1)(house)]) ) ) )
    display(screen)


@memoize
def fixcross():
    return compose(_bg())( 
                Padding.from_scale(c.Fixcross.factor)(
                    RectangleShaper()(
                        Cross(c.Fixcross.width))))


@memoize
def text_page(content):
    return compose(_bg())(
        Text(content, _font()))


@memoize
def feedback(difference):
    if difference == 0: mdiff = difference
    elif difference < 0: mdiff = difference + 0.5
    else: mdiff = difference - 0.5
    
    return compose(_bg())(
        Padding.from_scale(c.Feedback.percentual_display_width, 
                           c.Feedback.cell_height_percent)(
            LinLayout("h")(
                LLItem(1)(Text("Haus", _font())),
                LLItem(4)(Overlay(
                    LinLayout("h")(
                        LLItem(1)(Fill(c.Feedback.color_table["R"])),
                        LLItem(c.Feedback.yellow_prop)(Fill(c.Feedback.color_table["Y"])),
                        LLItem(c.Feedback.green_prop)(Fill(c.Feedback.color_table["G"])),
                        LLItem(c.Feedback.yellow_prop)(Fill(c.Feedback.color_table["Y"])),
                        LLItem(1)(Fill(c.Feedback.color_table["R"])),
                    ),
                    Surface(margin=Margin(c.Feedback.max_diff - mdiff, 
                                          c.Feedback.max_diff + mdiff))(
                        empty_surface(0, (c.Feedback.indicator_thickness,
                                    pygame.display.get_surface().get_rect().h
                                    * c.Feedback.cell_height_percent)))
                )),
                LLItem(1)(Text("Gesicht", _font()))
            )
        )
    )

