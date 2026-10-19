"""開運（招き馬）の壁紙の動き（まさちゃんの指定「常に周りに小判が上から下に降っている、1〜2秒にで、右手を前後ろに引っかかっているように振動させ、
   3秒で一気に右手を下に振り降ろす、8秒おきにリピートする。11秒〜19秒のランダムで、招きながらヒヒィーン（文字なし）とうえを向きながら鳴く」）：
   ページに入れる HTML と CSS
   - 絵は flat/lucky_banner.py の部品（parts：いつもの絵と同じ形・同じ場所）を べつべつの <svg> にして重ね、動く所だけを CSS で動かす。下から：
     地（光・青海波・うしろの桜と四つ葉）→ うしろの小判（降る・蹄鉄と招き馬の うしろを通る）→ 蹄鉄と招き馬 → 手前の金貨・桜・キラキラ → 手前の小判（降る・左右だけ）
   - 招き馬の 動かす部品（flat/lucky_maneki.py の rig で包む。動く中心は <g transform> で はさむ）：
     右前足（ひじを中心に 少し かたむく・前へ たおれて 少し短く見える）・ひづめ（手首を中心に 前へ おれる＝たての のびが cos θ。
     θ が 90度を こえると 裏＝金の ひづめの かべ・白い毛のふち に入れかわる）・頭（首を中心に 上がって 少し かたむく）・
     顔（目と かざりは 上へ ちぢむ・鼻先は 上へ 大きく＝上を向く・鼻先の下がわが 見える）・ひとみ（上を見る）・口（開ける・ふるえる）・
     耳（うしろへ たおれる）・たてがみ・しっぽ・体（少し のびる）
   - 8秒で1回り（CYCLE・R_KEYS）：0〜1秒 そのまま → 1〜2秒 ひづめが 前へ・うしろへ がたがた（前へ おれかけて 引っかかり、うしろへ もどる）
     → 2.25〜2.95秒 少しうしろへ ためる（ぷるぷる）→ 3秒 一気に 前へ おれて 振り下ろす（0.2秒・少し はねかえる）→ 3.55〜4.05秒 もどる → 8秒まで そのまま
   - ヒヒィーン（neigh_tracks）：首を上げて 上を向き（目も上を見る）・口を開けて 鳴く（頭と口が ふるえる・耳が たおれる・しっぽを ふる）・
     そのあいだに 招く（BECKON_S 秒に1回 ひづめを おって もどす）→ もどる。前のヒヒィーンから 11〜19秒（ばらばら・はじめ → はじめ）。
     招く所は がたがた・振り下ろしと かさならない（8秒の中の FREE。3秒の 振り下ろしの前に 首が上がった時は、振り下ろしも 招く1回）。
     招く右前足は もう1本（.lwAB：BECKON_S 秒で くり返す 動き）を 招く間だけ 出して、いつもの右前足（.lwAA）と 入れかえる
     （どちらも 止まっている時に 入れかえるので 見えない。だから ヒヒィーンの はじめは BECKON_S 秒の ます目の上）。
     EV_CYCLES 回ぶん（EV_LOOP 秒）で1回り。ページを開いてから 1回目は 11〜19秒
   - 小判（KOBAN）：うしろ8まい・手前8まい。上から下へ（うしろは 小さく ゆっくり）・左右に ゆれて かたむく・くるっと うらがえる（よこに 細くなる）
   - ページを開くと 0秒（いつもの絵と同じ招き馬）から。視差効果を減らす（prefers-reduced-motion）なら 動かさず、小判も出さない（いつもの絵と同じ）
   クラスの名前は lw…（的中ボタンの .kb とは別）
   python3 lucky_wall.py --judge <Judge_Lucky.dc.html>   → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 lucky_wall.py --plan                          → ヒヒィーンの予定"""
import sys, os, re, math, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'flat'))
import lucky_banner as LB
import lucky_maneki as LM

ALT = ('銀の蹄鉄の中で、右の前足をあげて福を招き、千両の小判をだいた白い招き馬（正面の顔・つり目の金色の目・赤い首輪と金の鈴）と、金貨・桜・四つ葉のアニメ風イラスト'
       '（まわりに いつも小判が降っている。8秒ごとに 右の前足が 引っかかったように がたがたして、一気に 振り下ろす。ときどき 上を向いて 招きながら いななく）')
CYCLE = 8.0                      # 振り下ろしの1回り
EV_CYCLES = 12                   # ヒヒィーンの1回りの 8秒の数（EV_LOOP＝96秒）
EV_LOOP = EV_CYCLES * CYCLE
EV_GAP = (11.0, 19.0)            # ヒヒィーンと つぎのヒヒィーンの間（はじめ → はじめ）
BECKON_S = 0.6                   # 招く1回の秒（ヒヒィーンの はじめも この ます目の上）
FREE = (4.25, 9.0)               # 招いてよい所・首が上がっていてよい おわり（8秒の中：振り下ろしが もどってから、つぎの がたがたまで）
NEIGH_FROM = 2.4                 # ヒヒィーンを はじめてよい所（8秒の中・がたがたの あと）
SEED = 0

