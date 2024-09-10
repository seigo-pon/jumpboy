from core import (
  Size, Path,
  Language, StringRes,
  GameConfig,
  GameEngine,
)
from scene import OpeningScene
import pyxel


DEBUG = False
COPYRIGHT = 'SEIGO-PON'
RELEASED_YEAR = 2024
GAME_WINDOW_SIZE = Size(160, 120)
FPS = 30
ASSET_FOLDER = 'assets'
ASSET_FILE = 'jumpboy.pyxres'
TRANSPARENT_COLOR = pyxel.COLOR_BLACK


class App:
  def __init__(self) -> None:
    path = Path(__file__, ASSET_FOLDER)
    string_res = StringRes(path)
    config = GameConfig(
      path=path,
      title=string_res.string('game_title_1', Language.EN),
      window_size=GAME_WINDOW_SIZE,
      fps=FPS,
      copyright=COPYRIGHT,
      released_year=RELEASED_YEAR,
      debug=DEBUG,
    )

    self.engine = GameEngine(
      config=config,
      quit_key=pyxel.KEY_Q,
      asset_file=ASSET_FILE,
      update=self.update,
      draw=self.draw,
    )
    self.scene = OpeningScene(config, string_res)
    self.engine.run()

  def update(self) -> None:
    self.scene = self.scene.update()

  def draw(self) -> None:
    self.scene.draw(TRANSPARENT_COLOR)


# start game
App()
