# お世話チャレンジの 素材（絵・データ・音）を アプリの 素材の フォルダ（ios/tc_assets）へ 置く
#   python3 kisekae/tc/drop/drop_install.py <絵と データの フォルダ（drop_data.py の 出力）> <音の フォルダ（kisekae/tc/snd/sfx_drop.py の 出力）> [ios/tc_assets]
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc/tc_drop.js の 名前も かえる）
#   ・置く もの：tc_dp.json・tc_dp_*.webp（18こ）・tc_se_dp_*.m4a（14こ）。リポジトリには 入れない（ios/tc_assets/ は .gitignore）
#   ・置いた あとは python3 kisekae/lite_assets.py（軽い 版を 作り直す）
import os, sys, shutil, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
IMGS = ['tc_dp.json', 'tc_dp_base.webp', 'tc_dp_front.webp', 'tc_dp_see.webp', 'tc_dp_ball.webp', 'tc_dp_icon.webp'] + [f'tc_dp_{k}{i}.webp' for k in ('uma', 'hold') for i in range(1, 7)]
SNDS = [f'tc_se_dp_{n}.m4a' for n in ['uma1', 'uma2', 'uma3', 'uma4', 'uma5', 'uma6', 'out', 'peg1', 'peg2', 'peg3', 'cup', 'miss', 'hold', 'open']]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


if __name__ == '__main__':
    img, snd = sys.argv[1], sys.argv[2]
    dst = sys.argv[3] if len(sys.argv) > 3 else os.path.normpath(os.path.join(HERE, '..', '..', '..', 'ios', 'tc_assets'))
    assert os.path.isdir(dst), dst
    todo = [(os.path.join(img, f), f) for f in IMGS] + [(os.path.join(snd, f), f) for f in SNDS]
    miss = [f for p, f in todo if not os.path.isfile(p)]
    assert not miss, ('足りない', miss)
    clash = [f for p, f in todo if os.path.exists(os.path.join(dst, f)) and sha(os.path.join(dst, f)) != sha(p)]
    assert not clash, ('同じ 名前で 中身が ちがう ファイルが もう ある（上書きしない）', clash)
    new = 0
    for p, f in todo:
        q = os.path.join(dst, f)
        if not os.path.exists(q): shutil.copyfile(p, q); new += 1
    print('置いた', new, 'こ・もう あった', len(todo) - new, 'こ →', dst, '（合わせて', sum(os.path.getsize(os.path.join(dst, f)) for _, f in todo), 'B）')
    print('つぎ：python3 kisekae/lite_assets.py')
