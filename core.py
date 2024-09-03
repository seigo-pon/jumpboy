from datetime import datetime
from enum import IntEnum
from typing import Any, TypeVar
from game import (
  Coordinate, Size, Dice, Stopwatch, Timer,
  TileMap, SoundEffect,
  Block, FlashSprite, Obstacle, Field as BaseField, GamePad as BaseGamePad,
  GameConfig, Language, StringRes, Snapshot as BaseSnapshot, Scene as BaseScene,
)
import pyxel


class GamePad(BaseGamePad):
  class Button(IntEnum):
    ENTER = 0
    CANCEL = 1

  def __init__(self) -> None:
    super().__init__(
      {
        self.Button.ENTER: [
          pyxel.KEY_RETURN,
          pyxel.MOUSE_BUTTON_LEFT,
          pyxel.GAMEPAD1_BUTTON_A,
        ],
        self.Button.CANCEL: [
          pyxel.KEY_SPACE,
          pyxel.MOUSE_BUTTON_RIGHT,
          pyxel.GAMEPAD1_BUTTON_B,
        ]
      }
    )

  def enter(self, pushing: bool) -> bool:
    if pushing:
      return self.pushing(self.Button.ENTER)
    else:
      return self.push(self.Button.ENTER)

  def cancel(self) -> bool:
    return self.push(self.Button.CANCEL)



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
    surface: int,
    ground_height: float,
  ) -> None:
    super().__init__(background_tiles, obstacles, max_size)

    self.surface = surface
    self.ground_height = ground_height

  @property
  def left(self) -> float:
    return -self.scroll_pos.x

  def left_end(self, origin: Coordinate) -> float | None:
    min_x: float | None = None
    for obstacle in self.obstacles:
      if obstacle.collision.top-self.scroll_pos.y <= origin.y <= obstacle.collision.bottom-self.scroll_pos.y:
        right = obstacle.collision.right-self.scroll_pos.x
        if min_x is None:
          min_x = right
        else:
          min_x = min(min_x, right)
    return min_x

  @property
  def right(self) -> float:
    return self.max_size.width-self.scroll_pos.x

  def right_end(self, origin: Coordinate) -> float | None:
    max_x: float | None = None
    for obstacle in self.obstacles:
      if obstacle.collision.top-self.scroll_pos.y <= origin.y <= obstacle.collision.bottom-self.scroll_pos.y:
        left = obstacle.collision.left-self.scroll_pos.x
        if max_x is None:
          max_x = left
        else:
          max_x = max(max_x, left)
    return max_x

  @property
  def top(self) -> float:
    return -self.scroll_pos.y

  @property
  def bottom(self) -> float:
    return self.ground_height-self.scroll_pos.y


TSnapshot = TypeVar('TSnapshot', bound='Snapshot')
TJumper = TypeVar('TJumper', bound='Jumper')

