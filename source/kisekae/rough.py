"""手書きっぽい 線（超プレミアムど的中：super_premium.py）：まさちゃん「新しく、超プレミアムど的中ボタン演出追加したい！
   この感じで、ちょっとぎゃくに線を雑にして手書きっぽく作れる？」
   SVG の 形を そのまま 使って、描き方だけ 手書きに する：
   - 線は ゆれる（ゆっくりの 大きな ゆれ。手の ふるえ（細かい ゆれ）は 見えないので 0）・太さが かわる（筆の 線＝形を ぬった 帯）・
     はしを 少し はみ出す（とじた 形は 少し 行きすぎる）・細い 線を もう1本 少し ずらして 重ねる（下書きの 線）
   - ぬりは 線から 少し ずれる（色を ぬる 時の ずれ）・ふちも 少し ゆれる
   - 出す path は 2次の B スプライン（相対・0.1 きざみ：qspline）で 小さく（art.smooth の 3分の1 くらい）
   鉛筆（style='pencil'：まさちゃん「線をもっと細くして！」「鉛筆で描いたかんじで！」）：
   - ふちの 線（ink に した 色・こい 色）は 細い 鉛筆の 線（1.3px・太さが 少し かわる・はしは 細く）を ぬりの **上** に 描き、
     もう1本 もっと 細い うすい 線で なぞる（少し ずれて 行きすぎる）。色は 鉛筆の 黒（PEN['ink']）
   - outlined（部品を まとめた ふち）は ほかの 部品の 中に 入る 所の 線を 描かない（まとめた 形の 外がわだけ）。
     線が とぎれる 所は 少し 行きすぎて 交わる（鉛筆の 線の 重なり）
   - ぬりの ずれは 小さく（0.6px）。白い つや など 色の 線は そのまま（下書きの 線なし）
   使い方：with hand(scale=…, seed=…): の 中で art の path()・outlined() を 呼ぶと 手書きに なる（cute.py なども 同じ。
   scale＝その 絵が 画面で 何倍に なるか：ゆれの 大きさを 画面の px で そろえる）。ellipse・circle・rect の 文字は ellipses() で 手書きの path に。
   乱数は seed で きまる（何回 作っても 同じ）"""
import math
import random
import re
import art

TOK = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')

# ゆれの 大きさなど（画面の px）
P = dict(amp=1.6, wl=64.0, tremor=0.0, sketch_tremor=0.0, over=7.0, wvar=.32, sketch_w=.36, sketch_amp=2.8, sketch_op=.62,
         fill_shift=2.0, fill_amp=.7, step=5.0)     # step：点の 間かく（px）。手の ふるえ（tremor）は 見えないので 0（点を へらして 軽く）
_S = dict(scale=1.0, rnd=random.Random(1), on=False)


# ---------------------------------------------------------------- path の d → 点の 列
def _arc(x1, y1, rx, ry, phi, fa, fs, x2, y2, n):
    """SVG の 円弧（はしの 点の 書き方）→ 点の 列"""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = c * dx + s * dy, -s * dx + c * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1p * x1p / (rx * rx) + y1p * y1p / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    k = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs:
        k = -k
    cxp, cyp = k * rx * y1p / ry, -k * ry * x1p / rx
    cx, cy = c * cxp - s * cyp + (x1 + x2) / 2, s * cxp + c * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    out = []
    for i in range(1, n + 1):
        t = t1 + dt * i / n
        px, py = rx * math.cos(t), ry * math.sin(t)
        out.append((c * px - s * py + cx, s * px + c * py + cy))
    return out


