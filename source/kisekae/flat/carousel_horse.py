"""メリーゴーランドの木馬（ぺたっとした色＋太い線・右向き・前足を上げた形）
   形はすべて一から作ったオリジナル。色・飾りはテーマ（パステル×金）に合わせる"""
import numpy as np
from flat_horse import smooth, limb, hoof, poly_d, outlined, shape, along

GOLD, GOLD_D, GOLD_L = '#E9C46A', '#C9952B', '#FFF1C2'


def mane_scallops(crest, n, out_w, depth):
    """首のうしろの線にそって：外がわはなめらか、首がわは丸い波（鞍の布と同じ形）"""
    C = [np.asarray(c, float) for c in crest]
    seg = np.cumsum([0] + [np.linalg.norm(C[i + 1] - C[i]) for i in range(len(C) - 1)])
    def at(sv):
        i = max(0, min(len(C) - 2, int(np.searchsorted(seg, sv) - 1)))
        t = (sv - seg[i]) / (seg[i + 1] - seg[i])
        dv = (C[i + 1] - C[i]) / np.linalg.norm(C[i + 1] - C[i])
        return C[i] + (C[i + 1] - C[i]) * t, np.array([dv[1], -dv[0]])   # 外向き（右向きの馬で左上）
    outer = []
    for k in range(n * 2 + 1):
        p, no = at(seg[-1] * k / (n * 2))
        outer.append(p - no * out_w)
    V = []
    for k in range(n + 1):
        p, no = at(seg[-1] * k / n)
        V.append((p + no * 2, no))
    d = smooth(outer, closed=False)
    d += f' L{V[-1][0][0]:.1f},{V[-1][0][1]:.1f}'
    for k in range(n, 0, -1):
        a, b = V[k][0], V[k - 1][0]
        mid = (a + b) / 2 + V[k][1] * depth * 2
        d += f' Q{mid[0]:.1f},{mid[1]:.1f} {b[0]:.1f},{b[1]:.1f}'
    return d + ' Z'


def blanket_d(a, b, bottom, n):
    """鞍の下の布：上は背中の線、下は丸い波が n 個"""
    ax, ay = a; bx, by = b
    d = f'M{ax},{ay} L{bx},{by} L{bx + 4},{bottom - 8} '
    w = (bx + 4 - (ax - 4)) / n
    x = bx + 4
    for k in range(n):
        x2 = x - w
        d += f'Q{(x + x2) / 2:.1f},{bottom + 16:.1f} {x2:.1f},{bottom - 8:.1f} '
        x = x2
    return d + 'Z'


