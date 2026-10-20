"""バレンタイン・ホワイトデーの壁紙の動き（まさちゃんの指定「バレンタイン、ホワイトデイ エフェクト:常にハートが動いている 常に馬がカップルを目でおっている
   1〜3秒でカップルが馬を撫でにいく 3〜5秒馬を撫でる 3秒〜5秒馬が喜んで尻尾を3回縦に振る 3秒〜5秒馬の耳が前を向く 6秒〜9秒でカップルが元に位置に戻る
   6回中1回ランダムで、カップルが馬に近く、撫でる時に馬がブチギレてカップルが吹っ飛ぶ、2人とも焦って立ち上がり顔をあせて元の位置に戻る」
   「10秒に一回リピート」）：ページに入れる HTML と CSS
   - 重ねる順：いまの止まった絵（<img class="bnr">：視差効果を減らす なら これだけ）→ 空の絵（kpB）→ バレンタインは 空の ハート（SVG：いつも ふわふわ）→
     前の絵（kpF：馬と とろける チョコ。すき通しつき）→ 馬の 頭と しっぽの コマ（kpH・kpT：すき通しつきの シート）→ カップル（SVG）→ 手前の チョコ・マシュマロ（SVG）。
     絵は flat/couple_run.py（キャンバスの id は couple_blobs.json・置く場所は couple_run.json）
   - 10秒（CYCLE）で 1回。12回（N_CYC＝2分）で1回り。12回のうち 2回（6回に1回：ANGRY）が ブチギレの回（いつも同じ予定：schedule）。
     ふつうの回と ブチギレの回は 部品を べつべつに 持ち（kpN・kpA）、2分の 切りかえ（visibility）で どちらかを 見せる（どちらも 10秒で くり返す CSS）
     1回の中の 時刻（秒）：
       ふつうの回：1〜2.85 カップルが 馬の所へ 歩く（前に 立つ子は 鼻を・うしろの子は 馬の 胸を なでる 場所：place）→ 3〜5 なでる（手を のばして なでなで・
             女の子は ＾＾）・馬は 3.05〜 耳が 前を向く（〜5.1）・3.1〜4.9 しっぽを 3回 たてに ふる・頭の上に 小さな ハート → 6〜9 もとの場所へ 歩いて もどる
             （カップルの上の ハートは 近づくほど 上へ：馬の 耳を かくさない）
       ブチギレの回：1〜2.85 いつもより 近くへ → 3.0 手を 上げた とたん 馬が ブチギレ（耳を ふせて おこった まゆ・💢・鼻から ふんっ）→ 3.16〜3.4 首を つきだす →
             3.2 カップルが 吹っ飛ぶ（1回転 半分 まわって 3.8 どすんと 床に ねころぶ・＞＜・ハートが はじける）→ 4.5 あせって 立ちあがり（汗）→ 4.75〜6.2 いそいで もとの場所へ →
             汗だくで 馬を 見る → 9.0 ハートが もどる
   - 馬は いつも カップルを 見る（馬の目から 2人の 頭の まん中への 向きで 見下ろす ぐあいを 決め、ばねで なめらかに ついていく：horse_e）
   - ハート：バレンタインの 空の ハート 16（ふわふわ 上下・ふくらむ）と、カップルの上の ハート 3（2人の まん中に ついていく・ふわふわ）
   クラスの名前は kp…（的中ボタンの .vl…・.wd… とは別）
   python3 couple_wall.py --judge <テーマ> <Judge_….dc.html> <couple_blobs.json> <couple_run.json>  → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 couple_wall.py --plan                                                               → 予定（ブチギレの回）"""
import sys, os, re, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'flat'))
import event_art as A

CYCLE = 10.0                     # 1回（まさちゃん「10秒に一回リピート」）
N_CYC = 12                       # 1回りの 回数
N_ANGRY = 2                      # そのうち ブチギレの回（まさちゃん「6回中1回ランダムで」）
SEED = 3                         # 予定の 乱数の種
LOOP = CYCLE * N_CYC
KS = 0.95                        # 子どもの 大きさ（いまの絵）
CLOSE = (16.0, 14.0)             # ブチギレの回は いつもより 近く（鼻の子・肩の子）
FLY = dict(nose=290.0, shoulder=205.0)    # 吹っ飛ぶ はば（もとの場所の 方へ：鼻の子・肩の子。ねころんだ 2人が かさならない）
LIE = 50.0                       # 吹っ飛んで 床に ねころぶ（からだの まん中で 90度 まわして、その ぶん 下げる）
HEART_UP = -30.0                 # なでる所では カップルの上の ハートを 上げる（馬の 耳が かくれない）
HEAD_Y = dict(girl=-128.0, boy=-134.0)    # 頭の まん中（子どもの 座標）
SHOULDER = dict(girl=dict(armD=(-16.0, -96.0), armO=(16.0, -96.0)), boy=dict(armO=(20.0, -98.0), armS=(-22.0, -98.0)))   # hand_out＝1 の 時（−1 は x を うらがえす）
ARM_END = dict(girl=dict(armD=(-22.0, -62.0), armO=(46.0, -84.0)), boy=dict(armO=(46.0, -86.0), armS=(-26.0, -62.0)))
BODY_C = -85.0                   # 子どもが まわる 中心（からだの まん中）
THEMES = {
    # place：なでる時の 足もと（鼻を なでる子は 鼻先から 前へ nose・胸を なでる子は 鼻先から うしろへ shoulder）と、胸の子が 手を のばす 先（鼻先から うしろへ・下へ）
    'valentine': dict(fx=1, home=dict(girl=552.0, boy=664.0), nose='boy', shoulder='girl', place=dict(nose=38.0, shoulder=67.0, aim_sh=(117.0, 1.0)),
                      girl=dict(args=lambda: dict(hold=A.heart_box(0.9), hand_out=1), pet='armD'),
                      boy=dict(args=lambda: dict(hand_out=-1, shy=True), pet='armO'),
                      shadow=(600.0, 300.0, 110.0, 7.0, '#C9708E', .45), hearts=((600, 116, 9), (624, 92, 6), (580, 92, 5)), heart_col='#E8547C',
                      pop_col='#F06A92'),
    # ホワイトデーの 男の子は びんを 女の子の方へ 持つので、首の 下より うしろ（胸の前）に 立つ（びんが 馬の 鼻先に かからない）
    'whiteday': dict(fx=-1, home=dict(girl=122.0, boy=226.0), nose='girl', shoulder='boy', place=dict(nose=38.0, shoulder=88.0, aim_sh=(143.0, -1.0)),
                     girl=dict(args=lambda: dict(dress='#F7B6CB', dressD='#E58FAD', hair='#4A2E22', hairD='#33201A', ribbon='#6FAEDB', hand_out=1, hold=None), pet='armO'),
                     boy=dict(args=lambda: dict(top='#6FA8DC', topD='#4F8CC8', pants='#3E5A80', hair='#5A3A28', hand_out=-1, shy=False,
                                                hold=A.g(A.jar(46, 54), 0, 26, 0.95)), pet='armS'),
                     shadow=(170.0, 300.0, 112.0, 7.0, '#8FB4D6', .45), hearts=((170, 104, 8), (150, 84, 5.5), (192, 86, 5)), heart_col='#8CC4EC',
                     pop_col='#7FB8E8'),
}
MOVE_ALT = ('（いつも ハートが ふわふわ動き、馬は いつも カップルを 目で追う。10秒ごとに カップルが 馬を なでにいき、馬は 耳を 前に向けて '
            'しっぽを 3回 たてに ふって よろこぶ。6回に1回は 馬が ブチギレて カップルが 吹っ飛び、あせって 立ちあがって もどる）')   # 絵の説明（themes20.py の alt）の あとに つける

