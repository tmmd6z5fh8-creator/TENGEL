"""桜・紅葉・雪・お正月の壁紙の馬の 動きの時間わり（まさちゃんの指定「この4枚の壁紙後ろ脚動かさない 前足は、6秒〜9秒のランダムで2回動かす。ゆったり
   1秒〜5秒のランダムで、地面の草を食べる5秒〜10秒でリピートする。」）。numpy なしの Python だけ（step_wall.py も flat/step_run.py も使う）
   - コマの名前（どのテーマも 47コマ）：
       U0 … 首を上げて 前足は地面（立っている）
       L1〜L11 … 首を下げていく とちゅう（LOWER_N＝12 だんかいの 1〜11）
       D0 … 首を地面まで下げた（草を食べる）・D1・D2 … 草を食べて 頭を小さく動かす
       UN1〜UN8・UF1〜UF8 … 首を上げたまま 手前（N）・奥（F）の前足を上げていく（8で いちばん上）
       DN1〜DN8・DF1〜DF8 … 首を下げたまま 同じ（少し低く上げる）
     コマ0 は いまの絵：桜・雪は U0、紅葉・お正月は UN8（手前の前足を上げた形）。シートの順は frames(theme)
   - 前足 … LEGS 秒ごと（ランダム）に 手前 → 奥の順で1本ずつ：T_LIFT 秒で上げて T_HOLD 秒そのまま、T_LIFT 秒で おろす
            （手前と奥のあいだは GAP 秒・ランダム）。うしろ足は 動かさない
     草 … GRAZE 秒ごと（ランダム）に T_LOWER 秒で首を下げて、EAT 秒（ランダム）食べて（D0 → D1 → D2 → D1 → D0 を ときどき）、T_LOWER 秒で上げる
     首を上げ下げしている時は 前足を動かさない（前足を上げている時の まえと あと SETTLE 秒も）。食べている時は 前足を動かしてよい（頭は D0 のまま）
     どの間も 決まりの はんいの中で ランダム（ぶつかる時は えらびなおす：まって ずらすことは しない）
   - きまった種（SEEDS）で作る 約2分（LOOP_AIM 秒）の くり返し。くり返しの つなぎめでも 間の決まりを まもる（えらんだ長さ T で切る）。
     紅葉・お正月は いまの絵が 前足を上げた形なので、くり返しは 手前の前足を上げた所から（おろす）はじまり、さいごに また上げた所で おわる
   - timeline(theme) → (くり返しの ミリ秒, [(はじまりの ミリ秒, コマの番号), …])：ページの CSS の keyframes（step_wall.py）
   python3 step_plan.py [テーマ…]   → 時間わりの まとめ（間の いちばん短い・長い・コマを めくる回数）"""
import random
import bisect

THEMES = ('sakura', 'autumn', 'snow', 'newyear')
ORIG = dict(sakura='U0', snow='U0', autumn='UN8', newyear='UN8')     # コマ0（いまの絵）
SEEDS = dict(sakura=11, autumn=12, snow=13, newyear=14)               # 時間わりの種（つなぎめが きれいに つながる種を さがす はじまり）

LIFT_N = 8                # 前足を上げる だんかい（0.1秒ずつ）
LOWER_N = 12              # 首を下げる だんかい（0.1秒ずつ）
T_LIFT = 0.8              # 前足を上げる秒（おろすのも同じ）
T_HOLD = 0.2              # 上げたまま
GAP = (0.3, 2.0)          # 手前の前足を おろしてから 奥の前足を上げるまで（秒・ランダム）
T_LOWER = 1.2             # 首を下げる秒（上げるのも同じ）
LEGS = (6.0, 9.0)         # 前足の はじまりの間（秒・ランダム）
GRAZE = (5.0, 10.0)       # 草を食べる はじまりの間（秒・ランダム）
EAT = (1.0, 5.0)          # 食べる秒（ランダム）
MIN_UP = 1.0              # 首を上げている いちばん短い秒
SETTLE = 0.05             # 前足を上げる まえと あと、首を上げ下げしない秒
NIB_T = 0.16              # 草を食べる 頭の動き（D1 → D2 → D1）の 1コマの秒
NIB_HOLD = (0.25, 0.7)    # その あいだの D0 の秒（ランダム）
FIRST_LEG = (1.0, 3.0)    # 桜・雪：ページを開いてから はじめて前足を動かすまで（秒）
FIRST_GRAZE = (2.0, 7.0)  # はじめて首を下げるまで（秒）
LOOP_AIM = 120.0          # くり返しの長さの めやす（秒）
LOOP_SPAN = 15.0          # めやすから ずれてよい はば（秒）
T_LEG = 2 * T_LIFT + T_HOLD   # 前足1本を上げて おろす秒


