from random import randint
from typing import Self
import os
import PyxelUniversalFont as puf


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
    self.first_frame: int | None = None
    self.limit_msec: int | None = None
    self.offset_msec = 0

  @classmethod
  def set_timer(cls, stopwatch: Stopwatch, start: bool) -> Self:
    timer = cls(stopwatch)
    if start:
      timer.resume()
    return timer

  @classmethod
  def set_msec(cls, stopwatch: Stopwatch, msec: int, start: bool) -> Self:
    timer = cls.set_timer(stopwatch, start)
    timer.limit_msec = msec
    return timer

  @property
  def msec(self) -> int:
    msec = 0
    if self.first_frame is not None:
      msec = self.stopwatch.msec-self.stopwatch.msec_from_frame(self.first_frame)
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
    return self.first_frame is not None

  def pause(self) -> None:
    if self.first_frame is not None:
      if self.msec is not None:
        self.offset_msec = self.msec
        self.first_frame = None

  def resume(self) -> None:
    if self.first_frame is None:
      self.first_frame = self.stopwatch.frame

  def reset(self) -> None:
    self.first_frame = self.stopwatch.frame
    self.offset_msec = 0


class TextScriber:
  FOLDER = 'font'
  DEFAULT_FONT_FILE = 'misaki_mincho.ttf'
  CUSTOM_FONT_FILES: dict[int, dict[bool, str]] = {
    10: {
      False: 'PixelMplus10-Regular.ttf',
      True: 'PixelMplus10-Bold.ttf',
    },
    12: {
      False: 'PixelMplus12-Regular.ttf',
      True: 'PixelMplus12-Bold.ttf',
    },
  }

  _instance: Self | None = None
  _writers: dict[str, puf.Writer] = {}

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super(TextScriber, cls).__new__(cls)
      print('text scriber create', cls._instance)
    return cls._instance

  @classmethod
  def word_size(cls, font_size: int) -> Size:
    return Size(font_size/2, font_size)

  def writer(self, font_size: int, bold: bool) -> puf.Writer:
    font = self.CUSTOM_FONT_FILES[font_size][bold]
    if font not in puf.get_available_fonts():
      font = self.DEFAULT_FONT_FILE

    if font not in self._writers:
      writer = puf.Writer(font)
      print('new font', font, writer, self._writers)
      self._writers[font] = writer

    return self._writers[font]


class Dice:
  @classmethod
  def roll(cls, max: int) -> int:
    value = randint(0, max)
    print('dice roll', max, value)
    return value
