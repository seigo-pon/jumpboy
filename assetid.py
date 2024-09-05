
from game import AssetImageId


class TileId:
  FIELD = AssetImageId(0, 0)


class ImageId:
  BALL = AssetImageId(0, 0)
  JUMPER = AssetImageId(0, 1)
  LIFE = AssetImageId(0, 3)


class SoundId:
  JUMPER = 0
  BALL = 10
  SCENE = 20
  BGM = 60
