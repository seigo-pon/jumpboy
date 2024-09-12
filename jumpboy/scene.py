from datetime import datetime
from enum import IntEnum
from typing import Any, Self
from core import (
  Coordinate, Size, Stopwatch, Timer,
  Language, StringRes, Image, AssetSound, RawBgm,
  Typewriter, Text, BlinkText,
  Poster, Signboard,
  GameConfig, Seq, TimeSeq, MusicBox,
)
from component import (
  GamePad,
  GameLevel, Score, ScoreBoard,
  Ball, Jumper,
  Snapshot, Scene,
)
from design import (
  ImageId, SoundId,
  GameLevelMode, GameLevelStage,
  GameDesign,
)
import pyxel


TEXT_FONT_SIZE = 10
TEXT_COLOR = pyxel.COLOR_WHITE

GAME_TITLE: dict[int, str] = {
  GameLevelMode.NORMAL: 'game_title_1',
  GameLevelMode.HARD: 'game_title_2',
}
SCORE: dict[int, str] = {
  GameLevelMode.NORMAL: 'score_title_1',
  GameLevelMode.HARD: 'score_title_2',
}

JUMPER_START_X = Image.basic_size().width*5

SCORE_RANKING_NUM = 3

BGM_FOLDER = 'bgm'
BGM_EXCLUDE_PLAY_CHANNEL = [AssetSound.channel_count()-1]

class SceneSound:
  READY = SoundId.SCENE+0
  PAUSE = SoundId.SCENE+1
  TIME_UP = SoundId.SCENE+2
  GAME_OVER = SoundId.SCENE+3
  STAGE_CLEAR = SoundId.SCENE+4
  SELECT = SoundId.SCENE+5
  RESTART = SoundId.SCENE+6
  START = SoundId.SCENE+7
  RECOVER_LIFE = SoundId.SCENE+8
  TITLE = SoundId.SCENE+9

TITLE_BGM: dict[int, str] = {
  GameLevelMode.NORMAL: 'title1',
  GameLevelMode.HARD: 'title2',
}
FIELD_BGM: dict[int, str] = {
  GameDesign.FieldSurface.ROAD: 'field1',
  GameDesign.FieldSurface.GRASS: 'field2',
  GameDesign.FieldSurface.CLAY: 'field3',
  GameDesign.FieldSurface.WOOD: 'field4',
}
END_BGM: dict[int, str] = {
  GameLevelMode.NORMAL: 'end1',
  GameLevelMode.HARD: 'end2',
}


