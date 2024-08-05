from enum import IntEnum, StrEnum
from game import (
  Coordinate,
  Image, Text,
  GameProfile, Language, StringResource, Stopwatch, Timer,
)
from core import (
  GamePad,
  Score,
  Jumper,
  Snapshot, Scene,
)
from component import (
  GameLevel, BoyStage,
  BoyStage1Field,
  BoyJumper,
  BoyStage1Ball,
)
from typing import Any, Self
import pyxel


class GameStrings(StrEnum):
  TITLE_BOY = "TITLE_BOY"
  GAME_START = "GAME_START"
  STAGE = "STAGE"
  SCORE_BOY = "SCORE_BOY"
  PAUSE = "PAUSE"
  GAME_OVER = "GAME_OVER"
  STAGE_CLEAR = "STAGE_CLEAR"
  GAME_CLEAR_1 = "GAME_CLEAR_1"
  GAME_CLEAR_2 = "GAME_CLEAR_2"


class Time(IntEnum):
  OPENING_JUMPER_WAIT = 1
  OPENING_TITLE_WAIT = 2
  OPENING_TITLE = 3

  TITLE_START_PULSE = 11
  TITLE_START = 12
  TITLE_START_PULSE_FAST = 13

  STAGE_PLAY_TIME = 21

  STAGE_START_WAIT = 31
  STAGE_START = 32


GAME_TITLE: dict[int, str] = {
  GameLevel.BOY: GameStrings.TITLE_BOY,
}
RELEASE_YEAR = 2024

JUMPER_START_X = Image.measure_size().width*5
TITLE_Y = Text.word_size()*5


class OpeningScene(Scene):
  TITLE_Y_MOVE_MIN = 1

  def __init__(self, profile: GameProfile, string_res: StringResource) -> None:
    super().__init__(
      profile,
      string_res,
      Stopwatch(profile.fps),
      {},
      Snapshot(
        Language.EN,
        GamePad(),
        Score(),
        GameLevel.BOY,
        BoyStage.STAGE_1,
        BoyStage1Field(profile.window_size),
        [BoyStage1Ball()],
        BoyJumper(),
      ),
    )

    self.snapshot.load()

    self.title = string_res.string(GAME_TITLE[self.snapshot.level], self.snapshot.lang)

    for ball in self.snapshot.balls:
      ball.origin = Coordinate(
        self.snapshot.field.left-ball.size.width,
        self.snapshot.field.bottom-ball.size.height,
      )

    self.snapshot.jumper.origin = Coordinate(
      self.snapshot.field.right,
      self.snapshot.field.bottom-self.snapshot.jumper.size.height,
    )
    self.jumper_walked: bool | None = None

    self.title_y: int | None = None

    self.timers = {
      Time.OPENING_JUMPER_WAIT: Timer.set_sec(self.stopwatch, 1, True),
      Time.OPENING_TITLE_WAIT: Timer.set_sec(self.stopwatch, 1),
      Time.OPENING_TITLE: Timer.set_sec(self.stopwatch, 2),
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
          if self.jumper_walked is None:
            self.snapshot.jumper.walk(
              self.snapshot.field.right-JUMPER_START_X,
            )
            self.jumper_walked = False
          elif not self.jumper_walked:
            if self.snapshot.jumper.action == Jumper.Action.STOP:
              self.jumper_walked = True
              self.timers[Time.OPENING_TITLE_WAIT].resume()
          else:
            if self.timers[Time.OPENING_TITLE_WAIT].over():
              self.title_y = -Text.word_size()
        else:
          if self.title_y < TITLE_Y:
            self.title_y += self.TITLE_Y_MOVE_MIN
          else:
            self.timers[Time.OPENING_TITLE].resume()

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.title_y is not None:
      title_text = Text(self.profile.title, pyxel.COLOR_WHITE)
      title_text.center = Coordinate(self.profile.window_size.center.x, self.title_y+Text.word_size()/2)
      title_text.draw(transparent_color)


class TitleScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.string_res,
      scene.stopwatch,
      scene.timers,
      scene.snapshot,
    )

    self.snapshot.jumper.stop()
    self.snapshot.jumper.origin = Coordinate(
      self.snapshot.field.right-JUMPER_START_X,
      self.snapshot.jumper.origin.y,
    )

    self.show_start = True
    self.timers = {
      Time.TITLE_START_PULSE: Timer.set_sec(self.stopwatch, 1, True),
      Time.TITLE_START: Timer.set_sec(self.stopwatch, 2),
      Time.TITLE_START_PULSE_FAST: Timer.set_msec(self.stopwatch, 120),
    }

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      self.timers[Time.TITLE_START].resume()
      self.timers[Time.TITLE_START_PULSE_FAST].resume()

    if not self.timers[Time.TITLE_START].running():
      if self.timers[Time.TITLE_START_PULSE].over():
        self.show_start = not self.show_start
        self.timers[Time.TITLE_START_PULSE].reset()
    else:
      if self.timers[Time.TITLE_START_PULSE_FAST].over():
        self.show_start = not self.show_start
        self.timers[Time.TITLE_START_PULSE_FAST].reset()

      if self.timers[Time.TITLE_START].over():
        return StageStartScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    title_text = Text(self.profile.title, pyxel.COLOR_WHITE)
    title_text.center = Coordinate(self.profile.window_size.center.x, TITLE_Y+Text.word_size()/2)
    title_text.draw(transparent_color)

    if self.show_start:
      start_text = Text(
        self.string_res.string(GameStrings.GAME_START, self.snapshot.lang),
        pyxel.COLOR_WHITE,
      )
      start_text.center = Coordinate(self.profile.window_size.center.x, self.profile.window_size.center.y)
      start_text.draw(transparent_color)

    copyright_text = Text('(c) {} {}'.format(RELEASE_YEAR, self.profile.copyright), pyxel.COLOR_WHITE)
    copyright_text.center = Coordinate(
      self.profile.window_size.center.x,
      self.snapshot.field.ground_top-Text.word_size()*3-Text.word_size()/2,
    )
    copyright_text.draw(transparent_color)


