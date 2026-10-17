"""ぺたっとした色のかわいい競走馬（SVG・線なし）：午年・雪・紅葉・海・桜のテーマ用
   - 体・首・頭・手前の足は同じ色でぬって、つなぎ目は見せない（線なし）。奥の足と奥の耳は少し暗い色
   - 頭は大きめ・目は小さなたて長の黒目に白い光・鼻先は明るい色・鼻の穴・小さな口・ほっぺ
   - たてがみはうしろへ流れるとがった房、前髪は2つの房、しっぽは根元から太くなって先が2〜3つに分かれる
   - 頭のベルト（鼻・ほお・ひたい）と、はみの輪・手綱、鞍の下の布（番号）・鞍・腹帯
   - ポーズ：stand（立つ）・walk（手前の前足を上げて歩く）・prance（前足を高く上げる）・gallop（走る）
   SVG は librsvg（OS のライブラリ）で描く：Chromium とちがって、何回描いても1画素もちがわない。
   形はすべて一から作ったオリジナル（参考の絵をなぞっていない）。
   cute_horse(pose, pal) → (SVG の部品, 目印)。座標は右向き・y は下・地面は y=290"""
import math
import numpy as np
from flat_horse import smooth, limb, poly_d

GROUND = 290.0


def V(*a):
    return np.array(a, float)


def dirv(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-9)


def f2(v):
    return f'{v:.2f}'


def mix(c1, c2, k):
    """色 c1 を c2 の上に k の濃さでのせた色（半とうめいを使わない：Chromium で毎回同じ絵になるように）"""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{int(round(x * k + y * (1 - k))):02X}' for x, y in zip(a, b))


def path(d, fill, extra=''):
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def stroke(d, col, w, extra=''):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f2(w)}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def circ(c, r, fill, extra=''):
    return f'<circle cx="{f2(c[0])}" cy="{f2(c[1])}" r="{f2(r)}" fill="{fill}" {extra}/>'


def ell(c, rx, ry, rot, fill, extra=''):
    return f'<ellipse cx="{f2(c[0])}" cy="{f2(c[1])}" rx="{f2(rx)}" ry="{f2(ry)}" transform="rotate({f2(rot)} {f2(c[0])} {f2(c[1])})" fill="{fill}" {extra}/>'


# ---------------- ポーズ（角度は画面の上で：0＝右・90＝下・180＝左） ----------------
POSES = {
    'stand': dict(neck=-60, head=60, tail='hang', plant=('fn', 'ff', 'hn', 'hf'),
                  fore_n=[94, 90, 70], fore_f=[90, 92, 70], hind_n=[124, 80, 70], hind_f=[114, 84, 70]),
    'walk': dict(neck=-52, head=52, tail='sway', plant=('ff', 'hn', 'hf'),
                 fore_n=[50, 124, 150], fore_f=[100, 92, 70], hind_n=[100, 80, 68], hind_f=[124, 96, 74]),
    'prance': dict(neck=-64, head=66, tail='sway', plant=('ff', 'hn', 'hf'),
                   fore_n=[8, 100, 122], fore_f=[96, 90, 70], hind_n=[104, 82, 68], hind_f=[118, 90, 72]),
    'gallop': dict(neck=-34, head=40, tail='fly', plant=(),
                   fore_n=[30, 66, 52], fore_f=[82, 150, 172], hind_n=[150, 142, 128], hind_f=[90, 52, 66]),
}

# 足の長さと太さ（上・ひざ・管の下・球節）
FORE_L = (40.0, 30.0, 11.0)
HIND_L = (44.0, 32.0, 11.0)
FORE_W = (34.0, 21.0, 18.0, 17.0)
HIND_W = (46.0, 23.0, 18.0, 17.0)
HEAD_SC = 1.24                                                    # 頭を大きく（かわいく）
TORSO = [(236, 116), (204, 124), (160, 127), (120, 122), (94, 113), (68, 121), (54, 148), (58, 178), (82, 200), (120, 209),
         (170, 213), (214, 209), (244, 192), (259, 164), (256, 134)]
NECK_BASE = V(238.0, 128.0)
NECK_LEN = 70.0
CREST_BASE = V(224.0, 114.0)
THROAT_BASE = V(260.0, 160.0)
FORE_AT = V(234.0, 184.0)
HIND_AT = V(88.0, 172.0)
FAR_OFF_F = V(12.0, -3.0)
FAR_OFF_H = V(18.0, -4.0)