def parse(d, step=2.0):
    """path の d → [(点の 列, とじている か)]（曲線は step ごとに 点に）"""
    toks = TOK.findall(d)
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    lc = None                      # 前の 制御点（S・T 用）
    subs, cur = [], []

    def nums(k):
        nonlocal i
        v = [float(t) for t in toks[i:i + k]]
        i += k
        return v

    def bez(p0, ps):
        L = sum(math.dist(a, b) for a, b in zip([p0] + ps[:-1], ps))
        n = max(2, int(L / step))
        if len(ps) == 3:
            (x1, y1), (x2, y2), (x3, y3) = ps
            return [(((1 - t) ** 3) * p0[0] + 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3 * x3,
                     ((1 - t) ** 3) * p0[1] + 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3 * y3) for t in (j / n for j in range(1, n + 1))]
        (x1, y1), (x2, y2) = ps
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * x1 + t * t * x2, (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * y1 + t * t * y2)
                for t in (j / n for j in range(1, n + 1))]

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in 'Zz':
                if cur:
                    subs.append((cur, True))
                cur, x, y, lc = [], sx, sy, None
                continue
        elif cmd is None:
            break
        rel = cmd.islower()
        C = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if C == 'M':
            a, b = nums(2)
            if cur:
                subs.append((cur, False))
            x, y = ox + a, oy + b
            sx, sy, cur, lc = x, y, [(x, y)], None
            cmd = 'l' if rel else 'L'
        elif C == 'L':
            a, b = nums(2)
            x, y = ox + a, oy + b
            cur.append((x, y))
            lc = None
        elif C == 'H':
            (a,) = nums(1)
            x = (x if rel else 0.0) + a
            cur.append((x, y))
            lc = None
        elif C == 'V':
            (b,) = nums(1)
            y = (y if rel else 0.0) + b
            cur.append((x, y))
            lc = None
        elif C == 'C':
            v = nums(6)
            p1, p2, p3 = (ox + v[0], oy + v[1]), (ox + v[2], oy + v[3]), (ox + v[4], oy + v[5])
            cur += bez((x, y), [p1, p2, p3])
            lc, (x, y) = p2, p3
        elif C == 'S':
            v = nums(4)
            p1 = (2 * x - lc[0], 2 * y - lc[1]) if lc else (x, y)
            p2, p3 = (ox + v[0], oy + v[1]), (ox + v[2], oy + v[3])
            cur += bez((x, y), [p1, p2, p3])
            lc, (x, y) = p2, p3
        elif C == 'Q':
            v = nums(4)
            p1, p2 = (ox + v[0], oy + v[1]), (ox + v[2], oy + v[3])
            cur += bez((x, y), [p1, p2])
            lc, (x, y) = p1, p2
        elif C == 'T':
            v = nums(2)
            p1 = (2 * x - lc[0], 2 * y - lc[1]) if lc else (x, y)
            p2 = (ox + v[0], oy + v[1])
            cur += bez((x, y), [p1, p2])
            lc, (x, y) = p1, p2
        elif C == 'A':
            rx, ry, phi, fa, fs, a, b = nums(7)
            x2, y2 = ox + a, oy + b
            L = math.dist((x, y), (x2, y2)) * 1.6 + 1
            cur += _arc(x, y, rx, ry, phi, int(fa), int(fs), x2, y2, max(4, int(L / step)))
            x, y, lc = x2, y2, None
        else:
            i += 1
    if cur:
        subs.append((cur, False))
    return [(pts, cl) for pts, cl in subs if len(pts) >= 1]


# ---------------------------------------------------------------- 点の 列 → 小さい path の d（2次の B スプライン・相対・0.1 きざみ）
def _t(v):
    return int(round(v * 10))


def _f10(n):
    """0.1 きざみの 整数 → 文字（.5・-1.2・3）"""
    a, b = divmod(abs(n), 10)
    t = (str(a) if a else '') + ('.' + str(b) if b else '')
    return ('-' if n < 0 else '') + (t or '0')


def _join(ns):
    o = ''
    for n in ns:
        t = _f10(n)
        if o and o[-1] not in 'MmLlQqZz' and t[0] != '-':
            o += ' '
        o += t
    return o


