"""ハロウィンの壁紙の動き（まさちゃんの指定「ハロウィン エフェクト:ドラキュラが羽をパタパタさせて少しだけ飛ぶ(2.7秒)、その後上手く飛べなくて
   落ちてしまう。落ちたらガイコツとかぼちゃが笑う(2秒) 馬は常にドラキュラの動きを顔と首の動きで追っている。 5回に1回ランダムで、ドラキュラちゃんと
   上に飛べて画面からフェードアウト、2秒後に落ちてきてガイコツとかぼちゃが笑う。 8秒〜11秒に一回リピート」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">：視差効果を減らす なら これだけ）。その上に 動く時の 下の絵（ドラキュラと その影・顔のある かぼちゃ3つ・
     ドクロなし：flat/halloween_banner.py を HALLOWEEN_BASE=1）・馬の 首と頭の コマ（flat/halloween_run.py のシート・背景ごと 切りぬいた・すき通しなし）・
     ドラキュラ（flat/event_art.py の vampire_bits を 部品ごとに <g> で包んだ SVG：止まっている時は いまの絵と同じ形・同じ場所。マントは 左右の 半分を
     うでと いっしょに 肩を 中心に まわして、羽のように はばたかせる）・顔のある かぼちゃ3つと ドクロ（pumpkin_bits・skull_bits：止まっている時は
     いまの絵と同じ。笑う時は pumpkin_laugh・skull_laugh の 顔に かえて、ぴょこぴょこ はねる・かぼちゃは 口を ぱくぱく・ドクロは あごを カタカタ）
   - 8〜11秒ごと（GAP・ばらばら）に 1回。10回ぶん（N_EV）で1回り（いつも同じ予定：schedule）。10回のうち 2回（N_UP：5回に1回）は うまく 飛べる回
     1回の中の 時刻（秒）：
       ふつうの回（n）：0〜0.18 しゃがんで マントを 上げる → 0.18〜 マントを 羽のように パタパタ（0.28秒に1回）・1.5秒までに 少しだけ 上へ →
             1.86〜 うまく いかなくて あせる（汗・パタパタが 小さく はやくなる・少し 下がる）→ 2.7 とべなくて 落ちる（目を ぎゅっと＞＜・口を あける・
             マントが 上へ ばたばた・足を ばたばた）→ 3.06 どすん（つぶれて はねかえる）→ 3.06〜5.1 ドクロと かぼちゃが 笑う（2秒）・
             ドラキュラは てれわらい（＾＾・汗・まっかな ほお・首を かしげる）→ 5.4 もとの形
       うまく 飛べる回（u）：1.4 まで ふつうの回と 同じ → にこっ（＾＾）→ ぐんぐん 上へ・2.1〜2.7 うすくなって 画面の上へ 消える（フェードアウト）→
             2秒後（4.7）に 画面の上から 落ちてくる（＞＜・口を あける・マントが 上へ ばたばた）→ 5.25 どすん → 5.25〜7.3 ドクロと かぼちゃが 笑う → 7.6 もとの形
   - 馬は いつも ドラキュラの 頭を 見る（馬の目から ドラキュラの 頭への 向きで 見上げる ぐあいを 決め、少し おくれて なめらかに ついていく：horse_e）
   - ページを開くと 0秒（いまの絵と同じ形）から。1回目は 2秒（FIRST）
   - キャンバスでは /_blob/<id>：止まった絵は blobs20.json の halloween・下の絵（base）と コマのシート（look）は halloween_blobs.json。置く場所は halloween_run.json
   クラスの名前は hl…（的中ボタンの .hw… とは別）
   python3 halloween_wall.py --judge <Judge_Halloween.dc.html> <halloween_blobs.json> <halloween_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 halloween_wall.py --plan                                                                       → 予定（はじまる秒）"""
import sys, os, re, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'flat'))
import event_art as A

ALT = ('むらさきの夜の満月とお城を背に、魔女の帽子をかぶった芦毛の競走馬（むらさきのゼッケン1）と、マントをひろげるドラキュラ、光るかぼちゃとドクロのイラスト'
       '（ときどき ドラキュラが マントを パタパタさせて 少しだけ 飛ぶけれど、うまく 飛べずに 落ちて、ドクロと かぼちゃが 笑う。5回に1回は 上へ 飛んでいって 消え、'
       '2秒後に 落ちてくる。馬は いつも ドラキュラを 目で追っている）')
GAP = (8.0, 11.0)                # つぎの回まで（まさちゃん「8秒〜11秒に一回リピート」：はじまりから はじまりまで）
N_EV = 10                        # 1回りの 回数
N_UP = 2                         # そのうち うまく 飛べる回（まさちゃん「5回に1回ランダムで」）
FIRST = 2.0                      # ページを開いて 1回目
SEED = 25                        # 予定の 乱数の種（schedule・check_schedule：2回目と 8回目が うまく 飛べる回＝あいだが 6回と 4回）
EV_LEN = dict(n=5.4, u=7.6)      # 1回の長さ（ふつうの回・うまく 飛べる回。つぎの回まで いつも 0.4秒 以上 あく：8−7.6）