# ---- 1回の中の 時刻（秒）
T_GO = (1.0, 2.85)               # 馬の所へ（まさちゃん「1〜3秒」）
GO_STEPS = 7
T_PET = (3.0, 5.0)               # なでる（まさちゃん「3〜5秒」）
T_EAR = (3.05, 3.30, 4.85, 5.10) # 耳が 前を向く（まさちゃん「3秒〜5秒」：むける・もどす）
T_WAG = (3.1, 4.9)               # しっぽを 3回 たてに（まさちゃん「3秒〜5秒」）
N_WAG = 3
T_BACK = (6.0, 9.0)              # もとの場所へ（まさちゃん「6秒〜9秒」）
BACK_STEPS = 10
T_HOP = 5.25                     # なでた あと うれしくて ぴょん
POPS = (3.35, 3.85, 4.35)        # 馬の 頭の上の 小さな ハート
# ブチギレの回
T_MAD = 3.0                      # 耳を ふせる（〜3.12）
T_LUNGE = (3.16, 3.24, 3.40)     # 首を つきだす・もどす
T_FLY = (3.2, 3.8)               # 吹っ飛ぶ
T_UP = (4.5, 4.75)               # あせって 立ちあがる
T_HURRY = (4.75, 6.2)            # いそいで もどる
HURRY_STEPS = 8
T_CALM = (4.40, 4.55)            # 馬の 耳が もどる
T_SWEAT_END = 9.2
T_HEARTS_BACK = (9.0, 9.4)
EASE = {'linear': 'linear', 'ease-in': 'ease-in', 'ease-out': 'ease-out', 'ease-in-out': 'ease-in-out', 'step-end': 'step-end'}
BEZ = {'ease-in': (.42, 0, 1, 1), 'ease-out': (0, 0, .58, 1), 'ease-in-out': (.42, 0, .58, 1)}


# ---------------------------------------------------------------- 予定
def schedule(seed=SEED):
    """1回りの うち ブチギレの回（0 から 数えた 番号）。はじめの回は ふつう・となりあわない・早めに 1回"""
    rnd = random.Random(seed)
    while True:
        a = sorted(rnd.sample(range(1, N_CYC), N_ANGRY))
        gaps = [b - x for x, b in zip(a, a[1:])] + [a[0] + N_CYC - a[-1]]
        if min(gaps) >= 3 and a[0] <= 3 and len(set(gaps)) > 1:
            return a


ANGRY = schedule()


# ---------------------------------------------------------------- 数と キーフレーム（1回 10秒の CSS）
def num(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    if s.startswith('0.'):
        s = s[1:]
    elif s.startswith('-0.'):
        s = '-' + s[2:]
    return '0' if s in ('-0', '', '-') else s


def pct(t, L=CYCLE):
    s = f'{t / L * 100:.3f}'.rstrip('0').rstrip('.')
    return (s or '0') + '%'


class Keys:
    """1回の キーを 時刻の順に つむ（to：その時刻に その値・e：つぎの キーまでの 動き）"""
    def __init__(self, rest, e='linear'):
        self.k = [(0.0, rest, e)]

    def to(self, t, v, e='linear'):
        t = round(t, 4)
        assert t > self.k[-1][0], (t, self.k[-1])
        self.k.append((t, v, e))
        return self

    def at(self, t, v, e='linear'):
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
        if self.k[-1][0] < CYCLE - 1e-9:
            self.to(CYCLE, self.k[0][1])
        assert self.k[-1][1] == self.k[0][1], (self.k[-1], self.k[0])
        return self.k


def clean(keys):
    """前と うしろと 同じ値の キーを はぶく。つぎと 同じ値の キーの 動きは どれでも同じ（None）"""
    out = [k for i, k in enumerate(keys) if i in (0, len(keys) - 1) or not (keys[i - 1][1] == k[1] == keys[i + 1][1])]
    return [(t, v, e if i + 1 < len(out) and out[i + 1][1] != v else None) for i, (t, v, e) in enumerate(out)]


def kf(name, keys, fmt):
    """1回の キー → (@keyframes, ふだんの 動き)"""
    ks = clean(keys)
    es = [e for _, _, e in ks if e]
    dflt = max(sorted(set(es)), key=es.count) if es else 'linear'
    ps = [pct(t) for t, _, _ in ks]
    assert len(set(ps)) == len(ps), name
    body = ''.join(f'{p}{{{fmt(v)}' + (f';animation-timing-function:{EASE[e]}' if e and e != dflt else '') + '}' for p, (t, v, e) in zip(ps, ks))
    return f'@keyframes {name}{{{body}}}', EASE[dflt]


def kf_step(name, keys, prop):
    """切りかえ [(秒, 値)…]（はじめの値＝止まっている値）→ step-end の @keyframes（1回 10秒）"""
    body = f'0%{{{prop}:{keys[0][1]}}}' + ''.join(f'{pct(t)}{{{prop}:{v}}}' for t, v in keys[1:])
    return f'@keyframes {name}{{{body}100%{{{prop}:{keys[0][1]}}}}}'


def bezier(x1, y1, x2, y2):
    def fn(u):
        lo, hi = 0.0, 1.0
        for _ in range(40):
            s = (lo + hi) / 2
            x = 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
            lo, hi = (s, hi) if x < u else (lo, s)
        s = (lo + hi) / 2
        return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3
    return fn


EASE_FN = {k: bezier(*v) for k, v in BEZ.items()}
EASE_FN['linear'] = lambda u: u
EASE_FN['step-end'] = lambda u: 0.0


def value_at(keys, t):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0, e0), (t1, v1, _) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            if v0 == v1:
                return v0
            return v0 + (v1 - v0) * EASE_FN[e0 or 'linear']((t - t0) / (t1 - t0))
    return keys[-1][1]


