"""着せ替え（App Store版 第4弾：アップデート指示書 9章・16.1・16.1.1・16.2.1・16.4）：見本（themes20.py・boards.py・gen_fx.py・push_events.py・
   mock/base/main_v17 の 定番5）の 色・字・形・壁紙の動き・テーマの的中PUSH・テーマのボードを、アプリ（source/kisekae.js・fx.js）が使う形に束ねる。
     python3 build_kisekae.py <出力フォルダ>   … 確かめる用（ks_<id>.json を 30こ と ks.json（window.__KS の中身）を書く）
     build_pwa.py が TARGET=app のとき bundle_js()（index.html に入れる 小さい分）と write_payloads(out)（テーマごとの ks_<id>.json）を呼ぶ。
   束ねるもの
     window.__KS … themes（30テーマの 一覧：id・名前（9.1 の 新しい名前）・説明・組・値段・帯の枚数・暗いテーマか・小さな絵）
                   css（全テーマの 色の変数 → アプリの変数（--bg・--surface・--ink・--primary …）・共通の形の規則・壁紙の置き場・選ぶ画面・@font-face）
     ks_<id>.json … そのテーマだけの 大きい分：bnr（上の絵の HTML と CSS＝見本の 判定画面と同じ 動く壁紙）・push（的中の PUSH：面の SVG・押したあとの面・はじけるかけら・CSS）・
                    board（結果のボードの 変数と飾りの CSS・すみの飾り）。アプリは そのテーマを選んだときに 1回だけ読む
   見本の /_blob/<id> の絵は、アプリの中のファイル ks_<id>.webp（build_ios.py が ios/kisekae_blobs/ から入れる。リポジトリには入れない：1章の11）に置きかえる。
   CSS は 置き場の中だけに効かせる（壁紙＝#ksBnr・PUSHとボード＝.fxs）。@keyframes の名前には頭を付ける（壁紙 kb・PUSH fx）。HTML の style="animation:…" の名前も同じに直す。
   「視差効果を減らす」の @media の中身は .calm にも効かせる（設定の「演出を控えめにする」：16.6）。"""
import json
import os
import re
import sys

K = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(K)
if K not in sys.path:
    sys.path.insert(0, K)
import boards  # noqa: E402
import build_fx as BF  # noqa: E402
from themes20 import THEMES as T20  # noqa: E402
import pack as PK  # noqa: E402

THEMES_ALL = boards.THEMES_ALL
BY_ID = boards.BY_ID

# ---------------------------------------------------------------- 9.1：名前・値段・組・帯
NEW_NAMES = dict(newyear='お正月', gold='ぷりけつのお馬', pixel='ドット', kids='毛糸のお馬とロボット', cute='かわいいお馬さん', marble='大理石の馬', lucky='招き馬')
PRICE = {}
for _p, _ids in ((1000, ('sakura', 'sea', 'autumn', 'snow', 'newyear')), (2000, ('gold', 'news', 'ink', 'carousel', 'stars', 'sunset')),
                 (3000, ('ranch', 'silks', 'neon', 'pixel')), (4000, ('fireworks', 'kids', 'cute', 'night', 'xmas', 'halloween', 'valentine', 'whiteday')),
                 (7000, ('marble', 'chalk', 'lucky'))):
    for _i in _ids:
        PRICE[_i] = _p
BAND = dict(silver=8, golden=16, tengel=25)             # 帯の壁紙：ポイントで解放した壁紙の枚数（8.3）
PAID = sorted(PRICE)                                     # ポイントで解放する 26枚
assert len(PAID) == 26 and sum(PRICE.values()) == 82000, (len(PAID), sum(PRICE.values()))
# 第4.92版：壁紙パック（買い切り 1,500円・11枚・pack/）は いちばん上の 組（買う ボタンと 解放の 進み具合は kisekae.js が 組の 上に 出す）
GROUPS = [('壁紙パック', list(PK.IDS)),
          ('定番', ['default', 'ranch', 'cute', 'kids', 'gold']),
          ('季節・行事', ['sakura', 'sea', 'sunset', 'autumn', 'snow', 'newyear', 'fireworks', 'xmas', 'halloween', 'valentine', 'whiteday']),
          ('競馬', ['night', 'news', 'silks', 'lucky']),
          ('和・アート', ['ink', 'marble']),
          ('レトロ・ポップ', ['neon', 'pixel', 'chalk', 'carousel', 'stars']),
          ('帯', ['silver', 'golden', 'tengel'])]
ORDER = [i for _, ids in GROUPS for i in ids]
assert sorted(ORDER) == sorted(BY_ID), set(ORDER) ^ set(BY_ID)
OLD_DESC = dict(default='紺と金', ranch='黄緑・芝と馬', cute='ピンク・リボン', kids='ぬいぐるみ', gold='金ピカ・ゴージャス')
T20_BY = {t['id']: t for t in T20}
BLOBS20 = json.load(open(os.path.join(K, 'blobs20.json')))
THUMB_DEFAULT = 'c1fccd55173e28903228b7256479cc32'      # いつもの の 小さな絵（見本の 選ぶ画面と同じ）
BANNER_SVG = dict(ranch='banner_ranch.svg', cute='banner_cute.svg', kids='banner_kids.svg', gold='banner_gold.svg')   # 定番4の 止まった絵（kisekae/svg・リポジトリにある）
# 子供向けの 上の帯の もよう（キャンバスの 小さな SVG。中身は 文字なので ここに持つ：絵のファイルにしない）
KIDS_HD_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 10' width='12' height='10'><rect width='12' height='10' fill='#FFF3B8'/>"
               "<ellipse cx='3.1' cy='5' rx='2.5' ry='4.7' transform='rotate(-30 3.1 5)' fill='#F4DC82'/><ellipse cx='8.9' cy='5' rx='2.5' ry='4.7' transform='rotate(30 8.9 5)' fill='#F4DC82'/>"
               "<path d='M2 2.4 q1.2 1.6 1.6 4 M10 2.4 q-1.2 1.6 -1.6 4' stroke='#FFF7CF' stroke-width='.9' fill='none' stroke-linecap='round'/></svg>")
