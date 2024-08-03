from game import Size, GameProfile, GameEngine
from component import GameLevel
from script import GAME_TITLE, OpeningScene
import os
import pyxel


class App:
  GAME_WINDOW_SIZE = Size(160, 120)
  FPS = 30
  COPYRIGHT = 'SEIGO-PON'
  ASSET_FOLDER = 'assets'
  ASSET_FILES = ['jumpboy.pyxres']

  def __init__(self) -> None:
    profile = GameProfile(GAME_TITLE[GameLevel.BOY], self.GAME_WINDOW_SIZE, self.FPS, self.COPYRIGHT)

    self.engine = GameEngine(
      profile=profile,
      quit_key=pyxel.KEY_Q,
      asset_filenames=[
        os.path.join(GameEngine.path(__file__, self.ASSET_FOLDER), asset_file) for asset_file in self.ASSET_FILES
      ],
      update=self.update,
      draw=self.draw,
      transparent_color=pyxel.COLOR_BLACK,
    )

    self.scene = OpeningScene(profile)

    self.engine.start()

  def update(self) -> None:
    self.scene = self.scene.update()

  def draw(self) -> None:
    self.scene.draw(self.engine.transparent_color)


App()
