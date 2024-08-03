from enum import IntEnum
from game import (
  Coordinate, Size,
  Text,
  GameProfile, Stopwatch, Timer,
)
from core import (
  GamePad,
  Score,
  Jumper, Ball,
  Snapshot, GameScreen as BaseGameScreen, Scene,
)
from component import (
  GameLevel, BoyStage,
  BoyStage1Field,
  BoyJumper,
  BoyStage1Ball,
)
from typing import Any, Self
import pyxel


GAME_TITLE: dict[int, str] = { GameLevel.BOY: 'JUMP BOY' }
GAME_RELEASE_YEAR = 2024
JUMPER: dict[int, str] = { GameLevel.BOY: 'BOY' }
JUMPER_START_X = 40.0
PLAY_TIME = 100


class OpeningGameScreen(BaseGameScreen):
  def draw(self, transparent_color: int) -> None:
    self.snapshot.field.draw(transparent_color)

    for ball in self.snapshot.balls:
      ball.draw(transparent_color)

    self.snapshot.jumper.draw(transparent_color)


class TitleGameScreen(BaseGameScreen):
  def draw(self, transparent_color: int) -> None:
    self.snapshot.field.draw(transparent_color)

    for ball in self.snapshot.balls:
      ball.draw(transparent_color)

    self.snapshot.jumper.draw(transparent_color)

    title_text = Text(self.profile.title, pyxel.COLOR_WHITE)
    title_text.origin = Coordinate(
      self.window_center_origin(Size(title_text.length, title_text.text_size())).x,
      title_text.text_size()*3,
    )
    title_text.draw(transparent_color)

    copyright_text = Text('© {} {}'.format(GAME_RELEASE_YEAR, self.profile.copyright), pyxel.COLOR_WHITE)
    copyright_text.origin = Coordinate(
      self.window_center_origin(Size(copyright_text.length, copyright_text.text_size())).x,
      self.snapshot.field.ground_top-copyright_text.text_size()*5,
    )
    copyright_text.draw(transparent_color)


class StageGameScreen(BaseGameScreen):
  def draw(self, transparent_color: int) -> None:
    self.snapshot.field.draw(transparent_color)

    for ball in self.snapshot.balls:
      ball.draw(transparent_color)

    self.snapshot.jumper.draw(transparent_color)

    stage_text = Text('STAGE.{:02}'.format(self.snapshot.stage+1), pyxel.COLOR_WHITE)
    stage_text.origin = Coordinate(stage_text.text_size(), stage_text.text_size())
    stage_text.draw(transparent_color)

    if PLAY_TIME in self.snapshot.timers:
      playing_time_text = Text(
        '{:02}:{:02}.{:03}'.format(
          int(self.snapshot.timers[PLAY_TIME].sec/60),
          int(self.snapshot.timers[PLAY_TIME].sec%60),
          self.snapshot.timers[PLAY_TIME].msec%1000
        ),
        pyxel.COLOR_WHITE,
      )
      playing_time_text.origin = Coordinate(
        self.window_center_origin(
          Size(playing_time_text.length,
              playing_time_text.text_size()),
        ).x,
        playing_time_text.text_size(),
      )
      playing_time_text.draw(transparent_color)

    score_text = Text(
      '{}:{:04}'.format(JUMPER[self.snapshot.level], self.snapshot.score.point),
      pyxel.COLOR_WHITE,
    )
    score_text.origin = Coordinate(
      self.profile.window_size.width-score_text.length-score_text.text_size(),
      score_text.text_size(),
    )
    score_text.draw(transparent_color)