def qspline(pts, closed=True):
    """点を なめらかに つなぐ（点は ひかえの 点・となりの 点との まん中を とおる：2次の B スプライン）。
       数は 0.1 きざみの 相対（丸めた 点どうしの 差＝ずれが たまらない）。smooth（3次・絶対）より 3分の1 くらいの 長さ"""
    P = [(_t(x), _t(y)) for x, y in pts]
    n = len(P)
    if n == 1:
        return 'M' + _join(P[0]) + 'l0 0'
    if n == 2:
        return 'M' + _join(P[0]) + 'l' + _join((P[1][0] - P[0][0], P[1][1] - P[0][1]))
    mid = lambda a, b: ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
    if closed:
        cur = mid(P[-1], P[0])
        d = 'M' + _join(cur)
        for i in range(n):
            c, e = P[i], mid(P[i], P[(i + 1) % n])
            d += 'q' + _join((c[0] - cur[0], c[1] - cur[1], e[0] - cur[0], e[1] - cur[1]))
            cur = e
        return d + 'z'
    cur = P[0]
    d = 'M' + _join(cur)
    for i in range(1, n - 1):
        c, e = P[i], (mid(P[i], P[i + 1]) if i < n - 2 else P[n - 1])
        d += 'q' + _join((c[0] - cur[0], c[1] - cur[1], e[0] - cur[0], e[1] - cur[1]))
        cur = e
    return d


# ---------------------------------------------------------------- 点の 列を 手書きに
def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def resample(pts, step):
    """点の 列を 同じ 間かくに（線の 長さに そって）"""
    if len(pts) < 2:
        return list(pts)
    L = length(pts)
    n = max(2, int(math.ceil(L / step)))
    out, acc, j = [pts[0]], 0.0, 0
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    for k in range(1, n):
        target = L * k / n
        while j < len(seg) - 1 and acc + seg[j] < target:
            acc += seg[j]
            j += 1
        u = (target - acc) / seg[j] if seg[j] else 0
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    out.append(pts[-1])
    return out


def normals(pts):
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        out.append((-dy / L, dx / L))
    return out


def noise(rnd, wl):
    """ゆっくりの ゆれ（2つの 波）＋ 手の ふるえ（短い 波）：s（線の 長さ）→ -1〜1 くらい"""
    p1, p2, p3, p4 = (rnd.uniform(0, 2 * math.pi) for _ in range(4))
    w2 = wl * rnd.uniform(.38, .52)
    return lambda s: (.62 * math.sin(2 * math.pi * s / wl + p1) + .38 * math.sin(2 * math.pi * s / w2 + p2),
                      math.sin(2 * math.pi * s / 7.3 + p3) * .6 + math.sin(2 * math.pi * s / 4.1 + p4) * .4)


def hand_pts(pts, closed, rnd, amp, over, step, tremor=None, both=False):
    """手書きの 線の 点：とじた 形は はじまりを ずらして 少し 行きすぎる・ひらいた 線は はしを 少し のばす（both：はじめも）。法線の 方へ ゆらす"""
    sc = _S['scale']
    stp = step / sc
    if closed:
        pts = list(pts)
        if pts[0] != pts[-1]:
            pts = pts + [pts[0]]
        pts = resample(pts, stp)[:-1]
        k = rnd.randrange(len(pts))
        pts = pts[k:] + pts[:k]
        L = length(pts + [pts[0]])
        ov = over / sc * rnd.uniform(.6, 1.4)
        extra, acc = [], 0.0
        for a, b in zip(pts + [pts[0]], pts[1:] + [pts[0]] + pts[1:]):
            if acc > ov or acc > L * .25:
                break
            extra.append(b)
            acc += math.dist(a, b)
        pts = pts + [pts[0]] + extra
    else:
        pts = resample(pts, stp)
        if len(pts) >= 2 and over:
            ov = over / sc * rnd.uniform(.3, 1.0)
            (ax, ay), (bx, by) = pts[-2], pts[-1]
            L = math.hypot(bx - ax, by - ay) or 1
            pts = pts + [(bx + (bx - ax) / L * ov, by + (by - ay) / L * ov)]
            if both:
                ov = over / sc * rnd.uniform(.3, 1.0)
                (ax, ay), (bx, by) = pts[1], pts[0]
                L = math.hypot(bx - ax, by - ay) or 1
                pts = [(bx + (bx - ax) / L * ov, by + (by - ay) / L * ov)] + pts
    nz = noise(rnd, P['wl'] / sc)
    nm = normals(pts)
    out, s = [], 0.0
    for i, (p, (nx, ny)) in enumerate(zip(pts, nm)):
        if i:
            s += math.dist(pts[i - 1], p)
        lo, hi = nz(s * sc)
        dv = (amp * lo + amp * (P['tremor'] if tremor is None else tremor) * hi) / sc
        out.append((p[0] + nx * dv, p[1] + ny * dv))
    return out


