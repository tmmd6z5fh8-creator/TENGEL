"""星座・ペガサスの 壁紙：馬を まさちゃんの 絵（星を むすんだ ペガサス：紫に 光る 線と 星）に する
   （第4.160版・まさちゃん 2026/11/12 14:31「星座の馬、一枚目の写真の馬を使用して！」）
   python3 flat/pegasus_art.py <まさちゃんの 絵（PNG・すき通し）> <出す フォルダ>            … 作って 見る だけ（手元の 絵の フォルダと 台帳は さわらない）
   python3 flat/pegasus_art.py <まさちゃんの 絵> <出す フォルダ> --install                  … 手元の 絵の フォルダ（ios/kisekae_blobs）へ 足して、台帳（stars_blobs.json・stars_pts.json・blobs20.json の stars）を 書きかえる
   作る もの
     stars_sky.webp … 夜空・天の川・三日月 だけ（1170×480＝画面の 3倍。前の 絵 flat/pegasus_banner.py と 同じ 夜空：780×320 で 作って 1.5倍に のばし、三日月 だけ 3倍の 細かさで 描く）。
                      うしろの 小さい 星 700こ は 描かない（ページの SVG が 流す：stars_wall.py）・前の ペガサス（コードで 描いた 形）も 描かない
     stars_peg.webp … まさちゃんの ペガサス（すき通し・画面の 3倍）。絵の まわりの ごく うすい もや（すき通し 5/255 以下）は 消す。余白を 切って、壁紙の 中の 高さ PEG_H pt に 合わせる
     stars_pts.json … 壁紙の 動きの 位置（780×320 の 座標＝ページの SVG の viewBox）：
                      size・bg（うしろの 星：前と 同じ 700こ）・moon（前と 同じ）・peg（ペガサスの 絵を 置く 箱：左・上・幅・高さ pt）・
                      con（明るい 星：かわるがわる きらっと 光る）・dots（小さい 星：光が ぐるっと 走る 順＝まん中の まわりの 角度の 順）・
                      spine（鼻の頭 → 頭 → 首 → 背中 → おしり → しっぽの先 の 道すじ：8秒に 1回の キラキラ）
     stars_still.webp … 止まった 絵（780×320：着せ替えの 一覧の 小さい 絵。夜空＋うしろの 星＋三日月＋ペガサス）→ blobs20.json の stars
     preview.png    … 見る 用（うしろの 星も 描いた 1170×480）
   星の 場所は 絵から 見つける（白い 芯の ある 丸い 光：線の 上の 明るさより 目立つ 所）。道すじは 下の SPINE（もとの 絵の 画素）に いちばん 近い 星を つなぐ
   ・もとの 絵（まさちゃんの PNG）と できた 絵は リポジトリに 入れない（ios/kisekae_blobs/ は .gitignore）。**前の 絵は 消さない・上書きしない**（同じ 名前＝同じ 中身）"""
import hashlib, json, os, sys
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
BLOB_DIR = os.environ.get('KISEKAE_ASSETS') or os.path.join(os.path.dirname(os.path.abspath(K)), 'ios', 'kisekae_blobs')
W, Hh, S3 = 780, 320, 1.5                 # 位置の 座標（前と 同じ）・絵は その 1.5倍（＝画面 390×160pt の 3倍）
PEG_H, PEG_CX, PEG_CY = 146.0, 193.0, 80.0   # ペガサスの 高さ・まん中（pt）。右上の 三日月（335〜365pt）に かからない
A_CUT = 5                                  # これ 以下の すき通しは 0（まわりの ごく うすい もや）
N_CON, N_BIG = 21, 8                       # 明るい 星の 数（前と 同じ 21こ）・その うち 大きい きらめきの 数
# 道すじ（もとの 絵の 画素：鼻の頭 → ほほ → ひたい → 首の 上 → 肩の 大きい 星 → 背中 → おしり → しっぽ → しっぽの先）
SPINE = ((1363, 400), (1311, 330), (1265, 313), (1173, 310), (1094, 368), (1052, 425), (893, 482), (715, 476), (615, 482), (562, 498), (470, 566), (403, 580), (321, 546), (258, 543), (211, 561), (190, 585))