VAMP_AT, VAMP_S = (108.0, 300.0), 0.92        # いまの絵の ドラキュラの 場所と 大きさ（flat/halloween_banner.py）
SHADOW = (66.0, 7.0, '#0E0818', .5)           # ドラキュラの 影（780×320 の 座標）
SH_L = (-22.0, -106.0)                        # 左の 肩（マントの 左半分と 左うでが まわる 中心。右は 左右を うらがえして 同じ動き）
HIP_L, HIP_R = (-11.5, -38.0), (11.5, -38.0)  # 足の つけね
NECK = (0.0, -120.0)                          # 首（頭が かたむく 中心）
HEAD_Y = -146.0                               # 頭の まん中（馬が 見る所）
PUMPKINS = ((560.0, 306.0, 78.0, 58.0, -4.0), (640.0, 310.0, 54.0, 40.0, 3.0), (216.0, 312.0, 46.0, 34.0, 4.0))   # 顔のある かぼちゃ（x, y, はば, 高さ, 顔の向き）
SKULL_AT, SKULL_S = (690.0, 308.0), 1.05
# 笑う時の はねかた：(はじまりの おくれ 秒, 1回の 秒, はねる 高さ, かたむき 度)。かぼちゃ 560・640・216・ドクロ（ドクロの あごは JAW_PER ごとに カタカタ）
LAUGHERS = ((0.00, 0.26, 5.0, 4.0), (0.06, 0.22, 4.0, 5.0), (0.10, 0.24, 4.0, 6.0), (0.03, 0.25, 3.0, 6.0))
JAW, JAW_PER = 4.5, 0.17                      # ドクロの あごが さがる はば・カタカタ 1回の 秒

# ---- 1回の中の 時刻（秒）
T_PREP = 0.18                    # しゃがんで マントを 上げる
FLAP, FLAP_DN = 0.28, 0.12       # パタパタ 1回（下へ あおぐ 0.12秒・上げる 0.16秒）
N_FLAP = 6                       # ふつうの回：ふつうの パタパタ 6回（〜1.86）→ あせって はやい パタパタ 4回（〜2.7）
FAST, FAST_DN, N_FAST = 0.21, 0.09, 4
N_FLAP_U = 9                     # うまく 飛べる回：ふつうの パタパタ 9回（〜2.7）
UP, DN = 28.0, -16.0             # マントの かたむき（上げた・あおいだ：度）
UP_F, DN_F = 22.0, -8.0          # あせって 小さく
FALL_W = (46.0, 34.0, 0.08)      # 落ちる時の ばたばた（上・下・半回りの 秒）
T_UP = 1.50                      # 少しだけ 飛ぶ（ここまでに 上がる）
RISE = -52.0                     # どれだけ 上がるか（ドラキュラの座標：足もと 0）
T_SWEAT = 1.86                   # あせる（はやい パタパタの はじまり）
T_FAIL = 2.70                    # とべなくて 落ちる（まさちゃん「2.7秒」）
T_LAND = dict(n=3.06, u=5.25)    # どすん（ふつうの回は 落ちるのに 0.36秒）
T_HAPPY = 1.40                   # うまく 飛べる回：にこっ
T_FADE = (2.10, 2.70)            # うすくなって 消える
TOP = -420.0                     # 画面の 外（上）
T_DROP = 4.70                    # 2秒後に 落ちてくる（まさちゃん「2秒後に落ちてきて」・0.55秒で 地面）
LAUGH = 2.0                      # 笑う（まさちゃん「笑う(2秒)」）
T_SHY = 0.45                     # どすんの あと、てれわらいに かわるまで
T_BACK = 0.40                    # おわりの 何秒前から もとの形へ
EASE = {'linear': 'linear', 'ease-in': 'ease-in', 'ease-out': 'ease-out', 'ease-in-out': 'ease-in-out',
        'quad-in': 'cubic-bezier(.3333,0,.6667,.3333)', 'quad-out': 'cubic-bezier(.3333,.6667,.6667,1)'}
BEZ = {'ease-in': (.42, 0, 1, 1), 'ease-out': (0, 0, .58, 1), 'ease-in-out': (.42, 0, .58, 1),
       'quad-in': (1 / 3, 0, 2 / 3, 1 / 3), 'quad-out': (1 / 3, 2 / 3, 2 / 3, 1)}


# ---------------------------------------------------------------- 予定
def schedule(seed=SEED):
    """1回りの (はじまる秒, 回の種類 n／u) と 1回りの 長さ"""
    rnd = random.Random(seed)
    gaps = [round(rnd.uniform(*GAP), 2) for _ in range(N_EV)]
    ups = set(rnd.sample(range(1, N_EV - 1), N_UP))
    st = [FIRST]
    for g in gaps[:-1]:
        st.append(round(st[-1] + g, 2))
    return list(zip(st, ['u' if k in ups else 'n' for k in range(N_EV)])), round(sum(gaps), 2)