class Jumper(FlashSprite):
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
    JOY = 4

  class Sound(IntEnum):
    WALK = 0
    JUMP = 1
    DAMAGE = 2
    FALL_DOWN = 3
    JOY = 3

  FLASH_MSEC = 100
  MAX_FLASH_COUNT = 4

  class Param:
    def __init__(
      self,
      max_life: int,
      max_accel: int,
      walking_distance: float,
      walking_period: int,
      joying_repeat_count: int,
    ) -> None:
      self.max_life = max_life
      self.max_accel = max_accel
      self.walking_distance = walking_distance
      self.walking_period = walking_period
      self.joying_repeat_count = joying_repeat_count

  def __init__(
    self,
    motions: dict[int, Block],
    sounds: dict[int, SoundEffect],
    stopwatch: Stopwatch,
    param: Param,
  ) -> None:
    super().__init__(motions, sounds, stopwatch, self.FLASH_MSEC, self.MAX_FLASH_COUNT)

    self.param = param

    self.action = self.Action.STOP
    self.life = self.param.max_life
    self.damaging = False
    self.walking_x = 0.0
    self.accel = 0.0
    self.now_accel = 0.0
    self.top_y = 0.0
    self.prev_y = 0.0
    self.keeping_jump = False
    self.joying_count = 0
    self.walking_interval = 0

  def clear(self, all: bool) -> None:
    if all:
      self.damaging = False
    self.walking_x = 0.0
    self.accel = 0.0
    self.now_accel = 0.0
    self.top_y = 0.0
    self.prev_y = 0.0
    self.keeping_jump = False
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
  def jumping_down(self) -> bool:
    return self.action == self.Action.JUMP and self.center.y > self.prev_y

  @property
  def falling_down(self) -> bool:
    return self.action == self.Action.FALL_DOWN

  @property
  def joying(self) -> bool:
    return self.action == self.Action.JOY

  def stop(self) -> None:
    print('jumper stop', self.id)
    if self.action == self.Action.JUMP:
      self.keeping_jump = False
    else:
      self.action = self.Action.STOP
      self.clear(True)

  def walk(self, x: float) -> None:
    if self.stopping:
      print('jumper walk', self.id, x)
      self.action = self.Action.WALK
      self.clear(True)
      self.walking_x = x

  def stand_by(self) -> None:
    if self.stopping:
      print('jumper stand by', self.id)
      self.action = self.Action.STAND_BY
      self.clear(True)

  @property
  def fuzzy_accel(self) -> int:
    accel = int(self.param.max_accel/2)
    accel += Dice.roll(abs(accel)) * (1 if self.param.max_accel >= 0 else -1)
    print('jump accel', accel, self.param.max_accel)
    return accel

  def jump(self) -> None:
    if self.standing_by:
      print('jumper jump', self.id, self.param.max_accel)
      self.action = self.Action.JUMP
      self.clear(True)
      self.accel = self.param.max_accel
      self.now_accel = self.accel
      self.prev_y = self.center.y
      self.keeping_jump = True

  def damage(self) -> None:
    if self.standing_by or self.jumping:
      self.life -= 1
      if self.life <= 0:
        print('jumper fall down', self.id, self.life)
        self.life = 0
        self.action = self.Action.FALL_DOWN
        self.clear(True)
        self.sounds[self.Sound.FALL_DOWN].play()
      else:
        print('jumper damage', self.id, self.life)
        self.damaging = True
        self.flash()
        self.sounds[self.Sound.DAMAGE].play()

  def joy(self) -> None:
    if self.stopping:
      print('jumper joy', self.id)
      self.action = self.Action.JOY
      self.clear(True)
      self.accel = self.fuzzy_accel
      self.now_accel = self.accel
      self.prev_y = self.center.y

  def update(self, stopwatch: Stopwatch, snapshot: TSnapshot) -> None:
    super().update(stopwatch, snapshot)

    if self.damaging:
      if not self.flashing:
        self.damaging = False

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
        self.clear(True)

      if self.walking_interval < self.param.walking_period:
        self.walking_interval += 1
      else:
        self.walking_interval = 0
        if self.motion == self.Motion.WALK:
          self.motion = self.Motion.STOP
        else:
          self.motion = self.Motion.WALK
          self.sounds[self.Sound.WALK].play()

    elif self.standing_by:
      self.motion = self.Motion.STOP
      if snapshot.game_pad.enter(False):
        self.jump()

    elif self.jumping:
      self.motion = self.Motion.JUMP

      if self.bottom < snapshot.field.bottom or self.accel == self.now_accel:
        if self.accel == self.now_accel:
          self.sounds[self.Sound.JUMP].play()

        center_y = self.center.y

        min_y = snapshot.field.top+self.size.height/2
        max_y = snapshot.field.bottom-self.size.height/2

        new_y = self.center.y + (self.center.y - self.prev_y) + self.accel
        if new_y < min_y:
          new_y = min_y
        if new_y > max_y:
          new_y = max_y

        self.center.y = new_y

        self.prev_y = center_y

        self.accel = 1
        if center_y < self.center.y:
          if self.center.y < self.top_y+self.size.height:
            if self.keeping_jump:
              if snapshot.game_pad.enter(True):
                self.accel = 0
              else:
                self.keeping_jump = False
        else:
          self.top_y = self.center.y
      else:
        print('jumper jump to stand by', self.id)
        self.action = self.Action.STAND_BY
        self.clear(False)

    elif self.falling_down:
      self.motion = self.Motion.FALL_DOWN

    elif self.joying:
      self.motion = self.Motion.JOY

      if self.bottom < snapshot.field.bottom or self.accel == self.now_accel:
        if self.accel == self.now_accel:
          self.sounds[self.Sound.JOY].play()

        center_y = self.center.y
        self.center.y += (self.center.y - self.prev_y) + self.accel
        self.prev_y = center_y
        self.accel = 1
      else:
        self.joying_count += 1
        if self.joying_count >= self.param.joying_repeat_count:
          print('jumper joy to stop', self.id, self.joying_count, self.param.joying_repeat_count)
          self.action = self.Action.STOP
          self.clear(True)
        else:
          print('jumper joy again', self.id, self.joying_count, self.param.joying_repeat_count)
          self.accel = self.fuzzy_accel
          self.now_accel = self.accel
          self.prev_y = self.center.y