BLOB_DIR = os.environ.get('KISEKAE_ASSETS') or os.path.join(SRC, 'ios', 'kisekae_blobs')


def asset_name(bid):
    """見本の /_blob/<id> → アプリの中のファイル名（ks_<id>.webp。手元のフォルダに別の形があればその形）"""
    ext = 'webp'
    if os.path.isdir(BLOB_DIR):
        for f in os.listdir(BLOB_DIR):
            if f.startswith(bid + '.'):
                ext = f.split('.')[-1]
    return f'ks_{bid}.{ext}'


def kids_hd_uri():
    from urllib.parse import quote
    return 'url("data:image/svg+xml,' + quote(KIDS_HD_SVG, safe=" =:/;,.'()-_") + '")'


def replace_blobs(s):
    s = s.replace('/_blob/6656b0f19559a587df356e2178631b83', 'KIDSHD')   # 子供向けの帯（CSS の中の data URI にする）
    s = re.sub(r'/_blob/([0-9a-f]{32})', lambda m: asset_name(m.group(1)), s)
    return s.replace('url(KIDSHD)', kids_hd_uri())


# ---------------------------------------------------------------- 色の道具
def first_color(val, default=''):
    m = re.search(r'#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b|rgba?\([^)]*\)', val or '')
    return m.group(0) if m else default


def lum(hexcol):
    h = hexcol.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def is_dark(t):
    return lum(first_color(t['v']['bg'], '#FFFFFF')) < .25


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _hex(c):
    return bool(re.fullmatch(r'#[0-9A-Fa-f]{6}', (c or '').strip()))


def _mix(c, to, k):
    h = c.lstrip('#'); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    t = (0, 0, 0) if to == 'black' else (255, 255, 255)
    return '#%02X%02X%02X' % tuple(round(x + (y - x) * k) for x, y in zip((r, g, b), t))


# 小さい文字と背景のコントラストは 4.5 以上（9.2）。見本の値で足りない組は、文字が背景より暗ければ文字を少し暗く、文字のほうが明るければ背景を少し暗くする（色みは変えない）※仮
# （文字, 背景, 文字だけ直すか）。ページの背景（bg）の上の文字は pageInk／pageSub（見本の選ぶ画面と同じ：ないテーマは ink／sub）で、背景は変えない
PAIRS = (('btnInk', 'btn', False), ('tabInk', 'tab', False), ('tabOnInk', 'tabOn', False), ('znInk', 'znBg', False), ('tagInk', 'tagBg', False), ('hdInk', 'hd', False),
         ('sub', 'card', False), ('sub', 'zBg', False), ('ink', 'card', False), ('badgeInk', 'badge', False), ('warnInk', 'warnBg', False), ('btn2Ink', 'btn2', False), ('pillInk', 'pill', False),
         ('pageInk', 'bg', True), ('pageSub', 'bg', True))
MIN_C = 4.5


def fix_contrast(v):
    v = dict(v)
    v.setdefault('pageInk', v.get('ink')); v.setdefault('pageSub', v.get('sub'))
    fixed = []
    for fg, bg, text_only in PAIRS:
        a, b = v.get(fg), v.get(bg)
        if not (_hex(a) and _hex(b)) or contrast(a, b) >= MIN_C:
            continue
        a0, b0 = a, b
        for _ in range(80):
            if contrast(a, b) >= MIN_C:
                break
            if lum(a) < lum(b):
                a = _mix(a, 'black', .06)
            elif text_only:
                a = _mix(a, 'white', .06)
            else:
                b = _mix(b, 'black', .04)
        v[fg], v[bg] = a, b
        fixed.append((fg, a0, a, bg, b0, b, round(contrast(a, b), 2)))
    return v, fixed


DARK_SEM = ('--A:#7DB1EC;--A-bg:#16294A;--B:#F2BE55;--B-bg:#3A2C0D;--C:#F27399;--C-bg:#40162A;'
            '--ok:#5FD39A;--ok-bg:#123726;--warn:#F3A45B;--warn-bg:#3D2410;--bad:#F2867D;--bad-bg:#401A17;color-scheme:dark')
LIGHT_SEM = ('--A:#2C67A8;--A-bg:#E3EDF8;--B:#A86F00;--B-bg:#FBF0D6;--C:#B8264F;--C-bg:#FBE3EA;'
             '--ok:#17784A;--ok-bg:#DDF2E6;--warn:#A14E06;--warn-bg:#FCEBD9;--bad:#A8231B;--bad-bg:#F9E0DE;color-scheme:light')