def check_schedule(plan, loop):
    st = [s for s, _ in plan] + [loop + FIRST]
    gaps = [b - a for a, b in zip(st, st[1:])]
    assert all(GAP[0] - 1e-6 <= g <= GAP[1] + 1e-6 for g in gaps), gaps
    assert all(st[k] + EV_LEN[plan[k][1]] + 0.4 <= st[k + 1] + 1e-6 for k in range(N_EV)), 'つぎの回と かさなる'
    ups = [k for k, (_, t) in enumerate(plan) if t == 'u']
    assert len(ups) == N_UP and ups[0] > 0 and plan[-1][1] == 'n' and all(b - a > 2 for a, b in zip(ups, ups[1:])), ups
    assert min(gaps) <= 8.6 and max(gaps) >= 10.4, '短いのと 長いのが ない'


PLAN, LOOP = schedule()


# ---------------------------------------------------------------- 数と キーフレーム
def num(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return '0' if s in ('-0', '', '-') else s


def pct(t):
    s = f'{t / LOOP * 100:.3f}'.rstrip('0').rstrip('.')         # 約1ミリ秒 きざみ
    return (s or '0') + '%'


def tr(x=0.0, y=0.0):
    return f'translate({num(x)}px,{num(y)}px)'


class Keys:
    """1回の キーを 時刻の順に つむ（to：その時刻に その値・e：つぎの キーまでの 動き）。L：1回の長さ"""
    def __init__(self, rest, L, e='linear'):
        self.k = [(0.0, rest, e)]
        self.L = L

    def to(self, t, v, e='linear'):
        t = round(t, 4)
        assert t > self.k[-1][0], (t, self.k[-1])
        self.k.append((t, v, e))
        return self

    def at(self, t, v, e='linear'):
        """その時刻に その値（前の キーと 同じ時刻なら、前の キーの 動きだけ かえる）"""
        t = round(t, 4)
        lt, lv, _ = self.k[-1]
        if t > lt + 1e-9:
            return self.to(t, v, e)
        assert abs(t - lt) < 1e-9 and lv == v, (t, v, self.k[-1])
        self.k[-1] = (lt, lv, e)
        return self

    def hold(self, t, e='linear'):
        return self.to(t, self.k[-1][1], e)

    def end(self):
        if self.k[-1][0] < self.L - 1e-9:
            self.to(self.L, self.k[0][1])
        assert self.k[-1][1] == self.k[0][1] and self.k[-1][0] <= self.L + 1e-9, (self.k[-1], self.k[0])
        return self.k


def everywhere(keys, plan=None):
    """回の種類ごとの キー {n: […], u: […]}（はじめと おわりは 止まっている値）→ 1回り（10回ぶん）"""
    plan = plan or PLAN
    rest = keys['n'][0][1]
    out = [(0.0, rest, 'linear')]
    for s, typ in plan:
        k = keys[typ]
        assert k[0][1] == rest and k[-1][1] == rest and k[0][0] == 0
        out += [(round(s + t, 4), v, e) for t, v, e in k]
    out.append((LOOP, rest, 'linear'))
    ts = [k[0] for k in out]
    assert all(b > a for a, b in zip(ts, ts[1:])), 'キーの 時刻が ならんでいない'
    out = [k for i, k in enumerate(out) if i in (0, len(out) - 1) or not (out[i - 1][1] == k[1] == out[i + 1][1])]
    return [(t, v, e if i + 1 < len(out) and out[i + 1][1] != v else None) for i, (t, v, e) in enumerate(out)]


def kf(name, keys, fmt):
    """回の種類ごとの キー → (@keyframes, ふだんの 動き)：いちばん多い 動きを アニメーションの 動きにして、ちがう キーだけ 書く"""
    ks = everywhere(keys)
    es = [e for _, _, e in ks if e]
    dflt = max(sorted(set(es)), key=es.count) if es else 'linear'
    ps = [pct(t) for t, _, _ in ks]
    assert len(set(ps)) == len(ps), name
    body = ''.join(f'{p}{{{fmt(v)}' + (f';animation-timing-function:{EASE[e]}' if e and e != dflt else '') + '}' for p, (t, v, e) in zip(ps, ks))
    return f'@keyframes {name}{{{body}}}', EASE[dflt]


def kf_step(name, keys, prop):
    """回の種類ごとの 切りかえ {n: [(秒, 値)…], u: […]}（はじめの値＝止まっている値）→ step-end の @keyframes"""
    rest = keys['n'][0][1]
    body = f'0%{{{prop}:{rest}}}'
    for s, typ in PLAN:
        body += ''.join(f'{pct(s + t)}{{{prop}:{v}}}' for t, v in keys[typ][1:])
    return f'@keyframes {name}{{{body}100%{{{prop}:{rest}}}}}'


# ---------------------------------------------------------------- 動きの 計算（馬が ドラキュラを 見るため：CSS と同じ 動きの 曲線）
def bezier(x1, y1, x2, y2):
    def fn(u):
        lo, hi = 0.0, 1.0
        for _ in range(40):                                    # x(s) = u を とく
            s = (lo + hi) / 2
            x = 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
            lo, hi = (s, hi) if x < u else (lo, s)
        s = (lo + hi) / 2
        return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3
    return fn


EASE_FN = {k: bezier(*v) for k, v in BEZ.items()}
EASE_FN['linear'] = lambda u: u


def value_at(keys, t):
    """1回の キー（数）の 時刻 t の 値"""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0, e0), (t1, v1, _) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            if v0 == v1:
                return v0
            return v0 + (v1 - v0) * EASE_FN[e0]((t - t0) / (t1 - t0))
    return keys[-1][1]


