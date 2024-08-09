from enum import IntEnum
from game import (
  Coordinate, Size,
  AssetImage, Image, TileMap,
  Collision, Block
)
from core import (
  GamePad,
  Jumper, Ball, Field
)


class GameLevel(IntEnum):
  BOY = 0


class BoyStage(IntEnum):
  STAGE_1 = 0


class BoyStage1Field(Field):
  def __init__(self, max_size: Size) -> None:
    super().__init__(
      [
        TileMap(0, Coordinate(0, 0), Size(1, 2), AssetImage.Pose.NORMAL),
        TileMap(0, Coordinate(0, 0), Size(1, 2), AssetImage.Pose.NORMAL),
        TileMap(0, Coordinate(0, 0), Size(1, 2), AssetImage.Pose.NORMAL),
      ],
      [],
      max_size,
      TileMap.basic_size().height+TileMap.basic_size().height*(3/4),
    )


class BoyJumper(Jumper):
  class Motion(IntEnum):
    STOP = 0
    WALK = 1
    JUMP = 2
    FALL_DOWN = 3

  WALKING_STEP = 2

  def __init__(self) -> None:
    super().__init__(
      {
        self.Motion.STOP: Block(
          Image(0, Coordinate(1, 0), Size(1, 1), Image.Pose.NORMAL),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height))),
        self.Motion.WALK: Block(
          Image(0, Coordinate(1, 1), Size(1, 1), Image.Pose.NORMAL),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        ),
        self.Motion.JUMP: Block(
          Image(0, Coordinate(1, 2), Size(1, 1), Image.Pose.NORMAL),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        ),
        self.Motion.FALL_DOWN: Block(
          Image(0, Coordinate(1, 3), Size(1, 1), Image.Pose.NORMAL),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        )
      },
    )
    self.walking_interval = 0

  @property
  def max_accel(self) -> int:
    return -10

  def update(self, game_pad: GamePad, field: Field) -> None:
    super().update(game_pad, field)

    if self.stopping:
      self.motion = self.Motion.STOP

    elif self.walking:
      if self.walking_interval < self.WALKING_STEP:
        self.walking_interval += 1
      else:
        self.walking_interval = 0
        if self.motion == self.Motion.WALK:
          self.motion = self.Motion.STOP
        else:
          self.motion = self.Motion.WALK

    elif self.standing_by:
      self.motion = self.Motion.STOP
      if game_pad.enter():
        self.jump()
        self.motion = self.Motion.JUMP

    elif self.jumping:
      pass

    elif self.falling_down:
      self.motion = self.Motion.FALL_DOWN

    elif self.joying:
      pass

  def draw(self, transparent_color) -> None:
    super().draw(transparent_color)


class BoyStage1Ball(Ball):
  class Motion(IntEnum):
    ANGLE_0 = 0
    ANGLE_90 = 1
    ANGLE_180 = 2
    ANGLE_270 = 3

  ROLLING_STEP = 1

  def __init__(self) -> None:
    super().__init__(
      {
        self.Motion.ANGLE_0: Block(
          Image(0, Coordinate(0, 0), Size(1, 1), Image.Pose.NORMAL),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        ),
        self.Motion.ANGLE_90: Block(
          Image(0, Coordinate(0, 0), Size(1, 1), Image.Pose.MIRROR_Y),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        ),
        self.Motion.ANGLE_180: Block(
          Image(0, Coordinate(0, 0), Size(1, 1), Image.Pose.MIRROR_XY),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        ),
        self.Motion.ANGLE_270: Block(
          Image(0, Coordinate(0, 0), Size(1, 1), Image.Pose.MIRROR_X),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        ),
      },
    )
    self.rolling_interval = 0

  @property
  def rolling_distance(self) -> float:
    return 2

  def update(self, field: Field) -> None:
    if self.stopping:
      pass

    elif self.rolling:
      next_x = self.origin.x + self.rolling_distance * (1 if self.rolling_direction else -1)
      if not self.rolling_direction:
        if next_x <= field.left:
          next_x = 0
          self.rolling_direction = True
      else:
        if next_x+self.size.width >= field.right:
          next_x = field.right-self.size.width
          self.rolling_direction = False

      self.origin = Coordinate(next_x, self.origin.y)

      if self.rolling_interval < self.ROLLING_STEP:
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
