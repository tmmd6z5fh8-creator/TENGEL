"""壁紙パック ④パドック（まさちゃんの 指定「馬がパドックを歩きまわる」）
   上の絵：スタンドから 見た パドック。手前の 道を 右へ 3頭（ゼッケン 2・5・7）、おくの 道を 左へ 3頭（1・4・8・小さく）が 歩く
     （いままでと 同じ 馬・常歩の コマ：pack/make/paddock_art.py）。まん中に 芝生と 花だん、白い さく、うしろに お客さんの スタンドと 木、上に 小さな 旗の ひも。
   動き：馬は いつも 歩いて 回る（コマを めくりながら 横へ：地面に ついた ひづめが すべらない はやさ）・手前と おくは 反対へ・旗の ひもが ゆれる・
     雲が ゆっくり 流れる"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'paddock'
CYCLE = 1.25       # 歩く 1回りの 秒（paddock_art.CYCLE と 同じ）
NEAR = ('n2', 'n5', 'n7')
FAR = ('f1', 'f4', 'f8')
FAR_K = 1.0        # おくの 馬の シートは はじめから 小さく 描いて いる（そのまま）
GREEN = dict(d='#2E5E34', m='#3F7A44', l='#5E9A58', ll='#8CC07A')
RAIL = '#F6F4EE'


# ---------------------------------------------------------------- 絵
def back_svg():
    """うしろ：空・木・お客さんの スタンド（小さな 色の つぶ）・おくの 外の さく・おくの 道"""
    defs = ("<linearGradient id='s' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#9ED2F0'/><stop offset='1' stop-color='#DDF0F8'/></linearGradient>"
            "<linearGradient id='p' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#D9C08A'/><stop offset='1' stop-color='#E8D3A0'/></linearGradient>")
    o = f"<rect width='{W}' height='60' fill='url(#s)'/>"
    R = rnd(7)
    # 木（まるい しげみ）
    for i in range(16):
        x = i * 26 + R.uniform(-6, 6)
        r = R.uniform(14, 20)
        o += f"<circle cx='{f(x)}' cy='{f(30 + R.uniform(-3, 4))}' r='{f(r)}' fill='{GREEN['d']}'/>"
    for i in range(16):
        x = i * 26 + 10 + R.uniform(-6, 6)
        r = R.uniform(10, 15)
        o += f"<circle cx='{f(x)}' cy='{f(27 + R.uniform(-3, 3))}' r='{f(r)}' fill='{GREEN['m']}'/><circle cx='{f(x - r * .3)}' cy='{f(23 + R.uniform(-2, 2))}' r='{f(r * .55)}' fill='{GREEN['l']}' opacity='.7'/>"
    # スタンド（3だん・お客さん）
    o += "<rect x='0' y='36' width='390' height='26' fill='#C9CDD2'/>"
    for k, y in enumerate((38, 45, 52)):
        o += f"<rect x='0' y='{y + 6}' width='390' height='1.2' fill='#A9AEB6'/>"
        for i in range(70):
            x = i * 5.6 + R.uniform(-1.2, 1.2) + (k % 2) * 2.8
            c = R.choice(('#E8574A', '#3E6FC2', '#F2C14E', '#FFFFFF', '#5A4A42', '#2E8A5A', '#E88AB0', '#3A3A44', '#F0E0C8'))
            o += f"<rect x='{f(x - 1.7)}' y='{f(y + 2)}' width='3.4' height='4' rx='1.2' fill='{c}'/><circle cx='{f(x)}' cy='{f(y + 1)}' r='1.5' fill='{R.choice(('#2A1E18', '#4A3A30', '#E8D2B8', '#1E1E22'))}'/>"
    o += "<rect x='0' y='60' width='390' height='3' fill='#9A9EA6'/>"
    # おくの 外の さく
    o += f"<rect x='0' y='60' width='390' height='44' fill='url(#p)'/>"
    o += f"<rect x='0' y='60' width='390' height='2' fill='{RAIL}'/><rect x='0' y='65' width='390' height='1.6' fill='{RAIL}'/>"
    for i in range(27):
        o += f"<rect x='{f(i * 15 + 2)}' y='60' width='1.6' height='7' fill='{RAIL}'/>"
    # 道の ひづめの あと（うすい）
    for i in range(40):
        x, y = R.uniform(0, W), R.uniform(70, 97)
        o += f"<ellipse cx='{f(x)}' cy='{f(y)}' rx='1.6' ry='.8' fill='#B89A64' opacity='.5'/>"
    return doc(W, H, o, defs=defs)


def infield_svg():
    """おくの 道の 前の 低い 生け垣と 花・まん中の 芝生（しま）・花だん・手前の 内の さく。おくの 馬の ひづめの あたりだけ 少し かくす"""
    o = ''
    for i in range(44):
        x = i * 9
        o += f"<circle cx='{x}' cy='101' r='4.4' fill='{GREEN['m']}'/>"
    for i in range(44):
        x = i * 9 + 4.5
        o += f"<circle cx='{x}' cy='99.4' r='3.2' fill='{GREEN['l']}'/>"
    R = rnd(4)
    for i in range(46):
        x = R.uniform(0, W)
        o += f"<circle cx='{f(x)}' cy='{f(R.uniform(97, 102))}' r='1.1' fill='{R.choice(('#FFFFFF', '#F2C14E', '#E8574A', '#F59ABE'))}'/>"
    # 芝生（しま）
    o += "<rect x='0' y='103' width='390' height='16' fill='#6DAA5A'/>"
    for i in range(14):
        o += f"<path d='M{i * 30} 103 h15 l-4 16 h-15 Z' fill='#7DBA66'/>"
    # 花だん（まん中）
    o += "<ellipse cx='195' cy='108.5' rx='58' ry='4.6' fill='#5A8A44'/>"
    for i in range(40):
        a = 2 * math.pi * i / 40
        x = 195 + math.cos(a) * 52 * R.uniform(.2, 1)
        y = 108.5 + math.sin(a) * 3.6 * R.uniform(.2, 1)
        c = R.choice(('#E8574A', '#F2C14E', '#FFFFFF', '#F59ABE', '#B06AD6'))
        o += f"<circle cx='{f(x)}' cy='{f(y - 1.2)}' r='1.6' fill='{c}'/>"
    # 手前の 内の さく（白）
    o += f"<rect x='0' y='112' width='390' height='2.2' fill='{RAIL}'/><rect x='0' y='116.4' width='390' height='2' fill='{RAIL}'/>"
    o += "<rect x='0' y='118.4' width='390' height='1.2' fill='#4A7A3A' opacity='.35'/>"
    for i in range(14):
        o += f"<rect x='{f(i * 29 + 6)}' y='110.6' width='2.6' height='9' rx='.6' fill='{RAIL}'/><rect x='{f(i * 29 + 7.6)}' y='110.6' width='1' height='9' fill='#D2D0C8'/>"
    return doc(W, H, o)


def lane_svg():
    """手前の 道（すなの 色・ひづめの あと）"""
    defs = ("<linearGradient id='p' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#D6BB82'/><stop offset='1' stop-color='#C2A066'/></linearGradient>")
    o = f"<rect x='0' y='119' width='390' height='41' fill='url(#p)'/>"
    R = rnd(9)
    for i in range(70):
        x, y = R.uniform(0, W), R.uniform(123, 158)
        k = (y - 119) / 41
        o += f"<ellipse cx='{f(x)}' cy='{f(y)}' rx='{f(1.4 + 1.6 * k)}' ry='{f(.7 + .8 * k)}' fill='#A98A54' opacity='.45'/>"
    # 手前の 外の さく（下の はし）
    o += f"<rect x='0' y='152' width='390' height='2.6' fill='{RAIL}'/><rect x='0' y='158' width='390' height='2' fill='{RAIL}'/>"
    for i in range(10):
        o += f"<rect x='{f(i * 42 + 10)}' y='150' width='3.4' height='10' rx='.8' fill='{RAIL}'/><rect x='{f(i * 42 + 12)}' y='150' width='1.4' height='10' fill='#D2D0C8'/>"
    return doc(W, H, o, defs=defs)


def clouds_svg(w=W, h=34):
    R = rnd(13)
    o = ''
    for cx, cy, n in ((50, 12, 5), (180, 8, 4), (300, 14, 6)):
        parts = [(cx + (i - n / 2) * 8 + R.uniform(-2, 2), cy + R.uniform(-2, 2) - math.sin(math.pi * (i + .5) / n) * 4, 6 + math.sin(math.pi * (i + .5) / n) * 5) for i in range(n)]
        for dx in (-w, 0, w):
            for x, y, r in parts:
                o += f"<circle cx='{f(x + dx)}' cy='{f(y)}' r='{f(r)}' fill='#FFFFFF' opacity='.92'/>"
    return doc(w, h, o)


def pennants_svg(w=W, h=24):
    """上の 旗の ひも（小さな 三角の 旗）"""
    o = f"<path d='M-4 4 Q{w / 2} 14 {w + 4} 4' fill='none' stroke='#8A8E96' stroke-width='.9'/>"
    cols = ('#E8574A', '#F2C14E', '#3E6FC2', '#2E8A5A', '#FFFFFF', '#E88AB0')
    for i in range(26):
        x = 6 + i * 15
        t = x / w
        y = 4 + 10 * 4 * t * (1 - t) * 1.0
        o += f"<path d='M{f(x - 4)} {f(y)} L{f(x + 4)} {f(y)} L{f(x)} {f(y + 8)} Z' fill='{cols[i % len(cols)]}'/>"
    return doc(w, h, o)


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    still = B.get('still')
    alt = ('スタンドから見たパドックで、ゼッケンをつけた競走馬たちが歩いて回るイラスト。手前は右へ3頭（ゼッケン2・5・7）、おくは左へ3頭（ゼッケン1・4・8）。'
           'まん中に芝生と花だん、白いさく、うしろにお客さんのスタンドと木、上に小さな旗のひも（馬はいつも歩いている）')
    html = f'<div class="pkw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    html += img('pkBk', back_svg())
    html += f'<i class="pkCl" style="background-image:url(&quot;{durl(clouds_svg())}&quot;)"></i>'
    for nm in FAR:
        if nm in B:
            html += f'<i class="pkH {nm}"><i></i></i>'
    html += img('pkIn', infield_svg()) + img('pkLn', lane_svg())
    for nm in NEAR:
        if nm in B:
            html += f'<i class="pkH {nm}"><i></i></i>'
    html += img('pkPn', pennants_svg())
    html += '</div>'
    css = ('.pkw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#DDF0F8}'
           '.pkw>*{position:absolute;display:block}'
           '.pkw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.pkw .pkBk,.pkw .pkIn,.pkw .pkLn{left:0;top:0;width:390px;height:160px}'
           f'.pkw .pkCl{{left:0;top:0;width:{2 * W + 2}px;height:34px;background-size:{W}px 34px;background-repeat:repeat-x;animation:pkCloud 80s linear infinite}}'
           '.pkw .pkPn{left:0;top:-2px;width:390px;height:24px;transform-origin:50% 0;animation:pkSway 4.2s ease-in-out infinite}'
           '.pkw .pkH{left:0;top:0;overflow:hidden;will-change:transform}')
    keys = ''
    for group, names in (('near', NEAR), ('far', FAR)):
        ms = [(nm, B[nm]) for nm in names if nm in B]
        if not ms:
            continue
        # 同じ 組は 同じ はやさ・同じ 1回り（3頭を 1/3 ずつ ずらす）
        v = sum(m.get('speed', 30) for _, m in ms) / len(ms)
        wmax = max(m['cell'][0] / 2 for _, m in ms)
        D = W + wmax + 30
        T = D / v
        for k, (nm, m) in enumerate(ms):
            n, (cw, ch), (ax, ay) = m['frames'], m['cell'], m['at']
            w, h = cw / 2, ch / 2
            css += (f'.pkw .pkH.{nm}{{top:{f(ay / 2)}px;width:{f(w)}px;height:{f(h)}px;animation:pk{group}{k} {f(T, 3)}s linear {f(-T * k / len(ms) - T * 0.18, 3)}s infinite}}'
                    f'.pkw .pkH.{nm}>i{{display:block;width:{f(n * w)}px;height:{f(h)}px;background:url({m["url"]}) 0 0/{f(n * w)}px {f(h)}px no-repeat;'
                    f'animation:pkWalk{nm} {CYCLE}s steps({n}) {f(-CYCLE * k * 0.37, 3)}s infinite}}'
                    + kf(f'pkWalk{nm}', [(100, f'transform:translateX({f(-n * w)}px)')]))
            if group == 'near':
                x0, x1 = -w - 14, W + 14
            else:
                x0, x1 = W + 14, -w - 14
            keys += kf(f'pk{group}{k}', [(0, f'transform:translateX({f(x0)}px)'), (100, f'transform:translateX({f(x1)}px)')])
    css += keys
    css += (kf('pkCloud', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-W}px)')])
            + kf('pkSway', [(0, 'transform:rotate(-.6deg)'), (50, 'transform:rotate(.6deg)'), (100, 'transform:rotate(-.6deg)')]))
    css += reduced('.pkw .pkBk,.pkw .pkCl,.pkw .pkIn,.pkw .pkLn,.pkw .pkH,.pkw .pkPn') if still else ''
    return html, css


# ================================================================== 色・字・形（themes20 と 同じ 形）
def tile_paddock():
    """背景の もよう：芝生の しまと 小さな 蹄鉄・ひづめの あと（うすく）"""
    o = "<rect width='60' height='120' fill='#2F6B3E' opacity='.04'/>"
    o += ("<path d='M86 34 C80 26 82 16 90 13 C93 12 97 12 100 13 C108 16 110 26 104 34 L101 32 C105 26 104 19 99 17 C97 16 93 16 91 17 C86 19 85 26 89 32 Z' fill='#B8862A' opacity='.22'/>")
    for x, y in ((30, 90), (40, 100), (24, 104)):
        o += f"<ellipse cx='{x}' cy='{y}' rx='3' ry='2.2' fill='#2F6B3E' opacity='.12'/>"
    return tile(120, 120, o)


def rail_strip():
    """上の 帯の 下の ふち：白い さく（柱と 横の 2本の 板）"""
    o = (f"<rect x='0' y='1' width='24' height='2.2' fill='{RAIL}'/><rect x='0' y='6' width='24' height='2' fill='{RAIL}'/>"
         f"<rect x='10' y='0' width='3' height='10' rx='.6' fill='{RAIL}'/><rect x='12' y='0' width='1' height='10' fill='#C9C7BE'/>")
    return tile(24, 10, o)


def orn():
    """すみの 飾り（44×44）：ロゼット（リボンの 花・たれる 2本の リボン）"""
    o = ("<path d='M15 26 L9 42 L14 39 L17 43 L21 28 Z' fill='#2F7A48'/><path d='M29 26 L35 42 L30 39 L27 43 L23 28 Z' fill='#B8862A'/>")
    for k in range(14):
        a = math.radians(k * 360 / 14)
        x, y = 22 + math.cos(a) * 12, 20 + math.sin(a) * 12
        o += f"<circle cx='{f(x)}' cy='{f(y)}' r='4.6' fill='{'#2F7A48' if k % 2 else '#3F9A5C'}'/>"
    o += "<circle cx='22' cy='20' r='9.4' fill='#F6E7B8' stroke='#B8862A' stroke-width='1.6'/><circle cx='22' cy='20' r='6' fill='none' stroke='#B8862A' stroke-width='1'/>"
    o += ("<path d='M18.6 23.6 C16.4 20.6 16.8 16.4 20 15.2 C21 14.8 23 14.8 24 15.2 C27.2 16.4 27.6 20.6 25.4 23.6 L24 22.8 C25.6 20.6 25.2 17.8 23.4 17.2 C22.6 16.9 21.4 16.9 20.6 17.2 "
          "C18.8 17.8 18.4 20.6 20 22.8 Z' fill='#B8862A'/>")
    return o


THEME = dict(
    id=ID, cat=7, name='パドック', desc='歩く馬たち', title='パドック（芝の緑×白いさく×金）', banner=ID,
    alt='スタンドから見たパドックで、ゼッケンをつけた競走馬たちが歩いて回るイラスト。まん中に芝生と花だん、白いさく、うしろにお客さんのスタンドと木',
    fonts=['Kaisei+HarunoUmi:wght@700', 'Zen+Maru+Gothic:wght@500;700'],
    v=dict(bg='#F3F1E6', ink='#22301E', sub='#56664E', card='#FFFFFF', cardB='1.5px solid #D6DCC8', cardO='0 solid transparent', cardS='0 3px 0 #E2E6D6',
           radius='14px', rs='10px', font='"Zen Maru Gothic"', dfont='"Kaisei HarunoUmi"', dw='700', logo='#F6E7B8', logoS='0 2px 0 #163A22',
           iii='#F6E7B8', iiiB='0 solid transparent', iiiR='2px', hd='linear-gradient(180deg,#2F6B3E,#24553A)', hdInk='#F6F3E2', hdB='0 solid transparent',
           mBg='rgba(255,255,255,.1)', mLine='rgba(246,231,184,.6)', mInk='#F6F3E2', pill='rgba(0,0,0,.16)', pillLine='rgba(246,231,184,.45)', pillInk='#F6F3E2',
           coin='#B8862A', coinInk='#FFFFFF', badge='#FBF5E0', badgeInk='#7A5414', badgeB='1.5px solid #E2CC8A', tagBg='#F1F5EA', tagInk='#3E5236',
           tagLine='#D6DCC8', warnBg='#FBE6DE', warnInk='#9A3424', zBg='#FBFCF8', zB='1.5px solid #E4E9DA', znBg='#1F6B45', znInk='#FFFFFF',
           znB='0 solid transparent', znR='6px', znS='none', acc='#8A5A14', nR='8px', w2B='0 solid transparent', sep='1.5px dashed #D6DCC8',
           btn='#1F6B45', btnInk='#FFFFFF', btnB='0 solid transparent', btnR='12px', btnS='0 3px 0 #134A2E', btn2='#FFFFFF', btn2Ink='#1F6B45',
           btn2B='1.5px solid #B9CDB4', tab='#FFFFFF', tabB='1px solid #DCE2D0', tabInk='#56664E', tabOn='#E3F0E4', tabOnInk='#1F6B45', tabR='12px',
           sel='#1F6B45', selInk='#FFFFFF', h1='#7A5414'),
    chk=dict(hd=['#2F6B3E', '#24553A']),
    css=[('', 'background-image:' + curi(tile_paddock()) + ';background-size:120px 120px'),
         ('.hd::after', 'content:"";position:absolute;left:0;right:0;bottom:-9px;height:10px;background:' + curi(rail_strip()) + ' 0 0/24px 10px repeat-x'),
         ('.card', 'background-image:linear-gradient(180deg,rgba(47,107,62,.035),transparent 30%)')],
    orn=orn(),
    guide=dict(colors=[('#2F6B3E', '芝の 緑'), ('#1F6B45', 'ボタン'), ('#B8862A', '金'), ('#F6F4EE', '白い さく'), ('#F3F1E6', '背景')],
               fonts='見出し：Kaisei HarunoUmi<br>本文：Zen Maru Gothic', shape='角丸14px・帯は 芝の 緑で 下に 白い さく・芝生の しまの 背景・すみに ロゼット・的中ボタンは ゼッケンの PUSH',
               pic='スタンドから 見た パドック・ゼッケンの 馬たちが 歩いて 回る（手前は 右へ・おくは 左へ）・芝生と 花だん・白い さく・お客さんの スタンド・旗の ひも'),
)


# ================================================================== 的中ボタン：ゼッケンの PUSH（pk）
def push_face(sfx=''):
    """ボタン（200×100）が 白い ゼッケン（四角い 布・緑と 金の ふち・下の すみが まるい）。上に 鞍の かげ・ひも"""
    o = ('<path d="M-4 -4 H204 V84 Q204 104 184 104 H16 Q-4 104 -4 84 Z" fill="#1F6B45"/>'
         '<path d="M2 2 H198 V82 Q198 98 182 98 H18 Q2 98 2 82 Z" fill="#B8862A"/>'
         '<path d="M7 7 H193 V80 Q193 93 180 93 H20 Q7 93 7 80 Z" fill="#FFFFFF"/>'
         '<path d="M7 7 H193 V18 H7 Z" fill="#F1F5EA"/>'
         '<path d="M60 -6 Q100 -22 140 -6 L136 6 Q100 -8 64 6 Z" fill="#3A2A20"/>'
         '<path d="M70 -4 Q100 -14 130 -4" fill="none" stroke="#6A5040" stroke-width="2" stroke-linecap="round"/>')
    o += '<path d="M12 12 H188 V79 Q188 88 179 88 H21 Q12 88 12 79 Z" fill="none" stroke="#1F6B45" stroke-width="1.4" stroke-dasharray="4 3" opacity=".55"/>'
    o += ('<path d="M164 22 C160 17 161 10 166 8.4 C167.6 7.8 170.4 7.8 172 8.4 C177 10 178 17 174 22 L172.4 21 C175 17.6 174.6 12.8 171.4 11.6 '
          'C170.2 11.2 167.8 11.2 166.6 11.6 C163.4 12.8 163 17.6 165.6 21 Z" fill="#B8862A"/>')
    for x in (20, 180):
        o += f'<circle cx="{x}" cy="86" r="3.4" fill="#B8862A"/><circle cx="{x}" cy="86" r="1.4" fill="#7A5414"/>'
    o += '<path d="M10 22 Q12 60 22 90" fill="none" stroke="#E6EAE0" stroke-width="5" stroke-linecap="round" opacity=".8"/>'
    return f'<i class="pkf" aria-hidden="true"><svg viewBox="-10 -26 220 136" width="220" height="136">{o}</svg></i>'


def push_decor(sfx=''):
    """まわりに うかぶ ロゼット（.pkro）と 小さな 金の キラッ（.pktw）"""
    o = ''
    for j, (x, y, s) in enumerate(((-20, 6, 1.0), (222, 70, 0.9))):
        o += f'<g transform="translate({x} {y}) scale({s})"><g class="pkro" style="animation-delay:{-1.2 * j:.1f}s">'
        o += '<path d="M-6 6 L-10 22 L-6 20 L-3 23 L0 8 Z" fill="#1F6B45"/><path d="M6 6 L10 22 L6 20 L3 23 L0 8 Z" fill="#B8862A"/>'
        for k in range(12):
            a = math.radians(k * 30)
            o += f'<circle cx="{math.cos(a) * 9:.1f}" cy="{math.sin(a) * 9:.1f}" r="3.6" fill="{"#1F6B45" if k % 2 else "#3F9A5C"}"/>'
        o += '<circle r="7" fill="#F6E7B8" stroke="#B8862A" stroke-width="1.4"/></g></g>'
    for j, (x, y, r) in enumerate(((30, -40, 5), (180, -34, 6), (-24, 86, 4.4), (226, 0, 4.6))):
        o += f'<path class="pktw" d="{sparkle_d(x, y, r, 0.16)}" fill="#F6E7B8" style="animation-delay:{-0.65 * j:.2f}s"/>'
    return f'<i class="pkd" aria-hidden="true"><svg viewBox="-40 -60 280 190" width="280" height="190">{o}</svg></i>'


def _rosette(c1='#1F6B45', c2='#3F9A5C'):
    o = "<path d='M9 14 L6 24 L9 22.4 L11 24.6 L12 15 Z' fill='#B8862A'/><path d='M15 14 L18 24 L15 22.4 L13 24.6 L12 15 Z' fill='#1F6B45'/>"
    for k in range(10):
        a = math.radians(k * 36)
        o += f"<circle cx='{f(12 + math.cos(a) * 6.6)}' cy='{f(11 + math.sin(a) * 6.6)}' r='2.8' fill='{c1 if k % 2 else c2}'/>"
    o += "<circle cx='12' cy='11' r='5' fill='#F6E7B8' stroke='#B8862A' stroke-width='1'/>"
    return doc(24, 26, o)


def _shoe():
    return doc(22, 22, "<path d='M5 19 C1 13 2 5 8 3 C10 2.4 12 2.4 14 3 C20 5 21 13 17 19 L14.4 17.4 C17 13 16.4 8 13 6.6 C12 6.2 10 6.2 9 6.6 C5.6 8 5 13 7.6 17.4 Z' fill='#B8862A' stroke='#7A5414' stroke-width='.8'/>")


def _clover():
    o = ''
    for a in (-90, 30, 150):
        r = math.radians(a)
        o += f"<circle cx='{f(11 + math.cos(r) * 4.4)}' cy='{f(10 + math.sin(r) * 4.4)}' r='4.4' fill='#3F9A5C'/>"
    return doc(22, 22, o + "<path d='M11 12 Q12 17 15 20' stroke='#2E6E40' stroke-width='1.6' fill='none' stroke-linecap='round'/>")


PIECES = dict(ro=piece(_rosette()), rb=piece(_rosette('#B8862A', '#E2B85A')), hs=piece(_shoe()), cl=piece(_clover()),
              cf='border-radius:2px;background:linear-gradient(90deg,#FFFFFF,#E6EAE0)')


def push_burst():
    return fly_burst('pk', ['ro', 'hs', 'cl', 'rb', 'cf', 'cl'], 28, 47, sizes=dict(ro=(17, 22), rb=(15, 20), hs=(14, 18), cl=(13, 17), cf=(8, 11)))


PUSH_CSS = r'''
/* ---------- パドックの的中ボタン：ゼッケンの PUSH（壁紙パック） ----------
   ボタンが まるごと 白い ゼッケン（緑と 金の ふち・下の すみは まるい・上に 鞍の かげ）に「PUSH」（ゼッケンの 番号の ように 大きな 黒い 字）。
   まわりに ロゼットが ふわふわ・小さな 金の キラッ。上下の 動きは 的中と 同じ。押すと ゼッケンが ちぢんで ふくらみ（強く 光らせない）、
   ロゼット・蹄鉄・クローバー・白い 布の かけらが はじけて 落ち、金の 光の 輪が 広がる */
.pk{--pushA:#FFFFFF;--pushB:#1F6B45;--pushC:#B8862A;--rim:#B8862A;--rimD:#1F6B45}
.push.pk{--pr:16px;background:none;border-radius:16px;box-shadow:none;filter:drop-shadow(0 8px 0 rgba(20,60,36,.45)) drop-shadow(0 18px 24px rgba(0,0,0,.35))}
.push.pk span{top:4px;font:700 44px/1 "Kaisei HarunoUmi",serif;letter-spacing:.06em;color:#1E2418;text-shadow:0 2px 0 #E2E6D6}
.push.pk::after{inset:-22px;top:-38px;border-radius:34px;border-color:rgba(184,134,42,.9)}
.pk .pkf{position:absolute;left:-10px;top:-26px;width:220px;height:136px;pointer-events:none;font-style:normal}
.pk .pkf svg{display:block;width:220px;height:136px;overflow:visible}
.pk .pkd{position:absolute;left:-40px;top:-60px;width:280px;height:190px;pointer-events:none;z-index:3;font-style:normal}
.pk .pkd svg{display:block;width:280px;height:190px;overflow:visible}
.pk .pkro{animation:pkRo 2.8s ease-in-out infinite alternate}
@keyframes pkRo{from{transform:translate(0,-4px) rotate(-8deg)}to{transform:translate(0,4px) rotate(8deg)}}
.pk .pktw{transform-box:fill-box;transform-origin:50% 50%;animation:pkTw 2.6s ease-in-out infinite}
@keyframes pkTw{0%,100%{opacity:.15;transform:scale(.45)}50%{opacity:1;transform:scale(1.05) rotate(20deg)}}
.pshadow.pk{width:220px}
.tap.pk{font-family:"Kaisei HarunoUmi",serif;font-weight:700;color:#F6E7B8;letter-spacing:.12em;text-shadow:0 2px 0 #163A22,0 0 10px rgba(246,231,184,.6)}
.pressed.pk{border-radius:16px;background:#FFFFFF;box-shadow:0 0 0 4px #B8862A,0 0 0 7px #1F6B45,0 8px 0 7px #134A2E;animation-name:pkPress,fxH}
@keyframes pkPress{0%{transform:scale(1)}22%{transform:scale(.92)}45%{transform:scale(1.06)}100%{transform:scale(1.45);opacity:0}}   /* 強く光らせない */
@media (prefers-reduced-motion:reduce){.pk .pkro,.pk .pktw{animation:none}.clips.pk{display:none}}
''' + fly_css('pk', 'rgba(184,134,42,.9)', PIECES)

PUSH = dict(code='pk', face=push_face, decor=push_decor, burst=push_burst, css=PUSH_CSS)