def names():
    L = ['U0'] + [f'L{k}' for k in range(1, LOWER_N)] + ['D0', 'D1', 'D2']
    for hd in 'UD':
        for lg in 'NF':
            L += [f'{hd}{lg}{k}' for k in range(1, LIFT_N + 1)]
    return L


def frames(theme):
    """シートの コマの順（コマ0＝いまの絵）"""
    L = names()
    o = ORIG[theme]
    L.remove(o)
    return [o] + L


def _ov(a, b):
    return a[0] < b[1] and b[0] < a[1]


def leg_lifts(l, gap):
    """前足の1回（はじまり l・手前と奥の間 gap）：(手前の はじまり, 奥の はじまり)"""
    return l, l + T_LEG + gap


def _lw(l, gap):
    """前足を上げている時（まえと あとの SETTLE つき）"""
    a, b = leg_lifts(l, gap)
    return [(a - SETTLE, a + T_LEG + SETTLE), (b - SETTLE, b + T_LEG + SETTLE)]


def _gw(g, E):
    """首を上げ下げしている時"""
    return [(g, g + T_LOWER), (g + T_LOWER + E, g + 2 * T_LOWER + E)]


def _ok(l, gap, g, E):
    return not any(_ov(x, y) for x in _lw(l, gap) for y in _gw(g, E))


def plan_events(theme, seed, horizon, tries=40, budget=4000):
    """前足（はじまり, 間）と 草（はじまり, 食べる秒）の並び（horizon 秒まで）。前の方から 1つずつ ランダムに えらんで、
       ぶつかる時は えらびなおす（行きづまったら 1つ前に もどって えらびなおす）。うまくいかない種は None"""
    rng = random.Random(seed)
    left = [budget]

    def leg_cands(legs, grazes):
        lp = legs[-1][0]
        for _ in range(tries * 8):
            l, gap = rng.uniform(lp + LEGS[0], lp + LEGS[1]), rng.uniform(*GAP)
            if all(_ok(l, gap, g, E) for g, E in grazes[-3:]):
                yield (l, gap)

    def graze_cands(legs, grazes):
        if not grazes:
            lo, hi = FIRST_GRAZE
        else:
            gp, Ep = grazes[-1]
            lo, hi = max(gp + GRAZE[0], gp + 2 * T_LOWER + Ep + MIN_UP), gp + GRAZE[1]
        if lo > hi:
            return
        for _ in range(tries * 8):
            g, E = rng.uniform(lo, hi), rng.uniform(*EAT)
            if g > SETTLE and all(_ok(l, gap, g, E) for l, gap in legs[-3:]):
                yield (g, E)

    def grow(legs, grazes):
        if grazes and min(legs[-1][0], grazes[-1][0]) >= horizon:
            return legs, grazes
        left[0] -= 1
        if left[0] < 0:
            return None
        if grazes and legs[-1][0] <= grazes[-1][0]:
            gen = ((legs + [c], grazes) for c in leg_cands(legs, grazes))
        else:
            gen = ((legs, grazes + [c]) for c in graze_cands(legs, grazes))
        for n, (L, G) in enumerate(gen):
            if n >= tries:
                break
            r = grow(L, G)
            if r is not None:
                return r
            if left[0] < 0:
                return None
        return None

    l0 = -T_LIFT if ORIG[theme] == 'UN8' else rng.uniform(*FIRST_LEG)
    return grow([(l0, rng.uniform(*GAP))], [])