class Ball(FlashSprite):
  class Action(IntEnum):
    STOP = 0
    ROLL = 1
    BURST = 2

  class Motion(IntEnum):
    ANGLE_0 = 0
    ANGLE_90 = 1
    ANGLE_180 = 2
    ANGLE_270 = 3
    BURST = 4

  class Sound(IntEnum):
    ROLL = 0
    CRASH = 1
    BURST = 2
    LEAP = 3

  FLASH_MSEC = 40
  MAX_FLASH_COUNT = 4

  class Param:
    def __init__(
      self,
      rolling_distance: float,
      max_accel: int,
      rolling_period: int,
      default_acquirement_points: dict[int, int],
    ) -> None:
      self.rolling_distance = rolling_distance
      self.max_accel = max_accel
      self.rolling_period = rolling_period
      self.default_acquirement_points = default_acquirement_points

  def __init__(
    self,
    motions: dict[int, Block],
    sounds: dict[int, SoundEffect],
    stopwatch: Stopwatch,
    param: Param,
  ) -> None:
    super().__init__(motions, sounds, stopwatch, self.FLASH_MSEC, self.MAX_FLASH_COUNT)

    self.param = param

    self.action = self.Action.STOP
    self.rolled_timer: Timer | None = None
    self.acquirement_points: dict[int, int] = {}
    self.dead = False
    self.rolling_direction = True
    self.accel = 0.0
    self.now_accel = 0.0
    self.prev_y = 0.0
    self.rolling_interval = 0
    self.bounced = False

  @property
  def stopping(self) -> bool:
    return self.action == self.Action.STOP

  @property
  def rolling(self) -> bool:
    return self.action == self.Action.ROLL

  @property
  def bursting(self) -> bool:
    return self.action == self.Action.BURST

  def stop(self) -> None:
    if self.rolling:
      print('ball stop', self.id)
      self.action = self.Action.STOP

  def roll(self) -> None:
    if self.stopping:
      print('ball roll', self.id)
      self.action = self.Action.ROLL
      self.rolled_timer = None
      if self.param.max_accel > 0:
        print('ball leap', self.id, self.param.max_accel)
        self.accel = self.param.max_accel
        self.now_accel = self.accel
        self.prev_y = self.origin.y
      self.acquirement_points = self.param.default_acquirement_points
      self.sounds[self.Sound.ROLL].play()

  def roll_msec(self, stopwatch: Stopwatch, rolled_msec: int) -> None:
    if self.stopping:
      if rolled_msec > 0:
        print('ball roll wait', self.id, rolled_msec)
        self.rolled_timer = Timer.set_msec(stopwatch, rolled_msec, True)
      else:
        self.roll()

  def burst(self) -> None:
    if self.rolling:
      print('ball burst', self.id)
      self.action = self.Action.BURST
      self.flash()
      self.sounds[self.Sound.BURST].play()

  def strike(self) -> None:
    print('ball strike', self.id)
    self.acquirement_points = {}

  @property
  def acquirement_point(self) -> int:
    if self.action in self.acquirement_points:
      return self.acquirement_points[self.action]
    return 0

  def update(self, stopwatch: Stopwatch, snapshot: TSnapshot) -> None:
    super().update(stopwatch, snapshot)

    self.bounced = False

    if self.stopping:
      pass

    elif self.rolling:
      next_x = self.origin.x + self.param.rolling_distance * (1 if self.rolling_direction else -1)

      if not self.rolling_direction:
        left_end = snapshot.field.left_end(Coordinate(next_x, self.origin.y))
        if left_end is not None:
          if next_x <= left_end:
            next_x = left_end
            self.rolling_direction = True
            self.bounced = True
            print('ball roll direction', self.id, self.rolling_direction, next_x)
            self.sounds[self.Sound.CRASH].play()
      else:
        right_end = snapshot.field.right_end(Coordinate(next_x, self.origin.y))
        if right_end is not None:
          right_end -= self.size.width
          if next_x >= right_end:
            next_x = right_end
            self.rolling_direction = False
            self.bounced = True
            print('ball roll direction', self.id, self.rolling_direction, next_x)
            self.sounds[self.Sound.CRASH].play()

      next_y = self.origin.y
      if self.accel != 0:
        if self.bottom < snapshot.field.bottom or self.accel == self.now_accel:
          if self.accel == self.now_accel:
            self.sounds[self.Sound.LEAP].play()

          origin_y = next_y

          min_y = snapshot.field.top+self.size.height/2
          max_y = snapshot.field.bottom-self.size.height/2

          new_y = next_y + (next_y - self.prev_y) + self.accel
          if new_y < min_y:
            new_y = min_y
          if new_y > max_y:
            new_y = max_y

          self.prev_y = origin_y
          self.accel = 1
        else:
          print('ball leap to next', self.id)
          self.accel = self.param.max_accel
          self.now_accel = self.accel
          self.prev_y = self.origin.y

      self.origin = Coordinate(next_x, next_y)

      if self.rolling_interval < self.param.rolling_period:
        self.rolling_interval += 1
      else:
        self.rolling_interval = 0
        if self.rolling_direction:
          self.motion += 1
          if self.motion > self.Motion.ANGLE_270:
            self.motion = self.Motion.ANGLE_0
        else:
          self.motion -= 1
          if self.motion < self.Motion.ANGLE_0:
            self.motion = self.Motion.ANGLE_270

    elif self.bursting:
      self.motion = self.Motion.BURST

      if not self.flashing:
        self.dead = True
        self.show = False


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

    if 'level' in data:
      self.level = GameLevel(int(data['level']), 0)


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
    variations: list[Any] = [ball for ball in self.snapshot.balls]
    variations.append(self.snapshot.jumper)
    return variations
