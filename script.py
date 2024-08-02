from game import (
  Coordinate, Size,
  Text,
  GameProfile, Stopwatch,
)
from core import (
  GamePad,
  Score,
  Ball,
  Snapshot, Scene,
)
from component import (
  GameLevel, BoyStage,
  BoyStage1Field,
  BoyJumper,
  BoyStage1Ball,
)
from typing import Self
import pyxel


GAME_TITLE: dict[int, str] = { GameLevel.BOY: 'JUMP BOY' }
GAME_DEVELOP_YEAR = 2024
JUMPER_START_X = 40.0
JUMPER: dict[int, str] = { GameLevel.BOY: 'BOY' }


class OpeningScene(Scene):
  JUMPER_WAIT_SEC = 1
  TITLE_WAIT_SEC = 2
  TITLE_SEC = 2

  def __init__(self, profile: GameProfile) -> None:
    game_pad = GamePad()
    score = Score()
    level = GameLevel.BOY
    stage = BoyStage.STAGE_1
    field = BoyStage1Field(profile.window_size)
    balls: list[Ball] = [BoyStage1Ball()]
    jumper = BoyJumper()

    super().__init__(profile, Stopwatch(profile.fps), Snapshot(game_pad, score, level, stage, field, balls, jumper))

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
    self.jumper_wait_timer_id = self.stopwatch.set_sec(self.JUMPER_WAIT_SEC)

    self.title_wait_timer_id: str | None = None
    self.title_timer_id: str | None = None

  def update(self) -> Self.__class__:
    if self.snapshot.game_pad.enter():
      return TitleScene(self)

    if self.stopwatch.over(self.jumper_wait_timer_id):
      if self.title_timer_id is None:
        if self.title_wait_timer_id is None:
          self.snapshot.jumper.walk(
            self.snapshot.field.right-JUMPER_START_X,
          )

          if self.title_wait_timer_id is None:
            self.title_wait_timer_id = self.stopwatch.set_sec(self.TITLE_WAIT_SEC)
        else:
          if self.stopwatch.over(self.title_wait_timer_id):
            self.title_timer_id = self.stopwatch.set_sec(self.TITLE_SEC)
      else:
        if self.stopwatch.over(self.title_timer_id):
          return TitleScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.title_timer_id is not None:
      title = Text(self.profile.title, pyxel.COLOR_WHITE)
      title.origin = Coordinate(
        self.window_center_origin(Size(title.length, title.text_size())).x,
        title.text_size()*3,
      )
      title.draw(transparent_color)

      copyright = Text('(c) {} {}'.format(GAME_DEVELOP_YEAR, self.profile.copyright), pyxel.COLOR_WHITE)
      copyright.origin = Coordinate(
        self.window_center_origin(Size(copyright.length, copyright.text_size())).x,
        self.snapshot.field.ground_top-copyright.text_size()*5,
      )
      copyright.draw(transparent_color)


class TitleScene(Scene):
  START_PULSE_SEC = 1
  START_WAIT_SEC = 1

  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

    pyxel.title(GAME_TITLE[self.snapshot.level])

    self.snapshot.jumper.stop()
    self.snapshot.jumper.origin = Coordinate(
      self.snapshot.field.right-JUMPER_START_X,
      self.snapshot.jumper.origin.y,
    )

    self.show_start = True
    self.start_pulse_timer_id = self.stopwatch.set_sec(self.START_PULSE_SEC)
    self.start_wait_timer_id: str | None = None

  def update(self) -> Self.__class__:
    if self.snapshot.game_pad.enter():
      if self.start_wait_timer_id is None:
        self.start_wait_timer_id = self.stopwatch.set_sec(self.START_WAIT_SEC)

    if self.start_wait_timer_id is None:
      if self.stopwatch.over(self.start_pulse_timer_id):
        self.show_start = not self.show_start
        self.start_pulse_timer_id = self.stopwatch.set_sec(self.START_PULSE_SEC)
    else:
      self.show_start = True
      if self.stopwatch.over(self.start_wait_timer_id):
        return GameStartScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    title = Text(self.profile.title, pyxel.COLOR_WHITE)
    title.origin = Coordinate(
      self.window_center_origin(Size(title.length, title.text_size())).x,
      title.text_size()*3,
    )
    title.draw(transparent_color)

    if self.show_start:
      start = Text('CLICK START', pyxel.COLOR_WHITE)
      start.origin = Coordinate(
        self.window_center_origin(Size(start.length, start.text_size())).x,
        self.window_center_origin(Size(start.length, start.text_size())).y-start.text_size(),
      )
      start.draw(transparent_color)

    copyright = Text('(c) {} {}'.format(GAME_DEVELOP_YEAR, self.profile.copyright), pyxel.COLOR_WHITE)
    copyright.origin = Coordinate(
      self.window_center_origin(Size(copyright.length, copyright.text_size())).x,
      self.snapshot.field.ground_top-copyright.text_size()*5,
    )
    copyright.draw(transparent_color)


