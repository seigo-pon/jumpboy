from game import (
  Coordinate, Size,
  Text,
  GameProfile, Stopwatch,
)
from core import (
  GamePad,
  Score,
  Field, Ball,
  Timer, Snapshot, Scene,
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
JUMPER_START_X = 40.0
JUMPER: dict[int, str] = { GameLevel.BOY: 'BOY' }


def window_center_origin(profile: GameProfile, size: Size) -> Coordinate:
  return Coordinate(profile.window_size.width/2-size.width/2, profile.window_size.height/2-size.height/2)


def draw_copyright(profile: GameProfile, field: Field, transparent_color: int) -> None:
  copyright_text = Text('© {} {}'.format(GAME_RELEASE_YEAR, profile.copyright), pyxel.COLOR_WHITE)
  copyright_text.origin = Coordinate(
    window_center_origin(profile, Size(copyright_text.length, copyright_text.text_size())).x,
    field.ground_top-copyright_text.text_size()*5,
  )
  copyright_text.draw(transparent_color)


def draw_score(profile: GameProfile, stage: int, level: int, score: Score, transparent_color: int) -> None:
  stage_text = Text('STAGE.{:02}'.format(stage+1), pyxel.COLOR_WHITE)
  stage_text.origin = Coordinate(stage_text.text_size(), stage_text.text_size())
  stage_text.draw(transparent_color)

  score_text = Text(
    '{}:{:04}'.format(JUMPER[level], score.point),
    pyxel.COLOR_WHITE,
  )
  score_text.origin = Coordinate(profile.window_size.width-score_text.length-score_text.text_size(), score_text.text_size())
  score_text.draw(transparent_color)


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
    self.jumper_wait_timer = Timer.set_sec(self.stopwatch, self.JUMPER_WAIT_SEC, True)

    self.title_wait_timer = Timer.set_sec(self.stopwatch, self.TITLE_WAIT_SEC)
    self.title_timer = Timer.set_sec(self.stopwatch, self.TITLE_SEC)

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      return TitleScene(self)

    if self.jumper_wait_timer.over():
      if not self.title_timer.counting():
        if not self.title_wait_timer.counting():
          self.snapshot.jumper.walk(
            self.snapshot.field.right-JUMPER_START_X,
          )

          self.title_wait_timer.resume()
        else:
          if self.title_wait_timer.over():
            self.title_timer.resume()
      else:
        if self.title_timer.over():
          return TitleScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    if self.title_timer.counting():
      title_text = Text(self.profile.title, pyxel.COLOR_WHITE)
      title_text.origin = Coordinate(
        window_center_origin(self.profile, Size(title_text.length, title_text.text_size())).x,
        title_text.text_size()*3,
      )
      title_text.draw(transparent_color)

      draw_copyright(self.profile, self.snapshot.field, transparent_color)


class TitleScene(Scene):
  START_PULSE_SEC = 1
  START_SEC = 1

  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

    pyxel.title(GAME_TITLE[self.snapshot.level])

    self.snapshot.jumper.stop()
    self.snapshot.jumper.origin = Coordinate(
      self.snapshot.field.right-JUMPER_START_X,
      self.snapshot.jumper.origin.y,
    )

    self.show_start = True
    self.start_pulse_timer = Timer.set_sec(self.stopwatch, self.START_PULSE_SEC, True)

    self.start_timer = Timer.set_sec(self.stopwatch, self.START_SEC)

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      self.start_timer.resume()

    if not self.start_timer.counting():
      if self.start_pulse_timer.over():
        self.show_start = not self.show_start
        self.start_pulse_timer.reset()
    else:
      self.show_start = True
      if self.start_timer.over():
        return GameStartScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    title_text = Text(self.profile.title, pyxel.COLOR_WHITE)
    title_text.origin = Coordinate(
      window_center_origin(self.profile, Size(title_text.length, title_text.text_size())).x,
      title_text.text_size()*3,
    )
    title_text.draw(transparent_color)

    if self.show_start:
      start_text = Text('CLICK START', pyxel.COLOR_WHITE)
      start_text.origin = Coordinate(
        window_center_origin(self.profile, Size(start_text.length, start_text.text_size())).x,
        window_center_origin(self.profile, Size(start_text.length, start_text.text_size())).y-start_text.text_size(),
      )
      start_text.draw(transparent_color)

    draw_copyright(self.profile, self.snapshot.field, transparent_color)


class GameStartScene(Scene):
  START_WAIT_SEC = 1
  START_SEC = 3
  STAGE_LIMIT_SEC: dict[int, dict[int, int]] = {
    GameLevel.BOY: {
      BoyStage.STAGE_1: 30,
    },
  }

  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

    pyxel.title(GAME_TITLE[self.snapshot.level])

    self.start_wait_timer = Timer.set_sec(self.stopwatch, self.START_WAIT_SEC, True)
    self.start_timer = Timer.set_sec(self.stopwatch, self.START_SEC)

  def update(self) -> Self | Any:
    if self.start_wait_timer.over():
      if not self.start_timer.counting():
        self.start_timer.resume()

    if self.start_timer.over():
      for ball in self.snapshot.balls:
        ball.roll()
      self.snapshot.jumper.standby()
      self.snapshot.playing_timer = Timer.set_sec(
        self.stopwatch,
        self.STAGE_LIMIT_SEC[self.snapshot.level][self.snapshot.stage],
      )
      return GamePlayScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    draw_score(self.profile, self.snapshot.stage, self.snapshot.level, self.snapshot.score, transparent_color)

    if self.start_timer.counting():
      sec = self.start_timer.sec if self.start_timer.sec is not None else 0
      wait_sec = max(self.START_SEC-sec, 1)
      wait_sec = min(wait_sec, self.START_SEC)
      start_wait_time_text = Text(str(wait_sec), pyxel.COLOR_WHITE)
      start_wait_time_text.origin = Coordinate(
        window_center_origin(
          self.profile,
          Size(start_wait_time_text.length, start_wait_time_text.text_size()),
        ).x,
        window_center_origin(
          self.profile,
          Size(start_wait_time_text.length, start_wait_time_text.text_size()),
        ).y-start_wait_time_text.text_size()*4,
      )
      start_wait_time_text.draw(transparent_color)


class GamePlayScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)
    
    self.resume_play()

  def resume_play(self) -> None:
    if self.snapshot.playing_timer is not None:
      self.snapshot.playing_timer.resume()

  def pause_play(self) -> None:
    if self.snapshot.playing_timer is not None:
      self.snapshot.playing_timer.pause()

  def over_play(self) -> bool:
    if self.snapshot.playing_timer is not None:
      return self.snapshot.playing_timer.over()

    return False

  def playing_msec(self) -> int:
    if self.snapshot.playing_timer is not None and self.snapshot.playing_timer.msec is not None:
      return self.snapshot.playing_timer.msec

    return 0

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.cancel():
      self.pause_play()
      return GamePauseScene(self)

    for ball in self.snapshot.balls:
      if ball.hit(self.snapshot.jumper):
        self.pause_play()

        self.snapshot.jumper.down()

        self.snapshot.jumper.stop()
        for ball in self.snapshot.balls:
          ball.stop()
        return GameOverScene(self)

    if self.over_play():
      self.pause_play()

      self.snapshot.jumper.stop()

      for ball in self.snapshot.balls:
        ball.stop()
      return GameStageClearScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)

    draw_score(self.profile, self.snapshot.stage, self.snapshot.level, self.snapshot.score, transparent_color)

    playing_time_text = Text(
      '{:02}:{:02}.{:03}'.format(
        int(self.playing_msec()/1000/60),
        int(self.playing_msec()/1000%60),
        self.playing_msec()%1000
      ),
      pyxel.COLOR_WHITE,
    )
    playing_time_text.origin = Coordinate(
      window_center_origin(self.profile, Size(playing_time_text.length, playing_time_text.text_size())).x,
      playing_time_text.text_size(),
    )
    playing_time_text.draw(transparent_color)


class GamePauseScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter():
      return GamePlayScene(self)

    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class GameOverScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

  def update(self) -> Self | Any:
    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)


class GameStageClearScene(Scene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(scene.profile, scene.stopwatch, scene.snapshot)

  def update(self) -> Self | Any:
    return super().update()

  def draw(self, transparent_color: int) -> None:
    super().draw(transparent_color)
