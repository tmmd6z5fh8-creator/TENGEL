#!/usr/bin/env python3
"""トレーニングセンターの 馬（2段目の 大きさ＝s2）の たてがみの さいごの ふさの 色の 直し
   （第4.168版・まさちゃん 2026/11/14 01:26「二枚目の赤丸の立髪の一部が色がおかしい！直して！」＝ぶちの 馬の たてがみの 根もとの ふさが 白い）

   わけ：s2 の 形（tc_horse_bk_brown_s2.bin：5色とも 同じ 形・同じ 絵の 貼り方）は、たてがみの いちばん うしろの ふさ（き甲の 上の 三角の ふさ）の
     うしろ半分が、色の 絵（tc_c_<色>_s2.webp）で「体の 色」で ぬられて いる（ぬりの さかいが ふさの 面の まん中を ぎざぎざに 横切る）。
     茶・黒・白・肌色は 体と 同じ 色 なので 目立たない が、ぶち（madara）は 体が 白と オレンジ → こい 茶の たてがみの 先だけ 白く 見えた。
     ほかの 大きさ（s1・s3・s4・s5）は さいごの ふさまで たてがみの 色（この 直しは いらない）。
   直し：その ふさの 面（絵の 島 112こ・三角 679まい）の 中の「体の 色で ぬられた 点」を、その 色の 馬の たてがみの 色に ぬり直す。
     ・どの 点か は 茶の 絵で 決める（5色とも ぬりの さかいが 同じ 形）：たてがみの こい 茶（D）から 体の オレンジ（B）への 線の 上で、体の 方へ 15% より 進んだ 点。
       紙の ふちの 白っぽい すじ（線から はなれた 色）は そのまま のこす（ほかの ふさと 同じ 見た目）
     ・ぬる 色＝その 色の 馬の、同じ ふさの もう こい 所の 色（まん中の 値）× 茶の 絵の 明るさの むら（±1割：紙の かげ）
     ・ふさの 面の そと（ほかの 三角の 上）は 1点も かえない
   もとの 絵（ios/tc_assets/tc_c_<色>_s2.webp・tc_horse_bk_<色>_s2.json）は **読む だけ**（上書きしない・消さない）。
   新しく 作る もの：tc_c_<色>_s2v2.webp（にごらない 形＝lossless：アプリに 入れる 軽い 版は lite_assets.py が ほかの 絵と 同じ 画質で 作る）と
     tc_horse_bk_<色>_s2v2.json（絵の 名前 だけ かえた もの。形 .bin と 法線の 絵は 今までの ものを 指す）。アプリは …_s2v2 を 読む（tc/tc_app.js の HFIX）・
     前の …_s2.json と tc_c_<色>_s2.webp は アプリに 入れない（assets_dir.superseded）

   使い方：python3 kisekae/tc/mane_fix.py [出す フォルダ（なければ ios/tc_assets）] [--check]
     同じ 入力からは いつも 同じ ファイルが できる。出す 先に もう ある ときは 中身が 同じか たしかめる だけ（ちがえば 止まる：上書きしない）。--check は 作らないで くらべる だけ
     作った あと：python3 kisekae/lite_assets.py（アプリに 入れる 軽い 版を 作り直す）
"""
import io, json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import assets_dir

STAGE = 2
COLORS = ('brown', 'black', 'white', 'hada', 'madara')
SUF = 'v2'                                              # 新しい ファイルの 名前の おわり（tc_c_<色>_s2v2.webp・tc_horse_bk_<色>_s2v2.json）
BOX = ((0.05, 1.615, -0.21), (0.34, 1.85, 0.10))        # さいごの ふさが 入る 箱（形の 座標：x＝前・y＝上・z＝横）。この 中に ぜんぶ 入る 島 だけ えらぶ
WANT = dict(islands=112, tris=679)                      # えらばれる はずの 数（形が かわったら 止める）
T0, R0, RH, GROW, PAD = 0.15, 48.0, 70.0, 1, 3          # 体の 方へ 進んだ 割合の しきい・線からの はなれ（体の 色と 見る 限り／白い すじと 見る 限り）・広げる 点の 数・島の まわりへ 広げる 点の 数


