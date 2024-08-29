from typing import Any, Self, TypeVar
from uuid import uuid4 as uuid
from game import (
  Coordinate, Size, Stopwatch,
  Image, TileMap, SoundEffect, Music,
)
import pyxel
import PyxelUniversalFont as puf


class Variation:
  def update(self, stopwatch: Stopwatch, snapshot: Any) -> None:
    raise RuntimeError()


class Subject:
  def draw(self) -> None:
    raise RuntimeError()


class Collision:
  def __init__(self, origin: Coordinate, size: Size) -> None:
    self.origin = origin
    self.size = size

  @property
  def left(self) -> float:
    return self.origin.x

  @property
  def right(self) -> float:
    return self.origin.x+self.size.width

  @property
  def top(self) -> float:
    return self.origin.y

  @property
  def bottom(self) -> float:
    return self.origin.y+self.size.height

  def min(self, center: Coordinate) -> Coordinate:
    return Coordinate(center.x-self.size.width/2+self.origin.x, center.y-self.size.height/2+self.origin.y)

  def max(self, center: Coordinate) -> Coordinate:
    return Coordinate(self.min(center).x+self.size.width, self.min(center).y+self.size.height)

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

class Sprite(Variation, Subject):
  def __init__(self, motions: dict[int, Block], sounds: dict[int, SoundEffect]) -> None:
    self.motions = motions
    self.sounds = sounds

    self.id = str(uuid())
    self.motion = list(self.motions.keys())[0]
    self.center = Coordinate(0, 0)

  @property
  def block(self) -> Block:
    return self.motions[self.motion]

  @property
  def origin(self) -> Coordinate:
    return Coordinate(self.center.x-self.block.collision.size.width/2, self.center.y-self.block.collision.size.height/2)

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

  def draw(self) -> None:
    pyxel.blt(
      self.center.x-self.block.image.size.width/2,
      self.center.y-self.block.image.size.height/2,
      self.block.image.id,
      self.block.image.origin.x,
      self.block.image.origin.y,
      self.block.image.copy_vector.width,
      self.block.image.copy_vector.height,
      self.block.image.transparent_color,
    )

  def hit(self, other: TSprite) -> bool:
    return self.block.collision.hit(self.center, other.block.collision, other.center)


class FlashSprite(Sprite):
  def __init__(
    self,
    motions: dict[int, Block],
    sounds: dict[int, SoundEffect],
    flash_period: int,
    max_flash_count: int,
  ) -> None:
    super().__init__(motions, sounds)

    self.flash_period = flash_period
    self.max_flash_count = max_flash_count

    self.flashing_interval = 0
    self.flashing = False
    self.show = True

  def flash(self) -> None:
    self.flashing_interval = 0
    self.flashing = True
    self.show = False

  def update(self, stopwatch: Stopwatch, snapshot: Any) -> None:
    if self.flashing:
      self.flashing_interval += 1
      if self.flashing_interval >= self.max_flash_count:
        self.flashing_interval = 0
        self.flashing = False
        self.show = True
      else:
        if self.flashing_interval%self.flash_period == 0:
          self.show = not self.show

  def draw(self) -> None:
    if self.show:
      super().draw()


class Obstacle:
  def __init__(self, collision: Collision) -> None:
    self.collision = collision


class Field(Variation, Subject):
  def __init__(self, backgrounds: list[TileMap], obstacles: list[Obstacle], max_size: Size) -> None:
    self.backgrounds = backgrounds
    self.obstacles = obstacles
    self.max_size = max_size
    self.scroll_pos = Coordinate(0, 0)

  def draw(self) -> None:
    pos = Coordinate(0, 0)
    distance = Coordinate(0, 0)
    for background in self.backgrounds:
      if self.scroll_pos.x <= distance.x and self.scroll_pos.y <= distance.y:
        pyxel.bltm(
          pos.x,
          pos.y,
          background.id,
          background.origin.x,
          background.origin.y,
          background.copy_vector.width,
          background.copy_vector.height,
          background.transparent_color,
        )
        pos = Coordinate(pos.x+background.size.width, pos.y)
      distance = Coordinate(distance.x+background.size.width, distance.y)


class Movable(Variation):
  def __init__(self) -> None:
    self.center = Coordinate(0, 0)
    self.moved_center: Coordinate | None = None
    self.moving_distance = 1.0

  @property
  def moving(self) -> bool:
    return self.moved_center is not None

  def move(self, center: Coordinate, moving_distance: float) -> None:
    self.moved_center = center
    self.moving_distance = moving_distance

  def update(self, stopwatch: Stopwatch, snapshot: Any) -> None:
    if self.moved_center is not None:
      distance_x = self.center.x - self.moved_center.x
      if distance_x != 0:
        if abs(distance_x) < self.moving_distance:
          distance_x = self.moving_distance if distance_x >= 0 else self.moving_distance*-1
        else:
          distance_x = self.moving_distance

      distance_y = self.center.y - self.moved_center.y
      if distance_y != 0:
        if abs(distance_y) < self.moving_distance:
          distance_y = self.moving_distance if distance_y >= 0 else self.moving_distance*-1
        else:
          distance_y = self.moving_distance

      self.center = Coordinate(self.center.x+distance_x, self.center.y+distance_y)

      if self.center.x == self.moved_center.x and self.center.y == self.moved_center.y:
        self.moved_center = None


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

  def __init__(self) -> None:
    self.writers: dict[str, puf.Writer] = {}

  @classmethod
  def word_size(cls, font_size: int) -> Size:
    return Size(font_size/2, font_size)

  def writer(self, font_size: int, bold: bool) -> puf.Writer:
    font = self.CUSTOM_FONT_FILES[font_size][bold]
    if font not in puf.get_available_fonts():
      font = self.DEFAULT_FONT_FILE

    if font not in self.writers:
      writer = puf.Writer(font)
      print('new font', font, writer)
      self.writers[font] = writer

    return self.writers[font]