class BaseStageScene(Scene):
  SCORE: dict[int, str] = {
    GameLevel.BOY: GameStrings.SCORE_BOY,
  }

  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.string_res,
      scene.stopwatch,
      scene.timers,
      scene.snapshot,
    )

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    stage_text = Text(
      '{}.{:02}'.format(
        self.string_res.string(GameStrings.STAGE, self.snapshot.lang),
        self.snapshot.stage+1,
      ),
      pyxel.COLOR_WHITE,
    )
    stage_text.origin = Coordinate(Text.word_size(), Text.word_size())
    stage_text.draw(transparent_color)

    if Time.STAGE_PLAY_TIME in self.timers:
      play_time_text = Text(
        '{:02}:{:02}.{:03}'.format(
          int(self.timers[Time.STAGE_PLAY_TIME].sec/60),
          int(self.timers[Time.STAGE_PLAY_TIME].sec%60),
          self.timers[Time.STAGE_PLAY_TIME].msec%1000
        ),
        pyxel.COLOR_WHITE,
      )
      play_time_text.center = Coordinate(
        self.profile.window_size.center.x,
        Text.word_size()+Text.word_size()/2,
      )
      play_time_text.draw(transparent_color)

    score_text = Text(
      '{}:{:04}'.format(
        self.string_res.string(self.SCORE[self.snapshot.level], self.snapshot.lang),
        self.snapshot.score.point,
      ),
      pyxel.COLOR_WHITE,
    )
    score_text.origin = Coordinate(
      self.profile.window_size.width-Text.word_size()-score_text.size.width,
      Text.word_size(),
    )
    score_text.draw(transparent_color)


class StageStartScene(BaseStageScene):
  START_SEC = 3

  def __init__(self, scene: Scene) -> None:
    super().__init__(scene)

    self.timers = {
      Time.STAGE_START_WAIT: Timer.set_sec(self.stopwatch, 1, True),
      Time.STAGE_START: Timer.set_sec(self.stopwatch, self.START_SEC),
    }

  def update(self) -> Self | Any:
    if self.timers[Time.STAGE_START_WAIT].over():
      if not self.timers[Time.STAGE_START].running():
        self.timers[Time.STAGE_START].resume()

    if self.timers[Time.STAGE_START].over():
      for ball in self.snapshot.balls:
        ball.roll()
      self.snapshot.jumper.standby()
      return StagePlayScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.timers[Time.STAGE_START].running():
      wait_sec = max(self.START_SEC-self.timers[Time.STAGE_START].sec, 1)
      wait_sec = min(wait_sec, self.START_SEC)
      start_wait_time_text = Text(str(wait_sec), pyxel.COLOR_WHITE)
      start_wait_time_text.center = Coordinate(self.profile.window_size.center.x, self.profile.window_size.center.y)
      start_wait_time_text.draw(transparent_color)


