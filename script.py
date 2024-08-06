from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Any, Self, Tuple
from game import (
  Coordinate,
  Image, Text,
  GameProfile, Language, StringRes, Stopwatch, Timer,
)
from core import (
  GamePad,
  Score, ScoreBoard,
  Ball, Jumper,
  Snapshot, Scene,
)
from component import (
  GameLevel, BoyStage,
  BoyStage1Field,
  BoyJumper,
  BoyStage1Ball,
)
import pyxel


class Strings(StrEnum):
  TITLE_BOY = "TITLE_BOY"
  GAME_START = "GAME_START"
  SCORE_RANKING = "SCORE_RANKING"
  NO_SCORE = "NO_SCORE"
  STAGE = "STAGE"
  SCORE_BOY = "SCORE_BOY"
  PAUSE = "PAUSE"
  PAUSE_RESTART = "PAUSE_RESTART"
  GAME_OVER = "GAME_OVER"
  GAME_OVER_END = "GAME_OVER_END"
  STAGE_CLEAR = "STAGE_CLEAR"
  STAGE_CLEAR_NEXT = "STAGE_CLEAR_NEXT"
  GAME_CLEAR = "GAME_CLEAR"
  GAME_CLEAR_END = "GAME_CLEAR_END"


class Time(IntEnum):
  OPENING_JUMPER_WAIT = 1
  OPENING_TITLE_WAIT = 2
  OPENING_TITLE = 3

  TITLE_START = 11
  TITLE_SCORE_START = 12
  TITLE_SCORE_WAIT = 13

  STAGE_PLAY_TIME = 21

  READY_WAIT = 31
  READY = 32

  GAME_OVER_WAIT = 41
  GAME_OVER = 42

  STAGE_CLEAR_WAIT = 51
  STAGE_CLEAR_JUMPER_WAIT = 52

  GAME_CLEAR_WAIT = 61
  GAME_CLEAR_JUMPER_WAIT = 62


GAME_TITLE: dict[int, str] = {
  GameLevel.BOY: Strings.TITLE_BOY,
}
SCORE: dict[int, str] = {
  GameLevel.BOY: Strings.SCORE_BOY,
}


class BaseScene(Scene):
  MENU_MARGIN_X = Text.word_size().width
  MENU_MARGIN_Y = Text.word_size().height
  JUMPER_START_X = Image.basic_size().width*5

  def __init__(
    self,
    profile: GameProfile,
    string_res: StringRes,
    stopwatch: Stopwatch,
    timers: dict[int, Timer],
    snapshot: Snapshot,
  ) -> None:
    super().__init__(profile, string_res, stopwatch, timers, snapshot)
    self.text_pulse_timers: dict[int, Tuple[Timer, bool]] = {}

  def menu_left_top(self) -> Coordinate:
    return Coordinate(self.MENU_MARGIN_X, self.MENU_MARGIN_Y)

  def menu_center_top(self) -> Coordinate:
    return Coordinate(self.profile.window_size.center.x, self.MENU_MARGIN_Y+Text.word_size().height/2)

  def menu_right_top(self, text: Text) -> Coordinate:
    return Coordinate(
      self.profile.window_size.width-self.MENU_MARGIN_X-text.size.width,
      self.MENU_MARGIN_Y,
    )

  def title_center(self) -> Coordinate:
    return Coordinate(
      self.profile.window_size.center.x,
      self.MENU_MARGIN_Y+Text.word_size().height*2+Text.word_size().height/2,
    )

  def subtitle_center(self) -> Coordinate:
    return Coordinate(
      self.profile.window_size.center.x,
      self.MENU_MARGIN_Y+Text.word_size().height*4+Text.word_size().height/2,
    )

  def menu_center(self) -> Coordinate:
    return Coordinate(self.profile.window_size.center.x, self.profile.window_size.center.y)

  def menu_center_bottom(self) -> Coordinate:
    return Coordinate(
      self.profile.window_size.center.x,
      self.snapshot.field.ground_top-self.MENU_MARGIN_Y-Text.word_size().height*2+Text.word_size().height/2,
    )

  def ball_init_origin(self, ball: Ball) -> Coordinate:
    return Coordinate(
      self.snapshot.field.left-ball.size.width,
      self.snapshot.field.bottom-ball.size.height,
    )

  def jumper_init_origin(self, jumper: Jumper) -> Coordinate:
    return Coordinate(
      self.snapshot.field.right,
      self.snapshot.field.bottom-jumper.size.height,
    )

  def jumper_start_x(self) -> float:
    return self.snapshot.field.right-self.JUMPER_START_X

  def to_text(self, string: str) -> Text:
    return Text(string, pyxel.COLOR_WHITE)

  def add_pulse_text(self, text_id: int, msec: int, show: bool) -> None:
    self.text_pulse_timers[text_id] = (Timer.set_msec(self.stopwatch, msec, True), show)

  def show_pulse_text(self, text_id: int) -> bool:
    if text_id in self.text_pulse_timers:
      return self.text_pulse_timers[text_id][1]
    return False

  def remove_pulse_text(self, text_id) -> None:
    if text_id in self.text_pulse_timers:
      del self.text_pulse_timers[text_id]

  def update(self) -> Self | Any:
    new_text_pulse_timers: dict[int, Tuple[Timer, bool]] = {}
    for (k, v) in self.text_pulse_timers.items():
      if v[0].over():
        v[0].reset()
        new_text_pulse_timers[k] = (v[0], not v[1])
      else:
        new_text_pulse_timers[k] = v
    self.text_pulse_timers = new_text_pulse_timers
    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.profile.debug:
      stopwatch_text = self.to_text(
        '{:02}:{:02}:{:02}:{:03}'.format(
          int(self.stopwatch.sec/60/60),
          int(self.stopwatch.sec/60%60),
          int(self.stopwatch.sec%60),
          self.stopwatch.msec%1000,
        )
      )
      stopwatch_text.origin = Coordinate(self.profile.window_size.width-stopwatch_text.size.width, 0)
      stopwatch_text.draw(transparent_color)


