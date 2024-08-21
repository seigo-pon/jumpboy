from typing import Callable
from game import GameConfig
import os
import pyxel


class GameEngine:
  def __init__(
    self,
    config: GameConfig,
    quit_key: int,
    asset_files: list[str],
    update: Callable[[], None],
    draw: Callable[[], None]
  ) -> None:
    print('engine', vars(config), quit_key, asset_files)
    self.update = update
    self.draw = draw

    pyxel.init(
      int(config.window_size.width),
      int(config.window_size.height),
      title=config.title,
      fps=config.fps,
      quit_key=quit_key,
    )
    for asset_file in asset_files:
      pyxel.load(os.path.join(config.path.asset_path, asset_file))

  def run(self) -> None:
    pyxel.run(self.update, self.draw)