def shadow_of_border(b):
    """'1.5px solid #8A93BF' → '0 0 0 1.5px #8A93BF'（馬番 2 の 黒い枠の ふち：box-shadow に）"""
    m = re.match(r'\s*([\d.]+)px\s+\w+\s+(.+)$', b or '')
    if not m or m.group(2).strip() in ('transparent',) or float(m.group(1)) == 0:
        return 'none'
    return f'0 0 0 {m.group(1)}px {m.group(2).strip()}'


# ---------------------------------------------------------------- テーマの 変数 → アプリの 変数
def app_vars(t):
    v = dict(boards.FALLBACK); v.update(t['v'])
    v, _ = fix_contrast(v)
    btn = v.get('btn') or v.get('gold') or v['acc']
    zn = v.get('znBg') or v.get('gold') or v['acc']
    line = first_color(v.get('cardB', '')) or first_color(v.get('tagLine', '')) or first_color(v.get('sep', '')) or v['sub']
    s2 = v.get('zBg') or v.get('tagBg') or v['card']
    out = dict(bg=v['bg'], surface=v['card'], ink=v['ink'], muted=v['sub'], line=line)
    out['surface-2'] = s2
    out['night'] = v['hd']; out['night-ink'] = v['hdInk']; out['lamp'] = first_color(v.get('iii', ''), v['acc'])
    out['primary'] = first_color(btn, v['acc']); out['primary-ink'] = v['btnInk']; out['focus'] = v['acc']; out['heat'] = v['acc']
    out['font-display'] = f"{v['dfont']},'Dela Gothic One','Hiragino Sans','Yu Gothic',sans-serif"
    out['font-body'] = f"{v['font']},'BIZ UDPGothic','Hiragino Sans','Hiragino Kaku Gothic ProN','Yu Gothic UI','Meiryo',sans-serif"
    out['r'] = v['radius']
    ks = dict(hd=v['hd'], hdB=v.get('hdB', '0 solid transparent'), logo=v['logo'], logoS=v['logoS'], dw=v['dw'],
              btn=btn, btnB=v['btnB'], btnR=v['btnR'], btnS=v['btnS'], btn2=v['btn2'], btn2Ink=v['btn2Ink'], btn2B=v['btn2B'],
              tab=v['tab'], tabB=v['tabB'], tabInk=v['tabInk'], tabOn=v['tabOn'], tabOnInk=v['tabOnInk'], tabR=v['tabR'],
              cardB=v['cardB'], cardO=v['cardO'], cardS=v['cardS'], rs=v['rs'], nR=v['nR'], zBg=v['zBg'], zB=v['zB'], znBg=zn, znInk=v.get('znInk', v['btnInk']),
              znR=v.get('znR', '6px'), tagBg=v['tagBg'], tagInk=v['tagInk'], tagLine=v['tagLine'], warnBg=v['warnBg'], warnInk=v['warnInk'],
              badge=v['badge'], badgeInk=v.get('badgeInk', v['acc']), badgeB=v['badgeB'], acc=v['acc'], h1=v.get('h1', v['acc']), sep=v['sep'],
              w2sh=shadow_of_border(v.get('w2B', '')), pill=v['pill'], pillLine=v['pillLine'], pillInk=v['pillInk'], pageInk=v['pageInk'], pageSub=v['pageSub'])
    for k, x in ks.items():
        out['ks-' + k] = x
    return out


# 見本の 選択子 → アプリの 選択子（テーマごとの 飾りの 規則：themes20 の css・main_v17 の .t-<id> …）
SEL_MAP = {'': 'body', '.hd': '.top', '.hd::after': '.top::after', '.logo': '.brand h1', '.h1': '.brand h1', '.lb': '.lbadge', '.lb b': '.lbadge .ll',
           '.card::before': '.card::before', '.card': '.card', '.card + .card': '.card+.card', '.mbtn': '.btn', '.pill': '.chip', '.seg': '.seg', '.tag': '.fchip',
           '.ocr': '.btn.primary', '.seg.on': '.seg button[aria-pressed="true"]', '.ch': '.card h2', '.tb': '.tabbar', '.tb::before': '.tabbar::before',
           '.tb button': '.tabbar button', '.tb button.on': '.tabbar button[aria-selected="true"]', '.bnr': '#ksBnr', '.vt': '.vkubun', '.zf': '.zflow',
           '.zn': '.zrank', '.iii i': '.brand h1 em', '.btn.sub': '.btn:not(.primary):not(.ghost):not(.danger)', '.n': '.num'}
SKIP_SEL = {'.coin', '.ct', '.acts'}
DROP_DECL = {'.lb': ('background',), '.tb': ('position',), '.tb button': ('font-weight',)}


def map_rules(t):
    out = []
    for sel, decl in t['rules']:
        parts = []
        for s in BF.split_top(sel, ','):
            s = s.strip()
            if s in SKIP_SEL:
                continue
            if s not in SEL_MAP:
                raise SystemExit(f'{t["id"]}：見本の選択子 {s!r} の アプリでの 置き場が 決まっていないよ（SEL_MAP）')
            parts.append(SEL_MAP[s])
        if not parts:
            continue
        ds = [d.strip() for d in BF.split_top(decl, ';') if d.strip()]
        drop = set()
        for s in BF.split_top(sel, ','):
            drop |= set(DROP_DECL.get(s.strip(), ()))
        ds = [d for d in ds if not any(d.startswith(k + ':') for k in drop)]
        if sel.strip() == '.iii i':
            ds = [d.replace('box-shadow:', 'text-shadow:') for d in ds]
        if not ds:
            continue
        root = f'html[data-ks="{t["id"]}"]'
        out.append(','.join(f'{root} {p}' for p in parts) + '{' + ';'.join(ds) + '}')
    return '\n'.join(out)


