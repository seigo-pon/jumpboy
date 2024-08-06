from game import (
  Size, Path,
  GameProfile, Language, StringRes,
  GameEngine,
)
from script import Strings, OpeningScene
import os
import pyxel


DEBUG = True


class App:
  GAME_WINDOW_SIZE = Size(160, 120)
  FPS = 30
  COPYRIGHT = 'SEIGO-PON'
  RELEASE_YEAR = 2024
  ASSET_FOLDER = 'assets'
  ASSET_FILES = ['jumpboy.pyxres']

  def __init__(self) -> None:
    string_res = StringRes(__file__, self.ASSET_FOLDER)
    profile = GameProfile(
      string_res.string(Strings.TITLE_BOY, Language.EN),
      self.GAME_WINDOW_SIZE,
      self.FPS,
      self.COPYRIGHT,
      self.RELEASE_YEAR,
      DEBUG,
    )
    asset_paths = []
    for asset_file in self.ASSET_FILES:
      asset_paths.append(os.path.join(os.path.join(Path.root(__file__), self.ASSET_FOLDER), asset_file))

    self.engine = GameEngine(
      profile=profile,
      quit_key=pyxel.KEY_Q,
      asset_paths=asset_paths,
      update=self.update,
      draw=self.draw,
      transparent_color=pyxel.COLOR_BLACK,
    )

    self.scene = OpeningScene(profile, string_res)

    self.engine.run()

  def update(self) -> None:
    self.scene = self.scene.update()

  def draw(self) -> None:
    self.scene.draw(self.engine.transparent_color)


App()
