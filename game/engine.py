from typing import Callable
from game import GameConfig
import pyxel


class GameEngine:
  def __init__(
    self,
    config: GameConfig,
    quit_key: int,
    asset_paths: list[str],
    update: Callable[[], None],
    draw: Callable[[], None]
  ) -> None:
    print('engine', vars(config), quit_key, asset_paths)
    self.update = update
    self.draw = draw

    pyxel.init(
      int(config.window_size.width),
      int(config.window_size.height),
      title=config.title,
      fps=config.fps,
      quit_key=quit_key,
    )
    for asset_path in asset_paths:
      pyxel.load(asset_path)

  def run(self) -> None:
    pyxel.run(self.update, self.draw)
