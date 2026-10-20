"""桜・紅葉・雪・お正月の壁紙の馬の 動きの時間わり。numpy なしの Python だけ（step_wall.py も flat/step_run.py も使う）
   まさちゃんの指定「この4枚の壁紙後ろ脚動かさない 前足は、6秒〜9秒のランダムで2回動かす。ゆったり
   1秒〜5秒のランダムで、地面の草を食べる5秒〜10秒でリピートする。」→「やっぱり4枚とも前脚も動かさなくていいよ！ あと首の動きもっとスムーズにして！」
   - 足は 4本とも 動かさない（いまの絵のまま）。首と頭だけ 動く
   - コマの名前（どのテーマも LOWER_N＋NOD_N＋1 コマ）：
       U0 … 首を上げた形（いまの絵＝コマ0）
       L1〜L{LOWER_N−1} … 首を下げていく とちゅう。頭の動く道のりが 同じ はばに なる 下げぐあい（flat/step_run.py の lower_levels・step_run.json の lower）
       D0 … 首を地面まで下げた形
       E1〜E{NOD_N} … 草を食べる 頭の動き（少し上げて もどす）の だんかい
   - 草 … GRAZE 秒ごと（ランダム）に T_LOWER 秒で首を下げて（はじめと おわりは ゆっくり）、EAT 秒（ランダム）食べて、T_LOWER 秒で上げる。
     食べている間は NOD_P 秒で 頭を ゆっくり 少し上げて もどす（あいだに D0 で NOD_HOLD 秒）。首の上げ下げも 頭の動きも、
     いちばん近い だんかいの コマを出す（動きの はやさに合わせて コマを めくる＝なめらか）
   - きまった種（SEEDS）で作る 約2分（LOOP_AIM 秒）の くり返し。つなぎめでも 間の決まりを まもる（えらんだ長さ T で切る）
   - timeline(theme, lower) → (くり返しの ミリ秒, [(はじまりの ミリ秒, コマの番号), …])：ページの CSS の keyframes（step_wall.py）
   python3 step_plan.py [テーマ…]   → 時間わりの まとめ（下げぐあいは だいたいの 等分で）"""
import random
import math

THEMES = ('sakura', 'autumn', 'snow', 'newyear')
SEEDS = dict(sakura=21, autumn=22, snow=23, newyear=24)               # 時間わりの種（さがす はじまり）

LOWER_N = 48              # 首を下げる だんかい（とちゅうの コマは LOWER_N−1）
NOD_N = 6                 # 草を食べる 頭の動きの だんかい
T_LOWER = 1.6             # 首を下げる秒（上げるのも同じ）
GRAZE = (5.0, 10.0)       # 草を食べる はじまりの間（秒・ランダム）
EAT = (1.0, 5.0)          # 食べる秒（ランダム）
MIN_UP = 1.0              # 首を上げている いちばん短い秒
NOD_P = (0.8, 1.1)        # 草を食べる 頭の動き 1回（少し上げて もどす）の秒（ランダム）
NOD_HOLD = (0.15, 0.5)    # その あいだの D0 の秒（ランダム）
FIRST_GRAZE = (1.5, 4.0)  # ページを開いてから はじめて首を下げるまで（秒）
LOOP_AIM = 120.0          # くり返しの長さの めやす（秒）
LOOP_SPAN = 15.0          # めやすから ずれてよい はば（秒）
VARIETY = dict(eat=(1.5, 4.5), graze=(6.5, 9.5))     # 間の はんいを 広く つかう時間わりを えらぶ（いちばん短い／長いの めやす）


def names():
    return ['U0'] + [f'L{k}' for k in range(1, LOWER_N)] + ['D0'] + [f'E{m}' for m in range(1, NOD_N + 1)]


def frames(theme):
    """シートの コマの順（コマ0＝いまの絵）"""
    return names()


def plan_events(theme, seed, horizon):
    """草（はじまり, 食べる秒）の並び（horizon 秒まで）"""
    rng = random.Random(seed)
    grazes = [(rng.uniform(*FIRST_GRAZE), rng.uniform(*EAT))]
    while grazes[-1][0] < horizon:
        gp, Ep = grazes[-1]
        lo = max(gp + GRAZE[0], gp + 2 * T_LOWER + Ep + MIN_UP)
        E = rng.uniform(*EAT)
        grazes.append((rng.uniform(lo, gp + GRAZE[1]), E))
    return grazes


def find_seam(grazes):
    """(くり返しの長さ T, くり返しの中の草)：つなぎめでも 間の決まりを まもる。なければ None"""
    lo_T, hi_T = LOOP_AIM - LOOP_SPAN, LOOP_AIM + LOOP_SPAN
    g0 = grazes[0][0]
    best = None
    for j in range(1, len(grazes)):
        gL, EL = grazes[j - 1]
        a = max(gL + 2 * T_LOWER + EL + 0.05, gL + GRAZE[0] - g0, gL + 2 * T_LOWER + EL + MIN_UP - g0, lo_T)
        b = min(gL + GRAZE[1] - g0, grazes[j][0], hi_T)
        if a <= b:
            T = min(max(LOOP_AIM, a), b)
            if best is None or abs(T - LOOP_AIM) < abs(best[0] - LOOP_AIM):
                best = (T, grazes[:j])
    return best