def sky():
    """夜空・天の川・三日月（1170×480・0〜1）。前の 絵（pegasus_banner.py）と 同じ 作り"""
    sys.path.insert(0, os.path.join(K, 'r3d')); sys.path.insert(0, K)
    from style2d import grad_v, hexc, soft_circle, blur, over
    from paint import fbm, warp
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    img = grad_v(Hh, W, [(0, '#070A24'), (0.6, '#1B1546'), (1, '#2D1B5A')])
    band = np.exp(-(((yy - (220 - xx * 0.28)) / 60) ** 2))
    neb = warp(fbm(Hh, W, 70, 5, seed=3), (fbm(Hh, W, 120, 3, seed=4) - .5) * 60, (fbm(Hh, W, 120, 3, seed=5) - .5) * 30)
    img = img + (band * neb ** 2)[..., None] * hexc('#9C7BFF') * 0.45 + (band * neb ** 4)[..., None] * hexc('#FFD6F2') * 0.35
    W3, H3 = int(W * S3), int(Hh * S3)
    img = cv2.resize(np.clip(img, 0, 1).astype(np.float32), (W3, H3), interpolation=cv2.INTER_CUBIC)
    MOON = ((700, 58, 30), (712, 50, 27))       # 三日月＝大きい円から小さい円をぬいた形（前と 同じ 場所）
    m3 = [tuple(v * S3 for v in c) for c in MOON]
    moon = soft_circle(H3, W3, *m3[0], 1.0) - soft_circle(H3, W3, *m3[1], 1.0)
    img = img + blur(np.clip(moon, 0, 1), 10 * S3)[..., None] * hexc('#FFE9A8') * 0.4
    img = over(img, hexc('#FFF2C4'), np.clip(moon, 0, 1))
    return np.clip(img, 0, 1), [list(m) for m in MOON]


def still(bg, peg, box):
    """止まった 絵（780×320・0〜1）：夜空・天の川＋うしろの 星（1画素）＋三日月（前の 止まった 絵 pegasus_banner.py と 同じ 作り）＋ペガサス（3倍の 絵を 2倍に）"""
    sys.path.insert(0, os.path.join(K, 'r3d')); sys.path.insert(0, K)
    from style2d import grad_v, hexc, soft_circle, blur, over
    from paint import fbm, warp
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    img = grad_v(Hh, W, [(0, '#070A24'), (0.6, '#1B1546'), (1, '#2D1B5A')])
    band = np.exp(-(((yy - (220 - xx * 0.28)) / 60) ** 2))
    neb = warp(fbm(Hh, W, 70, 5, seed=3), (fbm(Hh, W, 120, 3, seed=4) - .5) * 60, (fbm(Hh, W, 120, 3, seed=5) - .5) * 30)
    img = img + (band * neb ** 2)[..., None] * hexc('#9C7BFF') * 0.45 + (band * neb ** 4)[..., None] * hexc('#FFD6F2') * 0.35
    for x, y, v in bg:
        img[int(y), int(x)] = np.minimum(1, img[int(y), int(x)] + v)
    MOON = ((700, 58, 30), (712, 50, 27))
    moon = soft_circle(Hh, W, *MOON[0], 1.0) - soft_circle(Hh, W, *MOON[1], 1.0)
    img = img + blur(np.clip(moon, 0, 1), 10)[..., None] * hexc('#FFE9A8') * 0.4
    img = np.clip(over(img, hexc('#FFF2C4'), np.clip(moon, 0, 1)), 0, 1).astype(np.float32)
    # ペガサス（3倍 → 2倍：すき通しを かけた 色で 小さく）を 置く
    a = peg.astype(np.float32) / 255.0; pm = np.dstack([a[..., :3] * a[..., 3:4], a[..., 3]])
    w2, h2 = int(round(box[2] * 2)), int(round(box[3] * 2))
    pm = np.dstack([cv2.resize(pm[..., i], (w2, h2), interpolation=cv2.INTER_AREA) for i in range(4)])
    L, T = int(round(box[0] * 2)), int(round(box[1] * 2))
    x0, y0, x1, y1 = max(0, L), max(0, T), min(W, L + w2), min(Hh, T + h2)
    q = pm[y0 - T:y1 - T, x0 - L:x1 - L]
    img[y0:y1, x0:x1] = q[..., :3] + img[y0:y1, x0:x1] * (1 - q[..., 3:4])
    return np.clip(img, 0, 1)