def carousel_horse(pal, ow=6.0):
    """pal: body・shade・mane・maneD・blanket・seat・cuff・rosette・line
       戻り値：(SVGの<g>の中身, 目印の点 dict)"""
    L = pal['line']
    body, shade = pal['body'], pal['shade']
    g = []

    # ---------- 点（右向き。x→右、y→下） ----------
    torso = [(206, 116), (176, 124), (140, 126), (104, 118), (76, 124), (60, 150), (66, 180), (88, 198),
             (124, 206), (164, 208), (200, 204), (230, 190), (246, 166), (244, 138), (228, 122)]
    neck = [(196, 128), (204, 96), (220, 66), (244, 44), (266, 46), (280, 66), (276, 96), (262, 128), (248, 156), (222, 160)]
    head = [(248, 40), (270, 34), (292, 42), (314, 62), (330, 84), (332, 100), (322, 112), (304, 114), (286, 106), (270, 92), (258, 72)]
    HC, HS = np.array([258.0, 70.0]), 1.1
    hs = lambda pts: [tuple(HC + (np.asarray(q, float) - HC) * HS) for q in pts]
    head = hs(head)
    ear_n = hs([(258, 42), (258, 8), (276, 36)])
    ear_f = hs([(246, 46), (238, 16), (256, 40)])
    # 足：関節の点と太さ
    fore_n = ([(226, 182), (262, 176), (272, 212), (286, 226)], [30, 22, 17, 17])        # 手前の前足（高く上げる）
    fore_f = ([(214, 186), (240, 204), (236, 238), (246, 254)], [28, 20, 16, 16])        # 奥の前足
    hind_n = ([(104, 186), (76, 226), (90, 262), (96, 280)], [38, 22, 17, 17])           # 手前の後ろ足
    hind_f = ([(128, 190), (112, 230), (128, 262), (134, 280)], [34, 20, 16, 16])        # 奥の後ろ足

    def leg_parts(jw, col, cuff_col):
        J, Wd = jw
        poly = limb(J, Wd)
        hf = hoof(J[-2], np.asarray(J[-1]) + (np.asarray(J[-1]) - np.asarray(J[-2])) / np.linalg.norm(np.asarray(J[-1]) - np.asarray(J[-2])) * 9, Wd[-1] + 1, Wd[-1] + 5, 12)
        cuff = limb([along(J[-3], J[-2], 0.62), J[-2], J[-1]], [Wd[-2] + 1, Wd[-2] + 1, Wd[-1] + 1])
        return poly, hf, cuff

    # ---------- 奥の足（少し暗い色） ----------
    for jw in (fore_f, hind_f):
        poly, hf, cuff = leg_parts(jw, shade, pal['cuff'])
        g.append(outlined([poly_d(poly)], shade, L, ow))
        g.append(shape(poly_d(cuff), pal['cuffD'], L, ow))
        g.append(shape(poly_d(hf), GOLD_D, L, ow))

    # ---------- しっぽ（体のうしろ） ----------
    tail = [(78, 130), (54, 128), (34, 146), (26, 176), (32, 204), (22, 232), (44, 222), (58, 196), (52, 176), (60, 156)]
    g.append(shape(smooth(tail, sharp=(5,)), pal['mane'], L, ow))
    g.append(f'<path d="{smooth([(48, 140), (38, 170), (42, 198)], closed=False)}" fill="none" stroke="{pal["maneD"]}" stroke-width="{ow * 0.8:.1f}" stroke-linecap="round"/>')

    # 奥の耳
    g.append(shape(smooth(ear_f, sharp=(1,)), shade, L, ow))

    # ---------- 体（体・首・頭・手前の足をひとつの外線で） ----------
    fn_poly, fn_hf, fn_cuff = leg_parts(fore_n, body, pal['cuff'])
    hn_poly, hn_hf, hn_cuff = leg_parts(hind_n, body, pal['cuff'])
    g.append(outlined([smooth(torso), smooth(neck), smooth(head), poly_d(fn_poly), poly_d(hn_poly)], body, L, ow))
    # 足のつけねの線（ひじ・ももの丸み）
    g.append(f'<path d="{smooth([(214, 176), (228, 168), (244, 170)], closed=False)}" fill="none" stroke="{L}" stroke-width="{ow * 0.75:.1f}" stroke-linecap="round"/>')
    g.append(f'<path d="{smooth([(86, 168), (98, 158), (116, 160)], closed=False)}" fill="none" stroke="{L}" stroke-width="{ow * 0.75:.1f}" stroke-linecap="round"/>')
    # 手前の足の飾り（足首のリボン色）とひづめ（金）
    for cuff, hf in ((fn_cuff, fn_hf), (hn_cuff, hn_hf)):
        g.append(shape(poly_d(cuff), pal['cuff'], L, ow))
        g.append(shape(poly_d(hf), GOLD, L, ow))

    # ---------- たてがみ（首のうしろ・波の形） ----------
    crest = [(256, 36), (240, 42), (224, 56), (210, 76), (200, 98), (194, 122)]
    g.append(shape(mane_scallops(crest, 4, 4, 11), pal['mane'], L, ow))
    # 前髪
    fl = hs([(254, 36), (270, 30), (286, 40), (290, 52), (281, 50), (275, 44), (268, 50), (262, 44)])
    g.append(shape(smooth(fl, sharp=(4, 6)), pal['mane'], L, ow))

    # 手前の耳
    g.append(shape(smooth(ear_n, sharp=(1,)), body, L, ow))
    g.append(shape(smooth(hs([(262, 36), (261, 16), (270, 33)]), sharp=(1,)), pal['maneD'], 'none', 0))

    # ---------- 鞍（下の布＋座る所）・胸の飾り ----------
    g.append(shape(blanket_d((128, 118), (200, 112), 164, 4), pal['blanket'], L, ow))
    g.append(f'<path d="{smooth([(128, 150), (164, 150), (200, 150)], closed=False)}" fill="none" stroke="{GOLD}" stroke-width="{ow * 0.9:.1f}"/>')
    seat = [(136, 118), (146, 104), (156, 112), (176, 112), (190, 100), (198, 114), (190, 128), (146, 130)]
    g.append(shape(smooth(seat, sharp=(1, 4)), pal['seat'], L, ow))
    g.append(shape(f'M162,146 l7,-7 l7,7 l-7,7 Z', pal['rosette'], L, ow * 0.6))
    # 胸のベルト（金）と花
    g.append(f'<path d="{smooth([(198, 132), (224, 146), (244, 156)], closed=False)}" fill="none" stroke="{L}" stroke-width="{ow * 2.6:.1f}" stroke-linecap="round"/>')
    g.append(f'<path d="{smooth([(198, 132), (224, 146), (244, 156)], closed=False)}" fill="none" stroke="{GOLD}" stroke-width="{ow * 1.2:.1f}" stroke-linecap="round"/>')
    g.append(shape('M224,146 m-7,0 a7,7 0 1,0 14,0 a7,7 0 1,0 -14,0', pal['rosette'], L, ow * 0.6))

    # ---------- 顔（頭と同じく1.1倍） ----------
    g.append(f'<g transform="translate({HC[0]} {HC[1]}) scale({HS}) translate({-HC[0]} {-HC[1]})">')
    # 鼻のまわり（少し色）
    g.append(f'<path d="{smooth([(316, 70), (330, 86), (332, 100), (322, 112), (306, 112), (300, 96), (306, 80)])}" fill="{pal["muzzle"]}"/>')
    # 頭の飾り（金のベルト＝鼻の まわりの 紐）。第4.88版（まさちゃん「二枚目のメリーゴーランドの馬の口の紐青線の位置にして！」）：
    #   前は 目の うしろから あごへ たて（(300,52)→(300,104)）。→ 鼻すじの 上の ふち から あごの 下へ ななめ（顔の 向きに 直角＝鼻に まく 紐・鼻の 色の ところの すぐ うしろ）
    band = [(315.5, 64.5), (301.6, 83.4), (286.5, 101.5)]
    g.append(f'<path d="{smooth(band, closed=False)}" fill="none" stroke="{L}" stroke-width="{ow * 2.4:.1f}" stroke-linecap="round"/>')
    g.append(f'<path d="{smooth(band, closed=False)}" fill="none" stroke="{GOLD}" stroke-width="{ow * 1.1:.1f}" stroke-linecap="round"/>')
    g.append(shape('M301.2,83.2 m-6,0 a6,6 0 1,0 12,0 a6,6 0 1,0 -12,0', pal['rosette'], L, ow * 0.6))
    # 目（たて長の黒目＋光）・まつ毛・ほっぺ
    g.append(f'<ellipse cx="281" cy="62" rx="6.5" ry="8" fill="{L}"/>')
    g.append('<circle cx="283.2" cy="58.6" r="2.4" fill="#FFFFFF"/>')
    g.append(f'<path d="M276,55 l-5,-4 M279,53 l-3,-5" stroke="{L}" stroke-width="{ow * 0.55:.1f}" stroke-linecap="round"/>')
    g.append(f'<ellipse cx="290" cy="84" rx="8" ry="5" fill="{pal["blush"]}" opacity=".75"/>')
    # 鼻の穴・口
    g.append(f'<path d="M322,90 q4,2 3,7" fill="none" stroke="{L}" stroke-width="{ow * 0.6:.1f}" stroke-linecap="round"/>')
    g.append(f'<path d="M308,106 q7,3 13,0" fill="none" stroke="{L}" stroke-width="{ow * 0.55:.1f}" stroke-linecap="round"/>')
    g.append('</g>')

    # ---------- 頭の上の羽根飾り ----------

    marks = dict(pole_x=166, seat_y=106, belly_y=208, foot_y=286, left=20, right=336, top=0)
    return ''.join(g), marks


