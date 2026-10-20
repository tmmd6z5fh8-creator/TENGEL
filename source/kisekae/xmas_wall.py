"""クリスマスの壁紙の動き（まさちゃんの指定「クリスマス エフェクト:常に雪が降っている 5秒から12秒、ランダムにサンタさんの持っているプレゼントを
   食べようとしてサンタさんが焦って逃げる💨右側へフェードアウト、様子を見ながら元の位置に戻る 15秒に1回リピート」）：ページに入れる HTML と CSS
   - いちばん下は いまの止まった絵（<img class="bnr">：視差効果を減らす なら これだけ）。その上に 動く時の 下の絵（サンタさんと 手前の 降る雪なし：
     flat/xmas_banner.py を XMAS_BASE=1）・馬の 首と頭の コマ（flat/xmas_run.py のシート・背景ごと 切りぬいた・すき通しなし）・
     サンタさん（flat/event_art.py の santa_bits を 部品ごとに <g> で包んだ SVG：止まっている時は いまの絵と同じ形・同じ場所）と
     💨 の けむり・汗・びくっの線・走る線（event_art.santa_fx）・降る雪（SVG）
   - 15秒ごと（WIN）に 1回：その15秒の 5〜12秒（START・ばらばら）に はじまる。8回ぶん（120秒・LOOP）で1回り（いつも同じ予定：schedule）。
     1回の中の 時刻（秒）：
       0〜0.85 馬が 首を のばして プレゼントの リボンへ → 0.85 ぱくっ → 1.1 もう1回 ぱくっ（もう ない）→ 1.5〜2.5 首を もどす
       0.92 サンタさんが びくっ（とびあがる・目を まるく あける・口を あける・汗が とぶ・びくっの線）→ 0.95〜1.13 プレゼントを 胸に だきよせる
       1.18〜 右へ あわてて 走って逃げる（足を ばたばた・体を 前へ かたむける・うしろの馬を 見ながら・ふる手を ばたばた・
             足もとに 💨 の けむり 5つ・うしろに 走る線）→ 1.55〜2.2 うすくなって 消える（右へ フェードアウト）
       3.0〜3.35 画面の 右はしから そっと 出てくる（体を 左へ かたむけて のぞく）→ きょろきょろ（目と頭）→
       そろり そろり 3歩 → 止まって 馬を じっと見る（汗）→ 3歩 → ちらっと うしろを見て → 4歩で もとの場所へ →
       6.32 ほっとして にっこり（ぴょん・手を ふる）・また プレゼントを さしだす → 6.7 おわり（いまの絵と同じ形）
   - 雪：いつも 降っている（奥・まん中・手前の3つの層・ふわふわ ゆれる・結晶は くるくる。止まった絵の 降る雪と同じ 白い つぶと 結晶）
   - ページを開くと 0秒（いまの絵と同じ形）から。1回目は 5〜12秒
   - キャンバスでは /_blob/<id>：止まった絵は blobs20.json の xmas・下の絵（base）と コマのシート（reach）は xmas_blobs.json。置く場所は xmas_run.json
   クラスの名前は xw…（的中ボタンの .xm… とは別）
   python3 xmas_wall.py --judge <Judge_Xmas.dc.html> <xmas_blobs.json> <xmas_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 xmas_wall.py --plan                                                           → 予定（はじまる秒）"""
import sys, os, re, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'flat'))
import event_art as A

ALT = ('雪の夜の町で、サンタの帽子をかぶった鹿毛の競走馬（赤と緑の綱に金の鈴・赤いゼッケン1）と、プレゼントをさしだすサンタさん、'
       '星と玉でかざったクリスマスツリーのイラスト（いつも雪が降っている。ときどき 馬が プレゼントを 食べようとして、'
       'サンタさんが あわてて 右へ逃げ、ようすを見ながら もどってくる）')
WIN = 15.0                       # 1回の わく（まさちゃん「15秒に1回リピート」）
START = (5.0, 12.0)              # わくの中で はじまる秒（まさちゃん「5秒から12秒、ランダムに」）
N_WIN = 8                        # 1回りの わくの数
LOOP = WIN * N_WIN               # 1回り（120秒）
EV_LEN = 6.7                     # 1回の長さ（つぎの回まで いつも 1.3秒 以上 あく：15＋5−12−6.7）
SEED = 8                         # 予定の 乱数の種（schedule：最後の回が 1回りの中で おわる・となりの回と 1秒 以上 ずれる・早いのと おそいのが ある）