# 頭の形（u：うなじ→鼻先、w：顔の前（上）がわ）
HEAD = [(-6, -2), (0, 8), (14, 20), (44, 19), (70, 17), (82, 10), (87, -4), (81, -18), (70, -21), (60, -16),
        (42, -22), (24, -32), (6, -30), (-4, -17)]
MUZZLE = [(56, 19), (70, 17), (82, 10), (87, -4), (81, -18), (70, -21), (60, -16), (55, 0)]


def leg_chain(at, angs, lens):
    J = [np.asarray(at, float)]
    for a, L in zip(angs, lens):
        J.append(J[-1] + dirv(a) * L)
    return J


def leg_shapes(J, Wd, hoof_h=11.0):
    """足の形（多角形）・ひざ／球節の丸み・ひづめ（台形）"""
    poly = limb(J, Wd)
    d_last = unit(J[-1] - J[-2])
    nrm = np.array([-d_last[1], d_last[0]])
    toe = J[-1] + d_last * hoof_h
    hw0, hw1 = Wd[-1] * 0.5 + 0.5, Wd[-1] * 0.5 + 2.6
    hoof = [J[-1] + nrm * hw0, toe + nrm * hw1, toe - nrm * hw1, J[-1] - nrm * hw0]
    knees = [(J[1], Wd[1] * 0.58), (J[2], Wd[2] * 0.60)]
    return poly, hoof, knees, toe


def tuft(root, tip, w, bend=0.18, side=1.0):
    """とがった房（根元は丸く、先はとがる・少し曲がる）"""
    root, tip = np.asarray(root, float), np.asarray(tip, float)
    dv = tip - root
    L = np.linalg.norm(dv)
    u = dv / L
    n = np.array([-u[1], u[0]]) * side
    m1 = root + dv * 0.38 + n * (w * 0.55 + L * bend)
    m2 = root + dv * 0.42 - n * (w * 0.45 - L * bend * 0.6)
    pts = [root + n * w * 0.5, m1, tip, m2, root - n * w * 0.5, root - u * w * 0.35]
    return smooth(pts, sharp=(2,))


