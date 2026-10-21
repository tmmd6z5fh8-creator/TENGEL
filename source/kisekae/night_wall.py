"""ナイターの壁紙の動き（まさちゃんの指定「常に走ってる、背景が常に右から左に模様が動く同じ模様をリピートする、
   1秒〜5秒の間に3頭の順位が前後する、20秒に一回ゴールする馬はランダムにする」
   「ゴールしたら一回皆んなゆっくりとまって、5秒かけて画面暗くして 6秒から7秒で勝った馬表彰して！」
   「表彰後、1秒暗くして、2秒からまたレーススタートしてる演出にして！」）：ページに入れる HTML と CSS
   絵は flat/night_run.py（くり返せる背景3まい・1頭ずつの ギャロップのシート・止まる／立つ／走りだす コマのシート・表彰の絵）。
   キャンバスでは /_blob/<id>（night_blobs.json）
   1レース＝BLOCK 34秒（ブロックの中の時刻 u。0＝真っ暗の まんなか）：
     0.5秒 照明が1つずつ ぱっとつく → 0.8〜1.4秒 明るくなる → 1.0秒 3頭が走りだす（「スタート！」・足の運びが だんだん速く・景色も流れだす）
     → 1〜5秒ごとに となりどうしが入れかわる → 20.5秒 ゴール（照明がついてから 20秒。板が 1着の鼻先を通って ふわっと光る）
     → 3頭が ゆっくり止まる（約2.2秒・景色も止まる）・5秒かけて 真っ暗に
     → 25.5〜32.5秒 表彰（7秒：スポットライトの中に 勝った馬・騎手のガッツポーズ・優勝のレイ・1着のバッジ・紙ふぶき・カメラの光）
     → 32.5〜33.5秒 1秒で暗く → 真っ暗（つぎのレースの並びに かえる）→ つぎのブロックの 0.5秒（表彰の2秒あと）に 照明がつく
   6レース（1着 7→3→5→3→7→5）で 204秒の1回り。ページを開くと ブロック0の 10.5秒（いままでどおり 10秒で1回目のゴール）
   - 景色（3まいの帯）は 遠いほど ゆっくり：空とスタンドと照明 FLOW['far'] 秒・奥の柵とダート FLOW['track'] 秒・手前の柵 FLOW['rail'] 秒で
     1まいぶん（390px）。止まる時・走りだす時は 馬の足の運びと同じ速さの かわり方で（ブロックの はじめは いつも同じ位置）
   - 馬は 3つの重ね：走る（ギャロップ GALLOP_S 秒・steps）／止まる・走りだすの とちゅうで使う ギャロップのコマ（同じシート）／
     止まる・立つ・走りだす コマ（night_t*.webp）。どれを見せるかと コマは 1回りの キーフレームで めくる
   - いちばん下は いまの止まった絵（<img class="bnr">）。視差効果を減らす（prefers-reduced-motion）なら 動く絵を消して いまの絵だけ
   クラスの名前は nt…（ページの ほかの名前と ぶつからないように）
   python3 night_wall.py --judge <Judge_Night.dc.html> <night_blobs.json> <night_run.json>  → 判定画面の上の絵を「動くナイター」に書きかえる（何回やっても同じ）
   python3 night_wall.py --plan                                                          → レースの予定（照明・走りだし・順位の入れかわり・ゴールと 1着・表彰の時刻）"""
import sys, os, re, json, math, random
from itertools import permutations

W2, H2 = 390, 160
STATIC = '/_blob/5669e8b79972b750876e84c7eea2fb3f'        # いまの止まった絵（WebP）
ALT = ('照明に照らされた夜のコースを走る3頭の馬と騎手のアニメ風イラスト（いつも走っていて景色が流れる・順位が入れかわり、'
       'ゴールすると止まって暗くなり、勝った馬の表彰のあと 照明がついて また走りだす）')
FLOW = dict(far=24.0, track=3.2, rail=2.2)                # 1まいぶん（390px）流れる秒（手前の柵の支柱が 1秒に3本より少なく通る）
GALLOP_S = .5                                            # ギャロップ1回の秒
RACE_S, DARK_S, AWARD_S, FADE_S = 20.0, 5.0, 7.0, 1.0    # 照明がついてから ゴールまで・ゴールから真っ暗まで・表彰・表彰のあと暗くなる
T_LIGHT = 0.5                                            # 照明がつく（ブロックの中の時刻）
T_START = 1.0                                            # 走りだす（GALLOP_S の倍数：ギャロップの コマと そろう）
T_GOAL = T_LIGHT + RACE_S                                # 20.5：ゴール
T_AWARD = T_GOAL + DARK_S                                # 25.5：表彰
T_AWEND = T_AWARD + AWARD_S                              # 32.5：表彰おわり
T_BLACK = T_AWEND + FADE_S                               # 33.5：真っ暗
BLOCK = T_AWEND + 2.0 - T_LIGHT                          # 34：表彰の2秒あと（つぎのブロックの T_LIGHT）に 照明がつく
T_RESET = T_BLACK + 0.3                                  # 真っ暗の間に 景色・ゴール板・並びを もどす
RACES = 6
LOOP = BLOCK * RACES                                     # 204秒で1回り
OPEN_U = 10.5                                            # ページを開いた時の 1回りの中の時刻（10秒で1回目のゴール・GALLOP_S の倍数）
EPS = 0.002
# 順位ごとの 3頭の 鼻先の x（絵の画素・780のはば）。手前の大きな7番に 頭が かくれないように、順位の ならびごとに決めた
# （7番より うしろの馬は 7番のおしりより うしろ・ほかの馬の頭も 前の馬の体に かからない所。頭の見える割合は どれも 9割くらい以上）
LAYOUT = {(5, 3, 7): {5: 680, 3: 560, 7: 440}, (3, 5, 7): {5: 510, 3: 690, 7: 400},
          (5, 7, 3): {5: 700, 3: 350, 7: 620}, (3, 7, 5): {5: 330, 3: 700, 7: 620},
          (7, 5, 3): {5: 425, 3: 295, 7: 690}, (7, 3, 5): {5: 240, 3: 425, 7: 690}}
