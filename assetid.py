
from game import AssetId


class TileId:
  FIELD = AssetId(0, 0)


class ImageId:
  BALL = AssetId(0, 0)
  JUMPER = AssetId(0, 1)
  LIFE = AssetId(0, 3)


class SoundCh:
  JUMPER = 2
  BALL = 2
  SCENE = 3


class SoundId:
  JUMPER = 0
  BALL = 10
  SCENE = 20
