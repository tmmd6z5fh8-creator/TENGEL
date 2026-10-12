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