def theme_css(t):
    v = app_vars(t)
    sem = DARK_SEM if is_dark(t) else LIGHT_SEM
    head = f'html[data-ks="{t["id"]}"]{{' + ';'.join(f'--{k}:{x}' for k, x in v.items()) + ';' + sem + '}'
    return replace_blobs(head + '\n' + map_rules(t))


# 共通の形（どのテーマでも：--ks-… の変数で）。Web版の CSS には触らない（html[data-ks] の中だけ）
# 第4.85版（まさちゃん「ところどころ字体が違ったり、文字の太さが違ったり、文字の大きさが違うから、全体的に直して！ それぞれの壁紙のベースとなる字体に！」）：
#  選ぶ画面の 字の 太さを 700 まで・大きさを そろえた（下の /* 字 */）。この 文字列は そのまま アプリに 入るので、名前は ここ（Python の コメント）に 書く
COMMON_CSS = r'''
html[data-ks] body{background-color:var(--bg)}
html[data-ks] .top{background:var(--ks-hd);border-bottom:var(--ks-hdB)}
html[data-ks] .brand h1{color:var(--ks-logo);text-shadow:var(--ks-logoS);font-weight:var(--ks-dw)}
html[data-ks] .brand .ver{color:var(--night-ink)}
html[data-ks] .dbpill{border-color:var(--ks-pillLine);background:var(--ks-pill);color:var(--ks-pillInk)}
html[data-ks] .card{position:relative;border:var(--ks-cardB);outline:var(--ks-cardO);outline-offset:-7px;box-shadow:var(--ks-cardS)}
html[data-ks] .btn{border-radius:var(--ks-btnR)}
html[data-ks] .btn:not(.primary):not(.ghost):not(.danger){background:var(--ks-btn2);color:var(--ks-btn2Ink);border:var(--ks-btn2B)}
html[data-ks] .btn.primary{background:var(--ks-btn);color:var(--primary-ink);border:var(--ks-btnB);box-shadow:var(--ks-btnS)}
html[data-ks] .btn.primary:disabled{box-shadow:none}
html[data-ks] .tabbar{background:var(--ks-tab);border-top:var(--ks-tabB)}
html[data-ks] .tabbar button{color:var(--ks-tabInk);border-radius:var(--ks-tabR);margin:4px 3px 0}
html[data-ks] .tabbar button[aria-selected="true"]{background:var(--ks-tabOn);color:var(--ks-tabOnInk)}
html[data-ks] .tabbar button[aria-selected="true"] svg{color:var(--ks-tabOnInk)}
html[data-ks] .chip{background:var(--ks-tagBg);color:var(--ks-tagInk);border-color:var(--ks-tagLine)}
html[data-ks] .chip.ref{background:var(--ks-hd);color:var(--night-ink);border-color:transparent}
html[data-ks] .lbadge{border-radius:var(--ks-rs);border:var(--ks-badgeB)}
html[data-ks] .lbadge .ll,html[data-ks] .zrank,html[data-ks] .zr-no,html[data-ks] .lr-r,html[data-ks] .w5no,html[data-ks] .sep h2,html[data-ks] #setPoints .ptbig{font-weight:var(--ks-dw)}
html[data-ks] .zone{background:var(--ks-zBg);border:var(--ks-zB);border-radius:var(--ks-rs)}
html[data-ks] .zrank{display:inline-flex;align-items:center;justify-content:center;align-self:start;height:22px;padding:0 6px;border-radius:var(--ks-znR);background:var(--ks-znBg);color:var(--ks-znInk);font-size:12px}
html[data-ks] .zflow{color:var(--ks-acc)}
html[data-ks] .num{border-radius:var(--ks-nR)}
html[data-ks] .num.w2{box-shadow:inset 0 0 0 1px #5A5F6B,var(--ks-w2sh)}
html[data-ks] .banner.warn{background:var(--ks-warnBg);color:var(--ks-warnInk)}
html[data-ks] .zthird{border-top:var(--ks-sep)}
html[data-ks] .toast,html[data-ks] .minibar button{background:var(--ks-hd)}
html[data-ks] .fchip{border-radius:var(--ks-btnR)}
html[data-ks] .card h2{color:var(--muted)}
/* ページの背景の上に直に置く文字（記録の日付の見出し・実測の区切り・マザーデータの注意）：背景が暗くカードが明るいテーマ（ドット）でも読める色 */
html[data-ks] .sep h2,html[data-ks] .dgroup h3,html[data-ks] details.given>summary{color:var(--ks-pageInk)}
html[data-ks] .dgroup h3 .muted,html[data-ks] .mother-note{color:var(--ks-pageSub)}
html[data-ks] .sep::after{background:var(--ks-pageSub);opacity:.35}
/* 上の絵（壁紙）：判定タブのいちばん上に 390×160 の舞台を置いて、画面の幅に合わせて縮める（--ksk は kisekae.js が決める） */
#ksBnr{position:relative;overflow:hidden;margin:-16px -16px 14px;height:calc(160px * var(--ksk,1));background:var(--surface-2)}
#ksBnr[hidden]{display:none}
#ksBnr .ksb{position:absolute;left:50%;top:0;width:390px;height:160px;margin-left:-195px;transform:scale(var(--ksk,1));transform-origin:50% 0;overflow:hidden;color:var(--ink);font-family:"BIZ UDPGothic",sans-serif;-webkit-font-smoothing:antialiased}
#ksBnr .ksb *{box-sizing:border-box}
#ksBnr .bnr{display:block;width:390px;height:160px;object-fit:cover;max-width:none}
#ksBnr img{max-width:none}
#ksBnr .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
#ksBnr.pause *{animation-play-state:paused!important}
/* 選ぶ画面（設定 › 着せ替え） */
/* 字：太さは 700 まで（800 だと テーマの 本文の 字に 800 が なく、見出し用の 900 の 字（見出しの 字だけ しぼった もの）が 選ばれて、ない 字が 端末の 字に なる＝字体が まざる）。大きさも そろえる（第4.85版） */
#setKisekae .ksg{display:flex;align-items:center;gap:8px;margin:14px 0 8px;font-size:13.5px;font-weight:700}
#setKisekae .ksg small{display:inline-flex;align-items:center;height:19px;padding:0 7px;border-radius:999px;border:1px solid currentColor;font-size:11px;font-weight:700;opacity:.75}
#setKisekae .ksg::after{content:"";flex:1;height:1px;background:currentColor;opacity:.2}
#setKisekae .ksgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
#setKisekae .kst{position:relative;display:flex;flex-direction:column;align-items:stretch;padding:0 0 6px;margin:0;border:1px solid var(--line);border-radius:12px;background:var(--surface-2);color:inherit;overflow:hidden;text-align:left;cursor:pointer;font:inherit}
#setKisekae .kst.on{border-color:var(--primary);box-shadow:0 0 0 2px var(--primary)}
#setKisekae .kst .ksth{display:block;width:100%;height:58px;object-fit:cover;background:var(--line)}
#setKisekae .kst .ksn{display:block;padding:6px 7px 0;font-size:13px;font-weight:700;line-height:1.25}
#setKisekae .kst .ksd{display:block;padding:1px 7px 0;font-size:11.5px;color:var(--muted);line-height:1.3}
#setKisekae .kst .ksbadge{position:absolute;top:5px;left:5px;padding:1px 6px;border-radius:999px;background:var(--primary);color:var(--primary-ink);font-size:10.5px;font-weight:700}
#setKisekae .kst .kslock{display:block;margin:4px 7px 0;padding:2px 6px;border-radius:999px;background:var(--surface);border:1px solid var(--line);font-size:11.5px;font-weight:700;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#setKisekae .kst.lock .ksth{filter:saturate(.55) brightness(.92)}
#setKisekae .kst .kslive{position:absolute;left:0;top:0;width:100%;height:58px;overflow:hidden;pointer-events:none}
#setKisekae .kst .kslv{position:absolute;left:50%;top:50%;width:390px;height:160px;margin:-80px 0 0 -195px;transform:scale(var(--kss,.3625));transform-origin:50% 50%;overflow:hidden;color:var(--ink);font-family:"BIZ UDPGothic",sans-serif;-webkit-font-smoothing:antialiased}
#setKisekae .kst .kslv *{box-sizing:border-box}
#setKisekae .kst .kslv .bnr{display:block;width:390px;height:160px;object-fit:cover;max-width:none}
#setKisekae .kst .kslv img{max-width:none}
#setKisekae .kst .kslv .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
#setKisekae .kst .kslv.pause *{animation-play-state:paused!important}
#setKisekae .kst:focus-visible{outline:2px solid var(--primary);outline-offset:2px}
/* 解放の 確認（第4.64版）：タップした カギの 壁紙の タイルの 中・カギの 下に 出る（前は 一覧の 上の 1本の 帯） */
#setKisekae .kst.cf{border-color:var(--primary);box-shadow:0 0 0 2px var(--primary)}
#setKisekae .kst .ksconf{display:flex;flex-direction:column;gap:5px;margin:6px 6px 0;padding:7px 7px 6px;border-radius:9px;background:var(--surface);border:1px solid var(--line);font-size:12px;line-height:1.35;animation:ksCf .18s ease-out}
#setKisekae .kst .ksconf .kscq{display:block;font-weight:700}
#setKisekae .kst .ksconf .kscq small{display:block;font-size:11px;font-weight:400;color:var(--muted)}
#setKisekae .kst .ksconf .btn{width:100%;min-height:34px;padding:5px 4px;font-size:12.5px;line-height:1.2;white-space:normal;border-radius:8px;cursor:pointer}
#setKisekae .kst .ksconf .btn.ghost{min-height:28px;font-size:11.5px;color:var(--muted)}
@keyframes ksCf{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
#setKisekae .ksnums{display:flex;align-items:center;gap:5px;margin-top:8px;flex-wrap:wrap}
/* 壁紙パック（第4.92版）：組の 見出しの 下の 買う 箱・解放の 進み具合 */
#setKisekae .kspk{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 10px;align-items:center;margin:0 0 10px;padding:10px 12px;border:1.5px solid var(--primary);border-radius:12px;background:var(--surface)}
#setKisekae .kspk.on{grid-template-columns:minmax(0,1fr)}
#setKisekae .kspkt b{display:block;font-size:14px;font-weight:700;line-height:1.3}
#setKisekae .kspkt small{display:block;margin-top:2px;font-size:11.5px;color:var(--muted);line-height:1.35}
#setKisekae .kspk .btn.primary{min-height:38px;padding:6px 12px;font-size:13px;white-space:nowrap}
#setKisekae .kspkn{grid-column:1 / -1;margin:0;font-size:11.5px;line-height:1.45;color:var(--muted)}
#setKisekae .kspkr{grid-column:1 / -1;display:flex;justify-content:flex-end}
#setKisekae .kspkr .btn{min-height:30px;padding:4px 10px;font-size:12px}
#setKisekae .kspkb{height:7px;border-radius:999px;background:var(--surface-2);border:1px solid var(--line);overflow:hidden}
#setKisekae .kspkb i{display:block;height:100%;border-radius:inherit;background:var(--primary)}
#setKisekae .kst .kslock.pk{white-space:normal;overflow:visible;line-height:1.3;padding:3px 6px}
/* 壁紙パックの 解放の お知らせ（画面の 上・小さな 絵と「着せ替える」） */
#ksNote{position:fixed;left:50%;top:calc(var(--sat,0px) + 10px);z-index:80;transform:translateX(-50%);display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:10px;align-items:center;width:min(92vw,420px);padding:8px 10px;border-radius:14px;background:var(--surface);color:var(--ink);border:2px solid var(--primary);box-shadow:0 8px 22px rgba(0,0,0,.28);font-size:12.5px;line-height:1.4;animation:ksNote 6.5s ease-out both}
#ksNote img{width:72px;height:30px;border-radius:7px;object-fit:cover;display:block}
#ksNote b{display:block;font-size:14px;font-weight:700}
#ksNote .btn{min-height:34px;padding:5px 10px;font-size:12.5px;white-space:nowrap}
@keyframes ksNote{0%{opacity:0;transform:translate(-50%,-14px)}6%{opacity:1;transform:translate(-50%,0)}90%{opacity:1;transform:translate(-50%,0)}100%{opacity:0;transform:translate(-50%,-8px)}}
@media (prefers-reduced-motion:reduce){#ksNote{animation:ksNoteC 6.5s linear both}}
@keyframes ksNoteC{0%{opacity:0}5%{opacity:1}92%{opacity:1}100%{opacity:0}}
'''


