from datetime import datetime
from enum import IntEnum
from typing import Any, Self, TypeVar
from game import (
  Coordinate, Size,
  TileMap,
  Sprite, Block, Obstacle, Field as BaseField, Text, GamePad as BaseGamePad,
  GameConfig, Language, StringRes, Timer, Stopwatch, Snapshot as BaseSnapshot, Scene as BaseScene,
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



class GameLevel:
  def __init__(self, mode: int, stage: int) -> None:
    self.mode = mode
    self.stage = stage


class Score:
  def __init__(self, created_at: datetime, level: GameLevel, point: int) -> None:
    self.created_at = created_at
    self.level = level
    self.point = point


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
    ground_height: float,
  ) -> None:
    super().__init__(background_tiles, obstacles, max_size)
    self.ground_height = ground_height

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
    return self.ground_height-self.scroll_pos.y


TSnapshot = TypeVar('TSnapshot', bound='Snapshot')
class Jumper(Sprite):
  class Action(IntEnum):
    STOP = 0
    WALK = 1
    STAND_BY = 2
    JUMP = 3
    FALL_DOWN = 4
    JOY = 5

  class Motion(IntEnum):
    STOP = 0
    WALK = 1
    JUMP = 2
    FALL_DOWN = 3

  class Param:
    def __init__(
      self,
      max_accel: int,
      walking_distance: float,
      walking_step: int,
      joying_count_max: int,
    ) -> None:
      self.max_accel = max_accel
      self.walking_distance = walking_distance
      self.walking_step = walking_step
      self.joying_count_max = joying_count_max

  def __init__(self, motions: dict[int, Block], param: Param) -> None:
    super().__init__(motions)

    self.param = param

    self.action = self.Action.STOP
    self.walking_x = 0.0
    self.accel_y = 0.0
    self.prev_y = 0.0
    self.joying_count = 0
    self.walking_interval = 0

  def reset(self) -> None:
    self.walking_x = 0.0
    self.accel_y = 0.0
    self.prev_y = 0.0
    self.joying_count = 0
    self.walking_interval = 0

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
    print('jumper stop', self.id)
    self.action = self.Action.STOP
    self.reset()

  def walk(self, x: float) -> None:
    if self.stopping:
      print('jumper walk', self.id, x)
      self.action = self.Action.WALK
      self.reset()
      self.walking_x = x

  def stand_by(self) -> None:
    if self.stopping:
      print('jumper stand by', self.id)
      self.action = self.Action.STAND_BY
      self.reset()

  def jump(self) -> None:
    if self.standing_by:
      print('jumper jump', self.id, self.param.max_accel)
      self.action = self.Action.JUMP
      self.reset()
      self.accel_y = self.param.max_accel
      self.prev_y = self.center.y

  def fall_down(self) -> None:
    if self.standing_by or self.jumping:
      print('jumper fall down', self.id)
      self.action = self.Action.FALL_DOWN
      self.reset()

  def joy(self) -> None:
    if self.stopping:
      print('jumper fall joy', self.id)
      self.action = self.Action.JOY
      self.reset()
      self.accel_y = self.param.max_accel
      self.prev_y = self.center.y

  def update(self, snapshot: TSnapshot) -> None:
    if self.stopping:
      self.motion = self.Motion.STOP

    elif self.walking:
      distance = self.param.walking_distance
      diff = self.origin.x - self.walking_x
      if abs(diff) < distance:
        distance = diff
      else:
        if diff > 0:
          distance *= -1

      self.origin = Coordinate(self.origin.x+distance, self.origin.y)

      if self.origin.x == self.walking_x:
        print('jumper walk to stop', self.id)
        self.action = self.Action.STOP
        self.reset()

      if self.walking_interval < self.param.walking_step:
        self.walking_interval += 1
      else:
        self.walking_interval = 0
        if self.motion == self.Motion.WALK:
          self.motion = self.Motion.STOP
        else:
          self.motion = self.Motion.WALK

    elif self.standing_by:
      self.motion = self.Motion.STOP
      if snapshot.game_pad.enter():
        self.jump()

    elif self.jumping:
      self.motion = self.Motion.JUMP

      if self.bottom < snapshot.field.bottom or self.accel_y == self.param.max_accel:
        center_y = self.center.y
        self.center.y += (self.center.y - self.prev_y) + self.accel_y
        self.prev_y = center_y
        self.accel_y = 1
      else:
        print('jumper jump to stand by', self.id)
        self.action = self.Action.STAND_BY
        self.reset()

    elif self.falling_down:
      self.motion = self.Motion.FALL_DOWN

    elif self.joying:
      if self.bottom < snapshot.field.bottom or self.accel_y == self.param.max_accel:
        center_y = self.center.y
        self.center.y += (self.center.y - self.prev_y) + self.accel_y
        self.prev_y = center_y
        self.accel_y = 1
      else:
        self.joying_count += 1
        if self.joying_count > self.param.joying_count_max:
          print('jumper joy to stop', self.id, self.joying_count, self.param.joying_count_max)
          self.action = self.Action.STOP
          self.reset()
        else:
          print('jumper joy again', self.id, self.joying_count, self.param.joying_count_max)
          self.accel_y = self.param.max_accel
          self.prev_y = self.center.y


