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


TILE_ID = 0

class TileX(IntEnum):
  FIELD = 0

IMAGE_ID = 0

class ImageX(IntEnum):
  BALL = 0
  JUMPER = 1
  LIFE = 3

class SoundCh(IntEnum):
  JUMPER = 0
  BALL = 1
  SCENE = 2

SOUND_CHS: dict[int, int] = {
  SoundCh.JUMPER: 2,
  SoundCh.BALL: 2,
  SoundCh.SCENE: 3,
}

class SoundId(IntEnum):
  JUMPER = 0
  BALL = 10
  SCENE = 20

class SceneSound(IntEnum):
  START = 0
  READY = 1
  PAUSE = 2
  TIME_UP = 3
  GAME_OVER = 4
  STAGE_CLEAR = 5
  SELECT = 6
  RESTART = 7

SCENES_SOUNDS: dict[int, SoundEffect] = {
  SceneSound.READY: SoundEffect(SOUND_CHS[SoundCh.SCENE], SoundId.SCENE+0),
  SceneSound.PAUSE: SoundEffect(SOUND_CHS[SoundCh.SCENE], SoundId.SCENE+1),
  SceneSound.TIME_UP: SoundEffect(SOUND_CHS[SoundCh.SCENE], SoundId.SCENE+2),
  SceneSound.GAME_OVER: SoundEffect(SOUND_CHS[SoundCh.SCENE], SoundId.SCENE+3),
  SceneSound.STAGE_CLEAR: SoundEffect(SOUND_CHS[SoundCh.SCENE], SoundId.SCENE+4),
  SceneSound.SELECT: SoundEffect(SOUND_CHS[SoundCh.SCENE], SoundId.SCENE+5),
  SceneSound.RESTART: SoundEffect(SOUND_CHS[SoundCh.SCENE], SoundId.SCENE+6),
  SceneSound.START: SoundEffect(SOUND_CHS[SoundCh.SCENE], SoundId.SCENE+7),
}


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
          [TileMap(TILE_ID, Coordinate(TileX.FIELD, 0), Size(2.5, 2), Image.Pose.NORMAL)],
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
          [TileMap(TILE_ID, Coordinate(TileX.FIELD, 0), Size(2.5, 2), Image.Pose.NORMAL)],
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
            Image(IMAGE_ID, Coordinate(ImageX.JUMPER, 0), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height))),
          Jumper.Motion.WALK: Block(
            Image(IMAGE_ID, Coordinate(ImageX.JUMPER, 1), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JUMP: Block(
            Image(IMAGE_ID, Coordinate(ImageX.JUMPER, 2), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.FALL_DOWN: Block(
            Image(IMAGE_ID, Coordinate(ImageX.JUMPER, 3), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JOY: Block(
            Image(IMAGE_ID, Coordinate(ImageX.JUMPER, 4), Size(1, 1), Image.Pose.NORMAL),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
        },
        {
          Jumper.Sound.WALK: SoundEffect(SOUND_CHS[SoundCh.JUMPER], SoundId.JUMPER+0),
          Jumper.Sound.JUMP: SoundEffect(SOUND_CHS[SoundCh.JUMPER], SoundId.JUMPER+1),
          Jumper.Sound.FALL_DOWN: SoundEffect(SOUND_CHS[SoundCh.JUMPER], SoundId.JUMPER+2),
          Jumper.Sound.JOY: SoundEffect(SOUND_CHS[SoundCh.JUMPER], SoundId.JUMPER+3),
          Jumper.Sound.DAMAGE: SoundEffect(SOUND_CHS[SoundCh.JUMPER], SoundId.JUMPER+4),
        },
        Jumper.Param(3, -10, 0.5, 4, 3),
      )
    return jumper

  @classmethod
  def ball(cls, level: GameLevel) -> Ball:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.NORMAL_1.value.stage,
        GameLevelStage.NORMAL_2.value.stage,
        GameLevelStage.NORMAL_3.value.stage,
      ]:
        ball = Ball(
            {
              Ball.Motion.ANGLE_0: Block(
                Image(IMAGE_ID, Coordinate(ImageX.BALL, 0), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_90: Block(
                Image(IMAGE_ID, Coordinate(ImageX.BALL, 0), Size(1, 1), Image.Pose.MIRROR_Y),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_180: Block(
                Image(IMAGE_ID, Coordinate(ImageX.BALL, 0), Size(1, 1), Image.Pose.MIRROR_XY),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_270: Block(
                Image(IMAGE_ID, Coordinate(ImageX.BALL, 0), Size(1, 1), Image.Pose.MIRROR_X),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.BURST: Block(
                Image(IMAGE_ID, Coordinate(ImageX.BALL, 1), Size(1, 1), Image.Pose.NORMAL),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
            },
            {
              Ball.Sound.ROLL: SoundEffect(SOUND_CHS[SoundCh.BALL], SoundId.BALL+0),
              Ball.Sound.CRASH: SoundEffect(SOUND_CHS[SoundCh.BALL], SoundId.BALL+1),
              Ball.Sound.BURST: SoundEffect(SOUND_CHS[SoundCh.BALL], SoundId.BALL+2),
            },
            Ball.Param(
              2 if level.stage == GameLevelStage.NORMAL_1.value.stage else Dice.roll(3)+1,
              1,
              {
                Ball.Action.ROLL: 10,
                Ball.Action.BURST: 30
              },
            ),
          )
    return ball

  @classmethod
  def next_ball_frame_count(cls, level: GameLevel, config: GameConfig) -> int:
    if level.mode == GameLevelMode.NORMAL:
      if level.stage in [
        GameLevelStage.NORMAL_1.value.stage,
        GameLevelStage.NORMAL_2.value.stage,
        GameLevelStage.NORMAL_4.value.stage,
        GameLevelStage.NORMAL_5.value.stage,
      ]:
        next_frame = config.frame_count(2000)
      elif level.stage in [
        GameLevelStage.NORMAL_3.value.stage,
        GameLevelStage.NORMAL_6.value.stage,
      ]:
        next_frame = config.frame_count((Dice.roll(3)+1)*1000)
    return next_frame

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