PALETTES = {
    'pink': dict(body='#FFFFFF', shade='#E8DAEF', mane='#F49AC1', maneD='#DE6FA2', blanket='#F7B9D6', seat='#E26CA2', cuff='#F49AC1', cuffD='#E3A3C6',
                 rosette='#9ED8D0', plume='#F49AC1', muzzle='#FBE6F0', blush='#F7A8C8', line='#4A2A4E'),
    'gold': dict(body='#FFFFFF', shade='#E8DAEF', mane='#F7D06A', maneD='#DDA93C', blanket='#A8E0D2', seat='#5DBFAE', cuff='#A8E0D2', cuffD='#9CCFC4',
                 rosette='#F49AC1', plume='#A8E0D2', muzzle='#FBE6F0', blush='#F7A8C8', line='#4A2A4E'),
}

if __name__ == '__main__':
    import sys
    from flat_horse import to_png
    out = sys.argv[1]
    parts = []
    for i, k in enumerate(('pink', 'gold')):
        gtxt, m = carousel_horse(PALETTES[k])
        parts.append(f'<g transform="translate({20 + i * 360},20)">{gtxt}</g>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="740" height="340" viewBox="0 0 740 340"><rect width="740" height="340" fill="#F6ECF7"/>{"".join(parts)}</svg>'
    to_png(svg, 740, 340, out, scale=2)
    print(out)