# ---------------------------------------------------------------- テーマの 一覧（選ぶ画面・JS 用）
def theme_list():
    out = []
    for gname, ids in GROUPS:
        for tid in ids:
            t = BY_ID[tid]
            t20 = T20_BY.get(tid)
            name = NEW_NAMES.get(tid, t['name'])
            if tid == 'default':
                name = 'いつもの'
            desc = t20['desc'] if t20 else OLD_DESC[tid]
            if tid == 'tengel':
                desc = 'マスター帯（説明書の絵）'
            if tid in BANNER_SVG:
                thumb = 'ks_' + BANNER_SVG[tid]
            elif tid == 'default':
                thumb = asset_name(THUMB_DEFAULT)
            elif tid in PK.IDS:
                thumb = asset_name(PK.still_id(tid)) if PK.still_id(tid) else ''
            else:
                thumb = asset_name(BLOBS20[tid])
            row = dict(id=tid, name=name, desc=desc, group=gname, price=PRICE.get(tid, 0), band=BAND.get(tid, 0), dark=is_dark(t), thumb=thumb,
                       alt=(t20['alt'] if t20 else ''), fonts=[t['v']['font'].strip('"'), t['v']['dfont'].strip('"')], pc=push_code(tid))
            if tid in PK.IDS:
                row['pack'] = PK.ORDER.index(tid) + 1          # 壁紙パックの 解放の 順（1〜11：読み込み 5レースごと）
            out.append(row)
    return out


