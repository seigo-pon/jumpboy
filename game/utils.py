import os


class Coordinate:
  def __init__(self, x: float, y: float) -> None:
    self.x = x
    self.y = y


class Size:
  def __init__(self, width: int, height: int) -> None:
    self.width = width
    self.height = height

  @property
  def center(self) -> Coordinate:
    return Coordinate(self.width/2, self.height/2)


class Path:
  @classmethod
  def root(cls, file_path: str) -> str:
    return os.path.abspath(os.path.join(os.path.abspath(file_path), os.pardir))
