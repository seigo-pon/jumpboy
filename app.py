from game import (
  Size, Path,
  GameProfile, Language, StringResource,
  GameEngine,
)
from script import GameStrings, OpeningScene
import os
import pyxel


class App:
  GAME_WINDOW_SIZE = Size(160, 120)
  FPS = 30
  COPYRIGHT = 'SEIGO-PON'
  ASSET_FOLDER = 'assets'
  ASSET_FILES = ['jumpboy.pyxres']

  def __init__(self) -> None:
    string_res = StringResource(__file__, self.ASSET_FOLDER)
    profile = GameProfile(
      string_res.string(GameStrings.TITLE_BOY, Language.EN),
      self.GAME_WINDOW_SIZE,
      self.FPS,
      self.COPYRIGHT,
    )

    self.engine = GameEngine(
      profile=profile,
      string_res=string_res,
      quit_key=pyxel.KEY_Q,
      asset_filenames=[
        os.path.join(os.path.join(Path.root(__file__), self.ASSET_FOLDER), asset_file) for asset_file in self.ASSET_FILES
      ],
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
