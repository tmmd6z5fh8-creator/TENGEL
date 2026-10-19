"""子供向けの壁紙の動き（まさちゃんの指定）：ページに入れる HTML と CSS
   「1秒〜3秒で、毛糸が左から右にころがっていき、ロボットは目で追って、馬も目で追って4秒で毛糸が止まり、馬が跳ねて喜ぶ。8秒に一回リピートする」
   「毛糸が転がって消えるんじゃなくて、ロボットが毛糸拾いに行って、間違えて蹴っちゃって毛糸と一緒に画面からフェードアウトして！
    1秒後にロボットだけ持って戻ってきて！その後2秒にリピートして！」（持って戻った毛糸玉は「左へポーンと投げる」）
   「毛糸投げてけら画面上に転がるまで1.7秒間を空けて！ 3回〜8回のうち、ランダムで毛糸を追いかけようとしたロボットが動き出す時に故障して、
    止まって馬がヒヒィーンて首を上にあげて鳴くと、ロボットが復活して毛糸とりにいく演出入れえて！あとロボットが治らず馬が毛糸取りにいく演出も
    同じ3回〜8回のうちランダムで入れて！」
   - 絵は kids.py の部品（いつもの絵と同じ形・同じ場所）を べつべつの <svg> にして重ね、動く所だけを CSS で動かす。下から：
     下の絵（毛糸の編み目・布・雲・星）→ 毛糸玉と糸・投げた毛糸玉（枠の内がわだけ見える）→
     馬（枠の内がわだけ：かげ → 向き → はねる → のぞきこむ → 立ち上がる → 馬（目なし）・ボタンの目・くわえた毛糸玉）→
     ロボット（枠の内がわだけ：かげ → けむり・ピコーン → アンテナ → 左の腕 → 右の腕（手に持った毛糸玉）→ 足 → 体と頭 → 黒目・ぐるぐる目 → あせ・火花）→
     ハート → 「ヒヒーン！」→ 枠（毛糸玉は 馬とロボットの うしろ、馬は ロボットの うしろを通る＝いつもの絵と同じ重なり）
   - 1回（回のはじめ＝前の回で 毛糸玉を はなした時）：投げた毛糸玉が 左の外へ（FLY 秒）→ GAP（1.7秒）あけて 左から ころころ転がってくる
     （すべらない：進んだぶんだけ回る）→ だんだん ゆっくりになって いつもの場所に止まる（ロボットの黒目と 馬のボタンの目は 毛糸玉を追う。
     馬は 毛糸玉が頭の下を通る時に 少し前へ のぞきこむ）→ 馬が ぴょん・ぴょんと2回跳ねて喜ぶ（ハートが3つ）→
     ロボットが 拾いに 右へ とことこ3歩 → 右足が当たって うっかり蹴っちゃう（毛糸玉が 右へ ころん・フェードアウト）→ びっくり（あせ・ぴょん）→ そのあと 3とおり：
     ・N（いつもの）：あわてて追いかけて 右へ フェードアウト → 1秒後に 毛糸玉を 手に持って 右から戻ってくる → 馬に見せる → 2秒後に 左へポーン
     ・A（故障 → 復活）：追いかけようと 1歩目を出しかけた所で 故障（ガクッ・ブルブル・目が ぐるぐる・アンテナが へにゃっ・火花・けむり プスッ）→
       馬が 前足を上げて 首を上にあげ「ヒヒーン！」→ ロボットが ピコーンと復活（アンテナが ぴょん・目が もどる・ぴょん）→ 追いかけて あとは N と同じ
     ・B（故障 → 治らない）：同じく故障 → 「ヒヒーン！」→ 直りかけて また へにゃっ（火花・けむり プスン）→ 馬が 毛糸玉の方を見て、
       ぴょこぴょこ右へ（ロボットの うしろを通って）フェードアウト → 1秒後に 毛糸玉を くわえて 右から戻ってくる（左向き）→ 見せて →
       首を ふり上げて 左へポーン → 次の回の はじめに 馬は 右向きに戻り、ロボットは ピコーンと再起動して もとの場所へ 2歩もどる
   - A と B は、それぞれ 3〜8回に1回（ROUNDS の順で ばらばら・plan で確かめる）。ROUNDS の回ぶんで1回り（CYCLE 秒）。ページを開くと 1回目のはじめ（ポーン）から
   - 視差効果を減らす（prefers-reduced-motion）なら動かさない（部品が いつもの場所にあるので、いつもの絵と同じ）
   クラスの名前は kd…
   python3 kids_wall.py --judge <Judge_Kids.dc.html>   → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 kids_wall.py --plan                          → 1回りの予定（何回目に何が起きるか・何秒に どこにいるか）"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kids

ALT = ('毛糸の編み目の背景に、ぬいぐるみの馬と手をふるロボット、毛糸玉のイラスト（毛糸玉が左から ころころ転がってきて、ロボットと馬が目で追い、'
       '止まると馬が跳ねて喜ぶ。ロボットが拾いに行って うっかり蹴ってしまい、毛糸玉といっしょに画面の外へ。毛糸玉を持って戻ってきて、左へポーンと投げる。'
       'ときどき ロボットが故障して 馬が「ヒヒーン」と鳴き、ロボットが直って取りにいくか、馬が 毛糸玉を くわえて取ってくる）')
ROUNDS = 'NANBNNABN'          # 1回りの 回の順（N いつもの・A 故障 → 復活・B 故障 → 治らない）。A も B も 3〜8回に1回
FLY = .66                     # 投げた毛糸玉が 左の外に出るまで（秒）
GAP = 1.7                     # 外に出てから 転がってくるまで（まさちゃん「毛糸投げてけら画面上に転がるまで1.7秒間を空けて」）
D0 = FLY + GAP - 1.0          # 前の流れ（12秒・1秒で転がりはじめ）からの ずれ
ROLL = (1.0 + D0, 3.0 + D0, 4.0 + D0)    # 転がりはじめ・ゆっくりになりはじめ・止まる（回のはじめからの秒）
X0 = -12.0                    # 転がりはじめの 毛糸玉のまん中（枠の左の外）
SLOW = .2                     # ゆっくりになる間に進む道のりの わりあい（なめらかに ゆっくりになる）
EYE_H = 2.4                   # 馬のボタンの目が動く大きさ（馬の座標）・うしろ向きは小さく（EYE_H_BACK）
EYE_H_BACK = 1.2
EYE_R = 2.6                   # ロボットの黒目が 目のまん中から動く大きさ（ロボットの座標・白目の内がわに入る）
HOP_O = (121, 145.5)          # 馬が跳ねる時の 中心（足もと）
# 跳ねて喜ぶ：(秒, 上へ, よこ・たての のび, かたむき, 次までの動き)
HOP = [(4.00 + D0, 0, 1, 1, 0, 'quad-out'), (4.12 + D0, 0, 1.06, .9, 0, 'quad-out'), (4.40 + D0, 18, 1, 1, -4, 'quad-in'),
       (4.66 + D0, 0, .98, 1.03, 1, 'quad-out'), (4.74 + D0, 0, 1.06, .91, 0, 'quad-out'), (4.96 + D0, 10, 1, 1, -2, 'quad-in'),
       (5.16 + D0, 0, .99, 1.02, .5, 'quad-out'), (5.24 + D0, 0, 1.04, .94, 0, 'ease-in-out'), (5.40 + D0, 0, 1, 1, 0, 'linear')]
# 毛糸玉が 頭の下を通る時に 少し前へ のぞきこむ（前足のところを中心に かたむく）：(秒, かたむき, 次までの動き)
LEAN_O = (139, 145)
LEAN = [(1.65 + D0, 0, 'ease-in-out'), (2.05 + D0, 2.5, 'linear'), (2.35 + D0, 2.5, 'ease-in-out'), (2.8 + D0, 0, 'linear')]
# ハート：(出る秒, まん中, 大きさ, 色)
HEARTS = [(4.30 + D0, (184, 38), 6.4, '#F7A8C0'), (4.42 + D0, (204, 30), 5.4, '#FFB7C5'), (4.90 + D0, (168, 30), 5.6, '#F7A8C0')]
# ロボット（秒・ずれは絵の px）
WALK = (5.6 + D0, 6.5 + D0, 50.0)        # 拾いに行く：右へ 3歩（50px）
KICK = (6.5 + D0, 6.62 + D0, 6.76 + D0)  # 右足を出す → 毛糸玉に当たる（うっかり蹴る）→ もどす
SURP = (6.72 + D0, 6.8 + D0)             # びっくり（ぴょん）
CB = 6.92 + D0                           # 追いかけはじめ（N）・故障（A・B）
CHASE = (.68, 112.0)                     # あわてて追いかける：右へ 3歩（112pxまで）
# 追いかけはじめからの秒（N。A は DA 秒おくれ）
FADE_OUT = (.13, .68)                    # 毛糸玉といっしょに フェードアウト
HELD_ON = 1.08                           # 見えない間に 手に毛糸玉を持つ
BACK = (1.68, 3.08)                      # 1秒後に 右から戻る（4歩）→ もとの場所
FADE_IN = (1.68, 1.98)
SHOW = (3.53, 4.13)                      # 持ってきた毛糸玉を 馬に見せる（ふる・ぴょん）
WIND = (4.58, 4.88)                      # 投げる前に ためる → RELEASE で はなす
RELEASE = 5.08
HELD = (302, 48)                         # 手に持った毛糸玉のまん中（いつもの 右手の上）
THROW = ((196, 21), -24.0)               # ロボットが投げた毛糸玉：いちばん高い所・出た所の x（放物線・FLY 秒）
THROW_SPIN = -560.0
BALL_OUT = 48.0                          # 蹴られた毛糸玉が 右へ ころがる道のり（蹴ってから 追いかけおわるまで）
BALL_FADE = (6.95 + D0, 7.5 + D0)
LOOK_HORSE = (150, 64)                   # ロボットが 馬を見る時に 見る所（馬の顔）
OFF_R = (440, 120)                       # 右の外（出ていった所）
OFF_L = (-20, 128)                       # 左の外（投げた毛糸玉が 落ちた所）
N_BOB = (0.0, 1.0, 1.0, 0.0)             # ロボットの体：(上へ, よこ・たての のび, かたむき)
# 故障（A・B）：追いかけはじめ CB からの秒
BRK = .12                                # ガクッ（ここから ぐるぐる目・アンテナ へにゃっ・火花）
BROKE = (-1.0, 1.03, .96, 8.0)           # へたりこんだ体
NEIGH = CB + .87                         # 馬が立ち上がって「ヒヒーン！」（回のはじめからの秒）
NEIGH_UP, NEIGH_HOLD, NEIGH_DOWN = .25, .8, .25
REAR_O = (103, 145)                      # 立ち上がる時の 中心（うしろ足）
REAR_A = -20.0                           # 立ち上がる角度（前が上がる）
FIX = NEIGH + NEIGH_UP + NEIGH_HOLD + NEIGH_DOWN + .1    # 復活（A）・直りかけて また へにゃっ（B）
CA = FIX + .55                           # A：追いかけはじめ
DA = CA - CB                             # A は N より これだけ長い
# B：馬が 毛糸玉を取りにいく
GO_H = FIX + .7                          # 右へ ぴょこぴょこ（6回）
OUT_H = (1.4, 250.0)                     # かかる秒・右へ（px）
OFF_H = 1.0                              # 見えない間（1秒後に戻る）
BACK_H = 1.4                             # 戻る秒（6回）
TOSS_A = -20.0                           # 首を ふり上げて投げる（左向き）
FLIP_O = (130, 145)                      # 向きを変える時の まん中
HORSE_HELD = (176, 82)                   # くわえた毛糸玉のまん中（右向きで いつもの場所の時・絵の座標）
H_THROW = ((40, 16), -24.0)              # 馬が投げた毛糸玉：いちばん高い所・出た所の x（FLY 秒）
EASE = {'linear': 'linear', 'quad-out': 'cubic-bezier(.33,.67,.67,1)', 'quad-in': 'cubic-bezier(.33,0,.67,.33)', 'ease-in-out': 'ease-in-out',
        'ease-in': 'ease-in', 'ease-out': 'ease-out'}
BEZ = {'quad-out': (1 / 3, 2 / 3, 2 / 3, 1), 'quad-in': (1 / 3, 0, 2 / 3, 1 / 3), 'ease-in-out': (.42, 0, .58, 1), 'ease-in': (.42, 0, 1, 1), 'ease-out': (0, 0, .58, 1)}
IDS = (('knit', 'kdKnit'), ('felt', 'kdFelt'))
SWEAT = ('<path d="M227 44.6 C 228.3 47.4, 230.8 49.8, 230.8 52.2 A 3.8 3.8 0 0 1 223.2 52.2 C 223.2 49.8, 225.7 47.4, 227 44.6 Z" '
         f'fill="#BFE8FB" stroke="{kids.BR}" stroke-width="1.1" stroke-linejoin="round"/><ellipse cx="225.6" cy="52" rx=".9" ry="1.4" fill="#FFFFFF"/>')
SWEAT_B = (221, 43, 12, 15)


def round_len(kind):
    if kind == 'N':
        return CB + RELEASE
    if kind == 'A':
        return CB + DA + RELEASE
    return toss_release()


def toss_release():
    """B：馬が 毛糸玉を はなす秒（回のはじめから）"""
    return GO_H + OUT_H[0] + OFF_H + BACK_H + 1.31


def plan_rounds():
    """[(はじめの秒, 種類, 前の回の種類)]・1回りの秒。A・B が 3〜8回に1回か（1回りの つなぎ目も）を確かめる"""
    out, t = [], 0.0
    n = len(ROUNDS)
    for i, k in enumerate(ROUNDS):
        out.append((t, k, ROUNDS[i - 1]))
        t += round_len(k)
    for k in 'AB':
        at = [i for i, c in enumerate(ROUNDS) if c == k]
        gaps = [b - a for a, b in zip(at, at[1:] + [at[0] + n])]
        assert all(3 <= g <= 8 for g in gaps), (k, gaps)
    assert ROUNDS[-1] != 'B', '1回りの さいごは ロボットが投げる回（ページを開いた時の形）'
    return out, round(t, 4)


RUNS, CYCLE = plan_rounds()


def pct(t):
    s = f'{t / CYCLE * 100:.4f}'.rstrip('0').rstrip('.')
    return s + '%'


def num(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    if s in ('-0', ''):
        return '0'
    return s.replace('0.', '.', 1) if s.startswith(('0.', '-0.')) else s


def u(v, unit, nd=2):
    """数と単位（0 は 単位なし）"""
    s = num(v, nd)
    return s if s == '0' else s + unit


def sc2(sx, sy):
    return f'scale({num(sx, 3)})' if abs(sx - sy) < 1e-9 else f'scale({num(sx, 3)},{num(sy, 3)})'


def ease(e, s):
    """CSS の動き（cubic-bezier）の 0〜1 → 0〜1"""
    if e == 'linear' or s <= 0 or s >= 1:
        return min(max(s, 0.0), 1.0)
    x1, y1, x2, y2 = BEZ[e]
    lo, hi = 0.0, 1.0
    for _ in range(50):
        u = (lo + hi) / 2
        x = 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3
        lo, hi = (u, hi) if x < s else (lo, u)
    u = (lo + hi) / 2
    return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u * u * y2 + u ** 3


def mix(a, b, s):
    if isinstance(a, tuple):
        return tuple(x + (y - x) * s for x, y in zip(a, b))
    return a + (b - a) * s


class Tr:
    """キーフレームの列：[秒, 値, 次のキーまでの動き]。値は 数か タプル"""
    def __init__(self, v):
        self.k = [[0.0, v, 'linear']]

    def hold(self, t):
        if t > self.k[-1][0] + 1e-9:
            self.k.append([t, self.k[-1][1], 'linear'])
        return self

    def go(self, t, v, e='ease-in-out'):
        """前のキーから t 秒の v まで e で動く"""
        assert t > self.k[-1][0] + 1e-9, (t, self.k[-1][0])
        self.k[-1][2] = e
        self.k.append([t, v, 'linear'])
        return self

    def set(self, t, v):
        """t 秒で すぐに v（0.001秒で 切りかえ）"""
        return self.hold(t).go(t + .001, v, 'linear')

    def end(self):
        return self.hold(CYCLE)

    def at(self, t):
        k = self.k
        if t <= k[0][0]:
            return k[0][1]
        lo, hi = 0, len(k) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if k[m][0] <= t:
                lo = m
            else:
                hi = m
        (t0, v0, e), (t1, v1, _) = k[lo], k[hi]
        if t >= t1:
            return v1
        return mix(v0, v1, ease(e, (t - t0) / (t1 - t0)) if t1 > t0 else 1)


def page_xy(p, at):
    x, y, s = at
    return x + p[0] * s, y + p[1] * s


RP = lambda p: page_xy(p, kids.ROBOT_AT)
SHOULDER = (RP((24, 72)), RP((68, 70)))       # 腕を回す所（左・右）
ANKLE = (RP((38, 106)), RP((56, 106)))        # 足を回す所（左・右）
BOB_O = RP((47, 118.6))                       # 体が はねる・かたむく 中心（足もとの まん中）
ANT_O = RP((46, 21))                          # アンテナの根もと
ROBOT_HEAD = RP((46, 40))                     # 頭のまん中（馬が見る所）


def walk(T, t0, t1, x0, x1, n, lead, h, lean, sw, lift=3.2, fwd=3.0):
    """n 歩で ずれ x0 → x1（t0〜t1 秒）。1歩ごとに 体が ぴょこっと上がって、上げた足が 前へ出る。lead＝最初に上げる足（0 左・1 右）"""
    dx, bob, foot, arm = T['dx'], T['bob'], T['foot'], T['arm']
    d = (t1 - t0) / n
    sg = 1 if x1 > x0 else -1
    for tr in (dx, bob, *foot, *arm):
        tr.hold(t0)
    for k in range(n):
        a, b = t0 + k * d, t0 + (k + 1) * d
        m = a + d / 2
        f = lead if k % 2 == 0 else 1 - lead
        dx.go(b, x0 + (x1 - x0) * (k + 1) / n, 'ease-in-out')
        bob.go(m, (h, 1.0, 1.0, (-3.0 if f == 1 else 3.0) + sg * lean), 'quad-out')
        bob.go(b, (0.0, 1.0, 1.0, sg * lean if k < n - 1 else 0.0), 'quad-in')
        foot[f].hold(a).go(m, (sg * fwd, -lift, 0.0), 'quad-out').go(b, (0.0, 0.0, 0.0), 'quad-in')
        s = 1 if f == 1 else -1
        arm[0].go(m, s * sw[0], 'ease-in-out')
        arm[1].go(m, -s * sw[1], 'ease-in-out')
    arm[0].go(t1, 0.0, 'ease-in-out')
    arm[1].go(t1, 0.0, 'ease-in-out')


def hop_walk(H, t0, t1, x0, x1, n, h=7.0, tilt=3.0):
    """馬が ぴょこぴょこ n 回はねて ずれ x0 → x1（ぬいぐるみなので 足は動かさない）"""
    dx, hop = H['dx'], H['hop']
    d = (t1 - t0) / n
    dx.hold(t0)
    hop.hold(t0)
    for k in range(n):
        a, b = t0 + k * d, t0 + (k + 1) * d
        dx.go(b, x0 + (x1 - x0) * (k + 1) / n, 'ease-in-out')
        hop.go(a + d * .5, (h, 1.0, 1.0, -tilt), 'quad-out').go(b, (0.0, 1.03, .96, 0.0), 'quad-in')
    hop.go(t1 + .14, (0.0, 1.0, 1.0, 0.0), 'ease-out')


def pop(tr, t0, t1, big=1.12):
    """ぽんと出て（大きく → もとの大きさ）t1 まで出て すっと消える：値は (大きさ, こさ)"""
    tr.hold(t0).go(t0 + .001, (.3, 0.0), 'linear').go(t0 + .12, (big, 1.0), 'quad-out').go(t0 + .22, (1.0, 1.0), 'ease-in-out')
    tr.hold(t1).go(t1 + .2, (1.05, 0.0), 'ease-in').go(t1 + .201, (.3, 0.0), 'linear')


def flicker(tr, t0, n=4, dt=.08):
    """火花：ちかっ・ちかっ（小さいので 点めつは だいじょうぶ）"""
    for i in range(n):
        tr.set(t0 + 2 * i * dt, 1.0).set(t0 + (2 * i + 1) * dt, 0.0)


def puff(tr, t0, rise=26.0, dur=1.2):
    """けむり：(上へ, 大きさ, こさ)"""
    tr.hold(t0).go(t0 + .001, (0.0, .5, 0.0), 'linear').go(t0 + .18, (5.0, .9, .9), 'quad-out').go(t0 + dur, (rise, 1.35, 0.0), 'ease-out')
    tr.go(t0 + dur + .001, (0.0, .5, 0.0), 'linear')


def robot_tracks():
    """ロボットの動き（1回りぶん）"""
    T = dict(dx=Tr(0.0), op=Tr(1.0), bob=Tr(N_BOB), foot=[Tr((0.0, 0.0, 0.0)), Tr((0.0, 0.0, 0.0))], arm=[Tr(0.0), Tr(0.0)],
             held=Tr(0.0), sweat=Tr((0.0, .3, 0.0)), ant=Tr(0.0), broken=Tr(0.0), spark=Tr(0.0), smoke=[Tr((0.0, .5, 0.0)), Tr((0.0, .5, 0.0))],
             sparkle=Tr((.3, 0.0)))
    bob, arm, foot = T['bob'], T['arm'], T['foot']
    for S, kind, prev in RUNS:
        if prev == 'B':
            reboot(T, S)
        else:
            # 毛糸玉を はなした あと（のびて 左へ ふりぬく → もどる）
            bob.hold(S).go(S + .12, (3.0, .95, 1.07, -5.0), 'quad-out').go(S + .3, (0.0, 1.04, .95, -2.0), 'quad-in').go(S + .55, N_BOB, 'ease-out')
            arm[1].hold(S).go(S + .12, -22.0, 'quad-out').go(S + .3, -8.0, 'ease-in-out').go(S + .55, 0.0, 'ease-out')
            arm[0].hold(S).go(S + .12, 10.0, 'quad-out').go(S + .55, 0.0, 'ease-in-out')
        # 拾いに行く（右へ 3歩）→ 右足が 毛糸玉に当たる（うっかり蹴る）→ びっくり（ぴょん・あせ・腕が はねる）
        walk(T, S + WALK[0], S + WALK[1], 0.0, WALK[2], 3, lead=0, h=2.6, lean=2.0, sw=(10, 6))
        k0, k1, k2 = (S + k for k in KICK)
        foot[1].hold(k0).go(k1, (9.0, -4.0, -22.0), 'quad-out').go(k2, (0.0, 0.0, 0.0), 'ease-in-out')
        bob.hold(k0).go(k1, (0.0, 1.0, 1.0, -3.0), 'ease-out')
        c = S + CB
        bob.go(S + SURP[0], (4.0, .95, 1.07, 0.0), 'quad-out').go(S + SURP[1], (0.0, 1.05, .94, 0.0), 'quad-in').go(c, (0.0, 1.0, 1.0, 3.0), 'ease-out')
        arm[0].hold(k1).go(S + SURP[0], 28.0, 'quad-out').go(c, 8.0, 'ease-in-out')
        arm[1].hold(k1).go(S + SURP[0], 12.0, 'quad-out').go(c, 0.0, 'ease-in-out')
        T['sweat'].set(k1 + .04, (0.0, .3, 1.0)).go(k1 + .12, (0.0, 1.15, 1.0), 'quad-out').go(k1 + .18, (0.0, 1.0, 1.0), 'ease-in-out')
        if kind == 'N':
            T['sweat'].go(c + .53, (3.0, 1.0, 1.0), 'ease-in')
            chase_and_back(T, S, c)
        else:
            breakdown(T, S)
            if kind == 'A':
                recover(T, S + FIX)
                chase_and_back(T, S, S + CA)
            else:
                fail_fix(T, S + FIX)
    for tr in (T['dx'], T['op'], T['held'], T['sweat'], T['ant'], T['broken'], T['spark'], T['sparkle'], bob, *foot, *arm, *T['smoke']):
        tr.end()
    return T


def chase_and_back(T, S, c):
    """あわてて追いかけて フェードアウト → 1秒後に 毛糸玉を持って戻る → 見せる → ためて はなす（c＝追いかけはじめ）"""
    bob, arm = T['bob'], T['arm']
    walk(T, c, c + CHASE[0], WALK[2], CHASE[1], 3, lead=1, h=3.4, lean=7.0, sw=(22, 14), lift=3.6, fwd=4.0)
    T['op'].hold(c + FADE_OUT[0]).go(c + FADE_OUT[1], 0.0, 'ease-in')
    T['sweat'].set(c + FADE_OUT[1], (0.0, .3, 0.0))
    T['held'].set(c + HELD_ON, 1.0)
    T['op'].hold(c + FADE_IN[0]).go(c + FADE_IN[1], 1.0, 'ease-out')
    walk(T, c + BACK[0], c + BACK[1], CHASE[1], 0.0, 4, lead=0, h=2.6, lean=3.0, sw=(12, 3))
    b0 = c + BACK[1]
    bob.hold(b0).go(b0 + .1, (0.0, 1.05, .93, 0.0), 'quad-out').go(b0 + .28, N_BOB, 'ease-out')
    s0, s1 = c + SHOW[0], c + SHOW[1]
    arm[1].hold(s0).go(s0 + .15, -8.0, 'ease-in-out').go(s0 + .3, 5.0, 'ease-in-out').go(s0 + .45, -4.0, 'ease-in-out').go(s1, 0.0, 'ease-in-out')
    bob.hold(s0).go(s0 + .13, (2.5, .97, 1.04, 0.0), 'quad-out').go(s0 + .25, (0.0, 1.03, .96, 0.0), 'quad-in').go(s0 + .37, N_BOB, 'ease-out')
    w0, w1, r = c + WIND[0], c + WIND[1], c + RELEASE
    bob.hold(w0).go(w1, (0.0, 1.06, .9, 4.0), 'ease-in-out').go(r, N_BOB, 'quad-in')
    arm[1].hold(w0).go(w1, 24.0, 'ease-in-out').go(r, 0.0, 'quad-in')
    arm[0].hold(w0).go(w1, -8.0, 'ease-in-out').go(r, 0.0, 'quad-in')
    if r < CYCLE - 1e-6:
        T['held'].set(r, 0.0)
    else:                                                # 1回りの さいご：ちょうど 0秒（はじめ）で 投げた毛糸玉と 入れかわる
        T['held'].hold(r - .001).go(r, 0.0, 'linear')


def breakdown(T, S):
    """故障：追いかけようと 1歩目を出しかけて → ガクッ・ブルブル → へたりこむ（ぐるぐる目・アンテナ へにゃっ・火花・けむり）"""
    bob, arm, foot = T['bob'], T['arm'], T['foot']
    c = S + CB
    b = c + BRK
    foot[1].hold(c).go(c + .08, (4.0, -3.6, 0.0), 'quad-out').go(b + .1, (0.0, 0.0, 0.0), 'quad-in')
    bob.hold(c).go(b, (1.5, 1.0, 1.0, 7.0), 'quad-out')
    for i in range(6):
        bob.go(b + .05 * (i + 1), (.6, 1.0, 1.0, 7.0 + (2.6 if i % 2 == 0 else -2.6)), 'linear')
    bob.go(b + .55, BROKE, 'ease-out')
    T['dx'].hold(b)
    for i in range(6):
        T['dx'].go(b + .05 * (i + 1), WALK[2] + (1.0 if i % 2 == 0 else -1.0), 'linear')
    T['dx'].go(b + .35, WALK[2], 'linear')
    arm[0].hold(c).go(b + .55, 16.0, 'ease-out')
    arm[1].hold(c).go(b + .55, -12.0, 'ease-out')
    T['ant'].hold(b).go(b + .2, 58.0, 'quad-out').go(b + .32, 46.0, 'ease-in-out').go(b + .45, 52.0, 'ease-in-out')
    T['broken'].set(b, 1.0)
    T['sweat'].hold(b).go(b + .15, (2.0, .8, 0.0), 'ease-in').go(b + .151, (0.0, .3, 0.0), 'linear')
    flicker(T['spark'], b, 4)
    puff(T['smoke'][0], b + .1)


def recover(T, r):
    """ピコーンと復活：アンテナが ぴょん・目が もどる・ぴょん → 追いかける形（c の時と同じ）"""
    bob, arm = T['bob'], T['arm']
    T['ant'].hold(r).go(r + .13, -12.0, 'quad-out').go(r + .23, 4.0, 'ease-in-out').go(r + .33, 0.0, 'ease-out')
    T['broken'].set(r + .05, 0.0)
    pop(T['sparkle'], r, r + .3)
    bob.hold(r).go(r + .1, (4.0, .95, 1.07, 0.0), 'quad-out').go(r + .2, (0.0, 1.05, .94, 0.0), 'quad-in').go(r + .4, (0.0, 1.0, 1.0, 3.0), 'ease-out')
    arm[0].hold(r).go(r + .3, 8.0, 'ease-out')
    arm[1].hold(r).go(r + .3, 0.0, 'ease-out')


def fail_fix(T, r):
    """B：直りかけて（アンテナが 半分 もどる）→ また へにゃっ（火花・けむり プスン）"""
    T['ant'].hold(r).go(r + .15, 22.0, 'quad-out').go(r + .35, 58.0, 'quad-in').go(r + .45, 52.0, 'ease-out')
    T['bob'].hold(r).go(r + .12, (1.0, 1.0, 1.0, 4.0), 'quad-out').go(r + .35, BROKE, 'quad-in')
    flicker(T['spark'], r + .3, 2)
    puff(T['smoke'][1], r + .32, 22.0, 1.1)


def reboot(T, S):
    """B のあと（次の回の はじめ）：ピコーンと再起動して、もとの場所へ 2歩もどる"""
    r = S + .9
    T['ant'].hold(r).go(r + .13, -12.0, 'quad-out').go(r + .23, 4.0, 'ease-in-out').go(r + .33, 0.0, 'ease-out')
    T['broken'].set(r + .05, 0.0)
    pop(T['sparkle'], r, r + .3)
    T['bob'].hold(r).go(r + .1, (4.0, .95, 1.07, 0.0), 'quad-out').go(r + .2, (0.0, 1.05, .94, 0.0), 'quad-in').go(r + .38, N_BOB, 'ease-out')
    T['arm'][0].hold(r).go(r + .3, 0.0, 'ease-out')
    T['arm'][1].hold(r).go(r + .3, 0.0, 'ease-out')
    walk(T, S + 1.5, S + 2.15, WALK[2], 0.0, 2, lead=0, h=2.4, lean=2.0, sw=(8, 5))


def horse_tracks():
    """馬の動き（1回りぶん）：dx（よこ）・op（こさ）・flip（向き）・hop（はねる）・lean（のぞきこむ）・rear（立ち上がる）・held（くわえた毛糸玉）"""
    H = dict(dx=Tr(0.0), op=Tr(1.0), flip=Tr(1.0), hop=Tr((0.0, 1.0, 1.0, 0.0)), lean=Tr(0.0), rear=Tr(0.0), held=Tr(0.0),
             bubble=Tr((.3, 0.0)))
    for S, kind, prev in RUNS:
        if prev == 'B':                                  # 投げた あと：おりて → 右向きに もどる
            H['rear'].hold(S).go(S + .06, TOSS_A - 2, 'quad-out').go(S + .3, 0.0, 'quad-in')
            H['hop'].hold(S + .3).go(S + .38, (0.0, 1.05, .93, 0.0), 'quad-out').go(S + .5, (0.0, 1.0, 1.0, 0.0), 'ease-out')
            H['flip'].hold(S + .55).go(S + .75, 1.0, 'ease-in-out')
        H['lean'].hold(S + LEAN[0][0])                   # 毛糸玉が 頭の下を通る時に のぞきこむ
        for (t, a, e), (t1, a1, _) in zip(LEAN, LEAN[1:]):
            H['lean'].go(S + t1, a1, e)
        H['hop'].hold(S + HOP[0][0])                     # 跳ねて喜ぶ
        for (t, h, sx, sy, rot, e), (t1, h1, sx1, sy1, rot1, _) in zip(HOP, HOP[1:]):
            H['hop'].go(S + t1, (h1, sx1, sy1, rot1), e)
        if kind in 'AB':
            neigh(H, S + NEIGH)
        if kind == 'B':
            fetch(H, S)
    for tr in H.values():
        tr.end()
    return H


def neigh(H, n0):
    """前足を上げて 首を上にあげて「ヒヒーン！」（うしろ足を中心に 立ち上がる・鳴いている間 ふるえる）→ おりる"""
    up, hold, down = n0 + NEIGH_UP, n0 + NEIGH_UP + NEIGH_HOLD, n0 + NEIGH_UP + NEIGH_HOLD + NEIGH_DOWN
    H['rear'].hold(n0).go(up, REAR_A, 'quad-out')
    n = 8
    for i in range(n):
        H['rear'].go(up + (hold - up) * (i + 1) / n, REAR_A + (1.6 if i % 2 == 0 else -1.6) if i < n - 1 else REAR_A, 'ease-in-out')
    H['rear'].go(down, 0.0, 'quad-in')
    H['hop'].hold(down).go(down + .08, (0.0, 1.05, .93, 0.0), 'quad-out').go(down + .22, (0.0, 1.0, 1.0, 0.0), 'ease-out')
    pop(H['bubble'], n0 + .18, hold - .05)


def fetch(H, S):
    """B：馬が 毛糸玉の方へ ぴょこぴょこ → フェードアウト → 1秒後に くわえて 左向きで戻る → 見せる → 首を ふり上げて はなす"""
    g0 = S + GO_H
    g1 = g0 + OUT_H[0]
    hop_walk(H, g0, g1, 0.0, OUT_H[1], 6)
    H['op'].hold(g1 - .35).go(g1, 0.0, 'ease-in')
    H['flip'].set(g1 + .3, -1.0)
    H['held'].set(g1 + .35, 1.0)
    b0 = g1 + OFF_H
    b1 = b0 + BACK_H
    H['op'].hold(b0).go(b0 + .3, 1.0, 'ease-out')
    hop_walk(H, b0, b1, OUT_H[1], 0.0, 6)
    hp = H['hop']
    hp.hold(b1 + .3).go(b1 + .42, (6.0, .97, 1.04, -2.0), 'quad-out').go(b1 + .55, (0.0, 1.04, .95, 0.0), 'quad-in').go(b1 + .7, (0.0, 1.0, 1.0, 0.0), 'ease-out')
    H['lean'].hold(b1 + .9).go(b1 + 1.15, 5.0, 'ease-in-out').go(b1 + 1.3, 0.0, 'quad-out')
    r = S + toss_release()
    H['rear'].hold(b1 + 1.15).go(r, TOSS_A, 'quad-out')
    H['held'].set(r, 0.0)


def ground_tracks():
    """地面の毛糸玉（糸つき）：左から転がる → 止まる → 蹴られて 右へ ころん・フェードアウト（どの回も同じ）"""
    xe = kids.YARN_BALL[0]
    x1 = X0 + (1 - SLOW) * (xe - X0)
    gx, gop, gy = Tr(X0 - xe), Tr(1.0), Tr(0.0)
    for S, kind, prev in RUNS:
        if S > 0:
            gx.set(S, X0 - xe)
            gop.set(S + .01, 1.0)
        t0, t1, t2 = (S + t for t in ROLL)
        gx.hold(t0).go(t1, x1 - xe, 'linear').go(t2, 0.0, 'quad-out').hold(S + KICK[1]).go(S + CB + CHASE[0], BALL_OUT, 'quad-out')
        gop.hold(S + BALL_FADE[0]).go(S + BALL_FADE[1], 0.0, 'ease-in')
        k = S + KICK[1]
        gy.hold(k).go(k + .1, -6.0, 'quad-out').go(k + .22, 0.0, 'quad-in').go(k + .29, -2.0, 'quad-out').go(k + .36, 0.0, 'quad-in')
    gx.set(CYCLE - .02, X0 - xe)
    gop.set(CYCLE - .01, 1.0)
    return gx.end(), gop.end(), gy.end()


def arc(p0, apex, x_end, te):
    """放物線（よこは同じ速さ）：(いちばん高い所までの秒, 出た所の y)"""
    vx = (x_end - p0[0]) / te
    ta = (apex[0] - p0[0]) / vx
    g = 2 * (p0[1] - apex[1]) / ta ** 2
    return ta, apex[1] + .5 * g * (te - ta) ** 2


class Scene:
    """動きを まとめて持ち、何秒に どこにいるかを出す（目の向き・たしかめ）"""
    def __init__(self):
        self.R = robot_tracks()
        self.H = horse_tracks()
        self.gx, self.gop, self.gy = ground_tracks()
        self.throw_tracks()

    # ---- 馬 ----
    def horse_map(self, p, t):
        """馬の絵の点 p（いつもの場所の座標）が t 秒に どこにあるか（立ち上がる → のぞきこむ → はねる → 向き → よこ）"""
        H = self.H
        x, y = rot_map(p, REAR_O, H['rear'].at(t))
        x, y = rot_map((x, y), LEAN_O, H['lean'].at(t))
        h, sx, sy, a = H['hop'].at(t)
        ox, oy = HOP_O
        vx, vy = (x - ox) * sx, (y - oy) * sy
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        x, y = ox + c * vx - s * vy, oy + s * vx + c * vy - h
        x = FLIP_O[0] + (x - FLIP_O[0]) * H['flip'].at(t)
        return x + H['dx'].at(t), y

    def horse_eye(self, t):
        """ボタンの目が 見る向き（馬の中の向き・うしろは 小さく）"""
        e = self.horse_map(page_xy(kids.HORSE_EYE, kids.HORSE_AT), t)
        x, y = self.horse_local(look(e, self.horse_look(t), EYE_H), t)
        return max(x, -EYE_H_BACK), y

    def horse_local(self, d, t):
        """ページの向き d を 馬の目の中の向きに（向き・回る角度を もどす）"""
        H = self.H
        x, y = d
        if H['flip'].at(t) < 0:
            x = -x
        a = -(H['rear'].at(t) + H['lean'].at(t) + H['hop'].at(t)[3])
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        return c * x - s * y, s * x + c * y

    # ---- ロボット ----
    def held(self, t):
        R = self.R
        q = rot_map(HELD, SHOULDER[1], R['arm'][1].at(t))
        x, y = bob_map(q, R['bob'].at(t))
        return x + R['dx'].at(t), y

    def robot_eye(self, eye, t):
        x, y = bob_map(eye, self.R['bob'].at(t))
        return x + self.R['dx'].at(t), y

    # ---- 毛糸玉 ----
    def throw_tracks(self):
        """投げた毛糸玉（短い糸つき）：ロボットは 手の上から、馬は くわえた所から（よこは同じ速さ・たては 放物線）。位置は HELD からの ずれ"""
        tx, ty, top, tr = Tr(0.0), Tr(0.0), Tr(1.0), Tr(0.0)
        hx, hy = HELD
        for i, (S, kind, prev) in enumerate(RUNS):
            if prev == 'B':
                p0 = self.horse_map(HORSE_HELD, S)
                (apex, x_end) = H_THROW
            else:
                p0 = HELD
                (apex, x_end) = THROW
            ta, y_end = arc(p0, apex, x_end, FLY)
            if S > 0:
                tx.set(S - .01, p0[0] - hx)
                ty.set(S - .01, p0[1] - hy)
                tr.set(S - .01, 0.0)
                top.set(S, 1.0)
            tx.hold(S).go(S + FLY, x_end - hx, 'linear')
            ty.hold(S).go(S + ta, apex[1] - hy, 'quad-out').go(S + FLY, y_end - hy, 'quad-in')
            tr.hold(S).go(S + FLY, THROW_SPIN, 'linear')
            top.set(S + FLY, 0.0)
        # 1回りの さいご：はじめ（1回目・ロボットが投げる）の形に もどしておき、ちょうど 0秒で 見える
        e = CYCLE - .011
        tx.set(e, 0.0)
        ty.set(e, 0.0)
        tr.set(e, 0.0)
        top.hold(CYCLE - .001).go(CYCLE, 1.0, 'linear')
        self.tx, self.ty, self.top, self.tr = tx.end(), ty.end(), top.end(), tr.end()

    def thrown(self, t):
        return HELD[0] + self.tx.at(t), HELD[1] + self.ty.at(t)

    def ground(self, t):
        xe, ye, _ = kids.YARN_BALL
        return xe + self.gx.at(t), ye + self.gy.at(t)

    def round_at(self, t):
        for S, kind, prev in reversed(RUNS):
            if t >= S - 1e-9:
                return S, kind, prev
        return RUNS[0]

    def ball(self, t):
        """見えている毛糸玉（目で追う所）"""
        S, kind, prev = self.round_at(t)
        u = t - S
        if u < FLY:
            return self.thrown(t)
        if u < ROLL[0]:
            return OFF_L
        if u < BALL_FADE[1]:
            return self.ground(t)
        if kind == 'B':
            if u < GO_H + OUT_H[0] + OFF_H:
                return OFF_R
            return self.horse_map(HORSE_HELD, t)
        c = CB + (DA if kind == 'A' else 0)
        if u < c + BACK[0]:
            return OFF_R
        return self.held(t)

    def robot_look(self, t):
        """ロボットが見る所：戻ってくる時と 見せる時は 馬の顔、再起動の あとも 馬の顔、それ以外は 毛糸玉"""
        S, kind, prev = self.round_at(t)
        u = t - S
        if prev == 'B' and .9 <= u < ROLL[0]:
            return LOOK_HORSE
        if kind in 'NA':
            c = CB + (DA if kind == 'A' else 0)
            if c + BACK[0] <= u < c + WIND[0]:
                return LOOK_HORSE
        return self.ball(t)

    def horse_look(self, t):
        """馬が見る所：故障した ロボット → （B）毛糸玉の方（右）→ 戻る時は 前（左）→ ロボット → 投げる毛糸玉。それ以外は 毛糸玉"""
        S, kind, prev = self.round_at(t)
        u = t - S
        rob = (ROBOT_HEAD[0] + self.R['dx'].at(t), ROBOT_HEAD[1])
        if prev == 'B' and .9 <= u < 1.5:
            return rob
        if kind in 'AB' and CB + BRK <= u < FIX + .5:
            return rob
        if kind == 'B':
            g1 = GO_H + OUT_H[0]
            b1 = g1 + OFF_H + BACK_H
            if FIX + .5 <= u < g1 + OFF_H:
                return (520, 90)
            if g1 + OFF_H <= u < b1:
                return (-160, 100)
            if b1 <= u < b1 + 1.15:
                return rob
            if u >= b1 + 1.15:
                return (-40, -20)
        return self.ball(t)

    def check(self):
        R, H = self.R, self.H
        for tr in list(R.values()) + list(H.values()) + [self.gx, self.gop, self.gy, self.tx, self.ty, self.top, self.tr]:
            for t_ in (tr if isinstance(tr, list) else [tr]):
                assert close(t_.at(0.0), t_.at(CYCLE)), ('not periodic', t_.at(0.0), t_.at(CYCLE))
        for S, kind, prev in RUNS:
            r = S + round_len(kind)
            # はなす瞬間：手（くわえた所）の毛糸玉と 投げた毛糸玉が 同じ場所
            if kind == 'B':
                p = self.horse_map(HORSE_HELD, r - 1e-6)
            else:
                assert close(R['dx'].at(r), 0) and close(R['bob'].at(r), N_BOB) and close(R['arm'][1].at(r), 0), r
                p = self.held(r)
            q = self.thrown(r % CYCLE + 1e-6)
            assert math.dist(p, q) < .6, (kind, p, q)
            # 投げた毛糸玉は 消える時に 枠の外（左の外・短い糸も）
            x, y = self.thrown((r + FLY - 1e-4) % CYCLE)
            assert x + 16 < 6, (x, y)
            # 持つ毛糸玉は 見えない間に 出る
            if kind in 'NA':
                c = S + CB + (DA if kind == 'A' else 0)
                assert close(R['op'].at(c + HELD_ON), 0) and close(R['op'].at(c + BACK[0]), 0)
                assert close(R['dx'].at(c + FADE_OUT[1]), CHASE[1]) and close(R['dx'].at(c + BACK[0]), CHASE[1])
            else:
                g1 = S + GO_H + OUT_H[0]
                assert close(H['op'].at(g1 + .35), 0) and close(H['flip'].at(g1 + .4), -1)
            assert close(self.gop.at(S + ROLL[0]), 1) and close(self.gop.at(S + BALL_FADE[1] + .01), 0)
            # けった時 足が 毛糸玉に とどく（右足の くつの右はし ≒ 毛糸玉の左はし）
            shoe_r = RP((56 + 9, 114))[0] + R['dx'].at(S + KICK[1]) + R['foot'][1].at(S + KICK[1])[0]
            assert abs(shoe_r - (kids.YARN_BALL[0] - 14)) < 4, shoe_r
            # 毛糸玉が転がってくる時、ロボットと馬は もとの場所・もとの形
            t = S + ROLL[0]
            assert all(close(a, b) for a, b in ((R['dx'].at(t), 0), (R['bob'].at(t), N_BOB), (R['broken'].at(t), 0), (R['ant'].at(t), 0),
                                                (H['dx'].at(t), 0), (H['flip'].at(t), 1), (H['rear'].at(t), 0), (H['op'].at(t), 1))), (kind, prev)


def close(a, b, eps=1e-6):
    if isinstance(a, tuple):
        return all(abs(x - y) < eps for x, y in zip(a, b))
    return abs(a - b) < eps


def bob_map(p, b):
    """体の動き（translateY(-h) rotate(a) scale(sx,sy)・中心 BOB_O）で 点 p が どこへ行くか"""
    h, sx, sy, a = b
    ox, oy = BOB_O
    vx, vy = (p[0] - ox) * sx, (p[1] - oy) * sy
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return ox + c * vx - s * vy, oy + s * vx + c * vy - h


def rot_map(p, o, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    vx, vy = p[0] - o[0], p[1] - o[1]
    return o[0] + c * vx - s * vy, o[1] + s * vx + c * vy


def look(eye, target, r, back=None):
    """目のまん中 eye から target を見る向き × r"""
    dx, dy = target[0] - eye[0], target[1] - eye[1]
    n = math.hypot(dx, dy) or 1
    ox, oy = dx / n * r, dy / n * r
    if back is not None:
        ox = max(ox, -back)
    return ox, oy


def sample(fn, tol=.15):
    """0.05秒ごとの 値 → 折れ線で だいたい同じになる 少ないキー（ずれ tol 以下）→ [(秒, (x, y), 'linear')]"""
    n = int(round(CYCLE / .05))
    ts = [CYCLE * i / n for i in range(n + 1)]
    vals = [tuple(fn(t)) for t in ts]
    keep, stack = [0, n], [(0, n)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        ta, tb = ts[a], ts[b]
        worst, wi = 0.0, -1
        for i in range(a + 1, b):
            s = (ts[i] - ta) / (tb - ta)
            e = max(abs(vals[i][j] - (vals[a][j] + (vals[b][j] - vals[a][j]) * s)) for j in range(2))
            if e > worst:
                worst, wi = e, i
        if worst > tol:
            keep.append(wi)
            stack += [(a, wi), (wi, b)]
    return [(ts[i], tuple(round(v, 2) for v in vals[i]), 'linear') for i in sorted(set(keep))]


def kf_translate(name, ks):
    return f'@keyframes {name}{{' + ''.join(f'{pct(t)}{{transform:translate({u(x, "px")},{u(y, "px")})}}' for t, (x, y), e in ks) + '}'


def slim(keys):
    """同じ値が3つ以上 つづく所は 両はしだけ（形は変わらない）"""
    out = []
    for i, key in enumerate(keys):
        if 0 < i < len(keys) - 1 and close(keys[i - 1][1], key[1], 1e-9) and close(keys[i + 1][1], key[1], 1e-9):
            continue
        out.append(key)
    return out


def kf(name, tr, fmt):
    """キーフレーム（linear の所は 書かない＝ animation の linear）"""
    out = []
    for t, v, e in slim(tr.k):
        te = '' if e == 'linear' else f';animation-timing-function:{EASE[e]}'
        out.append(f'{pct(t)}{{{fmt(v)}{te}}}')
    return f'@keyframes {name}{{' + ''.join(out) + '}'


def heart_tracks():
    """ハート（どの回も 跳ねて喜ぶ時）：(上へ, 大きさ, かたむき, こさ)"""
    out = []
    for t0, *_ in HEARTS:
        tr = Tr((0.0, .3, -10.0, 0.0))
        for S, kind, prev in RUNS:
            a = S + t0
            tr.hold(a).go(a + .14, (-3.0, 1.15, -6.0, 1.0), 'quad-out').go(a + .26, (-5.0, 1.0, -2.0, 1.0), 'ease-in-out')
            tr.go(a + .85, (-12.0, 1.0, 8.0, 1.0), 'linear').go(a + 1.15, (-16.0, .9, 10.0, 0.0), 'ease-in').go(a + 1.151, (0.0, .3, -10.0, 0.0), 'linear')
        out.append(tr.end())
    return out


def spiral(cx, cy, r=5.4, turns=2.25):
    pts = []
    n = 40
    for i in range(n + 1):
        a = turns * 2 * math.pi * i / n
        rr = r * i / n
        pts.append(f'{cx + rr * math.cos(a):.2f} {cy + rr * math.sin(a):.2f}')
    return 'M' + 'L'.join(pts)


def broken_eyes():
    """ぐるぐる目（ロボットの座標）"""
    return ''.join(f'<path d="{spiral(ex, 39)}" fill="none" stroke="#2B1E16" stroke-width="1.5" stroke-linecap="round"/>' for ex in kids.ROBOT_EYES)


SPARK = (f'<path d="M66 14 L71 8 L68 7 L74 0" fill="none" stroke="{kids.BR}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
         '<path d="M66 14 L71 8 L68 7 L74 0" fill="none" stroke="#FFD966" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<path d="M24 16 L19 11 L22 10 L16 4" fill="none" stroke="{kids.BR}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
         '<path d="M24 16 L19 11 L22 10 L16 4" fill="none" stroke="#FFD966" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')


def smoke_svg():
    """けむり（フェルトの小さな雲）・まん中 (0, 0)"""
    d = kids.smooth([(-9, 3), (-8, -3), (-3, -7), (3, -6), (8, -3), (9, 3), (4, 6), (-4, 6)])
    return kids.stitched(d, '#EEEAE2', 1.2) + kids.stitched(kids.smooth(kids.ellipse_pts(-5, -7, 4.5, 4, 8)), '#EEEAE2', 1.1)


def sparkle_svg():
    """ピコーン（黄色い星と 光の線）・まん中 (0, 0)"""
    rays = ''.join(f'<path d="M{8 * math.cos(a):.1f} {8 * math.sin(a):.1f} L{12.5 * math.cos(a):.1f} {12.5 * math.sin(a):.1f}" stroke="{kids.BR}" stroke-width="1.6" stroke-linecap="round"/>'
                   for a in [math.radians(-90 + 45 * i) for i in range(8)])
    return rays + kids.stitched(kids.star5(0, 0, 6.5), '#FFD966', 1.3)


def bubble_svg():
    """「ヒヒーン！」のふきだし（フェルト）・左下の しっぽが 馬の口へ"""
    d = kids.smooth([(-40, -12), (40, -12), (44, 0), (40, 12), (-14, 12), (-28, 22), (-24, 12), (-40, 12), (-44, 0)])
    return (kids.stitched(d, '#FFFFFF', 1.6, None, False)
            + '<text x="0" y="5" text-anchor="middle" font-size="13" font-family="\'Mochiy Pop One\',\'Zen Maru Gothic\',sans-serif" '
              f'fill="{kids.BR}">ヒヒーン！</text>')


def fix_ids(s):
    for a, b in IDS:
        s = s.replace(f'id="{a}"', f'id="{b}"').replace(f'url(#{a})', f'url(#{b})')
    return s


def box_svg(inner, box, cls=None):
    x, y, w, h = box
    c = f' class="{cls}"' if cls else ''
    return f'<svg{c} viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" width="{num(w)}" height="{num(h)}">{fix_ids(inner)}</svg>'


BUBBLE_AT = (196, 26)       # ふきだしの まん中（立ち上がった馬の 頭の右上）
SMOKE_AT = (RP((46, 6)), RP((58, 4)))
SPARKLE_AT = RP((46, -8))


def inline(alt=ALT):
    """(html, css)。html は <div class="bnr kdw">（判定画面の <img class="bnr"> と入れかえる）"""
    p = {}
    kids.banner(p)
    W, H = p['size']
    xe, ye, r = kids.YARN_BALL
    sc = Scene()
    sc.check()
    R, Hs = sc.R, sc.H
    hx, hy = page_xy(kids.HORSE_EYE, kids.HORSE_AT)
    eyes = [page_xy((ex, 39), kids.ROBOT_AT) for ex in kids.ROBOT_EYES]
    pupils = [page_xy((ex + 1, 40), kids.ROBOT_AT) for ex in kids.ROBOT_EYES]
    s = kids.ROBOT_AT[2]
    full = (0, 0, W, H)
    BALL_B = (xe - 18, ye - 18, 36, 36)
    HB = (xe - 22, ye - 22, 44, 54)           # 持つ・投げる毛糸玉（短い糸つき）の絵の箱
    HB_AT = (HELD[0] - 22, HELD[1] - 22)
    HH_AT = (HORSE_HELD[0] - 22, HORSE_HELD[1] - 22)
    THREAD_B = (254, 128, 90, 28)
    SHADOW_B = (78, 139, 100, 14)
    RSHADOW_B = (230, 140, 64, 12)
    EYE_B = (round(hx) - 8, round(hy) - 8, 16, 16)
    PUP_B = [(round(px) - 6, round(py) - 6, 13, 13) for px, py in pupils]
    held_ball = p['ball'] + p['tail']
    rob_g = lambda inner: f'<g transform="{kids.at(kids.ROBOT_AT)}">{inner}</g>'
    SM_B = (-14, -14, 28, 24)
    SP_B = (-15, -15, 30, 30)
    BU_B = (-46, -16, 92, 40)
    html = (f'<div class="bnr kdw" role="img" aria-label="{alt}">'
            + box_svg(f'<defs>{p["defs"]}</defs>{p["bg"]}', full, 'kdb')
            + '<i class="kdc"><i class="kdy"><i class="kdyy"><i class="kdr">' + box_svg(p['ball'], BALL_B) + '</i>'
            + box_svg(p['thread'], THREAD_B, 'kdt') + '</i></i>'
            + '<i class="kdT"><i class="kdTy"><i class="kdTr">' + box_svg(held_ball, HB) + '</i></i></i></i>'
            + '<i class="kdz"><i class="kdHw">' + box_svg(p['shadow_h'], SHADOW_B, 'kdhs')
            + '<i class="kdHf"><i class="kdh"><i class="kdl"><i class="kdHr">' + box_svg(p['horse'], full)
            + '<i class="kde">' + box_svg(p['eye'], EYE_B) + '</i>'
            + '<i class="kdHh">' + box_svg(held_ball, HB) + '</i></i></i></i></i></i></i>'
            + '<i class="kdq"><i class="kdR">' + box_svg(p['shadow_r'], RSHADOW_B, 'kdRs')
            + ''.join(f'<i class="kdRm kdRm{k + 1}">' + box_svg(smoke_svg(), SM_B) + '</i>' for k in range(2))
            + '<i class="kdRp">' + box_svg(sparkle_svg(), SP_B) + '</i>'
            + '<i class="kdRb"><i class="kdRn">' + box_svg(p['rob_antenna'], full) + '</i>'
            + '<i class="kdRa1">' + box_svg(p['rob_arm'][0], full) + '</i>'
            + '<i class="kdRa2"><i class="kdRh">' + box_svg(held_ball, HB) + '</i>' + box_svg(p['rob_arm'][1], full) + '</i>'
            + ''.join(f'<i class="kdRf{k + 1}">' + box_svg(p['rob_foot'][k], full) + '</i>' for k in range(2))
            + box_svg(p['rob_body'] + p['rob_head'], full)
            + ''.join(f'<i class="kdp kdp{k + 1}">' + box_svg(p['pupils'][k], PUP_B[k]) + '</i>' for k in range(2))
            + '<i class="kdRz">' + box_svg(rob_g(broken_eyes()), full) + '</i>'
            + '<i class="kdRk">' + box_svg(rob_g(SPARK), full) + '</i>'
            + '<i class="kdRw">' + box_svg(SWEAT, SWEAT_B) + '</i></i></i></i>'
            + ''.join(f'<i class="kdj kdj{k + 1}">' + box_svg(kids.stitched(kids.heart(0, 0, sz), col, 1.1, kids.heart(0, 0, sz * .7)), (-sz * 1.4, -sz * 1.4, sz * 2.8, sz * 2.8)) + '</i>'
                      for k, (t0, (cx, cy), sz, col) in enumerate(HEARTS))
            + '<i class="kdU">' + box_svg(bubble_svg(), BU_B) + '</i>'
            + box_svg(p['frame'], full, 'kdf')
            + '</div>')
    pos = lambda b: f'left:{num(b[0])}px;top:{num(b[1])}px;width:{num(b[2])}px;height:{num(b[3])}px'
    FULL = f'left:0;top:0;width:{W}px;height:{H}px'
    an = lambda *names: 'animation:' + ','.join(f'{n} {CYCLE:g}s linear infinite' for n in names)
    org = lambda o: f'transform-origin:{num(o[0])}px {num(o[1])}px'
    # 馬が高く跳ねると かげは 小さく（ロボットの かげは よこに動くだけ）
    hsh = Tr(None)
    hsh.k = [[t, round(1 - .32 * max(v[0], 0) / 18, 2), e] for t, v, e in Hs['hop'].k]
    hp = lambda v: f'transform:translateY({u(-v[0], "px")}) rotate({u(v[3], "deg")}) {sc2(v[1], v[2])}'
    sz_op = lambda v: f'transform:scale({num(v[0], 3)});opacity:{num(v[1], 3)}'
    smk = lambda v: f'transform:translateY({num(-v[0])}px) scale({num(v[1], 3)});opacity:{num(v[2], 3)}'
    css = ('.kdw{position:relative;overflow:hidden;isolation:isolate}'
           '.kdw svg,.kdw i{position:absolute;display:block;font-style:normal}'
           '.kdw i svg{left:0;top:0}'
           '.kdw .kdb,.kdw .kdf{left:0;top:0}'
           f'.kdw .kdc,.kdw .kdq,.kdw .kdz{{{FULL};overflow:hidden;clip-path:inset(6px round 12px)}}'
           f'.kdw .kdy{{{FULL};{an("kdRoll", "kdRollO")}}}'
           f'.kdw .kdyy{{{FULL};{an("kdBnc")}}}'
           f'.kdw .kdt{{{pos(THREAD_B)}}}'
           f'.kdw .kdr{{{pos(BALL_B)};transform-origin:18px 18px;{an("kdSpin")}}}'
           f'.kdw .kdT{{{pos((*HB_AT, 44, 54))};opacity:0;{an("kdTx", "kdTo")}}}'
           f'.kdw .kdTy{{left:0;top:0;width:44px;height:54px;{an("kdTy")}}}'
           f'.kdw .kdTr{{left:0;top:0;width:44px;height:54px;transform-origin:22px 22px;{an("kdTr")}}}'
           # 馬
           f'.kdw .kdHw{{{FULL};{an("kdHx", "kdHo")}}}'
           f'.kdw .kdhs{{{pos(SHADOW_B)};transform-origin:50px 7px;{an("kdHs")}}}'
           f'.kdw .kdHf{{{FULL};{org(FLIP_O)};{an("kdHf")}}}'
           f'.kdw .kdh{{{FULL};{org(HOP_O)};{an("kdHop")}}}'
           f'.kdw .kdl{{{FULL};{org(LEAN_O)};{an("kdLean")}}}'
           f'.kdw .kdHr{{{FULL};{org(REAR_O)};{an("kdHr")}}}'
           f'.kdw .kde{{{pos(EYE_B)};{an("kdEye")}}}'
           f'.kdw .kdHh{{{pos((*HH_AT, 44, 54))};opacity:0;{an("kdHh")}}}'
           # ロボット
           f'.kdw .kdR{{{FULL};{an("kdRx", "kdRo")}}}'
           f'.kdw .kdRs{{{pos(RSHADOW_B)}}}'
           f'.kdw .kdRb{{{FULL};{org(BOB_O)};{an("kdRb")}}}'
           f'.kdw .kdRn{{{FULL};{org(ANT_O)};{an("kdRn")}}}'
           + ''.join(f'.kdw .kdRa{k + 1}{{{FULL};{org(SHOULDER[k])};{an(f"kdRa{k + 1}")}}}' for k in range(2))
           + ''.join(f'.kdw .kdRf{k + 1}{{{FULL};{org(ANKLE[k])};{an(f"kdRf{k + 1}")}}}' for k in range(2))
           + f'.kdw .kdRh{{{pos((*HB_AT, 44, 54))};opacity:0;{an("kdRh")}}}'
           + ''.join(f'.kdw .kdp{k + 1}{{{pos(PUP_B[k])};{an(f"kdPup{k + 1}", "kdPo")}}}' for k in range(2))
           + f'.kdw .kdRz{{{FULL};opacity:0;{an("kdRz")}}}'
           + f'.kdw .kdRk{{{FULL};opacity:0;{an("kdRk")}}}'
           + ''.join(f'.kdw .kdRm{k + 1}{{left:{num(SMOKE_AT[k][0] - 14)}px;top:{num(SMOKE_AT[k][1] - 14)}px;width:28px;height:24px;'
                     f'transform-origin:14px 14px;opacity:0;{an(f"kdRm{k + 1}")}}}' for k in range(2))
           + f'.kdw .kdRp{{left:{num(SPARKLE_AT[0] - 15)}px;top:{num(SPARKLE_AT[1] - 15)}px;width:30px;height:30px;transform-origin:15px 15px;opacity:0;{an("kdRp")}}}'
           + f'.kdw .kdRw{{{pos(SWEAT_B)};opacity:0;transform-origin:6px 12px;{an("kdRw")}}}'
           + ''.join(f'.kdw .kdj{k + 1}{{left:{num(cx - sz * 1.4)}px;top:{num(cy - sz * 1.4)}px;width:{num(sz * 2.8)}px;height:{num(sz * 2.8)}px;opacity:0;{an(f"kdJoy{k + 1}")}}}'
                     for k, (t0, (cx, cy), sz, col) in enumerate(HEARTS))
           + f'.kdw .kdU{{left:{BUBBLE_AT[0] - 46}px;top:{BUBBLE_AT[1] - 16}px;width:92px;height:40px;transform-origin:18px 36px;opacity:0;{an("kdU")}}}'
           # 地面の毛糸玉（左右と 回る は 同じ秒・同じ動き＝ 進んだぶんだけ回る）・投げた毛糸玉
           + kf('kdRoll', sc.gx, lambda v: f'transform:translateX({num(v)}px)')
           + kf('kdRollO', sc.gop, lambda v: f'opacity:{num(v, 3)}')
           + kf('kdBnc', sc.gy, lambda v: f'transform:translateY({num(v)}px)')
           + kf('kdSpin', sc.gx, lambda v: f'transform:rotate({num(math.degrees(v / r), 1)}deg)')
           + kf('kdTx', sc.tx, lambda v: f'transform:translateX({num(v)}px)')
           + kf('kdTo', sc.top, lambda v: f'opacity:{num(v, 3)}')
           + kf('kdTy', sc.ty, lambda v: f'transform:translateY({num(v)}px)')
           + kf('kdTr', sc.tr, lambda v: f'transform:rotate({num(v, 1)}deg)')
           # 馬
           + kf('kdHx', Hs['dx'], lambda v: f'transform:translateX({num(v)}px)')
           + kf('kdHo', Hs['op'], lambda v: f'opacity:{num(v, 3)}')
           + kf('kdHs', hsh, lambda v: f'transform:scale({num(v)})')
           + kf('kdHf', Hs['flip'], lambda v: f'transform:scaleX({num(v, 3)})')
           + kf('kdHop', Hs['hop'], hp)
           + kf('kdLean', Hs['lean'], lambda v: f'transform:rotate({num(v)}deg)')
           + kf('kdHr', Hs['rear'], lambda v: f'transform:rotate({num(v)}deg)')
           + kf('kdHh', Hs['held'], lambda v: f'opacity:{num(v, 3)}')
           + kf('kdU', Hs['bubble'], sz_op)
           + kf_translate('kdEye', [(t, (x * kids.HORSE_AT[2], y * kids.HORSE_AT[2]), e) for t, (x, y), e in sample(sc.horse_eye)])
           # ロボット
           + kf('kdRx', R['dx'], lambda v: f'transform:translateX({u(v, "px")})')
           + kf('kdRo', R['op'], lambda v: f'opacity:{num(v, 3)}')
           + kf('kdRb', R['bob'], hp)
           + kf('kdRn', R['ant'], lambda v: f'transform:rotate({num(v)}deg)')
           + ''.join(kf(f'kdRa{k + 1}', R['arm'][k], lambda v: f'transform:rotate({u(v, "deg")})') for k in range(2))
           + ''.join(kf(f'kdRf{k + 1}', R['foot'][k], lambda v: f'transform:translate({u(v[0], "px")},{u(v[1], "px")}) rotate({u(v[2], "deg")})') for k in range(2))
           + kf('kdRh', R['held'], lambda v: f'opacity:{num(v, 3)}')
           + kf('kdRz', R['broken'], lambda v: f'opacity:{num(v, 3)}')
           + kf('kdPo', R['broken'], lambda v: f'opacity:{num(1 - v, 3)}')
           + kf('kdRk', R['spark'], lambda v: f'opacity:{num(v, 3)}')
           + ''.join(kf(f'kdRm{k + 1}', R['smoke'][k], smk) for k in range(2))
           + kf('kdRp', R['sparkle'], sz_op)
           + kf('kdRw', R['sweat'], lambda v: f'transform:translateY({num(v[0])}px) scale({num(v[1], 3)});opacity:{num(v[2], 3)}')
           + ''.join(kf_translate(f'kdPup{k + 1}', [(t, ((x - 1) * s, (y - 1) * s), e)
                                                     for t, (x, y), e in sample(lambda t, k=k: look(sc.robot_eye(eyes[k], t), sc.robot_look(t), EYE_R))])
                     for k in range(2))
           + ''.join(kf(f'kdJoy{k + 1}', tr, lambda v: f'transform:translateY({num(v[0])}px) rotate({num(v[2])}deg) scale({num(v[1], 3)});opacity:{num(v[3])}')
                     for k, tr in enumerate(heart_tracks()))
           + '@media (prefers-reduced-motion:reduce){.kdw *{animation:none!important}}')
    return html, css


def judge_inline(fn, alt=ALT):
    """判定画面（Judge_Kids.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="bnr kdw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(alt)
    page, k = re.subn(r'<div class="bnr kdw" .*?</div>(?=\s*<main)|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = (f'/* 子供向けの壁紙：毛糸玉が転がって、ロボットと馬が目で追い、止まると馬が跳ねて喜ぶ → ロボットが拾いに行って うっかり蹴り、'
             f'いっしょに右へ → 持って戻って 左へポーン。ときどき ロボットが故障して 馬が「ヒヒーン」（kids_wall.py） */\n{css}\n/* /子供向けの壁紙 */\n')
    if '/* 子供向けの壁紙：' in page:
        page = re.sub(r'/\* 子供向けの壁紙：.*?/\* /子供向けの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def plan():
    sc = Scene()
    sc.check()
    name = dict(N='いつもの', A='故障 → 復活', B='故障 → 治らない（馬が取りにいく）')
    for i, (S, kind, prev) in enumerate(RUNS):
        print(f'{i + 1:2d}回目 {S:7.2f}秒〜（{round_len(kind):.2f}秒）{name[kind]}')
    print(f'1回り {CYCLE}秒')


if __name__ == '__main__':
    if '--plan' in sys.argv:
        plan()
    else:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1])