class StagePlayScene(BaseStageScene):
  STAGE_LIMIT_SEC: dict[int, dict[int, int]] = {
    GameLevel.BOY: {
      BoyStage.STAGE_1: 30,
    },
  }

  def __init__(self, scene: Scene) -> None:
    super().__init__(scene)

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
      return StagePauseScene(self)

    for ball in self.snapshot.balls:
      if ball.hit(self.snapshot.jumper):
        self.timers[Time.STAGE_PLAY_TIME].pause()

        self.snapshot.jumper.down()

        self.snapshot.jumper.stop()
        for ball in self.snapshot.balls:
          ball.stop()
        return GameOverScene(self)

    if self.timers[Time.STAGE_PLAY_TIME].over():
      self.timers[Time.STAGE_PLAY_TIME].pause()

      self.snapshot.jumper.stop()

      for ball in self.snapshot.balls:
        ball.stop()
      return StageClearScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class StagePauseScene(BaseStageScene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene)

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      return StagePlayScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    pause_text = Text(self.string_res.string(GameStrings.PAUSE, self.snapshot.lang), pyxel.COLOR_WHITE)
    pause_text.center = Coordinate(self.profile.window_size.center.x, self.profile.window_size.center.y)
    pause_text.draw(transparent_color)


class GameOverScene(BaseStageScene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene)

    self.snapshot.save()

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      return TitleScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    game_over_text = Text(self.string_res.string(GameStrings.GAME_OVER, self.snapshot.lang), pyxel.COLOR_WHITE)
    game_over_text.center = Coordinate(self.profile.window_size.center.x, self.profile.window_size.center.y)
    game_over_text.draw(transparent_color)


class StageClearScene(BaseStageScene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene)

    self.next_stage = self.snapshot.stage
    self.next_stage += 1
    if self.snapshot.level == GameLevel.BOY:
      if self.next_stage > [e for e in BoyStage][-1]:
        self.cleared = True

    self.snapshot.save()

  def update(self) -> Self | Any:
    if self.cleared:
      self.snapshot.save()
      return GameClearScene(self)

    if self.snapshot.game_pad.enter():
      self.snapshot.stage = self.next_stage
      self.snapshot.save()
      return StageStartScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    clear_text = Text(self.string_res.string(GameStrings.STAGE_CLEAR, self.snapshot.lang), pyxel.COLOR_WHITE)
    clear_text.center = Coordinate(self.profile.window_size.center.x, self.profile.window_size.center.y)
    clear_text.draw(transparent_color)


class GameClearScene(BaseStageScene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene)

    self.cleared = False
    self.next_level = self.snapshot.level+1

    if self.next_level > [e for e in GameLevel][-1]:
      self.cleared = True

    self.snapshot.save()

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      if not self.cleared:
        self.snapshot.level = self.next_level
      else:
        self.snapshot.level = GameLevel.BOY

      self.snapshot.stage = 0
      return TitleScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    clear1_text = Text(self.string_res.string(GameStrings.GAME_CLEAR_1, self.snapshot.lang), pyxel.COLOR_WHITE)
    clear1_text.center = Coordinate(self.profile.window_size.center.x, self.profile.window_size.center.y)
    clear1_text.draw(transparent_color)

    clear1_text = Text(self.string_res.string(GameStrings.GAME_CLEAR_2, self.snapshot.lang), pyxel.COLOR_WHITE)
    clear1_text.center = Coordinate(
      self.profile.window_size.center.x,
      self.profile.window_size.center.y+Text.word_size()+Text.word_size()/2,
    )
    clear1_text.draw(transparent_color)