def brush_d(pts, w, rnd, wvar=None):
    """太さが かわる 線（筆）の 形：はじめと おわりは 少し 細く・とちゅうは ゆっくり 太く 細く"""
    if len(pts) < 2:
        x, y = pts[0]
        r = w / 2
        return f'M{art.f(x - r)} {art.f(y)} a{art.f(r)} {art.f(r)} 0 1 0 {art.f(2 * r)} 0 a{art.f(r)} {art.f(r)} 0 1 0 {art.f(-2 * r)} 0Z'
    sc = _S['scale']
    nz = noise(rnd, P['wl'] * 1.7 / sc)
    L = length(pts)
    nm = normals(pts)
    left, right, s = [], [], 0.0
    taper = min(L * .18, 14 / sc)
    for i, (p, (nx, ny)) in enumerate(zip(pts, nm)):
        if i:
            s += math.dist(pts[i - 1], p)
        k = 1 + (P['wvar'] if wvar is None else wvar) * nz(s * sc)[0]
        e = min(s, L - s)
        k *= .55 + .45 * min(1.0, e / taper) if taper else 1
        h = w * k / 2
        left.append((p[0] + nx * h, p[1] + ny * h))
        right.append((p[0] - nx * h, p[1] - ny * h))
    return qspline(left + right[::-1], closed=True)


def rough_stroke(d, w, color, opacity=None, cap='round', sketch=True):
    """線を 手書きに：筆の 線（太さが かわる）＋ 細い 下書きの 線（少し ずれて うすく）"""
    rnd = _S['rnd']
    out = ''
    op = f' opacity="{opacity}"' if opacity not in (None, '') else ''
    for pts, closed in parse(d, step=1.5 / _S['scale']):
        if len(pts) < 2:
            continue
        hp = hand_pts(pts, closed, rnd, P['amp'], P['over'], P['step'])
        out += f'<path d="{brush_d(hp, w, rnd)}" fill="{color}"{op}/>'
        if sketch and w * _S['scale'] > 1.6:
            sp = hand_pts(pts, closed, rnd, P['sketch_amp'], P['over'] * 1.6, P['step'], P['sketch_tremor'])
            sop = P['sketch_op'] * (float(opacity) if opacity not in (None, '') else 1.0)
            out += (f'<path d="{qspline(sp, closed=False)}" fill="none" stroke="{color}" stroke-width="{art.f(max(.6 / _S["scale"], w * P["sketch_w"]))}" '
                    f'stroke-linecap="round" stroke-linejoin="round" opacity="{sop:.2f}"/>')
    return out


def wobble_d(d, amp=None):
    """ぬりの 形を 少し ゆらす（とじた 形のまま）"""
    rnd = _S['rnd']
    amp = P['fill_amp'] if amp is None else amp
    o = ''
    sc = _S['scale']
    for pts, closed in parse(d, step=1.5 / sc):
        if len(pts) < 3:
            continue
        q = resample(pts + ([pts[0]] if closed else []), P['step'] / sc)
        if closed:
            q = q[:-1]
        nz = noise(rnd, P['wl'] / sc)
        nm = normals(q)
        s, r = 0.0, []
        for i, (p, (nx, ny)) in enumerate(zip(q, nm)):
            if i:
                s += math.dist(q[i - 1], p)
            dv = amp * nz(s * sc)[0] / sc
            r.append((p[0] + nx * dv, p[1] + ny * dv))
        o += qspline(r, closed=closed)
    return o.strip() or d


# ---------------------------------------------------------------- 鉛筆の 線
PEN = dict(w=1.3, wvar=.38, amp=1.0, over=5.0, op=.9,          # 線：はば（画面の px）・太さの かわり方・ゆれ・行きすぎ・こさ
           re_w=.5, re_amp=1.6, re_over=9.0, re_op=.45,        # なぞる 線：はば・ゆれ・行きすぎ・こさ
           fill_shift=.6, ink='#4D4049', dark=.25, min_run=3.0)   # ぬりの ずれ・鉛筆の 色・これより こい 色の 線は 鉛筆に・これより 短い 線は 描かない（px）


