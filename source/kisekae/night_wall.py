"""ナイターの壁紙の動き（まさちゃんの指定「常に走ってる、背景が常に右から左に模様が動く同じ模様をリピートする、
   1秒〜5秒の間に3頭の順位が前後する、20秒に一回ゴールする馬はランダムにする」）：ページに入れる HTML と CSS
   絵は flat/night_run.py（くり返せる背景3まい・1頭ずつの ギャロップのシート）。キャンバスでは /_blob/<id>（night_blobs.json）
   - 背景は 右から左へ流れて、同じ模様がくり返す。遠いほど ゆっくり：空とスタンドと照明 FLOW['far'] 秒・奥の柵とダート FLOW['track'] 秒・
     手前の柵 FLOW['rail'] 秒で 1まいぶん（390px）
   - 3頭は いつも走っている（ギャロップ GALLOP_S 秒で1回・steps）。順位は 1〜5秒ごと（毎回ちがう）に となりどうしが入れかわる
     （追いぬく馬は前へ・ぬかれる馬は うしろへ、TRANS 秒で なめらかに）。3頭とも それぞれ 少し前後に ゆれる
   - 20秒に1回 ゴール：奥の柵に立つ ゴール板（白黒の市松もよう）が 右から流れてきて、1着の馬の鼻先を通る（板が ふわっと光る）。
     1着になる馬は レースごとに ばらばら（RACES 回で 3頭とも同じ回数・つづけて同じ馬はない）。RACES 回で1回り（CYCLE 秒）
   - いちばん下は いまの止まった絵（<img class="bnr">）。視差効果を減らす（prefers-reduced-motion）なら 動く絵を消して いまの絵だけ
   クラスの名前は nt…（ページの ほかの名前と ぶつからないように）
   python3 night_wall.py --judge <Judge_Night.dc.html> <night_blobs.json> <night_run.json>  → 判定画面の上の絵を「動くナイター」に書きかえる（何回やっても同じ）
   python3 night_wall.py --plan <night_run.json>                                         → レースの予定（順位の入れかわりと 1着）"""
import sys, os, re, json, math, random

W2, H2 = 390, 160
STATIC = '/_blob/5669e8b79972b750876e84c7eea2fb3f'        # いまの止まった絵（WebP）
ALT = '照明に照らされた夜のコースを走る3頭の馬と騎手のアニメ風イラスト（いつも走っていて景色が流れる・順位が入れかわり、20秒に1回ゴールする）'
FLOW = dict(far=24.0, track=3.2, rail=2.2)                # 1まいぶん（390px）流れる秒（手前の柵の支柱が 1秒に3本より少なく通る）
GALLOP_S = .5                                            # ギャロップ1回の秒
RACE_S = 20.0                                            # 1レースの秒（ゴールの間かく）
RACES = 6                                                # 1回りの レースの数
CYCLE = RACE_S * RACES
GOAL0 = 10.0                                             # 1回目の ゴール（ページを開いてから）
ORDER0 = (5, 7, 3)                                       # はじめの順位（いまの絵と同じ：5番が先頭・7番・3番）
# 順位ごとの 3頭の 鼻先の x（絵の画素・780のはば）。手前の大きな7番に 頭が かくれないように、順位の ならびごとに決めた
# （7番より うしろの馬は 7番のおしりより うしろ・ほかの馬の頭も 前の馬の体に かからない所。頭の見える割合は どれも 9割くらい以上）
LAYOUT = {(5, 3, 7): {5: 680, 3: 560, 7: 440}, (3, 5, 7): {5: 510, 3: 690, 7: 400},
          (5, 7, 3): {5: 700, 3: 350, 7: 620}, (3, 7, 5): {5: 330, 3: 700, 7: 620},
          (7, 5, 3): {5: 425, 3: 295, 7: 690}, (7, 3, 5): {5: 240, 3: 425, 7: 690}}