SANTA_AT, SANTA_S = (640.0, 300.0), 0.86      # いまの絵の サンタさんの 場所と 大きさ（flat/xmas_banner.py）
HIP_L, HIP_R = (-14.0, -38.0), (14.0, -38.0)   # 足の つけね（サンタさんの 座標：足もと 0,0）
SH_W, SH_G = (30.0, -104.0), (-24.0, -96.0)    # ふる手・プレゼントの手の 肩
NECK = (0.0, -112.0)                           # 首（頭が かたむく 中心）
HEAD_C = (0.0, -150.0)                         # びくっの線の まん中

# ---- 1回の中の 時刻（秒）
H_REACH = (0.00, 0.85)           # 馬：首を のばす
H_BITES = ((0.85, 1.07), (1.10, 1.32))         # ぱくっ（2回）
H_BACK = (1.50, 2.50)            # 首を もどす
T_STARTLE = 0.92                 # びくっ
T_PULL = (0.95, 1.13)            # プレゼントを 胸に
PULL = (34.0, -10.0)             # だきよせる ずれ
T_RUN, T_FAST, T_GONE = 1.18, 1.55, 2.25       # 走りだす・速くなりきる・止まる（見えない）
X_FAST, X_GONE = 40.0, 185.0     # その時の 位置（サンタさんの 座標・右へ）
T_FADE = (1.55, 2.20)            # うすくなって 消える
RUN_HALF = 0.09                  # 走る足の 半回り（片足ずつ）
T_BACK, T_IN = 3.00, 3.35        # 右はしに 出る・見えきる
X_PEEK = 150.0                   # 出てくる 位置（体の 右が 画面の外）
LOOKS = ((3.40, 1), (3.55, -1), (3.70, 1), (3.85, -1))          # きょろきょろ（1＝右・−1＝左＝馬の方）
STEPS = ((3.95, 3, 0.20, X_PEEK, 110.0), (4.90, 3, 0.20, 110.0, 60.0), (5.75, 4, 0.14, 60.0, 0.0))   # (はじめ, 歩数, 1歩の秒, から, まで)
PAUSE1 = (4.55, 4.90)            # 止まって 馬を じっと見る
GLANCES = ((5.55, 1), (5.66, -1))               # ちらっと うしろ（右）を見て もどす
T_RELIEF = 6.32                  # ほっとして にっこり
PUFFS = ((1.20, 1.0), (1.38, 1.0), (1.56, .9), (1.74, .7), (1.92, .45))   # 💨 の けむり：(出る秒, こさ)
DROPS = (((0.98, 1.35), (-26, -166), (-16, -4)), ((1.02, 1.40), (26, -170), (16, -4)),
         ((1.58, 1.95), (-22, -160), (-15, -1)), ((4.64, 5.02), (28, -164), (14, -3)))   # とぶ汗：(秒, はじめの所, とぶ先)
EASE = {'linear': 'linear', 'ease-in': 'ease-in', 'ease-out': 'ease-out', 'ease-in-out': 'ease-in-out',
        'quad-in': 'cubic-bezier(.3333,0,.6667,.3333)', 'quad-out': 'cubic-bezier(.3333,.6667,.6667,1)'}


# ---------------------------------------------------------------- 予定
def schedule(seed=SEED):
    """1回りの中の 8回の はじまる秒（わく k の 5〜12秒）"""
    rnd = random.Random(seed)
    return [round(k * WIN + rnd.uniform(*START), 2) for k in range(N_WIN)]


def check_schedule(st):
    offs = [s - k * WIN for k, s in enumerate(st)]
    assert all(START[0] <= o <= START[1] for o in offs)
    assert st[-1] + EV_LEN <= LOOP, '最後の回が 1回りを こえる'
    assert all(abs(offs[k] - offs[k - 1]) >= 1.0 for k in range(1, N_WIN)), 'となりの回と ずれが小さい'
    assert min(offs) <= 6.5 and max(offs) >= 10.0, '早いのと おそいのが ない'
    assert all(st[k + 1] - st[k] >= EV_LEN + 1.3 for k in range(N_WIN - 1))