def find_seam(theme, legs, grazes):
    """くり返しの長さ T（つなぎめでも 間の決まりを まもる）。なければ None"""
    lo_T, hi_T = LOOP_AIM - LOOP_SPAN, LOOP_AIM + LOOP_SPAN
    g0 = grazes[0][0]
    cands = []
    if ORIG[theme] == 'U0':
        l0 = legs[0][0]
        # T のあとは はじめに もどる：前の前足・草が T までに おわっていて、つぎ（l0+T・g0+T）までの間が 決まりの中
        for i in range(1, len(legs)):
            for j in range(1, len(grazes)):
                lL, gapL = legs[i - 1]
                gL, EL = grazes[j - 1]
                if legs[i][0] < lo_T - 20 or grazes[j][0] < lo_T - 20:
                    continue
                end = max(leg_lifts(lL, gapL)[1] + T_LEG + SETTLE, gL + 2 * T_LOWER + EL + SETTLE)
                a = max(end, lL + LEGS[0] - l0, gL + GRAZE[0] - g0, gL + 2 * T_LOWER + EL + MIN_UP - g0, lo_T)
                b = min(lL + LEGS[1] - l0, gL + GRAZE[1] - g0, legs[i][0], grazes[j][0], hi_T)
                # T までに ほかの前足・草が はじまらない（i, j が T のあとの さいしょ）
                if a <= b:
                    T = min(max(LOOP_AIM, a), b)
                    cands.append((abs(T - LOOP_AIM), T, i, j))
    else:
        # 紅葉・お正月：T は 首を上げた時の 前足の はじまり＋T_LIFT（その時 手前の前足が いちばん上＝いまの絵）。その前足の 間は はじめの前足と同じに する
        for i in range(1, len(legs)):
            l, gap = legs[i]
            T = l + T_LIFT
            if not (lo_T <= T <= hi_T):
                continue
            j = bisect.bisect_left([g for g, _ in grazes], l)          # l より前の草の数
            if j == 0 or j >= len(grazes):
                continue
            gL, EL = grazes[j - 1]
            if gL + 2 * T_LOWER + EL > l - SETTLE + 1e-9:               # 首を上げきっていない（食べている時の前足）
                continue
            if not (gL + GRAZE[0] <= g0 + T <= gL + GRAZE[1] and g0 + T >= gL + 2 * T_LOWER + EL + MIN_UP):
                continue
            cands.append((abs(T - LOOP_AIM), T, i, j))
    if not cands:
        return None
    _, T, i, j = min(cands)
    if ORIG[theme] == 'UN8':
        legs = legs[:i] + [(legs[i][0], legs[0][1])]                    # つなぎめの前足（くり返しの はじめと同じ1回）
    else:
        legs = legs[:i]
    return T, legs, grazes[:j]


def _nibbles(rng, a, b, busy):
    """草を食べている a〜b の あいだの 頭の動き（D1 → D2 → D1）の はじまり。前足を上げている時（busy）は しない"""
    out = []
    t = a + rng.uniform(*NIB_HOLD)
    while t + 3 * NIB_T + 0.1 <= b:
        seg = (t - 0.05, t + 3 * NIB_T + 0.05)
        clash = [x for x in busy if _ov(seg, x)]
        if clash:
            t = max(x[1] for x in clash) + rng.uniform(*NIB_HOLD)
            continue
        out.append(t)
        t += 3 * NIB_T + rng.uniform(*NIB_HOLD)
    return out


def _track(changes):
    changes.sort()
    return [c[0] for c in changes], [c[1] for c in changes]


def _at(track, t, default):
    ts, vs = track
    i = bisect.bisect_right(ts, t + 1e-9) - 1
    return vs[i] if i >= 0 else default


def spans(theme, T, legs, grazes):
    """くり返しの中の 食べる秒・草の間・前足の間（つなぎめを またぐ間も）"""
    eats = [E for _, E in grazes]
    gper = [b[0] - a[0] for a, b in zip(grazes, grazes[1:])] + [grazes[0][0] + T - grazes[-1][0]]
    lper = [b[0] - a[0] for a, b in zip(legs, legs[1:])]
    if ORIG[theme] == 'U0':
        lper.append(legs[0][0] + T - legs[-1][0])
    return eats, gper, lper


# ランダムに見えるように、間の はんいを 広く つかう時間わりを えらぶ（食べる秒・草の間・前足の間の いちばん短い／長いの めやす）
VARIETY = dict(eat=(1.8, 4.4), graze=(7.0, 9.4), legs=(6.6, 8.5))


def plan(theme, seed=None):
    """(T, 前足, 草)：決まった種から じゅんに さがして、間の はんいを 広く つかう さいしょの時間わり"""
    s = SEEDS[theme] if seed is None else seed
    best = None
    for k in range(400):
        ev = plan_events(theme, s * 1000 + k, LOOP_AIM + LOOP_SPAN + 30)
        if ev is None:
            continue
        sm = find_seam(theme, *ev)
        if sm is None:
            continue
        e, g, l = spans(theme, *sm)
        miss = (max(0, min(e) - VARIETY['eat'][0]) + max(0, VARIETY['eat'][1] - max(e)) + max(0, min(g) - VARIETY['graze'][0])
                + max(0, VARIETY['graze'][1] - max(g)) + max(0, min(l) - VARIETY['legs'][0]) + max(0, VARIETY['legs'][1] - max(l)))
        if best is None or miss < best[0]:
            best = (miss, k, sm)
        if miss == 0:
            break
    if best is None:
        raise SystemExit(f'{theme}: 時間わりが 作れない')
    return best[1], best[2]


