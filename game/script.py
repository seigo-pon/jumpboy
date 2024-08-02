from datetime import datetime
from typing import Generic, Self, Tuple, TypeVar
from uuid import uuid4 as uuid
from game import Size
import json
import os
import pyxel


class GameProfile:
  def __init__(self, title: str, window_size: Size, fps: int, copyright: str) -> None:
    self.title = title
    self.window_size = window_size
    self.fps = fps
    self.copyright = copyright
  

class Stopwatch:
  def __init__(self, fps: int) -> None:
    self.fps = fps
    self.count = 0
    self.timers: dict[str, Tuple[int | None, int, int]] = {}

  def set_timer(self) -> str:
    id = str(uuid())
    self.timers[id] = (self.count, 0, 0)
    return id

  def set_msec(self, msec: int) -> str:
    id = str(uuid())
    self.timers[id] = (self.count, msec, 0)
    return id

  def set_sec(self, sec: int) -> str:
    id = str(uuid())
    self.timers[id] = (self.count, sec*1000, 0)
    return id

  def remove(self, id: str) -> None:
    if id in self.timers:
      del self.timers[id]

  def map_msec(self, count: int) -> int:
    return int(1/self.fps*count*1000)

  @property
  def msec(self) -> int:
    return self.map_msec(self.count)

  @property
  def sec(self) -> int:
    return int(self.msec/1000)

  def elapsed_msec(self, id: str) -> int | None:
    if id in self.timers:
      msec = 0
      first_count = self.timers[id][0]
      if first_count is not None:
        msec = self.msec-self.map_msec(first_count)
      return msec+self.timers[id][2]

    return None

  def elapsed_sec(self, id: str) -> int | None:
    msec = self.elapsed_msec(id)
    if msec is not None:
      return int(msec/1000)
    return None

  def over(self, id: str) -> bool:
    if id in self.timers:
      if self.timers[id][1] > 0:
        msec = self.elapsed_msec(id)
        if msec is not None and msec >= self.timers[id][1]:
          return True

    return False

  def pause(self, id: str) -> None:
    if id in self.timers:
      msec = self.elapsed_msec(id)
      if msec is not None:
        self.timers[id] = (None, self.timers[id][1], msec)

  def resume(self, id: str) -> None:
    if id in self.timers:
      self.timers[id] = (self.count, self.timers[id][1], self.timers[id][2])

  def update(self) -> None:
    self.count += 1

class Snapshot:
  SAVE_FOLDER = 'snapshot'

  @property
  def folder(self) -> str:
    return os.path.join(self.SAVE_FOLDER)

  def to_json(self) -> str:
    raise Exception()

  def from_json(self, data: dict) -> None:
    pass

  def save(self) -> None:
    if not os.path.exists(self.folder):
      os.mkdir(self.folder)

    with open(os.path.join(self.folder, '{}.json'.format(datetime.now().timestamp)), mode='w') as f:
      json.dump(self.to_json(), f)

  def load(self) -> None:
    if os.path.exists(self.folder):
      files = os.listdir(self.folder)

    if len(files) > 0:
      files = sorted(files, reverse=True)
      with open(os.path.join(self.folder, files[0]), mode='r') as f:
        self.from_json(json.load(f))


T = TypeVar('T')

class Scene(Generic[T]):
  def __init__(self, profile: GameProfile, stopwatch: Stopwatch, snapshot: T) -> None:
    self.profile = profile
    self.stopwatch = stopwatch
    self.snapshot = snapshot

  def update(self) -> Self:
    raise Exception()

  def draw(self, transparent_color: int) -> None:
    pyxel.cls(transparent_color)
