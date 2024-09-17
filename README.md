# jumpboy

## Overviews
- jumpboyは、pyxelライブラリを用いて作成された2Dゲームです。
- ジャンルはアクションゲームです。
- PCではキーボード、スマホではタッチのみで操作します。

## Environments
### Software language
- Python 3.12

### Libraries
- pyxel

## Assets
### Fonts
- [PixelMplus](https://itouhiro.hatenablog.com/entry/20130602/font) に掲載されているフォントを使用しています。
  - TTFファイルをBDFファイルに変換しています。

### Sound effects
- [8bit_taste_game_se](https://booth.pm/ja/items/2576189) に掲載されている効果音を使用しています。

### BGMs
- [8bit-bgm-generator](https://github.com/shiromofufactory/8bit-bgm-generator?tab=readme-ov-file) を用いて作成したBGMを使用しています。

## Getting started
```bash
# Install libraries.
pip install -r requirement.txt

# Copy env file.
cp jumpboy/env.sample.py jumpboy/env.py

# Start game.
pyxel run jumpboy/app.py
```

## Edit assets
```bash
# Edit pyxel assets.
pyxel edit jumpboy/assets/jumpboy.pyxres
```

## Build packages
```bash
# Remove temporary folder.
rm -rf jumpboy/snapshot

# Build.
pyxel package jumpboy jumpboy/app.py

# Play game.
pyxel play jumpboy.pyxapp
```

## Game rules
- 作成中...

## License
- GNU General Public License (GPL)
