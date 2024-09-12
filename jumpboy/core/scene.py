from datetime import datetime
from typing import Any, Callable, Generic, Self, TypeVar
from core import Size, Path, Stopwatch, Timer, StringRes, Typewriter
import json
import os
import pyxel
try:
  import js
  print('pyodide loaded')
  js_import = True
except:
  js_import = False
  print('pyodide no loaded')


class GameConfig:
  def __init__(
    self,
    path: Path,
    title: str,
    window_size: Size,
    fps: int,
    copyright: str,
    released_year: int,
    debug: bool,
  ) -> None:
    self.path = path
    self.title = title
    self.window_size = window_size
    self.fps = fps
    self.copyright = copyright
    self.released_year = released_year
    self.debug = debug


class Snapshot:
  SNAPSHOT_NAME = 'snapshot'
  FILE_MAX_COUNT = 5

  def folder(self, path: Path) -> str:
    return os.path.join(path.root, self.SNAPSHOT_NAME)

  def to_json(self) -> dict:
    raise RuntimeError()

  def from_json(self, data: dict) -> None:
    raise RuntimeError()

  def save(self, path: Path) -> None:
    if js_import:
      json_data = self.to_json()
      print('snapshot save', json_data)
      js.window.localStorage.setItem(self.SNAPSHOT_NAME, json.dumps(json_data))
    else:
      folder = self.folder(path)
      print('snapshot folder', folder)
      if not os.path.exists(folder):
        os.mkdir(folder)

      if os.path.exists(folder):
        files = os.listdir(folder)
        delta_file_count = len(files)-self.FILE_MAX_COUNT
        if delta_file_count > 0:
          files = sorted(files)
          for index in range(delta_file_count):
            print('delete snapshot old file', files[index])
            os.remove(os.path.join(folder, files[index]))

      file_path = os.path.join(folder, '{}.json'.format(datetime.now().timestamp()))
      with open(file_path, mode='w') as f:
        json_data = self.to_json()
        print('snapshot save', file_path, json_data)
        json.dump(json_data, f)

  def load(self, path: Path) -> None:
    if js_import:
      json_str = js.window.localStorage.getItem(self.SNAPSHOT_NAME)
      if json_str is not None and json_str != '':
        json_data = json.loads(json_str)
        print('snapshot load', json_data)
        self.from_json(json_data)
    else:
      files = []
      folder = self.folder(path)
      print('snapshot folder', folder)

      if os.path.exists(folder):
        files = os.listdir(folder)

      if len(files) > 0:
        files = sorted(files, reverse=True)
        file_path = os.path.join(self.folder(path), files[0])
        with open(file_path, mode='r') as f:
          json_data = json.load(f)
          print('snapshot load', file_path, json_data)
          self.from_json(json_data)


class Seq:
  def __init__(
    self,
    stopwatch: Stopwatch,
    wait_msec: int,
    process: Callable[[bool, Timer], bool],
    to_next: Callable[[], Any] | None,
  ) -> None:
    self.timer = Timer.set_msec(stopwatch, wait_msec, False)
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

        res = seq.process(not seq.started, seq.timer)
        seq.started = True
        if not res:
          break

        seq.ended = True
        if seq.to_next is not None:
          return seq.to_next()

    return None


TSnapshot = TypeVar('TSnapshot', bound='Snapshot')

class Scene(Generic[TSnapshot]):
  def __init__(
    self,
    config: GameConfig,
    string_res: StringRes,
    stopwatch: Stopwatch,
    typewriter: Typewriter,
    snapshot: TSnapshot,
  ) -> None:
    self.config = config
    self.string_res = string_res
    self.stopwatch = stopwatch
    self.typewriter = typewriter
    self.snapshot = snapshot
    self.time_seq = TimeSeq([])

  @property
  def updating_variations(self) -> list[Any]:
    raise RuntimeError()

  def update(self) -> Self | Any:
    self.stopwatch.update()

    res = self.time_seq.update()
    if res is not None:
      print('next scene', vars(res))
      return res

    for variation in self.updating_variations:
      variation.update(self.stopwatch, self.snapshot)

    return self

  @property
  def drawing_subjects(self) -> list[Any]:
    raise RuntimeError()

  def draw(self, transparent_color: int) -> None:
    pyxel.cls(transparent_color)

    for subject in self.drawing_subjects:
      subject.draw(transparent_color)