class Text(Subject, Movable):
  def __init__(self, string: str, text_color: int, font_size: int, bold: bool, scriber: TextScriber) -> None:
    super().__init__()

    if string == '':
      raise RuntimeError()

    self.string = string
    self.text_color = text_color
    self.font_size = font_size
    self.bold = bold
    self.scriber = scriber

  @property
  def size(self) -> Size:
    return Size(
      len(self.string)*TextScriber.word_size(self.font_size).width,
      TextScriber.word_size(self.font_size).height,
    )

  @property
  def origin(self) -> Coordinate:
    return Coordinate(self.center.x-self.size.width/2, self.center.y-self.size.height/2)

  @origin.setter
  def origin(self, value: Coordinate) -> None:
    self.center = Coordinate(value.x+self.size.width/2, value.y+self.size.height/2)

  def draw(self) -> None:
    self.scriber.writer(
      self.font_size,
      self.bold,
    ).draw(
      self.origin.x,
      self.origin.y,
      self.string.upper(),
      self.font_size,
      self.text_color,
    )


class BlinkText(Text):
  def __init__(
    self,
    string: str,
    text_color: int,
    font_size: int,
    bold: bool,
    scriber: TextScriber,
    blink_period: int,
    show: bool,
  ) -> None:
    super().__init__(string, text_color, font_size, bold, scriber)

    self.blink_period = blink_period
    self.show = show

    self.blinking_interval = 0

  def update_blink_period(self, blink_period: int, show: bool) -> None:
    self.blink_period = blink_period
    self.show = show
    self.blinking_interval = 0

  def update(self, stopwatch: Stopwatch, snapshot: Any) -> None:
    self.blinking_interval += 1
    if self.blinking_interval%self.blink_period == 0:
      self.show = not self.show

    super().update(stopwatch, snapshot)

  def draw(self) -> None:
    if self.show:
      super().draw()


class SignboardPoster:
  def __init__(self, image: Image, origin: Coordinate) -> None:
    self.image = image
    self.origin = origin


class Signboard(Subject, Movable):
  def __init__(self, posters: list[SignboardPoster], texts: list[Text], width: float | None, height: float | None) -> None:
    super().__init__()

    if len(posters) == 0 and len(texts) == 0:
      raise RuntimeError()

    self.posters = posters
    self.texts = texts

    max_width = 0.0
    if width is not None:
      max_width = width
    else:
      if len(self.texts) > 0:
        max_width = max([text.origin.x+text.size.width for text in self.texts])
      elif len(self.posters) > 0:
        max_width = max([poster.origin.x+poster.image.size.width for poster in self.posters])

    max_height = 0.0
    if height is not None:
      max_height = height
    else:
      if len(self.texts) > 0:
        max_height = max([text.origin.y+text.size.height for text in self.texts])
      elif len(self.posters) > 0:
        max_height = max([poster.origin.y+poster.image.size.height for poster in self.posters])

    self.size = Size(max_width, max_height)

  @property
  def origin(self) -> Coordinate:
    return Coordinate(self.center.x-self.size.width/2, self.center.y-self.size.height/2)

  @origin.setter
  def origin(self, value: Coordinate) -> None:
    self.center = Coordinate(value.x+self.size.width/2, value.y+self.size.height/2)

  def draw(self) -> None:
    for poster in self.posters:
      pyxel.blt(
        poster.origin.x+self.origin.x,
        poster.origin.y+self.origin.y,
        poster.image.id,
        poster.image.origin.x,
        poster.image.origin.y,
        poster.image.copy_vector.width,
        poster.image.copy_vector.height,
        poster.image.transparent_color,
      )
    for text in self.texts:
      draw_text = Text(text.string, text.text_color, text.font_size, text.bold, text.scriber)
      draw_text.origin = Coordinate(self.origin.x+text.origin.x, self.origin.y+text.origin.y)
      draw_text.draw()


class GamePad:
  def __init__(self, watching_buttons: dict[int, list[int]]) -> None:
    self.watching_buttons: dict[int, list[int]] = watching_buttons

  def push(self, button: int) -> bool:
    for key in self.watching_buttons[button]:
      if pyxel.btnp(key):
        return True

    return False

  def pushing(self, button: int) -> bool:
    for key in self.watching_buttons[button]:
      if pyxel.btn(key):
        return True

    return False


class MusicBox:
  def __init__(self) -> None:
    self.music: Music | None = None

  def play(self, music: Music) -> None:
    if self.music is not None:
      self.music.stop()

    self.music = music
    self.music.play()

  def stop(self) -> None:
    if self.music is not None:
      self.music.stop()
