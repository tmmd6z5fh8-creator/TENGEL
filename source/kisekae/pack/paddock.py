"""壁紙パック ④パドック（まさちゃんの 指定「馬がパドックを歩きまわる」
   第4.93版の 直し「ランダムで馬が首を激しく振ったり、うんちしたり、早歩きになったり、首を下げて歩いたりするようにして！」
   第4.94版の 直し「パドックの馬地面から脚が浮いたり地面についたりしてるから安定して同じ場所で歩かせて！あと脚の動きもう少しスムーズにして！」
   第4.95版の 直し「赤四角のあたりにいる観客達に少しだけ動きをつけて！」）
   上の絵：スタンドから 見た パドック。手前の 道を 右へ 3頭（ゼッケン 2・5・7）、おくの 道を 左へ 3頭（1・4・8・小さく）が 歩く
     （いままでと 同じ 馬）。まん中に 芝生と 花だん、白い さく、うしろに お客さんの スタンドと 木、上に 小さな 旗の ひも。
   常歩（第4.94版）：1回り 1.25秒・24コマ（pack/make/paddock_gait.py：ひづめの 道を 先に 決めて 足の 角度を 逆に 解く）。
     地面に ついて いる ひづめは どの コマ・どの シートでも 同じ 地面の 線（道の 同じ 高さ）に つく。体は ほんの 少し 上下・影は 地面に 止まった まま。
   動き：馬は いつも 歩いて 回る（コマを めくりながら 横へ：地面に ついた ひづめが すべらない はやさ）・手前と おくは 反対へ・旗の ひもが ゆれる・雲が ゆっくり 流れる。
     スタンドの お客さん（第4.96版・crowd_parts）：210人の うち 75人が、人ごとに ちがう 長さの 1回りと ずれで ばらばらに 動く
     （首を 回して 馬を 目で 追う・となりと 話す・座りなおす・立ち上がる・手を あげる／指さす・スマホで 写真・新聞を 広げて めくる）。
     第4.96版の 直し「赤四角の観客全然動いてないから多少の動きが分かるようにして！実際のパドックだと人々はそんなに大きくは動かないけど、多少は動いてる。」
   ときどきの 動き（第4.93版）：馬ごとに 長い 1回り（手前 67.5秒・おく 60／90秒）の 中の ばらばらの 時に（PLAN）、
     首を 激しく 振る（上へ ぶんっと 振り上げて おろす・1回りに 2回・たてがみが はねる）／首を 下げて 歩く（下げていく → 下げて 歩く → 上げていく）／
     早歩き（常歩の コマを 1.5倍の はやさで めくって 横も 1.5倍＝ひづめが すべらない。あとで 見えない 所で ゆっくり 歩いて 前後の ずれを もどす＝となりの 馬に 追いつかない）／
     うんち（手前の 3頭：しっぽを 上げて 丸い うんちが 4つ ぽとぽと 落ちる。地面に ついた うんちは その 場所に 9秒 残って 消える）。
     行動ごとの コマの シート（pack/make/paddock_moves.py：常歩・首振り 24コマ・首下げ 24コマ×3まい・うんち 48コマ）は 足の 動きが 常歩と 同じで コマ0が 同じ 形
     → 見える シートを 回りの つぎめで 切りかえる（visibility の step-end）"""
import math
from .common import W, H, f, durl, curi, tile, doc, P, smooth, star_d, sparkle_d, mix, kf, img, rnd, reduced, fly_burst, fly_css, piece

ID = 'paddock'
CYCLE = 1.25       # 歩く 1回りの 秒（paddock_art.CYCLE と 同じ。コマの 数は シートの meta：常歩 24）
NEAR = ('n2', 'n5', 'n7')
FAR = ('f1', 'f4', 'f8')
FAR_K = 1.0        # おくの 馬の シートは はじめから 小さく 描いて いる（そのまま）
GREEN = dict(d='#2E5E34', m='#3F7A44', l='#5E9A58', ll='#8CC07A')
RAIL = '#F6F4EE'


# ---------------------------------------------------------------- 絵
def back_svg(people=None):
    """うしろ：空・木・お客さんの スタンド（小さな 色の つぶ）・おくの 外の さく・おくの 道。
       第4.96版：動く お客さん（crowd_roles：首を 回す 人は 体だけ・ほかの 動く 人は 描かない）。動かない 人にも 顔。people：お客さん [(だん, 番号, x, y, 服, 髪)] を 入れる list"""
    roles = crowd_roles()
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
            hc = R.choice(('#2A1E18', '#4A3A30', '#E8D2B8', '#1E1E22'))
            if people is not None:
                people.append((k, i, x, y, c, hc))
            role = roles.get((k, i))
            if role is None or role[0] == 'look':                           # 動かない 人・首を 回す 人の 体
                o += f"<rect x='{f(x - 1.7)}' y='{f(y + 2)}' width='3.4' height='4' rx='1.2' fill='{c}'/>"
            if role is None:                                                # 動かない 人の 頭と 顔（顔の 色は べつの 乱数＝ほかの 絵は かわらない）
                o += f"<circle cx='{f(x)}' cy='{f(y + 1)}' r='1.5' fill='{hc}'/>" + face_svg(x, y, rnd(800 + k * 100 + i).choice(CR_SKIN))
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


