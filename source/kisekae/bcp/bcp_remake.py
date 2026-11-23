# 結果ボードカスタム（絵の ボード）：アプリに 入れる 絵を 作り直す（第4.215版・まさちゃん 2026/11/24 01:31 の ①〜④）
#   python3 kisekae/bcp/bcp_remake.py <絵の フォルダ（ios/bcp_assets）> <出す フォルダ> [デザイン…]
#   デザインごとに：
#     1. bcp_ext.make   ：絵の 上・下に 足す 所を 作り直す（光の すじ・やわらかい うつりこみ・iPad の 画面の あとを 消す）
#     2. bcp_fg2.make   ：ボードの 前の 絵を 絵の ぎりぎりで 切りぬき直す → bcp_<デザイン>_f2.webp（前の 絵が ある デザイン だけ）
#     3. bcp_blank.clean：板の 中を ぬり直す（新しい 前の 絵に 合わせて・絵の ぎりぎり まで）→ bcp_<デザイン>_b2.webp
#   もとの 絵（bcp_<デザイン>.webp・_fg.webp・_bl.webp）は 読む だけ（消さない・上書きしない）。できた 絵を 絵の フォルダへ 写す ときも 新しい 名前 なので 上書きに ならない
import sys, os, time, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import bcp_app, bcp_blank, bcp_ext, bcp_fg2
BG, FG = '_b2', '_f2'


def remake(src, out, name, keep_ext=None):
    t = time.time(); E = bcp_ext.make(src, name)
    if keep_ext: Image.fromarray(np.clip(E + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(keep_ext, f'bcp_{name}.png'))
    has_fg = bool(bcp_app.cfg(name).get('fg')); fgm = None; info = ''
    if has_fg:
        f2 = bcp_fg2.make(src, name, P=E); fp = os.path.join(out, f'bcp_{name}{FG}.webp'); Image.fromarray(f2, 'RGBA').save(fp, 'WEBP', quality=90, method=6)
        f2 = np.asarray(Image.open(fp).convert('RGBA')); fgm = f2[..., 3] > 8; info = f' 前の絵 {int(fgm.sum())}px {os.path.getsize(fp)}B'
    o, M = bcp_blank.clean(src, name, bcp_blank.cfg_of(name, v2=True), P=E, fg=fgm if has_fg else np.zeros(E.shape[:2], bool))
    bp = os.path.join(out, f'bcp_{name}{BG}.webp'); Image.fromarray(o).save(bp, 'WEBP', quality=90, method=6)
    print(name, bcp_ext.fam_of(name) or '-', 'ぬり直した 点', int(M.sum()), os.path.getsize(bp), 'B' + info, round(time.time() - t, 1), 's', flush=True)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('使い方：bcp_remake.py <絵の フォルダ> <出す フォルダ> [デザイン…]'); sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); ke = os.environ.get('KEEP_EXT')
    if ke: os.makedirs(ke, exist_ok=True)
    for n in (sys.argv[3:] or [n for _i, _k, st in bcp_app.ITEMS for _d, n in st]):
        remake(src, out, n, ke)