PERMS = sorted(LAYOUT)
TRANS = (1.0, 1.8)                                       # 入れかわりの秒（動く はばが大きいほど ゆっくり）
GAP = (2.0, 4.8)                                         # つぎの入れかわりまで（秒）：1〜5秒の中で
FIRST = (2.5, 4.0)                                       # 走りだしてから 最初の入れかわりまで
CALM = 2.3                                               # ゴールの前は この秒のあいだ 入れかわらない（1着が 先頭のまま 板を通る）
LAST = 5.0                                               # ゴールの前 この秒の中に 入れかわりが1回はある（1〜5秒ごと）
START_DX = 14                                            # 走りだしで 前へ出る はば（画面の px）
SWAY = {5: (2.5, 3.0), 3: (3.0, 2.5), 7: (2.0, 2.0)}     # それぞれの 前後のゆれ（片道の秒・はば px）
SEED = 12
DRAW = (5, 3, 7)                                         # 重ねる順（奥 → 手前）
POST_FOOT = 100                                          # ゴール板の 柱の下のはしの y（画面の px・奥の柵の 白い横木の高さ）。板の絵は 高さ 78px
LAMPS = ((65, 20), (195, 10), (325, 17))                 # 照明（画面の px：景色が もどった時の位置＝flat/night_run.py の TOWERS の半分）
DARK = '#02030A'                                         # 暗くなる幕の色
CONFETTI = ('#FFD24A', '#FFF4D6', '#FF5A7A', '#FFB020', '#9EE6FF', '#FFFFFF')


