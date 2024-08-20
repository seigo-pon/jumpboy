from enum import IntEnum
from game import Coordinate, Size


class AssetImage:
  class Pose(IntEnum):
    NORMAL = 0
    MIRROR_X = 1
    MIRROR_Y = 2
    MIRROR_XY = 3

  def __init__(self, id: int, address: Coordinate, scale: Size, pose: Pose, transparent_color: int) -> None:
    self.id = id
    self.address = address
    self.scale = scale
    self.pose = pose
    self.transparent_color = transparent_color

  @classmethod
  def basic_size(cls) -> Size:
    raise RuntimeError()

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
  @classmethod
  def basic_size(cls) -> Size:
    return Size(8, 8)


class TileMap(AssetImage):
  @classmethod
  def basic_size(cls) -> Size:
    return Size(64, 64)


class AssetSound:
  pass


class Sound(AssetSound):
  pass


class Music(AssetSound):
  pass
