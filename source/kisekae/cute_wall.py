"""かわいいの壁紙の動き（まさちゃんの指定）：ページに入れる HTML と CSS
   「小さいハートと大きなハートとリボンは常に動いている、1秒〜5秒で、大きなハートと馬がお互いに近づき、馬とハートが当たる位置で馬が飛び跳ねて喜ぶ、
    8秒に一回リピートする」
   - 絵は cute.py の部品（いつもの絵と同じ形・同じ場所）を べつべつの <svg> にして重ね、動く所だけを CSS で動かす。下から：
     下の絵（水玉・レース・キラキラ）→ 大きいハート（光つき）→ 小さいハート7つ → 右上のリボン → ポニーのかげ → ポニー → よろこびのハート
   - いつも動いている（8秒で わりきれる秒で くり返す）：小さいハートは ふわふわ上下に ゆれる（それぞれ ちがう速さ）・
     大きいハートは どきどき（2回ずつ ふくらむ 1.6秒）と ふわふわ（4秒）・リボンは 結び目を中心に ゆらゆら（2秒）
   - 8秒で1回り（CYCLE）：0〜1秒 いつもの場所 → 1〜5秒 ポニーは ぴょこぴょこ はねながら右へ（MEET の pony）、大きいハートは ふわっと左へ（MEET の heart）→
     5秒 ポニーの鼻と ハートが ちょうど当たる（ハートは むにゅっと へこんで ぽよんと ふくらむ）→ その場所で ポニーが ぴょーん・ぴょんと飛び跳ねて喜ぶ
     （ちぢんで ふみこむ → 跳ぶ（頭が上がる）→ おりて ちぢむ・かげは上がると小さく うすく・ハートが3つ ふわっと出る）→
     6.4〜7.9秒 ポニーは ぴょこぴょこ もとの場所へ、ハートも ふわっと もどる → くり返す
   - 視差効果を減らす（prefers-reduced-motion）なら動かさない（部品が いつもの場所にあるので、いつもの絵と同じ）
   クラスの名前は cw…
   python3 cute_wall.py --judge <Judge_Cute.dc.html>   → 判定画面の上の絵を書きかえる（何回やっても同じ）"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cute

ALT = 'ピンクの水玉にハートとリボン、リボンをつけた目の大きい白いポニーのイラスト（ハートとリボンがゆれて、大きいハートとポニーが近づき、当たるとポニーが飛び跳ねて喜ぶ）'
CYCLE = 8.0
GO, MEET, BACK, HOME = 1.0, 5.0, 6.4, 7.9      # 近づきはじめ・当たる・もどりはじめ・もどる
# 当たる所：いつもの絵で ポニーの鼻と大きいハートは よこに106px はなれている（いちばん近い高さ）。ポニーが48・ハートが60 近づいて ちょうど当たる
MOVE = dict(pony=48, heart=60)
HOP_O = (124, 141)            # ポニーが はねる時の中心（足もと）
STEP = (.4, 3.5, -2)          # ぴょこぴょこ：1回の秒・高さ・かたむき（近づく時は 10回、もどる時は 4回）
# 飛び跳ねて喜ぶ：(秒, 上へ, よこ・たての のび, かたむき, 次までの動き)
JOY = [(5.00, 0, 1, 1, 0, 'quad-out'), (5.10, 0, 1.07, .9, 0, 'quad-out'), (5.40, 20, .98, 1.02, -6, 'quad-in'),
       (5.66, 0, .98, 1.03, 2, 'quad-out'), (5.74, 0, 1.07, .9, 0, 'quad-out'), (5.98, 11, .99, 1.01, -4, 'quad-in'),
       (6.18, 0, .99, 1.02, 1, 'quad-out'), (6.26, 0, 1.04, .95, 0, 'ease-in-out'), (6.40, 0, 1, 1, 0, 'linear')]
# ハートが当たった時：(秒, よこ, たて) の のび（むにゅっ → ぽよん）
BOING = [(5.00, 1, 1, 'quad-out'), (5.08, .9, 1.07, 'ease-out'), (5.22, 1.14, 1.14, 'ease-in-out'), (5.40, .96, .96, 'ease-in-out'),
         (5.56, 1.06, 1.06, 'ease-in-out'), (5.72, 1, 1, 'linear')]
# 小さいハートの ふわふわ：(秒, 上下, かたむき, ずらす秒)。秒は 8秒で わりきれる
FLOAT = [(2.0, 4, 8, 0), (2.6667, 3, 10, -1.1), (4.0, 3.5, 7, -2.3), (1.6, 3, 9, -.5), (2.0, 3.5, 8, -1.3), (2.6667, 3, 12, -.4), (4.0, 3, 9, -3.1)]
# よろこびのハート：(出る秒, まん中, 大きさ)
JOY_HEARTS = [(5.30, (236, 32), 7.4), (5.42, (257, 22), 6.2), (5.92, (215, 20), 6.6)]
EASE = {'linear': 'linear', 'quad-out': 'cubic-bezier(.3333,.6667,.6667,1)', 'quad-in': 'cubic-bezier(.3333,0,.6667,.3333)',
        'ease-in-out': 'ease-in-out', 'ease-in': 'ease-in', 'ease-out': 'ease-out'}
IDS = (('dots', 'cwDots'), ('pk', 'cwPk'))


def pct(t):
    s = f'{t / CYCLE * 100:.4f}'.rstrip('0').rstrip('.')
    return s + '%'


def num(v, nd=2):
    s = f'{v:.{nd}f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def fix_ids(s):
    for a, b in IDS:
        s = s.replace(f'id="{a}"', f'id="{b}"').replace(f'url(#{a})', f'url(#{b})')
    return s


def box_svg(inner, box, cls=None):
    x, y, w, h = box
    c = f' class="{cls}"' if cls else ''
    return f'<svg{c} viewBox="{num(x)} {num(y)} {num(w)} {num(h)}" width="{num(w)}" height="{num(h)}">{fix_ids(inner)}</svg>'


def steps(t0, t1, n, h, rot):
    """ぴょこぴょこ n 回（t0〜t1）：(秒, 上へ, よこ, たて, かたむき, 次までの動き)"""
    out = []
    d = (t1 - t0) / n
    for k in range(n):
        a = t0 + k * d
        out += [(a, 0, 1, 1, 0, 'quad-out'), (a + d * .45, h, 1, 1, rot, 'quad-in')]
    return out


def pony_css():
    """ポニーの 左右（.cwx）・はねる（.cwj）・かげ（.cws）"""
    dp = MOVE['pony']
    mv = [(0, 0, 'linear'), (GO, 0, 'linear'), (MEET, dp, 'linear'), (BACK, dp, 'linear'), (HOME, 0, 'linear'), (CYCLE, 0, 'linear')]
    x = '@keyframes cwPx{' + ''.join(f'{pct(t)}{{transform:translateX({num(v)}px);animation-timing-function:{EASE[e]}}}' for t, v, e in mv) + '}'
    per, h, rot = STEP
    ks = ([(0, 0, 1, 1, 0, 'linear')] + steps(GO, MEET, round((MEET - GO) / per), h, rot) + JOY
          + steps(BACK, HOME, 4, h * .85, rot) + [(HOME, 0, 1, 1, 0, 'linear'), (CYCLE, 0, 1, 1, 0, 'linear')])
    hmax = max(k[1] for k in ks)
    jump = ''.join(f'{pct(t)}{{transform:translateY({num(-hh)}px) rotate({num(r)}deg) scale({num(sx, 3)},{num(sy, 3)});animation-timing-function:{EASE[e]}}}'
                   for t, hh, sx, sy, r, e in ks)
    sh = ''.join(f'{pct(t)}{{transform:scale({num(1 - .3 * hh / hmax, 3)});opacity:{num(1 - .5 * hh / hmax, 3)};animation-timing-function:{EASE[e]}}}'
                 for t, hh, sx, sy, r, e in ks)
    return x + '@keyframes cwPj{' + jump + '}@keyframes cwPs{' + sh + '}'


def heart_css():
    """大きいハートの 左右（.cwh）・当たった時（.cwk）・ふわふわ（.cwf）・どきどき（.cwd）"""
    dh = MOVE['heart']
    mv = [(0, 0, 'linear'), (GO, 0, 'ease-in-out'), (MEET, -dh, 'linear'), (BACK, -dh, 'ease-in-out'), (HOME, 0, 'linear'), (CYCLE, 0, 'linear')]
    x = '@keyframes cwHx{' + ''.join(f'{pct(t)}{{transform:translateX({num(v)}px);animation-timing-function:{EASE[e]}}}' for t, v, e in mv) + '}'
    bo = [(0, 1, 1, 'linear')] + BOING + [(CYCLE, 1, 1, 'linear')]
    k = '@keyframes cwHk{' + ''.join(f'{pct(t)}{{transform:scale({num(sx, 3)},{num(sy, 3)});animation-timing-function:{EASE[e]}}}' for t, sx, sy, e in bo) + '}'
    return (x + k + '@keyframes cwHf{0%,100%{transform:translateY(0) rotate(-3deg)}50%{transform:translateY(-3px) rotate(3deg)}}'
            '@keyframes cwHd{0%,36%,100%{transform:scale(1)}8%{transform:scale(1.08)}16%{transform:scale(1)}26%{transform:scale(1.05)}}')


def joy_css(k, t0):
    ks = [(0, 0, .3, -10, 0, 'linear'), (t0, 0, .3, -10, 0, 'quad-out'), (t0 + .14, -3, 1.15, -6, 1, 'ease-in-out'),
          (t0 + .26, -5, 1, -2, 1, 'linear'), (t0 + .85, -12, 1, 8, 1, 'ease-in'), (t0 + 1.15, -16, .9, 10, 0, 'linear'), (CYCLE, -16, .9, 10, 0, 'linear')]
    out = ''.join(f'{pct(t)}{{transform:translateY({num(y)}px) rotate({num(r)}deg) scale({num(s, 3)});opacity:{num(o)};animation-timing-function:{EASE[e]}}}'
                  for t, y, s, r, o, e in ks)
    return f'@keyframes cwJoy{k}{{{out}}}'


def ibox(x0, y0, x1, y1):
    """画素の さかい目に そろえた箱（はしが半端だと、重ねた絵が いつもの絵と少しずれる）"""
    a, b = math.floor(x0), math.floor(y0)
    return (a, b, math.ceil(x1) - a, math.ceil(y1) - b)


def heart_box(cx, cy, s, pad=1.6):
    return ibox(cx - s * 1.1 - pad, cy - s * 1.1 - pad, cx + s * 1.1 + pad, cy + s * 1.05 + pad)


def inline(alt=ALT):
    """(html, css)。html は <div class="bnr cww">（判定画面の <img class="bnr"> と入れかえる）"""
    p = {}
    cute.banner(p)
    W, H = p['size']
    full = (0, 0, W, H)
    bx, by, bs = cute.BIG_BOW
    big = cute.HEARTS[0]
    BIG_B = heart_box(big[0], big[1], big[2], 4)
    BOW_B = ibox(bx - 28 * bs, by - 13 * bs, bx + 28 * bs, by + 29 * bs)
    small = cute.HEARTS[1:]
    SB = [heart_box(cx, cy, s) for cx, cy, s, c, o in small]
    SHADOW_B = (80, 139, 96, 14)
    pos = lambda b: f'left:{num(b[0])}px;top:{num(b[1])}px;width:{num(b[2])}px;height:{num(b[3])}px'
    org = lambda b, x, y: f'transform-origin:{num(x - b[0])}px {num(y - b[1])}px'
    html = (f'<div class="bnr cww" role="img" aria-label="{alt}">'
            + box_svg(f'<defs>{p["defs"]}</defs>{p["bg"]}{p["sparkles"]}', full, 'cwb')
            + '<i class="cwh"><i class="cwk"><i class="cwf"><i class="cwd">' + box_svg(p['hearts'][0] + p['shine'], BIG_B) + '</i></i></i></i>'
            + ''.join(f'<i class="cwz cwz{k + 1}">' + box_svg(p['hearts'][k + 1], SB[k]) + '</i>' for k in range(len(small)))
            + '<i class="cwr">' + box_svg(p['bow'], BOW_B) + '</i>'
            + '<i class="cwx"><i class="cws">' + box_svg(p['shadow'], SHADOW_B) + '</i><i class="cwj">' + box_svg(p['pony'], full) + '</i></i>'
            + ''.join(f'<i class="cwy cwy{k + 1}">' + box_svg(cute.path(cute.heart(0, 0, s), fill='#FF6FA8', stroke='#FFFFFF', stroke_width='1.4'), heart_box(0, 0, s)) + '</i>'
                      for k, (t0, (cx, cy), s) in enumerate(JOY_HEARTS))
            + '</div>')
    css = ('.cww{position:relative;overflow:hidden;isolation:isolate}'
           '.cww svg,.cww i{position:absolute;display:block;font-style:normal}'
           '.cww i svg{left:0;top:0}'
           '.cww .cwb{left:0;top:0}'
           f'.cww .cwh,.cww .cwk,.cww .cwf,.cww .cwd{{{pos(BIG_B)}}}'
           '.cww .cwk,.cww .cwf,.cww .cwd{left:0;top:0}'
           f'.cww .cwh{{animation:cwHx {CYCLE:g}s linear infinite}}'
           f'.cww .cwk{{{org(BIG_B, big[0], big[1])};animation:cwHk {CYCLE:g}s linear infinite}}'
           f'.cww .cwf{{{org(BIG_B, big[0], big[1])};animation:cwHf 4s ease-in-out infinite}}'
           f'.cww .cwd{{{org(BIG_B, big[0], big[1] + 4)};animation:cwHd 1.6s linear infinite}}'
           + ''.join(f'.cww .cwz{k + 1}{{{pos(SB[k])};{org(SB[k], small[k][0], small[k][1])};animation:cwZ{k + 1} {FLOAT[k][0]:g}s ease-in-out {FLOAT[k][3]:g}s infinite}}'
                     f'@keyframes cwZ{k + 1}{{0%,100%{{transform:translateY(0) rotate({num(-FLOAT[k][2])}deg)}}50%{{transform:translateY({num(-FLOAT[k][1])}px) rotate({num(FLOAT[k][2])}deg)}}}}'
                     for k in range(len(small)))
           + f'.cww .cwr{{{pos(BOW_B)};{org(BOW_B, bx, by)};animation:cwR 2s ease-in-out infinite}}'
           '@keyframes cwR{0%,100%{transform:rotate(-6deg) translateY(0)}50%{transform:rotate(6deg) translateY(-1.5px)}}'
           f'.cww .cwx{{left:0;top:0;width:{W}px;height:{H}px;animation:cwPx {CYCLE:g}s linear infinite}}'
           f'.cww .cws{{{pos(SHADOW_B)};transform-origin:48px 7px;animation:cwPs {CYCLE:g}s linear infinite}}'
           f'.cww .cwj{{left:0;top:0;width:{W}px;height:{H}px;transform-origin:{num(HOP_O[0])}px {num(HOP_O[1])}px;animation:cwPj {CYCLE:g}s linear infinite}}'
           + ''.join(f'.cww .cwy{k + 1}{{{pos((cx + b[0], cy + b[1], b[2], b[3]))};opacity:0;animation:cwJoy{k + 1} {CYCLE:g}s linear infinite}}'
                     for k, (t0, (cx, cy), s) in enumerate(JOY_HEARTS) for b in [heart_box(0, 0, s)])
           + pony_css() + heart_css() + ''.join(joy_css(k + 1, t0) for k, (t0, *_r) in enumerate(JOY_HEARTS))
           + '@media (prefers-reduced-motion:reduce){.cww *{animation:none!important}}')
    return html, css


def judge_inline(fn, alt=ALT):
    """判定画面（Judge_Cute.dc.html）の上の絵を書きかえる（<img class="bnr"> か、前に入れた <div class="bnr cww">）。CSS は <style> の最後（印のあいだ）"""
    page = open(fn, encoding='utf-8').read()
    html, css = inline(alt)
    page, k = re.subn(r'<div class="bnr cww" .*?</div>(?=\s*<main)|<img class="bnr" [^>]*>', lambda _: html, page, count=1, flags=re.S)
    assert k == 1, 'banner not found'
    block = f'/* かわいいの壁紙：ハートとリボンがゆれて、大きいハートとポニーが近づき、当たるとポニーが飛び跳ねて喜ぶ（cute_wall.py） */\n{css}\n/* /かわいいの壁紙 */\n'
    if '/* かわいいの壁紙：' in page:
        page = re.sub(r'/\* かわいいの壁紙：.*?/\* /かわいいの壁紙 \*/\n', lambda _: block, page, flags=re.S)
    else:
        page = page.replace('</style>', block + '</style>', 1)
    open(fn, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    judge_inline(sys.argv[sys.argv.index('--judge') + 1])
