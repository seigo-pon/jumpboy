from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Self
from game import (
  Coordinate, Size,
  AssetImage, Image, TileMap,
  Collision, Block, Image, Text, Signboard,
  GameConfig, Language, StringRes, Stopwatch, Timer, Seq, TimeSeq,
)
from core import (
  GamePad,
  GameLevel, Score, ScoreBoard,
  Ball, Jumper, Field, BlinkText,
  Snapshot, Scene,
)
import pyxel


GROUND_TOP = TileMap.basic_size().height+TileMap.basic_size().height*(3/4)
TEXT_HEIGHT = 10

class GameLevelAll(Enum):
  NORMAL_1 = GameLevel(0, 0)

  @classmethod
  def next(cls, level: GameLevel) -> GameLevel | None:
    try:
      levels = list([e.value for e in GameLevelAll])
      index = levels.index(level)
      next_level = levels[index+1]
      return next_level
    except:
      pass

    return None

  @classmethod
  def field(cls, level: GameLevel, config: GameConfig) -> Field:
    return Field(
      [
        TileMap(0, Coordinate(0, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
        TileMap(0, Coordinate(0, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
        TileMap(0, Coordinate(0, 0), Size(1, 2), AssetImage.Pose.NORMAL, config.transparent_color),
      ],
      [],
      config.window_size,
      GROUND_TOP,
    )

  @classmethod
  def jumper(cls, level: GameLevel, config: GameConfig) -> Jumper:
    return Jumper(
      {
        Jumper.Motion.STOP: Block(
          Image(0, Coordinate(1, 0), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height))),
        Jumper.Motion.WALK: Block(
          Image(0, Coordinate(1, 1), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        ),
        Jumper.Motion.JUMP: Block(
          Image(0, Coordinate(1, 2), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        ),
        Jumper.Motion.FALL_DOWN: Block(
          Image(0, Coordinate(1, 3), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
          Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
        )
      },
      Jumper.Param(-10, 1, 2, 3),
    )

  @classmethod
  def balls(cls, level: GameLevel, config: GameConfig) -> list[Ball]:
    return [
      Ball(
        {
          Ball.Motion.ANGLE_0: Block(
            Image(0, Coordinate(0, 0), Size(1, 1), Image.Pose.NORMAL, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Ball.Motion.ANGLE_90: Block(
            Image(0, Coordinate(0, 0), Size(1, 1), Image.Pose.MIRROR_Y, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Ball.Motion.ANGLE_180: Block(
            Image(0, Coordinate(0, 0), Size(1, 1), Image.Pose.MIRROR_XY, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
          Ball.Motion.ANGLE_270: Block(
            Image(0, Coordinate(0, 0), Size(1, 1), Image.Pose.MIRROR_X, config.transparent_color),
            Collision(Coordinate(0, 0), Size(Image.basic_size().width, Image.basic_size().height)),
          ),
        },
        Ball.Param(2, 1, 10),
      )
    ]

GAME_TITLE: dict[int, str] = {
  GameLevelAll.NORMAL_1.value.mode: 'TITLE_BOY',
}
SCORE: dict[int, str] = {
  GameLevelAll.NORMAL_1.value.mode: 'SCORE_BOY',
}
TEXT_COLOR = pyxel.COLOR_WHITE


class BaseScene(Scene):
  JUMPER_START_X = Image.basic_size().width*5

  def __init__(
    self,
    config: GameConfig,
    string_res: StringRes,
    stopwatch: Stopwatch,
    snapshot: Snapshot,
  ) -> None:
    super().__init__(config, string_res, stopwatch, snapshot)

  def menu_left_top_origin(self) -> Coordinate:
    return Coordinate(0, 0)

  def menu_middle_top_center(self, size: Size | None) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      (size.height if size is not None else TEXT_HEIGHT)/2,
    )

  def menu_right_top_origin(self, text: Text) -> Coordinate:
    return Coordinate(self.config.window_size.width-text.size.width, 0)

  def title_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      TEXT_HEIGHT*3+TEXT_HEIGHT/2,
    )

  def subtitle_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      TEXT_HEIGHT*4+TEXT_HEIGHT/2,
    )

  def menu_middle_center(self) -> Coordinate:
    return Coordinate(self.config.window_size.center.x, self.config.window_size.center.y)

  def menu_middle_bottom_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      self.snapshot.field.ground_height-TEXT_HEIGHT*3+TEXT_HEIGHT/2,
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
    return Text(string, TEXT_COLOR, TEXT_HEIGHT, False, self.config.path)

  def blink_text(self, string: str, msec: int, show: bool) -> BlinkText:
    return BlinkText(string, TEXT_COLOR, TEXT_HEIGHT, False, self.config.path, self.stopwatch, msec, show)

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects: list[Any] = []
    subjects.append(self.snapshot.field)
    subjects += self.snapshot.balls
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
        self.config.path,
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
    level = GameLevelAll.NORMAL_1.value

    super().__init__(
      config,
      string_res,
      Stopwatch(config.fps),
      Snapshot(
        Language.EN,
        GamePad(),
        ScoreBoard(),
        level,
        GameLevelAll.field(level, config),
        GameLevelAll.balls(level, config),
        GameLevelAll.jumper(level, config),
      ),
    )

    self.snapshot.load(self.config.path)
    self.title = self.string(GAME_TITLE[self.snapshot.level.mode])

    for ball in self.snapshot.balls:
      ball.origin = self.ball_start_origin(ball)
    self.snapshot.jumper.origin = self.jumper_start_origin(self.snapshot.jumper)

    self.title_text: Text | None = None

    def walk_jumper(start: bool) -> bool:
      if start:
        self.snapshot.jumper.walk(self.jumper_play_x())
      else:
        if not self.snapshot.jumper.walking:
          return True
      return False

    def move_title(start: bool) -> bool:
      if self.title_text is None:
        self.title_text = self.text(self.config.title)
        self.title_text.center = Coordinate(self.title_center().x, -TEXT_HEIGHT)
        self.title_text.move(self.title_center())
      else:
        if self.title_text.moving:
          return True
      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 2000, walk_jumper, None),
      Seq(self.stopwatch, 2000, move_title, None),
      Seq(self.stopwatch, 2000, lambda x: True, lambda: TitleScene(self)),
    ])

  @property
  def updating_variations(self) -> list[Any]:
    variations = super().updating_variations

    if self.title_text is not None:
      variations.append(self.title_text)

    return variations

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter(False, False):
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
    super().__init__(scene.config, scene.string_res, scene.stopwatch, scene.snapshot)

    for ball in self.snapshot.balls:
      ball.origin = self.ball_start_origin(ball)

    if self.snapshot.jumper.falling_down:
      self.snapshot.jumper.stop()
      self.snapshot.jumper.origin = Coordinate(self.jumper_play_x(), self.jumper_start_origin(self.snapshot.jumper).y)
    self.snapshot.jumper.walk(self.jumper_play_x())

    self.title_text = self.text(self.config.title)
    self.title_text.center = self.title_center()

    self.start_text = self.blink_text(self.string('GAME_START'), 1000, True)
    self.start_text.center = self.menu_middle_center()

    self.show_score = False
    self.score = self.scoreboard()
    self.score.center = Coordinate(self.menu_middle_top_center(None).x, -self.score.size.height/2)

    def walk_jumper(start: bool) -> bool:
      if start:
        self.snapshot.jumper.walk(self.snapshot.field.right)
      else:
        if not self.snapshot.jumper.walking:
          return True
      return False

    def show_score(start: bool):
      self.show_score = True
      self.score.move(self.menu_middle_top_center(
        Size(self.score.size.width, self.score.size.height+TEXT_HEIGHT*3)
      ))
      self.start_text.center = Coordinate(self.menu_middle_center().x, self.menu_middle_center().y+TEXT_HEIGHT*2)
      return True

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 20000, walk_jumper, None),
      Seq(self.stopwatch, 1000, show_score, None),
    ])

  def scoreboard(self) -> Signboard:
    score_texts: list[Text] = []

    score_center = self.menu_middle_top_center(None)
    score_text = self.text(self.string('SCORE_RANKING'))
    score_text.center = Coordinate(score_center.x, score_center.y)
    score_texts.append(score_text)

    score_center.y += score_text.word_size().height
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
        score_center.y += score_text.word_size().height
    else:
      no_score_text = self.text(self.string('NO_SCORE'))
      no_score_text.center = Coordinate(score_center.x, score_center.y)
      score_texts.append(no_score_text)

    return Signboard(None, score_texts, self.config.window_size.width, None)

  @property
  def updating_variations(self) -> list[Any]:
    variations = super().updating_variations

    if self.show_score:
      variations.append(self.score)
    if not self.score.moving:
      variations.append(self.start_text)

    return variations

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter(False, False):
      self.start_text.set_msec(120, True)
      self.time_seq = TimeSeq([
        Seq(self.stopwatch, 1000, lambda x: True, lambda: ReadyScene(self, 0, None, {})),
      ])

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_score:
      subjects.append(self.score)
    else:
      subjects.append(self.title_text)
    subjects.append(self.start_text)

    copyright_text = self.text('(c) {} {}'.format(self.config.released_year, self.config.copyright))
    copyright_text.center = self.menu_middle_bottom_center()
    subjects.append(copyright_text)

    return subjects


class BaseStageScene(BaseScene):
  STAGE_LIMIT_MSEC: dict[int, dict[int, int]] = {
    GameLevelAll.NORMAL_1.value.mode: {
      GameLevelAll.NORMAL_1.value.stage: 15000,
    },
  }

  def __init__(self, scene: Scene, point: int, play_timer: Timer | None, ball_last_directions: dict[str, bool]) -> None:
    super().__init__(scene.config, scene.string_res, scene.stopwatch, scene.snapshot)

    self.point = point
    self.play_timer = play_timer
    self.ball_last_directions = ball_last_directions

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

    stage_text = self.text('{}.{:02}'.format(self.string('STAGE'), self.snapshot.level.stage+1))
    stage_text.origin = self.menu_left_top_origin()
    subjects.append(stage_text)

    if self.play_timer is not None:
      play_time_text = self.text(
        '{:02}:{:02}.{:03}'.format(
          int(self.play_timer.sec/60),
          int(self.play_timer.sec%60),
          self.play_timer.msec%1000
        )
      )
      play_time_text.center = self.menu_middle_top_center(None)
      subjects.append(play_time_text)

    score_text = self.text('{}:{:04}'.format(self.string(SCORE[self.snapshot.level.mode]), self.point))
    score_text.origin = self.menu_right_top_origin(score_text)
    subjects.append(score_text)

    return subjects


class ReadyScene(BaseStageScene):
  class Describe(IntEnum):
    STAGE = 0
    TIME_LIMIT = 1
    READY = 2

  START_MSEC = 3000

  def __init__(self, scene: Scene, point: int, play_timer: Timer | None, ball_last_directions: dict[str, bool]) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    for ball in self.snapshot.balls:
      ball.stop()
      ball.origin = self.ball_start_origin(ball)

    self.snapshot.jumper.stop()

    self.describe: self.Describe | None = None
    self.describe_timer: Timer | None = None
    self.ready_timer: Timer | None = None

    def walk_jumper(start: bool) -> bool:
      if start:
        self.snapshot.jumper.walk(self.jumper_play_x())
      else:
        if not self.snapshot.jumper.walking:
          return True
      return False

    def ready_describe(start: bool) -> bool:
      if self.describe is None:
        self.describe = [e for e in self.Describe][0]
        self.describe_timer = Timer.set_msec(self.stopwatch, 1000, True)
      elif self.describe_timer is not None and self.describe_timer.over:
        self.describe += 1
        if self.describe > [e for e in self.Describe]:
          self.describe = None
          return True
      return False

    def ready_play(start: bool) -> bool:
      self.ready_timer = Timer.set_msec(self.stopwatch, self.START_MSEC, True)
      return True

    def start_play(start: bool) -> bool:
      if self.ready_timer is not None:
        if self.ready_timer.over:
          for ball in self.snapshot.balls:
            ball.roll()
          self.snapshot.jumper.stand_by()
          return True
      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 0, walk_jumper, None),
      Seq(self.stopwatch, 1000, ready_describe, None),
      Seq(self.stopwatch, 1000, ready_play, None),
      Seq(self.stopwatch, 0, start_play, lambda: PlayScene(self, self.point, self.play_timer, self.ball_last_directions)),
    ])

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.describe is not None:
      if self.describe == self.Describe.STAGE:
        describe_text = self.text('{}.{:02}'.format(self.string('STAGE'), self.snapshot.level.stage+1))
        describe_text.center = self.subtitle_center()
        subjects.append(describe_text)

      elif self.describe == self.Describe.TIME_LIMIT:
        describe_text = self.text(
          '{} {:02}{}'.format(
            self.string('TIME_LIMIT'),
            self.STAGE_LIMIT_MSEC[self.snapshot.level.mode][self.snapshot.level.stage]/1000,
            self.string('SEC'),
          ),
        )
        describe_text.center = self.subtitle_center()
        subjects.append(describe_text)

      elif self.describe == self.Describe.READY:
        describe_text = self.text(self.string('READY'))
        describe_text.center = self.subtitle_center()
        subjects.append(describe_text)

    elif self.ready_timer is not None:
      wait_sec = max(self.START_SEC-self.ready_timer.sec, 1)
      wait_sec = min(wait_sec, self.START_SEC)
      start_wait_time_text = self.text(str(wait_sec))
      start_wait_time_text.center = self.subtitle_center()
      subjects.append(start_wait_time_text)

    return subjects


class PlayScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None, ball_last_directions: dict[str, bool]) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    if self.play_timer is None:
      print('play start', vars(self.snapshot.level))
      self.play_timer = Timer.set_msec(
        self.stopwatch,
        self.STAGE_LIMIT_MSEC[self.snapshot.level.mode][self.snapshot.level.stage],
      )
      for ball in self.snapshot.balls:
        self.ball_last_directions[ball.id] = ball.rolling_direction

    if self.play_timer is not None:
      self.play_timer.resume()

  def update(self) -> Self | Any:
    if self.play_timer is not None:
      if self.snapshot.game_pad.cancel():
        self.play_timer.pause()
        return PauseScene(self, self.point, self.play_timer, self.ball_last_directions)

      for ball in self.snapshot.balls:
        if ball.hit(self.snapshot.jumper):
          self.play_timer.pause()
          for ball in self.snapshot.balls:
            ball.stop()
          self.snapshot.jumper.fall_down()
          return GameOverScene(self, self.point, self.play_timer, self.ball_last_directions)

        else:
          if self.ball_last_directions[ball.id] != ball.rolling_direction:
            self.point += ball.param.defeat_point
            self.ball_last_directions[ball.id] = ball.rolling_direction

      if self.play_timer.over:
        self.play_timer.pause()
        for ball in self.snapshot.balls:
          ball.stop()
        self.snapshot.jumper.stop()
        return StageClearScene(self, self.point, self.play_timer, self.ball_last_directions)

    return super().update()


