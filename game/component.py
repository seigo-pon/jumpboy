from typing import Self, TypeVar
from uuid import uuid4 as uuid
from game import Coordinate, Image, Size, TileMap, Music
import pyxel


class Scribe:
  def draw(self, transparent_color: int) -> None:
    raise RuntimeError()


class Collision:
  def __init__(self, origin: Coordinate, size: Size) -> None:
    self.origin = origin
    self.size = size

  def min(self, center: Coordinate) -> Coordinate:
    return Coordinate(
      center.x-self.size.width/2+self.origin.x,
      center.y-self.size.height/2+self.origin.y,
    )

  def max(self, center: Coordinate) -> Coordinate:
    return Coordinate(
      self.min(center).x+self.size.width,
      self.min(center).y+self.size.height,
    )

  def hit(self, center: Coordinate, other: Self, other_center: Coordinate) -> bool:
    if other.min(other_center).x <= self.min(center).x <= other.max(other_center).x:
      if other.min(other_center).y <= self.min(center).y <= other.max(other_center).y:
        return True

    if other.min(other_center).x <= self.max(center).x <= other.max(other_center).x:
      if other.min(other_center).y <= self.max(center).y <= other.max(other_center).y:
        return True

    return False


class Block:
  def __init__(self, image: Image, collision: Collision) -> None:
    self.image = image
    self.collision = collision


TSprite = TypeVar('TSprite', bound='Sprite')


class Sprite(Scribe):
  def __init__(self, motions: dict[int, Block]) -> None:
    self.id = str(uuid())
    self.motions = motions
    self.motion = list(self.motions.keys())[0]
    self.center = Coordinate(0, 0)

  @property
  def block(self) -> Block:
    return self.motions[self.motion]

  @property
  def origin(self) -> Coordinate:
    return Coordinate(
      self.center.x-self.block.collision.size.width/2,
      self.center.y-self.block.collision.size.height/2,
    )

  @origin.setter
  def origin(self, value: Coordinate) -> None:
    self.center = Coordinate(value.x+self.size.width/2, value.y+self.size.height/2)

  @property
  def size(self) -> Size:
    return self.block.collision.size

  @property
  def left(self) -> float:
    return self.origin.x

  @property
  def right(self) -> float:
    return self.left+self.size.width

  @property
  def top(self) -> float:
    return self.origin.y

  @property
  def bottom(self) -> float:
    return self.top+self.size.height

  def draw(self, transparent_color: int) -> None:
    pyxel.blt(
      self.center.x-self.block.image.size.width/2,
      self.center.y-self.block.image.size.height/2,
      self.block.image.id,
      self.block.image.origin.x,
      self.block.image.origin.y,
      self.block.image.copy_vector.width,
      self.block.image.copy_vector.height,
      transparent_color,
    )

  def hit(self, other: TSprite) -> bool:
    return self.block.collision.hit(self.center, other.block.collision, other.center)


class Obstacle:
  def __init__(self, figure: int, collision: Collision) -> None:
    self.figure = figure
    self.collision = collision


class Field(Scribe):
  def __init__(self, background_tiles: list[TileMap], obstacles: list[Obstacle], max_size: Size) -> None:
    self.background_tiles = background_tiles
    self.obstacles = obstacles
    self.max_size = max_size
    self.scroll_pos = Coordinate(0, 0)

  def draw(self, transparent_color: int) -> None:
    pos = Coordinate(0, 0)
    distance = Coordinate(0, 0)
    for tile in self.background_tiles:
      if self.scroll_pos.x <= distance.x and self.scroll_pos.y <= distance.y:
        pyxel.bltm(
          pos.x,
          pos.y,
          tile.id,
          tile.origin.x,
          tile.origin.y,
          tile.copy_vector.width,
          tile.copy_vector.height,
          transparent_color,
        )
        pos = Coordinate(pos.x+tile.size.width, pos.y)
      distance = Coordinate(distance.x+tile.size.width, distance.y)


class Text(Scribe):
  def __init__(self, text: str, text_color: int) -> None:
    self.text = text
    self.text_color = text_color
    self.center = Coordinate(0, 0)

  @classmethod
  def word_size(cls) -> int:
    return 4

  @property
  def size(self) -> Size:
    return Size(len(self.text)*Text.word_size(), Text.word_size())

  @property
  def origin(self) -> Coordinate:
    return Coordinate(self.center.x-self.size.width/2, self.center.y-self.size.height/2)

  @origin.setter
  def origin(self, value: Coordinate) -> None:
    self.center = Coordinate(value.x+self.size.width/2, value.y+self.size.height/2)

  def draw(self, transparent_color: int) -> None:
    pyxel.text(self.origin.x, self.origin.y, self.text, self.text_color)


class Signboard(Scribe):
  def __init__(self, image: Image, texts: list[Text]) -> None:
    self.image = image
    self.center = Coordinate(0, 0)
    self.texts = texts

  @property
  def origin(self) -> Coordinate:
    return Coordinate(self.center.x-self.image.size.width/2, self.center.y-self.image.size.height/2)

  @origin.setter
  def origin(self, value: Coordinate) -> None:
    self.center = Coordinate(value.x+self.image.size.width/2, value.y+self.image.size.height/2)

  def draw(self, transparent_color: int) -> None:
    pyxel.blt(
      self.origin.x,
      self.origin.y,
      self.image.id,
      self.image.origin.x,
      self.image.origin.y,
      self.image.copy_vector.width,
      self.image.copy_vector.height,
      transparent_color,
    )

    for text in self.texts:
      text.draw(transparent_color)


class GamePad:
  @classmethod
  def press(cls, keys: list[int]) -> bool:
    for key in keys:
      if pyxel.btnp(key):
        return True

    return False


class MusicBox:
  def __init__(self, music: Music) -> None:
    self.music = music

  def play(self) -> None:
    pass
