from datetime import datetime
from enum import IntEnum
from typing import Any, Self
from game import (
  Coordinate, Size,
  TileMap,
  Sprite, Block, Obstacle, Field as BaseField, Text, GamePad as BaseGamePad,
  GameProfile, Language, StringRes, Timer, Stopwatch, Snapshot as BaseSnapshot, Scene as BaseScene,
)
import pyxel


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
    STAND_BY = 2
    JUMP = 3
    FALL_DOWN = 4
    JOY = 5

  JOY_MAX = 3

  def __init__(self, motions: dict[int, Block]) -> None:
    super().__init__(motions)
    self.action = self.Action.STOP
    self.walking_x = 0.0
    self.accel_y = 0.0
    self.prev_y = 0.0
    self.joying_count = 0

  def reset(self) -> None:
    self.walking_x = 0.0
    self.accel_y = 0.0
    self.prev_y = 0.0
    self.joying_count = 0

  @property
  def walking_distance(self) -> float:
    return 1

  @property
  def max_accel(self) -> int:
    return -10

  @property
  def stopping(self) -> bool:
    return self.action == self.Action.STOP

  @property
  def walking(self) -> bool:
    return self.action == self.Action.WALK

  @property
  def standing_by(self) -> bool:
    return self.action == self.Action.STAND_BY

  @property
  def jumping(self) -> bool:
    return self.action == self.Action.JUMP

  @property
  def falling_down(self) -> bool:
    return self.action == self.Action.FALL_DOWN

  @property
  def joying(self) -> bool:
    return self.action == self.Action.JUMP

  def stop(self) -> None:
    self.action = self.Action.STOP
    self.reset()

  def walk(self, x: float) -> None:
    if self.stopping:
      self.action = self.Action.WALK
      self.reset()

  def stand_by(self) -> None:
    if self.stopping:
      self.action = self.Action.STAND_BY
      self.reset()

  def jump(self) -> None:
    if self.standing_by:
      self.action = self.Action.JUMP
      self.reset()
      self.accel_y = self.max_accel
      self.prev_y = self.center.y

  def fall_down(self) -> None:
    if self.standing_by or self.jumping:
      self.action = self.Action.FALL_DOWN
      self.reset()

  def joy(self) -> None:
    if self.stopping:
      self.action = self.Action.JOY
      self.reset()
      self.accel_y = self.max_accel
      self.prev_y = self.center.y

  def update(self, game_pad: GamePad, field: Field) -> None:
    if self.walking:
      distance = self.walking_distance
      diff = self.origin.x - self.walking_x
      if abs(diff) < distance:
        distance = diff
      else:
        if diff > 0:
          distance *= -1
      self.origin = Coordinate(self.origin.x+distance, self.origin.y)

      if self.origin.x == self.walking_x:
        self.action = self.Action.STOP
        self.reset()

    elif self.jumping:
      if self.bottom < field.bottom or self.accel_y == self.max_accel:
        center_y = self.center.y
        self.center.y += (self.center.y - self.prev_y) + self.accel_y
        self.prev_y = center_y
        self.accel_y = 1
      else:
        self.action = self.Action.STAND_BY
        self.reset()

    elif self.joying:
      if self.bottom < field.bottom or self.accel_y == self.max_accel:
        center_y = self.center.y
        self.center.y += (self.center.y - self.prev_y) + self.accel_y
        self.prev_y = center_y
        self.accel_y = 1
      else:
        self.joying_count += 1
        if self.joying_count > self.JOY_MAX:
          self.action = self.Action.STOP
          self.reset()
        else:
          self.accel_y = self.max_accel
          self.prev_y = self.center.y


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
  def rolling_distance(self) -> float:
    raise RuntimeError()

  @property
  def stopping(self) -> bool:
    return self.action == self.Action.STOP

  @property
  def rolling(self) -> bool:
    return self.action == self.Action.ROLL

  @property
  def breaking(self) -> bool:
    return self.action == self.Action.BREAK

  def stop(self) -> None:
    if self.rolling:
      self.action = self.Action.STOP

  def roll(self) -> None:
    if self.stopping:
      self.action = self.Action.ROLL

  def update(self, field: Field) -> None:
      raise RuntimeError()


class BlinkText(Text):
  def __init__(self, string: str, text_color: int, stopwatch: Stopwatch, msec: int, show: bool) -> None:
    super().__init__(string, text_color)
    self.timer = Timer.set_msec(stopwatch, msec, True)
    self.show = show

  def set_msec(self, msec: int, show: bool) -> None:
    self.timer = Timer.set_msec(self.timer.stopwatch, msec, True)
    self.show = show

  def update(self) -> None:
    if self.timer.over:
      self.show = not self.show
      self.timer.reset()

  def draw(self, transparent_color: int) -> None:
    if self.show:
      super().draw(transparent_color)


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
  def __init__(
    self,
    profile: GameProfile,
    string_res: StringRes,
    stopwatch: Stopwatch,
    snapshot: Snapshot,
  ) -> None:
    super().__init__(profile, string_res, stopwatch, snapshot)

  def string(self, key: str) -> str:
    return self.string_res.string(key, self.snapshot.lang)

  @property
  def can_update_sprite(self) -> bool:
    return True

  def update(self) -> Self | Any:
    if self.can_update_sprite:
      for ball in self.snapshot.balls:
        ball.update(self.snapshot.field)
      self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)
    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    return []

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)
    for subject in self.drawing_subjects:
      subject.draw(transparent_color)
