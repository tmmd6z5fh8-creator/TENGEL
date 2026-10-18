"""子供向けの壁紙の動き（まさちゃんの指定）：ページに入れる HTML と CSS
   「1秒〜3秒で、毛糸が左から右にころがっていき、ロボットは目で追って、馬も目で追って4秒で毛糸が止まり、馬が跳ねて喜ぶ。8秒に一回リピートする」
   - 絵は kids.py の部品（いつもの絵と同じ形・同じ場所）を べつべつの <svg> にして重ね、動く所だけを CSS で動かす。下から：
     下の絵（毛糸の編み目・布・雲・星）→ 毛糸玉と糸（枠の内がわだけ見える）→ 馬のかげ → 馬（目なし）とボタンの目 →
     枠・ロボットのかげ・ロボット（黒目なし）→ ロボットの黒目 → ハート
     （毛糸玉は 馬とロボットの うしろを通る＝いつもの絵と同じ重なり。どの部品も絵ごと動かすので、フェルトの もようは いっしょに動く）
   - 8秒で1回り（CYCLE）：
     0〜1秒 毛糸玉はまだ見えない（枠の左の外）→ 1〜3秒 左から右へ ころころ転がる（すべらない：進んだぶんだけ回る）→
     3〜4秒 だんだん ゆっくりになって、4秒で いつもの場所に止まる。ロボットの黒目と 馬のボタンの目は 1秒から 毛糸玉を追う
     （馬は 毛糸玉が頭の下を通る時に 少し前へ のぞきこむ）→
     4秒 馬が ぴょん・ぴょんと2回跳ねて喜ぶ（ちぢんで ふみこむ → 跳ぶ（頭が少し上がる）→ おりて ちぢむ。かげは上がると小さく・うすく。
     ハートが3つ ふわっと出て上がって消える）→ 7.5〜8秒 毛糸玉が ふわっと消えて、目が もとにもどる → くり返す
   - 視差効果を減らす（prefers-reduced-motion）なら動かさない（部品が いつもの場所にあるので、いつもの絵と同じ）
   クラスの名前は kd…
   python3 kids_wall.py --judge <Judge_Kids.dc.html>   → 判定画面の上の絵を書きかえる（何回やっても同じ）
   python3 kids_wall.py --plan                          → 何秒に どこにいるか（毛糸玉・目・馬）"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kids

ALT = '毛糸の編み目の背景に、ぬいぐるみの馬と手をふるロボット、毛糸玉のイラスト（毛糸玉が左から ころころ転がってきて、ロボットと馬が目で追い、止まると馬が跳ねて喜ぶ）'
CYCLE = 8.0
ROLL = (1.0, 3.0, 4.0)        # 転がりはじめ・ゆっくりになりはじめ・止まる（秒）
X0 = -12.0                    # 転がりはじめの 毛糸玉のまん中（枠の左の外）
SLOW = .2                     # 3〜4秒で進む道のりの わりあい（なめらかに ゆっくりになる：速さがそろう＝ 1秒あたりの道のりの半分）
FADE = (7.5, 8.0)             # 次の回のために 毛糸玉が ふわっと消える
LOOK = .2                     # 毛糸玉が出てから 目が追いつくまでの秒
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
EASE = {'linear': 'linear', 'quad-out': 'cubic-bezier(.3333,.6667,.6667,1)', 'quad-in': 'cubic-bezier(.3333,0,.6667,.3333)', 'ease-in-out': 'ease-in-out',
        'ease-in': 'ease-in', 'ease-out': 'ease-out'}
IDS = (('knit', 'kdKnit'), ('felt', 'kdFelt'))


def pct(t):
    s = f'{t / CYCLE * 100:.4f}'.rstrip('0').rstrip('.')
    return s + '%'


def num(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def ball_x(t):
    """毛糸玉のまん中の x（t 秒・止まっている所は いつもの場所）"""
    xe = kids.YARN_BALL[0]
    x1 = X0 + (1 - SLOW) * (xe - X0)
    t0, t1, t2 = ROLL
    if t <= t0:
        return X0
    if t <= t1:
        return X0 + (x1 - X0) * (t - t0) / (t1 - t0)
    if t <= t2:
        s = (t - t1) / (t2 - t1)
        return x1 + (xe - x1) * (2 * s - s * s)
    return xe


def page_xy(p, at):
    x, y, s = at
    return x + p[0] * s, y + p[1] * s


def look(eye, t, r, back=None):
    """目のまん中 eye（絵の座標）から 毛糸玉を見る向き × r（絵の座標）"""
    bx, by = ball_x(t), kids.YARN_BALL[1]
    dx, dy = bx - eye[0], by - eye[1]
    n = math.hypot(dx, dy)
    ox, oy = dx / n * r, dy / n * r
    if back is not None:
        ox = max(ox, -back)
    return ox, oy


def gaze(eye, r, base=(0, 0), back=None):
    """目の動き（translate の keyframes）：1秒まで いつもの所 → 毛糸玉を追う → 止まったら そのまま見る → 7.5〜8秒で もどる"""
    t0, _, t2 = ROLL
    ks = [(0, (0, 0), 'linear'), (t0, (0, 0), 'ease-out')]
    t = t0 + LOOK
    while t <= t2 + 1e-9:
        ox, oy = look(eye, t, r, back)
        ks.append((t, (ox - base[0], oy - base[1]), 'linear'))
        t = round(t + .1, 6)
    ks.append((FADE[0], ks[-1][1], 'ease-in-out'))
    ks.append((CYCLE, (0, 0), 'linear'))
    return ks


def kf_translate(name, ks):
    out = []
    for t, (x, y), e in ks:
        out.append(f'{pct(t)}{{transform:translate({num(x)}px,{num(y)}px);animation-timing-function:{EASE.get(e, e)}}}')
    return f'@keyframes {name}{{' + ''.join(out) + '}'


def roll_css():
    """毛糸玉：左右に動く（.kdy）と 回る（.kdr）は 同じ秒・同じ動きなので、進んだぶんだけ回る（すべらない）"""
    xe, _, r = kids.YARN_BALL
    t0, t1, t2 = ROLL
    pts = [(0, X0), (t0, X0), (t1, ball_x(t1)), (t2, xe), (FADE[0], xe), (CYCLE, xe)]
    eases = ['linear', 'linear', 'quad-out', 'linear', 'ease-in-out', 'linear']
    mv, sp = [], []
    for (t, x), e in zip(pts, eases):
        op = 0 if t >= CYCLE else 1
        mv.append(f'{pct(t)}{{transform:translateX({num(x - xe)}px);opacity:{op};animation-timing-function:{EASE[e]}}}')
        sp.append(f'{pct(t)}{{transform:rotate({num(math.degrees((x - xe) / r), 1)}deg);animation-timing-function:{EASE[e]}}}')
    return '@keyframes kdRoll{' + ''.join(mv) + '}@keyframes kdSpin{' + ''.join(sp) + '}'


def hop_css():
    """馬が跳ねる（.kdh）と かげ（.kdhs）"""
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
    hx, hy = page_xy(kids.HORSE_EYE, kids.HORSE_AT)
    eyes = [page_xy((ex, 39), kids.ROBOT_AT) for ex in kids.ROBOT_EYES]
    pupils = [page_xy((ex + 1, 40), kids.ROBOT_AT) for ex in kids.ROBOT_EYES]
    s = kids.ROBOT_AT[2]
    full = (0, 0, W, H)
    BALL_B = (xe - 18, ye - 18, 36, 36)
    THREAD_B = (254, 128, 90, 28)
    SHADOW_B = (78, 139, 100, 14)
    EYE_B = (round(hx) - 8, round(hy) - 8, 16, 16)
    PUP_B = [(round(px) - 6, round(py) - 6, 13, 13) for px, py in pupils]
    html = (f'<div class="bnr kdw" role="img" aria-label="{alt}">'
            + box_svg(f'<defs>{p["defs"]}</defs>{p["bg"]}', full, 'kdb')
            + '<i class="kdc"><i class="kdy"><i class="kdr">' + box_svg(p['ball'], BALL_B) + '</i>'
            + box_svg(p['thread'], THREAD_B, 'kdt') + '</i></i>'
            + box_svg(p['shadow_h'], SHADOW_B, 'kdhs')
            + '<i class="kdh"><i class="kdl">' + box_svg(p['horse'], full) + '<i class="kde">' + box_svg(p['eye'], EYE_B) + '</i></i></i>'
            + box_svg(p['frame'] + p['shadow_r'] + p['robot'], full, 'kdo')
            + ''.join(f'<i class="kdp kdp{k + 1}">' + box_svg(p['pupils'][k], PUP_B[k]) + '</i>' for k in range(2))
            + ''.join(f'<i class="kdj kdj{k + 1}">' + box_svg(kids.stitched(kids.heart(0, 0, sz), col, 1.1, kids.heart(0, 0, sz * .7)), (-sz * 1.4, -sz * 1.4, sz * 2.8, sz * 2.8)) + '</i>'
                      for k, (t0, (cx, cy), sz, col) in enumerate(HEARTS))
            + '</div>')
    pos = lambda b: f'left:{num(b[0])}px;top:{num(b[1])}px;width:{num(b[2])}px;height:{num(b[3])}px'
    css = ('.kdw{position:relative;overflow:hidden;isolation:isolate}'
           '.kdw svg,.kdw i{position:absolute;display:block;font-style:normal}'
           '.kdw i svg{left:0;top:0}'
           f'.kdw .kdb,.kdw .kdo{{left:0;top:0}}'
           f'.kdw .kdc{{left:0;top:0;width:{W}px;height:{H}px;overflow:hidden;clip-path:inset(6px round 12px)}}'
           f'.kdw .kdy{{left:0;top:0;width:{W}px;height:{H}px;animation:kdRoll {CYCLE:g}s linear infinite}}'
           f'.kdw .kdt{{{pos(THREAD_B)}}}'
           f'.kdw .kdr{{{pos(BALL_B)};transform-origin:18px 18px;animation:kdSpin {CYCLE:g}s linear infinite}}'
           f'.kdw .kdhs{{{pos(SHADOW_B)};transform-origin:50px 7px;animation:kdHs {CYCLE:g}s linear infinite}}'
           f'.kdw .kdh{{left:0;top:0;width:{W}px;height:{H}px;transform-origin:{num(HOP_O[0])}px {num(HOP_O[1])}px;animation:kdHop {CYCLE:g}s linear infinite}}'
           f'.kdw .kdl{{left:0;top:0;width:{W}px;height:{H}px;transform-origin:{num(LEAN_O[0])}px {num(LEAN_O[1])}px;animation:kdLean {CYCLE:g}s linear infinite}}'
           f'.kdw .kde{{{pos(EYE_B)};animation:kdEye {CYCLE:g}s linear infinite}}'
           + ''.join(f'.kdw .kdp{k + 1}{{{pos(PUP_B[k])};animation:kdPup{k + 1} {CYCLE:g}s linear infinite}}' for k in range(2))
           + ''.join(f'.kdw .kdj{k + 1}{{left:{num(cx - sz * 1.4)}px;top:{num(cy - sz * 1.4)}px;width:{num(sz * 2.8)}px;height:{num(sz * 2.8)}px;opacity:0;animation:kdJoy{k + 1} {CYCLE:g}s linear infinite}}'
                     for k, (t0, (cx, cy), sz, col) in enumerate(HEARTS))
           + roll_css() + hop_css()
           + kf_translate('kdEye', [(t, (x * kids.HORSE_AT[2], y * kids.HORSE_AT[2]), e) for t, (x, y), e in gaze((hx, hy), EYE_H, back=EYE_H_BACK)])
           + ''.join(kf_translate(f'kdPup{k + 1}', [(t, (x * s, y * s), e) for t, (x, y), e in gaze(eyes[k], EYE_R, base=(1, 1))]) for k in range(2))
           + ''.join(heart_css(k + 1, t0) for k, (t0, *_rest) in enumerate(HEARTS))
           + '@media (prefers-reduced-motion:reduce){.kdw *{animation:none!important}}')
    return html, css


def judge_inline(fn, alt=ALT):
    """判定画面（Judge_Kids.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="bnr kdw">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(alt)
    page, k = re.subn(r'<div class="bnr kdw" .*?</div>(?=\s*<main)|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* 子供向けの壁紙：毛糸玉が転がって、ロボットと馬が目で追い、止まると馬が跳ねて喜ぶ（kids_wall.py） */\n{css}\n/* /子供向けの壁紙 */\n'
    if '/* 子供向けの壁紙：' in page:
        page = re.sub(r'/\* 子供向けの壁紙：.*?/\* /子供向けの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


def plan():
    p = {}
    kids.banner(p)
    hx, hy = page_xy(kids.HORSE_EYE, kids.HORSE_AT)
    for t in [0, .5, 1, 1.2, 1.5, 2, 2.5, 3, 3.5, 4, 5, 7.5, 8]:
        print(f'{t:4.1f}秒  毛糸玉 x={ball_x(t):6.1f}  馬の目 {tuple(round(v, 2) for v in look((hx, hy), t, EYE_H, EYE_H_BACK))}')


if __name__ == '__main__':
    if '--plan' in sys.argv:
        plan()
    else:
        judge_inline(sys.argv[sys.argv.index('--judge') + 1])