class OpeningScene(Scene):
  class Time(IntEnum):
    JUMPER_WAIT = 1
    TITLE_WAIT = 2
    TITLE = 3

  TITLE_Y_MOVE_MIN = 1
  TITLE_Y_MAX = Text.text_size()*3

  def __init__(self, profile: GameProfile) -> None:
    game_pad = GamePad()
    score = Score()
    level = GameLevel.BOY
    stage = BoyStage.STAGE_1
    field = BoyStage1Field(profile.window_size)
    balls: list[Ball] = [BoyStage1Ball()]
    jumper = BoyJumper()
    snapshot = Snapshot(game_pad, score, level, stage, field, balls, jumper)

    super().__init__(
      profile,
      Stopwatch(profile.fps),
      snapshot,
      OpeningGameScreen(profile, snapshot),
    )

    pyxel.title(GAME_TITLE[level])

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

    self.snapshot.timers = {
      self.Time.JUMPER_WAIT: Timer.set_sec(self.stopwatch, 1, True),
      self.Time.TITLE_WAIT: Timer.set_sec(self.stopwatch, 1),
      self.Time.TITLE: Timer.set_sec(self.stopwatch, 2),
    }

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      return TitleScene(self)

    if self.snapshot.timers[self.Time.JUMPER_WAIT].over():
      if self.snapshot.timers[self.Time.TITLE].running():
        if self.snapshot.timers[self.Time.TITLE].over():
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
              self.snapshot.timers[self.Time.TITLE_WAIT].resume()
          else:
            if self.snapshot.timers[self.Time.TITLE_WAIT].over():
              self.title_y = -Text.text_size()
        else:
          if self.title_y < self.TITLE_Y_MAX:
            self.title_y += self.TITLE_Y_MOVE_MIN
          else:
            self.snapshot.timers[self.Time.TITLE].resume()

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.title_y is not None:
      title_text = Text(self.profile.title, pyxel.COLOR_WHITE)
      title_text.origin = Coordinate(
        self.screen.window_center_origin(Size(title_text.length, title_text.text_size())).x,
        self.title_y,
      )
      title_text.draw(transparent_color)


class TitleScene(Scene):
  class Time(IntEnum):
    START_PULSE = 1
    START = 2
    START_PULSE_FAST = 3

  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.stopwatch,
      scene.snapshot,
      TitleGameScreen(scene.profile, scene.snapshot),
    )

    pyxel.title(GAME_TITLE[self.snapshot.level])

    self.snapshot.jumper.stop()
    self.snapshot.jumper.origin = Coordinate(
      self.snapshot.field.right-JUMPER_START_X,
      self.snapshot.jumper.origin.y,
    )

    self.show_start = True
    self.snapshot.timers = {
      self.Time.START_PULSE: Timer.set_sec(self.stopwatch, 1, True),
      self.Time.START: Timer.set_sec(self.stopwatch, 2),
      self.Time.START_PULSE_FAST: Timer.set_msec(self.stopwatch, 200),
    }

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      self.snapshot.timers[self.Time.START].resume()
      self.snapshot.timers[self.Time.START_PULSE_FAST].resume()

    if not self.snapshot.timers[self.Time.START].running():
      if self.snapshot.timers[self.Time.START_PULSE].over():
        self.show_start = not self.show_start
        self.snapshot.timers[self.Time.START_PULSE].reset()
    else:
      if self.snapshot.timers[self.Time.START_PULSE_FAST].over():
        self.show_start = not self.show_start
        self.snapshot.timers[self.Time.START_PULSE_FAST].reset()

      if self.snapshot.timers[self.Time.START].over():
        return GameStartScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.show_start:
      start_text = Text('CLICK START', pyxel.COLOR_WHITE)
      start_text.origin = Coordinate(
        self.screen.window_center_origin(Size(start_text.length, start_text.text_size())).x,
        self.screen.window_center_origin(Size(start_text.length, start_text.text_size())).y-start_text.text_size(),
      )
      start_text.draw(transparent_color)


