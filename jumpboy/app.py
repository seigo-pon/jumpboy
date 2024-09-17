from datetime import datetime
from core import (
  Size, Path,
  Language, StringRes,
  GameConfig,
  GameEngine,
)
try:
  from env import (
    DEBUG as ENV_DEBUG,
    COPYRIGHT as ENV_COPYRIGHT,
    RELEASED_YEAR as ENV_RELEASED_YEAR,
  )
except:
  pass
from scene import OpeningScene
import pyxel


DEBUG = ENV_DEBUG if ENV_DEBUG is not None else False
COPYRIGHT = ENV_COPYRIGHT if ENV_COPYRIGHT is not None else 'ANONYMOUS'
RELEASED_YEAR = ENV_RELEASED_YEAR if ENV_RELEASED_YEAR is not None else datetime.now().year

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
