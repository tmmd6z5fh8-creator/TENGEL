"""勝負服の絵の背景（780×320・SVG）：ななめのコマ割りに勝負服の柄（市松・縦じま・星・輪）、
   まんなかの大きなコマは青に白い流線（スピード線）と光。コマのあいだは白いすき間＋紺のふち。下のほうに網点
   bg_svg() → SVG の文字列"""
import math
import numpy as np

W, Hh = 780, 320
K_ = 0.45                                   # コマのふちのかたむき（x = u - K_*y）
NAVY = '#121A33'
BLUE, RED, YEL, GRN = '#1A3FB8', '#E02424', '#FFC400', '#0F9D58'
PANELS = [(-260, 86, 'check'), (94, 222, 'stripe'), (230, 768, 'center'), (776, 880, 'star'), (888, 1200, 'hoop')]
GAP = 3.6


def f2(v):
    return f'{v:.2f}'


def panel_poly(u0, u1, inset=GAP):
    a, b = u0 + inset, u1 - inset
    return [(a, -2), (b, -2), (b - K_ * (Hh + 2), Hh + 2), (a - K_ * (Hh + 2), Hh + 2)]


def pts(poly):
    return ' '.join(f'{f2(x)},{f2(y)}' for x, y in poly)


def star_path(cx, cy, r, rot=0.0):
    p = []
    for j in range(10):
        rr = r if j % 2 == 0 else r * 0.42
        a = math.radians(-90 + rot + j * 36)
        p.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return 'M' + ' L'.join(f'{f2(x)} {f2(y)}' for x, y in p) + ' Z'


def halftone(u0, u1, y0, rmax, rng, col=NAVY, op=0.30, step=7.0):
    """網点（下へいくほど大きい点）"""
    out = []
    ys = np.arange(y0, Hh + step, step * 0.866)
    for j, y in enumerate(ys):
        off = (step / 2) if j % 2 else 0
        xa, xb = u0 - K_ * y - step, u1 - K_ * y + step
        for x in np.arange(xa + off, xb, step):
            t = (y - y0) / (Hh - y0)
            r = rmax * max(0.0, t) ** 1.1
            if r < 0.35:
                continue
            out.append(f"<circle cx='{f2(x)}' cy='{f2(y)}' r='{f2(r)}'/>")
    return f"<g fill='{col}' opacity='{op}'>" + ''.join(out) + "</g>"


def _defs(panels):
    defs = [f"<pattern id='chk' width='28' height='28' patternUnits='userSpaceOnUse' patternTransform='translate(6 4)'>"
            f"<rect width='28' height='28' fill='{YEL}'/><rect width='14' height='14' fill='{RED}'/><rect x='14' y='14' width='14' height='14' fill='{RED}'/></pattern>",
            f"<pattern id='stp' width='20' height='40' patternUnits='userSpaceOnUse' patternTransform='rotate({f2(math.degrees(math.atan(K_)))})'>"
            f"<rect width='20' height='40' fill='#FFFFFF'/><rect width='10' height='40' fill='{GRN}'/></pattern>",
            f"<pattern id='hoop' width='40' height='30' patternUnits='userSpaceOnUse' patternTransform='translate(0 6)'>"
            f"<rect width='40' height='30' fill='{YEL}'/><rect y='15' width='40' height='15' fill='{GRN}'/></pattern>",
            "<radialGradient id='glow' cx='440' cy='182' r='290' gradientUnits='userSpaceOnUse'>"
            "<stop offset='0' stop-color='#5D86FF'/><stop offset='0.45' stop-color='#2F5BE6'/><stop offset='1' stop-color='#173AAE'/></radialGradient>",
            "<linearGradient id='shine' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#FFFFFF' stop-opacity='.22'/>"
            "<stop offset='.35' stop-color='#FFFFFF' stop-opacity='0'/></linearGradient>"]
    for i, (u0, u1, kind) in enumerate(panels):
        defs.append(f"<clipPath id='cp{i}'><polygon points='{pts(panel_poly(u0, u1))}'/></clipPath>")
    return '<defs>' + ''.join(defs) + '</defs>'