def lock_d(p0, p1, p2, p3, wmax, w0=None, n=28):
    """房：3次ベジェの中心線と太さ（根元 w0 → ふくらみ wmax → 先は0）→ なめらかな形"""
    p0, p1, p2, p3 = (np.asarray(q, float) for q in (p0, p1, p2, p3))
    t = np.linspace(0, 1, n)[:, None]
    C = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
    tg = np.gradient(C, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    tt = t[:, 0]
    w0 = wmax * 0.55 if w0 is None else w0
    wd = (w0 + (wmax - w0) * np.sin(np.pi * np.clip(tt / 0.6, 0, 1) * 0.5)) * (1 - tt) ** 0.62
    Lp = C + nr * (wd / 2)[:, None]
    Rp = C - nr * (wd / 2)[:, None]
    pts = list(Lp[::3]) + [C[-1]] + list(Rp[::3][::-1])
    k = len(Lp[::3])
    return smooth(pts, sharp=(k,)), C


TAILS = {   # 房ごとに (p1, p2, p3 は根元からのずれ, ふくらみ)
    'hang': [((-24, 2), (-46, 44), (-36, 106), 38), ((-28, 10), (-58, 52), (-60, 96), 28), ((-14, 14), (-28, 62), (-16, 102), 24)],
    'sway': [((-26, -2), (-54, 36), (-58, 100), 38), ((-30, 8), (-68, 42), (-82, 86), 28), ((-16, 14), (-36, 60), (-32, 102), 24)],
    'fly': [((-30, -10), (-74, -6), (-128, 10), 34), ((-30, 0), (-70, 16), (-116, 34), 26), ((-26, -12), (-60, -24), (-104, -16), 22)],
}


def tail_shape(kind, root):
    r = np.asarray(root, float)
    ds, Cs = [], []
    for p1, p2, p3, wm in TAILS[kind]:
        d, C = lock_d(r, r + V(*p1), r + V(*p2), r + V(*p3), wm, w0=14)
        ds.append(d); Cs.append(C)
    return ds, Cs


def cute_horse(pose_name, pal, acc=None, number='1', acc_neck=None):
    """pal: body・shade・muzzle・mane・maneD・hoof・eye・blush・tack・ring・cloth・clothTrim・num・saddle
       acc: 飾り（関数 (marks) → SVG の部品）・acc_neck：首の飾り（たてがみの上、頭の下に描く）。戻り値 (SVG の部品の列, 目印 dict)"""
    P = POSES[pose_name]
    out = []
    body, shade = pal['body'], pal['shade']

    # ---------- 首と頭の位置 ----------
    poll = NECK_BASE + dirv(P['neck']) * NECK_LEN
    u = dirv(P['head'])
    w = np.array([u[1], -u[0]])                                   # 顔の前（上）がわ
    H = lambda a, b: poll + (u * a + w * b) * HEAD_SC
    head_pts = [H(a, b) for a, b in HEAD]

    # ---------- 奥の足（暗い色） ----------
    def leg(at, angs, lens, Wd, col, planted):
        at = np.asarray(at, float)
        if planted:                                               # ひづめが地面にとどくよう、長さを合わせる
            sy = sum(L * math.sin(math.radians(a)) for a, L in zip(angs, lens))
            k = (GROUND - 11.0 - at[1]) / sy
            lens = [L * k for L in lens]
        J = leg_chain(at, angs, lens)
        poly, hoofp, knees, toe = leg_shapes(J, Wd)
        if planted:                                               # 地面に平らなひづめ
            fx = J[-1][0]
            hoofp = [V(fx - Wd[-1] * 0.5 - 0.5, GROUND - 12.5), V(fx + Wd[-1] * 0.5 + 0.5, GROUND - 12.5),
                     V(fx + Wd[-1] * 0.5 + 4.5, GROUND), V(fx - Wd[-1] * 0.5 - 1.5, GROUND)]
            toe = V(fx + 1.5, GROUND)
        s_ = [path(poly_d(poly), col)]
        for c, r in knees:
            s_.append(circ(c, r, col))
        if Wd[0] > 40:                                            # うしろ足：飛節のうしろの出っぱり
            d1 = unit(J[1] - J[0]); d2 = unit(J[2] - J[1])
            bk = unit(d1 - d2)
            s_.append(circ(J[1] + bk * Wd[1] * 0.22, Wd[1] * 0.50, col))
        s_.append(path(smooth(hoofp, sharp=(0, 1, 2, 3), t=0.0), pal['hoof']))
        return s_, J, toe

    pl = P['plant']
    s, Jff, toe_ff = leg(FORE_AT + FAR_OFF_F, P['fore_f'], FORE_L, FORE_W, shade, 'ff' in pl)
    out += s
    s, Jhf, toe_hf = leg(HIND_AT + FAR_OFF_H, P['hind_f'], HIND_L, HIND_W, shade, 'hf' in pl)
    out += s

    # ---------- しっぽ（体のうしろ） ----------
    troot = V(66.0, 126.0)
    tds, tCs = tail_shape(P['tail'], troot)
    for d in tds[1:]:
        out.append(path(d, pal['maneD']))                          # うしろの房（少し暗い）
    out.append(path(tds[0], pal['mane']))
    C0 = tCs[0]
    out.append(stroke(smooth([C0[4], C0[11], C0[18]], closed=False), pal['maneD'], 2.6, 'stroke-opacity=".8"'))   # 毛の流れの線
    tC = tCs[0]

    # ---------- 奥の耳 ----------
    ear_dir = unit(w * 1.0 - u * 0.42)
    def ear(base, col, sc=1.0):
        b0 = base - u * 6 * sc
        b1 = base + u * 6 * sc
        tip = base + ear_dir * 26 * sc
        m0 = (b0 + tip) / 2 - u * 4.5 * sc
        m1 = (b1 + tip) / 2 + u * 4.5 * sc
        return smooth([b0, m0, tip, m1, b1], sharp=(2,))
    out.append(path(ear(H(-2, 10), shade, 0.92), shade))

    # ---------- 体・首・手前の足（同じ色・線なし） ----------
    crest_top = H(0, 8)
    neck_pts = [CREST_BASE, (CREST_BASE + crest_top) / 2 + unit(w - u) * 6 + V(-4, -4), crest_top, H(-6, -2), H(-4, -17),
                (H(-4, -17) + THROAT_BASE) / 2 + V(4, 4), THROAT_BASE, V(236.0, 160.0)]
    out.append(path(smooth(TORSO), body))
    out.append(path(smooth(neck_pts), body))
    s, Jfn, toe_fn = leg(FORE_AT, P['fore_n'], FORE_L, FORE_W, body, 'fn' in pl)
    out += s
    s, Jhn, toe_hn = leg(HIND_AT, P['hind_n'], HIND_L, HIND_W, body, 'hn' in pl)
    out += s

    # ---------- たてがみ（うしろへ流れるとがった房） ----------
    C = [crest_top + u * 2 - w * 1, (CREST_BASE + crest_top) / 2 + unit(w - u) * 3, CREST_BASE + V(4, 6)]
    crest_line = [C[0] + (C[1] - C[0]) * t for t in np.linspace(0, 1, 5)] + [C[1] + (C[2] - C[1]) * t for t in np.linspace(0, 1, 5)[1:]]
    crest_line = np.array(crest_line)
    n_t = 6
    back = unit(CREST_BASE - crest_top)
    for k in range(n_t):
        t = (k + 0.3) / n_t
        i = t * (len(crest_line) - 1)
        i0 = int(i); fr = i - i0
        p = crest_line[i0] + (crest_line[min(i0 + 1, len(crest_line) - 1)] - crest_line[i0]) * fr
        out_n = unit(np.array([back[1], -back[0]]))                  # 首の外がわ（上）
        if out_n[1] > 0:
            out_n = -out_n
        L = 30 - 6 * abs(t - 0.4)
        tip = p + back * L * 0.86 + out_n * L * (0.42 if pose_name != 'gallop' else 0.30)
        out.append(path(tuft(p - out_n * 4, tip, 17, bend=0.14, side=-1), pal['mane']))
    # 房のあいだの影の線
    out.append(stroke(smooth([crest_line[2] + V(2, 4), crest_line[5] + V(2, 5), crest_line[8] + V(2, 4)], closed=False), pal['maneD'], 2.6, 'stroke-opacity=".55"'))

    # ---------- 首の飾り（たてがみの上・頭の下） ----------
    ax = dirv(P['neck'])
    n_crest = np.array([ax[1], -ax[0]])                            # 首の上（たてがみ）がわ
    def collar(t, hw_c=20.0, hw_t=22.0):
        c = NECK_BASE + ax * NECK_LEN * t
        return c + n_crest * hw_c, c - n_crest * hw_t, ax
    if acc_neck is not None:
        out += acc_neck(dict(collar=collar, crest=crest_line, throat=THROAT_BASE, neck_base=CREST_BASE))

    # ---------- 頭・鼻先・前髪 ----------
    out.append(path(smooth(head_pts), body))
    out.append(path(smooth([H(a, b) for a, b in MUZZLE]), pal['muzzle']))
    fb = H(4, 14)
    out.append(path(tuft(fb, H(26, 22), 14, bend=0.10, side=1), pal['mane']))
    out.append(path(tuft(fb + u * 2, H(20, 12), 11, bend=0.08, side=-1), pal['maneD']))

    # ---------- 手前の耳 ----------
    out.append(path(ear(H(5, 13), body), body))
    ein = H(5, 13) + ear_dir * 6
    out.append(path(smooth([ein - u * 2.8, ein + ear_dir * 13 - u * 0.5, ein + u * 2.8], sharp=(1,)), pal['shade']))

    # ---------- 顔 ----------
    eye_c = H(24, 7)
    ang = math.degrees(math.atan2(u[1], u[0]))
    out.append(ell(eye_c, 4.2, 6.0, ang, pal['eye']))
    out.append(circ(eye_c + w * 2.4 - u * 1.0, 1.7, '#FFFFFF'))
    out.append(ell(H(40, -10), 8.0, 5.0, ang, mix(pal['blush'], body, 0.55)))           # ほっぺ（色はまぜておく）
    nost = H(76, 3)
    out.append(ell(nost, 2.6, 4.2, ang + 20, mix(pal['eye'], pal['muzzle'], 0.75)))
    out.append(stroke(smooth([H(66, -13), H(73, -15.5), H(80, -13)], closed=False), mix(pal['eye'], pal['muzzle'], 0.7), 1.8))

    # ---------- 頭のベルト・はみ・手綱 ----------
    tack, tw = pal['tack'], 3.4
    ring = H(66, -14)
    out.append(stroke(smooth([H(4, 15), H(30, -2), ring + u * 0.0], closed=False), tack, tw))           # ほお
    out.append(stroke(smooth([H(60, 19), H(60, 4), H(60, -15)], closed=False), tack, tw))               # 鼻
    out.append(stroke(smooth([H(8, 16), H(13, 19.5)], closed=False), tack, tw))                          # ひたい
    out.append(stroke(smooth([H(4, 15), H(0, -4), H(-1, -18)], closed=False), tack, tw * 0.9))           # のど
    saddle_front = V(190.0, 118.0)
    sag = (ring + saddle_front) / 2 + V(0, 18)
    out.append(stroke(smooth([ring, sag, saddle_front], closed=False), tack, 2.6))                       # 手綱
    out.append(circ(ring, 4.6, 'none', f'stroke="{pal["ring"]}" stroke-width="2.4"'))

    # ---------- 鞍の下の布（番号）・鞍・腹帯 ----------
    cx0, cx1, cy0, cy1 = 126.0, 200.0, 116.0, 178.0
    cloth = f'M{cx0 + 9},{cy0} H{cx1 - 9} Q{cx1},{cy0} {cx1},{cy0 + 9} V{cy1 - 9} Q{cx1},{cy1} {cx1 - 9},{cy1} H{cx0 + 9} Q{cx0},{cy1} {cx0},{cy1 - 9} V{cy0 + 9} Q{cx0},{cy0} {cx0 + 9},{cy0} Z'
    out.append(f'<defs><clipPath id="torsoclip"><path d="{smooth(TORSO)}"/></clipPath></defs>')
    out.append(f'<g clip-path="url(#torsoclip)">')
    out.append(path(cloth, pal['cloth']))
    out.append(stroke(f'M{cx0 + 2},{cy1 - 6} H{cx1 - 2}', pal['clothTrim'], 4.2))
    out.append(stroke(f'M{cx0 + 5},{cy0 + 4} V{cy1 - 6} M{cx1 - 5},{cy0 + 4} V{cy1 - 6}', pal['clothTrim'], 2.4))
    out.append('</g>')
    seat = [(140, 124), (138, 110), (146, 112), (162, 117), (180, 115), (192, 104), (198, 112), (196, 126), (168, 130)]
    out.append(path(smooth(seat, sharp=(1, 5)), pal['saddle']))
    out.append(path(f'M186,124 H196 L{196 + 2},{204} H{188 - 2} Z', pal['saddle']))                     # 腹帯
    marks = dict(cloth_c=V((cx0 + cx1) / 2 - 2, (cy0 + cy1) / 2 + 6), cloth_h=cy1 - cy0, poll=poll, u=u, w=w, eye=eye_c, ring=ring, collar=collar,
                 muzzle=H(87, -4), nostril=nost, hooves=[toe_fn, toe_ff, toe_hn, toe_hf], tail=tC, crest=crest_line,
                 neck_top=crest_top, neck_base=CREST_BASE, throat=THROAT_BASE, H=H, head_pts=head_pts)
    if acc is not None:
        out += acc(marks)
    return out, marks


def number_svg(marks, T, num, fill, size=30):
    """番号（左右をかえした馬でも、字は左右をかえさない）。T：目印の点 → 絵の座標。
       字のまんなかを布のまんなかに（数字の高さは字の大きさの約0.72倍なので、下の線は 0.36 倍下）"""
    c = T(marks['cloth_c'])
    return (f'<text x="{f2(c[0])}" y="{f2(c[1] + size * 0.36)}" font-family="Noto Sans CJK JP" font-weight="900" '
            f'font-size="{f2(size)}" fill="{fill}" text-anchor="middle">{num}</text>')


class Place:
    """右向きの目印の座標 → 絵の座標（大きさ・左右・位置）"""

    def __init__(self, x, y, sc, facing='right', width=320.0):
        self.x, self.y, self.sc, self.facing, self.width = x, y, sc, facing, width

    def __call__(self, p):
        p = np.asarray(p, float)
        px = p[0] if self.facing == 'right' else self.width - p[0]
        return np.array([self.x + px * self.sc, self.y + p[1] * self.sc])

    def g(self, parts):
        if self.facing == 'right':
            tr = f'translate({f2(self.x)} {f2(self.y)}) scale({f2(self.sc)})'
        else:
            tr = f'translate({f2(self.x + self.width * self.sc)} {f2(self.y)}) scale({f2(-self.sc)} {f2(self.sc)})'
        return f'<g transform="{tr}">' + ''.join(parts) + '</g>'


# ---------------- SVG を絵にする（librsvg＋cairo：いつも同じ絵になる） ----------------
_RS = {}


def _rsvg():
    """librsvg と cairo（どちらも OS に入っているライブラリ）を ctypes で使う"""
    if _RS:
        return _RS
    import ctypes
    rs = ctypes.CDLL('librsvg-2.so.2')
    ca = ctypes.CDLL('libcairo.so.2')
    go = ctypes.CDLL('libgobject-2.0.so.0')

    class Rect(ctypes.Structure):
        _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double), ('width', ctypes.c_double), ('height', ctypes.c_double)]

    vp = ctypes.c_void_p
    rs.rsvg_handle_new_from_data.restype = vp
    rs.rsvg_handle_new_from_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t, vp]
    rs.rsvg_handle_render_document.restype = ctypes.c_int
    rs.rsvg_handle_render_document.argtypes = [vp, vp, ctypes.POINTER(Rect), vp]
    ca.cairo_image_surface_create.restype = vp
    ca.cairo_image_surface_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    ca.cairo_create.restype = vp
    ca.cairo_create.argtypes = [vp]
    ca.cairo_image_surface_get_data.restype = ctypes.POINTER(ctypes.c_ubyte)
    ca.cairo_image_surface_get_data.argtypes = [vp]
    ca.cairo_image_surface_get_stride.restype = ctypes.c_int
    ca.cairo_image_surface_get_stride.argtypes = [vp]
    for f in ('cairo_surface_flush', 'cairo_destroy', 'cairo_surface_destroy'):
        getattr(ca, f).argtypes = [vp]
    go.g_object_unref.argtypes = [vp]
    _RS.update(rs=rs, ca=ca, go=go, Rect=Rect, ct=ctypes)
    return _RS


