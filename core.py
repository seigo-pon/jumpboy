from enum import IntEnum
from typing import Any, Self
from game import (
  Coordinate,
  TileMap,
  Sprite, Field as BaseField, GamePad as BaseGamePad,
  Timer, Snapshot as BaseSnapshot, Scene as BaseScene,
)
import pyxel

from game.component import Block, Obstacle
from game.utils import Size


class GamePad(BaseGamePad):
  def __init__(self) -> None:
    super().__init__()
    self.enter_keys = [
      pyxel.KEY_RETURN,
      pyxel.MOUSE_BUTTON_LEFT,
      pyxel.GAMEPAD1_BUTTON_A,
    ]
    self.cancel_keys = [
      pyxel.KEY_SPACE,
      pyxel.MOUSE_BUTTON_RIGHT,
      pyxel.GAMEPAD1_BUTTON_B,
    ]

  def enter(self) -> bool:
    return self.press(self.enter_keys)

  def cancel(self) -> bool:
    return self.press(self.cancel_keys)

class Score:
  def __init__(self) -> None:
    self.point = 0


class Field(BaseField):
  def __init__(self, background_tiles: list[TileMap], obstacles: list[Obstacle], max_size: Size, ground_top: int) -> None:
    super().__init__(background_tiles, obstacles, max_size)
    self.ground_top = ground_top

  @property
  def left(self) -> float:
    return -self.scroll_pos.x

  @property
  def right(self) -> float:
    return self.max_size.width-self.scroll_pos.x

  @property
  def top(self) -> float:
    return -self.scroll_pos.y

  @property
  def bottom(self) -> float:
    return self.ground_top-self.scroll_pos.y


class Jumper(Sprite):
  class Action(IntEnum):
    STOP = 0
    WALK = 1
    STANDBY = 2
    JUMP = 3
    DOWN = 4

  def __init__(self, motions: dict[int, Block]) -> None:
    super().__init__(motions)
    self.action = self.Action.STOP
    self.walking_x = 0.0

  @property
  def walking_distance_min(self) -> float:
    return 1

  def stop(self) -> None:
    if self.Action.WALK <= self.action <= self.Action.JUMP:
      self.action = self.Action.STOP
      self.walking_x = 0

  def walk(self, x: float) -> None:
    if self.action == self.Action.STOP:
      self.action = self.Action.WALK
      self.walking_x = x

  def standby(self) -> None:
    if self.action == self.Action.STOP:
      self.action = self.Action.STANDBY
      self.walking_x = 0

  def down(self) -> None:
    if self.Action.STANDBY <= self.action <= self.Action.JUMP:
      self.action = self.Action.DOWN
      self.walking_x = 0

  def update(self, game_pad: GamePad, field: Field) -> None:
    if self.action == self.Action.WALK:
      distance = self.walking_distance_min
      diff = self.origin.x - self.walking_x
      if abs(diff) < distance:
        distance = diff
      else:
        if diff > 0:
          distance *= -1
      self.origin = Coordinate(self.origin.x+distance, self.origin.y)

      if self.origin.x == self.walking_x:
        self.action = self.Action.STOP
        self.walking_x


class Ball(Sprite):
  class Action(IntEnum):
    STOP = 0
    ROLL = 1
    BREAK = 2

  def __init__(self, motions: dict[int, Block]) -> None:
    super().__init__(motions)
    self.action = self.Action.STOP
    self.rolling_direction = True

  @property
  def rolling_distance_min(self) -> float:
    raise Exception()

  @property
  def rolling_distance(self) -> float:
    return self.rolling_distance_min * (1 if self.rolling_direction else -1)

  def stop(self) -> None:
    if self.action == self.Action.ROLL:
      self.action = self.Action.STOP

  def roll(self) -> None:
    if self.action == self.Action.STOP:
      self.action = self.Action.ROLL

  def update(self, field: Field) -> None:
      pass


class Snapshot(BaseSnapshot):
  def __init__(
    self,
    game_pad: GamePad,
    score: Score,
    level :int,
    stage: int,
    field: Field,
    balls: list[Ball],
    jumper: Jumper,
  ) -> None:
    super().__init__()
    self.game_pad = game_pad
    self.score = score
    self.level = level
    self.stage = stage
    self.field = field
    self.balls = balls
    self.jumper = jumper
    self.playing_timer: Timer | None = None


class Scene(BaseScene[Snapshot]):
  def update(self) -> Self | Any:
    self.stopwatch.update()

    for ball in self.snapshot.balls:
      ball.update(self.snapshot.field)

    self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)

    return self

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    self.snapshot.field.draw(transparent_color)

    for ball in self.snapshot.balls:
      ball.draw(transparent_color)

    self.snapshot.jumper.draw(transparent_color)
