from typing import Any, Self, TypeVar
from uuid import uuid4 as uuid
from game import (
  Coordinate, Size, Stopwatch, Timer,
  Image, TileMap, SoundEffect, AssetSound, AssetBgm, Bgm, RawBgm,
)
import pyxel
import PyxelUniversalFont as puf


class Variation:
  def update(self, stopwatch: Stopwatch, snapshot: Any) -> None:
    raise RuntimeError()


class Subject:
  def draw(self, transparent_color: int) -> None:
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
  def __init__(
    self,
    name: str,
    motions: dict[int, Block],
    sounds: dict[int, int],
    stopwatch: Stopwatch,
  ) -> None:
    self.id = '{}_{}'.format(name, str(uuid()))
    self.motions = motions
    self.sounds = sounds
    self.elapsed_timer = Timer(stopwatch)

    self.motion = list(self.motions.keys())[0]
    self.center = Coordinate(0, 0)

  @property
  def elapsed_msec(self) -> int:
    return self.elapsed_timer.msec

  def pause(self) -> None:
    self.elapsed_timer.pause()

  def resume(self) -> None:
    self.elapsed_timer.resume()

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

  def draw(self, transparent_color: int) -> None:
    pyxel.blt(
      x=self.center.x-self.block.image.size.width/2,
      y=self.center.y-self.block.image.size.height/2,
      img=self.block.image.id,
      u=self.block.image.origin.x,
      v=self.block.image.origin.y,
      w=self.block.image.copy_vector.width,
      h=self.block.image.copy_vector.height,
      colkey=transparent_color,
    )

  def hit(self, other: TSprite) -> bool:
    return self.block.collision.hit(self.center, other.block.collision, other.center)


class FlashSprite(Sprite):
  def __init__(
    self,
    name: str,
    motions: dict[int, Block],
    sounds: dict[int, int],
    stopwatch: Stopwatch,
    flash_msec: int,
    max_flash_count: int,
  ) -> None:
    super().__init__(
      name=name,
      motions=motions,
      sounds=sounds,
      stopwatch=stopwatch,
    )

    self.flash_timer = Timer.set_msec(stopwatch, flash_msec, False)
    self.max_flash_count = max_flash_count

    self.flashing = False
    self.flash_count = 0
    self.show = True

  def flash(self) -> None:
    self.flash_timer.resume()
    self.flashing = True
    self.show = False

  def update(self, stopwatch: Stopwatch, snapshot: Any) -> None:
    if self.flashing:
      if self.flash_count >= self.max_flash_count:
        self.flashing = False
        self.flash_count = 0
        self.show = True
      else:
        if self.flash_timer.over:
          self.flash_timer.reset()
          self.show = not self.show
          if self.show:
            self.flash_count += 1

  def draw(self, transparent_color: int) -> None:
    if self.show:
      super().draw(transparent_color)


class Obstacle:
  def __init__(self, collision: Collision) -> None:
    self.collision = collision


class Field(Variation, Subject):
  def __init__(
    self,
    name: str,
    backgrounds: list[TileMap],
    obstacles: list[Obstacle],
    max_size: Size,
  ) -> None:
    self.id = '{}_{}'.format(name, str(uuid()))
    self.backgrounds = backgrounds
    self.obstacles = obstacles
    self.max_size = max_size
    self.scroll_pos = Coordinate(0, 0)

  def draw(self, transparent_color: int) -> None:
    pos = Coordinate(0, 0)
    distance = Coordinate(0, 0)
    for background in self.backgrounds:
      if self.scroll_pos.x <= distance.x and self.scroll_pos.y <= distance.y:
        pyxel.bltm(
          x=pos.x,
          y=pos.y,
          tm=background.id,
          u=background.origin.x,
          v=background.origin.y,
          w=background.copy_vector.width,
          h=background.copy_vector.height,
          colkey=transparent_color,
        )
        pos = Coordinate(pos.x+background.size.width, pos.y)
      distance = Coordinate(distance.x+background.size.width, distance.y)


class Movable(Variation):
  def __init__(self) -> None:
    self.center = Coordinate(0, 0)
    self.move_center: Coordinate | None = None
    self.move_distance = 1.0

  @property
  def moving(self) -> bool:
    return self.move_center is not None

  def move(self, center: Coordinate, move_distance: float) -> None:
    self.move_center = center
    self.move_distance = move_distance

  def update(self, stopwatch: Stopwatch, snapshot: Any) -> None:
    if self.move_center is not None:
      distance_x = self.center.x - self.move_center.x
      if distance_x != 0:
        if abs(distance_x) < self.move_distance:
          distance_x = self.move_distance if distance_x >= 0 else self.move_distance*-1
        else:
          distance_x = self.move_distance

      distance_y = self.center.y - self.move_center.y
      if distance_y != 0:
        if abs(distance_y) < self.move_distance:
          distance_y = self.move_distance if distance_y >= 0 else self.move_distance*-1
        else:
          distance_y = self.move_distance

      self.center = Coordinate(self.center.x+distance_x, self.center.y+distance_y)

      if self.center.x == self.move_center.x and self.center.y == self.move_center.y:
        self.move_center = None