# 動かす中心（招き馬の座標・viewBox 0 0 240 270）
P_EL = (44.0, 196.0)             # ひじ（右前足が かたむく）
P_WR = (42.5, 161.0)             # 手首（ひづめが おれる）
P_NK = (120.0, 170.0)            # 首（頭が上がる）
P_FE = (120.0, 58.0)             # 目と かざりが ちぢむ中心
P_FL = (120.0, 40.0)             # 前髪
P_MZ = (120.0, 149.0)            # 鼻先
P_MO = (120.0, 162.5)            # 開けた口の上のはし
P_EAR = ((86.0, 46.0), (154.0, 46.0))
P_MN = (74.0, 150.0)             # たてがみ
P_TL = (186.0, 222.0)            # しっぽの つけね
P_BD = (120.0, 268.0)            # 体の下（のびる）

# ---------- 8秒の1回り：ひづめの おれ θ（度・0＝いつも・＋＝前へ・−＝うしろへ）。(秒, θ, 次までの動き) ----------
R_KEYS = [(0.00, 0, 'linear'), (1.00, 0, 'ease-out'),
          # がたがた（前へ おれかけて 引っかかり → うしろへ もどる。ばらばらの間かく）
          (1.05, 32, 'linear'), (1.09, 24, 'ease-out'), (1.13, -12, 'ease-out'),
          (1.19, 30, 'linear'), (1.23, 22, 'ease-out'), (1.27, -10, 'ease-out'),
          (1.35, 37, 'linear'), (1.39, 28, 'ease-out'), (1.43, -14, 'ease-out'),
          (1.49, 27, 'linear'), (1.53, -8, 'ease-out'),
          (1.60, 38, 'linear'), (1.64, 30, 'ease-out'), (1.68, -13, 'ease-out'),
          (1.75, 33, 'linear'), (1.79, -10, 'ease-out'),
          (1.86, 36, 'linear'), (1.90, 27, 'ease-out'), (1.95, -6, 'ease-in-out'), (2.02, 0, 'linear'),
          # ためる（少し うしろへ・ぷるぷる）
          (2.25, 0, 'ease-in-out'), (2.72, -21, 'linear'), (2.77, -17, 'linear'), (2.82, -22, 'linear'), (2.87, -18, 'linear'), (2.92, -23, 'linear'),
          # 一気に 振り下ろす（90度で 裏に入れかわる）→ はねかえる → もどる
          (3.00, -24, 'ease-in'), (3.12, 90, 'ease-out'), (3.20, 162, 'ease-in-out'), (3.28, 143, 'ease-in-out'), (3.35, 150, 'linear'),
          (3.55, 150, 'ease-in'), (3.74, 90, 'ease-out'), (4.05, -8, 'ease-in-out'), (4.20, 0, 'linear'), (CYCLE, 0, 'linear')]
# 招く1回（BECKON_S 秒でくり返す・ヒヒィーンの時だけ出す右前足）
BECKON = [(0.00, 0, 'ease-in'), (0.09, 90, 'ease-out'), (0.15, 140, 'ease-in-out'), (0.21, 134, 'ease-in'), (0.30, 90, 'ease-out'),
          (0.42, -6, 'ease-in-out'), (0.50, 0, 'linear'), (BECKON_S, 0, 'linear')]
NEIGH_UP = 0.32                  # 首を上げる秒
NEIGH_DOWN = 0.45                # 首を もどす秒
NEIGH_HOLD = 1.95                # 首を上げている（はじめから。招くのが のびたら のばす）


def pct(t, period, nd=3):
    s = f'{t / period * 100:.{nd}f}'.rstrip('0').rstrip('.')
    return (s or '0') + '%'


