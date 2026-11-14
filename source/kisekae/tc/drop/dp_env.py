# お世話チャレンジの 道具が 使う 作業フォルダ（リポジトリの 外）。まさちゃんの 3D・絵・できた 素材は リポジトリに 入れない
#   TC_DROP_DIR=<作業フォルダ> python3 -I kisekae/tc/drop/<道具>.py …
#   作業フォルダの 中：in/machine_orig.glb（まさちゃんの 3D：書きかえない）・out/（直した 3D・釘の 場所・見る 用の 絵）・art/in（馬バレ・保留の 絵 01〜12）・art/out・app/（アプリ用の 素材）
import os, sys
ROOT = os.environ.get('TC_DROP_DIR', '').rstrip('/')
if not ROOT:
    sys.exit('TC_DROP_DIR=<作業フォルダ> を つけて 走らせてね（kisekae/tc/drop/README.md）')