def svg_rgba(svg, w, h):
    """SVG の文字列 → (h, w, 4) の premultiplied RGBA（0〜1）"""
    L = _rsvg()
    rs, ca, go, ctypes = L['rs'], L['ca'], L['go'], L['ct']
    data = svg.encode('utf-8')
    hd = rs.rsvg_handle_new_from_data(data, len(data), None)
    if not hd:
        raise RuntimeError('librsvg could not read the SVG')
    surf = ca.cairo_image_surface_create(0, w, h)                       # ARGB32
    cr = ca.cairo_create(surf)
    rect = L['Rect'](0.0, 0.0, float(w), float(h))
    ok = rs.rsvg_handle_render_document(hd, cr, ctypes.byref(rect), None)
    ca.cairo_surface_flush(surf)
    stride = ca.cairo_image_surface_get_stride(surf)
    buf = ca.cairo_image_surface_get_data(surf)
    arr = np.ctypeslib.as_array(buf, shape=(h, stride)).copy()
    ca.cairo_destroy(cr)
    ca.cairo_surface_destroy(surf)
    go.g_object_unref(hd)
    if not ok:
        raise RuntimeError('librsvg could not draw the SVG')
    bgra = arr[:, :w * 4].reshape(h, w, 4).astype(np.float32) / 255
    return bgra[..., [2, 1, 0, 3]]


def svg_layer(inner, W, Hh, scale=3, tmpname=None):
    """SVG の中身 → 1倍の (色, 不透明度)（3倍で描いて、色×透明度のまま縮める）"""
    import cv2
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">{inner}</svg>'
    pm = svg_rgba(svg, W * scale, Hh * scale)
    pm = cv2.resize(pm, (W, Hh), interpolation=cv2.INTER_AREA)
    al = pm[..., 3]
    rgb = np.where(al[..., None] > 1e-4, pm[..., :3] / np.maximum(al, 1e-4)[..., None], 0)
    return np.clip(rgb, 0, 1).astype(np.float32), np.clip(al, 0, 1).astype(np.float32)
