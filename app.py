from game import (
  Size, Path,
  GameProfile, Language, StringRes,
  GameEngine,
)
from script import OpeningScene
import os
import pyxel


DEBUG = True

GAME_WINDOW_SIZE = Size(160, 120)
FPS = 30
COPYRIGHT = 'SEIGO-PON'
RELEASE_YEAR = 2024
ASSET_FOLDER = 'assets'
ASSET_FILES = ['jumpboy.pyxres']


class App:
  def __init__(self) -> None:
    path = Path(__file__)
    string_res = StringRes(path, ASSET_FOLDER)

    profile = GameProfile(
      path,
      string_res.string('TITLE_BOY', Language.EN),
      GAME_WINDOW_SIZE,
      FPS,
      COPYRIGHT,
      RELEASE_YEAR,
      DEBUG,
    )

    asset_paths = []
    for asset_file in ASSET_FILES:
      asset_paths.append(os.path.join(os.path.join(profile.path.root, ASSET_FOLDER), asset_file))

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