def timeline(theme, seed=None, k=None):
    """(くり返しの ミリ秒, [(はじまりの ミリ秒, コマの番号), …])。コマの番号は frames(theme) の順。
       k：plan() が えらんだ 種の番号（step_run.json に書いてある。あれば さがさない）"""
    s = SEEDS[theme] if seed is None else seed
    if k is None:
        k, (T, legs, grazes) = plan(theme, s)
    else:
        T, legs, grazes = find_seam(theme, *plan_events(theme, s * 1000 + k, LOOP_AIM + LOOP_SPAN + 30))
    rng = random.Random(s * 7919 + k)
    # 前足（上げぐあい 0〜LIFT_N・どちらの足か）
    leg = []
    busy = []
    for l, gap in legs:
        for lg, a in zip('NF', leg_lifts(l, gap)):
            for q in range(1, LIFT_N + 1):
                leg.append((a + (q - .5) * T_LIFT / LIFT_N, (lg, q)))
            b = a + T_LIFT + T_HOLD
            for q in range(1, LIFT_N + 1):
                leg.append((b + (q - .5) * T_LIFT / LIFT_N, (lg, LIFT_N - q)))
            busy.append((a, a + T_LEG))
    # 首（下げぐあい 0〜LOWER_N）と 草を食べる頭の動き（0・1・2）
    head, nib = [], []
    for g, E in grazes:
        for q in range(1, LOWER_N + 1):
            head.append((g + (q - .5) * T_LOWER / LOWER_N, q))
        r = g + T_LOWER + E
        for q in range(1, LOWER_N + 1):
            head.append((r + (q - .5) * T_LOWER / LOWER_N, LOWER_N - q))
        for c in _nibbles(rng, g + T_LOWER, r, busy):
            nib += [(c, 1), (c + NIB_T, 2), (c + 2 * NIB_T, 1), (c + 3 * NIB_T, 0)]
    trs = [_track(leg), _track(head), _track(nib)]
    names_ = frames(theme)
    idx = {n: i for i, n in enumerate(names_)}

    def frame(t):
        lg, q = _at(trs[0], t, ('N', 0))
        h = _at(trs[1], t, 0)
        n = _at(trs[2], t, 0)
        if q:
            assert h in (0, LOWER_N), (theme, t, 'leg during head move')
            return f"{'U' if h == 0 else 'D'}{lg}{q}"
        if 0 < h < LOWER_N:
            return f'L{h}'
        if h == LOWER_N:
            return f'D{n}'
        return 'U0'
    times = sorted({0.0} | {t for tr in trs for t in tr[0] if 0 <= t < T})
    out = []
    for t in times:
        ms = int(round(t * 1000))
        f = idx[frame(t)]
        if out and out[-1][0] == ms:
            out[-1] = (ms, f)
        elif not out or out[-1][1] != f:
            out.append((ms, f))
    assert out[0] == (0, 0), out[:3]
    T_ms = int(round(T * 1000))
    assert out[-1][0] < T_ms
    if ORIG[theme] == 'UN8':
        assert out[-1][1] == 0                                          # さいごは いまの絵（つぎの はじめに つながる）
    else:
        assert out[-1][1] == idx['U0']
    return T_ms, out


def summary(theme):
    T_ms, tl = timeline(theme)
    names_ = frames(theme)
    seq = [(ms / 1000, names_[f]) for ms, f in tl]
    T = T_ms / 1000
    # 間を はかる（くり返しを 2回つないで）
    two = seq + [(t + T, n) for t, n in seq]
    lst = [t for t, n in two if n in ('UN1', 'DN1') and not (two[two.index((t, n)) - 1][1].startswith(('UN', 'DN')))]
    grz = [t for i, (t, n) in enumerate(two) if n == 'L1' and i and two[i - 1][1] == 'U0']
    downs = []
    for i, (t, n) in enumerate(two):
        if n == 'D0' and two[i - 1][1] == 'L11':
            for t2, n2 in two[i + 1:]:
                if n2 == 'L11':
                    downs.append(t2 - t)
                    break
    gi = [b - a for a, b in zip(grz, grz[1:])]
    li = [b - a for a, b in zip(lst, lst[1:])]
    print(f'{theme}: くり返し {T:.3f} 秒・コマを めくる {len(tl)} 回・草 {sum(1 for t in grz if t < T)} 回（間 {min(gi):.2f}〜{max(gi):.2f} 秒・'
          f'下げている {min(downs):.2f}〜{max(downs):.2f} 秒）・前足 {sum(1 for t in lst if t < T)} 回（間 {min(li):.2f}〜{max(li):.2f} 秒）')
    return T_ms, tl


if __name__ == '__main__':
    import sys
    for th in sys.argv[1:] or THEMES:
        summary(th)
