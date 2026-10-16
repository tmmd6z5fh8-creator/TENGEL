"""着せ替え（仮）の絵：SVGの部品づくり（なめらかな形・手足・ハート・キラキラ・薔薇など）"""
import math


def f(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s


def smooth(pts, closed=True, k=6.0):
    """点を通るなめらかな線（Catmull-Rom → 3次ベジェ）。点を2回続けると角になる"""
    n = len(pts)
    if n < 2:
        return ''
    d = f'M{f(pts[0][0])} {f(pts[0][1])}'
    last = n if closed else n - 1
    for i in range(last):
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        if p1 == p2:
            continue
        c1 = (p1[0] + (p2[0] - p0[0]) / k, p1[1] + (p2[1] - p0[1]) / k)
        c2 = (p2[0] - (p3[0] - p1[0]) / k, p2[1] - (p3[1] - p1[1]) / k)
        if p0 == p1:
            c1 = p1
        if p2 == p3:
            c2 = p2
        d += f' C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}'
    return d + (' Z' if closed else '')


def limb(pts, widths, cap=True):
    """線（骨）に太さをつけた手足・首・しっぽの形。widths は点ごとの太さ"""
    n = len(pts)
    L, R = [], []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = widths[i] / 2
        L.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        R.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    ring = L[:]
    if cap:  # 先を丸く
        e = pts[-1]; a = pts[-2]
        dx, dy = e[0] - a[0], e[1] - a[1]; ln = math.hypot(dx, dy) or 1
        ring.append((e[0] + dx / ln * widths[-1] * .45, e[1] + dy / ln * widths[-1] * .45))
    ring += R[::-1]
    if cap:
        s = pts[0]; b = pts[1]
        dx, dy = s[0] - b[0], s[1] - b[1]; ln = math.hypot(dx, dy) or 1
        ring.append((s[0] + dx / ln * widths[0] * .45, s[1] + dy / ln * widths[0] * .45))
    return smooth(ring)


def ellipse_pts(cx, cy, rx, ry, n=12, rot=0):
    r = math.radians(rot)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return out


def heart(cx, cy, s):
    """ハート（大きさ s＝幅のおよそ半分）"""
    p = lambda x, y: f'{f(cx + x * s)} {f(cy + y * s)}'
    return (f'M{p(0, -.45)} C{p(-.15, -1.05)} {p(-1.05, -1.0)} {p(-1.0, -.25)} '
            f'C{p(-.95, .3)} {p(-.35, .62)} {p(0, 1.0)} C{p(.35, .62)} {p(.95, .3)} {p(1.0, -.25)} '
            f'C{p(1.05, -1.0)} {p(.15, -1.05)} {p(0, -.45)} Z')


def sparkle(cx, cy, r, thin=.16):
    """4つの角のキラキラ"""
    t = r * thin
    return (f'M{f(cx)} {f(cy - r)} Q{f(cx + t)} {f(cy - t)} {f(cx + r)} {f(cy)} '
            f'Q{f(cx + t)} {f(cy + t)} {f(cx)} {f(cy + r)} Q{f(cx - t)} {f(cy + t)} {f(cx - r)} {f(cy)} '
            f'Q{f(cx - t)} {f(cy - t)} {f(cx)} {f(cy - r)} Z')


def star5(cx, cy, r, ri=None, rot=-90):
    ri = ri or r * .48
    pts = []
    for i in range(10):
        a = math.radians(rot + i * 36)
        rr = r if i % 2 == 0 else ri
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in pts) + ' Z'


def leaf(cx, cy, length, width, ang):
    """葉っぱ（月桂樹など）：付け根 (cx,cy) から ang の向きへ"""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    tip = (cx + ux * length, cy + uy * length)
    m1 = (cx + ux * length * .45 + vx * width / 2, cy + uy * length * .45 + vy * width / 2)
    m2 = (cx + ux * length * .45 - vx * width / 2, cy + uy * length * .45 - vy * width / 2)
    return (f'M{f(cx)} {f(cy)} Q{f(m1[0] + ux * length * .05)} {f(m1[1] + uy * length * .05)} {f(tip[0])} {f(tip[1])} '
            f'Q{f(m2[0] + ux * length * .05)} {f(m2[1] + uy * length * .05)} {f(cx)} {f(cy)} Z')


def svg(w, h, body, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            + (f'<defs>{defs}</defs>' if defs else '') + body + '</svg>')


def path(d, **a):
    attrs = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in a.items())
    return f'<path d="{d}" {attrs}/>'


def g(inner, **a):
    attrs = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in a.items())
    return f'<g {attrs}>{inner}</g>'


def outlined(parts, fill, line, lw):
    """部品をまとめてフチどり：下に太い線で全部を描いて、上から塗りで重ねる（内側の線は消える）"""
    under = ''.join(path(d, fill=line, stroke=line, stroke_width=lw * 2, stroke_linejoin='round') for d in parts)
    over = ''.join(path(d, fill=fill) for d in parts)
    return under + over
