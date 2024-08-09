from datetime import datetime
from typing import Any, Self
from game import (
  Coordinate, Size,
  Image, Text, Signboard,
  GameProfile, Language, StringRes, Stopwatch, Timer, Seq, TimeSeq
)
from core import (
  GamePad,
  Score, ScoreBoard,
  Ball, Jumper, BlinkText,
  Snapshot, Scene,
)
from component import (
  GameLevel, BoyStage,
  BoyStage1Field,
  BoyJumper,
  BoyStage1Ball,
)
import pyxel


GAME_TITLE: dict[int, str] = {
  GameLevel.BOY: 'TITLE_BOY',
}
SCORE: dict[int, str] = {
  GameLevel.BOY: 'SCORE_BOY',
}
TEXT_COLOR = pyxel.COLOR_WHITE


class BaseScene(Scene):
  JUMPER_START_X = Image.basic_size().width*5

  def __init__(
    self,
    profile: GameProfile,
    string_res: StringRes,
    stopwatch: Stopwatch,
    snapshot: Snapshot,
  ) -> None:
    super().__init__(profile, string_res, stopwatch, snapshot)

  def menu_left_top_origin(self) -> Coordinate:
    return Coordinate(0, 0)

  def menu_middle_top_center(self, size: Size | None) -> Coordinate:
    return Coordinate(
      self.profile.window_size.center.x,
      (size.height if size is not None else Text.word_size().height)/2,
    )

  def menu_right_top_origin(self, text: Text) -> Coordinate:
    return Coordinate(self.profile.window_size.width-text.size.width, 0)

  def title_center(self) -> Coordinate:
    return Coordinate(
      self.profile.window_size.center.x,
      Text.word_size().height*3+Text.word_size().height/2,
    )

  def subtitle_center(self) -> Coordinate:
    return Coordinate(
      self.profile.window_size.center.x,
      Text.word_size().height*4+Text.word_size().height/2,
    )

  def menu_middle_center(self) -> Coordinate:
    return Coordinate(self.profile.window_size.center.x, self.profile.window_size.center.y)

  def menu_middle_bottom_center(self) -> Coordinate:
    return Coordinate(
      self.profile.window_size.center.x,
      self.snapshot.field.ground_top-Text.word_size().height*2+Text.word_size().height/2,
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
    return Text(string, TEXT_COLOR)

  def blink_text(self, string: str, msec: int, show: bool) -> BlinkText:
    return BlinkText(string, TEXT_COLOR, self.stopwatch, msec, show)

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects: list[Any] = [self.snapshot.field]
    subjects += self.snapshot.balls
    subjects.append(self.snapshot.jumper)

    if self.profile.debug:
      stopwatch_text = Text(
        '{:02}:{:02}:{:02}:{:03}'.format(
          int(self.stopwatch.sec/60/60),
          int(self.stopwatch.sec/60%60),
          int(self.stopwatch.sec%60),
          self.stopwatch.msec%1000,
        ),
        pyxel.COLOR_BLACK,
      )
      stopwatch_text.origin = Coordinate(
        self.profile.window_size.width-stopwatch_text.size.width,
        self.profile.window_size.height-stopwatch_text.size.height,
      )
      subjects.append(stopwatch_text)

    return subjects


class OpeningScene(BaseScene):
  MOVE_TITLE_Y_MIN = 1

  def __init__(self, profile: GameProfile, string_res: StringRes) -> None:
    super().__init__(
      profile,
      string_res,
      Stopwatch(profile.fps),
      Snapshot(
        Language.EN,
        GamePad(),
        ScoreBoard(),
        GameLevel.BOY,
        BoyStage.STAGE_1,
        BoyStage1Field(profile.window_size),
        [BoyStage1Ball()],
        BoyJumper(),
      ),
    )

    self.snapshot.load(self.profile.path)
    self.title = self.string(GAME_TITLE[self.snapshot.level])

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
        self.title_text = self.text(self.profile.title)
        self.title_text.center = Coordinate(self.title_center().x, -Text.word_size().height)
        self.title_text.move(self.title_center())
      else:
        if self.title_text.moving:
          return True
      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 2000, walk_jumper, None),
      Seq(self.stopwatch, 1000, move_title, None),
      Seq(self.stopwatch, 1000, lambda x: True, lambda: TitleScene(self)),
    ])

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      return TitleScene(self)

    if self.title_text is not None:
      self.title_text.update()

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
    super().__init__(scene.profile, scene.string_res, scene.stopwatch, scene.snapshot)

    for ball in self.snapshot.balls:
      ball.origin = self.ball_start_origin(ball)
    if self.snapshot.jumper.falling_down:
      self.snapshot.jumper.stop()
      self.snapshot.jumper.origin = self.jumper_start_origin(self.snapshot.jumper)

    self.title_text = self.text(self.profile.title)
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
      self.score.move(self.menu_middle_top_center(self.score.size))
      self.title_text.move(
        Coordinate(
          self.title_text.center.x,
          self.snapshot.field.bottom+Text.word_size().height,
        )
      )
      return True

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 30000, walk_jumper, None),
      Seq(self.stopwatch, 1000, show_score, None),
    ])

  def scoreboard(self) -> Signboard:
    score_texts: list[Text] = []

    score_center = self.menu_middle_top_center(None)
    score_text = self.text(self.string('SCORE_RANKING'))
    score_text.center = score_center
    score_texts.append(score_text)

    score_center.y += Text.word_size().height*2
    scores = self.snapshot.score_board.ranking(self.SCORE_RANKING_NUM)
    if len(scores) > 0:
      for (index, score) in enumerate(scores):
        score_center.y += Text.word_size().height
        score_text = self.text(
          '{}.{}.{:02} {:04} {}'.format(
            index+1,
            self.string(SCORE[score.level]),
            score.stage,
            score.point,
            score.created_at.strftime('%Y/%m/%d %H:%M'),
          )
        )
        score_text.center = score_center
        score_texts.append(score_text)
    else:
      score_center.y += Text.word_size().height
      no_score_text = self.text(self.string('NO_SCORE'))
      no_score_text.center = score_center
      score_texts.append(no_score_text)

    return Signboard(None, score_texts)

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      self.start_text.set_msec(120, True)
      self.time_seq = TimeSeq([
        Seq(self.stopwatch, 1000, lambda x: True, lambda: ReadyScene(self, 0)),
      ])

    if self.show_score:
      self.score.update()
    self.start_text.update()

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_score:
      subjects.append(self.score)

    subjects.append(self.title_text)
    subjects.append(self.start_text)

    copyright_text = self.text('(c) {} {}'.format(self.profile.release_year, self.profile.copyright))
    copyright_text.center = self.menu_middle_bottom_center()
    subjects.append(copyright_text)

    return subjects