# ---------------------------------------------------------------- スタンドの お客さん（第4.96版：まさちゃんの 指定「赤四角の観客全然動いてないから多少の動きが分かるようにして！
#   実際のパドックだと人々はそんなに大きくは動かないけど、多少は動いてる。」・第4.95版の「少しだけ動きをつけて！」の 0.4px の ゆれは 見えなかった）
#   3だん 210人の うち 75人（1だん 25人）が 動く。人ごとに ちがう 長さの 1回りと ずれで、ばらばらに（波には しない）：
#     首を 回して 馬を 目で 追う（look：頭が 1px 横へ・顔が 少し 回る）／となりと 話す（chat：2人で 顔を 寄せて うなずく）／座りなおす（shift）／
#     立ち上がって まわりを 見て 座る（stand：2.6px）／手を あげて ふる・指さす（hand）／スマホで 写真を とる（phone）／競馬新聞を 広げて めくる（paper）。
#   動きは 位置と 角度だけ（色は かわらない＝点めつ なし）。体と 頭は CSS の 小さな 箱（絵の データなし）。顔（はだの 色）は みんなに つけた
CR_SKIN = ('#F2D2B6', '#E8BE98', '#D4A47C')
CR_PANTS = ('#3A3A44', '#4A5A78', '#5A4A42')
CR_TOP = 36                                                     # スタンドの 上の はし（だんの y：38・45・52）
TIER_KINDS = ['look'] * 10 + ['shift'] * 2 + ['stand'] * 2 + ['hand'] * 2 + ['phone'] * 2 + ['paper']    # 1だん（＋話す 2人組 3組）
CHAT_PAIRS = 3
DUR = dict(look=(8.0, 13.0), chat=(10.0, 15.0), shift=(9.0, 14.0), stand=(13.0, 18.0), hand=(10.0, 16.0), phone=(11.0, 16.0), paper=(12.0, 17.0))


def face_svg(x, y, skin):
    """すわって いる 人の 顔（頭の 下の ほう・はだの 色）"""
    return f"<ellipse cx='{f(x)}' cy='{f(y + 1.45)}' rx='1.1' ry='.95' fill='{skin}'/>"


def crowd_roles():
    """お客さんの 役：{(だん, 番号): (種類, 動く 人の 番号, 組の 相手の 番号 か None)}。1だんを 22の 区切りに わけて 1人ずつ（ちらばる ように）。
       話す 2人組は 右どなりと 組む。すみの 人（番号 0・1・68・69）は 動かさない"""
    R = rnd(96)
    roles = {}
    n = 0
    for k in range(3):
        kinds = ['chat'] * CHAT_PAIRS + TIER_KINDS
        R.shuffle(kinds)
        seg = 64 / len(kinds)
        used = set()
        for j, kd in enumerate(kinds):
            lo = 2 + j * seg
            cand = [i for i in range(int(lo), int(lo + seg) + 1) if 2 <= i <= 66 and i not in used and i - 1 not in used]
            if kd == 'chat':
                cand = [i for i in cand if i + 1 <= 67]
            if not cand:
                continue
            i = R.choice(cand)
            if kd == 'chat':
                roles[(k, i)] = ('chat', n, n + 1)
                roles[(k, i + 1)] = ('chat', n + 1, n)
                used |= {i, i + 1}
                n += 2
            else:
                roles[(k, i)] = (kd, n, None)
                used.add(i)
                n += 1
    return roles


def _kf_tr(name, pts, fn):
    """(割合 0〜1, 値) → @keyframes（fn：値 → 宣言）"""
    return kf(name, [(t * 100, fn(v)) for t, v in pts])


def _tr(v):
    x, y = v if isinstance(v, tuple) else (v, 0.0)
    return 'transform:none' if abs(x) < 1e-6 and abs(y) < 1e-6 else f'transform:translate({f(x)}px,{f(y)}px)'


def _face(v):
    """頭が 横へ x px の とき の 顔：少し 先に 動いて 細く（首を 回した 顔）"""
    x, y = v if isinstance(v, tuple) else (v, 0.0)
    if abs(x) < 1e-6:
        return 'transform:none'
    return f'transform:translateX({f(0.45 * x)}px) scaleX({f(1 - 0.24 * min(1.0, abs(x)))})'