def smooth01(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- 場所
def layout(theme, run):
    """子どもの 足もとの x：もとの場所（home）・なでる所（pet）・ブチギレの回（close）・吹っ飛んで おちる所（land）。と 鼻先・肩の 目あて"""
    th = THEMES[theme]
    fx = th['fx']
    mx, my = run['muzzle_look']
    nose, sh = th['nose'], th['shoulder']
    home = dict(th['home'])
    pl = th['place']
    pet = {nose: mx + fx * pl['nose'], sh: mx - fx * pl['shoulder']}
    close = {nose: pet[nose] - fx * CLOSE[0], sh: pet[sh] - fx * CLOSE[1]}
    land = {nose: close[nose] + fx * FLY['nose'], sh: close[sh] + fx * FLY['shoulder']}
    aim = {nose: (mx - fx * 2.0, my - 3.0), sh: (mx - fx * pl['aim_sh'][0], my + pl['aim_sh'][1])}      # 手を のばす 先（鼻先・胸：首の 下は 子どもの 頭と かさなって 手を ふる形に 見える）
    return dict(home=home, pet=pet, close=close, land=land, aim=aim)


def shoulder_of(kid, arm, ho):
    sx, sy = SHOULDER[kid][arm]
    ex, ey = ARM_END[kid][arm]
    return (sx * ho, sy), (ex * ho, ey)


def arm_angle(kid, arm, ho, foot_x, aim):
    """うでを aim（780×320 の 座標）へ むける まわす 角度（度・SVG の rotate）"""
    (sx, sy), (ex, ey) = shoulder_of(kid, arm, ho)
    gx, gy = foot_x + KS * sx, 300 + KS * sy
    a_rest = math.degrees(math.atan2(ey - sy, ex - sx))
    a_aim = math.degrees(math.atan2(aim[1] - gy, aim[0] - gx))
    d = a_aim - a_rest
    while d > 180:
        d -= 360
    while d < -180:
        d += 360
    return round(d, 2)


# ---------------------------------------------------------------- 子ども（1回の キー）
def steps(t0, t1, n):
    d = (t1 - t0) / n
    return [(t0 + i * d, t0 + (i + 1) * d, i % 2) for i in range(n)]


def walk_sets(typ):
    """歩く 組 [(はじめ, おわり, 歩数)]"""
    if typ == 'n':
        return [(T_GO[0], T_GO[1], GO_STEPS), (T_BACK[0], T_BACK[1], BACK_STEPS)]
    return [(T_GO[0], T_GO[1], GO_STEPS), (T_HURRY[0], T_HURRY[1], HURRY_STEPS)]


def kid_tracks(theme, run, typ, kid):
    """子ども 1人の 1回の キー：X（780 の 座標の よこ）・Y（上下）・R（からだの まん中で まわる：ブチギレの回）・Q（どすんで つぶれる）・
       LL／LR（足を 上げる）・Ar（なでる うで）・顔の 切りかえ"""
    th = THEMES[theme]
    fx = th['fx']
    lay = layout(theme, run)
    h = lay['home'][kid]
    tgt = (lay['pet'] if typ == 'n' else lay['close'])[kid]
    ho = th[kid]['args']()['hand_out']
    arm = th[kid]['pet']
    ang = arm_angle(kid, arm, ho, tgt, lay['aim'][kid])
    T = {}
    k = Keys(0.0).to(T_GO[0], 0.0, 'ease-in-out').to(T_GO[1], round(tgt - h, 2))
    if typ == 'n':
        k.hold(T_BACK[0], 'ease-in-out').to(T_BACK[1], 0.0)
    else:
        k.hold(T_FLY[0], 'ease-out').to(T_FLY[1], round(lay['land'][kid] - h, 2)).hold(T_HURRY[0], 'ease-in-out').to(T_HURRY[1], 0.0)
    T['X'] = k.end()
    # 上下：歩くと はずむ・なでた あと ぴょん（ふつう）／吹っ飛ぶ・どすん・立ちあがる（ブチギレ）
    k = Keys(0.0)
    ws = walk_sets(typ)
    for a, b, _ in steps(*ws[0]):
        k.at(a, 0.0, 'ease-out').to((a + b) / 2, -3.0, 'ease-in').to(b, 0.0)
    if typ == 'n':
        k.at(T_HOP, 0.0, 'ease-out').to(T_HOP + 0.14, -10.0, 'ease-in').to(T_HOP + 0.28, 0.0)
    else:
        k.at(T_FLY[0], 0.0, 'ease-out').to(T_FLY[0] + 0.3, -72.0, 'ease-in').to(T_FLY[1], LIE, 'ease-out').to(T_FLY[1] + 0.1, LIE - 6.0, 'ease-in')
        k.to(T_FLY[1] + 0.2, LIE).hold(T_UP[0], 'ease-out').to(T_UP[0] + 0.12, -14.0, 'ease-in').to(T_UP[1], 0.0)
    for a, b, _ in steps(*ws[1]):
        k.at(a, 0.0, 'ease-out').to((a + b) / 2, -3.0, 'ease-in').to(b, 0.0)
    T['Y'] = k.end()
    for side in (0, 1):
        k = Keys(0.0)
        for s in ws:
            for a, b, d in steps(*s):
                if d == side:
                    k.at(a, 0.0, 'ease-out').to((a + b) / 2, -5.0, 'ease-in').to(b, 0.0)
        T['L%d' % side] = k.end()
    # なでる うで（かたが 中心）
    k = Keys(0.0).to(T_PET[0], 0.0, 'ease-out').to(T_PET[0] + 0.2, ang, 'ease-in-out')
    if typ == 'n':                                      # なでなで：0.2秒ごとに ±8度（さいごは 下ろす）
        t, sg = T_PET[0] + 0.2, 1
        while t + 0.2 <= T_PET[1] - 0.2 + 1e-9:
            t += 0.2
            k.to(t, round(ang + 8.0 * sg, 2), 'ease-in-out')
            sg = -sg
        k.at(T_PET[1] - 0.2, k.k[-1][1], 'ease-in-out').to(T_PET[1], 0.0)
    else:
        k.hold(T_FLY[1], 'ease-in-out').to(T_FLY[1] + 0.15, 0.0)
    T['Ar'] = k.end()
    if typ == 'a':
        sg = fx
        T['R'] = (Keys(0.0).to(T_FLY[0], 0.0, 'ease-out').to(T_FLY[1], 450.0 * sg).hold(T_UP[0], 'ease-in-out').to(T_UP[1], 360.0 * sg, 'step-end')    # 1回転 半分 まわって ねころぶ → 立つ
                  .to(T_UP[1] + 0.05, 0.0).end())                                          # 360度＝0度（step-end：とちゅうの 角度を 出さない）
        T['Q'] = (Keys((1.0, 1.0)).to(T_FLY[1], (1.0, 1.0), 'ease-out').to(T_FLY[1] + 0.06, (0.85, 1.08), 'ease-in-out')   # どすん（ねころんだ 向きで つぶれる）
                  .to(T_FLY[1] + 0.18, (1.0, 1.0)).end())
    return T, ang


def kid_steps(theme, typ, kid):
    """顔と うでの 切りかえ（step）：E0＝いまの目・Eh＝＾＾・Eo＝まるい目・Es＝＞＜・M0＝いまの口・Mo＝あけた口・Fb／Ff＝なでる うでの うしろ／前の 絵"""
    out = {}
    if typ == 'n':
        if kid == 'girl':
            out['E0'] = [(0, 1), (T_PET[0], 0), (T_HOP + 0.35, 1)]
            out['Eh'] = [(0, 0), (T_PET[0], 1), (T_HOP + 0.35, 0)]
            out['Fb'] = [(0, 1), (T_PET[0], 0), (T_PET[1], 1)]
            out['Ff'] = [(0, 0), (T_PET[0], 1), (T_PET[1], 0)]
        return out
    calm = T_SWEAT_END
    if kid == 'girl':
        out['E0'] = [(0, 1), (T_FLY[0], 0), (T_UP[0], 1)]
        out['Fb'] = [(0, 1), (T_PET[0], 0), (T_FLY[1] + 0.15, 1)]
        out['Ff'] = [(0, 0), (T_PET[0], 1), (T_FLY[1] + 0.15, 0)]
    else:
        out['E0'] = [(0, 1), (T_FLY[0], 0), (calm, 1)]
        out['Eo'] = [(0, 0), (T_UP[0], 1), (calm, 0)]
    out['Es'] = [(0, 0), (T_FLY[0], 1), (T_UP[0], 0)]
    out['M0'] = [(0, 1), (T_FLY[0], 0), (T_HURRY[1], 1)]
    out['Mo'] = [(0, 0), (T_FLY[0], 1), (T_HURRY[1], 0)]
    return out


def sweat_keys():
    return Keys(0.0).to(T_UP[0], 0.0).to(T_UP[0] + 0.1, 1.0).hold(T_SWEAT_END - 0.2).to(T_SWEAT_END, 0.0).end()


def pair_keys(a, b, fn):
    """時刻と 動きが 同じ 2つの キー → fn(a の値, b の値) の キー"""
    assert [t for t, _, _ in a] == [t for t, _, _ in b] and [e for _, _, e in a] == [e for _, _, e in b]
    return [(t, fn(va, vb), e) for (t, va, e), (_, vb, _) in zip(a, b)]


# ---------------------------------------------------------------- 馬（コマ）
TRACK_W = 12.0                   # 馬が ついていく はやさ（ばね）


def gaze_target(theme, run, typ, t, KT):
    """2人の 頭の まん中（780×320）"""
    lay = layout(theme, run)
    xs, ys = [], []
    for kid in ('girl', 'boy'):
        T = KT[kid]
        xs.append(lay['home'][kid] + value_at(T['X'], t))
        ys.append(300 + KS * HEAD_Y[kid] + value_at(T['Y'], t))
    return sum(xs) / 2, sum(ys) / 2


def gaze(theme, run, typ, t, KT):
    """馬の目（いまの絵）から 2人の 頭の まん中への 下向きの 角度（度）"""
    fx = THEMES[theme]['fx']
    ex, ey = run['eye']
    x, y = gaze_target(theme, run, typ, t, KT)
    return math.degrees(math.atan2(y - ey, max(1.0, fx * (x - ex))))


def gaze_pet(theme, run):
    """なでる所に 2人が いる時の 角度（見下ろす ぐあい 1）"""
    th = THEMES[theme]
    lay = layout(theme, run)
    ex, ey = run['eye']
    x = (lay['pet']['girl'] + lay['pet']['boy']) / 2
    y = 300 + KS * (HEAD_Y['girl'] + HEAD_Y['boy']) / 2
    return math.degrees(math.atan2(y - ey, max(1.0, th['fx'] * (x - ex))))


def horse_e(theme, run, typ, KT, dt=0.001):
    """1回の中の 見下ろす ぐあい e（dt ごと）：ねらいに ばねで ついていく（耳・ブチギレの コマを 出している あいだは 1 で とめる）"""
    g0, g1 = gaze(theme, run, typ, 0.0, KT), gaze_pet(theme, run)
    hold = (T_EAR[0], T_EAR[3]) if typ == 'n' else (T_MAD, T_CALM[1])
    n = int(round(CYCLE / dt))
    e, v, out = 0.0, 0.0, []
    for i in range(n + 1):
        t = i * dt
        if hold[0] <= t <= hold[1]:
            e, v = 1.0, 0.0
        else:
            tgt = min(1.0, max(0.0, (gaze(theme, run, typ, t, KT) - g0) / (g1 - g0)))
            a = TRACK_W * TRACK_W * (tgt - e) - 2 * TRACK_W * v
            v += a * dt
            e += v * dt
        out.append(e)
    return out


def head_index(run, name):
    return run['head']['names'].index(name)


def head_frames_at(theme, run, typ, KT):
    """1回の中で 頭の コマが かわる時 [(秒, コマの番号)]（1ミリ秒 きざみ）"""
    lv = [0.0] + run['look']
    es = horse_e(theme, run, typ, KT)
    look = lambda e: min(range(len(lv)), key=lambda i: abs(lv[i] - e))       # U0＝0・L1〜＝1〜
    nE = sum(1 for nm in run['head']['names'] if nm[0] == 'E')
    nA = sum(1 for nm in run['head']['names'] if nm[0] == 'A')
    nK = sum(1 for nm in run['head']['names'] if nm[0] == 'K')
    L_top = len(lv) - 1

    def ramp(t, t0, t1, n, pre):
        """t0〜t1 で 1〜n（pre＋番号）"""
        k = min(n, max(1, int(math.floor((t - t0) / (t1 - t0) * n)) + 1))
        return head_index(run, f'{pre}{k}')

    out, cur = [], 0
    for i, e in enumerate(es):
        t = i / 1000
        f = look(e)
        if typ == 'n':
            if T_EAR[0] <= t < T_EAR[1]:
                f = ramp(t, T_EAR[0], T_EAR[1], nE, 'E')
            elif T_EAR[1] <= t < T_EAR[2]:
                f = head_index(run, f'E{nE}')
            elif T_EAR[2] <= t < T_EAR[3]:
                f = head_index(run, f'E{nE - min(nE - 1, int((t - T_EAR[2]) / (T_EAR[3] - T_EAR[2]) * nE))}')
        else:
            t_a1 = T_MAD + 0.12
            if T_MAD <= t < t_a1:
                f = ramp(t, T_MAD, t_a1, nA, 'A')
            elif t_a1 <= t < T_LUNGE[0]:
                f = head_index(run, f'A{nA}')
            elif T_LUNGE[0] <= t < T_LUNGE[1]:
                f = ramp(t, T_LUNGE[0], T_LUNGE[1], nK, 'K')
            elif T_LUNGE[1] <= t < T_LUNGE[2]:
                f = head_index(run, f'K{nK - min(nK - 1, int((t - T_LUNGE[1]) / (T_LUNGE[2] - T_LUNGE[1]) * nK))}')
            elif T_LUNGE[2] <= t < T_CALM[0]:
                f = head_index(run, f'A{nA}')
            elif T_CALM[0] <= t < T_CALM[1]:
                f = head_index(run, f'A{nA - min(nA - 1, int((t - T_CALM[0]) / (T_CALM[1] - T_CALM[0]) * nA))}')
        if f != cur:
            out.append((round(t, 3), f))
            cur = f
    assert cur == 0, (theme, typ, cur)
    return out


def tail_angle(typ, t):
    """しっぽを 持ちあげる 角度（度）"""
    if typ == 'n':
        if T_WAG[0] <= t < T_WAG[1]:
            per = (T_WAG[1] - T_WAG[0]) / N_WAG
            u = ((t - T_WAG[0]) % per) / per
            return 50.0 * smooth01(u * 2 if u < 0.5 else 2 - u * 2)
        return 0.0
    t0 = T_MAD + 0.12
    for k in range(2):                                   # ブチギレ：2回 びゅんっ
        a = t0 + k * 0.25
        if a <= t < a + 0.1:
            return 40.0 * smooth01((t - a) / 0.1)
        if a + 0.1 <= t < a + 0.25:
            return 40.0 * (1 - smooth01((t - a - 0.1) / 0.15))
    return 0.0


def tail_frames_at(run, typ):
    lv = [0.0] + run['tail_lift']
    out, cur = [], 0
    for i in range(int(round(CYCLE * 1000)) + 1):
        t = i / 1000
        a = tail_angle(typ, t)
        f = min(range(len(lv)), key=lambda j: abs(lv[j] - a))
        if f != cur:
            out.append((round(t, 3), f))
            cur = f
    assert cur == 0
    return out


def sheet_css(cls, blob, part, changes):
    """シートを コマごとに ずらす (html, css)（step-end・10秒）"""
    cols = part['cols']
    cw, ch = (v // 2 for v in part['cell'])
    ax, ay = (v // 2 for v in part['at'])
    g = part['pad'] // 2
    sw, sh = cols * (cw + 2 * g), part['rows'] * (ch + 2 * g)
    by = {0: ['0%', '100%']}
    for t, f in changes:
        by.setdefault(f, []).append(pct(t))
    body = ''
    for f in sorted(by):
        r, c = divmod(f, cols)
        body += f'{",".join(by[f])}{{transform:translate({-c * (cw + 2 * g)}px,{-r * (ch + 2 * g)}px)}}'
    html = f'<div class="{cls}"><div class="{cls}x"></div></div>'
    css = (f'.kp .{cls}{{position:absolute;left:{ax}px;top:{ay}px;width:{cw}px;height:{ch}px;overflow:hidden}}'
           f'.kp .{cls}x{{position:absolute;left:-{g}px;top:-{g}px;width:{sw}px;height:{sh}px;background:url({blob}) 0 0/{sw}px {sh}px no-repeat;'
           f'animation:{cls}A {CYCLE:g}s step-end infinite;will-change:transform}}@keyframes {cls}A{{{body}}}')
    return html, css


# ---------------------------------------------------------------- SVG
def pv(cls, p, inner):
    """動く中心 p で はさむ：<g translate(p)><g class><g translate(-p)>…"""
    return (f'<g transform="translate({num(p[0])} {num(p[1])})"><g class="{cls}">'
            f'<g transform="translate({num(-p[0])} {num(-p[1])})">{inner}</g></g></g>')


def gc(cls, inner):
    return f'<g class="{cls}">{inner}</g>'


def kid_svg(theme, typ, kid):
    """子ども 1人（いまの絵と 同じ 部品・同じ 順）：歩く・なでる・吹っ飛ぶ ための <g> つき"""
    th = THEMES[theme]
    spec = th[kid]
    args = spec['args']()
    ho = args['hand_out']
    b = A.girl_bits(**args) if kid == 'girl' else A.boy_bits(**args)
    fx = A.kid_fx(-126.0 if kid == 'girl' else -132.0)
    p = f'kp{typ}{kid[0]}'
    arm = spec['pet']
    sh, _ = shoulder_of(kid, arm, ho)
    st = kid_steps(theme, typ, kid)
    order = A.GIRL_ORDER if kid == 'girl' else A.BOY_ORDER
    legs = {'L': ('legL', 'shoeL', 'soleL'), 'R': ('legR', 'shoeR', 'soleR')}
    o = ''
    for k in order:
        v = b.get(k, '')
        if k in ('legL', 'legR'):
            side = 0 if k == 'legL' else 1
            v = gc(f'{p}L{side}', ''.join(b.get(q, '') for q in legs[k[-1]]))
        elif k in ('shoeL', 'shoeR', 'soleL', 'soleR'):
            continue                                            # 足と いっしょ（足の 上に かく：いまの絵と 同じ 見た目）
        elif k == arm:
            if kid == 'girl':                                   # 女の子の なでる うで：うしろの 絵（いまの順）と 前の 絵（髪の 上）を 切りかえる
                v = gc(f'{p}Fb', v)
            else:
                v = pv(f'{p}Ar', sh, v)
        elif k == 'eyes':
            v = gc(f'{p}E0', v)
            for nm, key in (('Eh', 'eyesHappy'), ('Eo', 'eyesOpen'), ('Es', 'eyesShut')):
                if nm in st:
                    v += gc(f'{p}{nm}', fx[key])
        elif k == 'mouth':
            v = gc(f'{p}M0', v) + (gc(f'{p}Mo', fx['mouthO']) if 'Mo' in st else '')
        elif k == 'hair':
            v = v + (gc(f'{p}Sw', fx['sweat']) if typ == 'a' else '')
        elif k == 'hand' and kid == 'girl' and arm == 'armO':
            v = gc(f'{p}Fb', v)
        o += v
        if k == 'ribbon' and kid == 'girl':                     # 前の うで（なでる時：髪の 上）
            front = b[arm] + (b['hand'] if arm == 'armO' else '')
            o += gc(f'{p}Ff', pv(f'{p}Ar', sh, front))
    if typ == 'a':
        o = pv(f'{p}R', (0.0, BODY_C), gc(f'{p}Q', o))
    hx = th['home'][kid]
    return gc(f'{p}X', gc(f'{p}Y', f'<g transform="translate({num(hx)} 300) scale({num(KS)})">{o}</g>'))


def love_svg(theme, typ):
    """カップルの上の ハート 3つ（2人の まん中に ついていく・ふわふわ）"""
    th = THEMES[theme]
    cx = sum(x for x, _, _ in th['hearts']) / 3
    cy = sum(y for _, y, _ in th['hearts']) / 3
    inner = ''
    for i, (x, y, s) in enumerate(th['hearts']):
        inner += (f'<g transform="translate({num(x)} {num(y)})"><g class="kpLb" style="animation-delay:{num(-0.55 * i)}s">'
                  f'{A.path(A.heart_d(0, 0, s), th["heart_col"])}</g></g>')
    return gc(f'kp{typ}LX', pv(f'kp{typ}LB', (cx, cy), inner))


def shadow_svg(theme, typ):
    x, y, rx, ry, col, op = THEMES[theme]['shadow']
    return gc(f'kp{typ}CX', f'<g transform="translate({num(x)} {num(y)})">' + gc(f'kp{typ}CS', A.ell(0, 0, rx, ry, col, extra=f'opacity="{op}"')) + '</g>')


def anger_mark():
    """💢（おこりの しるし：4つの かぎ。まん中が 0,0）"""
    o = ''
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        o += A.line(f'M{sx * 3},{sy * 10} Q{sx * 3},{sy * 3} {sx * 10},{sy * 3}', '#E8283C', 3.6)
    return o


def puff():
    pts = ((-4, 0, 4.5), (2, -3, 5.5), (6, 1, 4))
    return (''.join(A.circ(x, y, r + 1.2, '#C9D8EA') for x, y, r in pts) + ''.join(A.circ(x, y, r, '#FFFFFF') for x, y, r in pts))


def burst():
    return A.path(A.star_d(0, 0, 16, 7, n=8, rot=-90), '#FFE36A') + A.path(A.star_d(0, 0, 8, 3.5, n=8, rot=-67.5), '#FFFFFF')


def fx_svg(theme, run, typ):
    """馬の まわりの しるし：ふつう＝頭の上の 小さな ハート／ブチギレ＝💢・鼻から ふんっ・ドンッ"""
    th = THEMES[theme]
    fx = th['fx']
    ex, ey = run['eye_look']
    mx, my = run['muzzle_look']
    if typ == 'n':
        o = ''
        for i, _ in enumerate(POPS):
            x, y = ex + fx * (14 + 10 * i), ey - 26
            o += f'<g transform="translate({num(x)} {num(y)})">' + gc(f'kpnP{i}', A.path(A.heart_d(0, 0, 5.5), th['pop_col'])) + '</g>'
        return o
    o = f'<g transform="translate({num(ex - fx * 4)} {num(ey - 32)})">' + gc('kpaAm', anger_mark()) + '</g>'
    for i in range(2):
        o += f'<g transform="translate({num(mx + fx * 6)} {num(my - 8)}) scale({num(fx)} 1)">' + gc(f'kpaS{i}', puff()) + '</g>'
    o += f'<g transform="translate({num(mx + fx * 20)} {num(my - 6)})">' + gc('kpaIm', burst()) + '</g>'
    return o


def fx_tracks(typ):
    T = {}
    if typ == 'n':
        for i, t in enumerate(POPS):
            T[f'kpnP{i}'] = (Keys((0.0, 0.4, 0.0)).to(t, (0.0, 0.4, 0.0), 'ease-out').to(t + 0.18, (-8.0, 1.0, 1.0), 'ease-in-out')
                             .to(t + 0.8, (-30.0, 0.9, 0.0)).end())
        return T
    t0 = T_MAD + 0.1
    k = Keys((0.0, 0.0)).to(t0, (0.0, 0.0), 'ease-out').to(t0 + 0.1, (1.3, 1.0), 'ease-in-out').to(t0 + 0.2, (1.0, 1.0), 'ease-in-out')
    t = t0 + 0.2
    while t + 0.25 <= T_CALM[0]:
        k.to(t + 0.125, (1.15, 1.0), 'ease-in-out').to(t + 0.25, (1.0, 1.0), 'ease-in-out')
        t += 0.25
    T['kpaAm'] = k.hold(T_CALM[0]).to(T_CALM[1], (1.0, 0.0)).end()
    for i, ts in enumerate((T_MAD + 0.3, T_MAD + 0.75)):
        T[f'kpaS{i}'] = (Keys(((0.0, 0.0), 0.5, 0.0)).to(ts, ((0.0, 0.0), 0.5, 0.0), 'ease-out').to(ts + 0.12, ((4.0, -2.0), 1.0, 1.0), 'ease-out')
                         .to(ts + 0.55, ((16.0, -8.0), 1.5, 0.0)).end())
    T['kpaIm'] = (Keys((0.3, 0.0)).to(T_FLY[0] - 0.02, (0.3, 0.0), 'ease-out').to(T_FLY[0] + 0.08, (1.2, 1.0), 'ease-in')
                  .to(T_FLY[0] + 0.22, (1.4, 0.0)).end())
    return T


def bg_hearts_svg():
    """バレンタインの 空の ハート 16（いまの絵と 同じ 場所・大きさ・こさ。いつも ふわふわ 上下して ふくらむ）"""
    import numpy as np
    rng = np.random.default_rng(14)
    rnd = random.Random(17)
    o = ''
    for i, (x, y, s, op) in enumerate(A.sky_hearts(rng, 780)):
        dur = rnd.uniform(2.6, 4.2)
        o += (f'<g transform="translate({num(x)} {num(y)})"><g class="kpYh" style="animation-duration:{num(dur)}s;animation-delay:{num(-rnd.uniform(0, dur))}s">'
              f'{A.path(A.heart_d(0, 0, s), "#FFFFFF", f"opacity=\"{op:.2f}\"")}</g></g>')
    return f'<svg class="kpY" viewBox="0 0 780 320" aria-hidden="true">{o}</svg>'


def front_items_svg(theme):
    """手前の チョコ・マシュマロ（いまの絵と 同じ：カップルの 前）"""
    if theme == 'valentine':
        lay = A.shadow(400, 306, 120, 6, '#C9708E', .4)
        lay += A.g(A.choco_bar(76, 36), 380, 308, rot=-6) + A.g(A.truffle(12), 444, 308) + A.g(A.truffle(10, top='#F7A8C0'), 470, 310)
        lay += A.g(A.heart_box(0.75, '#6B3A22', '#4E2816', '#F2C14E'), 330, 296) + A.g(A.truffle(9, drizzle=False), 300, 312)
        lay += A.g(A.truffle(10), 740, 310) + A.g(A.heart_box(0.6), 768, 300)
    else:
        lay = A.shadow(400, 306, 110, 6, '#8FB4D6', .4)
        cols = (('#FFFFFF', '#E3EAF2'), ('#FFD6E2', '#F2B5C8'), ('#D6ECFB', '#B5D6EF'))
        for i, (x, y, w, rot) in enumerate(((330, 308, 26, -8), (360, 312, 22, 6), (392, 306, 28, -4), (424, 312, 22, 10), (452, 308, 24, -6), (300, 314, 20, 0))):
            c, cd = cols[i % 3]
            lay += A.g(A.marshmallow(w, w * 0.78, c, cd), x, y, rot=rot)
        lay += A.g(A.gift(40, 30, '#FFFFFF', '#D6E2EE', '#8CC4EC'), 740, 308) + A.g(A.marshmallow(22, 17, '#FFD6E2', '#F2B5C8'), 706, 312, rot=-8)
    return f'<svg class="kpS" viewBox="0 0 780 320" aria-hidden="true">{lay}</svg>'


# ---------------------------------------------------------------- CSS
def rig_css(theme, run, typ, blobs):
    """1つの 組（ふつう n／ブチギレ a）の (svg, players の html, css)"""
    th = THEMES[theme]
    L = f'{CYCLE:g}s'
    rules, kfs, mv = '', '', []

    def track(cls, keys, fmt):
        nonlocal rules, kfs
        k, e = kf(cls + 'K', keys, fmt)
        rules += f'.kp .{cls}{{animation:{cls}K {L} {e} infinite}}'
        kfs += k
        mv.append(cls)

    def step(cls, keys, prop='opacity'):
        nonlocal rules, kfs
        rules += f'.kp .{cls}{{animation:{cls}K {L} step-end infinite}}'
        kfs += kf_step(cls + 'K', keys, prop)

    tx = lambda v: f'transform:translateX({num(v)}px)'
    ty = lambda v: f'transform:translateY({num(v)}px)'
    rot = lambda v: f'transform:rotate({num(v)}deg)'
    KT = {}
    for kid in ('girl', 'boy'):
        T, _ = kid_tracks(theme, run, typ, kid)
        KT[kid] = T
        p = f'kp{typ}{kid[0]}'
        track(p + 'X', T['X'], tx)
        track(p + 'Y', T['Y'], ty)
        track(p + 'L0', T['L0'], ty)
        track(p + 'L1', T['L1'], ty)
        track(p + 'Ar', T['Ar'], rot)
        if typ == 'a':
            track(p + 'R', T['R'], rot)
            track(p + 'Q', T['Q'], lambda v: f'transform:scale({num(v[0])},{num(v[1])})')
            track(p + 'Sw', sweat_keys(), lambda v: f'opacity:{num(v)}')
        for nm, keys in kid_steps(theme, typ, kid).items():
            step(p + nm, keys)
    # ハートと 影：2人の まん中に ついていく
    avg = pair_keys(KT['girl']['X'], KT['boy']['X'], lambda a, b: round((a + b) / 2, 2))
    lay = layout(theme, run)
    tgt = lay['pet'] if typ == 'n' else lay['close']
    a1 = sum(tgt[k] - lay['home'][k] for k in ('girl', 'boy')) / 2          # なでる所に 着いた時の avg
    up = lambda v: round(HEART_UP * min(1.0, max(0.0, v / a1)), 2)          # 近づくほど ハートを 上げる（馬の 耳の 上を あける）
    track(f'kp{typ}LX', [(t, (v, up(v)), e) for t, v, e in avg], lambda v: f'transform:translate({num(v[0])}px,{num(v[1])}px)')
    track(f'kp{typ}CX', avg, tx)
    sp0 = th['home']['boy'] - th['home']['girl']
    ratio = pair_keys(KT['girl']['X'], KT['boy']['X'], lambda a, b: round(abs(sp0 + b - a) / abs(sp0), 3))
    if typ == 'n':
        track('kpnCS', [(t, (v, 1.0), e) for t, v, e in ratio], lambda v: f'transform:scaleX({num(v[0], 3)});opacity:{num(v[1])}')
        track('kpnLB', Keys(1.0).to(T_PET[0], 1.0, 'ease-out').to(T_PET[0] + 0.3, 1.25).hold(T_PET[1], 'ease-in-out').to(T_PET[1] + 0.4, 1.0).end(),
              lambda v: f'transform:scale({num(v)})')
    else:
        cs = [(t, (v, 1.0 if t <= T_FLY[0] or t >= T_HURRY[1] + 0.3 else 0.0), e) for t, v, e in ratio]
        cs = Keys((1.0, 1.0)).to(T_GO[0], (1.0, 1.0), 'ease-in-out')
        r_close = [v for t, v, e in ratio if abs(t - T_GO[1]) < 1e-9][0]
        cs.to(T_GO[1], (r_close, 1.0)).hold(T_FLY[0]).to(T_FLY[0] + 0.15, (r_close, 0.0)).hold(T_HURRY[1]).to(T_HURRY[1] + 0.001, (1.0, 0.0)).to(T_HURRY[1] + 0.3, (1.0, 1.0))
        track('kpaCS', cs.end(), lambda v: f'transform:scaleX({num(v[0], 3)});opacity:{num(v[1])}')
        track('kpaLB', (Keys((1.0, 1.0)).to(T_FLY[0], (1.0, 1.0), 'ease-out').to(T_FLY[0] + 0.25, (1.6, 0.0)).hold(T_HEARTS_BACK[0])
                        .to(T_HEARTS_BACK[0] + 0.001, (0.2, 0.0), 'ease-out').to(T_HEARTS_BACK[0] + 0.25, (1.15, 1.0), 'ease-in-out')
                        .to(T_HEARTS_BACK[1], (1.0, 1.0)).end()),
              lambda v: f'transform:scale({num(v[0])});opacity:{num(v[1])}')
    for cls, keys in fx_tracks(typ).items():
        if cls in ('kpaS0', 'kpaS1'):
            track(cls, keys, lambda v: f'transform:translate({num(v[0][0])}px,{num(v[0][1])}px) scale({num(v[1])});opacity:{num(v[2])}')
        elif cls == 'kpaIm' or cls == 'kpaAm':
            track(cls, keys, lambda v: f'transform:scale({num(v[0])});opacity:{num(v[1])}')
        else:
            track(cls, keys, lambda v: f'transform:translateY({num(v[0])}px) scale({num(v[1])});opacity:{num(v[2])}')
    # 馬の コマ
    hh, hc = sheet_css(f'kp{typ}H', blobs['head'], run['head'], head_frames_at(theme, run, typ, KT))
    th_, tc = sheet_css(f'kp{typ}T', blobs['tail'], run['tail'], tail_frames_at(run, typ))
    kids = ''.join(kid_svg(theme, typ, k) for k in ('girl', 'boy'))
    svg = (f'<svg class="kpS kp{typ.upper()}" viewBox="0 0 780 320" aria-hidden="true">{shadow_svg(theme, typ)}{kids}{love_svg(theme, typ)}'
           f'{fx_svg(theme, run, typ)}</svg>')
    players = f'<div class="kp{typ.upper()}">{hh}{th_}</div>'
    css = ','.join(f'.kp .{c}' for c in mv) + '{transform-box:view-box;transform-origin:0 0}' + rules + kfs + hc + tc
    hide = [f'.kp .kp{typ}{k}{nm}' for k in 'gb' for nm in ('Eh', 'Eo', 'Es', 'Mo', 'Ff', 'Sw')]
    css += ','.join(hide) + '{opacity:0}'
    return svg, players, css


def switch_css():
    """2分で 1回り：ブチギレの回だけ kpA を 見せて kpN を かくす（visibility・step-end）"""
    n, a = '0%{visibility:visible}', '0%{visibility:hidden}'
    for i in ANGRY:
        n += f'{pct(i * CYCLE, LOOP)}{{visibility:hidden}}{pct((i + 1) * CYCLE, LOOP)}{{visibility:visible}}'
        a += f'{pct(i * CYCLE, LOOP)}{{visibility:visible}}{pct((i + 1) * CYCLE, LOOP)}{{visibility:hidden}}'
    return (f'.kp .kpN{{animation:kpSwN {LOOP:g}s step-end infinite}}.kp .kpA{{visibility:hidden;animation:kpSwA {LOOP:g}s step-end infinite}}'
            f'@keyframes kpSwN{{{n}100%{{visibility:visible}}}}@keyframes kpSwA{{{a}100%{{visibility:hidden}}}}')


def inline(theme, blobs, run):
    """(html, css)。blobs：still（いまの止まった絵）・sky・front・head・tail → '/_blob/<id>'。run：couple_run.json の テーマの 所"""
    th = THEMES[theme]
    svg_n, pl_n, css_n = rig_css(theme, run, 'n', blobs)
    svg_a, pl_a, css_a = rig_css(theme, run, 'a', blobs)
    hearts = bg_hearts_svg() if theme == 'valentine' else ''
    from themes20 import THEMES as T20
    alt = next(x for x in T20 if x['id'] == theme)['alt'] + MOVE_ALT
    html = (f'<div class="kp" role="img" aria-label="{alt}"><img class="bnr" src="{blobs["still"]}" alt="">'
            f'<img class="kpB" src="{blobs["sky"]}" alt="">{hearts}<img class="kpF" src="{blobs["front"]}" alt="">'
            f'{pl_n}{pl_a}{svg_n}{svg_a}{front_items_svg(theme)}</div>')
    css = ('.kp{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.kp .bnr,.kp .kpB,.kp .kpF{position:absolute;left:0;top:0;width:390px;height:160px;display:block;object-fit:cover;object-position:50% 50%}'
           '.kp svg{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none}'
           '.kp .kpLb{transform-box:view-box;transform-origin:0 0;animation:kpLbK 1.7s ease-in-out infinite alternate}'
           '@keyframes kpLbK{to{transform:translateY(-4px) scale(1.12)}}'
           + ('.kp .kpYh{transform-box:view-box;transform-origin:0 0;animation:kpYhK 3s ease-in-out infinite alternate}'
              '@keyframes kpYhK{to{transform:translateY(-7px) scale(1.08)}}' if hearts else '')
           + switch_css() + css_n + css_a
           + '@media (prefers-reduced-motion:reduce){.kp .kpB,.kp .kpF,.kp .kpN,.kp .kpA,.kp svg{display:none}}')
    return html, css


def judge_inline(theme, fn, blobs, run):
    """判定画面（Judge_Valentine／Judge_WhiteDay）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="kp">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(theme, blobs, run)
    page, n = re.subn(r'<div class="kp" role="img".*?</svg></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* カップルの壁紙：いつも ハートが 動き、10秒ごとに カップルが 馬を なでにいく（couple_wall.py） */\n{css}\n/* /カップルの壁紙 */\n'
    if '/* カップルの壁紙：' in page:
        page = re.sub(r'/\* カップルの壁紙：.*?/\* /カップルの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn, theme):
    """couple_blobs.json（テーマごとの sky・front・head・tail）と、同じ フォルダの blobs20.json（いまの止まった絵）"""
    b = {k: f'/_blob/{v}' for k, v in json.load(open(fn))[theme].items()}
    b['still'] = '/_blob/' + json.load(open(os.path.join(os.path.dirname(os.path.abspath(fn)), 'blobs20.json')))[theme]
    return b


if __name__ == '__main__':
    if '--plan' in sys.argv:
        print('ブチギレの回（0 から）:', ANGRY, f'（{LOOP:g}秒で 1回り）')
    else:
        i = sys.argv.index('--judge')
        theme = sys.argv[i + 1]
        judge_inline(theme, sys.argv[i + 2], load_blobs(sys.argv[i + 3], theme), json.load(open(sys.argv[i + 4]))[theme])