class BaseStageScene(BaseScene):
  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene.profile, scene.string_res, scene.stopwatch, scene.snapshot)

    self.play_timer: Timer | None = None
    self.point = point

  def record_score(self) -> None:
    self.snapshot.score_board.scores.append(
      Score(
        datetime.now(),
        self.snapshot.level,
        self.snapshot.stage,
        self.point,
      )
    )
    self.point = 0

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    stage_text = self.text('{}.{:02}'.format(self.string('STAGE'), self.snapshot.stage+1))
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

    score_text = self.text('{}:{:04}'.format(self.string(SCORE[self.snapshot.level]), self.point))
    score_text.origin = self.menu_right_top_origin(score_text)
    subjects.append(score_text)

    return subjects

class ReadyScene(BaseStageScene):
  START_SEC = 3

  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    for ball in self.snapshot.balls:
      ball.stop()
      ball.origin = self.ball_start_origin(ball)
    self.snapshot.jumper.stop()

    self.ready_timer: Timer | None = None

    def walk_jumper(start: bool) -> bool:
      if start:
        self.snapshot.jumper.walk(self.jumper_play_x())
      else:
        if not self.snapshot.jumper.walking:
          return True
      return False

    def ready_play(start: bool) -> bool:
      self.ready_timer = Timer.set_sec(self.stopwatch, self.START_SEC, True)
      return True

    def start_play(start: bool) -> bool:
      if self.ready_timer.over:
        for ball in self.snapshot.balls:
          ball.roll()
        self.snapshot.jumper.stand_by()
        return True
      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 0, walk_jumper, None),
      Seq(self.stopwatch, 1000, ready_play, None),
      Seq(self.stopwatch, 0, start_play, lambda: PlayScene(self, self.point)),
    ])

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.ready_timer is not None:
      wait_sec = max(self.START_SEC-self.ready_timer.sec, 1)
      wait_sec = min(wait_sec, self.START_SEC)
      start_wait_time_text = self.text(str(wait_sec))
      start_wait_time_text.center = self.subtitle_center()
      subjects.append(start_wait_time_text)

    return subjects


