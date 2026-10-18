"""子供向けの壁紙の動き（まさちゃんの指定）：ページに入れる HTML と CSS
   「1秒〜3秒で、毛糸が左から右にころがっていき、ロボットは目で追って、馬も目で追って4秒で毛糸が止まり、馬が跳ねて喜ぶ。8秒に一回リピートする」
   「毛糸が転がって消えるんじゃなくて、ロボットが毛糸拾いに行って、間違えて蹴っちゃって毛糸と一緒に画面からフェードアウトして！
    1秒後にロボットだけ持って戻ってきて！その後2秒にリピートして！」（持って戻った毛糸玉は「左へポーンと投げる」）
   - 絵は kids.py の部品（いつもの絵と同じ形・同じ場所）を べつべつの <svg> にして重ね、動く所だけを CSS で動かす。下から：
     下の絵（毛糸の編み目・布・雲・星）→ 毛糸玉と糸・投げた毛糸玉（枠の内がわだけ見える）→ 馬のかげ → 馬（目なし）とボタンの目 →
     ロボット（枠の内がわだけ見える：かげ → アンテナ → 左の腕 → 右の腕（手に持った毛糸玉）→ 足 → 体と頭 → 黒目 → あせ）→ ハート → 枠
     （毛糸玉は 馬とロボットの うしろを通る＝いつもの絵と同じ重なり。どの部品も絵ごと動かすので、フェルトの もようは いっしょに動く）
   - 12秒で1回り（CYCLE）：
     0秒 ロボットが 手に持った毛糸玉を 左へポーン（ロボットの頭と 馬の うしろの上を越えて 左の外へ）→
     1〜3秒 毛糸玉が 左から ころころ転がってくる（すべらない：進んだぶんだけ回る）→ 3〜4秒 だんだん ゆっくりになって 4秒で いつもの場所に止まる
     （ロボットの黒目と 馬のボタンの目は 毛糸玉を追う。馬は 毛糸玉が頭の下を通る時に 少し前へ のぞきこむ）→
     4秒 馬が ぴょん・ぴょんと2回跳ねて喜ぶ（ハートが3つ）→
     5.6〜6.5秒 ロボットが 毛糸玉を拾いに 右へ とことこ3歩 → 6.62秒 右足が当たって うっかり蹴っちゃう（毛糸玉が 右へ ころん）→
     びっくり（あせ・ぴょん）→ 6.92〜7.6秒 あわてて追いかけて、毛糸玉といっしょに 右へ フェードアウト →
     1秒後の 8.6秒 ロボットだけ 毛糸玉を 手に持って 右から戻ってくる → 10秒 もとの場所（馬に見せる）→ 2秒後の 12秒＝0秒 左へポーン → くり返す
     （手に持った毛糸玉と 投げた毛糸玉は べつの絵。はなす瞬間（0秒）は ロボットが いつもの形なので、同じ場所・同じ向きで 入れかわる）
   - 視差効果を減らす（prefers-reduced-motion）なら動かさない（部品が いつもの場所にあるので、いつもの絵と同じ）
   クラスの名前は kd…
   python3 kids_wall.py --judge <Judge_Kids.dc.html>   → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 kids_wall.py --plan                          → 何秒に どこにいるか（毛糸玉・ロボット・目）"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kids

ALT = ('毛糸の編み目の背景に、ぬいぐるみの馬と手をふるロボット、毛糸玉のイラスト（毛糸玉が左から ころころ転がってきて、ロボットと馬が目で追い、'
       '止まると馬が跳ねて喜ぶ。ロボットが拾いに行って うっかり蹴ってしまい、毛糸玉といっしょに画面の外へ。毛糸玉を持って戻ってきて、左へポーンと投げる）')
CYCLE = 12.0
ROLL = (1.0, 3.0, 4.0)        # 転がりはじめ・ゆっくりになりはじめ・止まる（秒）
X0 = -12.0                    # 転がりはじめの 毛糸玉のまん中（枠の左の外）
SLOW = .2                     # 3〜4秒で進む道のりの わりあい（なめらかに ゆっくりになる：速さがそろう＝ 1秒あたりの道のりの半分）
EYE_H = 2.4                   # 馬のボタンの目が動く大きさ（馬の座標）・うしろ向きは小さく（EYE_H_BACK）
EYE_H_BACK = 1.2
EYE_R = 2.6                   # ロボットの黒目が 目のまん中から動く大きさ（ロボットの座標・白目の内がわに入る）
HOP_O = (121, 145.5)          # 馬が跳ねる時の 中心（足もと）
# 跳ねて喜ぶ：(秒, 上へ, よこ・たての のび, かたむき, 次までの動き)
HOP = [(4.00, 0, 1, 1, 0, 'quad-out'), (4.12, 0, 1.06, .9, 0, 'quad-out'), (4.40, 18, 1, 1, -4, 'quad-in'),
       (4.66, 0, .98, 1.03, 1, 'quad-out'), (4.74, 0, 1.06, .91, 0, 'quad-out'), (4.96, 10, 1, 1, -2, 'quad-in'),
       (5.16, 0, .99, 1.02, .5, 'quad-out'), (5.24, 0, 1.04, .94, 0, 'ease-in-out'), (5.40, 0, 1, 1, 0, 'linear')]
# 毛糸玉が 頭の下を通る時に 少し前へ のぞきこむ（前足のところを中心に かたむく）：(秒, かたむき, 次までの動き)
LEAN_O = (139, 145)
LEAN = [(0, 0, 'linear'), (1.65, 0, 'ease-in-out'), (2.05, 2.5, 'linear'), (2.35, 2.5, 'ease-in-out'), (2.8, 0, 'linear'), (CYCLE, 0, 'linear')]
# ハート：(出る秒, まん中, 大きさ, 色)
HEARTS = [(4.30, (184, 38), 6.4, '#F7A8C0'), (4.42, (204, 30), 5.4, '#FFB7C5'), (4.90, (168, 30), 5.6, '#F7A8C0')]
# ロボット（秒・ずれは絵の px）
WALK = (5.6, 6.5, 50.0)       # 拾いに行く：右へ 3歩（50px）
KICK = (6.5, 6.62, 6.76)      # 右足を出す → 毛糸玉に当たる（うっかり蹴る）→ もどす
CHASE = (6.92, 7.6, 112.0)    # あわてて追いかける：右へ 3歩（112pxまで）
FADE_OUT = (7.05, 7.6)        # 毛糸玉といっしょに フェードアウト
HELD_ON = 8.0                 # 見えない間に 手に毛糸玉を持つ
BACK = (8.6, 10.0)            # 1秒後に 右から戻る（4歩）→ もとの場所
FADE_IN = (8.6, 8.9)
SHOW = (10.45, 11.05)         # 持ってきた毛糸玉を 馬に見せる（ふる・ぴょん）
WIND = (11.5, 11.8)           # 投げる前に ためる → 12秒（＝0秒）で はなす
HELD = (302, 48)              # 手に持った毛糸玉のまん中（いつもの 右手の上）
THROW = (0.66, (196, 21), -24.0)   # 投げた毛糸玉：左の外に出るまでの秒・いちばん高い所・出た所の x（放物線）
THROW_SPIN = -560.0
BALL_OUT = 48.0               # 蹴られた毛糸玉が 右へ ころがる道のり（6.62〜7.6秒）
BALL_FADE = (6.95, 7.5)
LOOK_HORSE = (150, 64)        # 持ってきた毛糸玉を 見せる時に ロボットが見る所（馬の顔）
OFF_R = (440, 120)            # 右の外（ロボットと毛糸玉が 出ていった所）
OFF_L = (-20, 128)            # 左の外（投げた毛糸玉が 落ちた所）
N_BOB = (0.0, 1.0, 1.0, 0.0)  # ロボットの体：(上へ, よこ・たての のび, かたむき)
EASE = {'linear': 'linear', 'quad-out': 'cubic-bezier(.3333,.6667,.6667,1)', 'quad-in': 'cubic-bezier(.3333,0,.6667,.3333)', 'ease-in-out': 'ease-in-out',
        'ease-in': 'ease-in', 'ease-out': 'ease-out'}
BEZ = {'quad-out': (1 / 3, 2 / 3, 2 / 3, 1), 'quad-in': (1 / 3, 0, 2 / 3, 1 / 3), 'ease-in-out': (.42, 0, .58, 1), 'ease-in': (.42, 0, 1, 1), 'ease-out': (0, 0, .58, 1)}
IDS = (('knit', 'kdKnit'), ('felt', 'kdFelt'))
SWEAT = ('<path d="M227 44.6 C 228.3 47.4, 230.8 49.8, 230.8 52.2 A 3.8 3.8 0 0 1 223.2 52.2 C 223.2 49.8, 225.7 47.4, 227 44.6 Z" '
         f'fill="#BFE8FB" stroke="{kids.BR}" stroke-width="1.1" stroke-linejoin="round"/><ellipse cx="225.6" cy="52" rx=".9" ry="1.4" fill="#FFFFFF"/>')
SWEAT_B = (221, 43, 12, 15)


def pct(t):
    s = f'{t / CYCLE * 100:.4f}'.rstrip('0').rstrip('.')
    return s + '%'


def num(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


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
        for (t0, v0, e), (t1, v1, _) in zip(k, k[1:]):
            if t0 <= t <= t1:
                return mix(v0, v1, ease(e, (t - t0) / (t1 - t0)) if t1 > t0 else 1)
        return k[-1][1]


def page_xy(p, at):
    x, y, s = at
    return x + p[0] * s, y + p[1] * s


RP = lambda p: page_xy(p, kids.ROBOT_AT)
SHOULDER = (RP((24, 72)), RP((68, 70)))       # 腕を回す所（左・右）
ANKLE = (RP((38, 106)), RP((56, 106)))        # 足を回す所（左・右）
BOB_O = RP((47, 118.6))                       # 体が はねる・かたむく 中心（足もとの まん中）


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


def robot_tracks():
    """ロボットの動き（12秒）"""
    T = dict(dx=Tr(0.0), op=Tr(1.0), bob=Tr(N_BOB), foot=[Tr((0.0, 0.0, 0.0)), Tr((0.0, 0.0, 0.0))], arm=[Tr(0.0), Tr(0.0)],
             held=Tr(0.0), sweat=Tr((0.0, .3, 0.0)))
    bob, arm, foot = T['bob'], T['arm'], T['foot']
    # 0秒 毛糸玉を はなした あと（のびて 左へ ふりぬく → もどる）
    bob.go(.12, (3.0, .95, 1.07, -5.0), 'quad-out').go(.3, (0.0, 1.04, .95, -2.0), 'quad-in').go(.55, N_BOB, 'ease-out')
    arm[1].go(.12, -22.0, 'quad-out').go(.3, -8.0, 'ease-in-out').go(.55, 0.0, 'ease-out')
    arm[0].go(.12, 10.0, 'quad-out').go(.55, 0.0, 'ease-in-out')
    # 拾いに行く（右へ 3歩）
    walk(T, WALK[0], WALK[1], 0.0, WALK[2], 3, lead=0, h=2.6, lean=2.0, sw=(10, 6))
    # 右足が 毛糸玉に当たる（うっかり蹴る）
    k0, k1, k2 = KICK
    foot[1].hold(k0).go(k1, (9.0, -4.0, -22.0), 'quad-out').go(k2, (0.0, 0.0, 0.0), 'ease-in-out')
    bob.hold(k0).go(k1, (0.0, 1.0, 1.0, -3.0), 'ease-out')
    # びっくり（ぴょん・あせ・腕が はねる）
    bob.go(6.72, (4.0, .95, 1.07, 0.0), 'quad-out').go(6.8, (0.0, 1.05, .94, 0.0), 'quad-in').go(CHASE[0], (0.0, 1.0, 1.0, 3.0), 'ease-out')
    arm[0].hold(k1).go(6.72, 28.0, 'quad-out').go(CHASE[0], 8.0, 'ease-in-out')
    arm[1].hold(k1).go(6.72, 12.0, 'quad-out').go(CHASE[0], 0.0, 'ease-in-out')
    T['sweat'].set(6.66, (0.0, .3, 1.0)).go(6.74, (0.0, 1.15, 1.0), 'quad-out').go(6.8, (0.0, 1.0, 1.0), 'ease-in-out').go(7.45, (3.0, 1.0, 1.0), 'ease-in')
    # あわてて追いかけて、毛糸玉といっしょに フェードアウト
    walk(T, CHASE[0], CHASE[1], WALK[2], CHASE[2], 3, lead=1, h=3.4, lean=7.0, sw=(22, 14), lift=3.6, fwd=4.0)
    T['op'].hold(FADE_OUT[0]).go(FADE_OUT[1], 0.0, 'ease-in')
    T['sweat'].set(FADE_OUT[1], (0.0, .3, 0.0))
    # 見えない間に 手に毛糸玉を持つ → 1秒後に 右から戻る（左へ 4歩）
    T['held'].set(HELD_ON, 1.0)
    T['op'].hold(FADE_IN[0]).go(FADE_IN[1], 1.0, 'ease-out')
    walk(T, BACK[0], BACK[1], CHASE[2], 0.0, 4, lead=0, h=2.6, lean=3.0, sw=(12, 3))
    # 着いた（ちぢむ）→ 馬に見せる（毛糸玉を ふる・ぴょん）
    b0 = BACK[1]
    bob.hold(b0).go(b0 + .1, (0.0, 1.05, .93, 0.0), 'quad-out').go(b0 + .28, N_BOB, 'ease-out')
    s0, s1 = SHOW
    arm[1].hold(s0).go(s0 + .15, -8.0, 'ease-in-out').go(s0 + .3, 5.0, 'ease-in-out').go(s0 + .45, -4.0, 'ease-in-out').go(s1, 0.0, 'ease-in-out')
    bob.hold(s0).go(s0 + .13, (2.5, .97, 1.04, 0.0), 'quad-out').go(s0 + .25, (0.0, 1.03, .96, 0.0), 'quad-in').go(s0 + .37, N_BOB, 'ease-out')
    # ためて（ちぢんで 腕を うしろへ）→ 12秒（＝0秒）で いつもの形を通る所で はなす
    w0, w1 = WIND
    bob.hold(w0).go(w1, (0.0, 1.06, .9, 4.0), 'ease-in-out').go(CYCLE, N_BOB, 'quad-in')
    arm[1].hold(w0).go(w1, 24.0, 'ease-in-out').go(CYCLE, 0.0, 'quad-in')
    arm[0].hold(w0).go(w1, -8.0, 'ease-in-out').go(CYCLE, 0.0, 'quad-in')
    for tr in (T['dx'], T['op'], T['held'], T['sweat'], bob, *foot, *arm):
        tr.end()
    return T


def ground_tracks():
    """地面の毛糸玉（糸つき）：左から転がる → 止まる → 蹴られて 右へ ころん・フェードアウト"""
    xe = kids.YARN_BALL[0]
    t0, t1, t2 = ROLL
    x1 = X0 + (1 - SLOW) * (xe - X0)
    gx = Tr(X0 - xe).hold(t0).go(t1, x1 - xe, 'linear').go(t2, 0.0, 'quad-out').hold(KICK[1]).go(CHASE[1], BALL_OUT, 'quad-out').end()
    gop = Tr(1.0).hold(BALL_FADE[0]).go(BALL_FADE[1], 0.0, 'ease-in').end()
    k = KICK[1]
    gy = Tr(0.0).hold(k).go(k + .1, -6.0, 'quad-out').go(k + .22, 0.0, 'quad-in').go(k + .29, -2.0, 'quad-out').go(k + .36, 0.0, 'quad-in').end()
    return gx, gop, gy


def throw_tracks():
    """投げた毛糸玉（短い糸つき）：はなした所 → いちばん高い所 → 左の外（よこは同じ速さ・たては 放物線＝前半 quad-out・後半 quad-in）"""
    te, (ax, ay), x_end = THROW
    hx, hy = HELD
    vx = (x_end - hx) / te
    ta = (ax - hx) / vx
    g = 2 * (hy - ay) / ta ** 2
    y_end = ay + .5 * g * (te - ta) ** 2
    tx = Tr(0.0).go(te, x_end - hx, 'linear').end()
    top = Tr(1.0).set(te, 0.0).end()
    ty = Tr(0.0).go(ta, ay - hy, 'quad-out').go(te, y_end - hy, 'quad-in').end()
    tr = Tr(0.0).go(te, THROW_SPIN, 'linear').end()
    return tx, top, ty, tr


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


class Scene:
    """動きを まとめて持ち、何秒に どこにいるかを出す（目の向き・たしかめ）"""
    def __init__(self):
        self.R = robot_tracks()
        self.gx, self.gop, self.gy = ground_tracks()
        self.tx, self.top, self.ty, self.tr = throw_tracks()

    def held(self, t):
        R = self.R
        q = rot_map(HELD, SHOULDER[1], R['arm'][1].at(t))
        x, y = bob_map(q, R['bob'].at(t))
        return x + R['dx'].at(t), y

    def thrown(self, t):
        return HELD[0] + self.tx.at(t), HELD[1] + self.ty.at(t)

    def ground(self, t):
        xe, ye, _ = kids.YARN_BALL
        return xe + self.gx.at(t), ye + self.gy.at(t)

    def ball(self, t):
        """見えている毛糸玉（馬は いつも これを見る）"""
        if t < THROW[0]:
            return self.thrown(t)
        if t < ROLL[0]:
            return OFF_L
        if t < BALL_FADE[1]:
            return self.ground(t)
        if t < BACK[0]:
            return OFF_R
        return self.held(t)

    def robot_look(self, t):
        """ロボットが見る所：戻ってくる時と 見せる時は 馬の顔、それ以外は 毛糸玉"""
        if BACK[0] <= t < WIND[0]:
            return LOOK_HORSE
        return self.ball(t)

    def robot_eye(self, eye, t):
        x, y = bob_map(eye, self.R['bob'].at(t))
        return x + self.R['dx'].at(t), y

    def check(self):
        R = self.R
        for t in (0.0, CYCLE):
            assert R['dx'].at(t) == 0 and R['bob'].at(t) == N_BOB and R['arm'][1].at(t) == 0, t
            assert all(abs(a - b) < 1e-9 for a, b in zip(self.held(t), HELD)), t
        assert self.thrown(0) == HELD and self.top.at(0) == 1 and R['held'].at(CYCLE) == 1 and R['held'].at(0) == 0
        assert R['op'].at(HELD_ON) == 0 and R['op'].at(BACK[0]) == 0, 'held ball must appear while the robot is hidden'
        assert self.gop.at(CYCLE) == 0, 'ground ball must be hidden before it jumps back to the left'
        assert R['dx'].at(FADE_OUT[1]) == R['dx'].at(BACK[0]) == CHASE[2]
        # 投げた毛糸玉は 消える時に 枠の外（左の外・短い糸も）
        x, y = self.thrown(THROW[0])
        assert x + 16 < 6 and x + 30 < 6 + 40, (x, y)
        # けった時 足が 毛糸玉に とどく（右足の くつの右はし ≒ 毛糸玉の左はし）
        shoe_r = RP((56 + 9, 114))[0] + R['dx'].at(KICK[1]) + R['foot'][1].at(KICK[1])[0]
        assert abs(shoe_r - (kids.YARN_BALL[0] - 14)) < 4, shoe_r


def look(eye, target, r, back=None):
    """目のまん中 eye から target を見る向き × r"""
    dx, dy = target[0] - eye[0], target[1] - eye[1]
    n = math.hypot(dx, dy) or 1
    ox, oy = dx / n * r, dy / n * r
    if back is not None:
        ox = max(ox, -back)
    return ox, oy


def sample(fn):
    """0.1秒ごとの 値（同じ値が つづく所は 両はしだけ）→ [(秒, (x, y), 'linear')]"""
    ts = [round(i * .1, 6) for i in range(int(round(CYCLE * 10)) + 1)]
    vals = [tuple(round(v, 2) for v in fn(t)) for t in ts]
    ks = []
    for i, (t, v) in enumerate(zip(ts, vals)):
        if 0 < i < len(ts) - 1 and vals[i - 1] == v == vals[i + 1]:
            continue
        ks.append((t, v, 'linear'))
    return ks


def kf_translate(name, ks):
    out = []
    for t, (x, y), e in ks:
        out.append(f'{pct(t)}{{transform:translate({num(x)}px,{num(y)}px);animation-timing-function:{EASE.get(e, e)}}}')
    return f'@keyframes {name}{{' + ''.join(out) + '}'


def kf(name, tr, fmt):
    return f'@keyframes {name}{{' + ''.join(f'{pct(t)}{{{fmt(v)};animation-timing-function:{EASE[e]}}}' for t, v, e in tr.k) + '}'


def hop_css():
    """馬が跳ねる（.kdh）と かげ（.kdhs）・のぞきこむ（.kdl）"""
    hmax = max(h for _, h, *_ in HOP)
    ho, sh = [f'0%{{transform:none;animation-timing-function:linear}}'], [f'0%{{transform:none;opacity:1;animation-timing-function:linear}}']
    for t, h, sx, sy, rot, e in HOP:
        ho.append(f'{pct(t)}{{transform:translateY({num(-h)}px) rotate({num(rot)}deg) scale({num(sx, 3)},{num(sy, 3)});animation-timing-function:{EASE[e]}}}')
        k = h / hmax
        sh.append(f'{pct(t)}{{transform:scale({num(1 - .32 * k, 3)});opacity:{num(1 - .5 * k, 3)};animation-timing-function:{EASE[e]}}}')
    ho.append('100%{transform:none}')
    sh.append('100%{transform:none;opacity:1}')
    le = ''.join(f'{pct(t)}{{transform:rotate({num(a)}deg);animation-timing-function:{EASE[e]}}}' for t, a, e in LEAN)
    return '@keyframes kdHop{' + ''.join(ho) + '}@keyframes kdHs{' + ''.join(sh) + '}@keyframes kdLean{' + le + '}'


def heart_css(k, t0):
    ks = [(0, 0, .3, -10, 0, 'linear'), (t0, 0, .3, -10, 0, 'quad-out'), (t0 + .14, -3, 1.15, -6, 1, 'ease-in-out'),
          (t0 + .26, -5, 1, -2, 1, 'linear'), (t0 + .85, -12, 1, 8, 1, 'ease-in'), (t0 + 1.15, -16, .9, 10, 0, 'linear'), (CYCLE, -16, .9, 10, 0, 'linear')]
    out = ''.join(f'{pct(t)}{{transform:translateY({num(y)}px) rotate({num(r)}deg) scale({num(s, 3)});opacity:{num(o)};animation-timing-function:{EASE[e]}}}'
                  for t, y, s, r, o, e in ks)
    return f'@keyframes kdJoy{k}{{{out}}}'


def fix_ids(s):
    for a, b in IDS:
        s = s.replace(f'id="{a}"', f'id="{b}"').replace(f'url(#{a})', f'url(#{b})')
    return s


def box_svg(inner, box, cls=None):
    x, y, w, h = box
    c = f' class="{cls}"' if cls else ''
    return f'<svg{c} viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" width="{num(w)}" height="{num(h)}">{fix_ids(inner)}</svg>'


def inline(alt=ALT):
    """(html, css)。html は <div class="bnr kdw">（判定画面の <img class="bnr"> と入れかえる）"""
    p = {}
    kids.banner(p)
    W, H = p['size']
    xe, ye, r = kids.YARN_BALL
    sc = Scene()
    sc.check()
    R = sc.R
    hx, hy = page_xy(kids.HORSE_EYE, kids.HORSE_AT)
    eyes = [page_xy((ex, 39), kids.ROBOT_AT) for ex in kids.ROBOT_EYES]
    pupils = [page_xy((ex + 1, 40), kids.ROBOT_AT) for ex in kids.ROBOT_EYES]
    s = kids.ROBOT_AT[2]
    full = (0, 0, W, H)
    BALL_B = (xe - 18, ye - 18, 36, 36)
    HB = (xe - 22, ye - 22, 44, 54)           # 持つ・投げる毛糸玉（短い糸つき）の絵の箱
    HB_AT = (HELD[0] - 22, HELD[1] - 22)
    THREAD_B = (254, 128, 90, 28)
    SHADOW_B = (78, 139, 100, 14)
    RSHADOW_B = (230, 140, 64, 12)
    EYE_B = (round(hx) - 8, round(hy) - 8, 16, 16)
    PUP_B = [(round(px) - 6, round(py) - 6, 13, 13) for px, py in pupils]
    held_ball = p['ball'] + p['tail']
    html = (f'<div class="bnr kdw" role="img" aria-label="{alt}">'
            + box_svg(f'<defs>{p["defs"]}</defs>{p["bg"]}', full, 'kdb')
            + '<i class="kdc"><i class="kdy"><i class="kdyy"><i class="kdr">' + box_svg(p['ball'], BALL_B) + '</i>'
            + box_svg(p['thread'], THREAD_B, 'kdt') + '</i></i>'
            + '<i class="kdT"><i class="kdTy"><i class="kdTr">' + box_svg(held_ball, HB) + '</i></i></i></i>'
            + box_svg(p['shadow_h'], SHADOW_B, 'kdhs')
            + '<i class="kdh"><i class="kdl">' + box_svg(p['horse'], full) + '<i class="kde">' + box_svg(p['eye'], EYE_B) + '</i></i></i>'
            + '<i class="kdq"><i class="kdR">' + box_svg(p['shadow_r'], RSHADOW_B, 'kdRs')
            + '<i class="kdRb">' + box_svg(p['rob_antenna'], full)
            + '<i class="kdRa1">' + box_svg(p['rob_arm'][0], full) + '</i>'
            + '<i class="kdRa2"><i class="kdRh">' + box_svg(held_ball, HB) + '</i>' + box_svg(p['rob_arm'][1], full) + '</i>'
            + ''.join(f'<i class="kdRf{k + 1}">' + box_svg(p['rob_foot'][k], full) + '</i>' for k in range(2))
            + box_svg(p['rob_body'] + p['rob_head'], full)
            + ''.join(f'<i class="kdp kdp{k + 1}">' + box_svg(p['pupils'][k], PUP_B[k]) + '</i>' for k in range(2))
            + '<i class="kdRw">' + box_svg(SWEAT, SWEAT_B) + '</i></i></i></i>'
            + ''.join(f'<i class="kdj kdj{k + 1}">' + box_svg(kids.stitched(kids.heart(0, 0, sz), col, 1.1, kids.heart(0, 0, sz * .7)), (-sz * 1.4, -sz * 1.4, sz * 2.8, sz * 2.8)) + '</i>'
                      for k, (t0, (cx, cy), sz, col) in enumerate(HEARTS))
            + box_svg(p['frame'], full, 'kdf')
            + '</div>')
    pos = lambda b: f'left:{num(b[0])}px;top:{num(b[1])}px;width:{num(b[2])}px;height:{num(b[3])}px'
    FULL = f'left:0;top:0;width:{W}px;height:{H}px'
    an = lambda *names: 'animation:' + ','.join(f'{n} {CYCLE:g}s linear infinite' for n in names)
    org = lambda o: f'transform-origin:{num(o[0])}px {num(o[1])}px'
    # 体が上がると かげは 小さく・うすく
    shadow = Tr(None)
    shadow.k = [[t, (1 - .3 * v[0] / 6, 1 - .45 * v[0] / 6), e] for t, v, e in R['bob'].k]
    css = ('.kdw{position:relative;overflow:hidden;isolation:isolate}'
           '.kdw svg,.kdw i{position:absolute;display:block;font-style:normal}'
           '.kdw i svg{left:0;top:0}'
           '.kdw .kdb,.kdw .kdf{left:0;top:0}'
           f'.kdw .kdc,.kdw .kdq{{{FULL};overflow:hidden;clip-path:inset(6px round 12px)}}'
           f'.kdw .kdy{{{FULL};{an("kdRoll", "kdRollO")}}}'
           f'.kdw .kdyy{{{FULL};{an("kdBnc")}}}'
           f'.kdw .kdt{{{pos(THREAD_B)}}}'
           f'.kdw .kdr{{{pos(BALL_B)};transform-origin:18px 18px;{an("kdSpin")}}}'
           f'.kdw .kdT{{{pos((*HB_AT, 44, 54))};opacity:0;{an("kdTx", "kdTo")}}}'
           f'.kdw .kdTy{{left:0;top:0;width:44px;height:54px;{an("kdTy")}}}'
           f'.kdw .kdTr{{left:0;top:0;width:44px;height:54px;transform-origin:22px 22px;{an("kdTr")}}}'
           f'.kdw .kdhs{{{pos(SHADOW_B)};transform-origin:50px 7px;{an("kdHs")}}}'
           f'.kdw .kdh{{{FULL};{org(HOP_O)};{an("kdHop")}}}'
           f'.kdw .kdl{{{FULL};{org(LEAN_O)};{an("kdLean")}}}'
           f'.kdw .kde{{{pos(EYE_B)};{an("kdEye")}}}'
           f'.kdw .kdR{{{FULL};{an("kdRx", "kdRo")}}}'
           f'.kdw .kdRs{{{pos(RSHADOW_B)};transform-origin:32px 6px;{an("kdRs")}}}'
           f'.kdw .kdRb{{{FULL};{org(BOB_O)};{an("kdRb")}}}'
           + ''.join(f'.kdw .kdRa{k + 1}{{{FULL};{org(SHOULDER[k])};{an(f"kdRa{k + 1}")}}}' for k in range(2))
           + ''.join(f'.kdw .kdRf{k + 1}{{{FULL};{org(ANKLE[k])};{an(f"kdRf{k + 1}")}}}' for k in range(2))
           + f'.kdw .kdRh{{{pos((*HB_AT, 44, 54))};opacity:0;{an("kdRh")}}}'
           + ''.join(f'.kdw .kdp{k + 1}{{{pos(PUP_B[k])};{an(f"kdPup{k + 1}")}}}' for k in range(2))
           + f'.kdw .kdRw{{{pos(SWEAT_B)};opacity:0;transform-origin:6px 12px;{an("kdRw")}}}'
           + ''.join(f'.kdw .kdj{k + 1}{{left:{num(cx - sz * 1.4)}px;top:{num(cy - sz * 1.4)}px;width:{num(sz * 2.8)}px;height:{num(sz * 2.8)}px;opacity:0;{an(f"kdJoy{k + 1}")}}}'
                     for k, (t0, (cx, cy), sz, col) in enumerate(HEARTS))
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
           + hop_css()
           + kf_translate('kdEye', [(t, (x * kids.HORSE_AT[2], y * kids.HORSE_AT[2]), e)
                                    for t, (x, y), e in sample(lambda t: look((hx, hy), sc.ball(t), EYE_H, EYE_H_BACK))])
           # ロボット
           + kf('kdRx', R['dx'], lambda v: f'transform:translateX({num(v)}px)')
           + kf('kdRo', R['op'], lambda v: f'opacity:{num(v, 3)}')
           + kf('kdRs', shadow, lambda v: f'transform:scale({num(v[0], 3)});opacity:{num(v[1], 3)}')
           + kf('kdRb', R['bob'], lambda v: f'transform:translateY({num(-v[0])}px) rotate({num(v[3])}deg) scale({num(v[1], 3)},{num(v[2], 3)})')
           + ''.join(kf(f'kdRa{k + 1}', R['arm'][k], lambda v: f'transform:rotate({num(v)}deg)') for k in range(2))
           + ''.join(kf(f'kdRf{k + 1}', R['foot'][k], lambda v: f'transform:translate({num(v[0])}px,{num(v[1])}px) rotate({num(v[2])}deg)') for k in range(2))
           + kf('kdRh', R['held'], lambda v: f'opacity:{num(v, 3)}')
           + kf('kdRw', R['sweat'], lambda v: f'transform:translateY({num(v[0])}px) scale({num(v[1], 3)});opacity:{num(v[2], 3)}')
           + ''.join(kf_translate(f'kdPup{k + 1}', [(t, ((x - 1) * s, (y - 1) * s), e)
                                                     for t, (x, y), e in sample(lambda t, k=k: look(sc.robot_eye(eyes[k], t), sc.robot_look(t), EYE_R))])
                     for k in range(2))
           + ''.join(heart_css(k + 1, t0) for k, (t0, *_rest) in enumerate(HEARTS))
           + '@media (prefers-reduced-motion:reduce){.kdw *{animation:none!important}}')
    return html, css


def judge_inline(fn, alt=ALT):
    """判定画面（Judge_Kids.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="bnr kdw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(alt)
    page, k = re.subn(r'<div class="bnr kdw" .*?</div>(?=\s*<main)|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = (f'/* 子供向けの壁紙：毛糸玉が転がって、ロボットと馬が目で追い、止まると馬が跳ねて喜ぶ → ロボットが拾いに行って うっかり蹴り、'
             f'いっしょに右へ → 持って戻って 左へポーン（kids_wall.py） */\n{css}\n/* /子供向けの壁紙 */\n')
    if '/* 子供向けの壁紙：' in page:
        page = re.sub(r'/\* 子供向けの壁紙：.*?/\* /子供向けの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def plan():
    sc = Scene()
    sc.check()
    R = sc.R
    for t in [0, .2, .4, .66, 1, 2, 3, 4, 5, 5.6, 6.0, 6.5, 6.62, 6.8, 7.0, 7.3, 7.6, 8.0, 8.6, 9.0, 9.5, 10.0, 10.6, 11.5, 11.8, 12]:
        b = sc.ball(t)
        print(f'{t:5.2f}秒  見ている毛糸玉 ({b[0]:6.1f},{b[1]:6.1f})  ロボット ずれ {R["dx"].at(t):6.1f}・見える {R["op"].at(t):.2f}・'
              f'体 {tuple(round(v, 2) for v in R["bob"].at(t))}・右腕 {R["arm"][1].at(t):6.1f}°・手の毛糸玉 {R["held"].at(t):.0f}')


if __name__ == '__main__':
    if '--plan' in sys.argv:
        plan()
    else:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1])
