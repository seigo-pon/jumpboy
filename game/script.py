from datetime import datetime
from enum import StrEnum
from typing import Any, Generic, Self, TypeVar
from uuid import uuid4 as uuid
from game import Size, Path
import json
import os
import pyxel


class GameProfile:
  def __init__(self, title: str, window_size: Size, fps: int, copyright: str, release_year: int, debug: bool) -> None:
    self.title = title
    self.window_size = window_size
    self.fps = fps
    self.copyright = copyright
    self.release_year = release_year
    self.debug = debug


class Language(StrEnum):
  EN = 'en'


class StringRes:
  STRING_FILE = 'string.json'

  def __init__(self, file_path: str, folder: str) -> None:
    self.strings: dict[str, dict[str, str]] = {}
    with open(os.path.join(Path.root(file_path), folder, self.STRING_FILE), mode='r') as f:
      self.strings = json.loads(f.read())

  def string(self, key: str, language: Language) -> str:
    if language in self.strings and key in self.strings[language]:
      return self.strings[language][key]
    return ''


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
    self.id = str(uuid())
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

  @classmethod
  def set_sec(cls, stopwatch: Stopwatch, sec: int, start: bool = False) -> Self:
    return cls.set_msec(stopwatch, sec*1000, start)

  @property
  def msec(self) -> int:
    msec = 0
    if self.start_frame is not None:
      msec = self.stopwatch.msec-self.stopwatch.msec_from_frame(self.start_frame)
    return msec+self.offset_msec

  @property
  def sec(self) -> int:
    return int(self.msec/1000)

  def over(self) -> bool:
    if self.limit_msec is not None and self.limit_msec > 0:
      if self.msec is not None and self.msec >= self.limit_msec:
        return True
    return False

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


class Snapshot:
  SAVE_FOLDER = 'snapshot'

  def folder(self, file_path: str) -> str:
    return os.path.join(Path.root(file_path), self.SAVE_FOLDER)

  def to_json(self) -> dict:
    raise RuntimeError()

  def from_json(self, data: dict) -> None:
    raise RuntimeError()

  def save(self, file_path: str) -> None:
    if not os.path.exists(self.folder(file_path)):
      os.mkdir(self.folder(file_path))

    with open(os.path.join(self.folder(file_path), '{}.json'.format(datetime.now().timestamp())), mode='w') as f:
      json.dump(self.to_json(), f)

  def load(self, file_path: str) -> None:
    files = []
    if os.path.exists(self.folder(file_path)):
      files = os.listdir(self.folder(file_path))
    if len(files) > 0:
      files = sorted(files, reverse=True)
      with open(os.path.join(self.folder(file_path), files[0]), mode='r') as f:
        self.from_json(json.load(f))


TSnapshot = TypeVar('TSnapshot', bound='Snapshot')


class Scene(Generic[TSnapshot]):
  def __init__(
    self,
    profile: GameProfile,
    string_res: StringRes,
    stopwatch: Stopwatch,
    timers: dict[int, Timer],
    snapshot: TSnapshot,
  ) -> None:
    self.profile = profile
    self.string_res = string_res
    self.stopwatch = stopwatch
    self.timers = timers
    self.snapshot = snapshot

  @property
  def title(self) -> str:
    return self.profile.title

  @title.setter
  def title(self, value: str) -> None:
    self.profile.title = value
    pyxel.title(self.profile.title)

  def update(self) -> Self | Any:
    raise RuntimeError()

  def draw(self, transparent_color: int) -> None:
    pyxel.cls(transparent_color)