class PlayScene(BaseStageScene):
  STAGE_LIMIT_SEC: dict[int, dict[int, int]] = {
    GameLevel.BOY: {
      BoyStage.STAGE_1: 30,
    },
  }

  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    if self.play_timer is None:
      self.play_timer = Timer.set_sec(
        self.stopwatch,
        self.STAGE_LIMIT_SEC[self.snapshot.level][self.snapshot.stage],
      )
    if self.play_timer is not None:
      self.play_timer.resume()

  def update(self) -> Self | Any:
    if self.play_timer is not None:
      if self.snapshot.game_pad.cancel():
        self.play_timer.pause()
        return PauseScene(self, self.point)

      for ball in self.snapshot.balls:
        if ball.hit(self.snapshot.jumper):
          self.play_timer.pause()
          for ball in self.snapshot.balls:
            ball.stop()
          self.snapshot.jumper.fall_down()
          return GameOverScene(self, self.point)

      if self.play_timer.over:
        self.play_timer.pause()
        for ball in self.snapshot.balls:
          ball.stop()
        self.snapshot.jumper.stop()
        return StageClearScene(self, self.point)

    return super().update()


class PauseScene(BaseStageScene):
  RESTART_TEXT = 1

  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    self.restart_text = self.blink_text(self.string('PAUSE_RESTART'), 1000, False)
    self.restart_text.center = self.menu_middle_center()

  @property
  def can_update_sprite(self) -> bool:
    return False

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter() or self.snapshot.game_pad.cancel():
      return PlayScene(self, self.point)

    self.restart_text.update()

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
  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    self.record_score()
    self.snapshot.save(self.profile.path)

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
      if self.snapshot.game_pad.enter():
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
  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    self.record_score()
    self.snapshot.save(self.profile.path)

    self.next_stage = self.snapshot.stage
    self.next_stage += 1
    if self.snapshot.level == GameLevel.BOY:
      if self.next_stage > [e for e in BoyStage][-1]:
        self.cleared = True

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
    if self.cleared:
      return GameClearScene(self, self.point)

    if self.time_seq.ended:
      if self.snapshot.game_pad.enter():
        self.snapshot.stage = self.next_stage
        self.snapshot.save(self.profile.path)
        return ReadyScene(self, self.point)

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
  JOY_MAX = 3

  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    self.record_score()
    self.snapshot.save(self.profile.path)

    self.cleared = False
    self.next_level = self.snapshot.level+1
    if self.next_level > [e for e in GameLevel][-1]:
      self.cleared = True

    self.show_clear = False
    self.jumper_joy_count = 0
    self.show_thanks = False

    def show_clear(start: bool) -> bool:
      self.show_clear = True
      self.snapshot.jumper.joy()
      self.jumper_joy_count = 0
      return True

    def joy_jumper(start: bool) -> bool:
      if not self.snapshot.jumper.joying:
        self.jumper_joy_count += 1
        if self.jumper_joy_count > self.JOY_MAX:
          return True
        else:
          self.snapshot.jumper.joy()
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
      if self.snapshot.game_pad.enter():
        self.snapshot.level = self.next_level if not self.cleared else GameLevel.BOY
        self.snapshot.stage = 0
        return TitleScene(self)
    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.show_clear:
      clear_text = self.text(self.string('GAME_CLEAR' if not self.cleared else 'GAME_CLEAR_ALL'))
      clear_text.center = self.subtitle_center()
      subjects.append(clear_text)

    if self.show_thanks:
      thanks_text = self.text(self.string('GAME_CLEAR_THANKS'))
      thanks_text.center = self.menu_middle_center()
      subjects.append(thanks_text)

    return subjects
