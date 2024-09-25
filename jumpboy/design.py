from enum import IntEnum
from core import (
  Coordinate, Size, Stopwatch, Dice,
  AssetImageId, Image, TileMap,
  Collision, Block, Obstacle,
  GameConfig,
)
from component import (
  GameLevel, Field, Jumper, Ball,
)
import math


class TileId:
  FIELD = AssetImageId(0, 0)

class ImageId:
  BALL = AssetImageId(0, 0)
  JUMPER = AssetImageId(0, 1)
  LIFE = AssetImageId(0, 3)

class SoundId:
  JUMPER = 0
  BALL = 10
  SCENE = 20
  BGM = 60

class GameLevelMode(IntEnum):
  # boy
  NORMAL = 0
  # girl
  HARD = 1

class GameLevelStage(IntEnum):
  # road
  STAGE_1 = 0
  STAGE_2 = 1
  STAGE_3 = 2
  # grass
  STAGE_4 = 3
  STAGE_5 = 4
  STAGE_6 = 5
  # clay
  STAGE_7 = 6
  STAGE_8 = 7
  STAGE_9 = 8
  # wood
  STAGE_10 = 9
  STAGE_11 = 10
  STAGE_12 = 11


class GameDesign:
  GROUND_TOP = TileMap.basic_size().height+TileMap.basic_size().height*(3/4)

  class FieldSurface(IntEnum):
    ROAD = 0
    GRASS = 1
    CLAY = 2
    WOOD = 3

  def __init__(self) -> None:
    self.prev_params: list[Ball.Param] = []

  def clear(self) -> None:
    self.prev_params = []

  def first_level(self, config: GameConfig) -> GameLevel:
    if config.debug:
      return GameLevel(GameLevelMode.NORMAL, GameLevelStage.STAGE_1)
    else:
      return GameLevel(GameLevelMode.NORMAL, GameLevelStage.STAGE_1)

  def field(self, level: GameLevel, config: GameConfig) -> Field:
    if level.mode in [
      GameLevelMode.NORMAL,
      GameLevelMode.HARD,
    ]:
      if level.stage in [
        GameLevelStage.STAGE_1,
        GameLevelStage.STAGE_2,
        GameLevelStage.STAGE_3,
      ]:
        field = Field(
          name='road_field',
          background_tiles=[
            TileMap(TileId.FIELD.id, Coordinate(TileId.FIELD.x, 0), Size(2.5, 1.875), Image.Pose.NORMAL),
          ],
          obstacles=[],
          max_size=config.window_size,
          surface=self.FieldSurface.ROAD,
          ground_height=self.GROUND_TOP,
          start_x=Image.basic_size().width*5,
        )

      elif level.stage in [
        GameLevelStage.STAGE_4,
        GameLevelStage.STAGE_5,
        GameLevelStage.STAGE_6,
      ]:
        field = Field(
          name='grass_field',
          background_tiles=[
            TileMap(TileId.FIELD.id, Coordinate(TileId.FIELD.x, 2), Size(2.5, 1.875), Image.Pose.NORMAL),
          ],
          obstacles=[
            Obstacle(
              Collision(
                Coordinate(0, self.GROUND_TOP-Image.basic_size().height),
                Size(0, Image.basic_size().height),
              ),
            ),
            Obstacle(
              Collision(
                Coordinate(config.window_size.width, self.GROUND_TOP-Image.basic_size().height),
                Size(0, Image.basic_size().height),
              ),
            ),
          ],
          max_size=config.window_size,
          surface=self.FieldSurface.GRASS,
          ground_height=self.GROUND_TOP,
          start_x=config.window_size.width/2+Image.basic_size().width/2,
        )

      elif level.stage in [
        GameLevelStage.STAGE_7,
        GameLevelStage.STAGE_8,
        GameLevelStage.STAGE_9,
      ]:
        field = Field(
          name='clay_field',
          background_tiles=[
            TileMap(TileId.FIELD.id, Coordinate(TileId.FIELD.x, 4), Size(2.5, 1.875), Image.Pose.NORMAL),
          ],
          obstacles=[],
          max_size=config.window_size,
          surface=self.FieldSurface.CLAY,
          ground_height=self.GROUND_TOP,
          start_x=Image.basic_size().width*5,
        )

      elif level.stage in [
        GameLevelStage.STAGE_10,
        GameLevelStage.STAGE_11,
        GameLevelStage.STAGE_12,
      ]:
        field = Field(
          name='wood_field',
          background_tiles=[
            TileMap(TileId.FIELD.id, Coordinate(TileId.FIELD.x, 6), Size(2.5, 1.875), Image.Pose.NORMAL),
          ],
          obstacles=[
            Obstacle(
              Collision(
                Coordinate(0, self.GROUND_TOP-TileMap.basic_size().height*2),
                Size(0, TileMap.basic_size().height*2),
              ),
            ),
            Obstacle(
              Collision(
                Coordinate(config.window_size.width, self.GROUND_TOP-TileMap.basic_size().height*2),
                Size(0, TileMap.basic_size().height*2),
              ),
            ),
          ],
          max_size=config.window_size,
          surface=self.FieldSurface.WOOD,
          ground_height=self.GROUND_TOP,
          start_x=config.window_size.width/2+Image.basic_size().width/2,
        )

    return field

  def jumper(self, level: GameLevel, stopwatch: Stopwatch) -> Jumper:
    if level.mode == GameLevelMode.NORMAL:
      jumper = Jumper(
        name='boy_jumper',
        motions={
          Jumper.Motion.STOP: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 0), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.WALK_LEFT: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 1), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.WALK_RIGHT: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 1), Size(1, 1), Image.Pose.MIRROR_X),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JUMP_UP: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 2), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JUMP_DOWN: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 2), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.FALL_DOWN: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 3), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JOY: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 4), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
        },
        sounds={
          Jumper.Sound.WALK: SoundId.JUMPER+0,
          Jumper.Sound.JUMP: SoundId.JUMPER+1,
          Jumper.Sound.FALL_DOWN: SoundId.JUMPER+2,
          Jumper.Sound.JOY: SoundId.JUMPER+3,
          Jumper.Sound.DAMAGE: SoundId.JUMPER+4,
        },
        stopwatch=stopwatch,
        param=Jumper.Param(
          max_life=5,
          max_accel=-10,
          walk_distance=0.5,
          walk_period=4,
          keep_jump_height=Image.basic_size().height,
          joy_repeat_count=3,
        ),
      )

    elif level.mode == GameLevelMode.HARD:
      jumper = Jumper(
        'girl_jumper',
        motions={
          Jumper.Motion.STOP: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 5), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.WALK_LEFT: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 6), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.WALK_RIGHT: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 6), Size(1, 1), Image.Pose.MIRROR_X),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JUMP_UP: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 7), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JUMP_DOWN: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 8), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.FALL_DOWN: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 9), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JOY: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 10), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
        },
        sounds={
          Jumper.Sound.WALK: SoundId.JUMPER+5,
          Jumper.Sound.JUMP: SoundId.JUMPER+6,
          Jumper.Sound.FALL_DOWN: SoundId.JUMPER+7,
          Jumper.Sound.JOY: SoundId.JUMPER+8,
          Jumper.Sound.DAMAGE: SoundId.JUMPER+9,
        },
        stopwatch=stopwatch,
        param=Jumper.Param(
          max_life=3,
          max_accel=-10,
          walk_distance=0.5,
          walk_period=4,
          keep_jump_height=Image.basic_size().height/2,
          joy_repeat_count=3,
        ),
      )

    return jumper

  def ball(self, level: GameLevel, stopwatch: Stopwatch) -> Ball:
    if level.mode in [
      GameLevelMode.NORMAL,
      GameLevelMode.HARD,
    ]:
      if level.stage in [
        GameLevelStage.STAGE_1,
        GameLevelStage.STAGE_2,
        GameLevelStage.STAGE_3,
      ]:
        if level.stage == GameLevelStage.STAGE_1:
          spin_distance = 2
        elif level.stage == GameLevelStage.STAGE_2:
          spin_distance = 3
        elif level.stage == GameLevelStage.STAGE_3:
          latest_spin_distances = 0.0
          if len(self.prev_params) > 1:
            for param in self.prev_params[-2:]:
              latest_spin_distances += param.spin_distance

          if latest_spin_distances <= 4:
            spin_distance = 3
          elif latest_spin_distances >= 6:
            spin_distance = 2
          else:
            spin_distance = Dice.spin(1)+2

        ball = Ball(
            name='straight_ball',
            motions={
              Ball.Motion.ANGLE_0: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 0), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_90: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 0), Size(1, 1), Image.Pose.MIRROR_Y),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_180: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 0), Size(1, 1), Image.Pose.MIRROR_XY),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_270: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 0), Size(1, 1), Image.Pose.MIRROR_X),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.BURST: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 1), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
            },
            sounds={
              Ball.Sound.SPIN: SoundId.BALL+0,
              Ball.Sound.BOUNCE: SoundId.BALL+1,
              Ball.Sound.BURST: SoundId.BALL+2,
              Ball.Sound.LEAP: SoundId.BALL+3,
            },
            stopwatch=stopwatch,
            param=Ball.Param(
              spin_distance=spin_distance,
              max_accel=0,
              first_y=0,
              spin_period=1,
              max_points={
                Ball.Action.SPIN: 10,
                Ball.Action.BURST: 30
              },
            ),
          )

      elif level.stage in [
        GameLevelStage.STAGE_4,
        GameLevelStage.STAGE_5,
        GameLevelStage.STAGE_6,
      ]:
        if level.stage == GameLevelStage.STAGE_4:
          spin_distance = 2
        elif level.stage == GameLevelStage.STAGE_5:
          spin_distance = 3
        elif level.stage == GameLevelStage.STAGE_6:
          latest_spin_distances = 0.0
          if len(self.prev_params) > 1:
            for param in self.prev_params[-2:]:
              latest_spin_distances += param.spin_distance

          if latest_spin_distances <= 4:
            spin_distance = 3
          elif latest_spin_distances >= 6:
            spin_distance = 2
          else:
            spin_distance = Dice.spin(2)+1

        ball = Ball(
            name='bounce_ball',
            motions={
              Ball.Motion.ANGLE_0: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 2), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_90: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 2), Size(1, 1), Image.Pose.MIRROR_Y),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_180: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 2), Size(1, 1), Image.Pose.MIRROR_XY),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_270: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 2), Size(1, 1), Image.Pose.MIRROR_X),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.BURST: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 1), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
            },
            sounds={
              Ball.Sound.SPIN: SoundId.BALL+0,
              Ball.Sound.BOUNCE: SoundId.BALL+1,
              Ball.Sound.BURST: SoundId.BALL+2,
              Ball.Sound.LEAP: SoundId.BALL+3,
            },
            stopwatch=stopwatch,
            param=Ball.Param(
              spin_distance=spin_distance,
              max_accel=0,
              first_y=0,
              spin_period=1,
              max_points={
                Ball.Action.SPIN: 20,
                Ball.Action.BURST: 40
              },
            ),
          )

      elif level.stage in [
        GameLevelStage.STAGE_7,
        GameLevelStage.STAGE_8,
        GameLevelStage.STAGE_9,
      ]:
        if level.stage == GameLevelStage.STAGE_7:
          spin_distance = 3
          accel = -8
        elif level.stage == GameLevelStage.STAGE_8:
          spin_distance = 4
          accel = -8
        elif level.stage == GameLevelStage.STAGE_9:
          latest_spin_distances = 0.0
          if len(self.prev_params) > 1:
            for param in self.prev_params[-2:]:
              latest_spin_distances += param.spin_distance

          if latest_spin_distances <= 6:
            spin_distance = 4
          elif latest_spin_distances >= 8:
            spin_distance = 3
          else:
            spin_distance = Dice.spin(1)+3

          accel = -(Dice.spin(2)+8)

        first_y = Image.basic_size().height*3
        if len(self.prev_params) > 0 and self.prev_params[-1].first_y == first_y:
          first_y = Image.basic_size().height*6

        ball = Ball(
            name='straight_leap_ball',
            motions={
              Ball.Motion.ANGLE_0: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 3), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_90: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 3), Size(1, 1), Image.Pose.MIRROR_Y),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_180: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 3), Size(1, 1), Image.Pose.MIRROR_XY),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_270: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 3), Size(1, 1), Image.Pose.MIRROR_X),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.BURST: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 1), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
            },
            sounds={
              Ball.Sound.SPIN: SoundId.BALL+0,
              Ball.Sound.BOUNCE: SoundId.BALL+1,
              Ball.Sound.BURST: SoundId.BALL+2,
              Ball.Sound.LEAP: SoundId.BALL+3,
            },
            stopwatch=stopwatch,
            param=Ball.Param(
              spin_distance=spin_distance,
              max_accel=accel,
              first_y=first_y,
              spin_period=1,
              max_points={
                Ball.Action.SPIN: 30,
                Ball.Action.BURST: 50
              },
            ),
          )

      elif level.stage in [
        GameLevelStage.STAGE_10,
        GameLevelStage.STAGE_11,
        GameLevelStage.STAGE_12,
      ]:
        if level.stage == GameLevelStage.STAGE_10:
          spin_distance = 4
          accel = -8
        elif level.stage == GameLevelStage.STAGE_11:
          spin_distance = 5
          accel = -8
        elif level.stage == GameLevelStage.STAGE_12:
          latest_spin_distances = 0.0
          if len(self.prev_params) > 1:
            for param in self.prev_params[-2:]:
              latest_spin_distances += param.spin_distance

          if latest_spin_distances <= 8:
            spin_distance = 5
          elif latest_spin_distances >= 10:
            spin_distance = 4
          else:
            spin_distance = Dice.spin(1)+4

          accel = -(Dice.spin(4)+6)

        first_y = Image.basic_size().height*3
        if len(self.prev_params) > 0 and self.prev_params[-1].first_y == first_y:
          first_y = Image.basic_size().height*6

        ball = Ball(
            name='straight_leap_ball',
            motions={
              Ball.Motion.ANGLE_0: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 4), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_90: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 4), Size(1, 1), Image.Pose.MIRROR_Y),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_180: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 4), Size(1, 1), Image.Pose.MIRROR_XY),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_270: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 4), Size(1, 1), Image.Pose.MIRROR_X),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.BURST: Block(
                Image(ImageId.BALL.id, Coordinate(ImageId.BALL.x, 1), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
            },
            sounds={
              Ball.Sound.SPIN: SoundId.BALL+0,
              Ball.Sound.BOUNCE: SoundId.BALL+1,
              Ball.Sound.BURST: SoundId.BALL+2,
              Ball.Sound.LEAP: SoundId.BALL+3,
            },
            stopwatch=stopwatch,
            param=Ball.Param(
              spin_distance=spin_distance,
              max_accel=accel,
              first_y=first_y,
              spin_period=1,
              max_points={
                Ball.Action.SPIN: 40,
                Ball.Action.BURST: 60
              },
            ),
          )

    self.prev_params.append(ball.param)

    return ball

  def next_ball_msec(self, level: GameLevel, balls: list[Ball]) -> int | None:
    msec: int | None = 0
    if len(balls) > 0:
      if level.mode in [
        GameLevelMode.NORMAL,
        GameLevelMode.HARD,
      ]:
        if level.stage in [
          GameLevelStage.STAGE_1,
        ]:
          msec = 2000

        elif level.stage in [
          GameLevelStage.STAGE_2,
        ]:
          msec = 1000

        elif level.stage in [
          GameLevelStage.STAGE_3,
        ]:
          msec = (Dice.spin(1)+1)*1000

        elif level.stage in [
          GameLevelStage.STAGE_4,
        ]:
          if len(balls) < 2:
            msec = 3000
          else:
            msec = None

        elif level.stage in [
          GameLevelStage.STAGE_5,
        ]:
          if len(balls) < 2:
            msec = 2000
          else:
            msec = None

        elif level.stage in [
          GameLevelStage.STAGE_6,
        ]:
          if len(balls) < 3:
            msec = (Dice.spin(1)+1)*1000
          else:
            msec = None

        elif level.stage in [
          GameLevelStage.STAGE_7,
        ]:
          msec = 2000

        elif level.stage in [
          GameLevelStage.STAGE_8,
        ]:
          msec = 2000

        elif level.stage in [
          GameLevelStage.STAGE_9,
        ]:
          msec = (Dice.spin(1)+1)*1000

        elif level.stage in [
          GameLevelStage.STAGE_10,
        ]:
          if len(balls) < 3:
            msec = 2000
          else:
            msec = None

        elif level.stage in [
          GameLevelStage.STAGE_11,
        ]:
          if len(balls) < 3:
            msec = 2000
          else:
            msec = None

        elif level.stage in [
          GameLevelStage.STAGE_12,
        ]:
          if len(balls) < 4:
            msec = (Dice.spin(1)+0)*1000
          else:
            msec = None

    return msec

  def can_spin_ball(self, level: GameLevel, field: Field, ball: Ball, last_ball: Ball | None) -> int:
    spin = False
    if ball.spun_timer is None or ball.spun_timer.over:
      spin = True

    if last_ball is not None:
      if level.mode in [
        GameLevelMode.NORMAL,
        GameLevelMode.HARD,
      ]:
        if level.stage in [
          GameLevelStage.STAGE_1,
        ]:
          distance = field.max_size.width/2

        elif level.stage in [
          GameLevelStage.STAGE_2,
        ]:
          distance = field.max_size.width/3

        elif level.stage in [
          GameLevelStage.STAGE_3,
        ]:
          distance = field.max_size.width/4

        elif level.stage in [
          GameLevelStage.STAGE_4,
          GameLevelStage.STAGE_5,
        ]:
          distance = field.max_size.width/2

        elif level.stage in [
          GameLevelStage.STAGE_6,
        ]:
          distance = field.max_size.width/3

        elif level.stage in [
          GameLevelStage.STAGE_7,
          GameLevelStage.STAGE_8,
        ]:
          distance = field.max_size.width/2

        elif level.stage in [
          GameLevelStage.STAGE_9,
        ]:
          distance = field.max_size.width/3

        elif level.stage in [
          GameLevelStage.STAGE_10,
          GameLevelStage.STAGE_11,
        ]:
          distance = field.max_size.width/3

        elif level.stage in [
          GameLevelStage.STAGE_12,
        ]:
          distance = 0

      if last_ball.left < distance:
        spin = False

    return spin

  def play_limit_msec(self, level: GameLevel) -> int:
    if level.mode in [
      GameLevelMode.NORMAL,
      GameLevelMode.HARD,
    ]:
      if level.stage in [
        GameLevelStage.STAGE_1,
        GameLevelStage.STAGE_2,
      ]:
        limit_msec = 15000

      elif level.stage in [
        GameLevelStage.STAGE_3,
      ]:
        limit_msec = 20000

      elif level.stage in [
        GameLevelStage.STAGE_4,
        GameLevelStage.STAGE_5,
      ]:
        limit_msec = 15000

      elif level.stage in [
        GameLevelStage.STAGE_6,
      ]:
        limit_msec = 20000

      elif level.stage in [
        GameLevelStage.STAGE_7,
        GameLevelStage.STAGE_8,
      ]:
        limit_msec = 20000

      elif level.stage in [
        GameLevelStage.STAGE_9,
      ]:
        limit_msec = 30000

      elif level.stage in [
        GameLevelStage.STAGE_10,
        GameLevelStage.STAGE_11,
      ]:
        limit_msec = 30000

      elif level.stage in [
        GameLevelStage.STAGE_12,
      ]:
        limit_msec = 40000

    return limit_msec

  def bonus_point(self, level: GameLevel, jumper: Jumper) -> int:
    point = 0

    if level.mode == GameLevelMode.NORMAL:
      if jumper.life == jumper.param.max_life:
        point = jumper.life
      elif jumper.life == jumper.param.max_life - 1:
        point = math.floor(jumper.life*0.5)

    elif level.mode == GameLevelMode.HARD:
      if jumper.life == jumper.param.max_life:
        point = jumper.life*2
      elif jumper.life == jumper.param.max_life - 1:
        point = math.floor(jumper.life*1.5)

    return point

  def recovery_life_count(self, level: GameLevel) -> int:
    if level.mode == GameLevelMode.NORMAL:
      life = 2

    elif level.mode == GameLevelMode.HARD:
      life = 1

    return life