# 動きの ひな形（割合 0〜1 → 値）。頭：x・y px／体の 組：x・y px／腕：角度°（180＝下）／スマホ・新聞：上下 px
LOOK = {
    'a': [(0, 0), (.10, 0), (.16, -1.0), (.42, -1.0), (.49, 0), (.62, 0), (.68, 1.0), (.86, 1.0), (.92, 0), (1, 0)],          # 左を 見て → 右を 見る
    'b': [(0, -.9), (.06, -.9), (.46, .9), (.56, .9), (.63, 0), (.84, 0), (.92, -.9), (1, -.9)],                               # 右へ 歩く 馬を ゆっくり 目で 追う
    'c': [(0, .9), (.06, .9), (.46, -.9), (.56, -.9), (.63, 0), (.84, 0), (.92, .9), (1, .9)],                                 # 左へ 歩く 馬を 目で 追う
    'd': [(0, 0), (.28, 0), (.33, (.9, 0)), (.47, (.9, 0)), (.52, 0), (.70, 0), (.73, (0, .45)), (.76, 0), (.79, (0, .45)), (.82, 0), (1, 0)],   # ちらっと 見て うなずく
}
CHAT_A = [(0, 0), (.14, 0), (.20, (.8, 0)), (.25, (.8, .45)), (.29, (.8, 0)), (.36, (.8, .45)), (.40, (.8, 0)), (.58, (.8, 0)), (.64, 0), (1, 0)]
CHAT_B = [(0, 0), (.16, 0), (.22, (-.8, 0)), (.44, (-.8, 0)), (.48, (-.8, .45)), (.52, (-.8, 0)), (.56, (-.8, .45)), (.60, (-.8, 0)), (.66, 0), (1, 0)]
CHAT_BODY = [(0, 0), (.16, 0), (.22, .35), (.58, .35), (.65, 0), (1, 0)]
SHIFT = {
    'a': [(0, 0), (.18, 0), (.23, (.5, .45)), (.28, (.9, 0)), (.64, (.9, 0)), (.69, (.45, .4)), (.74, 0), (1, 0)],
    'b': [(0, 0), (.30, 0), (.35, (-.5, .45)), (.40, (-.9, 0)), (.70, (-.9, 0)), (.75, (-.45, .4)), (.80, 0), (1, 0)],
}
SHIFT_HEAD = [(0, 0), (.30, 0), (.36, .8), (.52, .8), (.58, 0), (1, 0)]
STAND = [(0, 0), (.20, 0), (.27, (0, -2.6)), (.60, (0, -2.6)), (.67, 0), (1, 0)]
STAND_HEAD = [(0, 0), (.30, 0), (.35, -.9), (.44, -.9), (.50, .9), (.56, .9), (.61, 0), (1, 0)]
HAND = {
    'wave': [(0, 180), (.34, 180), (.41, 28), (.45, 8), (.49, 30), (.53, 8), (.57, 26), (.64, 180), (1, 180)],
    'point': [(0, 180), (.48, 180), (.55, 74), (.72, 70), (.79, 180), (1, 180)],
}
HAND_HEAD = {'wave': [(0, 0), (1, 0)], 'point': [(0, 0), (.48, 0), (.54, .9), (.74, .9), (.80, 0), (1, 0)]}
PHONE = [(0, 7.0), (.30, 7.0), (.36, 0), (.45, (0, -.25)), (.54, 0), (.62, 0), (.68, 7.0), (1, 7.0)]
PAPER = [(0, 6.5), (.24, 6.5), (.30, 0), (.70, 0), (.76, 6.5), (1, 6.5)]
PAPER_FLIP = [(0, 1), (.48, 1), (.51, .12), (.54, 1), (1, 1)]
PAPER_HEAD = [(0, 0), (.30, 0), (.34, (0, .35)), (.68, (0, .35)), (.72, 0), (1, 0)]


SHIRTS = ('#E8574A', '#3E6FC2', '#F2C14E', '#FFFFFF', '#5A4A42', '#2E8A5A', '#E88AB0', '#3A3A44', '#F0E0C8')   # back_svg の 服の 色（同じ じゅん）
HAIRS = ('#2A1E18', '#4A3A30', '#E8D2B8', '#1E1E22')                                                             # back_svg の 髪の 色
SHOULDER = {1: 5.35, -1: 2.65}                                                                                   # 腕の 根もと（人の 箱 8×13 の 中の x・y は 7.9）


def _part(body):
    """人の 箱（8×13：頭の まん中 (4, 6)・いすの 線 y 11）の 部品の 絵 → CSS の url()"""
    return curi(doc(8, 13, body))


