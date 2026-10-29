# アプリに入れるフォント（SIL Open Font License 1.1）

App Store版のアプリ（build_ios.py）だけが使う。Web版は今までどおり Google Fonts から読む。
アプリでは Google に通信しないで、この中のフォントをそのまま使う（電波がなくても同じ見た目）。

| ファイル | フォント | 著作権 | ライセンス |
|---|---|---|---|
| BIZUDPGothic-Regular.ttf / BIZUDPGothic-Bold.ttf（アプリには .woff2） | BIZ UDPGothic | Copyright 2022 The BIZ UDGothic Project Authors | OFL-BIZUDPGothic.txt |
| DelaGothicOne-Regular.ttf（アプリには .woff2） | Dela Gothic One | Copyright 2020 The Dela Gothic Project Authors | OFL-DelaGothicOne.txt |
| IBMPlexMono-Medium.ttf / IBMPlexMono-SemiBold.ttf | IBM Plex Mono | Copyright © 2017 IBM Corp. with Reserved Font Name "Plex" | OFL-IBMPlexMono.txt |

- 入手元：github.com/google/fonts（ofl/bizudpgothic・ofl/delagothicone・ofl/ibmplexmono、コミット bd8f81ddb5c74d5c8897b36ad88b440266245103）
- **TTF は 入手した まま 変えない**（ほかの 道具（CM・絵を 作る スクリプト）も 使う・WOFF2 の もと）
- **第4.109版**：アプリに 入れるのは、Reserved Font Name が 無い BIZ UDPGothic（2つ）と Dela Gothic One を **字は そのまま（しぼらない）で WOFF2 に した もの**
  （`python3 ios/fonts/make_woff2.py`：約11.8MB → 約5.6MB。もどすと 字の 並び・cmap・幅・形・name の 表が もとの TTF と 同じ ことを 確かめる。DSIG＝電子署名の 表だけは WOFF2 の きまりで 入らない）。
  形式を かえるのは OFL の「改変」に あたるが、予約名が 無い ので 名前は そのまま 使える（著作権と ライセンスは フォントの 中の name の 表と OFL-<Family>.txt・「このアプリについて」に そのまま）。
  **IBM Plex Mono は 予約名「Plex」が ある ので もとの TTF の まま**（2つで 約0.28MB）
- ライセンスの全文はアプリの「設定 → このアプリについて → フォントのライセンス」で見られる（build_ios.py が入れる）

## 着せ替えの字（ks/・第4弾・2026/10/24〜）

`ks/` は 着せ替え（30テーマ）の 字：Google Fonts の 29ファミリー（SIL OFL 1.1）を **使う字だけに しぼった WOFF2**（45ファイル・約3.1MB）。`kisekae/build_fonts.py` が github.com/google/fonts（ofl/）の 元の TTF から 作る（可変フォントの Murecho・M PLUS 1 は 太さごとに 静的に）。

- 本文の 字（テーマの `--font`・太さ 700以下）：アプリの 画面の 言葉（文字列）＋ ASCII＋ かな（`ks/chars_body.txt`）。見出しの 字（`--dfont`・PUSH の 字・太さ 800以上）：決まった 言葉（`ks/chars_disp.txt`）。ない字は BIZ UDPGothic で 出る（`font-family` の つぎ）
- **どの フォントにも Reserved Font Name は 無い**ので、しぼっても 名前は そのまま（OFL の 条件：ライセンスと 著作権の 表示は フォントの 中（name の 表）と `ks/OFL-<Family>.txt` に 残して ある。M PLUS Rounded 1c は 元の フォルダに OFL.txt が 無いので METADATA.pb の 著作権＋ OFL 1.1 の 本文）
- 一覧は `ks/fonts.json`（family・weight・file・role・glyphs・bytes・元の ファイル）。画面の 言葉が ふえたら `python3 kisekae/build_fonts.py ~/google/fonts/ofl` で 作り直す（`test_iphone_only.py` が 足りない字を 見つける）
- ライセンスの 全文は アプリの「設定 → このアプリについて → フォントのライセンス」にも（build_pwa.py が 入れる）