# ---------------------------------------------------------------- ドラキュラ
def flaps(k, t, n, per, dn_t, up, dn):
    """パタパタ n回（t から：上 → 下（dn_t 秒）→ 上。はじめの 上は その時の 値から）"""
    for _ in range(n):
        if abs(k.k[-1][0] - round(t, 4)) < 1e-9:
            k.k[-1] = (k.k[-1][0], k.k[-1][1], 'ease-in-out')
        else:
            k.to(t, up, 'ease-in-out')
        k.to(t + dn_t, dn, 'ease-in-out').to(t + per, up)
        t += per
    return t


def flap_sets(typ):
    """パタパタの 組 [(はじめ, 回数, 1回の秒, 下へ あおぐ 秒, 上, 下, 体の 上下)]"""
    if typ == 'n':
        assert abs(T_PREP + N_FLAP * FLAP + N_FAST * FAST - T_FAIL) < 1e-9 and abs(T_PREP + N_FLAP * FLAP - T_SWEAT) < 1e-9
        return [(T_PREP, N_FLAP, FLAP, FLAP_DN, UP, DN, -5.0), (T_SWEAT, N_FAST, FAST, FAST_DN, UP_F, DN_F, -3.0)]
    assert abs(T_PREP + N_FLAP_U * FLAP - T_FADE[1]) < 1e-9
    return [(T_PREP, N_FLAP_U, FLAP, FLAP_DN, UP, DN, -6.0)]


def flail(k, t0, t1):
    """落ちる時の マントの ばたばた（t0〜t1・おわりは 上）"""
    hi, lo, h = FALL_W
    k.at(t0, k.k[-1][1], 'ease-out').to(t0 + 0.06, hi, 'ease-in-out')
    t, v = t0 + 0.06, lo
    while t + h < t1 - 0.03:
        t += h
        k.to(t, v, 'ease-in-out')
        v = hi if v == lo else lo
    return k.to(t1, hi)


def wing_keys(typ):
    L, tl = EV_LEN[typ], T_LAND[typ]
    k = Keys(0.0, L, 'ease-in-out').to(T_PREP, UP)
    for t, n, per, dn_t, up, dn, _ in flap_sets(typ):
        flaps(k, t, n, per, dn_t, up, dn)
    if typ == 'n':
        flail(k, T_FAIL, tl)
    else:
        k.hold(T_DROP - 0.02).to(T_DROP, FALL_W[0])
        flail(k, T_DROP, tl)
    land_wing(k, tl, L)
    return k.end()


def land_wing(k, tl, L):
    """どすん → マントを たらす → もとへ"""
    k.at(tl, FALL_W[0], 'ease-out').to(tl + 0.08, -30.0, 'ease-out').to(tl + 0.20, -22.0, 'ease-in-out').to(tl + 0.32, -28.0)
    k.hold(L - T_BACK, 'ease-in-out').to(L - 0.05, 0.0)


def bob_keys(typ):
    k = Keys(0.0, EV_LEN[typ])
    for t, n, per, dn_t, _, _, b in flap_sets(typ):
        for _ in range(n):
            k.at(t, 0.0, 'ease-in-out').to(t + dn_t, b, 'ease-in-out').to(t + per, 0.0)
            t += per
    return k.end()


def y_keys(typ):
    k = Keys(0.0, EV_LEN[typ]).to(T_PREP, 0.0, 'ease-out').to(T_UP, RISE)
    if typ == 'n':
        k.hold(T_SWEAT + 0.2, 'ease-in-out').to(2.34, RISE + 7, 'ease-in-out').to(2.50, RISE + 3, 'ease-in-out').to(T_FAIL, RISE + 9, 'quad-in').to(T_LAND['n'], 0.0)
    else:
        k.at(T_UP, RISE, 'quad-in').to(T_FADE[1], TOP).hold(T_DROP, 'quad-in').to(T_LAND['u'], 0.0)
    return k.end()


def squash_keys(typ):
    tl = T_LAND[typ]
    t_fall = T_FAIL if typ == 'n' else T_DROP
    k = Keys((1.0, 1.0), EV_LEN[typ]).to(0.10, (1.07, 0.90), 'ease-in').to(T_PREP, (0.95, 1.07), 'ease-out').to(0.36, (1.0, 1.0))
    k.hold(t_fall, 'ease-out').to(t_fall + 0.12, (0.96, 1.05)).hold(tl, 'ease-out')
    k.to(tl + 0.07, (1.16, 0.80), 'ease-out').to(tl + 0.18, (0.95, 1.06), 'ease-in-out').to(tl + 0.28, (1.03, 0.97), 'ease-in-out').to(tl + 0.36, (1.0, 1.0))
    return k.end()


