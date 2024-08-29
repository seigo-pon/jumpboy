from datetime import datetime
from enum import IntEnum
from typing import Any, Self
from game import (
  Coordinate, Size, Stopwatch, Timer, TextScriber,
  Image,
  Text, BlinkText,
  SignboardPoster, Signboard,
  GameConfig, Language, StringRes, Seq, TimeSeq,
)
from core import (
  GamePad,
  GameLevel, Score, ScoreBoard,
  Ball, Jumper,
  Snapshot, Scene,
)
from design import (
  IMAGE_ID, ImageX,
  SceneSound, SCENES_SOUNDS,
  GameLevelMode, GameLevelStage,
  GameDesign,
)
import pyxel


TEXT_FONT_SIZE = 10
TEXT_COLOR = pyxel.COLOR_WHITE

GAME_TITLE: dict[int, str] = {
  GameLevelMode.NORMAL: 'game_title_1',
}
SCORE: dict[int, str] = {
  GameLevelMode.NORMAL: 'score_title_1',
}


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
      (size.height
       if size is not None else
       TextScriber.word_size(TEXT_FONT_SIZE).height)/2,
    )

  def menu_right_top_origin(self, size: Size) -> Coordinate:
    return Coordinate(self.config.window_size.width-size.width, 0)

  def title_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      TextScriber.word_size(TEXT_FONT_SIZE).height*2
      +TextScriber.word_size(TEXT_FONT_SIZE).height/2,
    )

  def subtitle_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      TextScriber.word_size(TEXT_FONT_SIZE).height*3
      +TextScriber.word_size(TEXT_FONT_SIZE).height/2,
    )

  def menu_middle_center(self) -> Coordinate:
    return self.config.window_size.center

  def menu_middle_low_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      self.config.window_size.center.y
      +TextScriber.word_size(TEXT_FONT_SIZE).height*3,
    )

  def menu_middle_bottom_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      self.snapshot.field.ground_height
      -TextScriber.word_size(TEXT_FONT_SIZE).height*2
      +TextScriber.word_size(TEXT_FONT_SIZE).height/2,
    )

  def ball_ready_origin(self, ball: Ball) -> Coordinate:
    return Coordinate(
      self.snapshot.field.left-ball.size.width,
      self.snapshot.field.bottom-ball.size.height,
    )

  def jumper_ready_origin(self, jumper: Jumper) -> Coordinate:
    return Coordinate(
      self.snapshot.field.right,
      self.snapshot.field.bottom-jumper.size.height,
    )

  def jumper_start_x(self) -> float:
    return self.snapshot.field.right-self.JUMPER_START_X

  def text(self, string: str) -> Text:
    return Text(string, TEXT_COLOR, TEXT_FONT_SIZE, False)

  def blink_text(self, string: str, blink_period: int, show: bool) -> BlinkText:
    return BlinkText(
      string,
      TEXT_COLOR,
      TEXT_FONT_SIZE,
      False,
      blink_period,
      show,
    )

  def initial_sprites(self) -> None:
    self.snapshot.field = GameDesign.field(self.snapshot.level, self.config)

    self.snapshot.balls = []

    self.snapshot.jumper = GameDesign.jumper(self.snapshot.level)
    self.snapshot.jumper.origin = self.jumper_ready_origin(self.snapshot.jumper)

  def to_next_level(cls, level: GameLevel) -> GameLevel | None:
    levels = [e.value for e in GameLevelStage]
    for (index, value) in enumerate(levels):
      if value.mode == level.mode and value.stage == level.stage:
        index += 1
        if index < len(levels):
          next_level = levels[index]
          print('next level', next_level)
          return next_level

    print('next level none')
    return None

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
    level = GameLevelStage.NORMAL_1.value

    super().__init__(
      config,
      string_res,
      stopwatch,
      Snapshot(
        Language.EN,
        GamePad(),
        ScoreBoard(),
        level,
        GameDesign.field(level, config),
        [],
        GameDesign.jumper(level),
      ),
    )

    self.snapshot.load(self.config.path)
    self.config.title = self.string(GAME_TITLE[self.snapshot.level.mode])

    self.title_text: Text | None = None

    self.initial_sprites()

    def _walk_jumper(start: bool, timer: Timer) -> bool:
      if start:
        self.snapshot.jumper.walk(self.jumper_start_x())
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    def _move_title(start: bool, timer: Timer) -> bool:
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
      Seq(self.stopwatch, 500, _walk_jumper, None),
      Seq(self.stopwatch, 2000, _move_title, None),
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
      scene.snapshot,
    )

    self.title_text = self.text(self.config.title)
    self.title_text.center = self.title_center()

    self.show_start = True
    self.start_text = self.blink_text(
      self.string('game_start_text'),
      self.config.frame_count(1000),
      False,
    )
    self.start_text.center = self.menu_middle_center()
    self.wait_start = False

    self.show_score = False
    self.score = self.scoreboard()
    self.score.center = Coordinate(self.menu_middle_top_center(None).x, -self.score.size.height/2)

    def _walk_jumper(start: bool, timer: Timer) -> bool:
      self.snapshot.jumper.walk(self.jumper_start_x())
      return True

    def _escape_jumper(start: bool, timer: Timer) -> bool:
      if start:
        self.snapshot.jumper.walk(self.snapshot.field.right)
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    def _show_score(start: bool, timer: Timer):
      if start:
        self.show_score = True
        self.score.move(
          self.menu_middle_top_center(
            Size(
              self.score.size.width,
              self.score.size.height
              +TextScriber.word_size(TEXT_FONT_SIZE).height*2,
            )
          ),
          0.5,
        )
        self.show_start = False
      else:
        if not self.score.moving:
          self.show_start = True
          self.start_text.center = Coordinate(
            self.menu_middle_low_center().x,
            self.menu_middle_low_center().y
            -TextScriber.word_size(TEXT_FONT_SIZE).height,
          )
          return True

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 0, _walk_jumper, None),
      Seq(self.stopwatch, 15000, _escape_jumper, None),
      Seq(self.stopwatch, 1000, _show_score, None),
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

    return Signboard([], score_texts, self.config.window_size.width, None)

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
        self.start_text.update_blink_period(self.config.frame_count(100), True)
        self.time_seq = TimeSeq([
          Seq(self.stopwatch, 1000, lambda x, y: True, lambda: ReadyScene(self, 0, None)),
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
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(
      scene.config,
      scene.string_res,
      scene.stopwatch,
      scene.snapshot,
    )

    self.point = point
    self.play_timer = play_timer

    self.show_stage = True

  def record_score(self) -> None:
    self.snapshot.score_board.scores.append(Score(datetime.now(), self.snapshot.level, self.point))
    print('score record', vars(self.snapshot.score_board.scores[-1]))

  def life_gauge(self) -> Signboard:
    return Signboard(
      [
        SignboardPoster(
          Image(
            IMAGE_ID,
            Coordinate(
              ImageX.LIFE,
              0 if ((self.snapshot.jumper.param.max_life-1)-index) < self.snapshot.jumper.life else 1,
            ),
            Size(1, 1),
            Image.Pose.NORMAL,
          ),
          Coordinate(Image.basic_size().width*index, 0)
        )
        for index in range(self.snapshot.jumper.param.max_life)
      ],
      [],
      None,
      None,
    )

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
    score_text.origin = self.menu_right_top_origin(score_text.size)
    subjects.append(score_text)

    life = self.life_gauge()
    life.origin = Coordinate(
      self.menu_right_top_origin(life.size).x,
      self.menu_right_top_origin(life.size).y+score_text.size.height,
    )
    subjects.append(life)

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

  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(scene, point, play_timer)

    self.snapshot.jumper.life = self.snapshot.jumper.param.max_life
    self.snapshot.jumper.stop()

    print('ready', vars(self.snapshot.level))
    self.play_timer = Timer.set_msec(
      self.stopwatch,
      GameDesign.play_limit_msec(self.snapshot.level),
      False,
    )

    self.show_stage = False

    self.describe: self.Describe | None = None
    self.ready_timer: Timer | None = None
    self.last_sec = -1

    def _walk_jumper(start: bool, timer: Timer) -> bool:
      if start:
        self.snapshot.jumper.walk(self.jumper_start_x())
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    def _ready_describe(start: bool, timer: Timer) -> bool:
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

    def _ready_play(start: bool, timer: Timer) -> bool:
      self.ready_timer = Timer.set_msec(self.stopwatch, self.START_MSEC, True)
      self.last_sec = -1
      return True

    def _start_play(start: bool, timer: Timer) -> bool:
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
      Seq(self.stopwatch, 0, _walk_jumper, None),
      Seq(self.stopwatch, 1000, _ready_describe, None),
      Seq(self.stopwatch, 0, _ready_play, None),
      Seq(self.stopwatch, 0, _start_play, lambda: PlayScene(self, self.point, self.play_timer)),
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
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(scene, point, play_timer)

    if self.play_timer is not None:
      self.play_timer.resume()

  def update(self) -> Self | Any:
    if self.play_timer is not None:
      if self.snapshot.game_pad.cancel():
        self.play_timer.pause()
        SCENES_SOUNDS[SceneSound.PAUSE].play()
        return PauseScene(self, self.point, self.play_timer)

      next_balls: list[Ball] = []
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
          if ball.rolling:
            if ball.hit(self.snapshot.jumper):
              attack = False
              if self.snapshot.jumper.jumping:
                if ball.top <= self.snapshot.jumper.bottom <= ball.bottom:
                  if ball.left <= self.snapshot.jumper.center.x <= ball.right:
                    print('attack y', ball.top, self.snapshot.jumper.bottom, ball.bottom)
                    print('attack x', ball.left, self.snapshot.jumper.center.x, ball.right)
                    attack = True

              if attack:
                ball.burst()
                self.point += ball.acquirement_point
              else:
                ball.strike()
                self.snapshot.jumper.damage()

          if not self.snapshot.jumper.falling_down:
            if ball.bounced:
              print('ball bounced')
              self.point += ball.acquirement_point

      self.snapshot.balls = next_balls
      for ball in self.snapshot.balls:
        ball.bounced = False

      if self.snapshot.jumper.falling_down:
        self.play_timer.pause()
        for ball in self.snapshot.balls:
          ball.stop()
        return GameOverScene(self, self.point, self.play_timer)

      if self.play_timer.over:
        self.play_timer.pause()
        for ball in self.snapshot.balls:
          ball.stop()
        self.snapshot.jumper.stop()
        SCENES_SOUNDS[SceneSound.TIME_UP].play()
        return StageClearScene(self, self.point, self.play_timer)

      balls = sorted(self.snapshot.balls, key=lambda x: x.frame)
      if len(balls) == 0 or balls[0].frame >= GameDesign.next_ball_frame_count(self.snapshot.level, self.config):
        ball = GameDesign.ball(self.snapshot.level)
        ball.origin = self.ball_ready_origin(ball)
        ball.roll()
        self.snapshot.balls.append(ball)

    return super().update()


class PauseScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(scene, point, play_timer)

    self.pause_text = self.blink_text(
      self.string('game_pause_text'),
      self.config.frame_count(1000),
      True,
    )

  @property
  def updating_variations(self) -> list[Any]:
    return [self.pause_text]

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter(False) or self.snapshot.game_pad.cancel():
      SCENES_SOUNDS[SceneSound.RESTART].play()
      return PlayScene(self, self.point, self.play_timer)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    self.pause_text.center = self.subtitle_center()
    subjects.append(self.pause_text)

    return subjects


class GameOverScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(scene, point, play_timer)

    self.record_score()
    self.snapshot.save(self.config.path)

    self.show_game_over = False
    self.show_game_end = False

    self.restart_text = self.blink_text(
      self.string('game_restart_text'),
      self.config.frame_count(1000),
      False,
    )

    def _show_game_over(start: bool, timer: Timer) -> bool:
      self.show_game_over = True
      SCENES_SOUNDS[SceneSound.GAME_OVER].play()
      return True

    def _show_game_end(start: bool, timer: Timer) -> bool:
      self.show_game_end = True
      return True

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 1000, _show_game_over, None),
      Seq(self.stopwatch, 2000, _show_game_end, None),
    ])

  @property
  def updating_variations(self) -> list[Any]:
    variations = super().updating_variations

    if self.show_game_end:
      variations.append(self.restart_text)

    return variations

  def update(self) -> Self | Any:
    if self.time_seq.ended:
      if self.snapshot.game_pad.enter(False):
        self.snapshot.level = GameLevelStage.NORMAL_1.value
        self.initial_sprites()
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

      self.restart_text.center = self.menu_middle_low_center()
      subjects.append(self.restart_text)

    return subjects


class StageClearScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(scene, point, play_timer)

    self.next_level: GameLevel | None = self.snapshot.level
    self.same_surface = False

    self.show_clear = False
    self.show_next = False

    def _wait_jumper(start: bool, timer: Timer) -> bool:
      if not self.snapshot.jumper.jumping:
        self.snapshot.jumper.stop()

        self.record_score()
        self.snapshot.save(self.config.path)

        self.next_level = self.to_next_level(self.snapshot.level)
        if self.next_level is not None:
          if self.next_level.mode != self.snapshot.level.mode:
            self.next_level = None
          else:
            if self.snapshot.field.surface == GameDesign.field(self.next_level, self.config).surface:
              self.same_surface = True
        return True

      return False

    def _show_clear(start: bool, timer: Timer) -> bool:
      self.show_clear = True
      SCENES_SOUNDS[SceneSound.STAGE_CLEAR].play()
      return True

    def _show_next(start: bool, timer: Timer) -> bool:
      if start:
        self.show_next = True
        if self.next_level is not None:
          if not self.same_surface:
            self.snapshot.jumper.walk(self.snapshot.field.left-self.snapshot.jumper.size.width)
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 0, _wait_jumper, None),
      Seq(self.stopwatch, 1000, _show_clear, None),
      Seq(self.stopwatch, 2000, _show_next, None),
      Seq(self.stopwatch, 3000, lambda x, y: True, None),
    ])

  def update(self) -> Self | Any:
    if self.next_level is None:
      return GameClearScene(self, self.point, self.play_timer)

    if self.time_seq.ended or (self.show_next and self.snapshot.game_pad.enter(True)):
      self.snapshot.level = self.next_level

      self.initial_sprites()
      if self.same_surface:
        self.snapshot.jumper.origin = Coordinate(self.jumper_start_x(), self.snapshot.jumper.origin.y)

      self.snapshot.save(self.config.path)
      return ReadyScene(self, self.point, None)

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
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(scene, point, play_timer)

    self.record_score()
    self.snapshot.save(self.config.path)

    self.next_level = self.to_next_level(self.snapshot.level)

    self.show_clear = False
    self.show_thanks = False
    self.show_bye = False

    def _show_clear(start: bool, timer: Timer) -> bool:
      self.show_clear = True
      self.snapshot.jumper.joy()
      return True

    def _joy_jumper(start: bool, timer: Timer) -> bool:
      if not self.snapshot.jumper.joying:
        return True

      return False

    def _show_next(start: bool, timer: Timer) -> bool:
      if start:
        self.show_thanks = True
        self.snapshot.jumper.walk(self.snapshot.field.left-self.snapshot.jumper.size.width)
      else:
        if not self.snapshot.jumper.walking:
          self.show_bye = True
          return True

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 2000, _show_clear, None),
      Seq(self.stopwatch, 0, _joy_jumper, None),
      Seq(self.stopwatch, 2000, _show_next, None),
      Seq(self.stopwatch, 3000, lambda x, y: True, None),
    ])

  def update(self) -> Self | Any:
    if self.time_seq.ended:
      if self.next_level is not None:
        self.snapshot.level = self.next_level
      else:
        self.snapshot.level = GameLevelStage.NORMAL_1.value
      self.initial_sprites()
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
      thanks_text = self.text(self.string('game_clear_all_text_1'))
      thanks_text.center = self.menu_middle_center()
      subjects.append(thanks_text)

    if self.show_bye:
      thanks_text = self.text(self.string('game_clear_all_text_2'))
      thanks_text.center = self.menu_middle_low_center()
      subjects.append(thanks_text)

    return subjects
