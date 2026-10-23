# アプリに入れるフォント（SIL Open Font License 1.1）

App Store版のアプリ（build_ios.py）だけが使う。Web版は今までどおり Google Fonts から読む。
アプリでは Google に通信しないで、この中のフォントをそのまま使う（電波がなくても同じ見た目）。

| ファイル | フォント | 著作権 | ライセンス |
|---|---|---|---|
| BIZUDPGothic-Regular.ttf / BIZUDPGothic-Bold.ttf | BIZ UDPGothic | Copyright 2022 The BIZ UDGothic Project Authors | OFL-BIZUDPGothic.txt |
| DelaGothicOne-Regular.ttf | Dela Gothic One | Copyright 2020 The Dela Gothic Project Authors | OFL-DelaGothicOne.txt |
| IBMPlexMono-Medium.ttf / IBMPlexMono-SemiBold.ttf | IBM Plex Mono | Copyright © 2017 IBM Corp. with Reserved Font Name "Plex" | OFL-IBMPlexMono.txt |

- 入手元：github.com/google/fonts（ofl/bizudpgothic・ofl/delagothicone・ofl/ibmplexmono、コミット bd8f81ddb5c74d5c8897b36ad88b440266245103）
- **ファイルは変えない**（縮める・形式を変えるとOFLの「改変」になる。IBM Plex には予約名「Plex」がある）
- ライセンスの全文はアプリの「設定 → このアプリについて → フォントのライセンス」で見られる（build_ios.py が入れる）

## 着せ替えの字（ks/・第4弾・2026/10/24〜）

`ks/` は 着せ替え（30テーマ）の 字：Google Fonts の 29ファミリー（SIL OFL 1.1）を **使う字だけに しぼった WOFF2**（45ファイル・約3.1MB）。`kisekae/build_fonts.py` が github.com/google/fonts（ofl/）の 元の TTF から 作る（可変フォントの Murecho・M PLUS 1 は 太さごとに 静的に）。

- 本文の 字（テーマの `--font`・太さ 700以下）：アプリの 画面の 言葉（文字列）＋ ASCII＋ かな（`ks/chars_body.txt`）。見出しの 字（`--dfont`・PUSH の 字・太さ 800以上）：決まった 言葉（`ks/chars_disp.txt`）。ない字は BIZ UDPGothic で 出る（`font-family` の つぎ）
- **どの フォントにも Reserved Font Name は 無い**ので、しぼっても 名前は そのまま（OFL の 条件：ライセンスと 著作権の 表示は フォントの 中（name の 表）と `ks/OFL-<Family>.txt` に 残して ある。M PLUS Rounded 1c は 元の フォルダに OFL.txt が 無いので METADATA.pb の 著作権＋ OFL 1.1 の 本文）
- 一覧は `ks/fonts.json`（family・weight・file・role・glyphs・bytes・元の ファイル）。画面の 言葉が ふえたら `python3 kisekae/build_fonts.py ~/google/fonts/ofl` で 作り直す（`test_iphone_only.py` が 足りない字を 見つける）
- ライセンスの 全文は アプリの「設定 → このアプリについて → フォントのライセンス」にも（build_pwa.py が 入れる）

