from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Self
from game import (
  Coordinate, Size, Stopwatch, Timer,
  AssetImage, Image, TileMap, SoundEffect,
  Collision, Block, Obstacle, TextScriber, Text, Signboard, MusicBox,
  GameConfig, Language, StringRes, Seq, TimeSeq,
)
from core import (
  GamePad,
  GameLevel, Score, ScoreBoard,
  Ball, Jumper, Field, BlinkText,
  Snapshot, Scene,
)
import pyxel


GROUND_TOP = TileMap.basic_size().height+TileMap.basic_size().height*(3/4)
TEXT_FONT_SIZE = 10

TILE_ID = 0
FIELD_TILE_X = 0

IMAGE_ID = 0
JUMPER_IMAGE_X = 1
BALL_IMAGE_X = 0

JUMPER_SOUND_CH = 3
JUMPER_SOUND_ID = 0
BALL_SOUND_CH = 3
BALL_SOUND_ID = 10
SCENE_SOUND_CH = 3
SCENE_SOUND_ID = 20


class GameLevelAll(Enum):
  NORMAL_1 = GameLevel(0, 0)
  NORMAL_2 = GameLevel(0, 1)

  @classmethod
  def next(cls, level: GameLevel) -> GameLevel | None:
    try:
      levels = list([e.value for e in GameLevelAll])
      index = levels.index(level)
      next_level = levels[index+1]
      print('next level', next_level)
      return next_level
    except:
      print('next level none')

    return None

  @classmethod
  def field(cls, level: GameLevel, config: GameConfig) -> Field:
    if level.mode in [
      GameLevelAll.NORMAL_1.value.mode,
      GameLevelAll.NORMAL_2.value.mode,
    ]:
      if level.stage == GameLevelAll.NORMAL_1.value.stage:
        return Field(
          [
            TileMap(TILE_ID, Coordinate(FIELD_TILE_X, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
            TileMap(TILE_ID, Coordinate(FIELD_TILE_X, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
            TileMap(TILE_ID, Coordinate(FIELD_TILE_X, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
          ],
          [],
          config.window_size,
          GROUND_TOP,
        )
      elif level.stage == GameLevelAll.NORMAL_2.value.stage:
        return Field(
          [
            TileMap(TILE_ID, Coordinate(FIELD_TILE_X, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
            TileMap(TILE_ID, Coordinate(FIELD_TILE_X, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
            TileMap(TILE_ID, Coordinate(FIELD_TILE_X, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
          ],
          [
            Obstacle(
              Collision(
                Coordinate(0, GROUND_TOP-Image.basic_size().height),
                Size(0, Image.basic_size().height),
              ),
            ),
            Obstacle(
              Collision(
                Coordinate(config.window_size.width, GROUND_TOP-Image.basic_size().height),
                Size(0, Image.basic_size().height),
              ),
            ),
          ],
          config.window_size,
          GROUND_TOP,
        )

    raise RuntimeError()

  @classmethod
  def jumper(cls, level: GameLevel, config: GameConfig) -> Jumper:
    if level.mode in [
      GameLevelAll.NORMAL_1.value.mode,
      GameLevelAll.NORMAL_2.value.mode,
    ]:
      return Jumper(
        {
          Jumper.Motion.STOP: Block(
            Image(IMAGE_ID, Coordinate(JUMPER_IMAGE_X, 0), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height))),
          Jumper.Motion.WALK: Block(
            Image(IMAGE_ID, Coordinate(JUMPER_IMAGE_X, 1), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JUMP: Block(
            Image(IMAGE_ID, Coordinate(JUMPER_IMAGE_X, 2), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.FALL_DOWN: Block(
            Image(IMAGE_ID, Coordinate(JUMPER_IMAGE_X, 3), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Jumper.Motion.JOY: Block(
            Image(IMAGE_ID, Coordinate(JUMPER_IMAGE_X, 4), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
        },
        {
          Jumper.Sound.WALK: SoundEffect(JUMPER_SOUND_CH, JUMPER_SOUND_ID+0),
          Jumper.Sound.JUMP: SoundEffect(JUMPER_SOUND_CH, JUMPER_SOUND_ID+1),
          Jumper.Sound.FALL_DOWN: SoundEffect(JUMPER_SOUND_CH, JUMPER_SOUND_ID+2),
          Jumper.Sound.JOY: SoundEffect(JUMPER_SOUND_CH, JUMPER_SOUND_ID+3),
          Jumper.Sound.DAMAGE: SoundEffect(JUMPER_SOUND_CH, JUMPER_SOUND_ID+4),
        },
        Jumper.Param(3, 2, 30, -10, 0.5, 4, 3),
      )

    raise RuntimeError()

  @classmethod
  def ball(cls, level: GameLevel, config: GameConfig) -> Ball:
    if level.mode in [
      GameLevelAll.NORMAL_1.value.mode,
      GameLevelAll.NORMAL_2.value.mode,
    ]:
      if level.stage in [
        GameLevelAll.NORMAL_1.value.stage,
        GameLevelAll.NORMAL_2.value.stage,
      ]:
        return Ball(
            {
              Ball.Motion.ANGLE_0: Block(
                Image(IMAGE_ID, Coordinate(BALL_IMAGE_X, 0), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_90: Block(
                Image(IMAGE_ID, Coordinate(BALL_IMAGE_X, 0), Size(1, 1), Image.Pose.MIRROR_Y, config.transparent_color),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_180: Block(
                Image(IMAGE_ID, Coordinate(BALL_IMAGE_X, 0), Size(1, 1), Image.Pose.MIRROR_XY, config.transparent_color),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.ANGLE_270: Block(
                Image(IMAGE_ID, Coordinate(BALL_IMAGE_X, 0), Size(1, 1), Image.Pose.MIRROR_X, config.transparent_color),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
              Ball.Motion.BURST: Block(
                Image(IMAGE_ID, Coordinate(BALL_IMAGE_X, 1), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
                Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
              ),
            },
            {
              Ball.Sound.ROLL: SoundEffect(BALL_SOUND_CH, BALL_SOUND_ID+0),
              Ball.Sound.CRASH: SoundEffect(BALL_SOUND_CH, BALL_SOUND_ID+1),
              Ball.Sound.BURST: SoundEffect(BALL_SOUND_CH, BALL_SOUND_ID+2),
            },
            Ball.Param(2, 1, 10),
          )

    raise RuntimeError()

  @classmethod
  def balls(cls, level: GameLevel, config: GameConfig) -> list[Ball]:
    if level.mode in [
      GameLevelAll.NORMAL_1.value.mode,
      GameLevelAll.NORMAL_2.value.mode,
    ]:
      if level.stage in [
        GameLevelAll.NORMAL_1.value.stage,
        GameLevelAll.NORMAL_2.value.stage,
      ]:
        return [GameLevelAll.ball(level, config)]

    raise RuntimeError()

  @classmethod
  def play_limit_msec(cls, level: GameLevel) -> int:
    if level.mode in [
      GameLevelAll.NORMAL_1.value.mode,
      GameLevelAll.NORMAL_2.value.mode,
    ]:
      if level.stage in [
        GameLevelAll.NORMAL_1.value.stage,
        GameLevelAll.NORMAL_2.value.stage,
      ]:
        return 15000

    raise RuntimeError()


GAME_TITLE: dict[int, str] = {
  GameLevelAll.NORMAL_1.value.mode: 'game_title_1',
}
SCORE: dict[int, str] = {
  GameLevelAll.NORMAL_1.value.mode: 'score_title_1',
}
TEXT_COLOR = pyxel.COLOR_WHITE

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
  SceneSound.READY: SoundEffect(SCENE_SOUND_CH, SCENE_SOUND_ID+0),
  SceneSound.PAUSE: SoundEffect(SCENE_SOUND_CH, SCENE_SOUND_ID+1),
  SceneSound.TIME_UP: SoundEffect(SCENE_SOUND_CH, SCENE_SOUND_ID+2),
  SceneSound.GAME_OVER: SoundEffect(SCENE_SOUND_CH, SCENE_SOUND_ID+3),
  SceneSound.STAGE_CLEAR: SoundEffect(SCENE_SOUND_CH, SCENE_SOUND_ID+4),
  SceneSound.SELECT: SoundEffect(SCENE_SOUND_CH, SCENE_SOUND_ID+5),
  SceneSound.RESTART: SoundEffect(SCENE_SOUND_CH, SCENE_SOUND_ID+6),
  SceneSound.START: SoundEffect(SCENE_SOUND_CH, SCENE_SOUND_ID+7),
}


class BaseScene(Scene):
  JUMPER_START_X = Image.basic_size().width*5

  def __init__(
    self,
    config: GameConfig,
    string_res: StringRes,
    stopwatch: Stopwatch,
    scriber: TextScriber,
    music_box: MusicBox,
    snapshot: Snapshot,
  ) -> None:
    super().__init__(config, string_res, stopwatch, scriber, music_box, snapshot)

  def menu_left_top_origin(self) -> Coordinate:
    return Coordinate(0, 0)

  def menu_middle_top_center(self, size: Size | None) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      (size.height if size is not None else TextScriber.word_size(TEXT_FONT_SIZE).height)/2,
    )

  def menu_right_top_origin(self, text: Text) -> Coordinate:
    return Coordinate(self.config.window_size.width-text.size.width, 0)

  def title_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      TextScriber.word_size(TEXT_FONT_SIZE).height*2+TextScriber.word_size(TEXT_FONT_SIZE).height/2,
    )

  def subtitle_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      TextScriber.word_size(TEXT_FONT_SIZE).height*3+TextScriber.word_size(TEXT_FONT_SIZE).height/2,
    )

  def menu_middle_center(self) -> Coordinate:
    return Coordinate(self.config.window_size.center.x, self.config.window_size.center.y)

  def menu_middle_bottom_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      self.snapshot.field.ground_height
      -TextScriber.word_size(TEXT_FONT_SIZE).height*2
      +TextScriber.word_size(TEXT_FONT_SIZE).height/2,
    )

  def ball_start_origin(self, ball: Ball) -> Coordinate:
    return Coordinate(
      self.snapshot.field.left-ball.size.width,
      self.snapshot.field.bottom-ball.size.height,
    )

  def jumper_start_origin(self, jumper: Jumper) -> Coordinate:
    return Coordinate(
      self.snapshot.field.right,
      self.snapshot.field.bottom-jumper.size.height,
    )

  def jumper_play_x(self) -> float:
    return self.snapshot.field.right-self.JUMPER_START_X

  def text(self, string: str) -> Text:
    return Text(string, TEXT_COLOR, TEXT_FONT_SIZE, False, self.scriber)

  def blink_text(self, string: str, msec: int, show: bool) -> BlinkText:
    return BlinkText(
      string,
      TEXT_COLOR,
      TEXT_FONT_SIZE,
      False,
      self.scriber,
      self.stopwatch,
      msec,
      show,
    )

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects: list[Any] = [self.snapshot.field]
    subjects += [ball for ball in self.snapshot.balls]
    subjects.append(self.snapshot.jumper)

    if self.config.debug:
      stopwatch_text = Text(
        '{:02}:{:02}:{:02}:{:03}'.format(
          int(self.stopwatch.sec/60/60),
          int(self.stopwatch.sec/60%60),
          int(self.stopwatch.sec%60),
          self.stopwatch.msec%1000,
        ),
        pyxel.COLOR_BLACK,
        10,
        False,
        self.scriber,
      )
      stopwatch_text.origin = Coordinate(
        self.config.window_size.width-stopwatch_text.size.width,
        self.config.window_size.height-stopwatch_text.size.height,
      )
      subjects.append(stopwatch_text)

    return subjects


class OpeningScene(BaseScene):
  MOVE_TITLE_Y_MIN = 1

  def __init__(self, config: GameConfig, string_res: StringRes) -> None:
    stopwatch = Stopwatch(config.fps)
    level = GameLevelAll.NORMAL_1.value

    super().__init__(
      config,
      string_res,
      stopwatch,
      TextScriber(),
      MusicBox(),
      Snapshot(
        Language.EN,
        GamePad(),
        ScoreBoard(),
        level,
        GameLevelAll.field(level, config),
        [],
        GameLevelAll.jumper(level, config),
      ),
    )

    self.snapshot.load(self.config.path)
    self.title = self.string(GAME_TITLE[self.snapshot.level.mode])

    self.snapshot.field = GameLevelAll.field(self.snapshot.level, self.config)
    self.snapshot.balls = []
    self.snapshot.jumper = GameLevelAll.jumper(self.snapshot.level, self.config)
    self.snapshot.jumper.origin = self.jumper_start_origin(self.snapshot.jumper)

    self.title_text: Text | None = None

    def walk_jumper(start: bool, timer: Timer) -> bool:
      if start:
        self.snapshot.jumper.walk(self.jumper_play_x())
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    def move_title(start: bool, timer: Timer) -> bool:
      if self.title_text is None:
        self.title_text = self.text(self.config.title)
        self.title_text.center = Coordinate(
          self.title_center().x,
          -TextScriber.word_size(TEXT_FONT_SIZE).height,
        )
        self.title_text.move(self.title_center(), 0.5)
      else:
        if self.title_text.moving:
          return True

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 500, walk_jumper, None),
      Seq(self.stopwatch, 2000, move_title, None),
      Seq(self.stopwatch, 3000, lambda x, y: True, lambda: TitleScene(self)),
    ])

  @property
  def updating_variations(self) -> list[Any]:
    variations = super().updating_variations

    if self.title_text is not None:
      variations.append(self.title_text)

    return variations

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter(False):
      return TitleScene(self)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.title_text is not None:
      subjects.append(self.title_text)

    return subjects


class TitleScene(BaseScene):
  START_TEXT = 1
  SCORE_RANKING_NUM = 3

  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.config,
      scene.string_res,
      scene.stopwatch,
      scene.scriber,
      scene.music_box,
      scene.snapshot,
    )

    self.snapshot.jumper.walk(self.jumper_play_x())

    self.title_text = self.text(self.config.title)
    self.title_text.center = self.title_center()

    self.show_start = True
    self.start_text = self.blink_text(self.string('game_start_text'), 1000, True)
    self.start_text.center = self.menu_middle_center()
    self.wait_start = False

    self.show_score = False
    self.score = self.scoreboard()
    self.score.center = Coordinate(self.menu_middle_top_center(None).x, -self.score.size.height/2)

    def walk_jumper(start: bool, timer: Timer) -> bool:
      if start:
        self.snapshot.jumper.walk(self.snapshot.field.right)
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    def show_score(start: bool, timer: Timer):
      if start:
        self.show_score = True
        self.score.move(
          self.menu_middle_top_center(
            Size(
              self.score.size.width,
              self.score.size.height+TextScriber.word_size(TEXT_FONT_SIZE).height*2,
            )
          ),
          0.5,
        )
        self.show_start = False
      else:
        if not self.score.moving:
          self.show_start = True
          self.start_text.center = Coordinate(
            self.menu_middle_center().x,
            self.menu_middle_center().y+TextScriber.word_size(TEXT_FONT_SIZE).height*2,
          )
          return True

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 20000, walk_jumper, None),
      Seq(self.stopwatch, 1000, show_score, None),
    ])

  def scoreboard(self) -> Signboard:
    score_texts: list[Text] = []

    score_center = self.menu_middle_top_center(None)
    title_text = self.text(self.string('score_ranking_title'))
    title_text.center = Coordinate(score_center.x, score_center.y)
    score_texts.append(title_text)

    score_center.y += TextScriber.word_size(title_text.font_size).height*2
    scores = self.snapshot.score_board.ranking(self.SCORE_RANKING_NUM)
    if len(scores) > 0:
      for (index, score) in enumerate(scores):
        score_text = self.text(
          '{}.{}.{:02} {:04} {}'.format(
            index+1,
            self.string(SCORE[score.level.mode]),
            score.level.stage+1,
            score.point,
            score.created_at.strftime('%Y/%m/%d %H:%M'),
          )
        )
        score_text.center = Coordinate(score_center.x, score_center.y)
        score_texts.append(score_text)
        score_center.y += TextScriber.word_size(score_text.font_size).height
    else:
      no_score_text = self.text(self.string('score_no_text'))
      no_score_text.center = Coordinate(score_center.x, score_center.y)
      score_texts.append(no_score_text)

    return Signboard(None, score_texts, self.config.window_size.width, None)

  @property
  def updating_variations(self) -> list[Any]:
    variations = super().updating_variations

    if self.show_score:
      variations.append(self.score)
    variations.append(self.start_text)

    return variations

  def update(self) -> Self | Any:
    if not self.wait_start:
      if self.snapshot.game_pad.enter(False):
        self.wait_start = True
        self.start_text.set_msec(120, True)
        self.time_seq = TimeSeq([
          Seq(self.stopwatch, 1000, lambda x, y: True, lambda: ReadyScene(self, 0, None, {})),
        ])
        SCENES_SOUNDS[SceneSound.SELECT].play()

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_score:
      subjects.append(self.score)
    else:
      subjects.append(self.title_text)

    if self.show_start:
      subjects.append(self.start_text)

    copyright_text = self.text('© {} {}'.format(self.config.released_year, self.config.copyright))
    copyright_text.center = self.menu_middle_bottom_center()
    subjects.append(copyright_text)

    return subjects


class BaseStageScene(BaseScene):
  def __init__(
    self,
    scene: Scene,
    point: int,
    play_timer: Timer | None,
    ball_last_directions: dict[str, bool],
  ) -> None:
    super().__init__(
      scene.config,
      scene.string_res,
      scene.stopwatch,
      scene.scriber,
      scene.music_box,
      scene.snapshot,
    )

    self.point = point
    self.play_timer = play_timer
    self.ball_last_directions = ball_last_directions

    self.show_stage = True

  def record_score(self) -> None:
    self.snapshot.score_board.scores.append(
      Score(
        datetime.now(),
        self.snapshot.level,
        self.point,
      )
    )
    print('score record', vars(self.snapshot.score_board.scores[-1]))

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_stage:
      stage_text = self.text('{}.{:02}'.format(self.string('stage_title'), self.snapshot.level.stage+1))
      stage_text.origin = self.menu_left_top_origin()
      subjects.append(stage_text)

      if self.play_timer is not None:
        limit_msec = self.play_timer.limit_msec if self.play_timer.limit_msec is not None else 0
        remain_msec = limit_msec-self.play_timer.msec
        play_time_text = self.text(
          '{:02}:{:02}.{:03}'.format(
            int(int(remain_msec/1000)/60),
            int(int(remain_msec/1000)%60),
            remain_msec%1000,
          ),
        )
        play_time_text.center = self.menu_middle_top_center(None)
        subjects.append(play_time_text)

    score_text = self.text('{}:{:04}'.format(self.string(SCORE[self.snapshot.level.mode]), self.point))
    score_text.origin = self.menu_right_top_origin(score_text)
    subjects.append(score_text)

    life_text = self.text('{}'.format(self.snapshot.jumper.life))
    life_text.origin = Coordinate(
      self.menu_right_top_origin(life_text).x,
      self.menu_right_top_origin(life_text).y+score_text.size.height,
    )
    subjects.append(life_text)

    return subjects


class ReadyScene(BaseStageScene):
  class Describe(IntEnum):
    STAGE = 0
    READY = 1

  DESCRIBE_MSEC: dict[int, int] = {
    Describe.STAGE: 1000,
    Describe.READY: 1000,
  }
  START_MSEC = 3000

  def __init__(
    self,
    scene: Scene,
    point: int,
    play_timer: Timer | None,
    ball_last_directions: dict[str, bool],
  ) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    self.snapshot.balls = GameLevelAll.balls(self.snapshot.level, self.config)
    for ball in self.snapshot.balls:
      ball.origin = self.ball_start_origin(ball)

    self.snapshot.jumper.life = self.snapshot.jumper.param.max_life
    self.snapshot.jumper.stop()

    print('ready', vars(self.snapshot.level))
    self.play_timer = Timer.set_msec(
      self.stopwatch,
      GameLevelAll.play_limit_msec(self.snapshot.level),
      False,
    )

    self.show_stage = False

    self.describe: self.Describe | None = None
    self.ready_timer: Timer | None = None
    self.last_sec = -1

    def walk_jumper(start: bool, timer: Timer) -> bool:
      if start:
        self.snapshot.jumper.walk(self.jumper_play_x())
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    def ready_describe(start: bool, timer: Timer) -> bool:
      if self.describe is None:
        self.describe = [e for e in self.Describe][0]
        SCENES_SOUNDS[SceneSound.START].play()
      else:
        if self.describe == self.Describe.STAGE:
          self.show_stage = True

        self.describe += 1
        if self.describe > [e for e in self.Describe][-1]:
          self.describe = None
          return True

      timer.limit_msec = self.DESCRIBE_MSEC[self.describe]
      timer.reset()

      return False

    def ready_play(start: bool, timer: Timer) -> bool:
      self.ready_timer = Timer.set_msec(self.stopwatch, self.START_MSEC, True)
      self.last_sec = -1
      return True

    def start_play(start: bool, timer: Timer) -> bool:
      if self.ready_timer is not None:
        if self.ready_timer.over:
          for ball in self.snapshot.balls:
            ball.roll()
          self.snapshot.jumper.stand_by()
          return True
        else:
          last_sec = int(self.ready_timer.msec/1000)
          if self.last_sec != last_sec:
            SCENES_SOUNDS[SceneSound.READY].play()
            self.last_sec = last_sec

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 0, walk_jumper, None),
      Seq(self.stopwatch, 1000, ready_describe, None),
      Seq(self.stopwatch, 0, ready_play, None),
      Seq(self.stopwatch, 0, start_play, lambda: PlayScene(self, self.point, self.play_timer, self.ball_last_directions)),
    ])

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.describe is not None:
      if self.describe == self.Describe.STAGE:
        describe_text = self.text('{}.{:02}'.format(self.string('stage_title'), self.snapshot.level.stage+1))
        describe_text.center = self.subtitle_center()
        subjects.append(describe_text)

      elif self.describe == self.Describe.READY:
        describe_text = self.text(self.string('ready_title_1'))
        describe_text.center = self.subtitle_center()
        subjects.append(describe_text)

    elif self.ready_timer is not None:
      wait_sec = max(int(self.START_MSEC/1000)-int(self.ready_timer.msec/1000), 1)
      wait_sec = min(wait_sec, int(self.START_MSEC/1000))
      start_wait_time_text = self.text(str(wait_sec))
      start_wait_time_text.center = self.subtitle_center()
      subjects.append(start_wait_time_text)

    return subjects


class PlayScene(BaseStageScene):
  def __init__(
    self,
    scene: Scene,
    point: int,
    play_timer: Timer | None,
    ball_last_directions: dict[str, bool],
  ) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    if self.play_timer is not None:
      self.play_timer.resume()

  def update(self) -> Self | Any:
    if self.play_timer is not None:
      if self.snapshot.game_pad.cancel():
        self.play_timer.pause()
        SCENES_SOUNDS[SceneSound.PAUSE].play()
        return PauseScene(self, self.point, self.play_timer, self.ball_last_directions)

      next_balls = []
      for ball in [ball for ball in self.snapshot.balls]:
        if ball.dead:
          print('ball dead', ball.id)
          continue

        if ball.rolling_direction:
          if ball.left >= self.snapshot.field.right:
            print('ball over left', ball.id, ball.left, self.snapshot.field.right)
            self.point += ball.acquirement_point
            continue
        else:
          if ball.right <= self.snapshot.field.left:
            print('ball over right', ball.id, ball.right, self.snapshot.field.left)
            self.point += ball.acquirement_point
            continue

        next_balls.append(ball)

        if not self.snapshot.jumper.damaging:
          if ball.hit(self.snapshot.jumper):
            attack = False
            if self.snapshot.jumper.jumping:
              if self.snapshot.jumper.bottom < ball.center.y:
                if ball.left < self.snapshot.jumper.center.x < ball.right:
                  attack = True

            if attack:
              ball.burst()
              self.point += ball.acquirement_point
            else:
              ball.acquirement_point = 0
              self.snapshot.jumper.damage()

          if ball.id in self.ball_last_directions:
            if self.ball_last_directions[ball.id] != ball.rolling_direction:
              if not self.snapshot.jumper.falling_down:
                self.point += ball.acquirement_point

          self.ball_last_directions[ball.id] = ball.rolling_direction

      erased_ball_count = len(self.snapshot.balls) - len(next_balls)
      self.snapshot.balls = next_balls

      if self.snapshot.jumper.falling_down:
        self.play_timer.pause()
        for ball in self.snapshot.balls:
          ball.stop()
        return GameOverScene(self, self.point, self.play_timer, self.ball_last_directions)

      if self.play_timer.over:
        self.play_timer.pause()
        for ball in self.snapshot.balls:
          ball.stop()
        self.snapshot.jumper.stop()
        SCENES_SOUNDS[SceneSound.TIME_UP].play()
        return StageClearScene(self, self.point, self.play_timer, self.ball_last_directions)

      if erased_ball_count > 0:
        for _ in range(0, erased_ball_count):
          ball = GameLevelAll.ball(self.snapshot.level, self.config)
          ball.origin = self.ball_start_origin(ball)
          ball.roll()
          self.snapshot.balls.append(ball)

    return super().update()


class PauseScene(BaseStageScene):
  def __init__(
    self,
    scene: Scene,
    point: int,
    play_timer: Timer | None,
    ball_last_directions: dict[str, bool],
  ) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    self.restart_text = self.blink_text(self.string('game_restart_text'), 1000, True)
    self.restart_text.center = self.menu_middle_center()

  @property
  def updating_variations(self) -> list[Any]:
    variations: list[Any] = [self.restart_text]
    return variations

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter(False) or self.snapshot.game_pad.cancel():
      SCENES_SOUNDS[SceneSound.RESTART].play()
      return PlayScene(self, self.point, self.play_timer, self.ball_last_directions)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    pause_text = self.text(self.string('game_pause_text'))
    pause_text.center = self.subtitle_center()
    subjects.append(pause_text)

    subjects.append(self.restart_text)

    return subjects


class GameOverScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None, ball_last_directions: dict[str, bool]) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    self.record_score()
    self.snapshot.save(self.config.path)

    self.show_game_over = False
    self.show_game_end = False

    def show_game_over(start: bool, timer: Timer) -> bool:
      self.show_game_over = True
      SCENES_SOUNDS[SceneSound.GAME_OVER].play()
      return True

    def show_game_end(start: bool, timer: Timer) -> bool:
      self.show_game_end = True
      return True

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 1000, show_game_over, None),
      Seq(self.stopwatch, 2000, show_game_end, None),
    ])

  def update(self) -> Self | Any:
    if self.time_seq.ended:
      if self.snapshot.game_pad.enter(False):
        self.snapshot.level = GameLevelAll.NORMAL_1.value

        self.snapshot.field = GameLevelAll.field(self.snapshot.level, self.config)
        self.snapshot.balls = []
        self.snapshot.jumper = GameLevelAll.jumper(self.snapshot.level, self.config)
        self.snapshot.jumper.origin = self.jumper_start_origin(self.snapshot.jumper)

        self.snapshot.save(self.config.path)
        return TitleScene(self)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_game_over:
      game_over_text = self.text(self.string('game_over_title'))
      game_over_text.center = self.subtitle_center()
      subjects.append(game_over_text)

    if self.show_game_end:
      end_text = self.text(self.string('game_over_text'))
      end_text.center = self.menu_middle_center()
      subjects.append(end_text)

    return subjects


class StageClearScene(BaseStageScene):
  def __init__(
    self,
    scene: Scene,
    point: int,
    play_timer: Timer | None,
    ball_last_directions: dict[str, bool],
  ) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    self.next_level: GameLevel | None = self.snapshot.level

    self.show_clear = False
    self.show_next = False

    def wait_jumper(start: bool, timer: Timer) -> bool:
      if not self.snapshot.jumper.jumping:
        self.record_score()
        self.snapshot.save(self.config.path)

        self.next_level = GameLevelAll.next(self.snapshot.level)
        if self.next_level is not None:
          if self.next_level.mode != self.snapshot.level.mode:
            self.next_level = None
        return True

      return False

    def show_clear(start: bool, timer: Timer) -> bool:
      self.show_clear = True
      SCENES_SOUNDS[SceneSound.STAGE_CLEAR].play()
      return True

    def show_next(start: bool, timer: Timer) -> bool:
      if start:
        self.show_next = True
        self.snapshot.jumper.walk(self.snapshot.field.left-self.snapshot.jumper.size.width)
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 0, wait_jumper, None),
      Seq(self.stopwatch, 1000, show_clear, None),
      Seq(self.stopwatch, 2000, show_next, None),
    ])

  def update(self) -> Self | Any:
    if self.next_level is None:
      return GameClearScene(self, self.point, self.play_timer, self.ball_last_directions)

    else:
      if self.time_seq.ended:
        if self.snapshot.game_pad.enter(False):
          self.snapshot.level = self.next_level

          self.snapshot.field = GameLevelAll.field(self.snapshot.level, self.config)
          self.snapshot.balls = []
          self.snapshot.jumper.origin = self.jumper_start_origin(self.snapshot.jumper)

          self.snapshot.save(self.config.path)
          return ReadyScene(self, self.point, None, {})

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_clear:
      clear_text = self.text(self.string('stage_clear_title'))
      clear_text.center = self.subtitle_center()
      subjects.append(clear_text)

    if self.show_next:
      next_text = self.text(self.string('stage_clear_text'))
      next_text.center = self.menu_middle_center()
      subjects.append(next_text)

    return subjects


class GameClearScene(BaseStageScene):
  def __init__(
    self,
    scene: Scene,
    point: int,
    play_timer: Timer | None,
    ball_last_directions: dict[str, bool],
  ) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    self.record_score()
    self.snapshot.save(self.config.path)

    self.next_level = GameLevelAll.next(self.snapshot.level)

    self.show_clear = False
    self.show_thanks = False

    def show_clear(start: bool, timer: Timer) -> bool:
      self.show_clear = True
      self.snapshot.jumper.joy()
      return True

    def joy_jumper(start: bool, timer: Timer) -> bool:
      if not self.snapshot.jumper.joying:
        return True

      return False

    def show_next(start: bool, timer: Timer) -> bool:
      if start:
        self.show_thanks = True
        self.snapshot.jumper.walk(self.snapshot.field.left-self.snapshot.jumper.size.width)
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 2000, show_clear, None),
      Seq(self.stopwatch, 0, joy_jumper, None),
      Seq(self.stopwatch, 2000, show_next, None),
    ])

  def update(self) -> Self | Any:
    if self.time_seq.ended:
      if self.snapshot.game_pad.enter(False):
        self.snapshot.level = self.next_level if self.next_level is not None else GameLevelAll.NORMAL_1.value

        self.snapshot.field = GameLevelAll.field(self.snapshot.level, self.config)
        self.snapshot.balls = []
        self.snapshot.jumper = GameLevelAll.jumper(self.snapshot.level, self.config)
        self.snapshot.jumper.origin = self.jumper_start_origin(self.snapshot.jumper)

        self.snapshot.save(self.config.path)
        return TitleScene(self)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_clear:
      clear_text = self.text(self.string('game_clear_title' if self.next_level is not None else 'game_clear_all_title'))
      clear_text.center = self.subtitle_center()
      subjects.append(clear_text)

    if self.show_thanks:
      thanks_text = self.text(self.string('game_clear_all_text'))
      thanks_text.center = self.menu_middle_center()
      subjects.append(thanks_text)

    return subjects
