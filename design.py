from enum import Enum, IntEnum
from game import (
  Coordinate, Size, Dice,
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

class GameLevelStage(Enum):
  NORMAL_1 = GameLevel(GameLevelMode.NORMAL, 0)
  NORMAL_2 = GameLevel(GameLevelMode.NORMAL, 1)
  NORMAL_3 = GameLevel(GameLevelMode.NORMAL, 2)
  NORMAL_4 = GameLevel(GameLevelMode.NORMAL, 3)
  NORMAL_5 = GameLevel(GameLevelMode.NORMAL, 4)
  NORMAL_6 = GameLevel(GameLevelMode.NORMAL, 5)


class GameDesign:
  GROUND_TOP = TileMap.basic_size().height+TileMap.basic_size().height*(3/4)

  class FieldSurface(IntEnum):
    NORMAL = 0
    FENCE = 1

  @classmethod
  def field(cls, level: GameLevel, config: GameConfig) -> Field:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.NORMAL_1.value.stage,
        GameLevelStage.NORMAL_2.value.stage,
        GameLevelStage.NORMAL_3.value.stage,
      ]:
        field = Field(
          [TileMap(TileId.FIELD.id, Coordinate(TileId.FIELD.x, 0), Size(2.5, 2), Image.Pose.NORMAL)],
          [],
          config.window_size,
          cls.FieldSurface.NORMAL,
          cls.GROUND_TOP,
        )

      elif level.stage in [
        GameLevelStage.NORMAL_4.value.stage,
        GameLevelStage.NORMAL_5.value.stage,
        GameLevelStage.NORMAL_6.value.stage,
      ]:
        field = Field(
          [TileMap(TileId.FIELD.id, Coordinate(TileId.FIELD.x, 0), Size(2.5, 2), Image.Pose.NORMAL)],
          [
            Obstacle(
              Collision(
                Coordinate(0, cls.GROUND_TOP-Image.basic_size().height),
                Size(0, Image.basic_size().height),
              ),
            ),
            Obstacle(
              Collision(
                Coordinate(config.window_size.width, cls.GROUND_TOP-Image.basic_size().height),
                Size(0, Image.basic_size().height),
              ),
            ),
          ],
          config.window_size,
          cls.FieldSurface.FENCE,
          cls.GROUND_TOP,
        )

    return field

  @classmethod
  def jumper(cls, level: GameLevel) -> Jumper:
    if level.mode == GameLevelMode.NORMAL:
      jumper = Jumper(
        {
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
        {
          Jumper.Sound.WALK: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+0),
          Jumper.Sound.JUMP: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+1),
          Jumper.Sound.FALL_DOWN: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+2),
          Jumper.Sound.JOY: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+3),
          Jumper.Sound.DAMAGE: SoundEffect(SoundCh.JUMPER, SoundId.JUMPER+4),
        },
        Jumper.Param(3, -10, 0.5, 4, 3),
      )

    return jumper

  @classmethod
  def ball(cls, level: GameLevel) -> Ball:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.NORMAL_1.value.stage,
      ]:
        ball = Ball(
            {
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
            {
              Ball.Sound.ROLL: SoundEffect(SoundCh.BALL, SoundId.BALL+0),
              Ball.Sound.CRASH: SoundEffect(SoundCh.BALL, SoundId.BALL+1),
              Ball.Sound.BURST: SoundEffect(SoundCh.BALL, SoundId.BALL+2),
            },
            Ball.Param(
              2,
              1,
              {
                Ball.Action.ROLL: 10,
                Ball.Action.BURST: 30
              },
            ),
          )

      elif level.stage in [
        GameLevelStage.NORMAL_2.value.stage,
        GameLevelStage.NORMAL_3.value.stage,
      ]:
        ball = Ball(
            {
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
            {
              Ball.Sound.ROLL: SoundEffect(SoundCh.BALL, SoundId.BALL+0),
              Ball.Sound.CRASH: SoundEffect(SoundCh.BALL, SoundId.BALL+1),
              Ball.Sound.BURST: SoundEffect(SoundCh.BALL, SoundId.BALL+2),
            },
            Ball.Param(
              Dice.roll(3)+1,
              1,
              {
                Ball.Action.ROLL: 10,
                Ball.Action.BURST: 30
              },
            ),
          )

    return ball

  @classmethod
  def next_ball(cls, level: GameLevel, config: GameConfig, balls: list[Ball] | None) -> bool:
    next_ball = False
    if len(balls) > 0:
      balls = sorted([ball for ball in balls], key=lambda x: x.frame)
    else:
      next_ball = True

    if not next_ball:
      if level.mode == GameLevelMode.NORMAL:
        if level.stage in [
          GameLevelStage.NORMAL_1.value.stage,
          GameLevelStage.NORMAL_2.value.stage,
        ]:
          if balls[0].frame >= config.frame_count(2000):
            next_ball = True

        elif level.stage in [
          GameLevelStage.NORMAL_3.value.stage,
        ]:
          if balls[0].frame >= config.frame_count((Dice.roll(3)+1)*1000):
            next_ball = True

        elif level.stage in [
          GameLevelStage.NORMAL_4.value.stage,
          GameLevelStage.NORMAL_5.value.stage,
        ]:
          if len(balls) < 2:
            if balls[0].frame >= config.frame_count(2000):
              next_ball = True

        elif level.stage in [
          GameLevelStage.NORMAL_6.value.stage,
        ]:
          if len(balls) < 3:
            if balls[0].frame >= config.frame_count((Dice.roll(3)+1)*1000):
              next_ball = True

    return next_ball

  @classmethod
  def play_limit_msec(cls, level: GameLevel) -> int:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.NORMAL_1.value.stage,
        GameLevelStage.NORMAL_2.value.stage,
        GameLevelStage.NORMAL_3.value.stage,
      ]:
        limit_msec = 15000

      elif level.stage in [
        GameLevelStage.NORMAL_4.value.stage,
        GameLevelStage.NORMAL_5.value.stage,
        GameLevelStage.NORMAL_6.value.stage,
      ]:
        limit_msec = 30000

    return limit_msec
