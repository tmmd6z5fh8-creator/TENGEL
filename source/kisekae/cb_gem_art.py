# 決戦宝石（第4.197版・まさちゃん 2026/11/18 18:58「呼び寄せの決戦宝石」）の 絵
#   まさちゃんの 絵（ios/cb_assets/src/：リポジトリには 入れない・上書きしない）から アプリ用の 絵を 作る。kisekae/cb_art.py の plan() に 入る（台帳・古いかの たしかめも cb_art.py と 同じ）
#     宝石 5（1254×1254・すき通し）：cb_gem_<種類>.png → cb_gm_<種類>.webp（GEM_SIZE の 正方形：絵の ある 所を 切り出して まん中に）
#       m＝幻影のアメジスト（幻の馬トークン）・k＝日輪の黄金石（神様馬トークン）・1＝双炎のルビー（1トークン 2頭分）・3＝双葉のエメラルド（3トークン 2頭分）・7＝三峰の翡翠（7トークン 3頭分）
#     トークン 5（1024×1536・白い 紙の 上の カード）：cb_tok_<種類>.png → cb_ct<種類>.webp（800×1200）・cb_st<種類>.webp（300×450）
#       ＝ いつもの カードと 同じ 切り方（cb_art.card：2:3・同じ 角の 丸み）。アプリは「t ＋ 種類」を カードの 絵の 名前に する（cb_app.js の pk）
#     宝石ケース（2172×724・すき通し）：cb_gem_case.png → cb_gmcase.webp（CASE_W の 幅：絵の ある 所を 切り出す）。
#       5つの くぼみ（宝石を 置く 所）は CASE_SLOTS（もとの 絵の 中の 四角）→ アプリの 置き場所（cb_app.js の GEM_SLOT は ここから 計算した 数）
#     cb_gem_mock.png（まさちゃんの「宝石の設定位置イメージ」：手札の 下に ケース）は 見る だけ（アプリには 入れない）
import os, sys
import numpy as np
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
SRC = os.path.join(W, 'ios', 'cb_assets', 'src')
KINDS = ['m', 'k', '1', '3', '7']                 # ケースの 左から（まさちゃんの 1枚目〜5枚目の 順）
GEM_SIZE = (300, 300)
CASE = 'cb_gem_case.png'
CASE_W = 1100
# ケースの 5つの くぼみ（もとの 絵 2172×724 の 中：x0, y0, x1, y1。緑の くぼみの ふちの 内がわを 目で 測った）
CASE_SLOTS = [(197, 209, 547, 456), (566, 209, 903, 456), (919, 209, 1250, 456), (1278, 209, 1603, 456), (1634, 209, 1984, 456)]
TH = 40                                           # すき通しの ふちの もや（不透明度 40 より 下）は 消す


def PARAMS():
    """決めごと（cb_art.py の 台帳に 書く：かわったら 作り直す）"""
    return [KINDS, list(GEM_SIZE), CASE_W, [list(s) for s in CASE_SLOTS], TH]


def cut_soft(p, pad=0.04):
    """すき通しの ある 絵：絵の ある 所（不透明度 TH より 上）を 切り出す（まわりに 少し よゆう）・ふちの もやは 消す・まん中は ぴったり 不透明に"""
    a = np.asarray(Image.open(p).convert('RGBA')).astype(np.float32)
    al = a[..., 3]
    ys, xs = np.nonzero(al > TH)
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    m = int(round(max(x1 - x0, y1 - y0) * pad))
    x0, y0, x1, y1 = max(0, x0 - m), max(0, y0 - m), min(a.shape[1], x1 + m), min(a.shape[0], y1 + m)
    b = a[y0:y1, x0:x1].copy()
    b[..., 3] = np.clip((b[..., 3] - TH) / (236.0 - TH), 0, 1) * 255
    return b, (x0, y0, x1, y1)


def gem(p, o):
    import cb_art
    b, _box = cut_soft(p)
    return cb_art.save(cb_art.square(b), GEM_SIZE, o)


def case_box():
    """ケースの 絵の ある 所（もとの 絵の 中：x0, y0, x1, y1）"""
    return cut_soft(os.path.join(SRC, CASE), pad=0)[1]


def case(p, o):
    import cb_art
    b, (x0, y0, x1, y1) = cut_soft(p, pad=0)
    return cb_art.save(b, (CASE_W, round(CASE_W * (y1 - y0) / (x1 - x0))), o)


def token(size):
    def f(p, o):
        import cb_art
        return cb_art.save(cb_art.card(p)[0], size, o)
    return f


def slots_css():
    """アプリ（cb_app.js の GEM_SLOT）に 書く 数：くぼみの 四角を 切り出した ケースの 中の 割合（%：左・上・幅・高さ）"""
    x0, y0, x1, y1 = case_box(); w, h = x1 - x0, y1 - y0
    return [tuple(round(v, 2) for v in ((a - x0) / w * 100, (b - y0) / h * 100, (c - a) / w * 100, (d - b) / h * 100)) for a, b, c, d in CASE_SLOTS]


def jobs():
    """作る もの（cb_art.plan() が 使う）：[(できる 名前, もとの 名前, 作る 関数)]"""
    import cb_art
    j = []
    for k in KINDS:
        j.append((f'cb_gm_{k}.webp', f'cb_gem_{k}.png', gem))
    for k in KINDS:
        j.append((f'cb_ct{k}.webp', f'cb_tok_{k}.png', token(cb_art.BIG)))
        j.append((f'cb_st{k}.webp', f'cb_tok_{k}.png', token(cb_art.SMALL)))
    j.append(('cb_gmcase.webp', CASE, case))
    return j


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'slots':
        print(slots_css())
