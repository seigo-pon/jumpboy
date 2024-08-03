from typing import Callable
from game import GameProfile
import os
import pyxel


class GameEngine:
  def __init__(
    self,
    profile: GameProfile,
    quit_key: int,
    asset_filenames: list[str],
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

    for asset_filename in asset_filenames:
      pyxel.load(asset_filename)

  @classmethod
  def folder_path(cls, root, folder) -> str:
    root_dir = os.path.abspath(os.path.join(os.path.abspath(root), os.pardir))
    return os.path.join(root_dir, folder)

  def start(self) -> None:
    pyxel.run(self.update, self.draw)
