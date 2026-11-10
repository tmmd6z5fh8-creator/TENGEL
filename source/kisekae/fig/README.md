# 思い出フィギュアの 形と 絵（第4.134版〜）

まさちゃんの GLB（フィギュア 8体・3D の 棚）と 棚の 色ちがいの 写真 7まい、それから 作った もの は **リポジトリに 入れない**（`.gitignore`：`ios/fig_assets/`）。
ここに あるのは 作る 道具だけ。作業フォルダ（例：`/home/claude/work/figures`）に こう 置いて 使う：

```
src/fig1.glb … src/fig8.glb      まさちゃんの フィギュア（①〜⑤ 通常・⑥ 神様馬・⑦ 幻の馬・⑧ 幻の馬＆神様馬）
shelf/shelf_model.glb            3D の 棚
shelf/shelf_1.png … shelf_7.png  棚の 色ちがいの 正面の 写真（ブース 1〜7 の 色）
```

1. 形を へらして 絵を 作る（UV の 継ぎ目で 分かれた 頂点は いっしょに たたむ → 元の 絵を そのまま 使う。法線は 元の 細かい 形と 法線マップから 焼く）
   ※ まさちゃんの GLB は 1体 115万〜770万 三角（③ が いちばん 大きい：へらすのに 数分・メモリ 約4GB）
   `python3 kisekae/fig/fig_prep.py src/figN.glb out/figN <三角の 数>`（① 80000・② 80000・③ 120000・④ 80000・⑤ 100000・⑥ 90000・⑦ 90000・⑧ 100000）
   形は そのままで 絵だけ 作り直す ときは 最後に `--keep`
   - **破片を 出さない**（まさちゃん 11/09 23:01「ところどころ破片のようなパーツが出てきてしまってる」：うしろの 黒い 板に 金・白・紫の かけら）
     - 原因：元の 絵は 小さな 島（UV の かたまり）が たくさん。へらすと 島の ふちが まっすぐに なって 三角が 島の 外に はみ出し、となりの 島（別の 場所の 金の わく・大理石 など）の 色を 塗って いた。UV の 上で うら返った 三角も 重なって 同じ ことに なって いた
     - へらす とき（`qem.c` の `qem_decimate2`）：UV の 上で 面が うら返る／つぶれる たたみ方 と、島の ふちの 線が 1点（`FIG_UVTOL`・色の 絵 2048 の 点）より 動く たたみ方は しない
     - それでも はみ出る 絵の 点は、3D で 元の 同じ 場所の 色・法線・金属／あらさ に する（`fix_maps`）。ほかの 三角と 重なる 三角は 絵の あいて いる 所へ 引っこす
     - 金属／あらさ：元の 絵は 島ごとに あらさが 少し ちがい、アプリの 光では 島の 形の まだら（紙を はった ような 形）に 見える → 3D の 近くで あらさの 近い もの だけ ならす（`smooth_mr`・金の わくと 大理石は まぜない）
     - 法線・金属／あらさ は 色と 同じ 2048 で 作って、島を またがずに 小さく する（`chart_down`）。金属／あらさ は 1024（前は 512）・劣化なしの WebP
   棚：`python3 kisekae/fig/fig_prep.py shelf/shelf_model.glb out/shelf 24000`（UV が 重なると 柱に 黒い 三角が 出る：まさちゃん 11/09 23:51「赤丸のところかけてる」→ UV を 見る へらし方で）
   - ⑧ の 黒い 馬の 紫の たてがみ には 元の 絵から 金の すじが 入って いる → `python3 kisekae/fig/fig_recolor.py out/fig8`（まわりの 紫に する。まさちゃん 11/09 23:51「紫の立髪が白いところがあるから紫に直して！」）。fig_prep.py を やり直したら もう一度
2. ボードの 板（金の わくの 中の くぼんだ 面）：`python3 kisekae/fig/board_find.py out/fig1.npz … out/fig8.npz` → `out/figN_board.json`
3. 棚に 写真を はる：`SHELF_D=8 python3 kisekae/fig/shelf_proj.py out/shelf shelf/shelf_1.png … shelf/shelf_7.png` → `out/shelf_c1〜7.webp`
   （写真の 棚の 形に カメラを 合わせる：重なり 約0.98。写って いない 床・天井・横の かべ・外がわは 同じ 材料の 正面の ふちの 色）
4. 何も 書いて いない ボードを はめた 写真（「デザインを 選ぶ」画面・まさちゃん 11/09 21:04）
   `python3 kisekae/fig/blank_board.py src/figN.glb out/figN_board.json <gold・amethyst（⑦）・duel（⑧）> thumbs/figN.png 640`
   板は 長方形 2まい（角の まるみは 絵の すける ところ）・光は 前から（わくの かげを 小さく）。元の まま の 写真は `python3 kisekae/fig/thumb.py src/figN.glb thumbs/figN.png 640`
5. アプリに 入れる：`python3 kisekae/fig/collect_assets.py <作業フォルダ>` → `ios/fig_assets/`（`build_ios.py` が Resources/ に 入れる。CI は `FIG_ASSETS=/nonexistent`）
   ブース用の 半分の 絵（`fgN_cs`・`ns`・`ms`）も 島を またがずに 小さく する・金属／あらさ は 劣化なし

- `qem.c`：形を へらす（QEM）・UV の 上に 塗る・画面の 深さ（`fig_prep.py` が gcc で 作って ctypes で 使う）
- アプリの 中：`fig/fig_render.js`（WebGL）・`fig/fig_app.js`（ブース・一覧・部屋・作る 画面）・`fig/fig_launch.js`（入口：記録タブの ボタン と 右上の 丸い ボタン（第4.138版：トレーニングセンターの 下・押すと フィギュアブース・絵は `icons/icon_memory_figure.png` → `kisekae/fab_icon.py` → `fg_icon.webp`））
- 作業の 場所が 新しく なって 絵・音が 消えた ときは、前に 作った パッケージから `python3 ios/restore_assets.py <Tengel_xxx.swiftpm.zip>`
- ミッション（第4.138版・11/10 10:50）：思い出フィギュアを 1つ・5つ・8つ 完成させる → 5,000P・5,000P・10,000P（`points.js` の `figMissions`：作った 数＝台帳の `figs.items`）
