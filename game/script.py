from datetime import datetime
from enum import StrEnum
from typing import Any, Callable, Generic, Self, TypeVar
from game import Size, Path
import json
import os
import pyxel


class GameConfig:
  def __init__(
    self,
    path: Path,
    title: str,
    window_size: Size,
    fps: int,
    transparent_color: int,
    copyright: str,
    released_year: int,
    debug: bool,
  ) -> None:
    self.path = path
    self.title = title
    self.window_size = window_size
    self.fps = fps
    self.transparent_color = transparent_color
    self.copyright = copyright
    self.released_year = released_year
    self.debug = debug


class Language(StrEnum):
  EN = 'en'
  JP = 'jp'


class StringRes:
  STRING_FILE = 'string.json'

  def __init__(self, path: Path, folder: str) -> None:
    self.strings: dict[str, dict[str, str]] = {}
    with open(os.path.join(path.root, folder, self.STRING_FILE), mode='r') as f:
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


class Seq:
  def __init__(
    self,
    stopwatch: Stopwatch,
    msec: int,
    process: Callable[[bool], bool],
    to_next: Callable[[], Any] | None,
  ) -> None:
    self.timer = Timer.set_msec(stopwatch, msec)
    self.started = False
    self.process = process
    self.to_next = to_next
    self.ended = False


class TimeSeq:
  def __init__(self, seqs: list[Seq]) -> None:
    self.seqs = seqs

  @property
  def ended(self) -> bool:
    return len(list(filter(lambda x: not x.ended, self.seqs))) == 0

  def update(self) -> Any | None:
    for seq in self.seqs:
      if not seq.ended:
        seq.timer.resume()
        if not seq.timer.over:
          break

        res = seq.process(not seq.started)
        seq.started = True
        if not res:
          break

        seq.ended = True
        if seq.to_next is not None:
          return seq.to_next()

    return None


class Snapshot:
  SNAPSHOT_FOLDER = 'snapshot'

  def folder(self, path: Path) -> str:
    return os.path.join(path.root, self.SNAPSHOT_FOLDER)

  def to_json(self) -> dict:
    raise RuntimeError()

  def from_json(self, data: dict) -> None:
    raise RuntimeError()

  def save(self, path: Path) -> None:
    if not os.path.exists(self.folder(path)):
      os.mkdir(self.folder(path))
    with open(os.path.join(self.folder(path), '{}.json'.format(datetime.now().timestamp())), mode='w') as f:
      json.dump(self.to_json(), f)

  def load(self, path: Path) -> None:
    files = []
    if os.path.exists(self.folder(path)):
      files = os.listdir(self.folder(path))
    if len(files) > 0:
      files = sorted(files, reverse=True)
      with open(os.path.join(self.folder(path), files[0]), mode='r') as f:
        self.from_json(json.load(f))


TSnapshot = TypeVar('TSnapshot', bound='Snapshot')
class Scene(Generic[TSnapshot]):
  def __init__(
    self,
    config: GameConfig,
    string_res: StringRes,
    stopwatch: Stopwatch,
    snapshot: TSnapshot,
  ) -> None:
    self.config = config
    self.string_res = string_res
    self.stopwatch = stopwatch
    self.snapshot = snapshot
    self.time_seq = TimeSeq([])

  @property
  def title(self) -> str:
    return self.config.title

  @title.setter
  def title(self, value: str) -> None:
    self.config.title = value
    pyxel.title(self.config.title)

  def update(self) -> Self | Any:
    self.stopwatch.update()

    res = self.time_seq.update()
    if res is not None:
      return res

    return self

  def draw(self) -> None:
    pyxel.cls(self.config.transparent_color)
