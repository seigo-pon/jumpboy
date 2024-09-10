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
- pyxel-universal-font

## Assets
### Fonts
- [PixelMplus](https://itouhiro.hatenablog.com/entry/20130602/font) に掲載されているフォントを使用しています。

### Sound effects
- [8bit_taste_game_se](https://booth.pm/ja/items/2576189) に掲載されている効果音を使用しています。

### BGMs
- [8bit-bgm-generator](https://github.com/shiromofufactory/8bit-bgm-generator?tab=readme-ov-file) を用いて作成したBGMを使用しています。

## Getting started
```bash
# Install libraries.
pip install -r requirement.txt

# Start game.
pyxel run jumpboy/app.py
```

## Asset file edits
```bash
# Edit pyxel assets.
pyxel edit jumpboy/assets/jumpboy.pyxres
```

フォントをインストールする場合は、以下の操作を実行してください。
```bash
# Open font folder in 'pyxel-universal-font' library.
puf edit
# Copy font files in 'jumpboy/assets/font' folder.
```

## Build packages
```bash
# Remove folder
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