def _lum(c):
    """#RRGGBB の 明るさ（相対輝度）。色で ない もの（url(…)・none）は 1"""
    m = re.fullmatch(r'#([0-9a-fA-F]{6})', str(c).strip())
    if not m:
        return 1.0
    v = [int(m.group(1)[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    v = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in v]
    return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]


def pen_ink(color):
    """鉛筆で 描く 色か（ふちの 色・こい 色）→ 鉛筆の 色。ちがえば None（白い つや などは そのまま）"""
    if color in _S.get('inks', ()) or _lum(color) < PEN['dark']:
        return PEN['ink']
    return None


def pencil_line(pts, closed, op=1.0, both=True):
    """鉛筆の 線：細い 線（太さが 少し かわる・はしは 細く）＋ もっと 細い うすい なぞる 線（少し ずれて 行きすぎる）"""
    rnd, sc = _S['rnd'], _S['scale']
    hp = hand_pts(pts, closed, rnd, PEN['amp'], PEN['over'], P['step'], both=both)
    o = f'<path d="{brush_d(hp, PEN["w"] / sc, rnd, PEN["wvar"])}" fill="{PEN["ink"]}" opacity="{PEN["op"] * op:.2f}"/>'
    rp = hand_pts(pts, closed, rnd, PEN['re_amp'], PEN['re_over'], P['step'], both=both)
    o += (f'<path d="{qspline(rp, closed=False)}" fill="none" stroke="{PEN["ink"]}" stroke-width="{art.f(PEN["re_w"] / sc)}" '
          f'stroke-linecap="round" opacity="{PEN["re_op"] * op:.2f}"/>')
    return o


def _inside(P_, poly):
    """点（N×2）が 形（とじた 点の 列）の 中か（偶奇の きまり）"""
    import numpy as np
    x, y = poly[:, 0], poly[:, 1]
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    px, py = P_[:, :1], P_[:, 1:]
    cond = (y > py) != (y2 > py)
    xi = (x2 - x) * (py - y) / np.where(y2 == y, 1e-9, y2 - y) + x
    return ((cond & (px < xi)).sum(1) % 2) == 1


def pencil_outline(parts):
    """部品を まとめた 形の ふち（ほかの 部品の 中に 入る 所は 描かない）を 鉛筆の 線で"""
    import numpy as np
    sc = _S['scale']
    polys = []
    for d in parts:
        for pts, closed in parse(d, step=1.5 / sc):
            if len(pts) >= 3:
                polys.append(pts)
    arrs = [np.array(p) for p in polys]
    out = ''
    for i, poly in enumerate(polys):
        ring = resample(poly + [poly[0]], P['step'] / sc)[:-1]
        if len(ring) < 3:
            continue
        R_ = np.array(ring)
        vis = np.ones(len(ring), bool)
        for j, a in enumerate(arrs):
            if j != i:
                vis &= ~_inside(R_, a)
        if vis.all():
            out += pencil_line(ring, True)
            continue
        if not vis.any():
            continue
        k = int(np.argmin(vis))                 # 見えない 点から 回して、見える 点の ならびを 切り出す
        order = list(range(k, len(ring))) + list(range(0, k))
        run = []
        for idx in order + [None]:
            if idx is not None and vis[idx]:
                run.append(ring[idx])
                continue
            if len(run) >= 2 and length(run) * sc >= PEN['min_run']:
                out += pencil_line(run, False)
            run = []
    return out


# ---------------------------------------------------------------- art の path()・outlined() を 手書きに
_ORIG = dict(path=art.path, outlined=art.outlined)


def _attrs(a):
    return ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in a.items())