def _panels(panels, rng, rect=None):
    """コマの中身とふちの SVG の部品。rect(u0, u1)：コマの中をぬる四角の属性（なければ絵のはばいっぱい）"""
    S = []
    for i, (u0, u1, kind) in enumerate(panels):
        poly = pts(panel_poly(u0, u1))
        R_ = rect(u0, u1) if rect else f"width='{W}' height='{Hh}'"
        g = [f"<g clip-path='url(#cp{i})'>"]
        if kind == 'check':
            g.append(f"<rect {R_} fill='url(#chk)'/>")
        elif kind == 'stripe':
            g.append(f"<rect {R_} fill='url(#stp)'/>")
        elif kind == 'hoop':
            g.append(f"<rect {R_} fill='url(#hoop)'/>")
        elif kind == 'star':
            g.append(f"<rect {R_} fill='{RED}'/>")
            for row in range(9):
                y = 18 + row * 38
                for col in range(-1, 4):
                    x = u0 - K_ * y + 22 + col * 40 + (20 if row % 2 else 0)
                    g.append(f"<path d='{star_path(x, y, 10.5, rot=8)}' fill='#FFFFFF'/>")
        elif kind == 'center':
            g.append(f"<rect {R_} fill='url(#glow)'/>")
            # 流線（うしろへ流れる白いスピード線）：馬のうしろに多く、まんなかの高さに集める
            ys_ = np.sort(rng.uniform(10, 310, 38))
            for y in ys_:
                y = float(y + rng.uniform(-3, 3))
                xl = u0 - K_ * y                                   # コマの左のふち
                xr = u1 - K_ * y
                L = rng.uniform(90, 300) * (0.6 + 0.4 * math.exp(-((y - 180) / 90) ** 2))
                x0 = xl + rng.uniform(-30, 120)
                x1 = min(x0 + L, xr - 20)
                if x1 - x0 < 30:
                    continue
                th = rng.uniform(1.4, 4.2)
                op = rng.uniform(0.35, 0.8)
                xm = x0 + (x1 - x0) * 0.35                          # 左が太く、右へ細く消える
                g.append(f"<path d='M{f2(x0)} {f2(y)} Q{f2(xm)} {f2(y - th / 2)} {f2(x1)} {f2(y)} Q{f2(xm)} {f2(y + th / 2)} {f2(x0)} {f2(y)} Z' "
                         f"fill='#FFFFFF' fill-opacity='{f2(op)}'/>")
            # 光の帯（ななめ）
            for (ua, ub, op) in ((330, 372, 0.10), (392, 404, 0.08), (560, 610, 0.07)):
                g.append(f"<polygon points='{pts(panel_poly(ua, ub, 0))}' fill='#FFFFFF' opacity='{op}'/>")
        if kind != 'center':
            g.append(halftone(u0, u1, 196, 2.9, rng))
            g.append(f"<rect {R_} fill='url(#shine)'/>")
        else:
            g.append(halftone(u0, u1, 236, 2.2, rng, col='#0B1D63', op=0.45))
        g.append('</g>')
        S.append(''.join(g))
        S.append(f"<polygon points='{poly}' fill='none' stroke='{NAVY}' stroke-width='3' stroke-linejoin='round'/>")
    return S


def bg_svg(seed=5):
    rng = np.random.default_rng(seed)
    S = [f"<rect width='{W}' height='{Hh}' fill='#FFFFFF'/>"]
    S.insert(0, _defs(PANELS))
    S += _panels(PANELS, rng)
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{Hh}' viewBox='0 0 {W} {Hh}'>" + ''.join(S) + "</svg>"


# 壁紙の動き（まさちゃん「背景が常に右から左に模様が動く同じ模様をリピートする」）：くり返しの1まい（はば PERIOD）。
# コマの並びは いまの絵と同じ（市松・縦じま・青・星・輪）で、市松と輪のはばだけ ちぢめて、輪のあとに また市松が来るようにした。
# いまの絵の 0〜780 の所は いまの絵と同じ（見えない所だけ ちがう）
STRIP = [(-114, 86, 'check'), (94, 222, 'stripe'), (230, 768, 'center'), (776, 880, 'star'), (888, 1090, 'hoop')]
PERIOD = 1090 + 8 + 114                      # 輪のおわり → 次の市松のはじめ（すき間 8）


def strip_svg(seed=5):
    """くり返しの1まい（PERIOD × 320）：1回分のコマを、まえ・いま・つぎ の3か所に同じ形で置く（柄も一緒にずれるので、つぎ目がない）"""
    S = [_defs(STRIP), f"<rect width='{PERIOD}' height='{Hh}' fill='#FFFFFF'/>"]
    rect = lambda u0, u1: f"x='{f2(u0 - K_ * Hh - 12)}' width='{f2(u1 - u0 + K_ * Hh + 24)}' height='{Hh}'"
    for k in (-1, 0, 1):
        S.append(f"<g transform='translate({k * PERIOD} 0)'>" + ''.join(_panels(STRIP, np.random.default_rng(seed), rect)) + '</g>')
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{PERIOD}' height='{Hh}' viewBox='0 0 {PERIOD} {Hh}'>" + ''.join(S) + "</svg>"


if __name__ == '__main__':
    import sys, os, cv2
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from flat_horse import to_png
    tmp = sys.argv[1]
    to_png(bg_svg(), W, Hh, tmp, scale=2)
    im = cv2.imread(tmp, cv2.IMREAD_UNCHANGED)
    cv2.imwrite(tmp, cv2.resize(im[..., :3], (W, Hh), interpolation=cv2.INTER_AREA))
    print(tmp)
