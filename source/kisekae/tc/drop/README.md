# お世話チャレンジ（玉を 落とす 台）の 素材を 作る 道具

第4.173版（まさちゃん 2026/11/14 23:34「トレーニングセンターの抽選を、今のボタンと、もう一つボール落としができるようにしたい！ パチンコ台は俺が3Dで作ってくる！」）。
アプリの 中身は `tc/tc_drop.js`（台の 画面）・`tc/tc_app.js`（抽選・保存）・`tc/tc_care.js`（PUSH の 横の 入口）。ここは **素材を 作る 道具** だけ。

**まさちゃんの 3D（Meshy の GLB）・馬バレと 保留の 絵・できた 素材は リポジトリに 入れない**（`ios/tc_assets/` は `.gitignore`）。
道具は ぜんぶ 作業フォルダ（リポジトリの 外）を 読み書きする：

```
TC_DROP_DIR=<作業フォルダ> python3 -I kisekae/tc/drop/<道具>.py …
```

`-I` を つける（もらった ファイルを 読む Python は 切りはなして 動かす）。作業フォルダの 中：

| 場所 | 中身 |
|---|---|
| `in/machine_orig.glb` | まさちゃんの 3D（**書きかえない**） |
| `out/` | 直した 3D（`Tenger_Lucky_Drop_v2.glb`）・釘の 場所（`pegs_orig.json`）・見る 用（`look/`・`sheet/`） |
| `art/in/01〜12_*.png` | 馬バレ 6色（01〜06：青・緑・紫・赤・金・虹）・保留 6色（07〜12） |
| `art/out/` | そろえた 絵（`tc_dp_uma1〜6`・`tc_dp_hold1〜6`） |
| `app/` | アプリ用の 途中の もの（`base.npz`・`front.png`・`ball.png`・`paths.json` …） |

3D を 描くのは `kisekae/r3d/glb`（自前の 読みこみ・描く 道具）。`common.py` が GLB を 読む・書く（trimesh などは 使わない）。

## 1. 3D の 直し（釘を 2倍・屋根の 馬の 目）

まさちゃん 11/14 23:58「①釘をもっと伸ばせる？ ②目が色が変になってるからそこだけ塗り直せる？」→ 11/15 00:40「長さいいよ！目もOK」。

```
hmap.py in/machine_orig.glb out/look/hmap_orig.npz     # 正面から 見た 高さの 地図
pegs.py                                                # 釘 18本を 見つける → out/pegs_orig.json
make_v2.py out/Tenger_Lucky_Drop_v2.glb 2.0            # 釘を 2倍・目を ぬり直す（新しい GLB。もう あれば 止まる）
check_v2.py out/Tenger_Lucky_Drop_v2.glb               # 元と くらべる：動いたのは 釘の 頂点と 目の 絵の 点 だけ
```

- 釘：ピラミッドの 形に 合う 頂点 だけを 前（+z）へ のばす（土台・盤は 動かさない）。`pegs.py` の `stretch`
- 目：こぶ（球）の 表面に のって いる 絵の 点を 3D の 場所から 決めて ぬる（どの 向きから 見ても 同じ）。`eyes.py`
- 絵（テクスチャ）は PNG で 入れ直す（JPEG に すると 関係ない 所の 色まで 変わる）
- 見くらべの 絵：`prev_pegs.py`・`sheet_render.py`・`sheet_make.py`／いろいろな 向き：`view.py`／中身を 見る：`glb_info.py`

## 2. 台の 絵（アプリで 描く もと）

```
drop_render.py out/Tenger_Lucky_Drop_v2.glb app/base.npz   # 正面の 絵（1120×1830・影つき）→ base.npz と base.png
drop_layers.py                                             # 玉より 手前の 所（釘の 先・コップの 前）→ app/front.png
ball.py app/ball.png                                       # 玉（赤い 折り紙の 多面体・32コマ）
layout1.py ; layout2.py                                    # 液晶の 丸・当選の ます・ボタン・コップ・釘の 場所 → layout1.json・layout2.json
lock_open.py                                               # 「保留結果を見る」の あいた かぎ（その 所 だけ）→ see_open.png・see_open.json
```

- カメラと 写し方（台の 座標 → 絵の 画素）は `cam.py`。**正射影の カメラは 明かりの 向きが 逆に なる**（r3d の くせ）→ 遠い 所から 遠近で 描く
- 影は 帯に 分けて 2倍で 描く（`drop_render.py`：メモリを 使いすぎない）

## 3. 玉の 落ち方（16とおり）

```
E_PEG=0.62 physics.py 7000 out/look/sims_f.pkl     # 2D の 物理で 7,000回 落とす（玉＝円・台＝切り口の 折れ線）→ コップに 入った もの だけ のこす
E_PEG=0.62 paths.py out/look/sims_f.pkl            # コップごとに 4つ えらぶ → app/paths.json（60コマ／秒）＋ 見る 用の 絵
```

- 台の 形：`slice.py`（z＝一定で 切る）→ `world.py`（つなぐ・かどを へらす）。玉の 中心の 深さ `ZC=0.054`
- `E_PEG`＝釘の はね返り。0.46 だと いちばん 左の コップに ほとんど 入らない → 0.62（よく はずむ）
- えらび方：`pick.py`（出口から まっすぐ 出る・止まりかけない・釘に 4〜7回 当たる …）。同じ ような 落ち方は えらばない
- 左の コップを ねらって 足す とき：`aim0.py <回数>`（いまの 16とおりには 使って いない）／落ち方を 絵で 見る：`simview.py`
- どの コップに 入っても 抽選の 結果は 同じ（アプリは 16の 中から でたらめに 1つ）