def h_path(d, **a):
    if not _S['on']:
        return _ORIG['path'](d, **a)
    a = dict(a)
    stroke = a.pop('stroke', None)
    sw = float(a.pop('stroke_width', 1) or 1)
    cap = a.pop('stroke_linecap', 'round')
    a.pop('stroke_linejoin', None)
    fill = a.get('fill', '#000')
    wrap = {k: a.pop(k) for k in ('transform', 'opacity', 'style', 'class') if k in a}
    out = ''
    if fill not in ('none',):
        out += f'<path d="{wobble_d(d)}" {_attrs(a)}/>'
    if stroke and stroke != 'none':
        if _S.get('style') == 'pencil':
            if pen_ink(stroke):
                for pts, closed in parse(d, step=1.5 / _S['scale']):
                    if len(pts) >= 2:
                        out += pencil_line(pts, closed)
            else:
                out += rough_stroke(d, sw, stroke, cap=cap, sketch=False)
        else:
            out += rough_stroke(d, sw, stroke, cap=cap, sketch=sw * _S['scale'] > 2.2)
    if wrap:
        out = f'<g {_attrs(wrap)}>{out}</g>'
    return out


def h_outlined(parts, fill, line, lw):
    """ふちどり：線（筆・はば 2×lw）を 形ごとに → ぬりを 上に（少し ずらす：内がわの 線は ぬりで 消える）"""
    if not _S['on']:
        return _ORIG['outlined'](parts, fill, line, lw)
    rnd = _S['rnd']
    sc = _S['scale']
    if _S.get('style') == 'pencil':          # 鉛筆：ぬり（少し ずれる）→ まとめた 形の ふちを 細い 鉛筆の 線で 上に
        dx, dy = (rnd.uniform(-1, 1) * PEN['fill_shift'] / sc, rnd.uniform(-1, 1) * PEN['fill_shift'] / sc)
        over = ''.join(f'<path d="{wobble_d(d)}" fill="{fill}"/>' for d in parts)
        return f'<g transform="translate({dx:.2f} {dy:.2f})">{over}</g>' + pencil_outline(parts)
    under = ''.join(rough_stroke(d, lw * 2, line, sketch=True) for d in parts)
    dx, dy = (rnd.uniform(-1, 1) * P['fill_shift'] / sc, rnd.uniform(-.6, 1) * P['fill_shift'] / sc)
    over = ''.join(f'<path d="{wobble_d(d)}" fill="{fill}"/>' for d in parts)
    return under + f'<g transform="translate({dx:.2f} {dy:.2f})">{over}</g>'


ELL = re.compile(r'<(ellipse|circle|rect)\b([^>]*?)/>')
ATT = re.compile(r'([\w-]+)="([^"]*)"')


def ellipses(svg):
    """文字で 書いた ellipse・circle・rect も 手書きの path に（線が あれば 筆の 線）"""
    def one(m):
        tag, at = m.group(1), dict(ATT.findall(m.group(2)))
        g = lambda k, v=0.0: float(at.pop(k, v))
        if tag == 'rect':
            x, y, w, h = g('x'), g('y'), g('width'), g('height')
            d = f'M{x} {y} L{x + w} {y} L{x + w} {y + h} L{x} {y + h} Z'
        else:
            cx, cy = g('cx'), g('cy')
            rx = g('r') if tag == 'circle' else g('rx')
            ry = rx if tag == 'circle' else g('ry')
            d = art.smooth(art.ellipse_pts(cx, cy, rx, ry, 12))
        kw = {k.replace('-', '_'): v for k, v in at.items()}
        return h_path(d, **kw)
    return ELL.sub(one, svg)


class hand:
    """with hand(scale=2.7, seed=5): の 中で art.path・art.outlined（と mods の 中の 同じ 名前）を 手書きに する。
       style='pencil' で 鉛筆の 線（inks：鉛筆に する ふちの 色）"""

    def __init__(self, scale=1.0, seed=1, mods=(), style='brush', inks=()):
        self.scale, self.seed, self.mods, self.style, self.inks = scale, seed, mods, style, tuple(inks)

    def __enter__(self):
        self.prev = dict(_S)
        _S.update(scale=self.scale, rnd=random.Random(self.seed), on=True, style=self.style, inks=self.inks)
        self.saved = []
        for m in (art,) + tuple(self.mods):
            for name, fn in (('path', h_path), ('outlined', h_outlined)):
                if hasattr(m, name):
                    self.saved.append((m, name, getattr(m, name)))
                    setattr(m, name, fn)
        return self

    def __exit__(self, *e):
        for m, name, fn in self.saved:
            setattr(m, name, fn)
        _S.clear()
        _S.update(self.prev)
