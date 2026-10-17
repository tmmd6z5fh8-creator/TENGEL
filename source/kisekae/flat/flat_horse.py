"""ぺたっとした色＋太い線の馬（SVG）を作る道具
   - 形は点の列 → なめらかな線（Catmull-Rom）で作る。角にしたい点は sharp に入れる
   - 体・首・頭・手前の足は「線を先に太く → 色を上に」で、外側だけに線が出るようにする（つなぎ目に線が出ない）
   - すべて一から作った形（写真や絵をなぞっていない）"""
import math

import numpy as np


def _p(p):
    return f'{p[0]:.1f},{p[1]:.1f}'


def smooth(pts, closed=True, sharp=(), t=1.0):
    """点をなめらかにつなぐ SVG の d。sharp の番号の点は角になる"""
    P = [np.asarray(p, float) for p in pts]
    n = len(P)
    sharp = set(sharp)
    d = 'M' + _p(P[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0, p1 = P[(i - 1) % n], P[i]
        p2, p3 = P[(i + 1) % n], P[(i + 2) % n]
        if not closed:
            p0 = P[i - 1] if i > 0 else P[i]
            p3 = P[i + 2] if i + 2 < n else P[(i + 1)]
        c1 = p1 if i in sharp else p1 + (p2 - p0) / 6 * t
        c2 = p2 if ((i + 1) % n) in sharp else p2 - (p3 - p1) / 6 * t
        d += f' C{_p(c1)} {_p(c2)} {_p(p2)}'
    return d + (' Z' if closed else '')


def limb(joints, widths):
    """関節の点と太さから、足の形（多角形の点）を作る"""
    J = [np.asarray(j, float) for j in joints]
    L, R = [], []
    for i, j in enumerate(J):
        if i == 0:
            dv = J[1] - J[0]
        elif i == len(J) - 1:
            dv = J[-1] - J[-2]
        else:
            a = (J[i] - J[i - 1]) / np.linalg.norm(J[i] - J[i - 1])
            b = (J[i + 1] - J[i]) / np.linalg.norm(J[i + 1] - J[i])
            dv = a + b
        dv = dv / (np.linalg.norm(dv) + 1e-9)
        nrm = np.array([-dv[1], dv[0]])
        L.append(j + nrm * widths[i] / 2)
        R.append(j - nrm * widths[i] / 2)
    return L + R[::-1]


def along(a, b, t):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a + (b - a) * t


def hoof(knee, toe, w_top, w_bot, h):
    """足の先（ひづめ）：toe の方向に台形"""
    k, t = np.asarray(knee, float), np.asarray(toe, float)
    dv = (t - k) / np.linalg.norm(t - k)
    nrm = np.array([-dv[1], dv[0]])
    top = t - dv * h
    return [top + nrm * w_top / 2, t + nrm * w_bot / 2, t - nrm * w_bot / 2, top - nrm * w_top / 2]


def poly_d(pts):
    return 'M' + ' L'.join(_p(p) for p in pts) + ' Z'


def outlined(ds, fill, line, ow, extra=''):
    """線を先に（太さ2倍）→ 色を上に。ds は d の列"""
    a = ''.join(f'<path d="{d}"/>' for d in ds)
    return (f'<g fill="{line}" stroke="{line}" stroke-width="{ow * 2:.2f}" stroke-linejoin="round" stroke-linecap="round" {extra}>{a}</g>'
            f'<g fill="{fill}" {extra}>{a}</g>')


def shape(d, fill, line, ow, extra=''):
    """ふつうの形（線は形のまわり全部）"""
    return f'<path d="{d}" fill="{fill}" stroke="{line}" stroke-width="{ow:.2f}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def to_png(svg, w, h, path, scale=2):
    """SVG を透明な PNG に（Chromium で描く）"""
    from playwright.sync_api import sync_playwright
    html = (f'<!doctype html><html><head><style>html,body{{margin:0;background:transparent}}svg{{display:block}}</style></head>'
            f'<body>{svg}</body></html>')
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=scale)
        pg.set_content(html)
        pg.screenshot(path=path, omit_background=True, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        b.close()
    return path
