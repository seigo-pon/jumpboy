from datetime import datetime
from dotenv import load_dotenv
from game import (
  Size, Path,
  GameConfig, Language, StringRes,
  GameEngine,
)
from script import OpeningScene
import os
import pyxel


load_dotenv()


DEBUG = bool(os.getenv('DEBUG') == 'True')
COPYRIGHT = str(os.getenv('COPYRIGHT') or 'ANONYMOUS')
RELEASED_YEAR = int(os.getenv('RELEASED_YEAR') or datetime.now().year)

GAME_WINDOW_SIZE = Size(160, 120)
FPS = 30
ASSET_FOLDER = 'assets'
ASSET_FILES = ['jumpboy.pyxres']


class App:
  def __init__(self) -> None:
    path = Path(__file__, ASSET_FOLDER)
    string_res = StringRes(path)
    config = GameConfig(
      path,
      string_res.string('TITLE_BOY', Language.EN),
      GAME_WINDOW_SIZE,
      FPS,
      pyxel.COLOR_BLACK,
      COPYRIGHT,
      RELEASED_YEAR,
      DEBUG,
    )
    asset_paths = []
    for asset_file in ASSET_FILES:
      asset_paths.append(os.path.join(config.path.asset_path, asset_file))

    self.engine = GameEngine(
      config=config,
      quit_key=pyxel.KEY_Q,
      asset_paths=asset_paths,
      update=self.update,
      draw=self.draw,
    )

    self.scene = OpeningScene(config, string_res)

    self.engine.run()

  def update(self) -> None:
    self.scene = self.scene.update()

  def draw(self) -> None:
    self.scene.draw()


App()