def push_code(tid):
    G = sys.modules.get('gen_fx')
    th = (G.THEMED.get('hit_' + tid) if G else None)
    if th:
        return th.get('push', '')
    # gen_fx を読まずに 知る（build_fonts など）：見本の THEMED と同じ表
    if tid in PK.IDS:
        return PK.push_code(tid)
    return dict(gold='gp', ranch='gr', sakura='sk', sea='se', autumn='mo', snow='yk', newyear='ny', news='np', ink='nk', carousel='mg', stars='sz', neon='nn', pixel='dp',
                fireworks='hn', kids='ke', cute='kw', sunset='ss', night='nb', marble='mb', lucky='kb', silks='sj', chalk='kk', silver='ag', golden='au', tengel='tg',
                xmas='xm', halloween='hw', valentine='vl', whiteday='wd').get(tid, '')


def push_fonts():
    """的中の PUSH で使う字（gen_fx.THEMED の fonts）。gen_fx を読まずに 返す（見本と同じ）"""
    out = set()
    for t in THEMES_ALL:
        if t['id'] != 'default':
            out |= set(t['fonts'])
    out.add('Zen+Kaku+Gothic+New:wght@400;500;700')
    return sorted(out)


# ---------------------------------------------------------------- @font-face（ios/fonts/ks/fonts.json：build_fonts.py が作る）
def fontface_css():
    p = os.path.join(SRC, 'ios', 'fonts', 'ks', 'fonts.json')
    if not os.path.exists(p):
        return ''
    rows = json.load(open(p, encoding='utf-8'))['fonts']
    return '\n'.join(f"@font-face{{font-family:'{r['family']}';src:url('fonts/{r['file']}') format('woff2');font-weight:{r['weight']};font-style:normal;font-display:swap}}" for r in rows) + '\n'