def find_stars(a):
    """絵の 中の 星（白い 芯の ある 丸い 光）→ [{x, y, s（光の 大きさ）}]（もとの 絵の 画素）。線の 上の 明るさより 目立つ 所 だけ・近い もの は 1つに"""
    al = a[..., 3] / 255.0; rgb = a[..., :3]
    lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) / 255.0 * al
    pk = cv2.GaussianBlur(lum, (0, 0), 2.0) - 0.6 * cv2.GaussianBlur(lum, (0, 0), 9.0)
    mx = cv2.dilate(pk, np.ones((15, 15), np.uint8))
    ys, xs = np.nonzero((pk == mx) & (pk > 0.16))
    c = []
    for y, x in zip(ys, xs):
        r = 16; s = float(lum[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1].sum())
        if pk[y, x] >= 0.5 or s >= 400:
            c.append(dict(x=int(x), y=int(y), s=s))
    c.sort(key=lambda q: -q['s'])
    keep = []
    for q in c:
        rr = 40 if keep and q['s'] < 0.75 * keep[0]['s'] and (q['x'] - keep[0]['x']) ** 2 + (q['y'] - keep[0]['y']) ** 2 < 40 ** 2 else 18      # いちばん 大きい 星の 光の 中の 山は 星では ない
        if all((q['x'] - k['x']) ** 2 + (q['y'] - k['y']) ** 2 > rr ** 2 for k in keep):
            keep.append(q)
    return keep


def peg_layer(src):
    """→ (絵〈RGBA uint8・画面の 3倍〉, 置く 箱〈左・上・幅・高さ pt〉, 星〈780×320 の 座標：x, y, s〉, もとの 絵 → 座標の 係数)"""
    a = np.array(Image.open(src).convert('RGBA')).astype(np.float32)
    al = a[..., 3]
    al = np.where(al <= A_CUT, 0, (al - A_CUT) * (255.0 / (255 - A_CUT)))          # ごく うすい もやを 消す（なめらかに 0 へ）
    ys, xs = np.nonzero(al > 8)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    k = PEG_H / (y1 - y0)                                                           # pt ÷ もとの 絵の 画素
    pad = 10                                                                        # まわりの 光の ぶん（もとの 絵の 画素）
    bx0, by0, bx1, by1 = max(0, x0 - pad), max(0, y0 - pad), min(a.shape[1], x1 + pad), min(a.shape[0], y1 + pad)
    left = PEG_CX - (x0 + x1) / 2 * k + bx0 * k; top = PEG_CY - (y0 + y1) / 2 * k + by0 * k
    wpt, hpt = (bx1 - bx0) * k, (by1 - by0) * k
    ow, oh = int(round(wpt * 3)), int(round(hpt * 3))
    crop = np.dstack([a[by0:by1, bx0:bx1, :3], al[by0:by1, bx0:bx1]])
    pm = np.dstack([crop[..., :3] * (crop[..., 3:4] / 255.0), crop[..., 3]])       # すき通しを かけた 色で 小さく する（ふちに 外の 色が まざらない）
    ch = [cv2.resize(pm[..., i], (ow, oh), interpolation=cv2.INTER_AREA) for i in range(4)]
    a2 = np.clip(ch[3], 0, 255); rgb = np.dstack(ch[:3]) / np.maximum(a2[..., None] / 255.0, 1e-3)
    out = np.dstack([np.clip(rgb + 0.5, 0, 255), a2 + 0.5]).astype(np.uint8); out[out[..., 3] == 0] = 0
    to_xy = lambda x, y: ((left + (x - bx0) * k) * 2, (top + (y - by0) * k) * 2)   # もとの 絵の 画素 → 780×320 の 座標（1pt＝2）
    stars = [dict(zip(('x', 'y'), to_xy(q['x'], q['y'])), s=q['s'], sx=q['x'], sy=q['y']) for q in find_stars(a)]
    return out, [round(left, 2), round(top, 2), round(wpt, 2), round(hpt, 2)], stars, to_xy


def points(stars, to_xy, old):
    """位置の 台帳。old＝前の 台帳（うしろの 星 bg は そのまま 使う）"""
    by = sorted(stars, key=lambda q: -q['s'])
    con = by[:N_CON]; dots = by[N_CON:]
    cx = sum(q['x'] for q in stars) / len(stars); cy = sum(q['y'] for q in stars) / len(stars)
    dots.sort(key=lambda q: np.arctan2(q['y'] - cy, q['x'] - cx))                   # 光が ぐるっと 走る 順（まん中の まわり）
    sp = []
    for sx, sy in SPINE:                                                            # 道すじ：いちばん 近い 星へ
        q = min(stars, key=lambda t: (t['sx'] - sx) ** 2 + (t['sy'] - sy) ** 2)
        assert (q['sx'] - sx) ** 2 + (q['sy'] - sy) ** 2 < 30 ** 2, ('道すじの 星が 見つからない', sx, sy, q)
        p = [round(q['x'], 2), round(q['y'], 2)]
        if not sp or sp[-1] != p: sp.append(p)
    return dict(size=[W, Hh], bg=old['bg'], moon=old['moon'],
                con=[[round(q['x'], 2), round(q['y'], 2), int(i < N_BIG)] for i, q in enumerate(con)],
                dots=[[round(q['x'], 2), round(q['y'], 2), int(i % 3 == 0)] for i, q in enumerate(dots)], spine=sp)