def leg_keys(typ, side):
    """足（つけねが 中心・+ は 足先が 左へ）：落ちる時に ばたばた（左右 たがいちがい）。飛ぶ時は 体と いっしょに 上下するだけ"""
    sg = 1 if side == 0 else -1
    k = Keys(0.0, EV_LEN[typ])
    t0, t1 = (T_FAIL, T_LAND['n']) if typ == 'n' else (T_DROP, T_LAND['u'])
    t, i = t0, 0
    k.at(t0, 0.0, 'ease-in-out')
    while t + 0.09 <= t1 - 0.02:
        t += 0.09
        a = (18.0 if (i + side) % 2 == 0 else -4.0) * sg
        k.to(t, a, 'ease-in-out')
        i += 1
    k.to(t1, 0.0)
    return k.end()


def head_keys(typ):
    L, tl = EV_LEN[typ], T_LAND[typ]
    k = Keys(0.0, L)
    if typ == 'n':
        k.hold(T_SWEAT + 0.3, 'ease-in-out').to(2.30, -4.0, 'ease-in-out').to(2.45, 4.0, 'ease-in-out').to(2.60, -3.0, 'ease-in-out').to(T_FAIL, 0.0, 'ease-out')
        t_fall = T_FAIL
    else:
        k.hold(T_HAPPY, 'ease-in-out').to(T_HAPPY + 0.14, 6.0, 'ease-in-out').to(T_HAPPY + 0.28, -4.0, 'ease-in-out').to(T_HAPPY + 0.40, 0.0)
        t_fall = T_DROP
        k.hold(t_fall, 'ease-out')
    k.to(t_fall + 0.08, -7.0, 'ease-in-out').to(tl, 0.0, 'ease-out').to(tl + 0.06, 5.0, 'ease-in-out').to(tl + 0.16, 0.0)
    k.hold(tl + T_SHY, 'ease-in-out').to(tl + T_SHY + 0.2, -9.0).hold(L - T_BACK, 'ease-in-out').to(L - 0.05, 0.0)
    return k.end()


def face_steps(typ):
    """顔の 切りかえ（目：Eo＝いつもの・Es＝＞＜・Eh＝＾＾／口：Ms＝いつもの・Mo＝あけた／Bl＝まっかな ほお）"""
    L, tl = EV_LEN[typ], T_LAND[typ]
    back, shy = L - T_BACK, tl + T_SHY
    if typ == 'n':
        return dict(Eo=[(0, 1), (T_FAIL, 0), (back, 1)], Es=[(0, 0), (T_FAIL, 1), (shy, 0)], Eh=[(0, 0), (shy, 1), (back, 0)],
                    Ms=[(0, 1), (T_FAIL, 0), (shy, 1)], Mo=[(0, 0), (T_FAIL, 1), (shy, 0)], Bl=[(0, 0), (shy, 1), (back, 0)])
    return dict(Eo=[(0, 1), (T_HAPPY, 0), (back, 1)], Es=[(0, 0), (T_DROP, 1), (shy, 0)], Eh=[(0, 0), (T_HAPPY, 1), (T_FADE[1], 0), (shy, 1), (back, 0)],
                Ms=[(0, 1), (T_DROP, 0), (shy, 1)], Mo=[(0, 0), (T_DROP, 1), (shy, 0)], Bl=[(0, 0), (shy, 1), (back, 0)])


def sweat_keys(typ):
    L, tl = EV_LEN[typ], T_LAND[typ]
    t0 = T_SWEAT if typ == 'n' else tl + T_SHY
    return Keys(0.0, L).to(t0, 0.0).to(t0 + 0.10, 1.0).hold(L - T_BACK).to(L - T_BACK + 0.10, 0.0).end()


def opacity_keys(typ):
    if typ == 'n':
        return Keys(1.0, EV_LEN['n']).end()
    return Keys(1.0, EV_LEN['u']).to(T_FADE[0], 1.0).to(T_FADE[1], 0.0).hold(T_DROP - 0.01).to(T_DROP, 1.0).end()


def shadow_of(y):
    """足もとの 高さ y（ドラキュラの座標）の 影の 大きさ（こさも 同じ）"""
    return round(max(0.3, 1 + y / 170), 3)


def shadow_keys(typ):
    """影：ドラキュラが 上がるほど 小さく うすく（Y の キーと 同じ 時刻・動き）"""
    return [(t, shadow_of(v), e) for t, v, e in y_keys(typ)]


