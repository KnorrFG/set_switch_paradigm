import pathlib
from enum import Enum

import pygame
from toolz import memoize

import config as c


class ImagePair(object):
    def __init__(self, name, left, right):
        self.left = left
        self.right = right
        self.name = name

    def __getitem__(self, orientation):
        return self.left if orientation == Orientation.LEFT \
            else self.right


class Orientation(Enum):
    LEFT = 1
    RIGHT = 2

    def inverted(self):
        return Orientation.RIGHT if self == Orientation.LEFT \
            else Orientation.LEFT

    def to_id(self):
        return "l" if self == Orientation.LEFT else "r"

    def __str__(self):
        return self.name


def _load_stimuli(prefix, path):
    imgPath = pathlib.Path(path)
    images = list(imgPath.glob(prefix + "*.gif"))
    imagePairs = []

    def load(x):
        img = pygame.image.load(str(x)).convert_alpha()
        pArr = pygame.PixelArray(img)
        pArr.replace((255, 255, 255, 255), (0, 0, 0, 0))
        pArr.close()
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


faces = memoize(lambda: _load_stimuli(c.Stimuli.face_prefix, c.Stimuli.path))
houses = memoize(lambda: _load_stimuli(c.Stimuli.house_prefix, c.Stimuli.path))