def crowd_css(arms):
    """動く お客さんの 共通の CSS と @keyframes。部品は どれも 人の 箱と 同じ 8×13 の 絵（CSS の 背景・色ごとの クラス）を 重ねて、
       transform だけで 動かす（小さな 箱の 大きさを 1px に まるめる ブラウザでも 形が くずれない）。長さと ずれは 人ごとに style の --d・--t。
       arms：使う 腕の クラス {名前: (服, はだ, 左右)}"""
    css = ('.pkw .pkM,.pkw .pkHd{left:0;top:0;width:8px;height:11px}'
           '.pkw .pkM{overflow:hidden}'
           '.pkw .pkM i,.pkw .pkM b,.pkw .pkHd b{position:absolute;display:block;left:0;top:0;width:8px;height:13px;background-size:8px 13px}'
           '.pkw .pkM *,.pkw .pkHd *{animation-duration:var(--d);animation-delay:var(--t);animation-iteration-count:infinite;animation-timing-function:ease-in-out}'
           '.pkw .fc{transform-origin:4px 6.45px}'
           '.pkw .pp{transform:translateY(7px)}'
           '.pkw .pa{transform:translateY(6.5px)}'
           '.pkw .pa>b{transform-origin:4px 7.95px}')
    for n, c in enumerate(SHIRTS):
        css += f'.pkw .c{n}{{background-image:{_part(f"<rect x='2.3' y='7' width='3.4' height='4.2' rx='1.2' fill='{c}'/>")}}}'
    for n, c in enumerate(HAIRS):
        css += f'.pkw .k{n}{{background-image:{_part(f"<circle cx='4' cy='6' r='1.5' fill='{c}'/>")}}}'
    for n, c in enumerate(CR_SKIN):
        css += f'.pkw .s{n}{{background-image:{_part(f"<ellipse cx='4' cy='6.45' rx='1.1' ry='.95' fill='{c}'/>")}}}'
        css += (f'.pkw .q{n}{{background-image:{_part(f"<rect x='2.55' y='6.5' width='2.9' height='.95' rx='.45' fill='{c}'/>"
                                                         "<rect x='3.25' y='5.2' width='1.5' height='2.2' rx='.3' fill='#2C3038' stroke='#5A606C' stroke-width='.3'/>")}}}')
    for n, c in enumerate(CR_PANTS):
        css += f'.pkw .p{n}{{background-image:{_part(f"<rect x='2.5' y='10.2' width='3' height='2.8' rx='.6' fill='{c}'/>")}}}'
    css += ('.pkw .pa>b{background-image:' + _part("<rect x='1.9' y='6.5' width='4.2' height='2.9' rx='.25' fill='#F1EDE2'/>"
                                                     + ''.join(f"<rect x='2.3' y='{f(yy)}' width='3.4' height='.26' fill='#A9A59B'/>" for yy in (7.3, 7.95, 8.6))) + '}')
    for nm, (c, skin, side) in sorted(arms.items()):
        sx = SHOULDER[side]
        css += (f'.pkw .{nm}{{transform-origin:{f(sx)}px 7.9px;transform:rotate(180deg);background-image:'
                + _part(f"<path d='M{f(sx)} 7.9 L{f(sx)} 4.75' stroke='{c}' stroke-width='1' stroke-linecap='round'/><circle cx='{f(sx)}' cy='4.45' r='.62' fill='{skin}'/>") + '}')
    for v, pts in LOOK.items():
        css += _kf_tr(f'pkLk{v}', pts, _tr) + _kf_tr(f'pkLf{v}', pts, _face)
    for nm, pts in (('pkCa', CHAT_A), ('pkCb', CHAT_B)):
        css += _kf_tr(nm, pts, _tr) + _kf_tr(nm + 'f', pts, _face)
    css += _kf_tr('pkCbd', CHAT_BODY, _tr) + _kf_tr('pkCbe', [(t, -v) for t, v in CHAT_BODY], _tr)
    for v, pts in SHIFT.items():
        css += _kf_tr(f'pkSh{v}', pts, _tr)
    css += _kf_tr('pkShh', SHIFT_HEAD, _tr) + _kf_tr('pkShf', SHIFT_HEAD, _face)
    css += _kf_tr('pkSt', STAND, _tr) + _kf_tr('pkSth', STAND_HEAD, _tr) + _kf_tr('pkStf', STAND_HEAD, _face)
    neg = lambda pts: [(t, -x if isinstance(x, (int, float)) else x) for t, x in pts]
    for v, pts in HAND.items():
        css += _kf_tr(f'pkHr{v}', pts, lambda a: f'transform:rotate({f(a)}deg)') + _kf_tr(f'pkHl{v}', pts, lambda a: f'transform:rotate({f(-a)}deg)')
        css += _kf_tr(f'pkHh{v}', HAND_HEAD[v], _tr) + _kf_tr(f'pkHf{v}', HAND_HEAD[v], _face)
        css += _kf_tr(f'pkHm{v}', neg(HAND_HEAD[v]), _tr) + _kf_tr(f'pkHn{v}', neg(HAND_HEAD[v]), _face)
    css += _kf_tr('pkPh', PHONE, lambda v: _tr(v if isinstance(v, tuple) else (0, v)) if v else 'transform:translate(0,0)')
    css += _kf_tr('pkPa', PAPER, lambda v: _tr((0, v)) if v else 'transform:translate(0,0)')
    css += _kf_tr('pkPf', PAPER_FLIP, lambda v: 'transform:none' if v == 1 else f'transform:scaleX({f(v)})')
    css += _kf_tr('pkPd', PAPER_HEAD, _tr) + _kf_tr('pkPe', PAPER_HEAD, _face)
    return css