class PauseScene(BaseStageScene):
  RESTART_TEXT = 1

  def __init__(self, scene: Scene, point: int, play_timer: Timer | None, ball_last_directions: dict[str, bool]) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    self.restart_text = self.blink_text(self.string('RESTART'), 1000, False)
    self.restart_text.center = self.menu_middle_center()

  @property
  def updating_variations(self) -> list[Any]:
    return [self.restart_text]

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter(False, False) or self.snapshot.game_pad.cancel():
      return PlayScene(self, self.point, self.play_timer, self.ball_last_directions)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    pause_text = self.text(self.string('PAUSE'))
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

    def show_game_over(start: bool) -> bool:
      self.show_game_over = True
      return True

    def show_game_end(start: bool) -> bool:
      self.show_game_end = True
      return True

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 1000, show_game_over, None),
      Seq(self.stopwatch, 2000, show_game_end, None),
    ])

  def update(self) -> Self | Any:
    if self.time_seq.ended:
      if self.snapshot.game_pad.enter(False, False):
        return TitleScene(self)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_game_over:
      game_over_text = self.text(self.string('GAME_OVER'))
      game_over_text.center = self.subtitle_center()
      subjects.append(game_over_text)

    if self.show_game_end:
      end_text = self.text(self.string('GAME_END'))
      end_text.center = self.menu_middle_center()
      subjects.append(end_text)

    return subjects


class StageClearScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None, ball_last_directions: dict[str, bool]) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    self.record_score()
    self.snapshot.save(self.config.path)

    self.next_level = GameLevelAll.next(self.snapshot.level)
    if self.next_level is not None:
      if self.next_level.mode != self.snapshot.level.mode:
        self.next_level = None

    self.show_clear = False
    self.show_next = False

    def show_clear(start: bool) -> bool:
      self.show_clear = True
      return True

    def show_next(start: bool) -> bool:
      if start:
        self.show_next = True
        self.snapshot.jumper.walk(self.snapshot.field.left-self.snapshot.jumper.size.width)
      else:
        if not self.snapshot.jumper.walking:
          return True
      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 1000, show_clear, None),
      Seq(self.stopwatch, 2000, show_next, None),
    ])

  def update(self) -> Self | Any:
    if self.next_level is None:
      return GameClearScene(self, self.point, self.play_timer, self.ball_last_directions)

    else:
      if self.time_seq.ended:
        if self.snapshot.game_pad.enter(False, False):
          self.snapshot.level = self.next_level

          self.snapshot.field = GameLevelAll.field(self.snapshot.level, self.config)
          self.snapshot.balls = GameLevelAll.balls(self.snapshot.level, self.config)

          for ball in self.snapshot.balls:
            ball.origin = self.ball_start_origin(ball)
          self.snapshot.jumper.origin = self.jumper_start_origin(self.snapshot.jumper)

          self.snapshot.save(self.config.path)
          return ReadyScene(self, self.point, None, {})

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_clear:
      clear_text = self.text(self.string('STAGE_CLEAR'))
      clear_text.center = self.subtitle_center()
      subjects.append(clear_text)

    if self.show_next:
      next_text = self.text(self.string('STAGE_NEXT'))
      next_text.center = self.menu_middle_center()
      subjects.append(next_text)

    return subjects


class GameClearScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None, ball_last_directions: dict[str, bool]) -> None:
    super().__init__(scene, point, play_timer, ball_last_directions)

    self.record_score()
    self.snapshot.save(self.config.path)

    self.next_level = GameLevelAll.next(self.snapshot.level)

    self.show_clear = False
    self.show_thanks = False

    def show_clear(start: bool) -> bool:
      self.show_clear = True
      self.snapshot.jumper.joy()
      return True

    def joy_jumper(start: bool) -> bool:
      if not self.snapshot.jumper.joying:
        return True
      return False

    def show_next(start: bool) -> bool:
      if start:
        self.show_thanks = True
        self.snapshot.jumper.walk(self.snapshot.field.left-self.snapshot.jumper.size.width)
      else:
        if not self.snapshot.jumper.walking:
          return True
      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 1000, show_clear, None),
      Seq(self.stopwatch, 0, joy_jumper, None),
      Seq(self.stopwatch, 2000, show_next, None),
    ])

  def update(self) -> Self | Any:
    if self.time_seq.ended:
      if self.snapshot.game_pad.enter(False, False):
        self.snapshot.level = self.next_level if self.next_level is not None else GameLevelAll.NORMAL_1.value

        self.snapshot.field = GameLevelAll.field(self.snapshot.level, self.config)
        self.snapshot.balls = GameLevelAll.balls(self.snapshot.level, self.config)
        self.snapshot.jumper = GameLevelAll.jumper(self.snapshot.level, self.config)

        for ball in self.snapshot.balls:
          ball.origin = self.ball_start_origin(ball)
        self.snapshot.jumper.origin = self.jumper_start_origin(self.snapshot.jumper)

        self.snapshot.save(self.config.path)
        return TitleScene(self)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_clear:
      clear_text = self.text(self.string('GAME_CLEAR' if self.next_level is not None else 'GAME_CLEAR_ALL'))
      clear_text.center = self.subtitle_center()
      subjects.append(clear_text)

    if self.show_thanks:
      thanks_text = self.text(self.string('GAME_CLEAR_THANKS'))
      thanks_text.center = self.menu_middle_center()
      subjects.append(thanks_text)

    return subjects