class OpeningScene(BaseScene):
  MOVE_TITLE_Y_MIN = 1

  def __init__(self, profile: GameProfile, string_res: StringRes) -> None:
    super().__init__(
      profile,
      string_res,
      Stopwatch(profile.fps),
      {},
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

    self.snapshot.load(__file__)
    self.title = self.string(GAME_TITLE[self.snapshot.level])

    for ball in self.snapshot.balls:
      ball.origin = self.ball_init_origin(ball)
    self.snapshot.jumper.origin = self.jumper_init_origin(self.snapshot.jumper)

    self.walked_jumper: bool | None = None
    self.title_y: float | None = None

    self.timers = {
      Time.OPENING_JUMPER_WAIT: Timer.set_sec(self.stopwatch, 2, True),
      Time.OPENING_TITLE_WAIT: Timer.set_sec(self.stopwatch, 1),
      Time.OPENING_TITLE: Timer.set_sec(self.stopwatch, 1),
    }

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      return TitleScene(self)

    if self.timers[Time.OPENING_JUMPER_WAIT].over():
      if self.timers[Time.OPENING_TITLE].running():
        if self.timers[Time.OPENING_TITLE].over():
          return TitleScene(self)
      else:
        if self.title_y is None:
          if self.walked_jumper is None:
            self.snapshot.jumper.walk(self.jumper_start_x())
            self.walked_jumper = False
          elif not self.walked_jumper:
            if self.snapshot.jumper.action == Jumper.Action.STOP:
              self.walked_jumper = True
              self.timers[Time.OPENING_TITLE_WAIT].resume()
          else:
            if self.timers[Time.OPENING_TITLE_WAIT].over():
              self.title_y = -Text.word_size().height-Text.word_size().height/2
              self.walked_jumper = None
        else:
          if self.title_y < self.title_center().y:
            self.title_y += self.MOVE_TITLE_Y_MIN
          else:
            self.timers[Time.OPENING_TITLE].resume()

    for ball in self.snapshot.balls:
      ball.update(self.snapshot.field)
    self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.title_y is not None:
      title_text = self.to_text(self.profile.title)
      title_text.center = Coordinate(self.title_center().x, self.title_y)
      title_text.draw(transparent_color)


class TitleScene(BaseScene):
  START_TEXT = 1
  SCORE_RANKING_NUM = 3

  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.string_res,
      scene.stopwatch,
      scene.timers,
      scene.snapshot,
    )

    for ball in self.snapshot.balls:
      ball.stop()
      ball.origin = self.ball_init_origin(ball)
    self.snapshot.jumper.stop()
    self.snapshot.jumper.origin = Coordinate(
      self.jumper_start_x(),
      self.jumper_init_origin(self.snapshot.jumper).y
    )

    self.show_score = False
    self.walked_jumper: bool | None = None

    self.timers = {
      Time.TITLE_START: Timer.set_sec(self.stopwatch, 1),
      Time.TITLE_SCORE_START: Timer.set_sec(self.stopwatch, 30),
      Time.TITLE_SCORE_WAIT: Timer.set_sec(self.stopwatch, 1),
    }
    self.add_pulse_text(self.START_TEXT, 1000, True)

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      self.timers[Time.TITLE_START].resume()
      self.remove_pulse_text(self.START_TEXT)
      self.add_pulse_text(self.START_TEXT, 120, True)

    if self.timers[Time.TITLE_START].running():
      if self.timers[Time.TITLE_START].over():
        return ReadyScene(self, 0)

    if self.timers[Time.TITLE_SCORE_START].over():
      if self.walked_jumper is None:
        self.snapshot.jumper.walk(self.snapshot.field.right)
        self.walked_jumper = False
      elif not self.walked_jumper:
        if self.snapshot.jumper.action == Jumper.Action.STOP:
          self.walked_jumper = True
      else:
        if self.timers[Time.TITLE_SCORE_WAIT].over():
          self.show_score = True
        else:
          self.timers[Time.TITLE_SCORE_WAIT].resume()
    else:
      self.timers[Time.TITLE_SCORE_START].resume()

    for ball in self.snapshot.balls:
      ball.update(self.snapshot.field)
    self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.show_score:
      text_center = self.menu_center_top()

      score_text = self.to_text(self.string(Strings.SCORE_RANKING))
      score_text.center = text_center
      score_text.draw(transparent_color)

      text_center.y += Text.word_size().height*2
      scores = self.snapshot.score_board.ranking(self.SCORE_RANKING_NUM)
      if len(scores) > 0:
        for (index, score) in enumerate(scores):
          text_center.y += Text.word_size().height
          score_text = self.to_text(
            '{}.{}.{:02} {:04} {}'.format(
              index+1,
              self.string(SCORE[score.level]),
              score.stage,
              score.point,
              score.created_at.strftime('%Y/%m/%d %H:%M:%S'),
            )
          )
          score_text.center = text_center
          score_text.draw(transparent_color)
      else:
        text_center.y += Text.word_size().height
        no_score_text = self.to_text(self.string(Strings.NO_SCORE))
        no_score_text.center = text_center
        no_score_text.draw(transparent_color)

      if self.show_pulse_text(self.START_TEXT):
        start_text = self.to_text(self.string(Strings.GAME_START))
        start_text.center = self.menu_center_bottom()
        start_text.draw(transparent_color)
    else:
      title_text = self.to_text(self.profile.title)
      title_text.center = self.title_center()
      title_text.draw(transparent_color)

      if self.show_pulse_text(self.START_TEXT):
        start_text = self.to_text(self.string(Strings.GAME_START))
        start_text.center = self.menu_center()
        start_text.draw(transparent_color)

      copyright_text = self.to_text('(c) {} {}'.format(self.profile.release_year, self.profile.copyright))
      copyright_text.center = self.menu_center_bottom()
      copyright_text.draw(transparent_color)


