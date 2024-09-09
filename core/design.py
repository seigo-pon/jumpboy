from enum import IntEnum
from game import (
  Coordinate, Size, Stopwatch, Dice,
  AssetImageId, Image, TileMap,
  Collision, Block, Obstacle,
  GameConfig,
)
from core import (
  GameLevel, Field, Jumper, Ball,
)


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
  FIRST_LEVEL = GameLevel(GameLevelMode.NORMAL, GameLevelStage.STAGE_1)

  class FieldSurface(IntEnum):
    ROAD = 0
    GRASS = 1
    CLAY = 2
    WOOD = 3

  @classmethod
  def field(cls, level: GameLevel, config: GameConfig) -> Field:
    if level.mode == GameLevelMode.NORMAL:
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
          surface=cls.FieldSurface.ROAD,
          ground_height=cls.GROUND_TOP,
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
          max_size=config.window_size,
          surface=cls.FieldSurface.GRASS,
          ground_height=cls.GROUND_TOP,
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
          surface=cls.FieldSurface.CLAY,
          ground_height=cls.GROUND_TOP,
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
                Coordinate(0, cls.GROUND_TOP-TileMap.basic_size().height*2),
                Size(0, TileMap.basic_size().height*2),
              ),
            ),
            Obstacle(
              Collision(
                Coordinate(config.window_size.width, cls.GROUND_TOP-TileMap.basic_size().height*2),
                Size(0, TileMap.basic_size().height*2),
              ),
            ),
          ],
          max_size=config.window_size,
          surface=cls.FieldSurface.WOOD,
          ground_height=cls.GROUND_TOP,
        )

    return field

  @classmethod
  def jumper(cls, level: GameLevel, stopwatch: Stopwatch) -> Jumper:
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
          max_life=3,
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

  @classmethod
  def ball(cls, level: GameLevel, stopwatch: Stopwatch) -> Ball:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.STAGE_1,
        GameLevelStage.STAGE_2,
        GameLevelStage.STAGE_3,
      ]:
        distance = 2
        if level.stage == GameLevelStage.STAGE_1:
          distance = 2
        elif level.stage == GameLevelStage.STAGE_2:
          distance = 3
        elif level.stage == GameLevelStage.STAGE_3:
          distance = Dice.roll(1)+2

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
              Ball.Sound.ROLL: SoundId.BALL+0,
              Ball.Sound.CRASH: SoundId.BALL+1,
              Ball.Sound.BURST: SoundId.BALL+2,
              Ball.Sound.LEAP: SoundId.BALL+3,
            },
            stopwatch=stopwatch,
            param=Ball.Param(
              roll_distance=distance,
              max_accel=0,
              roll_period=1,
              max_points={
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
        distance = 2
        if level.stage == GameLevelStage.STAGE_4:
          distance = 2
        elif level.stage == GameLevelStage.STAGE_5:
          distance = 3
        elif level.stage == GameLevelStage.STAGE_6:
          distance = Dice.roll(2)+1

        ball = Ball(
            name='bound_ball',
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
              Ball.Sound.ROLL: SoundId.BALL+0,
              Ball.Sound.CRASH: SoundId.BALL+1,
              Ball.Sound.BURST: SoundId.BALL+2,
            },
            stopwatch=stopwatch,
            param=Ball.Param(
              roll_distance=distance,
              max_accel=0,
              roll_period=1,
              max_points={
                Ball.Action.ROLL: 20,
                Ball.Action.BURST: 40
              },
            ),
          )

    return ball

  @classmethod
  def next_ball_msec(cls, level: GameLevel, balls: list[Ball]) -> int | None:
    msec: int | None = 0
    if len(balls) > 0:
      if level.mode == GameLevelMode.NORMAL:
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
          msec = (Dice.roll(1)+1)*1000

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
          if len(balls) < 4:
            msec = 2000
          else:
            msec = None

        elif level.stage in [
          GameLevelStage.STAGE_6,
        ]:
          if len(balls) < 6:
            msec = (Dice.roll(1)+1)*1000
          else:
            msec = None

    return msec

  @classmethod
  def can_roll_ball(cls, level: GameLevel, field: Field, ball: Ball, last_ball: Ball | None) -> int:
    roll = False
    if ball.rolled_timer is None or ball.rolled_timer.over:
      roll = True

    if last_ball is not None:
      if level.mode == GameLevelMode.NORMAL:
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

      if last_ball.left < distance:
        roll = False

    return roll

  @classmethod
  def play_limit_msec(cls, level: GameLevel) -> int:
    if level.mode == GameLevelMode.NORMAL:
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

    return limit_msec

  @classmethod
  def recovery_life_count(cls, level: GameLevel) -> int:
    if level.mode == GameLevelMode.NORMAL:
      life = 2

    elif level.mode == GameLevelMode.HARD:
      life = 1

    return life
