from enum import IntEnum
from game import Coordinate, Size, Path
import json
import os
import pyxel


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
  def play(self) -> None:
    pass


class SoundEffect(AssetSound):
  def __init__(self, channel: int, id: int) -> None:
    self.channel = channel
    self.id = id

  def play(self) -> None:
    pyxel.play(self.channel, self.id, resume=True)


class AssetMusic(AssetSound):
  def __init__(self, name: str) -> None:
    self.name = name

  def stop(self) -> None:
    pass


class Music(AssetMusic):
  def __init__(self, id: int, channels: list[int]) -> None:
    super().__init__(str(id))

    self.id = id
    self.channels = channels

  def play(self) -> None:
    pyxel.playm(self.id, loop=True)

  def stop(self) -> None:
    for channel in self.channels:
      pyxel.stop(channel)


class Bgm8BitMusic(AssetMusic):
  BGM_FOLDER_NAME = 'bgm'

  def __init__(self, filename: str, path: Path, offset_id: int, un_play_channels: list[int]) -> None:
    super().__init__(filename)

    self.bgm: dict = {}
    file_path = os.path.join(path.asset_path, self.BGM_FOLDER_NAME, '{}.json'.format(filename))
    with open(file_path, mode='r') as f:
      self.bgm = json.loads(f.read())
    self.offset_id = offset_id
    self.un_play_channels = un_play_channels

    self.channels: list[int] = []

  def play(self) -> None:
    if len(self.channels) == 0:
      for (ch, sound) in enumerate(self.bgm):
        if ch in self.un_play_channels:
          continue

        pyxel.sounds[self.offset_id+ch].set(*sound)
        pyxel.play(ch, self.offset_id+ch, loop=True)
        self.channels.append(ch)
      print('bgm 8bit play', self.channels)

  def stop(self) -> None:
    for channel in self.channels:
      pyxel.stop(channel)
    print('bgm 8bit stop', self.channels)
    self.channels = []
