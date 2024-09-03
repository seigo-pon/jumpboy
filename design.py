from enum import IntEnum
from game import (
  Coordinate, Size, Stopwatch, Dice,
  Image, TileMap, SoundEffect,
  Collision, Block, Obstacle,
  GameConfig,
)
from core import (
  GameLevel, Field, Jumper, Ball,
)
from assetid import TileId, ImageId, SoundCh, SoundId


class GameLevelMode(IntEnum):
  NORMAL = 0

class GameLevelStage(IntEnum):
  STAGE_1 = 0
  STAGE_2 = 1
  STAGE_3 = 2
  STAGE_4 = 3
  STAGE_5 = 4
  STAGE_6 = 5


class GameDesign:
  GROUND_TOP = TileMap.basic_size().height+TileMap.basic_size().height*(3/4)

  class FieldSurface(IntEnum):
    NORMAL = 0
    FENCE = 1

  @classmethod
  def field(cls, level: GameLevel, config: GameConfig) -> Field:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.STAGE_1,
        GameLevelStage.STAGE_2,
        GameLevelStage.STAGE_3,
      ]:
        field = Field(
          background_tiles=[TileMap(TileId.FIELD.id, Coordinate(TileId.FIELD.x, 0), Size(2.5, 1.875), Image.Pose.NORMAL)],
          obstacles=[],
          max_size=config.window_size,
          surface=cls.FieldSurface.NORMAL,
          ground_height=cls.GROUND_TOP,
        )

      elif level.stage in [
        GameLevelStage.STAGE_4,
        GameLevelStage.STAGE_5,
        GameLevelStage.STAGE_6,
      ]:
        field = Field(
          background_tiles=[TileMap(TileId.FIELD.id, Coordinate(TileId.FIELD.x+3, 0), Size(2.5, 1.875), Image.Pose.NORMAL)],
          obstacles=[
            Obstacle(
              Collision(
                Coordinate(0, cls.GROUND_TOP-Image.basic_size().height*2),
                Size(1, Image.basic_size().height*2),
              ),
            ),
            Obstacle(
              Collision(
                Coordinate(config.window_size.width, cls.GROUND_TOP-Image.basic_size().height*2),
                Size(1, Image.basic_size().height*2),
              ),
            ),
          ],
          max_size=config.window_size,
          surface=cls.FieldSurface.FENCE,
          ground_height=cls.GROUND_TOP,
        )

    return field

  @classmethod
  def jumper(cls, level: GameLevel, stopwatch: Stopwatch) -> Jumper:
    if level.mode == GameLevelMode.NORMAL:
      jumper = Jumper(
        motions={
          Jumper.Motion.STOP: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 0), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height))),
          Jumper.Motion.WALK: Block(
            Image(ImageId.JUMPER.id, Coordinate(ImageId.JUMPER.x, 1), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JUMP: Block(
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
          Jumper.Sound.WALK: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+0),
          Jumper.Sound.JUMP: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+1),
          Jumper.Sound.FALL_DOWN: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+2),
          Jumper.Sound.JOY: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+3),
          Jumper.Sound.DAMAGE: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+4),
        },
        stopwatch=stopwatch,
        param=Jumper.Param(
          max_life=3,
          max_accel=-10,
          walking_distance=0.5,
          walking_period=4,
          joying_repeat_count=3,
        ),
      )

    return jumper

  @classmethod
  def ball(cls, level: GameLevel, stopwatch: Stopwatch) -> Ball:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.STAGE_1,
        GameLevelStage.STAGE_2,
        GameLevelStage.STAGE_3,
      ]:
        distance = 1
        if level.stage == GameLevelStage.STAGE_1:
          distance = 2
        elif level.stage == GameLevelStage.STAGE_2:
          distance = Dice.roll(1)+2
        elif level.stage == GameLevelStage.STAGE_3:
          distance = Dice.roll(2)+1

        ball = Ball(
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
              Ball.Sound.ROLL: SoundEffect(SoundCh.BALL, SoundId.BALL+0),
              Ball.Sound.CRASH: SoundEffect(SoundCh.BALL, SoundId.BALL+1),
              Ball.Sound.BURST: SoundEffect(SoundCh.BALL, SoundId.BALL+2),
            },
            stopwatch=stopwatch,
            param=Ball.Param(
              rolling_distance=distance,
              max_accel=0,
              rolling_period=1,
              default_acquirement_points={
                Ball.Action.ROLL: 10,
                Ball.Action.BURST: 30
              },
            ),
          )

      elif level.stage in [
        GameLevelStage.STAGE_4,
        GameLevelStage.STAGE_5,
        GameLevelStage.STAGE_6,
      ]:
        distance = 1
        if level.stage == GameLevelStage.STAGE_4:
          distance = 2
        elif level.stage == GameLevelStage.STAGE_5:
          distance = Dice.roll(1)+2
        elif level.stage == GameLevelStage.STAGE_6:
          distance = Dice.roll(2)+1

        ball = Ball(
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
              Ball.Sound.ROLL: SoundEffect(SoundCh.BALL, SoundId.BALL+0),
              Ball.Sound.CRASH: SoundEffect(SoundCh.BALL, SoundId.BALL+1),
              Ball.Sound.BURST: SoundEffect(SoundCh.BALL, SoundId.BALL+2),
            },
            param=Ball.Param(
              rolling_distance=distance,
              max_accel=0,
              rolling_period=1,
              default_acquirement_points={
                Ball.Action.ROLL: 20,
                Ball.Action.BURST: 40
              },
            ),
          )

    return ball

  @classmethod
  def next_ball_msec(cls, level: GameLevel, balls: list[Ball]) -> int:
    msec = 0
    if len(balls) > 0:
      if level.mode == GameLevelMode.NORMAL:
        if level.stage in [
          GameLevelStage.STAGE_1,
          GameLevelStage.STAGE_2,
        ]:
          msec = 2000

        elif level.stage in [
          GameLevelStage.STAGE_3,
        ]:
          msec = (Dice.roll(1)+2)*1000

        elif level.stage in [
          GameLevelStage.STAGE_4,
          GameLevelStage.STAGE_5,
        ]:
          msec = 2000

        elif level.stage in [
          GameLevelStage.STAGE_6,
        ]:
          msec = (Dice.roll(2)+1)*1000

    return msec

  @classmethod
  def can_roll_ball(cls, level: GameLevel, field: Field, ball: Ball, last_ball: Ball | None) -> int:
    roll = False
    if ball.rolled_timer.over:
      roll = True

    if last_ball is not None:
      if last_ball.param.rolling_distance < ball.param.rolling_distance:
        if level.mode == GameLevelMode.NORMAL:
          if level.stage in [
            GameLevelStage.STAGE_1,
            GameLevelStage.STAGE_2,
          ]:
            distance = field.max_size.width/2

          elif level.stage in [
            GameLevelStage.STAGE_3,
          ]:
            distance = field.max_size.width/3

          elif level.stage in [
            GameLevelStage.STAGE_4,
            GameLevelStage.STAGE_5,
          ]:
            distance = field.max_size.width/2

          elif level.stage in [
            GameLevelStage.STAGE_6,
          ]:
            distance = field.max_size.width/3

        if last_ball.origin.x < distance:
          roll = False

    return roll

  @classmethod
  def play_limit_msec(cls, level: GameLevel) -> int:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.STAGE_1,
        GameLevelStage.STAGE_2,
        GameLevelStage.STAGE_3,
      ]:
        limit_msec = 15000

      elif level.stage in [
        GameLevelStage.STAGE_4,
        GameLevelStage.STAGE_5,
        GameLevelStage.STAGE_6,
      ]:
        limit_msec = 30000

    return limit_msec
