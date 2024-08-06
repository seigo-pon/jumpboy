from typing import Callable
from game import GameProfile, StringRes
import pyxel


class GameEngine:
  def __init__(
    self,
    profile: GameProfile,
    quit_key: int,
    asset_paths: list[str],
    update: Callable[[], None],
    draw: Callable[[], None],
    transparent_color: int,
  ) -> None:
    self.update = update
    self.draw = draw
    self.transparent_color = transparent_color

    pyxel.init(
      profile.window_size.width,
      profile.window_size.height,
      title=profile.title,
      fps=profile.fps,
      quit_key=quit_key,
    )

    for asset_path in asset_paths:
      pyxel.load(asset_path)

  def run(self) -> None:
    pyxel.run(self.update, self.draw)
