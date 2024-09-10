from typing import Callable
from core import GameConfig
import os
import pyxel


class GameEngine:
  def __init__(
    self,
    config: GameConfig,
    quit_key: int,
    asset_file: str,
    update: Callable[[], None],
    draw: Callable[[], None]
  ) -> None:
    print('engine', vars(config), quit_key, asset_file)
    self.update = update
    self.draw = draw

    pyxel.init(
      width=int(config.window_size.width),
      height=int(config.window_size.height),
      title=config.title,
      fps=config.fps,
      quit_key=quit_key,
    )
    pyxel.load(os.path.join(config.path.asset_path, asset_file))

  def run(self) -> None:
    pyxel.run(self.update, self.draw)