def font_files():
    p = os.path.join(SRC, 'ios', 'fonts', 'ks', 'fonts.json')
    if not os.path.exists(p):
        return []
    return [r['file'] for r in json.load(open(p, encoding='utf-8'))['fonts']]


# ---------------------------------------------------------------- 見本の HTML の style="animation:…" の名前も 直す
def rename_inline(html, names, kf):
    def fix_style(m):
        st = m.group(1)

        def fix(mm):
            segs = []
            for s in BF.split_top(mm.group(2), ','):
                toks = s.strip().split(None, 1)
                if toks and toks[0] in names:
                    toks[0] = kf + toks[0]
                segs.append(' '.join(toks))
            return mm.group(1) + ','.join(segs)
        st = re.sub(r'(animation(?:-name)?\s*:)([^;"]*)', fix, st)
        return f'style="{st}"'
    return re.sub(r'style="([^"]*)"', fix_style, html)


def kf_names(css):
    names = set()

    def collect(rs):
        for sel, body in rs:
            if sel.startswith('@keyframes'):
                names.add(sel.split()[1])
            elif sel.startswith('@media'):
                collect(BF.split_rules(body))
    collect(BF.split_rules(css))
    return names


def scoped(css, prefix, kf, html='', extra_names=()):
    """CSS を prefix の中だけに・@keyframes に kf を付ける（HTML の style の名前も）。extra_names＝ほかで定義ずみの @keyframes の名前（的中ボタンの共通の CSS の popIn・bob など）"""
    names = kf_names(css) | set(extra_names)
    out = BF.scope(css, prefix, kf)
    if extra_names:
        out = BF.scope.__globals__['re'].sub(r'(animation(?:-name)?\s*:)([^;}]*)', lambda m: m.group(1) + _ren(m.group(2), set(extra_names), kf), out)
    return out, (rename_inline(html, names, kf) if html else html)


def _ren(val, names, kf):
    segs = []
    for s in BF.split_top(val, ','):
        toks = s.strip().split()
        toks = [(kf + t if t in names else t) for t in toks]
        segs.append(' '.join(toks))
    return ','.join(segs)


def base_kf_names(G):
    """的中ボタンの共通の CSS（build_fx が .fxs に束ねたもの）の @keyframes の名前（fx を付ける前）"""
    return kf_names(G.COMMON_CSS + G.HIT_CSS + G.MISS_CSS + G.BIG_CSS + G.BURST_CSS + G.fz_css())


# ---------------------------------------------------------------- テーマごとの 大きい分（ks_<id>.json）
PUSH_FN = None


def _push_fns(G):
    """PUSHの面（押す前・押したあと）と はじけるかけら を作る関数：gen_fx.page() と同じ組み合わせ"""
    PE = G.PE
    return dict(
        gp=(lambda: '', lambda: '', lambda: ''),
        gr=(G.turf_svg, G.turf_svg, G.clippings),
        sk=(G.sakura_push_svg, G.sakura_push_svg, G.petal_burst),
        se=(G.sea_push_svg, G.sea_push_svg, G.water_burst),
        mo=(G.momiji_push_svg, lambda: G.momiji_push_svg('moP'), G.leaf_burst),
        yk=(G.snow_push_svg, lambda: G.snow_push_svg('2'), G.snow_burst),
        ny=(G.newyear_push_svg, lambda: G.newyear_push_svg('2'), G.gold_burst),
        np=(G.news_push_svg, lambda: G.news_push_svg('2'), G.paper_burst),
        nk=(G.ink_push_svg, lambda: G.ink_push_svg('2'), G.ink_burst),
        mg=(G.carousel_push_svg, lambda: G.carousel_push_svg('2'), G.carousel_burst),
        sz=(G.stars_push_svg, lambda: G.stars_push_svg('2'), G.stars_burst),
        sj=(G.silks_push_svg, lambda: G.silks_push_svg('2'), G.silks_burst),
        nn=(G.neon_push_svg, lambda: G.neon_push_svg('2'), G.neon_burst),
        dp=(G.pixel_push_svg, lambda: G.pixel_push_svg('2'), G.pixel_burst),
        hn=(G.fireworks_push_svg, lambda: G.fireworks_push_svg('2'), G.fireworks_burst),
        ke=(G.keito_push_svg, lambda: G.keito_push_svg('2'), G.keito_burst),
        kw=(G.kawaii_push_svg, lambda: G.kawaii_push_svg('2'), G.kawaii_burst),
        ss=(G.sunset_push_svg, lambda: G.sunset_push_svg('2'), G.sunset_burst),
        nb=(G.night_push_svg, lambda: G.night_push_svg('2'), G.night_burst),
        mb=(G.marble_push_svg, lambda: G.marble_push_svg('2'), G.marble_burst),
        kb=(G.koban_push_svg, lambda: G.koban_push_svg('2'), G.koban_burst),
        kk=(G.chalk_push_svg, lambda: G.chalk_push_svg('2'), G.chalk_burst),
        ag=(lambda: G.metal_push_svg('ag'), lambda: G.metal_push_svg('ag', '2'), lambda: G.metal_burst('ag')),
        au=(lambda: G.metal_push_svg('au'), lambda: G.metal_push_svg('au', '2'), lambda: G.metal_burst('au')),
        tg=(G.tengel_push_svg, lambda: G.tengel_push_svg('2'), G.tengel_burst),
        **{c: ((lambda c=c: PE.push_svg(c)), (lambda c=c: PE.push_svg(c, '2')), (lambda c=c: PE.burst(c))) for c in PE.CODES})


