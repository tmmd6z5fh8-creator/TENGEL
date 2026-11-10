# 動く 絵の 部品を アプリと 同じ じゅんに 重ねた 絵 と 止まった 絵（背景＋前の 絵）の 点ごとの 差（第4.145版）
#   python3 kisekae/bcp/chr/parts_vs_still.py [絵の フォルダ（ios/bcp_assets）] [名前,…]
#   第4.145版から、キャラなしの 背景（bgx）が ある 48段は 止まった 絵を アプリに 入れない（bcx.js の picParts が 部品を 重ねて 同じ 絵を 出す）。
#   部品を 作り直した（chr_stage.py → chr_snap.py）あとは、これで「重ねた 形が 止まった 絵と 同じ（ちがいは 圧縮 だけ）」を 確かめる。
#   重ねる じゅん（ボードは のぞく）：キャラなしの 背景 → キャラ（top で ない とき）→ oc → 前の 絵 → キャラ（top）→ ボードの 前に 出る 所（f）→ ot
#   2026/11/10 の 数：48段で 平均 0.8〜2.1／255・p99.9 8〜20・最大 67（ふちの 圧縮の ちがい）・32 より 大きい 点は 多い 絵で 102こ（296万点の うち）
#   SAVE=<フォルダ>：重ねた 絵（parts_<名前>.png）と 止まった 絵（still_<名前>.png）を 書く
import os, sys
import numpy as np
from PIL import Image
H_ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(H_)); import bcp_app as B
A = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(H_), '..', '..', 'ios', 'bcp_assets')
ONLY = sys.argv[2].split(',') if len(sys.argv) > 2 else None
SAVE = os.environ.get('SAVE')
K = 3; Wc, Hc = 390 * K, 844 * K


def rgba(f):
    return np.asarray(Image.open(os.path.join(A, f)).convert('RGBA')).astype(np.float32) / 255


def over(C, x):
    return x[..., :3] * x[..., 3:4] + C * (1 - x[..., 3:4])


def put(C, f, box):
    x = rgba(f); x0, y0, bw, bh = [int(round(v * K)) for v in box]
    assert x.shape[:2] == (bh, bw), (f, x.shape, bh, bw)
    assert abs(box[0] * K - x0) < 1e-6 and abs(box[1] * K - y0) < 1e-6, (f, box)       # 3倍で ちょうど 点に 合う 場所
    C[y0:y0 + bh, x0:x0 + bw] = over(C[y0:y0 + bh, x0:x0 + bw], x)


def one(n):
    mo = B.MOTION[n]
    stb = rgba(f'bcp_{n}.webp')[..., :3]; fgp = f'bcp_{n}_fg.webp'; has_fg = bool(B.cfg(n).get('fg'))
    assert has_fg == os.path.exists(os.path.join(A, fgp)) == bool(mo.get('fgx')), n
    comp = over(stb, rgba(fgp)) if has_fg else stb
    bx = rgba(mo['bgx']); assert bx.shape[:2] == (Hc, Wc) and float(bx[..., 3].min()) == 1.0, (n, bx.shape)
    C = bx[..., :3].copy(); L = mo['layers']
    if not mo.get('top'):
        for l in L: put(C, l['src'], l['box'])
    if mo.get('oc'): put(C, mo['oc']['src'], mo['oc']['box'])
    if has_fg: C = over(C, rgba(mo['fgx']))
    if mo.get('top'):
        for l in L: put(C, l['src'], l['box'])
    for l in L:
        if l.get('f'): put(C, l['f'], l['box'])
    if mo.get('ot'): put(C, mo['ot']['src'], mo['ot']['box'])
    if SAVE:
        os.makedirs(SAVE, exist_ok=True)
        Image.fromarray((np.clip(C, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(SAVE, f'parts_{n}.png'))
        Image.fromarray((np.clip(comp, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(SAVE, f'still_{n}.png'))
    d = np.abs(C - comp).max(-1) * 255
    return n, float(d.mean()), float(np.percentile(d, 99)), float(np.percentile(d, 99.9)), float(d.max()), int((d > 16).sum()), int((d > 32).sum())


if __name__ == '__main__':
    rows = []
    for n, mo in B.MOTION.items():
        if not mo.get('bgx') or (ONLY and n not in ONLY): continue          # トロフィー（光と 雲だけ）は 止まった 絵の まま
        rows.append(one(n)); print('%-10s 平均 %.2f p99 %.1f p99.9 %.1f 最大 %.0f  16より 大きい 点 %d  32より 大きい 点 %d' % rows[-1], flush=True)
    bad = [r[0] for r in rows if r[1] > 3 or r[3] > 28 or r[6] > 400]       # ここを こえたら 部品が 止まった 絵と 合って いない（そろえ直す）
    print('段', len(rows), '・p99.9 の 最大', max(r[3] for r in rows), '・最大', max(r[4] for r in rows), '・32より 大きい 点の 最大', max(r[6] for r in rows), '・合って いない 段', bad)
    sys.exit(1 if bad else 0)
