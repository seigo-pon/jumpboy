import os


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
  def __init__(self, file_path: str) -> None:
    self.file_path = file_path

  @property
  def root(self) -> str:
    return os.path.abspath(os.path.join(os.path.abspath(self.file_path), os.pardir))