class GameStartScene(Scene):
  START_WAIT_SEC = 1
  START_SEC = 3
  STAGE_LIMIT_SEC: dict[int, dict[int, int]] = { GameLevel.BOY: { BoyStage.STAGE_1: 30 } }

  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

    pyxel.title(GAME_TITLE[self.snapshot.level])

    self.start_wait_timer_id = self.stopwatch.set_sec(self.START_WAIT_SEC)
    self.start_timer_id: str | None = None

  def update(self) -> Self.__class__:
    if self.stopwatch.over(self.start_wait_timer_id):
      if self.start_timer_id is None:
        self.start_timer_id = self.stopwatch.set_sec(self.START_SEC)

    if self.start_timer_id is not None:
      if self.stopwatch.over(self.start_timer_id):
        for ball in self.snapshot.balls:
          ball.roll()
        self.snapshot.jumper.standby()
        self.snapshot.playing_timer_id = self.stopwatch.set_sec(self.STAGE_LIMIT_SEC[self.snapshot.level][self.snapshot.stage])
        return GamePlayScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    stage = Text('STAGE.{:02}'.format(self.snapshot.stage+1), pyxel.COLOR_WHITE)
    stage.origin = Coordinate(stage.text_size(), stage.text_size())
    stage.draw(transparent_color)

    if self.start_timer_id is not None:
      sec = self.stopwatch.elapsed_sec(self.start_timer_id)
      sec = sec if sec is not None else 0
      wait_sec = max(self.START_SEC-sec, 1)
      wait_sec = min(wait_sec, self.START_SEC)
      start_wait_timer = Text(str(wait_sec), pyxel.COLOR_WHITE)
      start_wait_timer.origin = Coordinate(
        self.window_center_origin(Size(start_wait_timer.length, start_wait_timer.text_size())).x,
        self.window_center_origin(Size(start_wait_timer.length, start_wait_timer.text_size())).y-start_wait_timer.text_size()*4,
      )
      start_wait_timer.draw(transparent_color)

    score = Text(
      '{}:{:04}'.format(JUMPER[self.snapshot.level], self.snapshot.score.point),
      pyxel.COLOR_WHITE,
    )
    score.origin = Coordinate(self.profile.window_size.width-score.length-score.text_size(), score.text_size())
    score.draw(transparent_color)


class GamePlayScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

  def update(self) -> Self.__class__:
    if self.snapshot.game_pad.cancel():
      if self.snapshot.playing_timer_id is not None:
        self.stopwatch.pause(self.snapshot.playing_timer_id)
      return GamePauseScene(self)

    for ball in self.snapshot.balls:
      if ball.hit(self.snapshot.jumper):
        if self.snapshot.playing_timer_id is not None:
          self.stopwatch.pause(self.snapshot.playing_timer_id)

        self.snapshot.jumper.down()

        self.snapshot.jumper.stop()
        for ball in self.snapshot.balls:
          ball.stop()
        return GameOverScene(self)

    if self.snapshot.playing_timer_id is not None:
      if self.stopwatch.over(self.snapshot.playing_timer_id):
        self.stopwatch.pause(self.snapshot.playing_timer_id)

        self.snapshot.jumper.stop()

        for ball in self.snapshot.balls:
          ball.stop()
        return GameStageClearScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    stage = Text('STAGE.{:02}'.format(self.snapshot.stage+1), pyxel.COLOR_WHITE)
    stage.origin = Coordinate(stage.text_size(), stage.text_size())
    stage.draw(transparent_color)

    if self.snapshot.playing_timer_id is not None:
      msec = self.stopwatch.elapsed_msec(self.snapshot.playing_timer_id)
      if msec is not None:
        playing_timer = Text(
          '{:02}:{:02}.{:03}'.format(
            int(msec/1000/60),
            int(msec/1000%60),
            msec%1000
          ),
          pyxel.COLOR_WHITE,
        )
        playing_timer.origin = Coordinate(
          self.window_center_origin(Size(playing_timer.length, playing_timer.text_size())).x,
          playing_timer.text_size(),
        )
        playing_timer.draw(transparent_color)

    score = Text(
      '{}:{:04}'.format(JUMPER[self.snapshot.level], self.snapshot.score.point),
      pyxel.COLOR_WHITE,
    )
    score.origin = Coordinate(self.profile.window_size.width-score.length-score.text_size(), score.text_size())
    score.draw(transparent_color)


class GamePauseScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

  def update(self) -> Self.__class__:
    if self.snapshot.game_pad.enter():
      new_scene = GamePlayScene(self)
      return new_scene

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class GameOverScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

  def update(self) -> Self.__class__:
    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class GameStageClearScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

  def update(self) -> Self.__class__:
    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)
