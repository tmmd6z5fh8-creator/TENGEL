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

## 6. まとめる・置く

```
drop_data.py app/assets                                    # tc_dp.json（場所と 落ち方）＋ 絵 17まい
python3 kisekae/tc/drop/drop_install.py <app/assets> <音の フォルダ>   # ios/tc_assets へ（上書きしない）
python3 kisekae/lite_assets.py                             # 軽い 版を 作り直す
```

絵と データが 入って いない ビルド（CI など）では、入口が 出ない だけ（`TCDrop.ready()` が false）。