class TextScriber:
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
  
  
class Text(Subject, Movable):
  def __init__(self, string: str, text_color: int, font_size: int, bold: bool) -> None:
    super().__init__()

    if string == '':
      raise RuntimeError()

    self.string = string
    self.text_color = text_color
    self.font_size = font_size
    self.bold = bold

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

  def draw(self, transparent_color: int) -> None:
    TextScriber().writer(self.font_size,self.bold).draw(
      x=self.origin.x,
      y=self.origin.y,
      text=self.string.upper(),
      font_size=self.font_size,
      font_color=self.text_color,
    )


class BlinkText(Text):
  def __init__(
    self,
    string: str,
    text_color: int,
    font_size: int,
    bold: bool,
    stopwatch: Stopwatch,
    blink_msec: int,
    show: bool,
  ) -> None:
    super().__init__(
      string=string,
      text_color=text_color,
      font_size=font_size,
      bold=bold,
    )

    self.blink_timer = Timer.set_msec(stopwatch, blink_msec, False)
    self.show = show

  def update_blink_msec(self, blink_msec: int, show: bool) -> None:
    self.blink_timer.limit_msec = blink_msec
    self.blink_timer.reset()
    self.show = show

  def pause(self) -> None:
    self.blink_timer.pause()

  def resume(self) -> None:
    self.blink_timer.resume()
    
  def update(self, stopwatch: Stopwatch, snapshot: Any) -> None:
    if self.blink_timer.over:
      self.blink_timer.reset()
      self.show = not self.show

    super().update(stopwatch, snapshot)

  def draw(self, transparent_color: int) -> None:
    if self.show:
      super().draw(transparent_color)


class Poster:
  def __init__(self, image: Image, origin: Coordinate) -> None:
    self.image = image
    self.origin = origin


class Signboard(Subject, Movable):
  def __init__(
    self,
    posters: list[Poster],
    texts: list[Text],
    width: float | None,
    height: float | None,
  ) -> None:
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

  def draw(self, transparent_color: int) -> None:
    for poster in self.posters:
      pyxel.blt(
        x=poster.origin.x+self.origin.x,
        y=poster.origin.y+self.origin.y,
        img=poster.image.id,
        u=poster.image.origin.x,
        v=poster.image.origin.y,
        w=poster.image.copy_vector.width,
        h=poster.image.copy_vector.height,
        colkey=transparent_color,
      )
    for text in self.texts:
      draw_text = Text(text.string, text.text_color, text.font_size, text.bold)
      draw_text.origin = Coordinate(self.origin.x+text.origin.x, self.origin.y+text.origin.y)
      draw_text.draw(transparent_color)


class GamePad:
  def __init__(self, watch_buttons: dict[int, list[int]]) -> None:
    self.watch_buttons: dict[int, list[int]] = watch_buttons

  def push(self, button: int) -> bool:
    for key in self.watch_buttons[button]:
      if pyxel.btnp(key):
        return True

    return False

  def pushing(self, button: int) -> bool:
    for key in self.watch_buttons[button]:
      if pyxel.btn(key):
        return True

    return False


class MusicBox:
  def __init__(self, bgm_param: Bgm.Param | None, raw_bgm_param: RawBgm.Param | None) -> None:
    self.bgm_param = bgm_param
    self.raw_bgm_param = raw_bgm_param

    self.can_play_se = True
    self.can_play_bgm = True
    self.bgm: AssetBgm | None = None

  def play_se(self, id: int) -> None:
    if not self.can_play_se:
      print('sound effect disabled', id)
      return

    play_channel = -1
    for channel in reversed(range(AssetSound.channel_count())):
      if self.bgm is not None:
        if channel in self.bgm.channels:
          continue

      if pyxel.play_pos(channel) is not None:
        continue

      play_channel = channel
      break

    if play_channel < 0:
      play_channel = AssetSound.channel_count()-1
      print('sound effect no enable channel', play_channel)
    SoundEffect(play_channel, id).play()
      

  def play_bgm(self, id: int) -> None:
    if not self.can_play_bgm or self.bgm_param is None:
      print('bgm disabled', id)
      return

    if self.bgm is not None:
      if self.bgm.name == Bgm.setup_name(id):
        print('bgm play already', self.bgm.name)
        return

      self.bgm.stop()

    self.bgm = Bgm(id, self.bgm_param)
    self.bgm.play()

  def play_raw_bgm(self, filename: str) -> None:
    if not self.can_play_bgm or self.raw_bgm_param is None:
      print('bgm disabled', filename)
      return

    if self.bgm is not None:
      if self.bgm.name == RawBgm.setup_name(filename):
        print('raw bgm play already', self.bgm.name)
        return

      self.bgm.stop()

    self.bgm = RawBgm(filename, self.raw_bgm_param)
    self.bgm.play()

  def stop_bgm(self) -> None:
    if self.bgm is not None:
      self.bgm.stop()
    self.bgm = None
