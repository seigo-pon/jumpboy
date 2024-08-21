import os
from random import randint


class Coordinate:
  def __init__(self, x: float, y: float) -> None:
    self.x = x
    self.y = y


class Size:
  def __init__(self, width: float, height: float) -> None:
    self.width = width
    self.height = height

  @property
  def center(self) -> Coordinate:
    return Coordinate(self.width/2, self.height/2)


class Path:
  def __init__(self, file_path: str, asset_folder: str) -> None:
    self.root = os.path.abspath(os.path.join(os.path.abspath(file_path), os.pardir))
    self.asset_folder = asset_folder
    print('root path', self.root, self.asset_folder)

  @property
  def asset_path(self) -> str:
    return os.path.join(self.root, self.asset_folder)


class Dice:
  @classmethod
  def roll(cls, max: int) -> int:
    value = randint(0, max)
    print('dice roll', max, value)
    return value
