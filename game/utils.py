from random import randint
from typing import Self
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
  def __init__(self, file_path: str, asset_folder: str) -> None:
    self.root = os.path.abspath(os.path.join(os.path.abspath(file_path), os.pardir))
    self.asset_folder = asset_folder
    print('root path', self.root, self.asset_folder)

  @property
  def asset_path(self) -> str:
    return os.path.join(self.root, self.asset_folder)


class Stopwatch:
  def __init__(self, fps: int) -> None:
    self.fps = fps
    self.frame = 0

  def msec_from_frame(self, frame: int) -> int:
    return int(1/self.fps*frame*1000)

  @property
  def msec(self) -> int:
    return self.msec_from_frame(self.frame)

  @property
  def sec(self) -> int:
    return int(self.msec/1000)

  def update(self) -> None:
    self.frame += 1


class Timer:
  def __init__(self, stopwatch: Stopwatch) -> None:
    self.stopwatch = stopwatch
    self.start_frame: int | None = None
    self.limit_msec: int | None = None
    self.offset_msec = 0

  @classmethod
  def set_timer(cls, stopwatch: Stopwatch, start: bool = False) -> Self:
    timer = cls(stopwatch)
    if start:
      timer.resume()
    return timer

  @classmethod
  def set_msec(cls, stopwatch: Stopwatch, msec: int, start: bool = False) -> Self:
    timer = cls.set_timer(stopwatch, start)
    timer.limit_msec = msec
    return timer

  @property
  def msec(self) -> int:
    msec = 0
    if self.start_frame is not None:
      msec = self.stopwatch.msec-self.stopwatch.msec_from_frame(self.start_frame)
    return msec+self.offset_msec

  @property
  def sec(self) -> int:
    return int(self.msec/1000)

  @property
  def over(self) -> bool:
    if self.limit_msec is not None and self.limit_msec >= 0:
      if self.msec is not None and self.msec >= self.limit_msec:
        return True
    return False

  @property
  def running(self) -> bool:
    return self.start_frame is not None

  def pause(self) -> None:
    if self.msec is not None:
      self.offset_msec += self.msec
      self.start_frame = None

  def resume(self) -> None:
    if self.start_frame is None:
      self.start_frame = self.stopwatch.frame

  def reset(self) -> None:
    self.start_frame = self.stopwatch.frame
    self.offset_msec = 0


class Dice:
  @classmethod
  def roll(cls, max: int) -> int:
    value = randint(0, max)
    print('dice roll', max, value)
    return value