class BaseStageScene(BaseScene):
  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(
      scene.profile,
      scene.string_res,
      scene.stopwatch,
      scene.timers,
      scene.snapshot,
    )
    self.point = point

  def record_score(self) -> None:
    self.snapshot.score_board.scores.append(
      Score(datetime.now(), self.snapshot.level, self.snapshot.stage, self.point)
    )
    self.point = 0

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    stage_text = self.to_text('{}.{:02}'.format(self.string(Strings.STAGE), self.snapshot.stage+1))
    stage_text.origin = self.menu_left_top()
    stage_text.draw(transparent_color)

    if Time.STAGE_PLAY_TIME in self.timers:
      play_time_text = self.to_text(
        '{:02}:{:02}.{:03}'.format(
          int(self.timers[Time.STAGE_PLAY_TIME].sec/60),
          int(self.timers[Time.STAGE_PLAY_TIME].sec%60),
          self.timers[Time.STAGE_PLAY_TIME].msec%1000
        )
      )
      play_time_text.center = self.menu_center_top()
      play_time_text.draw(transparent_color)

    score_text = self.to_text('{}:{:04}'.format(self.string(SCORE[self.snapshot.level]), self.point))
    score_text.origin = self.menu_right_top(score_text)
    score_text.draw(transparent_color)