## 4. 馬バレ・保留の 絵

```
drop_art.py art/in art/out     # 6色の 大きさ・まん中を そろえる。馬バレは 金の 枠を 取って 中の 丸 だけ（台の 黄色い 縁に はめる）
```

まさちゃん 11/15 01:08「サイズ合うなら馬バレアイコンの金の枠無くして、馬バレの縁に合わせた方が綺麗かもね！」。形を 測る：`art_fit.py`・`art_ring.py`

## 5. 音

`kisekae/tc/snd/sfx_drop.py <出力の フォルダ>`（馬バレ 6色・玉が 出る・釘・コップ・はずれ・保留・かぎ：14こ）。数で 確かめる：`snd_check.py <wav の フォルダ>`

第4.174版（まさちゃん 2026/11/15 12:29）：馬バレ音を 作り直した（`tc_se_dp_umb1〜6.m4a`：0.1秒 ごとの 拍に ピ・ドゥ・ギュン ＋ 金と 虹は ドーンドーン・デゥデゥーン を ぜんぶ 同時に）。
`sfx_drop.py` は 前の 6つ（`uma1〜6`）と 新しい 6つ（`umb1〜6`）の 両方を 出す（20こ）。アプリに 入るのは 新しい 6つ（前の 6つは もとの フォルダに のこす：`assets_dir.superseded`）。
大きさは 耳に 聞こえる 大きさ（A特性）で そろえる：`python3 kisekae/tc/snd/loud.py <wav か m4a> …`。拍の 数・間（`BEAT`・`LONG_GAP`・`N_BEAT`・`N_LONG`）を かえたら `tc/tc_drop.js` の 同じ 数字も かえる（ランプが 拍で 光る）

## 6. まとめる・置く

```
drop_data.py app/assets                                    # tc_dp.json（場所と 落ち方）＋ 絵 17まい
python3 kisekae/tc/drop/drop_install.py <app/assets> <音の フォルダ>   # ios/tc_assets へ（上書きしない）
python3 kisekae/lite_assets.py                             # 軽い 版を 作り直す
```

絵と データが 入って いない ビルド（CI など）では、入口が 出ない だけ（`TCDrop.ready()` が false）。

## 7. 激馬熱馬（第4.175版）

まさちゃん 2026/11/15 13:56「トレーニングセンターに激馬熱馬当選を追加　1/299999 …」。素材は 7こ（どれも リポジトリに 入れない）。道具は ここと 1つ 上（`kisekae/tc/`）と 音（`kisekae/tc/snd/`）。

```
python3 -I kisekae/tc/drop/geki_art.py <馬バレの 絵（丸）> <保留の 絵（八角）> <出力>      # tc_dp_uma7.webp・tc_dp_hold7.webp（ほかの 6色と 同じ 大きさ）
python3 -I kisekae/tc/geki_cut_measure.py <40000P の 3D>                              # 「4」の くぼみの 底の 三角を 頂点から 測る（何も 書かない）
python3 -I kisekae/tc/geki_cut.py <40000P の 3D> <出す 3D>                            # 「4」の 三角の 中 だけ くりぬく（14:11「4の3Dの赤線の中だけくり抜いて！」）
python3 -I kisekae/tc/geki_film.py <くりぬいた 3D> <天国の 絵> <コマの フォルダ>          # 天国の 動画の コマ（1170×1842・72コマ：1コマ 14秒 ほど）
python3 -I kisekae/tc/geki_film.py --flash <コマの フォルダ>                           # 動画 だけで 光の 点めつを 数える（決まり：10% 未満）
python3 -I kisekae/tc/geki_film.py --encode <コマの フォルダ> <出力>                   # tc_gk_film2.mp4・tc_gk_end2.webp
python3 kisekae/tc/snd/sfx_geki.py <出力>                                            # tc_se_gk_pchun.m4a・tc_se_gk_heaven.m4a・tc_se_gk_tedeen.m4a
python3 kisekae/tc/geki_install.py <絵> <動画> <音>                                   # ios/tc_assets へ（上書きしない）
python3 kisekae/lite_assets.py                                                      # 軽い 版を 作り直す
```

- 動画の 動かし方（`geki_film.py` の `shot`）を かえたら `--flash` で 数える（小さく 作った コマ `--scale 0.2` でも 同じ 数に なる：1回 50秒）。
  はじめの 動かし方（カットインの 間に カメラが 12度 回る）は 11.0% で 決まりを こえて いた → ゆっくり 寄る だけに して 1.7%。アプリの 中での 数は `test_tc_geki_flash.py`
- カットの 時刻（`CUT_F`・`TEXT_F`）を かえたら `kisekae/tc/snd/sfx_geki.py` の `FILM` と `tc/tc_fx.js` の `GK` も かえる（`test_tc_geki.py` が 見くらべる）
- プチュンの 線の 形（`tc/tc_fx.js` の `GKL`）と 音（`sfx_geki.py`）は、まさちゃんの 見本の 動画を 数字で 測って 作った（線の 太さ・明るさ・音の 高さの 動き）。見本の 動画・その 音は 使って いない（リポジトリにも 入れない）
- 素材が ない とき：激馬熱馬の 絵（uma7・hold7）だけ ない＝馬バレと 保留は 虹の 絵で 代わり／動画と さいごの コマが ない（CI など）＝天国の 場面は 暗い 舞台に 字 だけ。どちらも 40,000P は 受け取れる