def load(color, root):
    m = json.load(open(os.path.join(root, f'tc_horse_bk_{color}_s{STAGE}.json'), encoding='utf8'))
    raw = open(os.path.join(root, m.get('bin') or f'tc_horse_bk_{color}_s{STAGE}.bin'), 'rb').read()
    assert raw[:4] != b'TGIZ' and not m.get('idx32'), 'もとの 形（ios/tc_assets）を 読む こと'
    L, nv = m['layout'], m['v']
    pos = np.frombuffer(raw, '<f4', nv * 3, L['pos'][0]).reshape(nv, 3).astype(np.float64)
    uv = np.frombuffer(raw, '<u2', nv * 2, L['uv'][0]).reshape(nv, 2).astype(np.float64) / 65535.0
    idx = np.frombuffer(raw, '<u2', m['i'], L['idx'][0]).reshape(-1, 3).astype(np.int64)
    tex = np.asarray(Image.open(os.path.join(root, m['tex'])).convert('RGB')).astype(np.float64)
    return m, pos, uv, idx, tex


def islands(pos, uv, idx):
    """絵の 島（絵の 上で つながって いる 三角の かたまり）の 番号（三角ごと）"""
    _, vid = np.unique(np.round(pos * 5000).astype(np.int64), axis=0, return_inverse=True)
    _, uid = np.unique(np.c_[np.round(uv * 65535).astype(np.int64), vid], axis=0, return_inverse=True)
    f = uid[idx]; n = int(uid.max()) + 1
    g = coo_matrix((np.ones(len(f) * 3), (np.r_[f[:, 0], f[:, 1], f[:, 2]], np.r_[f[:, 1], f[:, 2], f[:, 0]])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    return lab[f[:, 0]]


def raster_uv(uv, idx, tris, W, H):
    """三角（番号の ならび）を 絵の 上に ぬった 面（True）。ふちは 少し 広く（となりの 点と まざる 分）"""
    m = np.zeros((H, W), bool)
    for t in tris:
        p = uv[idx[t]] * [W, H]
        x0, x1 = int(max(0, np.floor(p[:, 0].min() - 1))), int(min(W - 1, np.ceil(p[:, 0].max() + 1)))
        y0, y1 = int(max(0, np.floor(p[:, 1].min() - 1))), int(min(H - 1, np.ceil(p[:, 1].max() + 1)))
        d = (p[1, 1] - p[2, 1]) * (p[0, 0] - p[2, 0]) + (p[2, 0] - p[1, 0]) * (p[0, 1] - p[2, 1])
        if abs(d) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((p[1, 1] - p[2, 1]) * (gx - p[2, 0]) + (p[2, 0] - p[1, 0]) * (gy - p[2, 1])) / d
        w1 = ((p[2, 1] - p[0, 1]) * (gx - p[2, 0]) + (p[0, 0] - p[2, 0]) * (gy - p[2, 1])) / d
        e = -0.75 / max(1.0, np.sqrt(abs(d)))
        m[y0:y1 + 1, x0:x1 + 1] |= (w0 >= e) & (w1 >= e) & (1 - w0 - w1 >= e)
    return m


def plan(root):
    """茶の 形と 絵から：ぬり直す 重み（w：0〜1）・明るさの むら（s）・ふさの 面（mT）・たてがみの 色を 読む 所（ref）"""
    _m, pos, uv, idx, tb = load('brown', root)
    H, W = tb.shape[:2]
    isl = islands(pos, uv, idx)
    tv = pos[idx]; inside = ((tv >= np.array(BOX[0])) & (tv <= np.array(BOX[1]))).all(axis=(1, 2))
    T = [i for i in np.unique(isl[inside]) if inside[isl == i].all()]
    sel = np.isin(isl, T)
    got = dict(islands=len(T), tris=int(sel.sum()))
    assert got == WANT, f'さいごの ふさの 面の 数が ちがう（形が かわった？）：{got}'
    mT = raster_uv(uv, idx, np.where(sel)[0], W, H); mO = raster_uv(uv, idx, np.where(~sel)[0], W, H)
    assert not (mT & mO).any(), 'ふさの 面が ほかの 三角と 絵の 上で 重なって いる'
    mask = mT | (ndimage.binary_dilation(mT, iterations=PAD) & ~mO)
    V = tb.max(2); sat = (V - tb.min(2)) / np.maximum(V, 1)
    D = np.median(tb[mT & (V < 95)], axis=0); B = np.median(tb[mT & (V > 150) & (sat > 0.5)], axis=0)      # 茶の 絵の たてがみの 色・体の 色
    ax = B - D; t = np.clip(((tb - D) @ ax) / float(ax @ ax), 0, 1)
    res = np.linalg.norm(tb - (D + t[..., None] * ax), axis=2)
    core = (t > T0) & (res < R0) & mask; hi = (res >= RH) & (V > 120)
    body = core.copy()
    for _ in range(GROW):
        body = (ndimage.binary_dilation(body) & mask & ~hi) | body
    w = ndimage.uniform_filter(body.astype(np.float64), 3)
    w = np.where(body, 1.0, w) * mask * (~hi)
    Vb = np.median(V[core & (t > 0.9)])
    s = ndimage.uniform_filter(np.where(t > 0.9, np.clip(V / Vb, 0.9, 1.08), 1.0), 5)
    ref = mT & (t < 0.05) & (res < 20)
    return dict(w=w, s=s, mask=mask, mT=mT, ref=ref, info=dict(got, texels=int(mT.sum()), body=int(body.sum()), D=D.round(1).tolist(), B=B.round(1).tolist()))


def fix_tex(tex, P):
    mane = np.median(tex[P['ref']], axis=0)
    new = tex * (1 - P['w'][..., None]) + (mane[None, None, :] * P['s'][..., None]) * P['w'][..., None]
    out = np.clip(np.round(new), 0, 255).astype(np.uint8)
    assert not (np.abs(out.astype(int) - tex.astype(int)).max(2) > 0)[~P['mask']].any(), 'ふさの 面の そとが かわった'
    return out, mane


def webp_bytes(arr):
    b = io.BytesIO(); Image.fromarray(arr).save(b, 'WEBP', lossless=True, quality=100, method=6); return b.getvalue()


def build(root):
    """→ { ファイル名: 中身 }・色ごとの しらべ"""
    P = plan(root); out = {}; rep = {}
    for c in COLORS:
        m, _pos, _uv, _idx, tex = load(c, root)
        arr, mane = fix_tex(tex, P)
        tname = f'tc_c_{c}_s{STAGE}{SUF}.webp'
        data = webp_bytes(arr)
        back = np.asarray(Image.open(io.BytesIO(data)).convert('RGB'))
        assert (back == arr).all(), 'にごらない 形で 書けて いない'
        m2 = dict(m); m2['tex'] = tname; m2['bin'] = m.get('bin') or f'tc_horse_bk_{c}_s{STAGE}.bin'
        out[tname] = data; out[f'tc_horse_bk_{c}_s{STAGE}{SUF}.json'] = json.dumps(m2).encode('utf8')
        ch = np.abs(arr.astype(int) - tex.astype(int)).max(2)
        rep[c] = dict(mane=[round(float(v), 1) for v in mane], changed=int((ch > 2).sum()), bytes=len(data))
    return out, P['info'], rep


def main(argv):
    check = '--check' in argv; args = [a for a in argv if not a.startswith('--')]
    root = assets_dir.master('tc_assets'); dst = args[0] if args else root
    files, info, rep = build(root)
    print('さいごの ふさ：', info)
    for c in COLORS:
        print(f'  {c}: たてがみの 色 {rep[c]["mane"]}・かえた 点 {rep[c]["changed"]}・絵 {rep[c]["bytes"]:,} バイト')
    bad = 0
    for f, data in sorted(files.items()):
        p = os.path.join(dst, f)
        if os.path.isfile(p):
            same = open(p, 'rb').read() == data
            print(f'  {f}: もう ある（{"同じ" if same else "中身が ちがう ※ 上書きしない"}）'); bad += 0 if same else 1
        elif check:
            print(f'  {f}: まだ ない'); bad += 1
        else:
            os.makedirs(dst, exist_ok=True)
            with open(p, 'xb') as fh:
                fh.write(data)
            print(f'  {f}: 作った（{len(data):,} バイト）')
    if bad:
        raise SystemExit(f'※ そろって いない／ちがう ファイルが {bad}こ')
    print('OK')


if __name__ == '__main__':
    main(sys.argv[1:])