class BaseScene(Scene):
  def __init__(
    self,
    config: GameConfig,
    string_res: StringRes,
    stopwatch: Stopwatch,
    typewriter: Typewriter,
    snapshot: Snapshot,
  ) -> None:
    super().__init__(
      config=config,
      string_res=string_res,
      stopwatch=stopwatch,
      typewriter=typewriter,
      snapshot=snapshot,
    )

  def menu_left_top_origin(self) -> Coordinate:
    return Coordinate(0, 0)

  def menu_middle_top_center(self, size: Size | None) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      (size.height
       if size is not None else
       Typewriter.word_size(TEXT_FONT_SIZE).height)/2,
    )

  def menu_right_top_origin(self, size: Size) -> Coordinate:
    return Coordinate(self.config.window_size.width-size.width, 0)

  def title_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      Typewriter.word_size(TEXT_FONT_SIZE).height*2
      +Typewriter.word_size(TEXT_FONT_SIZE).height/2,
    )

  def subtitle_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      Typewriter.word_size(TEXT_FONT_SIZE).height*3
      +Typewriter.word_size(TEXT_FONT_SIZE).height/2,
    )

  def menu_middle_center(self) -> Coordinate:
    return self.config.window_size.center

  def menu_middle_low_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      self.config.window_size.center.y
      +Typewriter.word_size(TEXT_FONT_SIZE).height*3,
    )

  def menu_middle_bottom_center(self) -> Coordinate:
    return Coordinate(
      self.config.window_size.center.x,
      self.snapshot.field.ground_height
      -Typewriter.word_size(TEXT_FONT_SIZE).height*2
      +Typewriter.word_size(TEXT_FONT_SIZE).height/2,
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
    return self.snapshot.field.right-JUMPER_START_X

  def text(self, string: str) -> Text:
    return Text(
      typewriter=self.typewriter,
      string=string,
      text_color=TEXT_COLOR,
      font_size=TEXT_FONT_SIZE,
      bold=False,
    )

  def blink_text(self, string: str, blink_msec: int, show: bool) -> BlinkText:
    return BlinkText(
      typewriter=self.typewriter,
      string=string,
      text_color=TEXT_COLOR,
      font_size=TEXT_FONT_SIZE,
      bold=False,
      stopwatch=self.stopwatch,
      blink_msec=blink_msec,
      show=show,
    )

  def initial_sprites(self, reset: bool) -> None:
    self.snapshot.field = GameDesign.field(self.snapshot.level, self.config)
    print('field', self.snapshot.field.id)

    self.snapshot.balls = []

    life = self.snapshot.jumper.life
    self.snapshot.jumper = GameDesign.jumper(self.snapshot.level, self.stopwatch)
    if not reset:
      self.snapshot.jumper.life = life

    print('jumper', self.snapshot.jumper.id)
    self.snapshot.jumper.origin = self.jumper_ready_origin(self.snapshot.jumper)

  def to_next_level(cls, level: GameLevel) -> GameLevel | None:
    stages = [e for e in GameLevelStage]
    for (index, stage) in enumerate(stages):
      if stage == level.stage:
        index += 1
        if index < len(stages):
          next_stage = stages[index]
          print('next stage', next_stage)
          return GameLevel(level.mode, next_stage)

    levels = [e for e in GameLevelMode]
    for (index, mode) in enumerate(levels):
      if mode == level.mode:
        index += 1
        if index < len(levels):
          next_level = levels[index]
          print('next stage', next_level)
          return GameLevel(next_level, GameLevelStage.STAGE_1)

    print('next level none')
    return None

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects: list[Any] = [self.snapshot.field]
    subjects += [ball for ball in self.snapshot.balls]
    subjects.append(self.snapshot.jumper)

    if self.config.debug:
      stopwatch_text = Text(
        typewriter=self.typewriter,
        string='{:02}:{:02}:{:02}:{:03}'.format(
          int(self.stopwatch.sec/60/60),
          int(self.stopwatch.sec/60%60),
          int(self.stopwatch.sec%60),
          self.stopwatch.msec%1000,
        ),
        text_color=pyxel.COLOR_BLACK,
        font_size=10,
        bold=False,
      )
      stopwatch_text.origin = Coordinate(
        self.config.window_size.width-stopwatch_text.size.width,
        self.config.window_size.height-stopwatch_text.size.height,
      )
      subjects.append(stopwatch_text)

    return subjects


class OpeningScene(BaseScene):
  def __init__(self, config: GameConfig, string_res: StringRes) -> None:
    stopwatch = Stopwatch(config.fps)
    level = GameDesign.first_level(config)

    super().__init__(
      config=config,
      string_res=string_res,
      stopwatch=stopwatch,
      typewriter=Typewriter(config.path),
      snapshot=Snapshot(
        lang=Language.EN,
        game_pad=GamePad(),
        music_box=MusicBox(
          bgm_param=None,
          raw_bgm_param=RawBgm.Param(
            path=config.path,
            folder=BGM_FOLDER,
            start_id=SoundId.BGM,
            exclude_play_channels=BGM_EXCLUDE_PLAY_CHANNEL,
          ),
        ),
        score_board=ScoreBoard(),
        level=level,
        field=GameDesign.field(level, config),
        balls=[],
        jumper=GameDesign.jumper(level, stopwatch),
      ),
    )

    self.snapshot.load(self.config.path)
    self.config.title = self.string(GAME_TITLE[self.snapshot.level.mode])
    print('snapshot', vars(self.snapshot), vars(self.snapshot.level))

    self.title_text: Text | None = None
    self.play_title = False

    self.initial_sprites(True)

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
          -Typewriter.word_size(TEXT_FONT_SIZE).height,
        )
        self.title_text.move(center=self.title_center(), move_distance=0.5)
        self.snapshot.music_box.play_raw_bgm(TITLE_BGM[self.snapshot.level.mode])
      else:
        if not self.title_text.moving:
          return True

      return False

    def _play_title(start: bool, timer: Timer) -> bool:
      self.play_title = True
      self.snapshot.music_box.play_se(SceneSound.TITLE)
      return True

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 500, _walk_jumper, None),
      Seq(self.stopwatch, 2000, _move_title, None),
      Seq(self.stopwatch, 500, _play_title, None),
      Seq(self.stopwatch, 500, lambda x, y: True, lambda: TitleScene(self)),
    ])

  @property
  def updating_variations(self) -> list[Any]:
    variations = super().updating_variations

    if self.title_text is not None:
      variations.append(self.title_text)

    return variations

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter(False):
      if not self.play_title:
        self.snapshot.music_box.play_se(SceneSound.TITLE)
      return TitleScene(self)

    return super().update()

  @property
  def drawing_subjects(self) -> list[Any]:
    subjects = super().drawing_subjects

    if self.title_text is not None:
      subjects.append(self.title_text)

    return subjects


