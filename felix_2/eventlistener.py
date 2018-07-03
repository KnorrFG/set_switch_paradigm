import pygame

from enum import Enum

import time

class EventConsumerInfo(Enum):
    DONT_CARE = 0
    CONSUMED = 1


class EventListener(object):
    """If a function passed to the listener returns anything but an 
    EventConsumerInfo its return value will be passed through.
    In the case of EventConsumerInfo.DONT_CARE nothing happens, and
    if it is CONSUMED no other functions will see this event.
    """

    @staticmethod
    def _exit_on_ctrl_c(event):
        if event.type == pygame.KEYDOWN \
            and event.key == pygame.K_c \
            and pygame.key.get_mods() & pygame.KMOD_CTRL:
            pygame.quit()
            exit(1)
        else:
            return EventConsumerInfo.DONT_CARE


    def __init__(self, permanently_applied_functions=None):
        self.permanently_applied_functions = permanently_applied_functions + (
            EventListener._exit_on_ctrl_c,
        )


    def listen(self, functions = None):
        if functions:
            funcs = self.permanently_applied_functions + functions
        else:
            funcs = self.permanently_applied_functions

        for event in pygame.event.get():
            for func in funcs:
                #import ipdb; ipdb.set_trace()
                ret = func(event)
                if ret == EventConsumerInfo.CONSUMED: break
                if ret == EventConsumerInfo.DONT_CARE: continue
                else: return ret


    def wait_for_keypress(self, key, n=1):
        my_const = "key_consumed"
        keypress_listener = lambda e: my_const \
            if e.type == pygame.KEYDOWN and e.key == key \
            else EventConsumerInfo.DONT_CARE

        while True:
            if self.listen((keypress_listener,)) == my_const:
                return


    def wait_for_seconds(self, seconds):
        start = time.time()
        while time.time() - start < seconds:
            self.listen()
