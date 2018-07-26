import pygame

import config as c
from simple_types import ImagePair

import pathlib
import configparser

class Resources(object):
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance._cache = {}
        return cls._instance


    def _get_or_compute_and_save(self, key, func):
        if not key in self._cache:
            self._cache[key] = func()
        return self._cache[key]


    def load_all(self):
        for pname in dir(self):
            if not pname.startswith("_") and pname != "load_all":
                getattr(self, pname)

        
    @staticmethod
    def _make_font():
        return pygame.font.SysFont(c.Text.font, c.Text.font_size)


    @staticmethod
    def _load_ini():
        parser = configparser.ConfigParser()
        parser.read("config.ini")
        return parser


    @staticmethod
    def _load_stimuli(prefix, path):
        #import ipdb; ipdb.set_trace()
        imgPath = pathlib.Path(path)
        images = list(imgPath.glob(prefix + "*.gif"))
        imagePairs = []

        def load(x):
            img = pygame.image.load(str(x)).convert()
            img.set_colorkey(c.Stimuli.color_key, pygame.RLEACCEL)
            return img

        i = 0
        while True:
            imgId = prefix + str(i)
            imgL = imgPath / (imgId + "l.gif")
            imgR = imgPath / (imgId + "r.gif")

            if imgL in images and imgR in images:
                imagePairs.append(ImagePair(imgId, load(imgL), load(imgR)))
                i += 1
            else:
                return imagePairs


    @staticmethod
    def _load_houses():
        return Resources._load_stimuli(c.Stimuli.house_prefix, c.Stimuli.path)


    @staticmethod
    def _load_faces():
        return Resources._load_stimuli(c.Stimuli.face_prefix, c.Stimuli.path)


    @staticmethod
    def _make_stim_bg():
        screen_rect = pygame.display.get_surface().get_rect()
        bg = pygame.Surface((int(screen_rect.width*c.Stimuli.scale), 
            int(screen_rect.height*c.Stimuli.scale)))
        return bg.convert()


    @property
    def font(self):
        return self._get_or_compute_and_save("font", Resources._make_font)


    @property
    def faces(self):
        return self._get_or_compute_and_save("faces", 
            Resources._load_faces)


    @property
    def houses(self):
        return self._get_or_compute_and_save("houses", 
            Resources._load_houses)


    @property
    def stim_background(self):
        return self._get_or_compute_and_save("stim_bg",
            self._make_stim_bg)


    @property
    def output_base_path(self):
        return pathlib.Path(self.ini["Path"]["output_base"])


    @property
    def display_position(self):
        return self.ini["Display"]["position"]


    @property
    def ini(self):
        return self._get_or_compute_and_save("ini",
            Resources._load_ini)


    @property
    def show_intro(self):
        return self.ini["Options"]["show_help"].lower().strip() == "true"


    @property
    def do_train_run(self):
        return self.ini["Options"]["do_train_run"].lower().strip() == "true"