def laugh_keys(typ, i):
    """i 番目の 笑う物（かぼちゃ 0〜2・ドクロ 3）の はねかた (上へ, かたむき)"""
    d, per, hop, rot = LAUGHERS[i]
    k = Keys((0.0, 0.0), EV_LEN[typ])
    t = T_LAND[typ] + d
    for b in range(int(LAUGH // per + 1e-9)):
        sg = 1 if b % 2 == 0 else -1
        k.at(t, (0.0, 0.0), 'ease-in-out').to(t + per / 2, (-hop, rot * sg), 'ease-in-out').to(t + per, (0.0, 0.0))
        t += per
    return k.end()


def mouth_keys(typ, i):
    """かぼちゃの 笑う口（口の 上の線を 中心に たてに のびちぢみ）：はねる 上で せまく・下で 大きく"""
    d, per, _, _ = LAUGHERS[i]
    k = Keys(1.0, EV_LEN[typ])
    t = T_LAND[typ] + d
    for b in range(int(LAUGH // per + 1e-9)):
        k.at(t, 1.0, 'ease-in-out').to(t + per / 2, 0.55, 'ease-in-out').to(t + per, 1.0)
        t += per
    return k.end()


def jaw_keys(typ):
    """ドクロの あご（カタカタ：JAW_PER 秒に 1回）"""
    d = LAUGHERS[3][0]
    k = Keys(0.0, EV_LEN[typ])
    t = T_LAND[typ] + d
    for b in range(int(LAUGH // JAW_PER + 1e-9)):
        k.at(t, 0.0, 'ease-in-out').to(t + JAW_PER / 2, JAW, 'ease-in-out').to(t + JAW_PER, 0.0)
        t += JAW_PER
    return k.end()


def laugh_steps(typ):
    """笑う顔に かえる（Pf＝いつもの かぼちゃの顔・Pl＝笑う顔・Ks＝いつもの ドクロ・Kl＝笑う ドクロ）"""
    tl = T_LAND[typ]
    t1 = tl + LAUGH + 0.1
    return dict(Pf=[(0, 1), (tl, 0), (t1, 1)], Pl=[(0, 0), (tl, 1), (t1, 0)], Ks=[(0, 1), (tl, 0), (t1, 1)], Kl=[(0, 0), (tl, 1), (t1, 0)])


def tracks():
    """部品ごとの 回の種類ごとの キー"""
    T = {}
    for typ in ('n', 'u'):
        T.setdefault('W', {})[typ] = wing_keys(typ)
        T.setdefault('Bb', {})[typ] = bob_keys(typ)
        T.setdefault('Y', {})[typ] = y_keys(typ)
        T.setdefault('Sq', {})[typ] = squash_keys(typ)
        T.setdefault('LL', {})[typ] = leg_keys(typ, 0)
        T.setdefault('LR', {})[typ] = leg_keys(typ, 1)
        T.setdefault('Hd', {})[typ] = head_keys(typ)
        T.setdefault('Sw', {})[typ] = sweat_keys(typ)
        T.setdefault('O', {})[typ] = opacity_keys(typ)
        T.setdefault('Sh', {})[typ] = shadow_keys(typ)
        for i in range(4):
            T.setdefault(f'J{i}', {})[typ] = laugh_keys(typ, i)
        for i in range(3):
            T.setdefault(f'Pm{i}', {})[typ] = mouth_keys(typ, i)
        T.setdefault('Kj', {})[typ] = jaw_keys(typ)
    return T


# ---------------------------------------------------------------- 馬（コマ）
TRACK_W = 14.0                   # 馬が ついていく はやさ（ゆるやかに 止まる ばね：1/秒。おくれは 約 2/TRACK_W 秒）
GAZE_GAIN = 1.25                 # 見る向きの かわりより 少し 大きく 頭を まわす（ドラキュラが 少しだけ 飛ぶ時も 見上げるのが わかるように。
                                 # うまく 飛べる回は ドラキュラが 画面の 上の 方に 来た所で いちばん 上を 見る）


def gaze(t, typ, run, T):
    """馬の目から ドラキュラの 頭への 向き（度・上が +）"""
    y = value_at(T['Y'][typ], t) + value_at(T['Bb'][typ], t) + HEAD_Y * value_at([(a, b[1], c) for a, b, c in T['Sq'][typ]], t)
    ex, ey = run['eye']
    return math.degrees(math.atan2(ey - (VAMP_AT[1] + VAMP_S * y), ex - VAMP_AT[0]))


def horse_e(typ, run, T=None, dt=0.001):
    """1回の中の 馬の 見上げる ぐあい e（dt ごと）：ドラキュラの 頭への 向き（止まっている時から どれだけ 上か）を 頭の まわる 角度で わった ねらいに、
       ばね（TRACK_W）で なめらかに ついていく"""
    T = T or tracks()
    g0 = gaze(0.0, typ, run, T)
    n = int(round(EV_LEN[typ] / dt))
    e, v, out = 0.0, 0.0, []
    for i in range(n + 1):
        t = i * dt
        tgt = min(1.0, max(0.0, GAZE_GAIN * (gaze(t, typ, run, T) - g0) / run['turn']))
        a = TRACK_W * TRACK_W * (tgt - e) - 2 * TRACK_W * v
        v += a * dt
        e += v * dt
        out.append(e)
    return out


def horse_frame(e, run):
    lv = [0.0] + run['look']
    return min(range(len(lv)), key=lambda i: abs(lv[i] - e))


def horse_changes(typ, run, T=None):
    """1回の中で コマが かわる時 [(秒, コマ)]（1ミリ秒 きざみ）"""
    out, cur = [], 0
    for i, e in enumerate(horse_e(typ, run, T)):
        f = horse_frame(e, run)
        if f != cur:
            out.append((round(i / 1000, 3), f))
            cur = f
    assert cur == 0, (typ, cur)
    return out


def horse_css(blob, run, T):
    """馬の コマの (html, css)：シートを コマごとに ずらす（step-end。同じコマの時は まとめて1つに書く）"""
    cols = run['cols']
    cw, ch = (v // 2 for v in run['cell'])
    ax, ay = (v // 2 for v in run['at'])
    g = run['pad'] // 2
    sw, sh = cols * (cw + 2 * g), run['rows'] * (ch + 2 * g)
    ch_ = {typ: horse_changes(typ, run, T) for typ in ('n', 'u')}
    by = {0: ['0%', '100%']}
    for s, typ in PLAN:
        for t, f in ch_[typ]:
            by.setdefault(f, []).append(pct(s + t))
    body = ''
    for f in sorted(by):
        r, c = divmod(f, cols)
        body += f'{",".join(by[f])}{{transform:{tr(-c * (cw + 2 * g), -r * (ch + 2 * g))}}}'
    html = '<div class="hlH"><div class="hlHx"></div></div>'
    css = (f'.hl .hlH{{position:absolute;left:{ax}px;top:{ay}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.hl .hlHx{{position:absolute;left:-{g}px;top:-{g}px;width:{sw}px;height:{sh}px;background:url({blob}) 0 0/{sw}px {sh}px no-repeat;'
           f'animation:hlHA {LOOP:g}s step-end infinite;will-change:transform}}@keyframes hlHA{{{body}}}')
    return html, css


# ---------------------------------------------------------------- SVG
def pv(cls, p, inner):
    """動く中心 p で はさむ：<g translate(p)><g class><g translate(-p)>…"""
    return (f'<g transform="translate({num(p[0])} {num(p[1])})"><g class="{cls}">'
            f'<g transform="translate({num(-p[0])} {num(-p[1])})">{inner}</g></g></g>')


def wings(part):
    """マントの 左半分の 部品を 左の羽（肩が 中心）と、左右を うらがえした 右の羽に（同じ 動き＝左右 そろって はばたく）"""
    w = pv('hlW', SH_L, part)
    return w + f'<g transform="scale(-1 1)">{w}</g>'


def vampire_svg():
    """ドラキュラと 影（780×320 の 座標）"""
    b = A.vampire_bits()
    fx = A.vampire_fx()
    head = (b['ears'] + b['face'] + b['hair'] + f'<g class="hlEo">{b["eyeL"]}{b["eyeR"]}</g><g class="hlEs">{fx["eyesShut"]}</g>'
            f'<g class="hlEh">{fx["eyesHappy"]}</g>' + b['browL'] + b['browR'] + b['cheeks'] + f'<g class="hlBl">{fx["blush"]}</g>'
            f'<g class="hlMs">{b["mouth"]}</g><g class="hlMo">{fx["mouthOpen"]}</g><g class="hlSw">{fx["sweat"]}</g>')
    body = (wings(b['capeL']) + wings(b['liningL']) + wings(b['shadeL'])
            + pv('hlLL', HIP_L, b['legL']) + pv('hlLR', HIP_R, b['legR']) + pv('hlLL', HIP_L, b['bootL']) + pv('hlLR', HIP_R, b['bootR'])
            + b['body'] + wings(b['armL']) + wings(b['handL']) + b['collar'] + pv('hlHd', NECK, head))
    rx, ry, col, op = SHADOW
    shadow = f'<g transform="translate({num(VAMP_AT[0])} {num(VAMP_AT[1])})"><g class="hlSh">{A.ell(0, 0, rx, ry, col, extra=f"opacity=\"{op}\"")}</g></g>'
    return (shadow + f'<g transform="translate({num(VAMP_AT[0])} {num(VAMP_AT[1])}) scale({num(VAMP_S)})"><g class="hlO"><g class="hlY"><g class="hlBb"><g class="hlSq">'
            f'{body}</g></g></g></g></g>')


def pumpkin_svg(i):
    x, y, w, h, look = PUMPKINS[i]
    b = A.pumpkin_bits(w, h, look=look)
    lf = A.pumpkin_laugh(w, h, look)
    top = lf['mouth_top']
    glow = re.sub(r'pkg\d+', f'hlG{i}', b['glow'])
    laugh = (lf['eyes'] + lf['nose'] + f'<g transform="translate(0 {num(top)})"><g class="hlPm{i}"><g transform="translate(0 {num(-top)})">{lf["mouth"]}</g></g></g>')
    return (f'<g transform="translate({num(x)} {num(y)})"><g class="hlJ{i}">{glow}{b["body"]}{b["stem"]}'
            f'<g class="hlPf">{b["eyes"]}{b["nose"]}{b["mouth"]}</g><g class="hlPl">{laugh}</g></g></g>')


def skull_svg():
    b = A.skull_bits()
    lf = A.skull_laugh('hlK')
    still = ''.join(b[k] for k in A.SKULL_ORDER)
    return (f'<g transform="translate({num(SKULL_AT[0])} {num(SKULL_AT[1])}) scale({num(SKULL_S)})"><g class="hlJ3">'
            f'<g class="hlKs">{still}</g><g class="hlKl">{lf["mouth"]}<g class="hlKj">{lf["jaw"]}</g>{lf["head"]}</g></g></g>')


def scene_svg():
    """ドラキュラ・かぼちゃ・ドクロ（いまの絵と 同じ 重なりの順：影 → ドラキュラ →（馬）→ かぼちゃ 560・640・ドクロ・かぼちゃ 216）"""
    return (f'<svg class="hlS" viewBox="0 0 780 320" aria-hidden="true">{vampire_svg()}{pumpkin_svg(0)}{pumpkin_svg(1)}{skull_svg()}{pumpkin_svg(2)}</svg>')


def scene_css(T):
    L = f'{LOOP:g}s'
    rules, kfs, mv = '', '', []

    def track(cls, keys, fmt):
        nonlocal rules, kfs
        k, e = kf(cls + 'K', keys, fmt)
        rules += f'.hl .{cls}{{animation:{cls}K {L} {e} infinite}}'
        kfs += k
        mv.append(cls)

    def step(cls, keys, prop='opacity'):
        nonlocal rules, kfs
        rules += f'.hl .{cls}{{animation:{cls}K {L} step-end infinite}}'
        kfs += kf_step(cls + 'K', keys, prop)

    rot = lambda v: f'transform:rotate({num(v)}deg)'
    op = lambda v: f'opacity:{num(v)}'
    ty = lambda v: f'transform:translateY({num(v)}px)'
    track('hlW', T['W'], rot)
    track('hlY', T['Y'], ty)
    track('hlBb', T['Bb'], ty)
    track('hlSq', T['Sq'], lambda v: f'transform:scale({num(v[0], 3)},{num(v[1], 3)})')
    track('hlLL', T['LL'], rot)
    track('hlLR', T['LR'], rot)
    track('hlHd', T['Hd'], rot)
    track('hlSw', T['Sw'], op)
    track('hlO', T['O'], op)
    track('hlSh', T['Sh'], lambda v: f'transform:scale({num(v, 3)});opacity:{num(v, 3)}')
    for i in range(4):
        track(f'hlJ{i}', T[f'J{i}'], lambda v: f'transform:translateY({num(v[0])}px) rotate({num(v[1])}deg)')
    for i in range(3):
        track(f'hlPm{i}', T[f'Pm{i}'], lambda v: f'transform:scaleY({num(v)})')
    track('hlKj', T['Kj'], ty)
    fs = {typ: face_steps(typ) for typ in ('n', 'u')}
    for c in ('Eo', 'Es', 'Eh', 'Ms', 'Mo', 'Bl'):
        step('hl' + c, {typ: fs[typ][c] for typ in fs})
    ls = {typ: laugh_steps(typ) for typ in ('n', 'u')}
    for c in ('Pf', 'Pl', 'Ks', 'Kl'):
        step('hl' + c, {typ: ls[typ][c] for typ in ls})
    css = ','.join(f'.hl .{c}' for c in mv) + '{transform-box:view-box;transform-origin:0 0}'
    css += '.hl .hlEs,.hl .hlEh,.hl .hlMo,.hl .hlBl,.hl .hlSw,.hl .hlPl,.hl .hlKl{opacity:0}'
    return css + rules + kfs


# ---------------------------------------------------------------- ページ
def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：still（いまの止まった絵）・base（動く時の 下の絵）・look（馬の コマの シート）→ '/_blob/<id>'。run：halloween_run.json"""
    check_schedule(PLAN, LOOP)
    T = tracks()
    hh, hc = horse_css(blobs['look'], run, T)
    html = (f'<div class="hl" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["still"]}" alt="">'
            f'<img class="hlB" src="{blobs["base"]}" alt="">{hh}{scene_svg()}</div>')
    css = ('.hl{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.hl .bnr,.hl .hlB{position:absolute;left:0;top:0;width:390px;height:160px;display:block;object-fit:cover;object-position:50% 50%}'
           '.hl svg{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           + hc + scene_css(T)
           + '@media (prefers-reduced-motion:reduce){.hl .hlB,.hl .hlH,.hl svg{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Halloween.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="hl">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="hl" role="img".*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* ハロウィンの壁紙：ときどき ドラキュラが パタパタ 飛んで 落ち、ドクロと かぼちゃが 笑う・馬は ドラキュラを 目で追う（halloween_wall.py） */\n{css}\n/* /ハロウィンの壁紙 */\n'
    if '/* ハロウィンの壁紙：' in page:
        page = re.sub(r'/\* ハロウィンの壁紙：.*?/\* /ハロウィンの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    """halloween_blobs.json（base・look）と、同じ フォルダの blobs20.json（halloween＝いまの止まった絵）"""
    b = {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}
    b['still'] = '/_blob/' + json.load(open(os.path.join(os.path.dirname(os.path.abspath(fn)), 'blobs20.json')))['halloween']
    return b


if __name__ == '__main__':
    if '--plan' in sys.argv:
        check_schedule(PLAN, LOOP)
        for k, (s, typ) in enumerate(PLAN):
            nxt = PLAN[k + 1][0] if k + 1 < N_EV else LOOP + FIRST
            print(f'{k}: {s:7.2f}秒 {"うまく 飛べる" if typ == "u" else "ふつう      "}（つぎまで {nxt - s:5.2f}秒）〜{s + EV_LEN[typ]:7.2f}')
        print('1回り', LOOP, '秒')
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