# ---------------------------------------------------------------- 数と キーフレーム
def num(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return '0' if s in ('-0', '', '-') else s


def pct(t):
    s = f'{t / LOOP * 100:.3f}'.rstrip('0').rstrip('.')         # 1.2ミリ秒 きざみ
    return (s or '0') + '%'


def tr(x=0.0, y=0.0):
    return f'translate({num(x)}px,{num(y)}px)'


def everywhere(keys, starts):
    """1回の キー [(秒, 値, 次までの動き)]（はじめと おわりは 止まっている値）→ 1回り（8回ぶん）"""
    rest = keys[0][1]
    assert keys[-1][1] == rest and keys[0][0] == 0 and keys[-1][0] <= EV_LEN + 1e-9
    out = [(0.0, rest, 'linear')]
    for s in starts:
        out += [(round(s + t, 4), v, e) for t, v, e in keys]
    out.append((LOOP, rest, 'linear'))
    ts = [k[0] for k in out]
    assert all(b > a for a, b in zip(ts, ts[1:])), 'キーの 時刻が ならんでいない'
    # 前と うしろと 同じ値の キーは いらない（止まっている あいだ）。つぎと 同じ値の キーの 動きは どれでも同じ（None）
    out = [k for i, k in enumerate(out) if i in (0, len(out) - 1) or not (out[i - 1][1] == k[1] == out[i + 1][1])]
    return [(t, v, e if i + 1 < len(out) and out[i + 1][1] != v else None) for i, (t, v, e) in enumerate(out)]


def kf(name, keys, fmt, starts):
    """1回の キー → (@keyframes, ふだんの 動き)：いちばん多い 動きを アニメーションの 動きにして、ちがう キーだけ 書く"""
    ks = everywhere(keys, starts)
    es = [e for _, _, e in ks if e]
    dflt = max(sorted(set(es)), key=es.count) if es else 'linear'
    ps = [pct(t) for t, _, _ in ks]
    assert len(set(ps)) == len(ps), name
    body = ''.join(f'{p}{{{fmt(v)}' + (f';animation-timing-function:{EASE[e]}' if e and e != dflt else '') + '}' for p, (t, v, e) in zip(ps, ks))
    return f'@keyframes {name}{{{body}}}', EASE[dflt]


def kf_step(name, keys, prop, starts):
    """1回の キー [(秒, 値)]（切りかえ）→ step-end の @keyframes"""
    body = f'0%{{{prop}:{keys[0][1]}}}'
    for s in starts:
        body += ''.join(f'{pct(s + t)}{{{prop}:{v}}}' for t, v in keys[1:])
    return f'@keyframes {name}{{{body}100%{{{prop}:{keys[0][1]}}}}}'


class Keys:
    """1回の キーを 時刻の順に つむ（to：その時刻に その値・e：つぎの キーまでの 動き）"""
    def __init__(self, rest):
        self.k = [(0.0, rest, 'linear')]

    def to(self, t, v, e='linear'):
        t = round(t, 4)
        assert t > self.k[-1][0], (t, self.k[-1])
        self.k.append((t, v, e))
        return self

    def at(self, t, v, e='linear'):
        """その時刻に その値（前の キーと 同じ時刻なら、前の キーの 動きだけ かえる）"""
        t = round(t, 4)
        lt, lv, _ = self.k[-1]
        if t > lt:
            return self.to(t, v, e)
        assert t == lt and lv == v, (t, v, self.k[-1])
        self.k[-1] = (lt, lv, e)
        return self

    def hold(self, t, e='linear'):
        return self.to(t, self.k[-1][1], e)

    def end(self):
        if self.k[-1][0] < EV_LEN:
            self.to(EV_LEN, self.k[0][1])
        assert self.k[-1][1] == self.k[0][1]
        return self.k


# ---------------------------------------------------------------- 馬（コマ）
def ease_io(u):
    """ゆっくり はじまって ゆっくり 止まる（smoothstep：いちばん速い所が ならしの 1.5倍。コマを とばさずに めくれる）"""
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def horse_pq(t):
    """1回の中の 時刻 t の (首を のばす ぐあい p, ぱくっ q)"""
    if t <= H_REACH[0] or t >= H_BACK[1]:
        return 0.0, 0.0
    if t < H_REACH[1]:
        return ease_io((t - H_REACH[0]) / (H_REACH[1] - H_REACH[0])), 0.0
    if t < H_BACK[0]:
        for a, b in H_BITES:
            if a <= t < b:
                return 1.0, math.sin(math.pi * (t - a) / (b - a))
        return 1.0, 0.0
    return 1.0 - ease_io((t - H_BACK[0]) / (H_BACK[1] - H_BACK[0])), 0.0


def horse_frame(p, q, run):
    """(p, q) に いちばん近い コマの番号（U0＝0・R1〜R32＝1〜32・B1〜B4＝33〜36）"""
    nR = len(run['reach'])
    if q > 0:
        lv = [0.0] + run['bite']
        k = min(range(len(lv)), key=lambda i: abs(lv[i] - q))
        return nR + k
    lv = [0.0] + run['reach']
    return min(range(len(lv)), key=lambda i: abs(lv[i] - p))


def horse_changes(run):
    """1回の中で コマが かわる時 [(秒, コマ)]（1ミリ秒 きざみで しらべる）"""
    out, cur = [], 0
    for i in range(int(round(EV_LEN * 1000)) + 1):
        t = i / 1000
        f = horse_frame(*horse_pq(t), run)
        if f != cur:
            out.append((round(t, 3), f))
            cur = f
    assert cur == 0
    return out


def horse_css(blob, run, starts):
    """馬の コマの (html, css)：シートを コマごとに ずらす（step-end。同じコマの時は まとめて1つに書く）"""
    cols = run['cols']
    cw, ch = (v // 2 for v in run['cell'])
    ax, ay = (v // 2 for v in run['at'])
    g = run['pad'] // 2
    sw, sh = cols * (cw + 2 * g), run['rows'] * (ch + 2 * g)
    by = {0: ['0%', '100%']}
    for s in starts:
        for t, f in horse_changes(run):
            by.setdefault(f, []).append(pct(s + t))
    body = ''
    for f in sorted(by):
        r, c = divmod(f, cols)
        body += f'{",".join(by[f])}{{transform:{tr(-c * (cw + 2 * g), -r * (ch + 2 * g))}}}'
    html = '<div class="xwH"><div class="xwHx"></div></div>'
    css = (f'.xw .xwH{{position:absolute;left:{ax}px;top:{ay}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.xw .xwHx{{position:absolute;left:-{g}px;top:-{g}px;width:{sw}px;height:{sh}px;background:url({blob}) 0 0/{sw}px {sh}px no-repeat;'
           f'animation:xwHA {LOOP:g}s step-end infinite;will-change:transform}}@keyframes xwHA{{{body}}}')
    return html, css


# ---------------------------------------------------------------- サンタさん
def run_x(t):
    """走って逃げる時の 位置（1回の中の 時刻 t。T_RUN〜T_GONE）"""
    if t <= T_RUN:
        return 0.0
    if t < T_FAST:
        u = (t - T_RUN) / (T_FAST - T_RUN)
        return X_FAST * u * u
    return X_FAST + (X_GONE - X_FAST) * min(1.0, (t - T_FAST) / (T_GONE - T_FAST))


def steps_list():
    """もどる 歩み [(はじめ, おわり, 足 0＝左／1＝右, から, まで)]"""
    out = []
    for t0, n, d, x0, x1 in STEPS:
        for k in range(n):
            out.append((t0 + k * d, t0 + (k + 1) * d, k % 2, x0 + (x1 - x0) * k / n, x0 + (x1 - x0) * (k + 1) / n))
    return out


def tracks():
    """部品ごとの 1回の キー"""
    T = {}
    # 位置（右へ 走る → 消える → 右はしから もどる）
    k = Keys(0.0).to(T_RUN, 0.0, 'quad-in').to(T_FAST, X_FAST).to(T_GONE, X_GONE).hold(T_BACK - 0.02).to(T_BACK, X_PEEK)
    for a, b, _, x0, x1 in steps_list():
        k.at(a, x0, 'ease-in-out').to(b, x1)
    T['X'] = k.end()
    T['O'] = Keys(1.0).to(T_FADE[0], 1.0).to(T_FADE[1], 0.0).hold(T_BACK).to(T_IN, 1.0).end()
    # 体の かたむき（足もとが 中心）：走る時は 前（右）へ・のぞく時は 左へ
    T['lean'] = (Keys(0.0).to(1.12, 0.0, 'ease-out').to(1.30, 10.0).hold(T_BACK - 0.02).to(T_BACK, -7.0).hold(3.95, 'ease-in-out')
                 .to(4.55, -4.0, 'ease-in-out').to(4.70, -7.0, 'ease-in-out').to(4.90, -6.0, 'ease-in-out').to(5.50, -3.0, 'ease-in-out')
                 .to(5.75, -2.0, 'ease-in-out').to(6.31, 0.0).end())
    # 体の 上下：びくっ（とびあがる）・走る（半回りごとに はずむ）・歩く・ほっとして ぴょん
    k = Keys(0.0).to(T_STARTLE, 0.0, 'ease-out').to(T_STARTLE + 0.07, -13.0, 'ease-in').to(T_STARTLE + 0.16, 0.0)
    t = T_RUN
    while t + RUN_HALF <= T_GONE + 1e-6:
        k.at(t, 0.0, 'ease-out').to(t + RUN_HALF / 2, -5.0, 'ease-in').to(t + RUN_HALF, 0.0)
        t += RUN_HALF
    for a, b, _, _, _ in steps_list():
        k.at(a, 0.0, 'ease-out').to((a + b) / 2, -3.0, 'ease-in').to(b, 0.0)
    k.hold(T_RELIEF, 'ease-out').to(T_RELIEF + 0.10, -6.0, 'ease-in').to(T_RELIEF + 0.20, 0.0)
    T['bob'] = k.end()
    # 足（つけねが 中心）：走る時は 片足ずつ 大きく 上げて うしろへ けり上げる・歩く時は そっと
    for side in (0, 1):
        k = Keys((0.0, 0.0))
        t, i = T_RUN, 0
        while t + RUN_HALF <= T_GONE + 1e-6:
            if i % 2 == side:
                k.at(t, (0.0, 0.0), 'ease-out').to(t + RUN_HALF / 2, (-12.0, 14.0), 'ease-in').to(t + RUN_HALF, (0.0, 0.0))
            t += RUN_HALF
            i += 1
        for a, b, leg, _, _ in steps_list():
            if leg == side:
                k.at(a, (0.0, 0.0), 'ease-out').to((a + b) / 2, (-6.0, 8.0), 'ease-in').to(b, (0.0, 0.0))
        T['leg%d' % side] = k.end()
    # ふる手（肩が 中心）：びくっ → ばたばた → もどる時は そのまま → ほっとして 手を ふる
    k = Keys(0.0).to(T_STARTLE, 0.0, 'ease-out').to(T_STARTLE + 0.06, 14.0, 'ease-in-out')
    t, s = T_STARTLE + 0.16, -1
    while t <= T_GONE:
        k.to(t, 16.0 if s > 0 else -14.0, 'ease-in-out')
        t += 0.10
        s = -s
    k.hold(T_BACK - 0.02).to(T_BACK, 0.0).hold(T_RELIEF, 'ease-in-out').to(T_RELIEF + 0.13, -12.0, 'ease-in-out').to(T_RELIEF + 0.26, 5.0, 'ease-in-out')
    T['armW'] = k.end()
    # プレゼントの手：胸に だきよせる → ほっとして また さしだす
    T['armG'] = Keys((0.0, 0.0)).to(T_PULL[0], (0.0, 0.0), 'ease-out').to(T_PULL[1], PULL).hold(T_RELIEF, 'ease-in-out').to(T_RELIEF + 0.30, (0.0, 0.0)).end()
    # 頭（首が 中心）：びくっ（ふるえる）・走る時は うしろの馬を 見る・きょろきょろ
    k = Keys(0.0).to(T_STARTLE, 0.0, 'ease-out').to(T_STARTLE + 0.05, -7.0, 'ease-in-out').to(T_STARTLE + 0.11, 5.0, 'ease-in-out').to(T_STARTLE + 0.18, 0.0)
    k.hold(T_RUN, 'ease-in-out').to(T_RUN + 0.12, -8.0).hold(T_BACK - 0.02).to(T_BACK, -4.0)
    for t, d in LOOKS:
        k.hold(t, 'ease-in-out').to(t + 0.07, 5.0 * d)
    k.hold(3.95, 'ease-in-out').to(4.15, -2.0).hold(PAUSE1[0], 'ease-in-out').to(PAUSE1[0] + 0.12, -5.0).hold(PAUSE1[1], 'ease-in-out').to(PAUSE1[1] + 0.15, -2.0)
    for t, d in GLANCES:
        k.hold(t, 'ease-in-out').to(t + 0.06, 5.0 * d)
    k.hold(5.80, 'ease-in-out').to(5.95, -2.0).hold(T_RELIEF - 0.02, 'ease-in-out').to(T_RELIEF + 0.12, 0.0)
    T['head'] = k.end()
    # 目（あけた目の ひとみ：左右）
    k = Keys(0.0).to(T_RUN - 0.03, 0.0, 'ease-in-out').to(T_RUN + 0.04, -2.8).hold(T_BACK)
    for t, d in LOOKS:
        k.hold(t, 'ease-in-out').to(t + 0.06, 2.8 * d)
    k.hold(3.95, 'ease-in-out').to(4.10, -2.0).hold(PAUSE1[0], 'ease-in-out').to(PAUSE1[0] + 0.08, -2.8).hold(PAUSE1[1], 'ease-in-out').to(PAUSE1[1] + 0.12, -2.0)
    for t, d in GLANCES:
        k.hold(t, 'ease-in-out').to(t + 0.05, 2.8 * d)
    k.hold(5.80, 'ease-in-out').to(5.92, -2.0).hold(T_RELIEF - 0.01).to(T_RELIEF, 0.0)
    T['pupil'] = k.end()
    T['sweat'] = Keys(0.0).to(0.95, 0.0).to(1.05, 1.0).hold(T_RELIEF).to(T_RELIEF + 0.14, 0.0).end()
    for i, ((a, b), _, (dx, dy)) in enumerate(DROPS):
        m = a + (b - a) * 0.45
        T['drop%d' % i] = (Keys(((0.0, 0.0), 0.0, .6)).to(a - 0.02, ((0.0, 0.0), 0.0, .6)).to(a + 0.03, ((0.0, 0.0), 1.0, 1.0), 'ease-out')
                           .to(m, ((dx * 0.65, -9.0), 1.0, 1.0), 'ease-in').to(b, ((dx, dy), 0.0, .8)).end())
    T['burst'] = (Keys((0.6, 0.0)).to(T_STARTLE, (0.6, 0.0), 'ease-out').to(T_STARTLE + 0.04, (0.95, 1.0), 'ease-out')
                  .to(T_STARTLE + 0.20, (1.1, 1.0)).to(T_STARTLE + 0.33, (1.15, 0.0)).end())
    T['speed'] = Keys(0.0).to(T_RUN + 0.22, 0.0).to(T_RUN + 0.32, 1.0).hold(T_GONE).to(T_GONE + 0.05, 0.0).end()
    T['shadow'] = Keys(1.0).to(T_STARTLE, 1.0, 'ease-out').to(T_STARTLE + 0.07, .8, 'ease-in').to(T_STARTLE + 0.16, 1.0).end()
    for i, (ts, op) in enumerate(PUFFS):
        T['puff%d' % i] = (Keys((0.0, .55, 0.0)).to(ts - 0.01, (0.0, .55, 0.0)).to(ts + 0.05, (-3.0, 1.0, op), 'ease-out')
                           .to(ts + 0.25, (-10.0, 1.35, op * .8)).to(ts + 0.55, (-17.0, 1.6, 0.0)).end())
    return T


def pv(cls, p, inner):
    """動く中心 p で はさむ：<g translate(p)><g class><g translate(-p)>…"""
    return (f'<g transform="translate({num(p[0])} {num(p[1])})"><g class="{cls}">'
            f'<g transform="translate({num(-p[0])} {num(-p[1])})">{inner}</g></g></g>')


def santa_svg():
    """サンタさんと 💨・汗・線（SVG・780×320 の 座標を 390×160 に）"""
    b = A.santa_bits()
    fx = A.santa_fx()
    head = (b['skin'] + f'<g class="xwEh">{b["eyes"]}</g><g class="xwEo"><g class="xwEp">{fx["eyesOpen"]}</g></g>' + b['cheeks'] + b['nose']
            + b['beard'] + f'<g class="xwMo">{fx["mouthOpen"]}</g>' + b['stache'] + b['mouth'] + f'<g class="xwSw">{fx["sweat"]}</g>'
            + b['brows'] + b['hat'])
    body = (pv('xwL0', HIP_L, b['pantsL'] + b['bootL'] + b['shine']) + pv('xwL1', HIP_R, b['pantsR'] + b['bootR'])
            + pv('xwAW', SH_W, b['sleeveW']) + pv('xwAG', SH_G, b['sleeveG']) + b['coat'] + pv('xwAW', SH_W, b['handW'])
            + pv('xwHd', NECK, head) + pv('xwAG', SH_G, b['gift'] + b['handG'])
            + pv('xwBu', HEAD_C, fx['burst'])
            + ''.join(f'<g transform="translate({num(x)} {num(y)})"><g class="xwD{i}"><g transform="translate({num(-x)} {num(-y)})">{A.drop(x, y, 0.85)}</g></g></g>'
                      for i, (_, (x, y), _) in enumerate(DROPS)))
    puffs = ''
    for i, (ts, _) in enumerate(PUFFS):
        x = run_x(ts) - 26
        puffs += f'<g transform="translate({num(x)} -5)"><g class="xwP{i}">{fx["puff"]}</g></g>'
    shadow = A.ell(0, 0, 54 / SANTA_S, 7 / SANTA_S, '#8FA9C8', extra='opacity=".55"')
    root = (f'<g class="xwO"><g class="xwX"><g class="xwSh">{shadow}</g><g class="xwSp">{fx["speed"]}</g>'
            f'<g class="xwBl"><g class="xwBb">{body}</g></g></g></g>')
    return (f'<svg class="xwS" viewBox="0 0 780 320" aria-hidden="true"><g transform="translate({num(SANTA_AT[0])} {num(SANTA_AT[1])}) scale({num(SANTA_S)})">'
            f'{puffs}{root}</g></svg>')


def santa_css(starts):
    T = tracks()
    L = f'{LOOP:g}s'
    rules, kfs, mv = '', '', []

    def track(cls, keys, fmt):
        nonlocal rules, kfs
        k, e = kf(cls + 'K', keys, fmt, starts)
        rules += f'.xw .{cls}{{animation:{cls}K {L} {e} infinite}}'
        kfs += k
        mv.append(cls)

    def step(cls, keys, prop='opacity'):
        nonlocal rules, kfs
        rules += f'.xw .{cls}{{animation:{cls}K {L} step-end infinite}}'
        kfs += kf_step(cls + 'K', keys, prop, starts)
        mv.append(cls)
    rot = lambda v: f'transform:rotate({num(v)}deg)'
    op = lambda v: f'opacity:{num(v)}'
    track('xwX', T['X'], lambda v: f'transform:translateX({num(v)}px)')
    track('xwO', T['O'], op)
    track('xwBl', T['lean'], rot)
    track('xwBb', T['bob'], lambda v: f'transform:translateY({num(v)}px)')
    for i in (0, 1):
        track(f'xwL{i}', T[f'leg{i}'], lambda v: f'transform:translateY({num(v[0])}px) rotate({num(v[1])}deg)')
    track('xwAW', T['armW'], rot)
    track('xwAG', T['armG'], lambda v: f'transform:{tr(*v)}')
    track('xwHd', T['head'], rot)
    track('xwEp', T['pupil'], lambda v: f'transform:translateX({num(v)}px)')
    track('xwSw', T['sweat'], op)
    for i in range(len(DROPS)):
        track(f'xwD{i}', T[f'drop{i}'], lambda v: f'transform:{tr(*v[0])} scale({num(v[2])});opacity:{num(v[1])}')
    track('xwBu', T['burst'], lambda v: f'transform:scale({num(v[0])});opacity:{num(v[1])}')
    track('xwSp', T['speed'], op)
    track('xwSh', T['shadow'], lambda v: f'transform:scale({num(v)})')
    for i in range(len(PUFFS)):
        track(f'xwP{i}', T[f'puff{i}'], lambda v: f'transform:translateX({num(v[0])}px) scale({num(v[1])});opacity:{num(v[2])}')
    step('xwEh', [(0, 1), (T_STARTLE, 0), (T_RELIEF, 1)])
    step('xwEo', [(0, 0), (T_STARTLE, 1), (T_RELIEF, 0)])
    step('xwMo', [(0, 0), (T_STARTLE, 1), (2.30, 0)])
    css = ','.join(f'.xw .{c}' for c in mv) + '{transform-box:view-box;transform-origin:0 0}'
    css += ('.xw .xwEo,.xw .xwMo,.xw .xwSw,.xw .xwBu,.xw .xwSp' + ''.join(f',.xw .xwD{i}' for i in range(len(DROPS)))
            + ''.join(f',.xw .xwP{i}' for i in range(len(PUFFS))) + '{opacity:0}')
    return css + rules + kfs


# ---------------------------------------------------------------- 雪（いつも 降っている）
SNOW_DOTS, SNOW_CRYS = 60, 8
SNOW_LAYERS = ((3, (3.4, 4.1)), (6, (3.0, 3.6)), (9, (2.6, 3.2)))     # (ゆれの はば px, 組ごとの ゆれの秒)
SNOW_H = 160


def flake_d(r):
    """止まった絵の 雪の結晶（event_art.snowflake）と同じ形：3本の線が 60度ずつ（まん中 0,0）"""
    d = ''
    for k in range(3):
        a = math.radians(k * 60)
        dx, dy = math.cos(a) * r, math.sin(a) * r
        d += f'M{num(-dx)} {num(-dy)}L{num(dx)} {num(dy)}'
    return d


def flakes(seed=41):
    rnd = random.Random(seed)
    n = SNOW_DOTS + SNOW_CRYS
    crys = set(rnd.sample(range(n // 3, n), SNOW_CRYS))
    out = []
    for i in range(n):
        z = rnd.random() if i not in crys else rnd.uniform(.35, 1)
        layer = 0 if z < .4 else 1 if z < .75 else 2
        d = 16 - 9 * z + rnd.uniform(-.6, .6)
        out.append(dict(x0=round(rnd.uniform(-20, 384), 1), d=round(d, 2), dl=round(-rnd.uniform(0, d), 2), layer=layer, grp=rnd.randrange(2),
                        kind='c' if i in crys else 'd', r=round(.6 + 1.4 * z + rnd.uniform(-.1, .1), 2), o=round(.55 + .4 * z, 2),
                        cs=1 if z < .7 else 2, spin=round(rnd.uniform(8, 14), 1), rev=rnd.random() < .5))
    cs = [p for p in out if p['kind'] == 'c']                  # 結晶は かたまらないように：横は 8つの場所に1つずつ・落ちる とちゅうも ずらす
    slots = list(range(SNOW_CRYS))
    rnd.shuffle(slots)
    for k, p in enumerate(cs):
        p['x0'] = round(-4 + slots[k] * (388 / SNOW_CRYS) + rnd.uniform(0, 388 / SNOW_CRYS - 8), 1)
        p['dl'] = round(-p['d'] * ((k + rnd.uniform(.1, .5)) / SNOW_CRYS), 2)
    return out


def snow_svg():
    defs = ''.join(f'<path id="xwC{k}" d="{flake_d(r)}" fill="none" stroke="#FFFFFF" stroke-width="{num(r * .22)}" stroke-linecap="round"/>'
                   for k, r in ((1, 2.3), (2, 3.2)))
    body = ''
    fl = flakes()
    for li, (_, periods) in enumerate(SNOW_LAYERS):
        for gi, per in enumerate(periods):
            inner = ''
            for p in fl:
                if p['layer'] != li or p['grp'] != gi:
                    continue
                tm = f'animation-duration:{num(p["d"])}s;animation-delay:{num(p["dl"])}s'
                if p['kind'] == 'd':
                    shape = f'<circle r="{num(p["r"])}" fill="#FFFFFF" opacity="{num(p["o"])}"/>'
                else:
                    shape = (f'<g class="xwFr{" rv" if p["rev"] else ""}" style="animation-duration:{num(p["spin"])}s">'
                             f'<use href="#xwC{p["cs"]}" opacity="{num(min(1, p["o"] + .1))}"/></g>')
                inner += f'<g transform="translate({num(p["x0"])} 0)"><g class="xwFy" style="{tm}">{shape}</g></g>'
            body += (f'<g class="xwFx" style="animation-name:xwFS{li};animation-duration:{num(per)}s;animation-delay:{num(-per * (.3 + .4 * gi))}s">'
                     f'{inner}</g>')
    return f'<svg class="xwF" viewBox="0 0 390 160" aria-hidden="true"><defs>{defs}</defs>{body}</svg>'


def snow_css():
    css = ('.xw .xwFy,.xw .xwFx,.xw .xwFr{transform-box:view-box;transform-origin:0 0}'
           '.xw .xwFy{animation:xwFY 10s linear infinite}.xw .xwFx{animation:xwFS0 3s ease-in-out infinite alternate}'
           '.xw .xwFr{animation:xwFR 12s linear infinite}.xw .xwFr.rv{animation-direction:reverse}'
           f'@keyframes xwFY{{from{{transform:translate(0px,-12px)}}to{{transform:translate(12px,{SNOW_H + 12}px)}}}}'
           '@keyframes xwFR{to{transform:rotate(360deg)}}')
    for li, (a, _) in enumerate(SNOW_LAYERS):
        css += f'@keyframes xwFS{li}{{from{{transform:translateX(-{a}px)}}to{{transform:translateX({a}px)}}}}'
    return css


# ---------------------------------------------------------------- ページ
def inline(blobs, run, alt=ALT):
    """(html, css)。blobs：still（いまの止まった絵）・base（動く時の 下の絵）・reach（馬の コマの シート）→ '/_blob/<id>'。run：xmas_run.json"""
    starts = schedule()
    check_schedule(starts)
    hh, hc = horse_css(blobs['reach'], run, starts)
    html = (f'<div class="xw" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["still"]}" alt="">'
            f'<img class="xwB" src="{blobs["base"]}" alt="">{hh}{santa_svg()}{snow_svg()}</div>')
    css = ('.xw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.xw .bnr,.xw .xwB{position:absolute;left:0;top:0;width:390px;height:160px;display:block;object-fit:cover;object-position:50% 50%}'
           '.xw svg{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           + hc + santa_css(starts) + snow_css()
           + '@media (prefers-reduced-motion:reduce){.xw .xwB,.xw .xwH,.xw svg{display:none}}')
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Xmas.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="xw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="xw" role="img".*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* クリスマスの壁紙：いつも 雪・ときどき 馬が プレゼントを 食べようとして サンタさんが 逃げる（xmas_wall.py） */\n{css}\n/* /クリスマスの壁紙 */\n'
    if '/* クリスマスの壁紙：' in page:
        page = re.sub(r'/\* クリスマスの壁紙：.*?/\* /クリスマスの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    """xmas_blobs.json（base・reach）と、同じ フォルダの blobs20.json（xmas＝いまの止まった絵）"""
    b = {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}
    b['still'] = '/_blob/' + json.load(open(os.path.join(os.path.dirname(os.path.abspath(fn)), 'blobs20.json')))['xmas']
    return b


if __name__ == '__main__':
    if '--plan' in sys.argv:
        st = schedule()
        check_schedule(st)
        for k, s in enumerate(st):
            print(f'{k}: {s:7.2f}秒（わくの {s - k * WIN:5.2f}秒）〜{s + EV_LEN:7.2f}')
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