TRANS = (1.0, 1.8)                                       # 入れかわりの秒（動く はばが大きいほど ゆっくり）
GAP = (2.0, 4.8)                                         # つぎの入れかわりまで（秒）：1〜5秒の中で
CALM = 2.3                                               # ゴールの前は この秒のあいだ 入れかわらない（1着が 先頭のまま 板を通る）
SWAY = {5: (2.5, 3.0), 3: (3.0, 2.5), 7: (2.0, 2.0)}     # それぞれの 前後のゆれ（片道の秒・はば px）
SEED = 12
DRAW = (5, 3, 7)                                         # 重ねる順（奥 → 手前）
POST_FOOT = 100                                          # ゴール板の 柱の下のはしの y（画面の px・奥の柵の 白い横木の高さ）。板の絵は 高さ 78px（柱の下のはしが 絵の下のはし）


def winners(seed=SEED):
    """RACES 回の1着（3頭とも同じ回数・つづけて同じ馬はない・1回りの さいごと はじめも ちがう）"""
    rnd = random.Random(seed)
    while True:
        w = [5, 3, 7] * (RACES // 3)
        rnd.shuffle(w)
        if all(w[i] != w[(i + 1) % RACES] for i in range(RACES)) and not all(w[i] == w[(i + 3) % RACES] for i in range(RACES)):
            return w                                             # （3回ごとの くり返しの順も よける）


def inversions(order):
    """ORDER0 にもどすのに いる となりどうしの入れかえの回数"""
    pos = [ORDER0.index(v) for v in order]
    return sum(1 for a in range(3) for b in range(a + 1, 3) if pos[a] > pos[b])


def plan(seed=SEED):
    """レースの予定：(入れかわり [(時刻, 新しい順位)], 1着 [(ゴールの時刻, 馬)])。順位は 先頭から。1回り CYCLE 秒（くり返し）。
       入れかわりは 1回に となりどうし1組。間かくは 1〜5秒（1回りの つなぎ目も）・ゴールの前 CALM 秒は 入れかわらない・
       ゴールの時に その回の1着が先頭・1回りの さいごに ORDER0 にもどる（くり返しが つながる）"""
    rnd = random.Random(seed * 7 + 1)
    win = winners(seed)
    goals = [(GOAL0 + RACE_S * k, win[k]) for k in range(RACES)]
    for attempt in range(5000):
        times = []
        t = rnd.uniform(*GAP)
        while t < CYCLE - 0.6:
            for gt, _ in goals:
                if gt - CALM < t < gt + 0.6:                         # ゴールの前は入れかわらない：ゴールのあとへ
                    t = gt + rnd.uniform(0.6, 1.4)
            if t < CYCLE - 0.6:
                times.append(round(t, 2))
            t += rnd.uniform(*GAP)
        n = len(times)
        gaps = [(times[(k + 1) % n] - times[k]) % CYCLE for k in range(n)]
        if not all(1.0 <= g <= 5.0 for g in gaps):
            continue
        sol = []

        def dfs(i, order):
            lo = times[i - 1] if i else 0.0
            hi = times[i] if i < n else CYCLE
            for gt, gw in goals:                                     # このあいだの ゴール：1着が先頭か
                if lo < gt < hi and order[0] != gw:
                    return False
            if i == n:
                return tuple(order) == ORDER0
            left = n - i
            d = inversions(order)
            if d > left or (left - d) % 2:
                return False
            for gt, gw in goals:                                     # つぎの ゴールまでに 1着の馬を先頭へ上げられるか
                if gt > times[i]:
                    m = sum(1 for tt in times[i:] if tt < gt)
                    if order.index(gw) > m:
                        return False
                    break
            opts = [0, 1]
            rnd.shuffle(opts)
            for k in opts:
                o2 = list(order)
                o2[k], o2[k + 1] = o2[k + 1], o2[k]
                sol.append((times[i], tuple(o2)))
                if dfs(i + 1, o2):
                    return True
                sol.pop()
            return False
        if dfs(0, list(ORDER0)):
            return sol, goals
    raise SystemExit('plan not found')


def pos_x(run, num, order):
    """順位の ならび order の時の その馬の 横のずれ（画面の px）"""
    return (LAYOUT[tuple(order)][num] - run['horses'][str(num)]['nose']) / 2


def trans_s(dx):
    """横に dx（画面の px）動く 入れかわりの秒"""
    return min(TRANS[1], max(TRANS[0], 0.9 + abs(dx) / 130))


def kf_pct(t):
    return f'{100 * t / CYCLE:.3f}'.rstrip('0').rstrip('.') + '%'


def horse_keyframes(run, num, events):
    """順位の入れかわりで 前後する 横のずれ（1回り CYCLE 秒）"""
    order0 = events[-1][1]                                       # 0秒の順位＝1回りの さいごの順位（＝ORDER0）
    x = pos_x(run, num, order0)
    kfs = [(0.0, x, None)]
    for t, order in events:
        nx = pos_x(run, num, order)
        if abs(nx - x) < 1e-6:
            continue
        kfs.append((t, x, 'ease-in-out'))
        kfs.append((t + trans_s(nx - x), nx, None))
        assert kfs[-1][0] < CYCLE, 'a swap must end before the loop restarts'
        x = nx
    kfs.append((CYCLE, x, None))
    out = []
    for t, v, tf in kfs:
        f = f';animation-timing-function:{tf}' if tf else ''
        out.append(f'{kf_pct(t)}{{transform:translateX({v:.1f}px){f}}}')
    return ''.join(out)


def post_keyframes(run, goals, events):
    """ゴール板：奥の柵と同じ速さで 右から左へ。ゴールの時刻に 1着の鼻先を通る"""
    v = W2 / FLOW['track']
    off_r, off_l = W2 + 30, -40
    kfs = [(0.0, off_l, 'step-end')]
    for gt, gw in goals:
        prev = [e for e in events if e[0] <= gt]
        order = prev[-1][1] if prev else events[-1][1]
        xg = LAYOUT[tuple(order)][gw] / 2
        t_in = gt - (off_r - xg) / v
        t_out = gt + (xg - off_l) / v
        kfs.append((t_in, off_r, 'linear'))
        kfs.append((t_out, off_l, 'step-end'))
    kfs.append((CYCLE, off_l, None))
    kfs.sort(key=lambda k: k[0])
    return ''.join(f'{kf_pct(t)}{{transform:translateX({x:.1f}px)' + (f';animation-timing-function:{tf}' if tf else '') + '}' for t, x, tf in kfs)


def glow_keyframes(goals):
    """ゴールの時に 板が ふわっと光る（0.9秒）"""
    kfs = [(0.0, 0)]
    for gt, gw in goals:
        kfs += [(gt - 0.15, 0), (gt + 0.15, 1), (gt + 0.75, 0)]
    kfs.append((CYCLE, 0))
    return ''.join(f'{kf_pct(t)}{{opacity:{o}}}' for t, o in kfs)


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


def inline(blobs, run, alt=ALT, static=STATIC):
    """(html, css)。blobs：far・track・rail・h5・h3・h7 → '/_blob/<id>'。run：night_run.json"""
    events, goals = plan()
    hz = run['horses']
    bands = dict(far=('ntf', run['far']), track=('ntt', run['track']), rail=('ntr', run['rail']))
    html = (f'<div class="ntw" role="img" aria-label="{alt}"><img class="bnr" src="{static}" alt="">'
            f'<div class="ntb ntf"></div><div class="ntb ntt"></div>'
            f'<div class="ntg">{post_svg()}</div>')
    for num in DRAW:
        html += f'<div class="nth nth{num}"><div class="ntj ntj{num}"><div class="ntc ntc{num}"><div class="nts nts{num}"></div></div></div></div>'
    html += '<div class="ntb ntr"></div></div>'
    css = ('.ntw{position:relative;flex:none;width:390px;height:160px;overflow:hidden}'
           '.ntw .bnr{position:absolute;left:0;top:0;width:390px;height:160px}'
           '.ntb{position:absolute;left:0;width:780px;background-repeat:repeat-x;will-change:transform}')
    for name, (cls, (y0, y1)) in bands.items():
        h = (y1 - y0) / 2
        css += (f'.{cls}{{top:{y0 / 2:g}px;height:{h:g}px;background-image:url({blobs[name]});background-size:{W2}px {h:g}px;'
                f'animation:ntFlow {FLOW[name]:g}s linear infinite}}')
    css += f'@keyframes ntFlow{{to{{transform:translateX(-{W2}px)}}}}'
    # ゴール板（柱の下のはしが 奥の柵の上）
    css += (f'.ntg{{position:absolute;left:-14px;top:{POST_FOOT - 78}px;width:28px;height:78px;pointer-events:none;'
            f'animation:ntGo {CYCLE:g}s infinite}}.ntg .ntgs{{display:block;overflow:visible}}'
            f'.ntgl{{opacity:0;animation:ntGl {CYCLE:g}s linear infinite}}'
            f'@keyframes ntGo{{{post_keyframes(run, goals, events)}}}@keyframes ntGl{{{glow_keyframes(goals)}}}')
    for num in DRAW:
        r = hz[str(num)]
        cw, ch = r['cell'][0] / 2, r['cell'][1] / 2
        ax, ay = r['at'][0] / 2, r['at'][1] / 2
        n = r['frames']
        dur, amp = SWAY[num]
        css += (f'.nth{num}{{position:absolute;left:0;top:0;width:390px;height:160px;pointer-events:none;will-change:transform;'
                f'animation:ntR{num} {CYCLE:g}s linear infinite}}'
                f'.ntj{num}{{position:absolute;left:0;top:0;width:390px;height:160px;animation:ntJ{num} {dur:g}s ease-in-out infinite alternate}}'
                f'.ntc{num}{{position:absolute;left:{ax:g}px;top:{ay:g}px;width:{cw:g}px;height:{ch:g}px;overflow:hidden}}'
                f'.nts{num}{{width:{n * cw:g}px;height:{ch:g}px;background:url({blobs["h" + str(num)]}) 0 0/{n * cw:g}px {ch:g}px no-repeat;'
                f'animation:ntS{num} {GALLOP_S:g}s steps({n}) infinite;will-change:transform}}'
                f'@keyframes ntS{num}{{to{{transform:translateX(-{n * cw:g}px)}}}}'
                f'@keyframes ntJ{num}{{from{{transform:translateX(-{amp:g}px)}}to{{transform:translateX({amp:g}px)}}}}'
                f'@keyframes ntR{num}{{{horse_keyframes(run, num, events)}}}')
    css += '@media (prefers-reduced-motion:reduce){.ntb,.ntg,.nth{display:none}}'
    return html, css


def judge_inline(fn, blobs, run):
    """判定画面（Judge_Night.dc.html）の上の絵を「動くナイター」に書きかえる（<img class="bnr"> か、前に入れた <div class="ntw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(blobs, run)
    page, n = re.subn(r'<div class="ntw" .*?<div class="ntb ntr"></div></div>|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert n == 1, 'banner not found'
    block = f'/* ナイターの壁紙：3頭が走って順位が入れかわり、20秒に1回ゴール（night_wall.py） */\n{css}\n/* /ナイターの壁紙 */\n'
    if '/* ナイターの壁紙：' in page:
        page = re.sub(r'/\* ナイターの壁紙：.*?/\* /ナイターの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def load_blobs(fn):
    return {k: f'/_blob/{v}' for k, v in json.load(open(fn)).items()}


if __name__ == '__main__':
    if sys.argv[1] == '--plan':
        ev, gl = plan()
        for t, o in ev:
            g = [f'  ★ゴール {gt:.0f}秒 1着 {gw}番' for gt, gw in gl if 0 <= gt - t < 5 and not any(t < e[0] <= gt for e in ev)]
            print(f'{t:6.2f}秒  {"-".join(map(str, o))}' + ''.join(g))
        print('1着：', ' → '.join(f'{gw}番（{gt:.0f}秒）' for gt, gw in gl))
    else:
        i = sys.argv.index('--judge')
        judge_inline(sys.argv[i + 1], load_blobs(sys.argv[i + 2]), json.load(open(sys.argv[i + 3])))
