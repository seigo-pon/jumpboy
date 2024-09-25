from datetime import datetime
from enum import IntEnum
from typing import TypeVar
from core import (
  Coordinate, Size, Dice, Stopwatch, Timer,
  Language, TileMap,
  Block, FlashSprite, Obstacle, Field as BaseField, GamePad as BaseGamePad, MusicBox,
  Snapshot as BaseSnapshot,
)
import pyxel


class GamePad(BaseGamePad):
  class Button(IntEnum):
    ENTER = 0
    CANCEL = 1

  def __init__(self) -> None:
    super().__init__(
      watch_buttons={
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

  def enter(self, push: bool) -> bool:
    if push:
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
    name: str,
    background_tiles: list[TileMap],
    obstacles: list[Obstacle],
    max_size: Size,
    surface: int,
    ground_height: float,
    start_x: float,
  ) -> None:
    super().__init__(
      name=name,
      backgrounds=background_tiles,
      obstacles=obstacles,
      max_size=max_size,
    )

    self.surface = surface
    self.ground_height = ground_height
    self.start_x = start_x

  @property
  def left(self) -> float:
    return -self.scroll_pos.x

  def left_end(self, origin: Coordinate) -> float | None:
    min_x: float | None = None
    for obstacle in self.obstacles:
      if obstacle.collision.top-self.scroll_pos.y <= origin.y <= obstacle.collision.bottom-self.scroll_pos.y:
        right = obstacle.collision.right-self.scroll_pos.x
        if right <= origin.x:
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
        if origin.x <= left:
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
    WALK_LEFT = 1
    WALK_RIGHT = 2
    JUMP_UP = 3
    JUMP_DOWN = 4
    FALL_DOWN = 5
    JOY = 6

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
      walk_distance: float,
      walk_period: int,
      keep_jump_height: float,
      joy_repeat_count: int,
    ) -> None:
      self.max_life = max_life
      self.max_accel = max_accel
      self.walk_distance = walk_distance
      self.walk_period = walk_period
      self.keep_jump_height = keep_jump_height
      self.joy_repeat_count = joy_repeat_count

  def __init__(
    self,
    name: str,
    motions: dict[int, Block],
    sounds: dict[int, int],
    stopwatch: Stopwatch,
    param: Param,
  ) -> None:
    super().__init__(
      name=name,
      motions=motions,
      sounds=sounds,
      stopwatch=stopwatch,
      flash_msec=self.FLASH_MSEC,
      max_flash_count=self.MAX_FLASH_COUNT,
    )

    self.param = param

    self.action = self.Action.STOP
    self.life = self.param.max_life
    self.damaging = False
    self.start_damage = False
    self.walk_x = 0.0
    self.accel = 0.0
    self.now_accel = 0.0
    self.top_y = 0.0
    self.prev_y = 0.0
    self.keep_jump = False
    self.joy_count = 0
    self.walk_interval = 0

  def clear(self, all: bool) -> None:
    if all:
      self.damaging = False
      self.start_damage = False
    self.walk_x = 0.0
    self.accel = 0.0
    self.now_accel = 0.0
    self.top_y = 0.0
    self.prev_y = 0.0
    self.keep_jump = False
    self.joy_count = 0
    self.walk_interval = 0

  @property
  def stopping(self) -> bool:
    return self.action == self.Action.STOP

  @property
  def walking(self) -> bool:
    return self.action == self.Action.WALK

  @property
  def standing_by(self) -> bool:
    return self.action == self.Action.STAND_BY

  def jumping(self, up: bool | None) -> bool:
    jump = self.action == self.Action.JUMP
    if jump and up is not None:
      if up:
        if self.center.y >= self.prev_y:
          jump = False
      else:
        if self.center.y <= self.prev_y:
          jump = False
    return jump

  @property
  def falling_down(self) -> bool:
    return self.action == self.Action.FALL_DOWN

  @property
  def joying(self) -> bool:
    return self.action == self.Action.JOY

  def stop(self) -> None:
    print('jumper stop', self.id)
    if self.action == self.Action.JUMP:
      self.keep_jump = False
    else:
      self.action = self.Action.STOP
      self.clear(True)

  def walk(self, x: float) -> None:
    if self.stopping:
      print('jumper walk', self.id, x)
      self.action = self.Action.WALK
      self.clear(True)
      self.walk_x = x

  def stand_by(self) -> None:
    if self.stopping:
      print('jumper stand by', self.id)
      self.action = self.Action.STAND_BY
      self.clear(True)

  @property
  def fuzzy_accel(self) -> int:
    accel = int(self.param.max_accel/2)
    accel += Dice.spin(abs(accel)) * (1 if self.param.max_accel >= 0 else -1)
    print('jump accel', accel, self.param.max_accel)
    return accel

  def jump(self) -> None:
    if self.standing_by:
      print('jumper jump', self.id, self.param.max_accel)
      self.action = self.Action.JUMP
      self.clear(False)
      self.accel = self.param.max_accel
      self.now_accel = self.accel
      self.prev_y = self.center.y
      self.keep_jump = True

  def damage(self) -> None:
    if self.standing_by or self.jumping(None):
      self.life -= 1
      if self.life <= 0:
        print('jumper fall down', self.id, self.life)
        self.life = 0
        self.action = self.Action.FALL_DOWN
        self.clear(True)
      else:
        print('jumper damage', self.id, self.life)
        self.damaging = True
        self.flash()
        self.start_damage = True

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
      if self.start_damage:
        snapshot.music_box.play_se(self.sounds[self.Sound.DAMAGE])
        self.start_damage = False

      if not self.flashing:
        self.damaging = False

    if self.stopping:
      self.motion = self.Motion.STOP

    elif self.walking:
      distance = self.param.walk_distance
      diff = self.origin.x - self.walk_x
      if abs(diff) < distance:
        distance = diff
      else:
        if diff > 0:
          distance *= -1

      self.origin = Coordinate(self.origin.x+distance, self.origin.y)

      if self.origin.x == self.walk_x:
        print('jumper walk to stop', self.id)
        self.action = self.Action.STOP
        self.clear(True)

      if self.walk_interval < self.param.walk_period:
        self.walk_interval += 1
      else:
        self.walk_interval = 0
        if self.motion == self.Motion.WALK_LEFT or self.motion == self.Motion.WALK_RIGHT:
          self.motion = self.Motion.STOP
        else:
          self.motion = self.Motion.WALK_LEFT if distance <= 0 else self.Motion.WALK_RIGHT
          snapshot.music_box.play_se(self.sounds[self.Sound.WALK])

    elif self.standing_by:
      self.motion = self.Motion.STOP
      if snapshot.game_pad.enter(False):
        self.jump()

    elif self.jumping(None):
      if self.bottom < snapshot.field.bottom or self.accel == self.now_accel:
        if self.accel == self.now_accel:
          snapshot.music_box.play_se(self.sounds[self.Sound.JUMP])

        center_y = self.center.y

        min_y = snapshot.field.top+self.size.height/2
        max_y = snapshot.field.bottom-self.size.height/2

        new_y = self.center.y + (self.center.y - self.prev_y) + self.accel
        if new_y < min_y:
          new_y = min_y
        if new_y > max_y:
          new_y = max_y

        self.center = Coordinate(self.center.x, new_y)
        self.prev_y = center_y

        self.motion = self.Motion.JUMP_UP if new_y < center_y else self.Motion.JUMP_DOWN

        self.accel = 1
        if center_y < self.center.y:
          if self.center.y < self.top_y+self.param.keep_jump_height:
            if self.keep_jump:
              if snapshot.game_pad.enter(True):
                self.accel = 0
              else:
                self.keep_jump = False
        else:
          self.top_y = self.center.y
      else:
        print('jumper jump to stand by', self.id)
        self.action = self.Action.STAND_BY
        self.clear(False)

    elif self.falling_down:
      if self.motion != self.Motion.FALL_DOWN:
        snapshot.music_box.play_se(self.sounds[self.Sound.FALL_DOWN])
      self.motion = self.Motion.FALL_DOWN

    elif self.joying:
      self.motion = self.Motion.JOY

      if self.bottom < snapshot.field.bottom or self.accel == self.now_accel:
        if self.accel == self.now_accel:
          snapshot.music_box.play_se(self.Sound.JOY)

        center_y = self.center.y
        self.center.y += (self.center.y - self.prev_y) + self.accel
        self.prev_y = center_y
        self.accel = 1
      else:
        self.joy_count += 1
        if self.joy_count >= self.param.joy_repeat_count:
          print('jumper joy to stop', self.id, self.joy_count, self.param.joy_repeat_count)
          self.action = self.Action.STOP
          self.clear(True)
        else:
          print('jumper joy again', self.id, self.joy_count, self.param.joy_repeat_count)
          self.accel = self.fuzzy_accel
          self.now_accel = self.accel
          self.prev_y = self.center.y