# ---------------- 1着とレースの予定 ----------------
def winners(seed=SEED):
    """RACES 回の1着（3頭とも同じ回数・つづけて同じ馬はない・1回りの さいごと はじめも ちがう）"""
    rnd = random.Random(seed)
    while True:
        w = [5, 3, 7] * (RACES // 3)
        rnd.shuffle(w)
        if all(w[i] != w[(i + 1) % RACES] for i in range(RACES)) and not all(w[i] == w[(i + 3) % RACES] for i in range(RACES)):
            return w                                             # （3回ごとの くり返しの順も よける）


def plan(seed=SEED):
    """レースの予定：[dict(win=1着, start=走りだしの順位, events=[(u, 新しい順位)])]。u はブロックの中の時刻。
       入れかわりは 1回に となりどうし1組・間かくは 1〜5秒（GAP）・走りだしてから FIRST 秒で1回目・ゴールの前 CALM 秒は 入れかわらない・
       ゴールの前 LAST 秒の中に1回はある・ゴールの時に その回の1着が先頭。走りだしの順位は 1着の馬が先頭でない ならび"""
    rnd = random.Random(seed * 7 + 1)
    races = []
    for w in winners(seed):
        for attempt in range(20000):
            start = rnd.choice([p for p in PERMS if p[0] != w])
            times, t = [], T_START + rnd.uniform(*FIRST)
            while t <= T_GOAL - CALM:
                times.append(round(t, 2))
                t += rnd.uniform(*GAP)
            if not times or times[-1] < T_GOAL - LAST:
                continue
            sol = []

            def dfs(i, order, last):
                if i == len(times):
                    return order[0] == w
                opts = [0, 1]
                rnd.shuffle(opts)
                opts.sort(key=lambda k: k == last)                    # 同じ2頭が すぐ入れかわり直すのは あとで
                for k in opts:
                    o2 = list(order)
                    o2[k], o2[k + 1] = o2[k + 1], o2[k]
                    sol.append((times[i], tuple(o2)))
                    if dfs(i + 1, o2, k):
                        return True
                    sol.pop()
                return False
            if dfs(0, list(start), None):
                races.append(dict(win=w, start=start, events=sol))
                break
        else:
            raise SystemExit('plan not found')
    return races


# ---------------- 止まる・走りだすの 時刻（flat/night_run.py の timing） ----------------
class Timing:
    def __init__(self, tm):
        self.f0, self.dt, self.dp, self.dend, self.dstand = tm['f0'], tm['dec_t'], tm['dec_p'], tm['dec_end'], tm['dec_stand']
        self.at, self.aq, self.ag0 = tm['acc_t'], tm['acc_q'], tm['acc_g0']
        self.phi_at = self.f0 * self.at / (self.aq + 1)          # 走りだして at 秒の 足の運びの回数
        self._table()

    def dec_phi(self, t):
        t = min(max(t, 0.0), self.dt)
        return self.f0 * self.dt / (self.dp + 1) * (1 - (1 - t / self.dt) ** (self.dp + 1))

    def dec_t(self, phi):
        x = 1 - phi * (self.dp + 1) / (self.f0 * self.dt)
        return self.dt * (1 - max(x, 0.0) ** (1 / (self.dp + 1)))

    def dec_amp(self, phi):
        u = min(max((phi - 1.0) / (self.dend - 1.0), 0.0), 1.0)
        return 0.5 * (1 + math.cos(math.pi * u))

    def acc_phi(self, t):
        if t <= 0:
            return 0.0
        if t <= self.at:
            return self.phi_at * (t / self.at) ** (self.aq + 1)
        return self.phi_at + self.f0 * (t - self.at)

    def acc_t(self, phi):
        if phi <= self.phi_at:
            return self.at * (phi / self.phi_at) ** (1 / (self.aq + 1))
        return self.at + (phi - self.phi_at) / self.f0

    def acc_amp(self, phi):
        return math.sin(math.pi / 2 * min(max(phi, 0.0), 1.0))

    def speed(self, u):
        """ブロックの時刻 u の 景色の速さ（走る時＝1）：足の運びの速さ × 足の大きさ"""
        if u < T_START:
            return 0.0
        if u < T_GOAL:
            t = u - T_START
            if t >= self.at and self.acc_phi(t) >= 1.0:
                return 1.0
            return min(1.0, (t / self.at) ** self.aq) * self.acc_amp(self.acc_phi(t))
        t = u - T_GOAL
        if t >= self.dec_t(self.dstand):
            return 0.0
        return (1 - t / self.dt) ** self.dp * self.dec_amp(self.dec_phi(t))

    def _table(self, du=0.002):
        """景色が流れた きょり（走る速さで1秒＝1）の表：ブロックの はじめから"""
        n = int(round(BLOCK / du))
        self.du = du
        self.I = [0.0]
        v0 = self.speed(0.0)
        for i in range(1, n + 1):
            v1 = self.speed(i * du)
            self.I.append(self.I[-1] + (v0 + v1) / 2 * du)
            v0 = v1

    def dist(self, u):
        x = min(max(u, 0.0), BLOCK) / self.du
        i = min(int(x), len(self.I) - 2)
        f = x - i
        return self.I[i] * (1 - f) + self.I[i + 1] * f


# ---------------- キーフレーム ----------------
def kf_pct(t, period):
    return f'{100 * t / period:.{5 if period > BLOCK else 4}f}'.rstrip('0').rstrip('.') + '%'


def keyframes(name, kfs, fmt, period=BLOCK, step=False):
    """kfs：[(t, 値, 次までの動き)] → @keyframes（period 秒で1回り）。100% は さいごの値。step：どれも step-end（動きの名前を書かない）"""
    out = []
    for t, v, tf in kfs:
        f = f';animation-timing-function:{tf}' if tf and not step else ''
        out.append(f'{kf_pct(t, period)}{{{fmt(v)}{f}}}')
    out.append(f'100%{{{fmt(kfs[-1][1])}}}')
    return f'@keyframes {name}{{{"".join(out)}}}'


def races_kfs(blocks):
    """ブロックごとの [(u, 値, 動き)] → 1回り（LOOP 秒）の [(t, 値, 動き)]"""
    return [(k * BLOCK + u, v, tf) for k, kfs in enumerate(blocks) for u, v, tf in kfs]


def anim(name, period=BLOCK, tf='linear', twin=None):
    """ページを開いた時が 1回りの OPEN_U 秒（BLOCK の くり返しも 同じ ずれ：LOOP は BLOCK の倍数）。
       twin：見えない 間は 描かない アニメ（vis_twin の 名前・step-end で 同じ 周期）を いっしょに つける"""
    tw = f',{twin} {period:g}s step-end -{OPEN_U:g}s infinite' if twin else ''
    return f'animation:{name} {period:g}s {tf} -{OPEN_U:g}s infinite{tw}'


def vis_(o):
    """こさ 0/1 の コマ（step-end）を visibility に（見た目は 同じ・0 の 間は 描かない）"""
    return f'visibility:{"visible" if o else "hidden"}'


def vis_twin(name, kfs, period=BLOCK, op=lambda v: v):
    """こさの キーフレーム kfs（[(t, 値, 次までの動き)]・op：値 → こさ）から、こさが 0 の 間だけ visibility:hidden に する
       アニメ（step-end）を 作る（まさちゃん「他も同じようにいらないデータ使ってるものが、もしあれは整えて！」：
       見えない 間も 合成の 層の 画素を 使わない ように）。次の キーフレームまでの 間に こさが 0 より 大きい 所が あれば 見せる"""
    out = []
    for i, (t, v, tf) in enumerate(kfs):
        o0 = op(v)
        o1 = op(kfs[i + 1][1]) if i + 1 < len(kfs) else o0
        show = o0 > 0 or (o1 > 0 and tf != 'step-end')
        if not out or out[-1][1] != show:
            out.append((t, show, None))
    return keyframes(name, out, vis_, period, step=True)


def pos_x(run, num, order):
    """順位の ならび order の時の その馬の 横のずれ（画面の px）"""
    return (LAYOUT[tuple(order)][num] - run['horses'][str(num)]['nose']) / 2


def trans_s(dx):
    """横に dx（画面の px）動く 入れかわりの秒"""
    return min(TRANS[1], max(TRANS[0], 0.9 + abs(dx) / 130))


def order_at(race, u):
    o = race['start']
    for t, order in race['events']:
        if t <= u:
            o = order
    return o


def band_block(tm, v, period=W2):
    """1ブロックの 帯の横のずれ（速さ v px/秒）：くり返しの はばで もどす（もどる所は 同じ絵なので見えない）"""
    ts = [0.0, T_START] + [T_START + 0.05 * i for i in range(1, 25)] + [T_GOAL] + [T_GOAL + 0.1 * i for i in range(1, 31)] + [T_RESET]
    kfs = [(0.0, 0.0, None)]
    for t0, t1 in zip(ts, ts[1:]):
        d0, d1 = v * tm.dist(t0), v * tm.dist(t1)
        w = math.floor(d0 / period + 1e-9) + 1
        while w * period < d1 - 1e-6:                                         # このあいだで 1まいぶん流れた所
            tw = t0 + (w * period - d0) / (d1 - d0) * (t1 - t0)
            kfs.append((tw, -period, 'step-end'))
            kfs.append((tw + EPS, -(v * tm.dist(tw + EPS) - w * period), None))
            w += 1
        kfs.append((t1, -(d1 - math.floor(d1 / period + 1e-9) * period), None))
    u, x, _ = kfs.pop()                                                       # 真っ暗の間に もどす
    kfs += [(u, x, 'step-end'), (u + EPS, 0.0, None)]
    return kfs


def post_block(tm, xmin):
    """ゴール板の 1着の鼻先（xg）からの ずれ と 見える／見えない：奥の柵と同じ速さで 右から左へ、ゴールの時刻に ずれ 0（鼻先）。
       止まる時は 景色と同じに止まる。xmin：いちばん左の xg（どのレースでも 右の外から入る）"""
    v = W2 / FLOW['track']
    off = W2 + 40 - xmin
    u_in = T_GOAL - off / v
    kfs = [(0.0, (off, 0), 'step-end'), (u_in, (off, 1), 'linear'), (T_GOAL, (0.0, 1), None)]
    for i in range(1, 31):
        u = T_GOAL + 0.1 * i
        kfs.append((u, (-v * (tm.dist(u) - tm.dist(T_GOAL)), 1), None))
    kfs += [(T_RESET, kfs[-1][1], 'step-end'), (T_RESET + EPS, (off, 0), None)]
    return kfs


def horse_block(run, num, race, nxt):
    """馬の 横のずれ：走りだしで START_DX 前へ → 入れかわり → ゴール後は そのまま → 真っ暗の間に つぎの走りだしの並びへ"""
    x = pos_x(run, num, race['start']) - START_DX
    kfs = [(0.0, x, None), (T_START, x, 'cubic-bezier(.2,.7,.3,1)')]
    x = pos_x(run, num, race['start'])
    kfs.append((T_START + 1.4, x, None))
    for t, order in race['events']:
        nx = pos_x(run, num, order)
        if abs(nx - x) < 1e-6:
            continue
        kfs.append((t, x, 'ease-in-out'))
        kfs.append((t + trans_s(nx - x), nx, None))
        x = nx
    kfs += [(T_RESET, x, 'step-end'), (T_RESET + EPS, pos_x(run, num, nxt['start']) - START_DX, None)]
    return kfs


def sway_block(num):
    """前後のゆれ：走っている間だけ（走りだして1.5秒から・ゴールのあと 1.2秒で 0 へ）"""
    dur, amp = SWAY[num]
    u0 = T_START + 1.5
    kfs = [(0.0, 0.0, None), (u0, 0.0, 'ease-in-out')]
    t, sgn = u0 + dur / 2, 1
    while t < T_GOAL:
        kfs.append((t, sgn * amp, 'ease-in-out'))
        t += dur
        sgn = -sgn
    kfs.append((T_GOAL + 1.2, 0.0, None))
    return kfs


def show_block(on):
    """見せる／かくす（step-end）：on＝[(u, 1か0)]"""
    return [(u, v, 'step-end') for u, v in on]


def gallop_frames_block(tm, cw):
    """止まる・走りだすの とちゅうで使う ギャロップのコマ（ギャロップのシートの 何番目か）"""
    kfs = [(0.0, 0.0, 'step-end')]
    m = 10
    while True:                                                               # 走りだし：足の運びが1回をこえてから ページのギャロップに かわるまで
        t = tm.acc_t(m / 10)
        if t >= 1.0 - 1e-6:
            break
        kfs.append((T_START + t, -((round(10 * tm.ag0) + m) % 10) * cw, 'step-end'))
        m += 1
    for k in range(0, 11):                                                     # 止まる：ギャロップ1回ぶん（足の運びが だんだん ゆっくり）
        kfs.append((T_GOAL + tm.dec_t(k / 10), -(k % 10) * cw, 'step-end'))
    return kfs


def trans_frames_block(tm, tr):
    """止まる・立つ・走りだす コマ（night_t*.webp の 何番目か）"""
    cw, ch, cols = tr['cell'][0] / 2, tr['cell'][1] / 2, tr['cols']
    cell = lambda i: (-(i % cols) * cw, -(i // cols) * ch)
    idx = {(f['kind'], f['phi']): i for i, f in enumerate(tr['frames'])}
    stand = [i for i, f in enumerate(tr['frames']) if f['kind'] == 'stand'][0]
    kfs = [(0.0, cell(stand), 'step-end')]
    for f in tr['frames']:
        if f['kind'] == 'acc':
            kfs.append((T_START + tm.acc_t(f['phi']), cell(idx[('acc', f['phi'])]), 'step-end'))
    for f in tr['frames']:
        if f['kind'] == 'dec':
            kfs.append((T_GOAL + tm.dec_t(f['phi']), cell(idx[('dec', f['phi'])]), 'step-end'))
    kfs.append((T_GOAL + tm.dec_t(tm.dstand), cell(stand), 'step-end'))
    return sorted(kfs, key=lambda k: k[0])


# ---------------- 絵（SVG） ----------------
def post_svg():
    """ゴール板（白い柱の上に、白黒の市松もようの板・金のふち。ゴールの時に うしろが ふわっと光る .ntgl）"""
    sq = ''.join(f'<rect x="{-12 + 4 * c}" y="{-39 + 4 * r}" width="4" height="4" fill="{"#1A1024" if (r + c) % 2 else "#FFFFFF"}"/>'
                 for r in range(4) for c in range(6))
    return ('<svg class="ntgs" viewBox="-14 -46 28 78" width="28" height="78" aria-hidden="true">'
            '<defs><radialGradient id="ntgG"><stop offset="0" stop-color="#FFF6D8" stop-opacity=".95"/><stop offset=".5" stop-color="#FFD27A" stop-opacity=".45"/>'
            '<stop offset="1" stop-color="#FFD27A" stop-opacity="0"/></radialGradient></defs>'
            '<circle class="ntgl" cx="0" cy="-31" r="24" fill="url(#ntgG)"/>'
            '<rect x="-1.6" y="-23" width="3.2" height="55" rx="1" fill="#E8ECFF"/><rect x="0.4" y="-23" width="1.2" height="55" fill="#9EA6D4"/>'
            '<rect x="-14" y="-41" width="28" height="20" rx="2.5" fill="#F2C14E"/><rect x="-13" y="-40" width="26" height="18" rx="1.8" fill="#1A1024"/>'
            + sq + '<rect x="-12" y="-39" width="24" height="16" fill="none" stroke="#1A1024" stroke-width=".6"/></svg>')


def badge_svg(num):
    """1着のバッジ（金のロゼット・こい紺の まるに「1着」・下に 番号のリボン）"""
    pts = []
    for i in range(36):
        r = 44 if i % 2 == 0 else 37.5
        a = math.pi * 2 * i / 36 - math.pi / 2
        pts.append(f'{r * math.cos(a):.1f},{r * math.sin(a):.1f}')
    g = f'ntbg{num}'
    return (f'<svg viewBox="-48 -48 96 126" width="96" height="126" aria-hidden="true">'
            f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF0B0"/><stop offset=".45" stop-color="#F4C24A"/>'
            f'<stop offset="1" stop-color="#B9771A"/></linearGradient></defs>'
            f'<path d="M-20 26 L-31 74 L-22 67 L-14 76 L-6 30 Z" fill="#E8264A" stroke="#6A1228" stroke-width="1.2"/>'
            f'<path d="M20 26 L31 74 L22 67 L14 76 L6 30 Z" fill="#E8264A" stroke="#6A1228" stroke-width="1.2"/>'
            f'<polygon points="{" ".join(pts)}" fill="url(#{g})" stroke="#8A5410" stroke-width="1.2"/>'
            f'<circle r="31" fill="#1A1024" stroke="#FFE08A" stroke-width="2.4"/><circle r="26.5" fill="none" stroke="#F4C24A" stroke-width=".8" opacity=".7"/>'
            f'<text x="0" y="4" text-anchor="middle" font-family="RocknRoll One, sans-serif" font-size="22" fill="#FFF6D8">1着</text>'
            f'<rect x="-15" y="9" width="30" height="13" rx="3" fill="#FFFFFF"/><text x="0" y="19.6" text-anchor="middle" '
            f'font-family="BIZ UDPGothic, sans-serif" font-weight="700" font-size="11.5" fill="#141022">{num}番</text></svg>')


def confetti_html(n=26, seed=41):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = 6 + (W2 - 12) * (i + rnd.uniform(0, 1)) / n
        c = CONFETTI[i % len(CONFETTI)]
        d = rnd.uniform(2.6, 4.2)
        out.append(f'<i style="left:{x:.0f}px;background:{c};--d:{d:.2f}s;--dl:-{rnd.uniform(0, d):.2f}s;'
                   f'--dx:{rnd.uniform(-26, 26):.0f}px;--r:{rnd.choice((-1, 1)) * rnd.uniform(300, 720):.0f}deg;'
                   f'width:{rnd.choice((4, 5, 6))}px;height:{rnd.choice((6, 7, 9))}px"></i>')
    return ''.join(out)


def flashes_html(seed=43):
    """カメラの光（下の方・小さく・1か所は 2秒に1回より少なく）"""
    rnd = random.Random(seed)
    xs = (28, 92, 158, 236, 300, 366)
    out = []
    for i, x in enumerate(xs):
        p = rnd.uniform(2.2, 3.1)
        out.append(f'<b style="left:{x}px;top:{rnd.uniform(118, 148):.0f}px;--p:{p:.2f}s;--dl:-{rnd.uniform(0, p):.2f}s"></b>')
    return ''.join(out)


# ---------------- ページに入れる HTML と CSS ----------------
def inline(blobs, run, alt=ALT, static=STATIC):
    """(html, css)。blobs：far・track・rail・h5・h3・h7（走る）・t5・t3・t7（止まる・立つ・走りだす）・a5・a3・a7（表彰）→ '/_blob/<id>'。run：night_run.json
       どのレースでも同じ動き（景色・コマ・幕・照明・紙ふぶき）は 1レース（BLOCK 秒）の キーフレーム、レースごとに ちがう所（並び・ゴール板の場所・表彰の馬）は 1回り（LOOP 秒）"""
    races = plan()
    tm = Timing(run['timing'])
    hz, tz = run['horses'], run['trans']
    nxt = lambda k: races[(k + 1) % RACES]
    bands = dict(far=('ntf', run['far']), track=('ntt', run['track']), rail=('ntr', run['rail']))
    html = (f'<div class="ntw" role="img" aria-label="{alt}"><img class="bnr" src="{static}" alt="">'
            f'<div class="ntb ntf"></div><div class="ntb ntt"></div>'
            f'<div class="ntg"><div class="ntgi">{post_svg()}</div></div>')
    for num in DRAW:
        html += (f'<div class="nth nth{num}"><div class="ntj ntj{num}">'
                 f'<div class="ntc{num}"><div class="nts nts{num}"></div></div>'
                 f'<div class="ntu{num}"><div class="ntv{num}"></div></div>'
                 f'<div class="ntk{num}"><div class="ntq{num}"></div></div></div></div>')
    html += '<div class="ntb ntr"></div><div class="ntd"></div>'
    html += ''.join(f'<i class="ntl ntl{i}"></i>' for i in range(len(LAMPS)))
    html += '<div class="ntst">スタート！</div><div class="ntaw">'
    for num in DRAW:
        html += f'<div class="nta nta{num}"><div class="ntz ntz{num}"></div><div class="ntbd ntbd{num}">{badge_svg(num)}</div></div>'
    html += f'<div class="ntfx">{confetti_html()}{flashes_html()}</div></div></div><!--/ntw-->'

    tx_ = lambda x: f'transform:translateX({x:.2f}px)'
    op_ = lambda o: f'opacity:{o}'
    css = ('.ntw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.ntw .bnr{position:absolute;left:0;top:0;width:390px;height:160px}'
           '.ntb{position:absolute;left:0;width:780px;background-repeat:repeat-x;will-change:transform}')
    for name, (cls, (y0, y1)) in bands.items():
        h = (y1 - y0) / 2
        css += (f'.{cls}{{top:{y0 / 2:g}px;height:{h:g}px;background-image:url({blobs[name]});background-size:{W2}px {h:g}px;{anim("ntF" + cls)}}}'
                + keyframes('ntF' + cls, band_block(tm, W2 / FLOW[name]), tx_))
    # ゴール板（柱の下のはしが 奥の柵の上）：外がわは レースごとの 1着の鼻先・内がわは そこからの ずれ（どのレースも同じ）
    xg = [LAYOUT[order_at(r, T_GOAL)][r['win']] / 2 for r in races]
    css += (f'.ntg{{position:absolute;left:-14px;top:{POST_FOOT - 78}px;width:28px;height:78px;pointer-events:none;{anim("ntGo", LOOP, "step-end")}}}'
            f'.ntgi{{width:28px;height:78px;{anim("ntGi")}}}.ntg .ntgs{{display:block;overflow:visible}}.ntgl{{opacity:0;{anim("ntGl", twin="ntGlV")}}}'
            + keyframes('ntGo', races_kfs([[(0.0, x, None)] for x in xg]), lambda x: f'transform:translateX({x:g}px)', LOOP, step=True)
            + keyframes('ntGi', post_block(tm, min(xg)), lambda p: f'transform:translateX({p[0]:.1f}px);opacity:{p[1]}')
            + keyframes('ntGl', GL := [(0.0, 0, None), (T_GOAL - 0.15, 0, None), (T_GOAL + 0.15, 1, None), (T_GOAL + 0.75, 0, None)], op_)
            + vis_twin('ntGlV', GL))
    for num in DRAW:
        r, t = hz[str(num)], tz[str(num)]
        cw, ch = r['cell'][0] / 2, r['cell'][1] / 2
        ax, ay = r['at'][0] / 2, r['at'][1] / 2
        n = r['frames']
        tw, th = t['cell'][0] / 2, t['cell'][1] / 2
        tx, ty = t['at'][0] / 2, t['at'][1] / 2
        d1 = T_GOAL + tm.dec_t(min(f['phi'] for f in t['frames'] if f['kind'] == 'dec'))      # 止まる コマ（night_t）に かわる
        a1 = T_START + tm.acc_t(1.0)                                                            # 走りだしの コマから ギャロップの コマに かわる
        gal = [(0.0, 0), (T_START + 1.0, 1), (T_GOAL, 0)]                                      # 走る（ページの ギャロップ）
        mid = [(0.0, 0), (a1, 1), (T_START + 1.0, 0), (T_GOAL, 1), (d1, 0)]                    # 止まる・走りだすの とちゅうの ギャロップのコマ
        trn = [(0.0, 1), (a1, 0), (d1, 1)]                                                     # 止まる・立つ・走りだす
        css += (f'.nth{num}{{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none;will-change:transform;{anim(f"ntR{num}", LOOP)}}}'
                f'.ntj{num}{{position:absolute;left:0;top:0;width:390px;height:160px;{anim(f"ntJ{num}")}}}'
                f'.ntc{num},.ntu{num}{{position:absolute;left:{ax:g}px;top:{ay:g}px;width:{cw:g}px;height:{ch:g}px;overflow:hidden}}'
                f'.ntk{num}{{position:absolute;left:{tx:g}px;top:{ty:g}px;width:{tw:g}px;height:{th:g}px;overflow:hidden;{anim(f"ntK{num}", tf="step-end")}}}'
                f'.ntc{num}{{{anim(f"ntC{num}", tf="step-end")}}}.ntu{num}{{{anim(f"ntU{num}", tf="step-end")}}}'
                f'.nts{num},.ntv{num}{{width:{n * cw:g}px;height:{ch:g}px;background:url({blobs["h" + str(num)]}) 0 0/{n * cw:g}px {ch:g}px no-repeat;will-change:transform}}'
                f'.nts{num}{{animation:ntS{num} {GALLOP_S:g}s steps({n}) infinite}}.ntv{num}{{{anim(f"ntV{num}", tf="step-end")}}}'
                f'.ntq{num}{{width:{t["cols"] * tw:g}px;height:{t["rows"] * th:g}px;background:url({blobs["t" + str(num)]}) 0 0/{t["cols"] * tw:g}px {t["rows"] * th:g}px no-repeat;'
                f'will-change:transform;{anim(f"ntQ{num}", tf="step-end")}}}'
                f'@keyframes ntS{num}{{to{{transform:translateX(-{n * cw:g}px)}}}}'
                + keyframes(f'ntR{num}', races_kfs([horse_block(run, num, rc, nxt(k)) for k, rc in enumerate(races)]), lambda x: f'transform:translateX({x:.1f}px)', LOOP)
                + keyframes(f'ntJ{num}', sway_block(num), lambda x: f'transform:translateX({x:g}px)')
                + keyframes(f'ntC{num}', show_block(gal), vis_, step=True)
                + keyframes(f'ntU{num}', show_block(mid), vis_, step=True)
                + keyframes(f'ntK{num}', show_block(trn), vis_, step=True)
                + keyframes(f'ntV{num}', gallop_frames_block(tm, cw), lambda x: f'transform:translateX({x:g}px)', step=True)
                + keyframes(f'ntQ{num}', trans_frames_block(tm, t), lambda p: f'transform:translate({p[0]:g}px,{p[1]:g}px)', step=True))
    # 暗くなる幕・照明・「スタート！」
    DK = [(0.0, 1, None), (T_LIGHT + 0.3, 1, 'ease-out'), (T_LIGHT + 0.9, 0, None), (T_GOAL, 0, 'cubic-bezier(.42,0,.58,1)'), (T_GOAL + DARK_S, 1, None)]
    css += (f'.ntd{{position:absolute;inset:0;background:{DARK};pointer-events:none;{anim("ntD", twin="ntDV")}}}'
            + keyframes('ntD', DK, op_) + vis_twin('ntDV', DK))
    css += ('.ntl{position:absolute;width:84px;height:84px;margin:-42px 0 0 -42px;border-radius:50%;pointer-events:none;opacity:0;'
            'background:radial-gradient(circle,#FFFFFF 0,#F4F6FF 9%,rgba(176,196,255,.62) 24%,rgba(120,140,255,.18) 48%,rgba(120,140,255,0) 70%)}'
            '.ntl::before,.ntl::after{content:"";position:absolute;left:50%;top:50%;width:110px;height:2px;margin:-1px 0 0 -55px;'
            'background:linear-gradient(90deg,rgba(226,232,255,0),#E2E8FF 50%,rgba(226,232,255,0))}.ntl::after{transform:rotate(90deg) scaleX(.42)}')
    sc_ = lambda p: f'opacity:{p[0]};transform:scale({p[1]})'
    for i, (lx, ly) in enumerate(LAMPS):
        t0 = T_LIGHT + 0.15 * i
        LK = [(0.0, (0, .6), None), (t0, (0, .6), 'ease-out'), (t0 + 0.12, (1, 1), None), (T_LIGHT + 0.9, (1, 1), 'ease-in-out'),
              (T_LIGHT + 1.8, (0, 1), 'step-end'), (T_LIGHT + 1.9, (0, .6), None)]
        css += (f'.ntl{i}{{left:{lx}px;top:{ly}px;{anim(f"ntL{i}", twin=f"ntL{i}V")}}}'
                + keyframes(f'ntL{i}', LK, sc_) + vis_twin(f'ntL{i}V', LK, op=lambda v: v[0]))
    css += ('.ntst{position:absolute;left:0;right:0;top:33px;text-align:center;pointer-events:none;opacity:0;'
            'font:400 29px/1 "RocknRoll One",sans-serif;letter-spacing:.06em;color:#FFF6E0;'
            f'text-shadow:0 0 6px #FFB020,0 0 16px rgba(255,176,32,.8),0 2px 0 #7A3A00;{anim("ntSt", twin="ntStV")}}}'
            + keyframes('ntSt', SK := [(0.0, (0, .72), None), (T_START - 0.1, (0, .72), 'cubic-bezier(.2,.8,.3,1.25)'), (T_START + 0.2, (1, 1), None),
                                       (T_START + 0.9, (1, 1), 'ease-in'), (T_START + 1.35, (0, 1.06), 'step-end'), (T_START + 1.45, (0, .72), None)], sc_)
            + vis_twin('ntStV', SK, op=lambda v: v[0]))
    # 表彰（勝った馬の絵・1着のバッジ・紙ふぶき・カメラの光）：どの馬の表彰かは 1回り、出方は どのレースも同じ
    AW = [(0.0, 0, None), (T_AWARD, 0, 'ease-out'), (T_AWARD + 0.8, 1, None), (T_AWEND, 1, 'ease-in'), (T_BLACK, 0, None)]
    css += ('.ntaw{position:absolute;inset:0;pointer-events:none;opacity:0;' + anim('ntAw', twin='ntAwV') + '}'
            '.nta{position:absolute;inset:0;overflow:hidden;visibility:hidden}'
            '.ntz{position:absolute;inset:0;transform-origin:45% 75%;will-change:transform;' + anim('ntZ') + '}'
            '.ntbd{position:absolute;left:290px;top:8px;width:96px;height:126px;opacity:0;transform-origin:50% 38%;' + anim('ntBd') + '}.ntbd svg{display:block}'
            + keyframes('ntAw', AW, op_) + vis_twin('ntAwV', AW)
            + keyframes('ntZ', [(0.0, 1.0, None), (T_AWARD, 1.0, 'linear'), (T_BLACK, 1.045, 'step-end'), (T_RESET, 1.0, None)], lambda s_: f'transform:scale({s_})')
            + keyframes('ntBd', [(0.0, (0, .4), None), (T_AWARD + 0.55, (0, .4), 'cubic-bezier(.3,.7,.4,1.3)'), (T_AWARD + 1.0, (1, 1), None),
                                 (T_BLACK, (1, 1), 'step-end'), (T_RESET, (0, .4), None)], sc_))
    for num in DRAW:
        css += (f'.nta{num}{{{anim(f"ntA{num}", LOOP, "step-end")}}}.ntz{num}{{background:url({blobs["a" + str(num)]}) 0 0/390px 160px no-repeat}}'
                + keyframes(f'ntA{num}', races_kfs([[(0.0, 0, None), (T_AWARD - 0.5, int(rc['win'] == num), None)] for rc in races]), vis_, LOOP, step=True))
    css += ('.ntfx{position:absolute;inset:0;overflow:hidden;opacity:0;' + anim('ntFx') + '}'
            '.ntfx i{position:absolute;top:-14px;border-radius:1px;animation:ntCf var(--d) linear infinite;animation-delay:var(--dl);will-change:transform}'
            '@keyframes ntCf{from{transform:translate(0,-6px) rotate(0)}to{transform:translate(var(--dx),186px) rotate(var(--r))}}'
            '.ntfx b{position:absolute;width:24px;height:24px;margin:-12px 0 0 -12px;border-radius:50%;opacity:0;'
            'background:radial-gradient(circle,#FFFFFF 0,rgba(255,255,255,.92) 16%,rgba(255,240,214,.38) 38%,rgba(255,240,214,0) 70%);'
            'animation:ntFl var(--p) linear infinite;animation-delay:var(--dl)}'
            '@keyframes ntFl{0%,82%{opacity:0;transform:scale(.4)}86%{opacity:1;transform:scale(1)}94%{opacity:0;transform:scale(1.25)}100%{opacity:0;transform:scale(.4)}}'
            + keyframes('ntFx', [(0.0, 0, None), (T_AWARD + 0.4, 0, 'ease-out'), (T_AWARD + 1.2, 1, None), (T_AWEND - 0.2, 1, 'ease-in'), (T_BLACK - 0.3, 0, None)], op_))
    css += '@media (prefers-reduced-motion:reduce){.ntb,.ntg,.nth,.ntd,.ntl,.ntst,.ntaw{display:none}}'
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Night.dc.html）の上の絵を「動くナイター」に書きかえる（<img class="bnr"> か、前に入れた <div class="ntw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="ntw" .*?(?:<!--/ntw-->|<div class="ntb ntr"></div></div>)|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* ナイターの壁紙：3頭が走って順位が入れかわり、ゴール → 止まって暗く → 表彰 → また走りだす（night_wall.py） */\n{css}\n/* /ナイターの壁紙 */\n'
    if '/* ナイターの壁紙：' in page:
        page = re.sub(r'/\* ナイターの壁紙：.*?/\* /ナイターの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    if sys.argv[1] == '--plan':
        for k, rc in enumerate(races := plan()):
            base = k * BLOCK - OPEN_U
            page_t = lambda u: (base + u) % LOOP
            print(f'レース{k + 1}：照明 {page_t(T_LIGHT):6.1f}秒・走りだし {page_t(T_START):6.1f}秒（{"-".join(map(str, rc["start"]))}）')
            for t, o in rc['events']:
                print(f'   {page_t(t):6.2f}秒  {"-".join(map(str, o))}')
            print(f'   ★ゴール {page_t(T_GOAL):6.1f}秒 1着 {rc["win"]}番 → 表彰 {page_t(T_AWARD):.1f}〜{page_t(T_AWEND):.1f}秒')
        print('1着：', ' → '.join(f'{rc["win"]}番' for rc in races), f'（{LOOP:g}秒で1回り・ページを開いて {T_GOAL - OPEN_U:g}秒で1回目のゴール）')
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