class ReadyScene(BaseStageScene):
  START_SEC = 3

  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    for ball in self.snapshot.balls:
      ball.stop()
      ball.origin = self.ball_init_origin(ball)
    self.snapshot.jumper.stop()
    self.snapshot.jumper.origin = Coordinate(
      self.jumper_start_x(),
      self.jumper_init_origin(self.snapshot.jumper).y,
    )

    self.timers = {
      Time.READY_WAIT: Timer.set_sec(self.stopwatch, 1),
      Time.READY: Timer.set_sec(self.stopwatch, self.START_SEC),
    }

  def update(self) -> Self | Any:
    if self.timers[Time.READY_WAIT].over():
      if not self.timers[Time.READY].running():
        self.timers[Time.READY].resume()

    if self.timers[Time.READY].over():
      for ball in self.snapshot.balls:
        ball.roll()
      self.snapshot.jumper.standby()
      return PlayScene(self, self.point)
    else:
      self.timers[Time.READY_WAIT].resume()

    for ball in self.snapshot.balls:
      ball.update(self.snapshot.field)
    self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.timers[Time.READY].running():
      wait_sec = max(self.START_SEC-self.timers[Time.READY].sec, 1)
      wait_sec = min(wait_sec, self.START_SEC)
      start_wait_time_text = self.to_text(str(wait_sec))
      start_wait_time_text.center = self.subtitle_center()
      start_wait_time_text.draw(transparent_color)


class PlayScene(BaseStageScene):
  STAGE_LIMIT_SEC: dict[int, dict[int, int]] = {
    GameLevel.BOY: {
      BoyStage.STAGE_1: 30,
    },
  }

  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    if Time.STAGE_PLAY_TIME not in self.timers:
      self.timers = {
        Time.STAGE_PLAY_TIME: Timer.set_sec(
          self.stopwatch,
          self.STAGE_LIMIT_SEC[self.snapshot.level][self.snapshot.stage],
        ),
      }
    self.timers[Time.STAGE_PLAY_TIME].resume()

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.cancel():
      self.timers[Time.STAGE_PLAY_TIME].pause()
      return PauseScene(self, self.point)

    for ball in self.snapshot.balls:
      if ball.hit(self.snapshot.jumper):
        self.timers[Time.STAGE_PLAY_TIME].pause()
        self.snapshot.jumper.down()
        for ball in self.snapshot.balls:
          ball.stop()
        return GameOverScene(self, self.point)

    if self.timers[Time.STAGE_PLAY_TIME].over():
      self.timers[Time.STAGE_PLAY_TIME].pause()
      self.snapshot.jumper.stop()
      for ball in self.snapshot.balls:
        ball.stop()
      return StageClearScene(self, self.point)

    for ball in self.snapshot.balls:
      ball.update(self.snapshot.field)
    self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class PauseScene(BaseStageScene):
  RESTART_TEXT = 1

  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)
    self.add_pulse_text(self.RESTART_TEXT, 1000, False)

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter() or self.snapshot.game_pad.cancel():
      return PlayScene(self, self.point)
    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    pause_text = self.to_text(self.string(Strings.PAUSE))
    pause_text.center = self.subtitle_center()
    pause_text.draw(transparent_color)

    if self.show_pulse_text(self.RESTART_TEXT):
      restart_text = self.to_text(self.string(Strings.PAUSE_RESTART))
      restart_text.center = self.menu_center()
      restart_text.draw(transparent_color)


class GameOverScene(BaseStageScene):

  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    self.record_score()
    self.snapshot.save(__file__)

    self.timers.update({
      Time.GAME_OVER_WAIT: Timer.set_sec(self.stopwatch, 1, True),
      Time.GAME_OVER: Timer.set_sec(self.stopwatch, 2),
    })

  def update(self) -> Self | Any:
    if self.timers[Time.GAME_OVER_WAIT].over():
      if self.timers[Time.GAME_OVER].over():
        if self.snapshot.game_pad.enter():
          return TitleScene(self)
      else:
        self.timers[Time.GAME_OVER].resume()

    for ball in self.snapshot.balls:
      ball.update(self.snapshot.field)
    self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.timers[Time.GAME_OVER_WAIT].over():
      game_over_text = self.to_text(self.string(Strings.GAME_OVER))
      game_over_text.center = self.subtitle_center()
      game_over_text.draw(transparent_color)

    if self.timers[Time.GAME_OVER].over():
      end_text = self.to_text(self.string(Strings.GAME_OVER_END))
      end_text.center = self.menu_center()
      end_text.draw(transparent_color)


class StageClearScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    self.next_stage = self.snapshot.stage
    self.next_stage += 1
    if self.snapshot.level == GameLevel.BOY:
      if self.next_stage > [e for e in BoyStage][-1]:
        self.cleared = True

    self.record_score()
    self.snapshot.save(__file__)

    self.walked_jumper: bool | None = None

    self.timers.update({
      Time.STAGE_CLEAR_WAIT: Timer.set_sec(self.stopwatch, 1, True),
      Time.STAGE_CLEAR_JUMPER_WAIT: Timer.set_sec(self.stopwatch, 2, True),
    })

  def update(self) -> Self | Any:
    if self.cleared:
      return GameClearScene(self, self.point)

    if self.timers[Time.STAGE_CLEAR_WAIT].over():
      if self.timers[Time.STAGE_CLEAR_JUMPER_WAIT].over():
        if self.walked_jumper is not None:
          self.walked_jumper = False
          self.snapshot.jumper.walk(self.snapshot.field.left-self.snapshot.jumper.size.width)
        elif not self.walked_jumper:
          if self.snapshot.jumper.action == Jumper.Action.STOP:
            self.walked_jumper = True
        elif self.walked_jumper:
          if self.snapshot.game_pad.enter():
            self.snapshot.stage = self.next_stage
            self.snapshot.save(__file__)
            return ReadyScene(self, self.point)
      else:
        self.timers[Time.STAGE_CLEAR_JUMPER_WAIT].resume()

    for ball in self.snapshot.balls:
      ball.update(self.snapshot.field)
    self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.timers[Time.STAGE_CLEAR_WAIT].over():
      clear_text = self.to_text(self.string(Strings.STAGE_CLEAR))
      clear_text.center = self.subtitle_center()
      clear_text.draw(transparent_color)

    if self.timers[Time.STAGE_CLEAR_JUMPER_WAIT].over():
      next_text = self.to_text(self.string(Strings.STAGE_CLEAR_NEXT))
      next_text.center = self.menu_center()
      next_text.draw(transparent_color)


class GameClearScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int) -> None:
    super().__init__(scene, point)

    self.cleared = False
    self.next_level = self.snapshot.level+1

    if self.next_level > [e for e in GameLevel][-1]:
      self.cleared = True

    self.record_score()
    self.snapshot.save(__file__)

    self.walked_jumper: bool | None = None

    self.timers.update({
      Time.GAME_CLEAR_WAIT: Timer.set_sec(self.stopwatch, 1, True),
      Time.GAME_CLEAR_JUMPER_WAIT: Timer.set_sec(self.stopwatch, 2, True),
    })

  def update(self) -> Self | Any:
    if self.timers[Time.GAME_CLEAR_WAIT].over():
      if self.timers[Time.GAME_CLEAR_JUMPER_WAIT].over():
        if self.walked_jumper is not None:
          self.walked_jumper = False
          self.snapshot.jumper.walk(self.snapshot.field.right)
        elif not self.walked_jumper:
          if self.snapshot.jumper.action == Jumper.Action.STOP:
            self.walked_jumper = True
        elif self.walked_jumper:
          if self.snapshot.game_pad.enter():
            if not self.cleared:
              self.snapshot.level = self.next_level
            else:
              self.snapshot.level = GameLevel.BOY
            self.snapshot.stage = 0
            return TitleScene(self)
      else:
        self.timers[Time.GAME_CLEAR_JUMPER_WAIT].resume()

    for ball in self.snapshot.balls:
      ball.update(self.snapshot.field)
    self.snapshot.jumper.update(self.snapshot.game_pad, self.snapshot.field)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.timers[Time.GAME_CLEAR_WAIT].over():
      clear_text = self.to_text(self.string(Strings.GAME_CLEAR))
      clear_text.center = self.subtitle_center()
      clear_text.draw(transparent_color)

    if self.timers[Time.GAME_CLEAR_JUMPER_WAIT].over():
      end_text = self.to_text(self.string(Strings.GAME_CLEAR_END))
      clear_text.center = self.menu_center()
      end_text.draw(transparent_color)