class GameStartScene(Scene):
  class Time(IntEnum):
    START_WAIT = 1
    START = 2

  START_SEC = 3

  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.stopwatch,
      scene.snapshot,
      StageGameScreen(scene.profile, scene.snapshot),
    )

    pyxel.title(GAME_TITLE[self.snapshot.level])

    self.snapshot.timers = {
      self.Time.START_WAIT: Timer.set_sec(self.stopwatch, 1, True),
      self.Time.START: Timer.set_sec(self.stopwatch, self.START_SEC),
    }

  def update(self) -> Self | Any:
    if self.snapshot.timers[self.Time.START_WAIT].over():
      if not self.snapshot.timers[self.Time.START].running():
        self.snapshot.timers[self.Time.START].resume()

    if self.snapshot.timers[self.Time.START].over():
      for ball in self.snapshot.balls:
        ball.roll()
      self.snapshot.jumper.standby()
      return GamePlayScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.snapshot.timers[self.Time.START].running():
      wait_sec = max(self.START_SEC-self.snapshot.timers[self.Time.START].sec, 1)
      wait_sec = min(wait_sec, self.START_SEC)
      start_wait_time_text = Text(str(wait_sec), pyxel.COLOR_WHITE)
      start_wait_time_text.origin = Coordinate(
        self.screen.window_center_origin(
          Size(start_wait_time_text.length,
               start_wait_time_text.text_size()),
        ).x,
        self.screen.window_center_origin(
          Size(start_wait_time_text.length, start_wait_time_text.text_size())
        ).y-start_wait_time_text.text_size()*4,
      )
      start_wait_time_text.draw(transparent_color)

class GamePlayScene(Scene):
  STAGE_LIMIT_SEC: dict[int, dict[int, int]] = {
    GameLevel.BOY: {
      BoyStage.STAGE_1: 30,
    },
  }

  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.stopwatch,
      scene.snapshot,
      StageGameScreen(scene.profile, scene.snapshot),
    )

    if PLAY_TIME in scene.snapshot.timers:
      self.snapshot.timers = {
        PLAY_TIME: scene.snapshot.timers[PLAY_TIME]
      }
    else:
      self.snapshot.timers = {
        PLAY_TIME: Timer.set_sec(
          self.stopwatch,
          self.STAGE_LIMIT_SEC[self.snapshot.level][self.snapshot.stage],
        ),
      }
    self.snapshot.timers[PLAY_TIME].resume()

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.cancel():
      self.snapshot.timers[PLAY_TIME].pause()
      return GamePauseScene(self)

    for ball in self.snapshot.balls:
      if ball.hit(self.snapshot.jumper):
        self.snapshot.timers[PLAY_TIME].pause()

        self.snapshot.jumper.down()

        self.snapshot.jumper.stop()
        for ball in self.snapshot.balls:
          ball.stop()
        return GameOverScene(self)

    if self.snapshot.timers[PLAY_TIME].over():
      self.snapshot.timers[PLAY_TIME].pause()

      self.snapshot.jumper.stop()

      for ball in self.snapshot.balls:
        ball.stop()
      return GameStageClearScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class GamePauseScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.stopwatch,
      scene.snapshot,
      StageGameScreen(scene.profile, scene.snapshot),
    )

    if PLAY_TIME in scene.snapshot.timers:
      self.snapshot.timers = {
        PLAY_TIME: scene.snapshot.timers[PLAY_TIME]
      }

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      return GamePlayScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class GameOverScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.stopwatch,
      scene.snapshot,
      StageGameScreen(scene.profile, scene.snapshot),
    )

    if PLAY_TIME in scene.snapshot.timers:
      self.snapshot.timers = {
        PLAY_TIME: scene.snapshot.timers[PLAY_TIME]
      }

  def update(self) -> Self | Any:
    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class GameStageClearScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(
      scene.profile,
      scene.stopwatch,
      scene.snapshot,
      StageGameScreen(scene.profile, scene.snapshot),
    )

    if PLAY_TIME in scene.snapshot.timers:
      self.snapshot.timers = {
        PLAY_TIME: scene.snapshot.timers[PLAY_TIME]
      }

  def update(self) -> Self | Any:
    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)
