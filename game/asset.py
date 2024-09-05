from enum import IntEnum, StrEnum
from game import Coordinate, Size, Path
import json
import os
import pyxel


class Language(StrEnum):
  EN = 'en'
  JP = 'jp'


class StringRes:
  STRING_FILE = 'string.json'

  def __init__(self, path: Path) -> None:
    self.strings: dict[str, dict[str, str]] = {}
    with open(os.path.join(path.asset_path, self.STRING_FILE), mode='r') as f:
      self.strings = json.loads(f.read())

  def string(self, key: str, language: Language) -> str:
    if language in self.strings and key in self.strings[language]:
      return self.strings[language][key]
    return ''


class AssetImageId:
  def __init__(self, id: int, x: int) -> None:
    self.id = id
    self.x = x


class AssetImage:
  class Pose(IntEnum):
    NORMAL = 0
    MIRROR_X = 1
    MIRROR_Y = 2
    MIRROR_XY = 3

  def __init__(self, id: int, address: Coordinate, scale: Size, pose: Pose) -> None:
    self.id = id
    self.address = address
    self.scale = scale
    self.pose = pose

  @classmethod
  def basic_size(cls) -> Size:
    return Size(8, 8)

  @property
  def origin(self) -> Coordinate:
    return Coordinate(self.address.x*self.basic_size().width, self.address.y*self.basic_size().height)

  @property
  def size(self) -> Size:
    return Size(self.scale.width*self.basic_size().width, self.scale.height*self.basic_size().height)

  @property
  def copy_vector(self) -> Size:
    if self.pose == self.Pose.MIRROR_X:
      return Size(self.size.width*-1, self.size.height)
    elif self.pose == self.Pose.MIRROR_Y:
      return Size(self.size.width, self.size.height*-1)
    elif self.pose == self.Pose.MIRROR_XY:
      return Size(self.size.width*-1, self.size.height*-1)
    return self.size


class Image(AssetImage):
  pass


class TileMap(AssetImage):
  @classmethod
  def basic_size(cls) -> Size:
    return Size(64, 64)


class AssetSound:
  @classmethod
  def channel_count(cls) -> int:
    return 4

  def play(self) -> None:
    raise RuntimeError()


class SoundEffect(AssetSound):
  def __init__(self, channel: int, id: int) -> None:
    self.channel = channel
    self.id = id

  def play(self) -> None:
    pyxel.play(self.channel, self.id, resume=True)
    print('sound effect play', self.id, self.channel)


class AssetBgm(AssetSound):
  def __init__(self, name: str) -> None:
    self.name = name

    self.channels: list[int] = []

  def stop(self) -> None:
    for channel in self.channels:
      pyxel.stop(channel)
    print('bgm stop', self.channels)


class Bgm(AssetBgm):
  class Param:
    def __init__(self, channels: list[int]) -> None:
      self.channels = channels

  @classmethod
  def get_name(cls, id: int) -> str:
    return 'bgm_{}'.format(id)

  def __init__(self, id: int, param: Param) -> None:
    super().__init__(Bgm.get_name(id))

    self.id = id
    self.channels = param.channels

  def play(self) -> None:
    if len(self.channels) > 0 and pyxel.play_pos(self.channels[0]) is None:
      pyxel.playm(self.id, loop=True)
      print('bgm play', self.name, self.channels)


class RawBgm(AssetBgm):
  class Param:
    def __init__(
      self,
      path: Path,
      folder: str,
      start_id: int,
      exclude_play_channels: list[int],
    ) -> None:
      self.path = path
      self.folder = folder
      self.start_id = start_id
      self.exclude_play_channels = exclude_play_channels

  @classmethod
  def get_name(cls, filename: str) -> str:
    return 'raw_bgm_{}'.format(filename)

  def __init__(self, filename: str, param: Param) -> None:
    super().__init__(RawBgm.get_name(filename))

    self.bgm_raw_data: dict = {}

    file_path = os.path.join(param.path.asset_path, param.folder, '{}.json'.format(filename))
    with open(file_path, mode='r') as f:
      self.bgm_raw_data = json.loads(f.read())
    print('raw bgm loaded', filename)

    self.start_id = param.start_id
    self.exclude_play_channels = param.exclude_play_channels

  def play(self) -> None:
    if len(self.channels) == 0:
      for (channel, sound) in enumerate(self.bgm_raw_data):
        if channel in self.exclude_play_channels:
          continue

        id = self.start_id+channel

        pyxel.sounds[id].set(*sound)
        pyxel.play(channel, id, loop=True, resume=True)

        self.channels.append(channel)
      print('raw bgm play', self.name, self.channels)

  def stop(self) -> None:
    super().stop()
    self.channels = []