def crowd_parts(ppl):
    """動く お客さんの html と css。ppl：back_svg が 入れた [(だん, 番号, x, y, 服, 髪)]（だんの 上から じゅんに＝手前の だんが 上に かさなる）。
       人の 箱は transform で 置く（left・top を 1px に まるめる ブラウザでも もとの 場所と ずれない）"""
    roles = crowd_roles()
    html = ''
    arms = {}
    for k, i, x, y, c, hc in ppl:
        role = roles.get((k, i))
        if not role:
            continue
        kd, n, mate = role
        R = rnd(700 + n)
        si, pi = R.randrange(len(CR_SKIN)), R.randrange(len(CR_PANTS))
        ci, hi_ = SHIRTS.index(c), HAIRS.index(hc)
        lo, hi = DUR[kd]
        if kd == 'chat':                                                    # 2人組は 同じ 長さと ずれ（小さい 番号の 人の 乱数）
            R2 = rnd(900 + min(n, mate))
            d = R2.uniform(lo, hi)
            t = -R2.uniform(0, d)
        else:
            d = R.uniform(lo, hi)
            t = -R.uniform(0, d)
        st = f'transform:translate({f(x - 4)}px,{f(y - 5)}px);--d:{f(d, 2)}s;--t:{f(t, 2)}s'
        head = lambda hn, fn: (f'<b class="k{hi_}" style="animation-name:{hn}"><b class="fc s{si}" style="animation-name:{fn}"></b></b>')
        if kd == 'look':                                                    # 頭だけ（体は うしろの 絵）
            v = R.choice(tuple(LOOK))
            html += f'<i class="pkHd" style="{st}">' + head(f'pkLk{v}', f'pkLf{v}') + '</i>'
            continue
        hn, fn, gn, bn, extra, arm = 'none', 'none', 'none', 'none', '', ''
        if kd == 'chat':
            left = mate > n                                                 # 左の 人（相手は 右）
            hn, fn = ('pkCa', 'pkCaf') if left else ('pkCb', 'pkCbf')
            bn = 'pkCbd' if left else 'pkCbe'
        elif kd == 'shift':
            gn = 'pkSh' + R.choice(tuple(SHIFT))
            hn, fn = 'pkShh', 'pkShf'
        elif kd == 'stand':
            gn, hn, fn = 'pkSt', 'pkSth', 'pkStf'
        elif kd == 'hand':
            v = R.choice(('wave', 'point', 'wave'))
            side = R.choice((-1, 1))
            an = f'a{"R" if side > 0 else "L"}{ci}{si}'
            arms[an] = (c, CR_SKIN[si], side)
            arm = f'<b class="{an}" style="animation-name:{"pkHr" if side > 0 else "pkHl"}{v}"></b>'
            hn, fn = (f'pkHh{v}', f'pkHf{v}') if side > 0 else (f'pkHm{v}', f'pkHn{v}')
        elif kd == 'phone':
            extra = f'<b class="pp q{si}" style="animation-name:pkPh"></b>'
        elif kd == 'paper':
            extra = '<i class="pa" style="animation-name:pkPa"><b style="animation-name:pkPf"></b></i>'
            hn, fn = 'pkPd', 'pkPe'
        html += (f'<i class="pkM" style="{st}"><i style="animation-name:{gn}">' + arm
                 + f'<b class="p{pi}"></b><b class="c{ci}" style="animation-name:{bn}"></b>'
                 + head(hn, fn) + extra + '</i></i>')
    return html, crowd_css(arms)


# ---------------------------------------------------------------- 馬の 歩きと ときどきの 動き（第4.93版）
FAST, SLOW = CYCLE / 1.5, CYCLE * 1.5           # 早歩き・ゆっくり 歩きの 1回り（常歩の シートを はやく／おそく めくる＝横の はやさも 1.5倍／2/3倍）
PASS = dict(near=22.5, far=30.0)                 # 舞台を 1回 横切る 秒（3頭が 1/3 ずつ ずれて 歩く）
# 馬ごとの 1回りの 秒と、通る 回ごとの 行動（s1・s2：首振り 1・2回り／d2・d3：首を 下げて 2・3回り（下げていく・上げていく 1回りずつ を 足す）／p：うんち／f：早歩き）
#   早歩きの あとには 見えない 所で ゆっくり 歩く（3.75秒）＝ 1回りで 前後の ずれが もどる（となりの 馬に 追いつかない）
PLAN = {
    'n2': (67.5, [['s2'], ['f', 'd2'], ['p']]),          # 第4.93版：2番も 首を 下げて 歩く（n2_d の シートを 使う）
    'n5': (67.5, [['d3'], ['p'], ['s1', 'f']]),
    'n7': (67.5, [['p'], ['d2'], ['f', 's2']]),
    'f1': (60.0, [['s2'], ['d3']]),
    'f4': (90.0, [['f'], ['s1'], ['d2']]),
    'f8': (60.0, [['d2'], ['f', 's2']]),
}
DUNG_STAY = 9.0                                  # 地面の うんちが 残る 秒（そのあと 1.2秒で 消える）


def _ev_len(code):
    if code[0] == 's':
        return int(code[1]) * CYCLE
    if code[0] == 'd':
        return (int(code[1]) + 2) * CYCLE
    if code == 'p':
        return 2 * CYCLE
    if code == 'f':
        return 2 * CYCLE
    raise KeyError(code)


def _grid(code):
    return 2 * CYCLE if code in ('p', 'f') else CYCLE


def _segments(evs, Lh):
    """歩く はやさの 区間 [(t0, t1, 倍率)]"""
    marks = sorted([(t, t + _ev_len(c) if c != 'w' else t + 2 * SLOW, 1.5 if c == 'f' else 2 / 3) for t, c in evs if c in ('f', 'w')])
    segs, t = [], 0.0
    for a, b, k in marks:
        if a > t:
            segs.append((t, a, 1.0))
        segs.append((a, b, k))
        t = b
    if t < Lh:
        segs.append((t, Lh, 1.0))
    return segs


def _dist(segs, v, t):
    s = 0.0
    for a, b, k in segs:
        if t <= a:
            break
        s += v * k * (min(t, b) - a)
    return s