class TitleScene(BaseScene):
  def __init__(self, scene: Scene) -> None:
    super().__init__(
      config=scene.config,
      string_res=scene.string_res,
      stopwatch=scene.stopwatch,
      typewriter=scene.typewriter,
      snapshot=scene.snapshot,
    )

    self.title_text = self.text(self.config.title)
    self.title_text.center = self.title_center()

    self.show_start = True
    self.start_text = self.blink_text(self.string('game_start_text'), 1000, True)
    self.start_text.center = self.menu_middle_center()
    self.start_text.resume()
    self.wait_start = False

    self.show_score = False
    self.score = self.scoreboard()
    self.score.center = Coordinate(self.menu_middle_top_center(None).x, -self.score.size.height/2)

    self.snapshot.music_box.play_raw_bgm(TITLE_BGM[self.snapshot.level.mode])

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
          center=self.menu_middle_top_center(
            Size(
              self.score.size.width,
              self.score.size.height+Typewriter.word_size(TEXT_FONT_SIZE).height*2,
            )
          ),
          move_distance=0.5,
        )
        self.show_start = False
      else:
        if not self.score.moving:
          self.show_start = True
          self.start_text.center = Coordinate(
            self.menu_middle_low_center().x,
            self.menu_middle_low_center().y-Typewriter.word_size(TEXT_FONT_SIZE).height,
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

    score_center.y += Typewriter.word_size(title_text.font_size).height*2
    scores = self.snapshot.score_board.ranking(SCORE_RANKING_NUM)
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
        score_center.y += Typewriter.word_size(score_text.font_size).height
    else:
      no_score_text = self.text(self.string('score_no_text'))
      no_score_text.center = Coordinate(score_center.x, score_center.y)
      score_texts.append(no_score_text)

    return Signboard(
      posters=[],
      texts=score_texts,
      width=self.config.window_size.width,
      height=None,
    )

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
        self.start_text.update_blink_msec(120, True)
        self.time_seq = TimeSeq([
          Seq(self.stopwatch, 1000, lambda x, y: True, lambda: ReadyScene(self, 0, None)),
        ])
        self.snapshot.music_box.play_se(SceneSound.SELECT)
        self.snapshot.music_box.stop_bgm()

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
      config=scene.config,
      string_res=scene.string_res,
      stopwatch=scene.stopwatch,
      typewriter=scene.typewriter,
      snapshot=scene.snapshot,
    )

    self.point = point
    self.play_timer = play_timer

    self.show_stage = True

  def record_score(self) -> None:
    self.snapshot.score_board.scores.append(
      Score(
        created_at=datetime.now(),
        level=self.snapshot.level,
        point=self.point,
      )
    )
    print('score record', vars(self.snapshot.score_board.scores[-1]))

  def life_gauge(self) -> Signboard:
    return Signboard(
      posters=[
        Poster(
          image=Image(
            ImageId.LIFE.id,
            Coordinate(
              ImageId.LIFE.x,
              0 if ((self.snapshot.jumper.param.max_life-1)-index) < self.snapshot.jumper.life else 1,
            ),
            Size(1, 1),
            Image.Pose.NORMAL,
          ),
          origin=Coordinate(Image.basic_size().width*index, 0)
        )
        for index in range(self.snapshot.jumper.param.max_life)
      ],
      texts=[],
      width=None,
      height=None,
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

    self.snapshot.music_box.stop_bgm()

    print('ready', vars(self.snapshot.level))
    self.play_timer = Timer.set_msec(
      stopwatch=self.stopwatch,
      msec=GameDesign.play_limit_msec(self.snapshot.level),
      start=False,
    )

    self.snapshot.jumper.stop()

    self.max_add_life = 0
    if self.snapshot.jumper.life < self.snapshot.jumper.param.max_life:
      self.max_add_life = GameDesign.recovery_life_count(self.snapshot.level)
      self.max_add_life = min(self.max_add_life, self.snapshot.jumper.param.max_life-self.snapshot.jumper.life)
    print('recovery life', self.max_add_life, self.snapshot.jumper.life, self.snapshot.jumper.param.max_life)
    self.add_life = 0

    self.show_stage = False

    self.describe: int | None = None
    self.ready_timer: Timer | None = None
    self.last_sec = -1

    def _walk_jumper(start: bool, timer: Timer) -> bool:
      if start:
        self.snapshot.jumper.walk(self.jumper_start_x())
      else:
        if not self.snapshot.jumper.walking:
          return True

      return False

    def _recovery_life(start: bool, timer: Timer) -> bool:
      if start:
        if self.max_add_life == 0:
          return True
      else:
        if self.add_life == self.max_add_life:
          return True

        self.snapshot.jumper.life += 1
        self.add_life += 1
        self.snapshot.music_box.play_se(SceneSound.RECOVER_LIFE)

      timer.limit_msec = 1000
      timer.reset()

      return False

    def _ready_describe(start: bool, timer: Timer) -> bool:
      if self.describe is None:
        self.describe = [e for e in self.Describe][0]
        self.snapshot.music_box.play_se(SceneSound.START)
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
          self.snapshot.jumper.stand_by()
          return True
        else:
          last_sec = int(self.ready_timer.msec/1000)
          if self.last_sec != last_sec:
            self.snapshot.music_box.play_se(SceneSound.READY)
            self.last_sec = last_sec

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 0, _walk_jumper, None),
      Seq(self.stopwatch, 0, _recovery_life, None),
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

    for ball in self.snapshot.balls:
      ball.resume()
    self.snapshot.jumper.resume()

    if self.play_timer is not None:
      self.play_timer.resume()

    self.snapshot.music_box.play_raw_bgm(FIELD_BGM[self.snapshot.field.surface])

  def update(self) -> Self | Any:
    if self.play_timer is not None:
      if self.snapshot.game_pad.cancel():
        self.snapshot.music_box.play_se(SceneSound.PAUSE)
        return PauseScene(self, self.point, self.play_timer)

      next_balls: list[Ball] = []
      for ball in [ball for ball in self.snapshot.balls]:
        if ball.dead:
          print('ball dead', ball.id)
          continue

        if ball.spin_direction:
          if ball.left >= self.snapshot.field.right:
            print('ball over left', ball.id, ball.left, self.snapshot.field.right)
            self.point += ball.point
            continue
        else:
          if ball.right <= self.snapshot.field.left:
            print('ball over right', ball.id, ball.right, self.snapshot.field.left)
            self.point += ball.point
            continue

        next_balls.append(ball)

        if not self.snapshot.jumper.damaging:
          if ball.spinning:
            if ball.hit(self.snapshot.jumper):
              attack = False
              if self.snapshot.jumper.jumping(up=False):
                if ball.top <= self.snapshot.jumper.bottom <= ball.bottom:
                  if ball.left <= self.snapshot.jumper.center.x <= ball.right:
                    print('attack y', ball.top, self.snapshot.jumper.bottom, ball.bottom)
                    print('attack x', ball.left, self.snapshot.jumper.center.x, ball.right)
                    attack = True

              if attack:
                ball.burst()
                self.point += ball.point
              else:
                ball.through()
                self.snapshot.jumper.damage()

          if not self.snapshot.jumper.falling_down:
            if ball.bounced:
              print('ball bounced', ball.id)
              self.point += ball.point

      self.snapshot.balls = next_balls

      if self.snapshot.jumper.falling_down:
        return GameOverScene(self, self.point, self.play_timer)

      if self.play_timer.over:
        self.snapshot.music_box.play_se(SceneSound.TIME_UP)
        return StageClearScene(self, self.point, self.play_timer)

      stopped = False
      if len(self.snapshot.balls) > 0:
        last_ball: Ball | None = None
        balls = sorted([ball for ball in self.snapshot.balls], key=lambda x: x.elapsed_msec, reverse=True)
        for ball in balls:
          if ball.stopping:
            if GameDesign.can_spin_ball(self.snapshot.level, self.snapshot.field, ball, last_ball):
              ball.spin()
            else:
              stopped = True
          else:
            last_ball = ball

      if not stopped:
        next_msec = GameDesign.next_ball_msec(self.snapshot.level, self.snapshot.balls)
        if next_msec is not  None:
          stopping_ball = GameDesign.ball(self.snapshot.level, self.stopwatch)
          stopping_ball.origin = self.ball_ready_origin(stopping_ball)
          stopping_ball.spin_after_msec(self.stopwatch, next_msec)
          self.snapshot.balls.append(stopping_ball)

    return super().update()


class PauseScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(scene, point, play_timer)

    if self.play_timer is not None:
      self.play_timer.pause()
    for ball in self.snapshot.balls:
      ball.pause()
    self.snapshot.jumper.pause()

    self.pause_text = self.blink_text(self.string('game_pause_text'), 1000, True)
    self.pause_text.resume()

  @property
  def updating_variations(self) -> list[Any]:
    return [self.pause_text]

  def update(self) -> Self | Any:
    if self.snapshot.game_pad.enter(False) or self.snapshot.game_pad.cancel():
      self.snapshot.music_box.play_se(SceneSound.RESTART)
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

    self.snapshot.music_box.stop_bgm()

    if self.play_timer is not None:
      self.play_timer.pause()

    for ball in self.snapshot.balls:
      ball.stop()

    self.record_score()
    self.snapshot.save(self.config.path)

    self.show_game_over = False
    self.show_game_end = False

    self.restart_text = self.blink_text(self.string('game_restart_text'), 1000, False)

    def _show_game_over(start: bool, timer: Timer) -> bool:
      self.show_game_over = True
      self.snapshot.music_box.play_se(SceneSound.GAME_OVER)
      return True

    def _show_game_end(start: bool, timer: Timer) -> bool:
      self.show_game_end = True
      self.restart_text.resume()
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
        self.snapshot.level = GameDesign.first_level(self.config)
        self.initial_sprites(True)
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

    self.snapshot.music_box.stop_bgm()

    if self.play_timer is not None:
      self.play_timer.pause()

    for ball in self.snapshot.balls:
      ball.stop()
    self.snapshot.jumper.stop()

    self.next_level: GameLevel | None = self.snapshot.level
    self.same_surface = False

    self.show_clear = False
    self.show_next = False
    self.walked_jumper = False

    def _wait_jumper(start: bool, timer: Timer) -> bool:
      if not self.snapshot.jumper.jumping(None):
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
      self.snapshot.music_box.play_se(SceneSound.STAGE_CLEAR)
      return True

    def _show_next(start: bool, timer: Timer) -> bool:
      if start:
        self.show_next = True
        if self.next_level is not None:
          if not self.same_surface:
            self.snapshot.jumper.walk(self.snapshot.field.left-self.snapshot.jumper.size.width)
      else:
        if not self.snapshot.jumper.walking:
          if not self.same_surface and not self.walked_jumper:
            timer.limit_msec = 3000
            timer.reset()
            self.walked_jumper = True
          return True

      return False

    self.time_seq = TimeSeq([
      Seq(self.stopwatch, 0, _wait_jumper, None),
      Seq(self.stopwatch, 1000, _show_clear, None),
      Seq(self.stopwatch, 2000, _show_next, None),
    ])

  def update(self) -> Self | Any:
    if self.next_level is None:
      return GameClearScene(self, self.point, self.play_timer)

    if self.time_seq.ended or (self.show_next and self.snapshot.game_pad.enter(True)):
      self.snapshot.level = self.next_level

      self.initial_sprites(False)
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

    if self.show_next and not self.same_surface:
      next_text = self.text(self.string('stage_clear_text'))
      next_text.center = self.menu_middle_center()
      subjects.append(next_text)

    return subjects


class GameClearScene(BaseStageScene):
  def __init__(self, scene: Scene, point: int, play_timer: Timer | None) -> None:
    super().__init__(scene, point, play_timer)

    self.snapshot.music_box.stop_bgm()

    self.record_score()
    self.snapshot.save(self.config.path)

    self.next_level = self.to_next_level(self.snapshot.level)

    self.show_clear = False
    self.show_thanks = False
    self.show_bye = False

    def _show_clear(start: bool, timer: Timer) -> bool:
      self.show_clear = True
      self.snapshot.jumper.joy()
      self.snapshot.music_box.play_raw_bgm(END_BGM[self.snapshot.level.mode])
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
        self.snapshot.level = GameDesign.first_level(self.config)
      self.initial_sprites(True)
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