def webp(img, **kw):
    import io
    b = io.BytesIO(); img.save(b, 'WEBP', method=6, **kw); return b.getvalue()


def put(data):
    """絵を 手元の フォルダへ（同じ 名前＝同じ 中身。上書きしない）→ id"""
    bid = hashlib.md5(data).hexdigest(); dst = os.path.join(BLOB_DIR, bid + '.webp')
    if os.path.exists(dst):
        assert open(dst, 'rb').read() == data, dst
    else:
        open(dst, 'wb').write(data)
    return bid


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    old = json.load(open(os.path.join(K, 'stars_pts.json')))
    sk, moon = sky(); assert moon == old['moon'], (moon, old['moon'])
    sky_im = Image.fromarray((sk * 255 + 0.5).astype(np.uint8), 'RGB')
    peg, box, stars, to_xy = peg_layer(src)
    peg_im = Image.fromarray(peg, 'RGBA')
    pts = points(stars, to_xy, old); pts['peg'] = box
    d_sky = webp(sky_im, quality=90); d_peg = webp(peg_im, quality=92, alpha_quality=100, exact=False)
    st_im = Image.fromarray((still(old['bg'], peg, box) * 255 + 0.5).astype(np.uint8), 'RGB'); d_still = webp(st_im, quality=88)
    open(os.path.join(out, 'stars_still.webp'), 'wb').write(d_still)
    back = np.array(Image.open(__import__('io').BytesIO(d_peg)).convert('RGBA')); assert np.array_equal(back[..., 3], peg[..., 3]), 'すき通しが かわった'
    open(os.path.join(out, 'stars_sky.webp'), 'wb').write(d_sky); open(os.path.join(out, 'stars_peg.webp'), 'wb').write(d_peg)
    json.dump(pts, open(os.path.join(out, 'stars_pts.json'), 'w'), separators=(',', ':'))
    # 見る 用：夜空＋うしろの 星＋ペガサス（3倍）
    pv = sk.copy()
    for x, y, v in old['bg']:
        xi, yi = int(x * S3), int(y * S3); pv[yi:yi + 2, xi:xi + 2] = np.minimum(1, pv[yi:yi + 2, xi:xi + 2] + v)
    pvi = Image.fromarray((pv * 255 + 0.5).astype(np.uint8), 'RGB').convert('RGBA')
    L, T = int(round(box[0] * 3)), int(round(box[1] * 3)); pvi.alpha_composite(peg_im, (L, T)); pvi.convert('RGB').save(os.path.join(out, 'preview.png'))
    print('夜空', sky_im.size, len(d_sky), 'B ／ ペガサス', peg_im.size, len(d_peg), 'B・置く 箱（pt）', box, '／ 星', len(stars), '（明るい', len(pts['con']), '・小さい', len(pts['dots']), '）・道すじ', len(pts['spine']), '点')
    if '--install' in sys.argv:
        bp = os.path.join(K, 'stars_blobs.json'); blobs = json.load(open(bp))
        was = dict(blobs); blobs['base'] = put(d_sky); blobs['peg'] = put(d_peg)
        json.dump(blobs, open(bp, 'w')); json.dump(pts, open(os.path.join(K, 'stars_pts.json'), 'w'), separators=(',', ':'))
        print('台帳', was, '→', blobs, '（前の 絵は のこる：', os.path.exists(os.path.join(BLOB_DIR, was['base'] + '.webp')), '）')
        b2 = os.path.join(K, 'blobs20.json'); txt = open(b2, encoding='utf8').read(); b20 = json.loads(txt); was20 = b20['stars']; new20 = put(d_still)
        if new20 != was20:                       # 台帳の ならびと 書き方は かえない（その 行の id だけ）
            assert txt.count('"stars": "%s"' % was20) == 1
            open(b2, 'w', encoding='utf8').write(txt.replace('"stars": "%s"' % was20, '"stars": "%s"' % new20))
        print('止まった 絵（一覧の 小さい 絵）', was20, '→', new20, st_im.size, len(d_still), 'B（前の 絵は のこる：', os.path.exists(os.path.join(BLOB_DIR, was20 + '.webp')), '）')
