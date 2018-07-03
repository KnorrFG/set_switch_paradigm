from enum import Enum

class Orientation(Enum):
    LEFT = 1
    RIGHT = 2


    def inverted(self):
        return Orientation.RIGHT if self == Orientation.LEFT \
            else Orientation.LEFT


    def to_id(self):
        return "l" if self == Orientation.LEFT else "r"


class ImagePair(object):
    def __init__(self, name, left, right):
        self.left = left
        self.right = right
        self.name = name

    def __getitem__(self, orientation):
        return self.left if orientation == Orientation.LEFT \
            else self.right