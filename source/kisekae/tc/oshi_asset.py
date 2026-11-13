# 「推し馬」の 丸い ボタンの 絵を アプリ用に 置く（第4.165版・まさちゃん 2026/11/13 12:47「推し馬はすぐに確認できるように、トレーニングセンターと思い出フィギュアの
#   アイコンのところの1番上に配置して！推し馬のアイコンをタップしたら、推し馬の欄に飛ぶように設定して！」＋ 金の 輪・緑の 地に 笑って いる 茶色の 馬と ピンクの ハートの 丸い 絵 1まい）
#   python3 kisekae/tc/oshi_asset.py <まさちゃんの 絵（PNG・すき通し）> [ios/tc_assets]
#   → tc_icon_oshi.webp（240×240・丸は 232px）：トレーニングセンター（tc_icon_tc.webp）・思い出フィギュア（fg_icon.webp）の アイコンと 同じ 作り方（kisekae/fab_icon.py）＝ 3つの 丸が 同じ 大きさ
#   ・使う 所：tc/tc_launch.js の 右下の 丸い ボタンの 列（#fabCol）の 1番 上（#oshiFab）→ 押すと 作戦会議の「推し馬」の 欄
#   ・もとの 絵（まさちゃんの PNG）と できた ファイルは リポジトリに 入れない（ios/tc_assets/ は .gitignore）
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc/tc_launch.js の 名前も かえる）
#   ・kisekae/tc/collect_assets.py は 出す フォルダを 作り直す ので、走らせた あとは これを もう一度。足した あとは python3 kisekae/lite_assets.py
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fab_icon
NAME = 'tc_icon_oshi.webp'


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ios', 'tc_assets')
    assert os.path.isdir(out_dir), out_dir
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, NAME); im = fab_icon.make(src, tmp); data = open(tmp, 'rb').read()
    dst = os.path.join(out_dir, NAME)
    if os.path.exists(dst):
        if open(dst, 'rb').read() == data: print('同じ ものが もう ある：', dst); return
        raise SystemExit(f'もう ある ファイルと 中身が ちがう（上書きしない）：{dst}')
    with open(dst, 'xb') as f: f.write(data)
    print(f'{NAME}：{im.size[0]}×{im.size[1]}・{len(data):,}B → {dst}')


if __name__ == '__main__':
    main()