def spans(T, grazes):
    """食べる秒・草の間（つなぎめを またぐ間も）"""
    return [E for _, E in grazes], [b[0] - a[0] for a, b in zip(grazes, grazes[1:])] + [grazes[0][0] + T - grazes[-1][0]]


def plan(theme, seed=None):
    """(k, (T, 草))：決まった種から じゅんに さがして、間の はんいを 広く つかう さいしょの時間わり"""
    s = SEEDS[theme] if seed is None else seed
    best = None
    for k in range(400):
        sm = find_seam(plan_events(theme, s * 1000 + k, LOOP_AIM + LOOP_SPAN + 30))
        if sm is None:
            continue
        e, g = spans(*sm)
        miss = (max(0, min(e) - VARIETY['eat'][0]) + max(0, VARIETY['eat'][1] - max(e))
                + max(0, min(g) - VARIETY['graze'][0]) + max(0, VARIETY['graze'][1] - max(g)))
        if best is None or miss < best[0]:
            best = (miss, k, sm)
        if miss == 0:
            break
    if best is None:
        raise SystemExit(f'{theme}: 時間わりが 作れない')
    return best[1], best[2]


def _acos_t(y):
    """ease（0.5−0.5cos(πu)）が y になる u（0〜1）"""
    return math.acos(max(-1.0, min(1.0, 1 - 2 * y))) / math.pi


def timeline(theme, lower=None, seed=None, k=None):
    """(くり返しの ミリ秒, [(はじまりの ミリ秒, コマの番号), …])。コマの番号は frames(theme) の順。
       lower：L1〜L{LOWER_N−1} の 下げぐあい（0〜1・ふえていく。step_run.json の lower。なければ 等分）
       k：plan() が えらんだ 種の番号（step_run.json に書いてある。あれば さがさない）"""
    s = SEEDS[theme] if seed is None else seed
    if k is None:
        k, (T, grazes) = plan(theme, s)
    else:
        T, grazes = find_seam(plan_events(theme, s * 1000 + k, LOOP_AIM + LOOP_SPAN + 30))
    lv = [0.0] + list(lower if lower is not None else [i / LOWER_N for i in range(1, LOWER_N)]) + [1.0]
    assert len(lv) == LOWER_N + 1 and all(a < b for a, b in zip(lv, lv[1:]))
    rng = random.Random(s * 7919 + k)
    ch = []                                            # (時刻, 首の だんかい 0〜LOWER_N か None, 頭の動きの だんかい 0〜NOD_N か None)
    for g, E in grazes:
        for q in range(1, LOWER_N + 1):                # 下げる：下げぐあい ease(u) が となりの だんかいとの まん中を こえる時
            ch.append((g + T_LOWER * _acos_t((lv[q - 1] + lv[q]) / 2), q, None))
        r = g + T_LOWER + E
        for q in range(LOWER_N - 1, -1, -1):           # 上げる：1−ease(u) が まん中を こえる時
            ch.append((r + T_LOWER * _acos_t(1 - (lv[q] + lv[q + 1]) / 2), q, None))
        t = g + T_LOWER + rng.uniform(*NOD_HOLD)       # 食べる：頭を 少し上げて もどす（(1−cos)/2）
        while True:
            P = rng.uniform(*NOD_P)
            if t + P > r - 0.05:
                break
            for m in range(1, NOD_N + 1):
                ch.append((t + P / 2 * _acos_t((m - .5) / NOD_N), None, m))
            for m in range(NOD_N, 0, -1):
                ch.append((t + P - P / 2 * _acos_t((m - .5) / NOD_N), None, m - 1))
            t += P + rng.uniform(*NOD_HOLD)
    ch.sort(key=lambda c: c[0])
    idx = {n: i for i, n in enumerate(frames(theme))}
    h, n = 0, 0
    out = [(0, idx['U0'])]
    for t, hq, nq in ch:
        if not (0 <= t < T):
            continue
        if hq is not None:
            h = hq
        if nq is not None:
            n = nq
        assert n == 0 or h == LOWER_N, (theme, t, 'nod while the head moves')
        f = 'U0' if h == 0 else f'L{h}' if h < LOWER_N else ('D0' if n == 0 else f'E{n}')
        ms = int(round(t * 1000))
        if out[-1][0] == ms:
            out[-1] = (ms, idx[f])
            if len(out) > 1 and out[-2][1] == out[-1][1]:
                out.pop()
        elif out[-1][1] != idx[f]:
            out.append((ms, idx[f]))
    T_ms = int(round(T * 1000))
    assert out[0] == (0, 0) and out[-1][0] < T_ms and out[-1][1] == idx['U0']
    assert all(a[0] < b[0] and a[1] != b[1] for a, b in zip(out, out[1:]))
    return T_ms, out


def summary(theme, lower=None):
    k, (T, grazes) = plan(theme)
    T_ms, tl = timeline(theme, lower, k=k)
    e, g = spans(T, grazes)
    dt = [b[0] - a[0] for a, b in zip(tl, tl[1:])]
    print(f'{theme}: 種 {SEEDS[theme]}・{k}・くり返し {T:.3f} 秒・草 {len(grazes)} 回（間 {min(g):.2f}〜{max(g):.2f} 秒・食べる {min(e):.2f}〜{max(e):.2f} 秒）'
          f'・コマを めくる {len(tl)} 回（いちばん短い間 {min(dt)} ms）')
    return T_ms, tl


if __name__ == '__main__':
    import sys
    for th in sys.argv[1:] or THEMES:
        summary(th)
