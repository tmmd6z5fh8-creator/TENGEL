# 激馬熱馬（第4.175版）の 素材（絵・動画・音）を アプリの 素材の フォルダ（ios/tc_assets）へ 置く
#   python3 kisekae/tc/geki_install.py <絵の フォルダ（kisekae/tc/drop/geki_art.py の 出力）> <動画の フォルダ（kisekae/tc/geki_film.py --encode の 出力）> <音の フォルダ（kisekae/tc/snd/sfx_geki.py の 出力）> [ios/tc_assets]
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc/tc_fx.js・tc/tc_drop.js・tc/tc_app.js の 名前も かえる）
#   ・置く もの 7こ：tc_dp_uma7.webp・tc_dp_hold7.webp（馬バレ・保留の 絵）／tc_gk_film2.mp4・tc_gk_end2.webp（天国の 動画と さいごの コマ）／tc_se_gk_pchun.m4a・tc_se_gk_heaven.m4a・tc_se_gk_tedeen.m4a
#     リポジトリには 入れない（ios/tc_assets/ は .gitignore）
#   ・置いた あとは python3 kisekae/lite_assets.py（軽い 版を 作り直す）
import os, sys, shutil, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
ART = ['tc_dp_uma7.webp', 'tc_dp_hold7.webp']
FILM = ['tc_gk_film2.mp4', 'tc_gk_end2.webp']      # 2＝カットインの カメラを ゆっくりに した もの（kisekae/tc/geki_film.py）。はじめの もの（番号 なし）は もとの フォルダに 残す
SNDS = ['tc_se_gk_pchun.m4a', 'tc_se_gk_heaven.m4a', 'tc_se_gk_tedeen.m4a']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


if __name__ == '__main__':
    art, film, snd = sys.argv[1], sys.argv[2], sys.argv[3]
    dst = sys.argv[4] if len(sys.argv) > 4 else os.path.normpath(os.path.join(HERE, '..', '..', 'ios', 'tc_assets'))
    assert os.path.isdir(dst), dst
    todo = [(os.path.join(art, f), f) for f in ART] + [(os.path.join(film, f), f) for f in FILM] + [(os.path.join(snd, f), f) for f in SNDS]
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
