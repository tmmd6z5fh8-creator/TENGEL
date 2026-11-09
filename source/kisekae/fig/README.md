# 思い出フィギュアの 形と 絵（第4.134版〜）

まさちゃんの GLB（フィギュア 8体・3D の 棚）と 棚の 色ちがいの 写真 7まい、それから 作った もの は **リポジトリに 入れない**（`.gitignore`：`ios/fig_assets/`）。
ここに あるのは 作る 道具だけ。作業フォルダ（例：`/home/claude/work/figures`）に こう 置いて 使う：

```
src/fig1.glb … src/fig8.glb      まさちゃんの フィギュア（①〜⑤ 通常・⑥ 神様馬・⑦ 幻の馬・⑧ 幻の馬＆神様馬）
shelf/shelf_model.glb            3D の 棚
shelf/shelf_1.png … shelf_7.png  棚の 色ちがいの 正面の 写真（ブース 1〜7 の 色）
```

1. 形を へらして 絵を 作る（UV の 継ぎ目は 動かさない → 元の 絵を そのまま 使う。法線は 元の 細かい 形から 焼く）
   `python3 kisekae/fig/fig_prep.py src/figN.glb out/figN <三角の 数>`（① 80000・② 80000・③ 120000・④ 80000・⑤ 100000・⑥ 90000・⑦ 90000・⑧ 100000）
   棚：`python3 kisekae/fig/fig_prep.py shelf/shelf_model.glb out/shelf 24000`
2. ボードの 板（金の わくの 中の くぼんだ 面）：`python3 kisekae/fig/board_find.py out/fig1.npz … out/fig8.npz` → `out/figN_board.json`
3. 棚に 写真を はる：`python3 kisekae/fig/shelf_proj.py out/shelf shelf/shelf_1.png … shelf/shelf_7.png` → `out/shelf_c1〜7.webp`
4. 何も 書いて いない ボードを はめた 写真（「デザインを 選ぶ」画面・まさちゃん 11/09 21:04）
   `python3 kisekae/fig/blank_board.py src/figN.glb out/figN_board.json <gold・amethyst（⑦）・duel（⑧）> thumbs/figN.png 640`
   元の まま の 写真は `python3 kisekae/fig/thumb.py src/figN.glb thumbs/figN.png 640`
5. アプリに 入れる：`python3 kisekae/fig/collect_assets.py <作業フォルダ>` → `ios/fig_assets/`（`build_ios.py` が Resources/ に 入れる。CI は `FIG_ASSETS=/nonexistent`）

- `qem.c`：形を へらす（QEM）・UV の 上に 塗る・画面の 深さ（`fig_prep.py` が gcc で 作って ctypes で 使う）
- アプリの 中：`fig/fig_render.js`（WebGL）・`fig/fig_app.js`（ブース・一覧・部屋・作る 画面）・`fig/fig_launch.js`（入口）
- 作業の 場所が 新しく なって 絵・音が 消えた ときは、前に 作った パッケージから `python3 ios/restore_assets.py <Tengel_xxx.swiftpm.zip>`
