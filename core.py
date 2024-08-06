from datetime import datetime
from enum import IntEnum
from typing import Any, Self
from game import (
  Coordinate,
  TileMap,
  Sprite, Field as BaseField, GamePad as BaseGamePad,
  Language, Snapshot as BaseSnapshot, Scene as BaseScene,
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
    return GamePad.press(self.enter_keys)

  def cancel(self) -> bool:
    return GamePad.press(self.cancel_keys)


class Score:
  def __init__(self, created_at: datetime, level: int, stage: int, point: int) -> None:
    self.created_at = created_at
    self.level = level
    self.stage = stage
    self.point = 0


class ScoreBoard:
  def __init__(self) -> None:
    self.scores: list[Score] = []

  def ranking(self, num: int) -> list[Score]:
    return sorted(self.scores, key=lambda x: (x.point, x.created_at), reverse=True)[:num]


class Field(BaseField):
  def __init__(
    self,
    background_tiles: list[TileMap],
    obstacles: list[Obstacle],
    max_size: Size,
    ground_top: float,
  ) -> None:
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
  def walking_distance_abs(self) -> float:
    return 1

  def stop(self) -> None:
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
      distance = self.walking_distance_abs
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
  def rolling_distance_abs(self) -> float:
    raise RuntimeError()

  @property
  def rolling_distance(self) -> float:
    return self.rolling_distance_abs * (1 if self.rolling_direction else -1)

  def stop(self) -> None:
    if self.action == self.Action.ROLL:
      self.action = self.Action.STOP

  def roll(self) -> None:
    if self.action == self.Action.STOP:
      self.action = self.Action.ROLL

  def update(self, field: Field) -> None:
      raise RuntimeError()


class Snapshot(BaseSnapshot):
  def __init__(
    self,
    lang: Language,
    game_pad: GamePad,
    score_board: ScoreBoard,
    level :int,
    stage: int,
    field: Field,
    balls: list[Ball],
    jumper: Jumper,
  ) -> None:
    super().__init__()
    self.lang = lang
    self.game_pad = game_pad
    self.score_board = score_board
    self.level = level
    self.stage = stage
    self.field = field
    self.balls = balls
    self.jumper = jumper

  def to_json(self) -> dict:
    return {
      'score_board': [{
        'created_at': score.created_at.timestamp(),
        'level': score.level,
        'stage': score.stage,
        'point': score.point,
      } for score in self.score_board.scores],
      'level': self.level,
      'stage': self.stage,
    }

  def from_json(self, data: dict) -> None:
    if 'score_board' in data:
      scores = []
      for score in data['score_board']:
        scores.append(
          Score(
            datetime.fromtimestamp(score['created_at']),
            score['level'],
            score['stage'],
            score['point'],
          )
        )
      self.score_board.scores = scores
    if 'level' in data:
      self.level = data['level']
    if 'stage' in data:
      self.stage = data['stage']


class Scene(BaseScene[Snapshot]):
  def string(self, key: str) -> str:
    return self.string_res.string(key, self.snapshot.lang)

  def update(self) -> Self | Any:
    self.stopwatch.update()
    return self

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    self.snapshot.field.draw(transparent_color)
    for ball in self.snapshot.balls:
      ball.draw(transparent_color)
    self.snapshot.jumper.draw(transparent_color)