def _push_css(G, pc):
    PE = G.PE
    return dict(gp=G.GP_CSS, gr=G.GR_CSS, sk=G.SK_CSS, se=G.SE_CSS, mo=G.MO_CSS, yk=G.YK_CSS, ny=G.NY_CSS, np=G.NP_CSS, nk=G.NK_CSS, mg=G.MG_CSS, sz=G.SZ_CSS,
                sj=G.SJ_CSS, nn=G.NN_CSS, dp=G.DP_CSS, hn=G.HN_CSS, ke=G.KE_CSS, kw=G.KW_CSS, ss=G.SS_CSS, nb=G.NB_CSS, mb=G.MB_CSS, kb=G.KB_CSS, kk=G.KK_CSS,
                ag=G.AG_CSS, au=G.AU_CSS, tg=G.TG_CSS, **PE.CSS)[pc]


def board_part(tid):
    t = BY_ID[tid]
    css = BF.scope(boards.board_theme_css(tid), '.fxs', 'fx')     # 変数・飾り・ボードだけの 直し（boards.BOARD_EXTRA：第4.89版 海の 波）
    vb, body = t['orn']
    oc = ' o34' if vb.endswith('44 34') else ' o40' if vb.endswith('40 40') else ''
    orn = f'<svg class="orn{oc}" viewBox="{vb}" aria-hidden="true">{body}</svg>' if body else ''
    return dict(css=replace_blobs(css), orn=orn)


def payload(tid, G):
    out = dict(id=tid, bnr=None, push=None, board=board_part(tid))
    th = G.THEMED.get('hit_' + tid)
    if th and th.get('banner'):
        html, css = G.theme_banner(th['banner'])
        css, html = scoped(css, '#ksBnr', 'kb', html)
        out['bnr'] = dict(html=replace_blobs(html), css=replace_blobs(css))
    if th and th.get('push'):
        pc = th['push']
        f_push, f_pressed, f_burst = _push_fns(G)[pc]
        css = _push_css(G, pc)
        css, html = scoped(css, '.fxs', 'fx', f_push() + '\x00' + f_pressed() + '\x00' + f_burst(), extra_names=base_kf_names(G))
        a, b, c = html.split('\x00')
        out['push'] = dict(pc=pc, svg=replace_blobs(a), pressed=replace_blobs(b), burst=replace_blobs(c), css=replace_blobs(css))
    return out


def asset_ids(G=None):
    """アプリに入れる 見本の絵の id（上の絵・動きの絵・PUSHの絵・小さな絵）"""
    ids = set(BLOBS20.values()) | {THUMB_DEFAULT}
    if G is None:
        G = BF.load_gen_fx()
    for tid in ORDER:
        p = payload(tid, G)
        s = json.dumps(p, ensure_ascii=False)
        for m in re.finditer(r'ks_([0-9a-f]{32})\.', s):
            ids.add(m.group(1))
    return sorted(ids)


def write_payloads(out, G=None):
    """テーマごとの ks_<id>.json と 定番4の 止まった絵（SVG）を out に書く。返り値：使う 絵の id"""
    if G is None:
        G = BF.load_gen_fx()
    ids = set(BLOBS20.values()) | {THUMB_DEFAULT}
    for tid in ORDER:
        p = payload(tid, G)
        s = json.dumps(p, ensure_ascii=False, separators=(',', ':'))
        assert '/_blob/' not in s, tid
        for m in re.finditer(r'ks_([0-9a-f]{32})\.', s):
            ids.add(m.group(1))
        open(os.path.join(out, f'ks_{tid}.json'), 'w', encoding='utf-8').write(s)
    for tid, fn in BANNER_SVG.items():
        # 選ぶ画面の タイルの 絵：止まった 絵に（牧場・ぷりけつの SVG は 動く CSS が 入って いる → animation:none を 足す。第4.89版：
        #   まさちゃん「普段は壁紙は動かさないで、タップして選択しているときだけ壁紙が動くようにして！」。判定タブの 上の絵は 別（inline））
        svg = open(os.path.join(K, 'svg', fn), encoding='utf-8').read()
        if '</style>' in svg:
            svg = svg.replace('</style>', '*{animation:none!important}</style>', 1)
        open(os.path.join(out, 'ks_' + fn), 'w', encoding='utf-8').write(svg)
    return sorted(ids)


def bundle():
    css = COMMON_CSS + '\n'.join(theme_css(BY_ID[tid]) for tid in ORDER) + '\n' + fontface_css()
    return dict(themes=theme_list(), css=css, band=dict(BAND), paid=PAID, v=1,
                pack=dict(ids=list(PK.IDS), order=list(PK.ORDER), product=PK.PRODUCT, every=PK.EVERY, name=PK.CAT_NAME))


def bundle_js():
    s = json.dumps(bundle(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return 'window.__KS=' + s + ';'


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(K, 'ks_out')
    os.makedirs(out, exist_ok=True)
    G = BF.load_gen_fx()
    ids = write_payloads(out, G)
    b = bundle()
    json.dump(b, open(os.path.join(out, 'ks.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    sizes = {f: os.path.getsize(os.path.join(out, f)) for f in sorted(os.listdir(out))}
    print('ks.json css', len(b['css']), 'themes', len(b['themes']), 'assets', len(ids))
    print({k: v for k, v in sizes.items() if k.startswith('ks_')})