def schedule(nm, meta, group, k_idx):
    """馬 nm の 1回り：行動の ならび [(時刻, 記号)]・はやさの 区間・場所の 関数"""
    Lh, plan = PLAN[nm]
    P = PASS[group]
    v = meta['speed']
    D = v * P
    lo, hi = meta['_span']                        # 全部の シートの 横の はし（入れものの 左から：左がわ・右がわ）
    dirn = 1 if group == 'near' else -1
    if dirn > 0:
        x_lo, x_hi = -hi - 3, -hi - 3 + D
    else:
        x_hi, x_lo = W - lo + 3, W - lo + 3 - D
    vis = (-lo - 22, W - hi + 22)                 # 行動は 舞台に ほぼ 入って いる 間に（はしが 少し 切れて も よい）
    s0 = D * 0.02                                                     # 1回りの はじめは 舞台の 外（入って くる 前）。馬どうしの ずれは ページの おくれ（delay）で
    R = rnd(sum(map(ord, nm)) * 7)
    evs = []

    def pos(s):
        q = (s0 + s) % D
        return x_lo + q if dirn > 0 else x_hi - q

    def free(a, b):
        return all(b <= t or a >= t + (_ev_len(c) if c != 'w' else 2 * SLOW) for t, c in evs)

    def seen(segs, t0, t1):
        return all(vis[0] <= pos(_dist(segs, v, tt)) <= vis[1] for tt in (t0, (t0 + t1) / 2, t1))

    def hidden(segs, t0, t1):
        return all(not (vis[0] - 30 <= pos(_dist(segs, v, tt)) <= vis[1] + 30) for tt in (t0, (t0 + t1) / 2, t1))

    def cands(code, pi=None):
        g, ln, out, t = _grid(code), _ev_len(code), [], 0.0
        while t + ln <= Lh - 0.01:
            segs = _segments(evs + [(t, code)], Lh)
            if free(t - 1.0, t + ln + 1.0) and seen(segs, t, t + ln):
                if pi is None or int((s0 + _dist(segs, v, t)) // D) % len(plan) == pi:
                    out.append(t)
            t += g
        return out

    for pi, codes in enumerate(plan):
        for code in codes:
            cand = cands(code, pi) or cands(code)
            if not cand:
                continue
            t = cand[int(R.uniform(0.2, 0.8) * len(cand))]
            evs.append((t, code))
            if code == 'f':                                              # 早歩きの あとに ゆっくり 歩く（なるべく 見えない 所で）
                ln = _ev_len(code)
                t2s = [k * 2 * SLOW for k in range(int(Lh // (2 * SLOW)) + 1) if k * 2 * SLOW >= t + ln + 1.0 and k * 2 * SLOW + 2 * SLOW <= Lh]
                t2s = [t2 for t2 in t2s if free(t2, t2 + 2 * SLOW)]
                hid = [t2 for t2 in t2s if hidden(_segments(evs + [(t2, 'w')], Lh), t2, t2 + 2 * SLOW)]
                if hid or t2s:
                    evs.append(((hid or t2s)[0], 'w'))
                else:                                                    # 入らなければ 早歩きを やめる
                    evs.remove((t, code))
    evs.sort()
    segs = _segments(evs, Lh)
    return evs, segs, pos, D, v, dirn, s0


def _vis_keys(windows, Lh, show_outside=False):
    """見える 区間（[(t0, t1)]）→ visibility の @keyframes（step-end）"""
    rows = [(0, 'visibility:visible' if show_outside else 'visibility:hidden')]
    for a, b in sorted(windows):
        rows.append((a / Lh * 100, 'visibility:hidden' if show_outside else 'visibility:visible'))
        rows.append((b / Lh * 100, 'visibility:visible' if show_outside else 'visibility:hidden'))
    rows.append((100, rows[0][1]))
    out = []
    for p, d in rows:                                                    # 同じ 所の つづきは まとめる
        if out and abs(out[-1][0] - p) < 1e-6:
            out[-1] = (p, d)
        else:
            out.append((p, d))
    return out


def horse_parts(nm, B, group, k_idx):
    """1頭の html と css（動く 入れもの・常歩／早歩き／ゆっくり／首振り／首下げ／うんちの シート・地面の うんち）"""
    m = B[nm]
    ax, ay = m['at']
    lays = {'w': m}
    for kind in ('s', 'dl', 'dd', 'dr', 'p'):
        if f'{nm}_{kind}' in B:
            lays[kind] = B[f'{nm}_{kind}']
    has_d = all(k in lays for k in ('dl', 'dd', 'dr'))
    lo = min((l['at'][0] - ax) / 2 for l in lays.values())
    hi = max((l['at'][0] - ax) / 2 + l['cell'][0] / 2 for l in lays.values())
    meta = dict(m, _span=(lo, hi))
    evs, segs, pos, D, v, dirn, s0 = schedule(nm, meta, group, k_idx)
    evs = [(t, c) for t, c in evs if (c[0] != 's' or 's' in lays) and (c[0] != 'd' or has_d) and (c != 'p' or 'p' in lays)]
    Lh = PLAN[nm][0]
    dl = -(k_idx * PASS[group] / 3 + 0.41 * k_idx + (3.3 if group == 'far' else 0.0))   # 馬ごとの ずれ：1/3 ずつ はなれて 歩く・足が そろわない ように
    name = f'pk{nm}'
    s_tot = _dist(segs, v, Lh)

    def time_at_dist(sd):
        a_, b_ = 0.0, Lh
        for _ in range(60):
            mid = (a_ + b_) / 2
            if _dist(segs, v, mid) < sd:
                a_ = mid
            else:
                b_ = mid
        return (a_ + b_) / 2
    # 入れものの 横の 動き：はやさの 区間の さかい と 舞台の はしで 反対の はしへ（見えない 所）
    wraps = [time_at_dist(kk * D - s0) for kk in range(1, int((s0 + s_tot) // D) + 2) if 0 < kk * D - s0 < s_tot - 1e-6]
    keyt = sorted(set([0.0, Lh] + [a_ for a_, b_, k_ in segs] + [b_ for a_, b_, k_ in segs]))
    rows = []
    for t in sorted(set(keyt + wraps)):
        s = _dist(segs, v, t)
        if any(abs(t - w_) < 1e-9 for w_ in wraps):
            rows.append((t / Lh * 100, f'transform:translateX({f(pos(s - 1e-6), 1)}px)'))
            rows.append((t / Lh * 100 + 0.002, f'transform:translateX({f(pos(s + 1e-6), 1)}px)'))
        else:
            rows.append((t / Lh * 100, f'transform:translateX({f(pos(s), 1)}px)'))
    html = f'<i class="pkH {nm}">'
    css = f'.pkw .pkH.{nm}{{top:{f(ay / 2)}px;animation:{name}X {f(Lh)}s linear {f(dl, 3)}s infinite}}' + kf(f'{name}X', rows)
    # 見える 区間
    win = {k: [] for k in ('w', 'f', 'sl', 's', 'dl', 'dd', 'dr', 'p')}
    for t, c in evs:
        if c == 'f':
            win['f'].append((t, t + 2 * CYCLE))
        elif c == 'w':
            win['sl'].append((t, t + 2 * SLOW))
        elif c[0] == 's':
            win['s'].append((t, t + _ev_len(c)))
        elif c[0] == 'd':
            nd = int(c[1])
            win['dl'].append((t, t + CYCLE))
            win['dd'].append((t + CYCLE, t + CYCLE * (1 + nd)))
            win['dr'].append((t + CYCLE * (1 + nd), t + CYCLE * (2 + nd)))
        elif c == 'p':
            win['p'].append((t, t + 2 * CYCLE))
    busy = [w for k, ws in win.items() if k != 'w' for w in ws]
    LAY = [('w', 'w', CYCLE), ('f', 'w', FAST), ('sl', 'w', SLOW), ('s', 's', CYCLE), ('dl', 'dl', CYCLE), ('dd', 'dd', CYCLE), ('dr', 'dr', CYCLE), ('p', 'p', 2 * CYCLE)]
    for key, src, per in LAY:                                            # 常歩・首振り・首下げ（3まい）は 1回りで 24コマ・うんちは 2回りで 48コマ（シートの meta）
        if src not in lays or (key != 'w' and not win[key]):
            continue
        l = lays[src]
        f0, nf = 0, l['frames']
        lw, lh = l['cell'][0] / 2, l['cell'][1] / 2
        tot = l['frames'] * lw
        lx, ly = (l['at'][0] - ax) / 2, (l['at'][1] - ay) / 2
        vk = _vis_keys(busy, Lh, show_outside=True) if key == 'w' else _vis_keys(win[key], Lh)
        html += f'<i class="pkL {key}"><i></i></i>'
        css += (f'.pkw .pkH.{nm}>.pkL.{key}{{left:{f(lx)}px;top:{f(ly)}px;width:{f(lw)}px;height:{f(lh)}px;animation:{name}V{key} {f(Lh)}s step-end {f(dl, 3)}s infinite}}'
                f'.pkw .pkH.{nm}>.pkL.{key}>i{{width:{f(tot)}px;height:{f(lh)}px;background:url({l["url"]}) 0 0/{f(tot)}px {f(lh)}px no-repeat;'
                f'animation:{name}F{key} {f(per, 4)}s steps({nf}) {f(dl, 3)}s infinite}}'
                + kf(f'{name}V{key}', vk)
                + kf(f'{name}F{key}', [(0, f'transform:translateX({f(-f0 * lw)}px)'), (100, f'transform:translateX({f(-(f0 + nf) * lw)}px)')]))
    html += '</i>'
    # 地面の うんち（落ちた 所に 残って、しばらく して 消える）
    dung_html, dung_css = '', ''
    if 'p' in lays and win['p']:
        pm = lays['p']
        fall = pm.get('fall', 8)
        for wi, (t0, t1) in enumerate(win['p']):
            for di, d in enumerate(pm.get('drops', [])):
                tl_ = t0 + (d['f'] + fall) * (2 * CYCLE / pm['frames'])
                X = pos(_dist(segs, v, tl_))
                r = d['r'] / 2
                xs, ys = X + (d['x'] - ax) / 2, d['g'] / 2
                cls = f'pkDg {nm}{wi}{di}'
                dung_html += f'<img class="{cls}" src="{durl(dung_svg(r))}" alt="">'
                a = tl_ / Lh * 100
                b = (tl_ + DUNG_STAY) / Lh * 100
                c = (tl_ + DUNG_STAY + 1.2) / Lh * 100
                rows = [(0, 'opacity:0'), (a, 'opacity:0'), (a + 0.002, 'opacity:1'), (min(b, 99.99), 'opacity:1'), (min(c, 100), 'opacity:0'), (100, 'opacity:0')]
                dung_css += (f'.pkw .pkDg.{nm}{wi}{di}{{left:{f(xs - 2 * r, 1)}px;top:{f(ys - 2 * r, 1)}px;width:{f(4 * r, 2)}px;height:{f(4 * r, 2)}px;'
                             f'animation:pkDg{nm}{wi}{di} {f(Lh)}s linear {f(dl, 3)}s infinite}}' + kf(f'pkDg{nm}{wi}{di}', rows))
    return html, css, dung_html, dung_css, evs


def dung_svg(r):
    """地面の うんち 1つ（4r × 4r の 絵の まん中：まわりの 影・ふち・まん中・つや）"""
    s = 4 * r
    c = s / 2
    return doc(s, s, f"<ellipse cx='{f(c)}' cy='{f(c + r * 0.86)}' rx='{f(r * 1.1)}' ry='{f(r * 0.32)}' fill='#3A2A10' opacity='.22'/>"
                     f"<circle cx='{f(c)}' cy='{f(c)}' r='{f(r)}' fill='#3E2C14'/><circle cx='{f(c - 0.12 * r)}' cy='{f(c - 0.12 * r)}' r='{f(r * 0.8)}' fill='#5A4220'/>"
                     f"<circle cx='{f(c - 0.38 * r)}' cy='{f(c - 0.4 * r)}' r='{f(r * 0.26)}' fill='#8A6A3A' opacity='.9'/>", vb=f'0 0 {f(s)} {f(s)}')


# ---------------------------------------------------------------- 上の絵（HTML と CSS）
def banner(B):
    still = B.get('still')
    alt = ('スタンドから見たパドックで、ゼッケンをつけた競走馬たちが歩いて回るイラスト。手前は右へ3頭（ゼッケン2・5・7）、おくは左へ3頭（ゼッケン1・4・8）。'
           'ひづめはいつも地面について、なめらかな足どりで歩く。ときどき首を激しく振ったり、首を下げて歩いたり、早歩きになったり、うんちをしたりする。'
           'まん中に芝生と花だん、白いさく、うしろにお客さんのスタンド（首を回して馬を目で追ったり、となりと話したり、座りなおしたり、立ち上がったり、手をあげたり、スマホで写真をとったり、新聞を広げたりする人がいる）と木、上に小さな旗のひも')
    html = f'<div class="pkw" role="img" aria-label="{alt}">'
    html += f'<img class="bnr" src="{still["url"]}" alt="">' if still else ''
    ppl = []
    html += img('pkBk', back_svg(ppl))
    ch, cc = crowd_parts(ppl)                                              # 動く お客さん（第4.96版）
    html += ch
    html += f'<i class="pkCl" style="background-image:url(&quot;{durl(clouds_svg())}&quot;)"></i>'
    css = ('.pkw{position:relative;flex:none;width:390px;height:160px;overflow:hidden;background:#DDF0F8}'
           '.pkw>*{position:absolute;display:block}'
           '.pkw .bnr{left:0;top:0;width:390px;height:160px;object-fit:cover}'
           '.pkw .pkBk,.pkw .pkIn,.pkw .pkLn{left:0;top:0;width:390px;height:160px}'
           f'.pkw .pkCl{{left:0;top:0;width:{2 * W + 2}px;height:34px;background-size:{W}px 34px;background-repeat:repeat-x;animation:pkCloud 80s linear infinite}}'
           '.pkw .pkPn{left:0;top:-2px;width:390px;height:24px;transform-origin:50% 0;animation:pkSway 4.2s ease-in-out infinite}'
           '.pkw .pkH{left:0;top:0;width:0;height:0;will-change:transform}'
           '.pkw .pkL{position:absolute;display:block;overflow:hidden}'
           '.pkw .pkL>i{display:block}'
           '.pkw .pkDg{display:block}')
    far_h, near_h, dung_h = '', '', ''
    for group, names in (('far', FAR), ('near', NEAR)):
        for k, nm in enumerate(names):
            if nm not in B:
                continue
            h, c, dh, dc, _ = horse_parts(nm, B, group, k)
            css += c + dc
            dung_h += dh
            if group == 'far':
                far_h += h
            else:
                near_h += h
    html += far_h + img('pkIn', infield_svg()) + img('pkLn', lane_svg()) + dung_h + near_h
    html += img('pkPn', pennants_svg())
    html += '</div>'
    css += (kf('pkCloud', [(0, 'transform:translateX(0)'), (100, f'transform:translateX({-W}px)')])
            + kf('pkSway', [(0, 'transform:rotate(-.6deg)'), (50, 'transform:rotate(.6deg)'), (100, 'transform:rotate(-.6deg)')]))
    css += cc
    css += reduced('.pkw .pkBk,.pkw .pkM,.pkw .pkHd,.pkw .pkCl,.pkw .pkIn,.pkw .pkLn,.pkw .pkH,.pkw .pkPn,.pkw .pkDg') if still else ''
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
    alt='スタンドから見たパドックで、ゼッケンをつけた競走馬たちがひづめを地面につけてなめらかに歩いて回るイラスト。ときどき首を振ったり首を下げて歩いたり早歩きになったりする。まん中に芝生と花だん、白いさく、うしろにお客さんのスタンド（首を回したり話したり立ち上がったりと、少しずつ動く）と木',
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
               pic='スタンドから 見た パドック・ゼッケンの 馬たちが 歩いて 回る（手前は 右へ・おくは 左へ・1回り 24コマの なめらかな 足・ひづめは いつも 同じ 地面の 線に つく）・ときどき 首を 激しく 振る・首を 下げて 歩く・早歩き・うんち・芝生と 花だん・白い さく・お客さんの スタンド（首を 回して 馬を 目で 追う・となりと 話す・座りなおす・立ち上がる・手を あげる・スマホで 写真・新聞を 広げる）・旗の ひも'),
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