class Ball(FlashSprite):
  class Action(IntEnum):
    STOP = 0
    SPIN = 1
    BURST = 2

  class Motion(IntEnum):
    ANGLE_0 = 0
    ANGLE_90 = 1
    ANGLE_180 = 2
    ANGLE_270 = 3
    BURST = 4

  class Sound(IntEnum):
    SPIN = 0
    BOUNCE = 1
    BURST = 2
    LEAP = 3

  FLASH_MSEC = 40
  MAX_FLASH_COUNT = 4

  class Param:
    def __init__(
      self,
      spin_distance: float,
      max_accel: int,
      first_y: float,
      spin_period: int,
      max_points: dict[int, int],
    ) -> None:
      self.spin_distance = spin_distance
      self.max_accel = max_accel
      self.first_y = first_y
      self.spin_period = spin_period
      self.max_points = max_points

  def __init__(
    self,
    name: str,
    motions: dict[int, Block],
    sounds: dict[int, int],
    stopwatch: Stopwatch,
    param: Param,
  ) -> None:
    super().__init__(
      name=name,
      motions=motions,
      sounds=sounds,
      stopwatch=stopwatch,
      flash_msec=self.FLASH_MSEC,
      max_flash_count=self.MAX_FLASH_COUNT,
    )

    self.param = param

    self.action = self.Action.STOP
    self.spun_timer: Timer | None = None
    self.points: dict[int, int] = {}
    self.dead = False
    self.spin_direction = True
    self.start_spin = False
    self.accel = 0.0
    self.now_accel = 0.0
    self.prev_y = 0.0
    self.spin_interval = 0
    self.bounced = False

  @property
  def stopping(self) -> bool:
    return self.action == self.Action.STOP

  @property
  def spinning(self) -> bool:
    return self.action == self.Action.SPIN

  @property
  def bursting(self) -> bool:
    return self.action == self.Action.BURST

  def stop(self) -> None:
    if self.spinning:
      print('ball stop', self.id)
      self.action = self.Action.STOP

  def spin(self) -> None:
    if self.stopping:
      print('ball spin', self.id)
      self.action = self.Action.SPIN
      self.spun_timer = None
      if self.param.max_accel != 0:
        print('ball leap', self.id, self.param.max_accel)
        self.accel = 1
        self.now_accel = self.param.max_accel
        self.origin = Coordinate(self.origin.x, self.origin.y-self.param.first_y)
        self.prev_y = self.origin.y
      self.points = self.param.max_points
      self.start_spin = True

  def spin_after_msec(self, stopwatch: Stopwatch, spun_msec: int) -> None:
    if self.stopping:
      if spun_msec > 0:
        print('ball spin wait', self.id, spun_msec)
        self.spun_timer = Timer.set_msec(stopwatch, spun_msec, True)
      else:
        self.spin()

  def burst(self) -> None:
    if self.spinning:
      print('ball burst', self.id)
      self.action = self.Action.BURST
      self.flash()

  def through(self) -> None:
    print('ball through', self.id)
    self.points = {}

  @property
  def point(self) -> int:
    if self.action in self.points:
      return self.points[self.action]
    return 0

  def update(self, stopwatch: Stopwatch, snapshot: TSnapshot) -> None:
    super().update(stopwatch, snapshot)

    self.bounced = False

    if self.stopping:
      pass

    elif self.spinning:
      if self.start_spin:
        snapshot.music_box.play_se(self.sounds[self.Sound.SPIN])
        self.start_spin = False

      new_x = self.origin.x + self.param.spin_distance * (1 if self.spin_direction else -1)

      if not self.spin_direction:
        left_end = snapshot.field.left_end(self.origin)
        if left_end is not None:
          if new_x <= left_end:
            new_x = left_end
            self.spin_direction = True
            self.bounced = True
            print('ball spin direction', self.id, self.spin_direction, new_x)
            snapshot.music_box.play_se(self.sounds[self.Sound.BOUNCE])
      else:
        right_end = snapshot.field.right_end(self.origin)
        if right_end is not None:
          right_end -= self.size.width
          if new_x >= right_end:
            new_x = right_end
            self.spin_direction = False
            self.bounced = True
            print('ball spin direction', self.id, self.spin_direction, new_x)
            snapshot.music_box.play_se(self.sounds[self.Sound.BOUNCE])

      new_y = self.origin.y
      if self.accel != 0:
        if self.bottom < snapshot.field.bottom or self.accel == self.now_accel:
          if self.accel == self.now_accel:
            snapshot.music_box.play_se(self.sounds[self.Sound.LEAP])

          origin_y = new_y

          min_y = snapshot.field.top+self.size.height
          max_y = snapshot.field.bottom-self.size.height

          new_y = new_y + (new_y - self.prev_y) + self.accel
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

      self.origin = Coordinate(new_x, new_y)

      if self.spin_interval < self.param.spin_period:
        self.spin_interval += 1
      else:
        self.spin_interval = 0
        if self.spin_direction:
          self.motion += 1
          if self.motion > self.Motion.ANGLE_270:
            self.motion = self.Motion.ANGLE_0
        else:
          self.motion -= 1
          if self.motion < self.Motion.ANGLE_0:
            self.motion = self.Motion.ANGLE_270

    elif self.bursting:
      if self.motion != self.Motion.BURST:
        snapshot.music_box.play_se(self.sounds[self.Sound.BURST])
      self.motion = self.Motion.BURST

      if not self.flashing:
        self.dead = True
        self.show = False


class Snapshot(BaseSnapshot):
  def __init__(
    self,
    lang: Language,
    game_pad: GamePad,
    music_box: MusicBox,
    score_board: ScoreBoard,
    level :GameLevel,
    field: Field,
    balls: list[Ball],
    jumper: Jumper,
  ) -> None:
    super().__init__()

    self.lang = lang
    self.game_pad = game_pad
    self.music_box = music_box
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
      self.level = GameLevel(int(data['level']), self.level.stage)