class Ball(Sprite):
  class Action(IntEnum):
    STOP = 0
    ROLL = 1
    BREAK = 2

  class Motion(IntEnum):
    ANGLE_0 = 0
    ANGLE_90 = 1
    ANGLE_180 = 2
    ANGLE_270 = 3

  class Param:
    def __init__(self, rolling_distance: float, rolling_step: int, defeat_point: int) -> None:
      self.rolling_distance = rolling_distance
      self.rolling_step = rolling_step
      self.defeat_point = defeat_point

  def __init__(self, motions: dict[int, Block], param: Param) -> None:
    super().__init__(motions)

    self.param = param

    self.action = self.Action.STOP
    self.rolling_direction = True
    self.rolling_interval = 0

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
      print('ball stop')
      self.action = self.Action.STOP

  def roll(self) -> None:
    if self.stopping:
      print('ball roll')
      self.action = self.Action.ROLL

  def update(self, snapshot: TSnapshot) -> None:
    if self.stopping:
      pass

    elif self.rolling:
      next_x = self.origin.x + self.param.rolling_distance * (1 if self.rolling_direction else -1)
      if not self.rolling_direction:
        if next_x <= snapshot.field.left:
          next_x = 0
          self.rolling_direction = True
          print('ball roll direction +', self.id, self.rolling_direction)
      else:
        if next_x+self.size.width >= snapshot.field.right:
          next_x = snapshot.field.right-self.size.width
          self.rolling_direction = False
          print('ball roll direction -', self.id, self.rolling_direction)

      self.origin = Coordinate(next_x, self.origin.y)

      if self.rolling_interval < self.param.rolling_step:
        self.rolling_interval += 1
      else:
        self.rolling_interval = 0
        if self.rolling_direction:
          self.motion += 1
          if self.motion > [e for e in self.Motion][-1]:
            self.motion = [e for e in self.Motion][0]
        else:
          self.motion -= 1
          if self.motion < [e for e in self.Motion][0]:
            self.motion = [e for e in self.Motion][-1]

    elif self.breaking:
      pass


class BlinkText(Text):
  def __init__(self, string: str, text_color: int, stopwatch: Stopwatch, msec: int, show: bool) -> None:
    super().__init__(string, text_color)

    self.timer = Timer.set_msec(stopwatch, msec, True)
    self.show = show

  def set_msec(self, msec: int, show: bool) -> None:
    self.timer = Timer.set_msec(self.timer.stopwatch, msec, True)
    self.show = show

  def update(self, snapshot: TSnapshot) -> None:
    if self.timer.over:
      self.show = not self.show
      self.timer.reset()
      print('blink text update', self.string, self.show)

    super().update(snapshot)

  def draw(self) -> None:
    if self.show:
      super().draw()


class Snapshot(BaseSnapshot):
  def __init__(
    self,
    lang: Language,
    game_pad: GamePad,
    score_board: ScoreBoard,
    level :GameLevel,
    field: Field,
    balls: list[Ball],
    jumper: Jumper,
  ) -> None:
    super().__init__()
    self.lang = lang
    self.game_pad = game_pad
    self.score_board = score_board
    self.level = level
    self.field = field
    self.balls = balls
    self.jumper = jumper

  def to_json(self) -> dict:
    return {
      'score_board': [{
        'created_at': score.created_at.timestamp(),
        'level': score.level.mode,
        'stage': score.level.stage,
        'point': score.point,
      } for score in self.score_board.scores],
      'level': self.level.mode,
      'stage': self.level.stage,
    }

  def from_json(self, data: dict) -> None:
    if 'score_board' in data:
      scores = []
      for score in data['score_board']:
        scores.append(
          Score(
            datetime.fromtimestamp(score['created_at']),
            GameLevel(score['level'], score['stage']),
            score['point'],
          )
        )
      self.score_board.scores = scores

    if 'level' in data and 'stage' in data:
      self.level = GameLevel(data['level'], data['stage'])


class Scene(BaseScene[Snapshot]):
  def __init__(
    self,
    config: GameConfig,
    string_res: StringRes,
    stopwatch: Stopwatch,
    snapshot: Snapshot,
  ) -> None:
    super().__init__(config, string_res, stopwatch, snapshot)

  def string(self, key: str) -> str:
    return self.string_res.string(key, self.snapshot.lang)

  @property
  def updating_variations(self) -> list[Any]:
    variations: list[Any] = self.snapshot.balls
    variations.append(self.snapshot.jumper)
    return variations

  def update(self) -> Self | Any:
    for variation in self.updating_variations:
      variation.update(self.snapshot)
    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    return []

  def draw(self) -> None:
    super().draw()
    for subject in self.drawing_subjects:
      subject.draw()