def num(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return '0' if s in ('-0', '', '-') else s


def T(r=None, s=None, t=None):
    """動く中心から見た 動き：ずらす（t）→ まわす（r）→ のばす（s）。キー どうしで 同じ形にする"""
    out = []
    px = lambda v: num(v) + ('px' if num(v) != '0' else '')
    if t is not None:
        out.append(f'translate({px(t[0])},{px(t[1])})')
    if r is not None:
        out.append(f'rotate({num(r)}deg)' if num(r) != '0' else 'rotate(0)')
    if s is not None:
        out.append(f'scale({num(s[0], 3)},{num(s[1], 3)})')
    return 'transform:' + ' '.join(out)


def pv(cls, p, inner):
    """動く中心 p で はさむ：<g translate(p)><g class><g translate(-p)>…"""
    return (f"<g transform='translate({num(p[0])} {num(p[1])})'><g class='{cls}'>"
            f"<g transform='translate({num(-p[0])} {num(-p[1])})'>{inner}</g></g></g>")


def fold(th):
    """ひづめの おれ θ → (よこ, たて) の のび。前へ おれると 近づくので 少し大きく、うしろへは 少し小さく"""
    s = math.sin(math.radians(th))
    return (1 + 0.07 * s if th >= 0 else 1 + 0.04 * s), math.cos(math.radians(th))


def arm_of(th):
    """ひづめの おれ θ → 右前足（ひじが中心）の (かたむき, たての のび)。がたがたの時は 前へ おれると 内がわへ・うしろへ もどると 外がわへ ゆれ、
       振り下ろすと 内がわへ 5度・前へ たおれて 0.93"""
    if th <= 40:
        return 0.1 * th, 1.0
    u = min(1.0, (th - 40) / 110)
    return 4.0 + 1.0 * u, 1 - 0.07 * u


def crossings(keys):
    """θ が 90度を こえる 秒（キーに 90 を入れてあるので、その秒）→ [(秒, 裏か)]"""
    out = []
    for (t0, a, _), (t1, b, _) in zip(keys, keys[1:]):
        if (a < 90 <= b) or (a >= 90 > b):
            assert b == 90 or a == 90, (t0, a, t1, b)
            out.append((t1 if b == 90 else t0, b > 90 or (b == 90 and a < 90)))
    return out


def kf(name, keys, period, fmt, nd=3, dflt='linear'):
    """[(秒, 値, 次までの動き)] → @keyframes（dflt＝アニメーションの動き と同じものは 書かない）"""
    body = ''.join(f'{pct(t, period, nd)}{{{fmt(v)}' + (f';animation-timing-function:{e}' if e != dflt else '') + '}'
                   for t, v, e in keys)
    return f'@keyframes {name}{{{body}}}'


def kf_step(name, keys, period, prop='opacity', nd=3):
    """[(秒, 値)] → 切りかえの @keyframes（step-end で使う）"""
    keys = list(keys) + [(period, keys[-1][1])]
    body = ''.join(f'{pct(t, period, nd)}{{{prop}:{v}}}' for t, v in keys)
    return f'@keyframes {name}{{{body}}}'


# ---------- ヒヒィーンの予定 ----------
def grid(t):
    return round(t / BECKON_S) * BECKON_S


def neigh_plan(s):
    """s 秒（BECKON_S の ます目の上）に はじめた ヒヒィーン → dict(招く はじめ・回数（ページの秒）, 首を もどしはじめる秒, おわり, 振り下ろしも招くか)"""
    c0 = math.floor(s / CYCLE) * CYCLE
    o = s - c0
    swing = o < 2.95                                   # 3秒の 振り下ろしの前に 首が上がる → 振り下ろしも 招く1回
    first = s + BECKON_S
    while first < c0 + FREE[0] - 1e-9:
        first += BECKON_S
    n = 2 if swing else 3
    down = max(s + NEIGH_HOLD, first + n * BECKON_S - 0.05)
    return dict(b0=round(first, 3), n=n, down=round(down, 3), end=round(down + NEIGH_DOWN, 3), swing=swing, o=o, c0=c0)


def neigh_ok(s):
    pl = neigh_plan(s)
    if not NEIGH_FROM - 1e-9 <= pl['o'] <= FREE[1]:
        return False
    return pl['b0'] >= pl['c0'] + FREE[0] - 1e-9 and pl['end'] <= pl['c0'] + FREE[1] + 1e-9


def schedule():
    """ヒヒィーンの はじめの秒の列（EV_LOOP の中・BECKON_S の ます目の上）。いつも同じ予定（SEED から しらべて、決まりに合う さいしょの予定）。
       決まり：はじめ → つぎのはじめ が EV_GAP（つなぎ目も）・招く所と 首が上がっている所は FREE の中・ページを開いてから 1回目は EV_GAP の中・
       11〜19秒が かたよらない（短い 11〜13・長い 17〜19 を どちらも ふくむ）"""
    gaps_all = [round(BECKON_S * k, 3) for k in range(int(math.ceil(EV_GAP[0] / BECKON_S)), int(EV_GAP[1] / BECKON_S) + 1)]
    for seed in range(SEED, SEED + 50000):
        rnd = random.Random(seed)
        firsts = [g for g in gaps_all if neigh_ok(g)]
        t = rnd.choice(firsts)
        starts = [t]
        while True:
            opts = [g for g in gaps_all if neigh_ok(round(t + g, 3))]
            if not opts:
                break
            t = round(t + rnd.choice(opts), 3)
            if t + EV_GAP[0] > EV_LOOP + starts[0] + 1e-9:
                break
            starts.append(t)
        if starts[-1] >= EV_LOOP:
            starts.pop()
        wrap = round(EV_LOOP + starts[0] - starts[-1], 3)
        if not EV_GAP[0] <= wrap <= EV_GAP[1] or neigh_plan(starts[-1])['end'] > EV_LOOP:
            continue
        gaps = [round(b - a, 3) for a, b in zip(starts, starts[1:])] + [wrap]
        if min(gaps) > 12.6 or max(gaps) < 17.4 or len(set(gaps)) < len(gaps) - 1:
            continue
        return starts
    raise RuntimeError('no schedule')


def neigh_tracks(starts):
    """ヒヒィーンの キー（EV_LOOP 秒の中）：{名前: [(秒, 値, 次までの動き)]}・招く右前足を出す間 [(はじめ, おわり)]"""
    K = {k: [] for k in ('u', 'vib', 'm', 'ear', 'mane', 'mf', 'tail')}
    beck = []
    for s in starts:
        pl = neigh_plan(s)
        up, dn, end = s + NEIGH_UP, pl['down'], pl['end']
        K['u'] += [(s, 0, 'ease-out'), (up, 1, 'linear'), (dn, 1, 'ease-in-out'), (end, 0, 'linear')]
        v = [(up + 0.1, 0, 'ease-in-out')]                # 頭の ふるえ（鳴いている間・0.24秒で 1往復）
        t, k = up + 0.1, 0
        while t + 0.12 < dn - 0.1:
            t += 0.12
            v.append((round(t, 3), 1.6 if k % 2 == 0 else -1.6, 'ease-in-out'))
            k += 1
        v.append((round(dn - 0.02, 3), 0, 'linear'))
        K['vib'] += v
        K['m'] += [(s + 0.14, 0, 'ease-out'), (s + 0.3, 1, 'linear'), (dn - 0.12, 1, 'ease-in'), (dn + 0.05, 0, 'linear')]
        K['ear'] += [(s + 0.05, 0, 'ease-out'), (s + 0.42, 1, 'linear'), (dn, 1, 'ease-in-out'), (end - 0.02, 0, 'linear')]
        K['mane'] += [(s, 0, 'ease-out'), (up + 0.08, 1, 'linear'), (dn, 1, 'ease-in-out'), (end, 0, 'linear')]
        mf = [(up + 0.08, 0, 'ease-in-out')]              # たてがみが ゆれる（0.6秒で 1往復）
        t, k = up + 0.08, 0
        while t + 0.3 < dn:
            t += 0.3
            mf.append((round(t, 3), -2.2 if k % 2 == 0 else 1.4, 'ease-in-out'))
            k += 1
        mf.append((round(dn + 0.2, 3), 0, 'linear'))
        K['mf'] += mf
        K['tail'] += [(s + 0.2, 0, 'ease-in-out'), (s + 0.42, 9, 'ease-in-out'), (s + 0.72, -5, 'ease-in-out'), (s + 1.02, 7, 'ease-in-out'),
                      (s + 1.36, -3, 'ease-in-out'), (s + 1.75, 0, 'linear')]
        beck.append((pl['b0'], round(pl['b0'] + pl['n'] * BECKON_S, 3)))
    for k in K:
        K[k] = [(0.0, 0, 'linear')] + [(round(t, 3), v, e) for t, v, e in K[k]] + [(EV_LOOP, 0, 'linear')]
        ts = [t for t, _, _ in K[k]]
        assert all(a <= b + 1e-9 for a, b in zip(ts, ts[1:])), (k, ts)
    for a, b in beck:
        assert abs(a / BECKON_S - round(a / BECKON_S)) < 1e-6 and abs(b / BECKON_S - round(b / BECKON_S)) < 1e-6, (a, b)
    return K, beck


def merge(a, b):
    """2つの キー列を 時刻で まとめる → [(秒, (値a, 値b), 次までの動き)]。どの あいだも 動くのは かたほうだけ（首の上げ下げと ふるえは かさならない）"""
    def at(keys, t):
        for (t0, v0, e), (t1, v1, _) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                return v1 if t1 == t0 else v0 + (v1 - v0) * ease_val(e, (t - t0) / (t1 - t0))
        return keys[-1][1]

    def ease_at(keys, t):
        e = keys[0][2]
        for t0, _, e0 in keys:
            if t0 <= t + 1e-9:
                e = e0
        return e
    ts = sorted(set([t for t, _, _ in a] + [t for t, _, _ in b]))
    out = []
    for t, t1 in zip(ts, ts[1:] + [ts[-1]]):
        da = abs(at(a, t1) - at(a, t)) > 1e-9
        db = abs(at(b, t1) - at(b, t)) > 1e-9
        assert not (da and db), ('both move', t, t1)
        e = ease_at(a, t) if da else ease_at(b, t) if db else 'linear'
        out.append((t, (at(a, t), at(b, t)), e))
    return out


def ease_val(e, x):
    if e == 'linear':
        return x
    if e in ('ease-out',):
        return 1 - (1 - x) ** 2
    if e in ('ease-in',):
        return x * x
    return 0.5 - 0.5 * math.cos(math.pi * x)


def steps_of(keys, th=0.0):
    """値が th より大きい間 1・ほかは 0 の 切りかえ [(秒, 0|1)]（上がりはじめ → 下がりきり）"""
    out = [(0.0, 0)]
    for (t0, v0, _), (t1, v1, _) in zip(keys, keys[1:]):
        if v0 <= th < v1:
            out.append((t0, 1))
        elif v0 > th >= v1:
            out.append((t1, 0))
    return out


# ---------- 小判 ----------
GOLD, GOLD_SH, GOLD_HI, OUT = LM.GOLD, LM.GOLD_SH, LM.GOLD_HI, LM.OUT
# (x, 高さ, 落ちる秒, 回る秒, かたむき, 回り方, きらっ の秒)。うしろ（蹄鉄と招き馬の うしろ）・手前（左右だけ）。
# 回り方：f＝くるっと うらがえる（よこに 細くなって 裏へ）・p＝少しだけ 回って もどる。きらっ：0＝なし
KOBAN = dict(
    back=[(34, 26, 9.0, 3.4, 16, 'p', 0), (148, 27, 8.4, 4.0, -14, 'f', 0), (246, 25, 9.6, 3.0, 12, 'p', 0), (318, 27, 8.8, 3.6, -18, 'f', 0),
          (466, 26, 9.2, 3.2, 15, 'p', 0), (548, 28, 8.6, 4.2, -12, 'f', 0), (650, 25, 9.4, 2.8, 18, 'p', 0), (748, 27, 8.2, 3.8, -16, 'f', 0)],
    front=[(22, 38, 5.6, 3.2, -20, 'f', 3.1), (86, 34, 6.2, 2.6, 22, 'p', 0), (150, 40, 5.2, 3.6, -24, 'p', 2.7), (206, 35, 6.0, 2.9, 18, 'f', 0),
           (582, 36, 5.8, 3.0, -18, 'p', 3.4), (646, 41, 5.4, 3.4, 24, 'f', 0), (712, 34, 6.4, 2.7, -22, 'p', 2.9), (762, 37, 5.0, 3.8, 20, 'f', 0)])
SWAY = ((9, 10, 3.1), (12, 14, 2.6), (7, 18, 2.2))     # ゆれ（よこ・かたむき・秒）3とおり
FALL = (-40, 362)                # 落ちる はじめと おわり（絵の座標・枠の外）
KOBAN_H = 24                     # 小判の絵の高さ（1まいずつ のばす）


def koban_svg(h, gid):
    """小判（まん中が 0 0・高さ h）：金の だ円・太い線・内がわの線・ござ目・まん中の刻印・上下の丸い印・つや"""
    a, b = h / 2, h / 2 * 0.62
    s = (f"<ellipse rx='{num(b)}' ry='{num(a)}' fill='url(#{gid})' stroke='{OUT}' stroke-width='2.4'/>"
         f"<ellipse rx='{num(b * .74)}' ry='{num(a * .8)}' fill='none' stroke='{GOLD_SH}' stroke-width='1.1'/>")
    for k in range(-5, 6):
        y = k * a * 0.13
        hw = b * .7 * math.sqrt(max(0.0, 1 - (y / (a * .78)) ** 2))
        if abs(k) >= 3 and hw > 1.5:
            s += f"<path d='M{num(-hw)} {num(y)}H{num(hw)}' stroke='{GOLD_SH}' stroke-width='.8' opacity='.85'/>"
    s += (f"<rect x='{num(-b * .3)}' y='{num(-a * .3)}' width='{num(b * .6)}' height='{num(a * .6)}' rx='1' fill='#FFF3C4' stroke='{GOLD_SH}' stroke-width='.8'/>"
          f"<path d='M{num(-b * .14)} {num(-a * .12)}h{num(b * .28)}M{num(-b * .14)} {num(a * .04)}h{num(b * .28)}M0 {num(-a * .2)}v{num(a * .36)}' "
          f"stroke='#B07A1A' stroke-width='.9' stroke-linecap='round'/>"
          f"<circle cy='{num(-a * .64)}' r='{num(a * .08)}' fill='{GOLD}' stroke='{GOLD_SH}' stroke-width='.6'/>"
          f"<circle cy='{num(a * .64)}' r='{num(a * .08)}' fill='{GOLD}' stroke='{GOLD_SH}' stroke-width='.6'/>"
          f"<path d='M{num(-b * .7)} {num(-a * .2)} C{num(-b * .62)} {num(-a * .6)} {num(-b * .3)} {num(-a * .82)} {num(b * .05)} {num(-a * .86)}' "
          f"fill='none' stroke='#FFFFFF' stroke-width='{num(max(1.2, h * .07))}' stroke-linecap='round' opacity='.85'/>")
    return s


def koban_layer(which, n):
    """降る小判の <svg> の中身（780×320 の絵の座標）。1まいずつ：位置（x）→ 落ちる（.lwKy）→ ゆれ（.lwKx）→ かたむき → 回る（.lwKf・.lwKp）→ 大きさ。
       きらっ（.lwKs）は ゆれの中（回らない）"""
    gid, kid = f'lwKg{n}', f'lwKo{n}'
    defs = (f"<defs><linearGradient id='{gid}' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#FFF4B8'/>"
            f"<stop offset='.45' stop-color='#F5C542'/><stop offset='1' stop-color='#D18A22'/></linearGradient>"
            f"<g id='{kid}'>{koban_svg(KOBAN_H, gid)}</g></defs>")
    body = ''
    for i, (x, h, Tf, Ft, tilt, kind, gl) in enumerate(KOBAN[which]):
        ph = (i * 0.618 + (0.31 if which == 'front' else 0)) % 1            # 落ちる位相（ばらばらに）
        sw = SWAY[i % 3]
        glint = ''
        if gl:
            a, r = h / 2, h * 0.3
            pts = ' '.join(f'{num(math.sin(k * math.pi / 4) * (r if k % 2 == 0 else r * .22))},{num(-math.cos(k * math.pi / 4) * (r if k % 2 == 0 else r * .22))}'
                           for k in range(8))
            glint = (f"<g transform='translate({num(-a * .2)} {num(-a * .42)})'><g class='lwKs' style='animation-duration:{gl:g}s;animation-delay:{num(-(i * 0.29 % 1) * gl)}s'>"
                     f"<polygon points='{pts}' fill='#FFFFFF' stroke='#E9B23A' stroke-width='.7' stroke-linejoin='round'/></g></g>")
        body += (f"<g transform='translate({x} 0)'><g class='lwKy' style='animation-duration:{Tf:g}s;animation-delay:{num(-ph * Tf)}s'>"
                 f"<g class='lwKx lwKx{i % 3}' style='animation-delay:{num(-(i * 0.37 % 1) * sw[2])}s'>"
                 f"<g transform='rotate({tilt})'><g class='lwK{kind}' style='animation-duration:{Ft:g}s;animation-delay:{num(-(i * 0.53 % 1) * Ft)}s'>"
                 f"<use href='#{kid}' transform='scale({num(h / KOBAN_H, 3)})'/></g></g>{glint}</g></g></g>")
    return defs + body


# ---------- 招き馬（rig） ----------
def back_hoof():
    """ひづめの裏（前へ おれて 下に たれた時に見える がわ）：表と同じ形・金の かべ・白い毛のふち（手首がわ）・つや。
       たての のびが − で 上下が 入れかわるので、ここでは 上下を ひっくり返して描く（下が 手首）"""
    P, L = LM.P, LM.L
    return (P('M24 140 C20 126 29 115 43 115 C57 115 66 125 63 138 C61 147 51 152 40 151 C32 150 26 146 24 140 Z', GOLD, LM.LW2 + 0.6)
            + f"<path d='M26.5 131 C27 121 34 117 43 117 C53 117 60 121 61 131 C56 125 50 123 43 123 C36 123 30 125 26.5 131 Z' fill='{GOLD_SH}' opacity='.75'/>"
            + L('M28.5 133 C35 128 52 128 59 133', 2.0, GOLD_SH)
            + "<path d='M26.5 142 C33 147.5 51 148.5 60.5 141 C58 148 51 152 40 151 C32 150 27.5 146.5 26.5 142 Z' fill='#FFFFFF'/>"
            + L('M26.5 142 C33 147.5 51 148.5 60.5 141', 2.2)
            + f"<path d='M31 137.5 C34 140.5 38 141.5 44 141' fill='none' stroke='{GOLD_HI}' stroke-width='2.2' stroke-linecap='round'/>")


def open_mouth():
    """開けた口（鳴く）：こい茶の口・上の歯・桃色の舌"""
    return (f"<path d='M103 162.5 C109 160 131 160 137 162.5 C139 170 131 178.5 120 178.5 C109 178.5 101 170 103 162.5 Z' fill='#4A2E36' stroke='{OUT}' stroke-width='2.4' stroke-linejoin='round'/>"
            "<path d='M106.5 163.6 C112 162 128 162 133.5 163.6 L132.6 166.3 C127 165.2 113 165.2 107.4 166.3 Z' fill='#FFFFFF'/>"
            "<path d='M110 174.5 C113 170.5 127 170.5 130 174.5 C127 177.6 113 177.6 110 174.5 Z' fill='#F28C9B'/>")


def rig():
    """lucky_maneki.maneki_svg の rig：動かす部品を <g class=…> で包む・足す"""
    G = lambda cls: (lambda x: f"<g class='{cls}'>{x}</g>")
    BY = LM.BY

    def arm(arm_svg, hoof_svg):
        back = f"<g transform='translate(0 {BY})'>{back_hoof()}</g>"
        a = pv('lwA1', P_EL, arm_svg + pv('lwW1', P_WR, f"<g class='lwV1a'>{hoof_svg}</g><g class='lwV1b'>{back}</g>"))
        b = pv('lwA0', P_EL, arm_svg + pv('lwW2', P_WR, f"<g class='lwHf'>{hoof_svg}</g><g class='lwHb'>{back}</g>"))
        return f"<g class='lwAA'>{a}</g><g class='lwAB'>{b}</g>"
    mouth_o = pv('lwMo', P_MO, pv('lwMq', P_MO, open_mouth()))
    return dict(tail=lambda x: pv('lwTl', P_TL, x), body=lambda x: pv('lwBd', P_BD, x), mane=lambda x: pv('lwMn', P_MN, pv('lwMf', P_MN, x)),
                head=lambda x: pv('lwHd', P_NK, pv('lwHv', P_NK, x)), ear_l=lambda x: pv('lwEL', P_EAR[0], x), ear_r=lambda x: pv('lwER', P_EAR[1], x),
                muzzle=lambda x: pv('lwMz', P_MZ, x), feat=lambda x: pv('lwFe', P_FE, x), pupil=G('lwPu'), forelock=lambda x: pv('lwFl', P_FL, x),
                nose=lambda x: pv('lwNs', P_MZ, x), mouth=G('lwMc'),
                under=lambda _: f"<g class='lwUn'><ellipse cx='120' cy='149' rx='41' ry='22' fill='{LM.MUZ_SH}'/></g>",
                mouth_open=lambda _: f"<g class='lwMv'>{mouth_o}</g>", arm=arm)


def prefix_ids(s, pre='lw'):
    for i in sorted(set(re.findall(r"id='([^']+)'", s)), key=len, reverse=True):
        s = s.replace(f"id='{i}'", f"id='{pre}{i}'").replace(f'url(#{i})', f'url(#{pre}{i})')
    return s


def svg_layer(inner, cls='lwL'):
    return f'<svg class="{cls}" viewBox="0 0 780 320" width="390" height="160" aria-hidden="true">{inner}</svg>'


def tracks():
    """CSS のキーフレーム（8秒の1回り・招く1回・ヒヒィーンの1回り）と、ヒヒィーンの予定"""
    css = ''
    # 8秒の1回り：ひづめ（.lwW1）・右前足（.lwA1）・表と裏（.lwV1a・.lwV1b）
    css += kf('lwW1K', R_KEYS, CYCLE, lambda th: T(s=fold(th)), 2)
    css += kf('lwA1K', R_KEYS, CYCLE, lambda th: T(r=arm_of(th)[0], s=(1, arm_of(th)[1])), 2)
    cr = crossings(R_KEYS)
    css += kf_step('lwV1aK', [(0, 1)] + [(t, 0 if bk else 1) for t, bk in cr], CYCLE, nd=2)
    css += kf_step('lwV1bK', [(0, 0)] + [(t, 1 if bk else 0) for t, bk in cr], CYCLE, nd=2)
    # 招く1回（BECKON_S 秒で くり返す）
    css += kf('lwW2K', BECKON, BECKON_S, lambda th: T(s=fold(th)), 2)
    css += kf('lwA0K', BECKON, BECKON_S, lambda th: T(r=arm_of(th)[0], s=(1, arm_of(th)[1])), 2)
    cb = crossings(BECKON)
    css += kf_step('lwHfK', [(0, 1)] + [(t, 0 if bk else 1) for t, bk in cb], BECKON_S, nd=2)
    css += kf_step('lwHbK', [(0, 0)] + [(t, 1 if bk else 0) for t, bk in cb], BECKON_S, nd=2)
    # ヒヒィーン（EV_LOOP 秒）
    starts = schedule()
    K, beck = neigh_tracks(starts)
    L = EV_LOOP
    css += kf_step('lwAAK', [(0, 1)] + [x for a, b in beck for x in ((a, 0), (b, 1))], L)
    css += kf_step('lwABK', [(0, 0)] + [x for a, b in beck for x in ((a, 1), (b, 0))], L)
    css += kf('lwHdK', K['u'], L, lambda u: T(t=(0, -8 * u), r=-5 * u, s=(1, 1 - 0.03 * u)))
    css += kf('lwFlK', K['u'], L, lambda u: T(t=(0, -3 * u), s=(1, 1 - 0.15 * u)))
    css += kf('lwHvK', K['vib'], L, lambda r: T(r=r), dflt='ease-in-out')
    css += kf('lwFeK', K['u'], L, lambda u: T(t=(0, -6 * u), s=(1, 1 - 0.16 * u)))
    css += kf('lwPuK', K['u'], L, lambda u: T(t=(0, -3.4 * u)))
    css += kf('lwMzK', K['u'], L, lambda u: T(t=(0, -11 * u), s=(1 + 0.09 * u, 1 + 0.09 * u)))          # 鼻先と 鼻の穴・口（.lwMz・.lwNs）
    css += kf('lwBdK', K['u'], L, lambda u: T(r=-1 * u, s=(1, 1 + 0.014 * u)))
    css += kf('lwELK', K['ear'], L, lambda e: T(r=-18 * e, s=(1, 1 - 0.12 * e)))
    css += kf('lwERK', K['ear'], L, lambda e: T(r=18 * e, s=(1, 1 - 0.12 * e)))
    css += kf('lwMnK', K['mane'], L, lambda m: T(t=(0, -3 * m), r=-3 * m))
    css += kf('lwMfK', K['mf'], L, lambda r: T(r=r), dflt='ease-in-out')
    css += kf('lwTlK', K['tail'], L, lambda r: T(r=r))
    css += kf('lwMoK', K['m'], L, lambda m: T(s=(1, max(m, 0.001))))
    css += kf_step('lwUnK', steps_of(K['u']), L)
    css += kf_step('lwMvK', steps_of(K['m'], 0.0), L)
    css += kf_step('lwMcK', [(t, 1 - v) for t, v in steps_of(K['m'], 0.0)], L)
    return css, starts


def inline(alt=ALT):
    """(html, css)。html は <div class="bnr lw">（判定画面の <img class="bnr"> と入れかえる）"""
    P = LB.parts(rig())
    k_css, starts = tracks()
    html = (f'<div class="bnr lw" role="img" aria-label="{alt}">'
            + svg_layer(prefix_ids(P['defs'] + P['bg']))
            + svg_layer(koban_layer('back', 1), 'lwL lwK')
            + svg_layer(prefix_ids(P['shoe'] + P['maneki']))
            + svg_layer(P['fg'])
            + svg_layer(koban_layer('front', 2), 'lwL lwK')
            + '</div>')
    mv = ('lwTl', 'lwBd', 'lwMn', 'lwMf', 'lwHd', 'lwHv', 'lwFl', 'lwEL', 'lwER', 'lwMz', 'lwNs', 'lwFe', 'lwPu', 'lwMo', 'lwMq',
          'lwA0', 'lwA1', 'lwW1', 'lwW2', 'lwKy', 'lwKx', 'lwKf', 'lwKp', 'lwKs')
    loop = lambda c, k=None: f'.lw .{c}{{animation:{k or c + "K"} {EV_LOOP:g}s linear infinite}}'
    css = ('.lw{position:relative;overflow:hidden;isolation:isolate}'
           '.lw .lwL{position:absolute;left:0;top:0;display:block;overflow:hidden}'
           + ','.join(f'.lw .{c}' for c in mv) + '{transform-box:view-box;transform-origin:0 0}'
           # 8秒の1回り（がたがた → 振り下ろす）
           + f'.lw .lwW1{{animation:lwW1K {CYCLE:g}s linear infinite}}.lw .lwA1{{animation:lwA1K {CYCLE:g}s linear infinite}}'
           + f'.lw .lwV1a{{animation:lwV1aK {CYCLE:g}s step-end infinite}}.lw .lwV1b{{opacity:0;animation:lwV1bK {CYCLE:g}s step-end infinite}}'
           # 招く右前足（ヒヒィーンの間だけ出す・BECKON_S 秒で くり返す）
           + f'.lw .lwAA{{animation:lwAAK {EV_LOOP:g}s step-end infinite}}.lw .lwAB{{opacity:0;animation:lwABK {EV_LOOP:g}s step-end infinite}}'
           + f'.lw .lwW2{{animation:lwW2K {BECKON_S:g}s linear infinite}}.lw .lwA0{{animation:lwA0K {BECKON_S:g}s linear infinite}}'
           + f'.lw .lwHf{{animation:lwHfK {BECKON_S:g}s step-end infinite}}.lw .lwHb{{opacity:0;animation:lwHbK {BECKON_S:g}s step-end infinite}}'
           # ヒヒィーン（EV_LOOP 秒）
           + ''.join(loop(c) for c in ('lwHd', 'lwFl', 'lwFe', 'lwPu', 'lwMz', 'lwBd', 'lwEL', 'lwER', 'lwMn', 'lwTl', 'lwMo'))
           + loop('lwNs', 'lwMzK')
           + ''.join(f'.lw .{c}{{animation:{c}K {EV_LOOP:g}s ease-in-out infinite}}' for c in ('lwHv', 'lwMf'))
           + f'.lw .lwMo{{transform:scale(1,.001)}}'
           + f'.lw .lwMq{{animation:lwMqK .16s ease-in-out infinite alternate}}@keyframes lwMqK{{from{{transform:scale(1,1)}}to{{transform:scale(1.03,.9)}}}}'
           + f'.lw .lwUn{{opacity:0;animation:lwUnK {EV_LOOP:g}s step-end infinite}}'
           + f'.lw .lwMv{{opacity:0;animation:lwMvK {EV_LOOP:g}s step-end infinite}}.lw .lwMc{{animation:lwMcK {EV_LOOP:g}s step-end infinite}}'
           # 小判
           + f'.lw .lwKy{{animation:lwKy 9s linear infinite}}'
           + f'@keyframes lwKy{{from{{transform:translate(0px,{FALL[0]}px)}}to{{transform:translate(0px,{FALL[1]}px)}}}}'
           + ''.join(f'.lw .lwKx{j}{{animation:lwKx{j} {d:g}s ease-in-out infinite alternate}}'
                     f'@keyframes lwKx{j}{{from{{transform:translate({-a}px,0px) rotate({-r}deg)}}to{{transform:translate({a}px,0px) rotate({r}deg)}}}}'
                     for j, (a, r, d) in enumerate(SWAY))
           + '.lw .lwKf{animation:lwKf 3s ease-in-out infinite}.lw .lwKp{animation:lwKp 3s ease-in-out infinite}'
           + '@keyframes lwKf{0%{transform:scale(1,1)}50%{transform:scale(-1,1)}100%{transform:scale(1,1)}}'
           + '@keyframes lwKp{0%{transform:scale(1,1)}50%{transform:scale(.3,1)}100%{transform:scale(1,1)}}'
           + '.lw .lwKs{transform:scale(0);animation:lwKs 3s linear infinite}'
           + '@keyframes lwKs{0%,74%{transform:scale(0) rotate(0)}84%{transform:scale(1) rotate(25deg)}94%,100%{transform:scale(0) rotate(50deg)}}'
           + k_css
           + '@media (prefers-reduced-motion:reduce){.lw *{animation:none!important}.lw .lwK{display:none}}')
    return html, css


def judge_inline(fn, alt=ALT):
    """判定画面（Judge_Lucky.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="bnr lw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(alt)
    page, k = re.subn(r'<div class="bnr lw" .*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* 開運の壁紙：小判が降って、招き馬が 8秒ごとに 右の前足を がたがた → 一気に 振り下ろす・ときどき 上を向いて 招きながら いななく（lucky_wall.py） */\n{css}\n/* /開運の壁紙 */\n'
    if '/* 開運の壁紙：' in page:
        page = re.sub(r'/\* 開運の壁紙：.*?/\* /開運の壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def plan():
    starts = schedule()
    prev = None
    for s in starts:
        pl = neigh_plan(s)
        gap = '' if prev is None else f'（前から {s - prev:5.2f}秒）'
        print(f'{s:7.2f}秒（8秒の中の {pl["o"]:4.2f}秒）{gap} 招く：' + '・'.join(f'{pl["b0"] + k * BECKON_S:.2f}' for k in range(pl['n']))
              + ('（3秒の 振り下ろしも）' if pl['swing'] else '') + f'  首が もどる：{pl["end"]:.2f}')
        prev = s
    print(f'つなぎ目：{EV_LOOP + starts[0] - starts[-1]:.2f}秒（{EV_LOOP:g}秒で1回り）')


if __name__ == '__main__':
    if '--plan' in sys.argv:
        plan()
    else:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1])
