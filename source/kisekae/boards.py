"""結果のボード（テーマごと・30テーマ）：的中・デカ的中・ど的中・隠れど的中・ハズレ。馬は出さない（まさちゃんの指定で撤廃）。
   ボードは「そのテーマの判定画面をぎゅっと小さくしたもの」：テーマの背景のもよう（ボードのふち）・上の帯（見出し）・カード・タグ・
   色・字・すみの飾りを、判定画面と同じ変数（--bg・--hd・--card・--tagBg …）と同じ飾りのルールで使う。
   色はテーマの変数のまま（判定画面で文字と背景のコントラスト4.5以上を確かめた値）。
   使い方：from boards import THEMES_ALL, CAT_ORDER, board_css, board_html, font_links
     board_css(['ranch'])              → 見本の画面に入れるCSS（ボードの共通の形＋そのテーマの変数と飾り）
     board_html('ranch', 'hit', bets, total, race='9R')  → ボードのHTML（kind：hit・big・fz・hidden・miss）"""
import os
import re
from themes20 import THEMES as T20, CATS

K = os.path.dirname(os.path.abspath(__file__))
# 置き場所：作業フォルダでは canvas/project、リポジトリでは mock/（gen_fx.py・gen_main.py と同じ）
P = f'{K}/canvas/project' if os.path.isdir(f'{K}/canvas/project') else f'{K}/mock'
BASE = f'{K}/canvas' if os.path.isdir(f'{K}/canvas/project') else f'{K}/mock/base'


def split_decl(block):
    """'a:b;c:url(x;y)' を ; で分ける（かっこ・引用符の中の ; では切らない）"""
    out, cur, depth, q = [], '', 0, ''
    for ch in block:
        if q:
            cur += ch
            if ch == q:
                q = ''
            continue
        if ch in '"\'':
            q = ch
        elif ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ';' and depth == 0:
            out.append(cur)
            cur = ''
            continue
        cur += ch
    if cur.strip():
        out.append(cur)
    return out


def vars_of(block):
    v = {}
    for kv in split_decl(block):
        if ':' in kv and kv.strip().startswith('--'):
            k, val = kv.split(':', 1)
            v[k.strip()[2:]] = val.strip()
    return v


# ---------------------------------------------------------------- 定番の5つ（いつもの・牧場・かわいい・子供向け・カッコいい）
# 変数：選ぶ画面の元の版（main_v17）の .t-<id>{…} に、判定画面（Judge_<名前>.dc.html）の .ph{--…} を重ねる（判定画面の値を優先）
OLD = [('default', 1, 'いつもの', 'Default', ['Dela+Gothic+One']),
       ('ranch', 1, '牧場', 'Ranch', ['Zen+Maru+Gothic:wght@500;700;900']),
       ('cute', 1, 'かわいい', 'Cute', ['Hachi+Maru+Pop', 'M+PLUS+Rounded+1c:wght@500;700;800']),
       ('kids', 1, '子供向け', 'Kids', ['Mochiy+Pop+One', 'Zen+Maru+Gothic:wght@500;700']),
       ('gold', 1, 'カッコいい', 'Gold', ['Dela+Gothic+One', 'Zen+Kaku+Gothic+New:wght@400;500;700'])]

# すみの飾り（判定画面のカードと同じ所）：かわいい＝リボン・子供向け＝フェルトの星（判定画面の絵そのまま）。
# いつもの・牧場・カッコいいは判定画面に飾りがないので、ボード用に小さく描いた（金の星・蹄鉄・金の王冠）
ORN_OLD = {
    'default': ('0 0 44 44', '<path d="M22 4 L26.6 16.4 L39.8 16.9 L29.4 25 L33 37.8 L22 30.4 L11 37.8 L14.6 25 L4.2 16.9 L17.4 16.4 Z" fill="#E2A23B" stroke="#161F3D" stroke-width="2.2" stroke-linejoin="round"></path>'
                '<path d="M22 10 L24.6 17.6" stroke="#FFF1C8" stroke-width="2" stroke-linecap="round"></path>'),
    'ranch': ('0 0 44 44', '<path d="M11 33 C5 25 6 11 15 7 C19 5.2 25 5.2 29 7 C38 11 39 25 33 33 L28.6 30.6 C32.4 24.6 32 14.6 26.4 12.2 C23.8 11.2 20.2 11.2 17.6 12.2 C12 14.6 11.6 24.6 15.4 30.6 Z" '
              'fill="#B98A3A" stroke="#5A3A1A" stroke-width="2" stroke-linejoin="round"></path>'
              '<path d="M13 31.6 L16.8 29.4 M27.2 29.4 L31 31.6" stroke="#5A3A1A" stroke-width="2.2" stroke-linecap="round"></path>'
              + ''.join(f'<circle cx="{x}" cy="{y}" r="1.5" fill="#FFF3D0"></circle>' for x, y in ((10.6, 23), (11.4, 16.4), (15.2, 10.6), (33.4, 23), (32.6, 16.4), (28.8, 10.6)))),
    'gold': ('0 0 44 44', '<path d="M6 32 L8.4 13 L16 22 L22 8 L28 22 L35.6 13 L38 32 Z" fill="#E9C25A" stroke="#6B5014" stroke-width="2" stroke-linejoin="round"></path>'
             '<path d="M6.6 35 H37.4" stroke="#C9972B" stroke-width="4" stroke-linecap="round"></path>'
             '<circle cx="22" cy="8" r="2.6" fill="#FFF1B8" stroke="#6B5014" stroke-width="1.4"></circle><circle cx="8.4" cy="13" r="2.2" fill="#FFF1B8" stroke="#6B5014" stroke-width="1.4"></circle>'
             '<circle cx="35.6" cy="13" r="2.2" fill="#FFF1B8" stroke="#6B5014" stroke-width="1.4"></circle><path d="M14 28 H30" stroke="#FFF1B8" stroke-width="1.6" stroke-linecap="round" opacity=".8"></path>'),
}


def _old_themes():
    main = open(f'{BASE}/main_v17.dc.html', encoding='utf-8').read()
    style = re.search(r'<style>\n(.*?)\n</style>', main, re.S).group(1)
    out = []
    for tid, cat, name, page, fonts in OLD:
        v = vars_of(re.search(r'\n\.t-' + tid + r'\{([^}]*)\}', style).group(1))
        judge = open(f'{P}/Judge_{page}.dc.html', encoding='utf-8').read()
        for m in re.finditer(r'(?:^|\n)\.ph\{([^}]*--bg:[^}]*)\}', judge):
            v.update(vars_of(m.group(1)))
        rules = []
        for m in re.finditer(r'\n(\.t-' + tid + r'([ .:][^{]*))\{([^}]*)\}', style):
            sels = []
            for s in m.group(1).split(','):
                s = s.strip()
                s = re.sub(r'^\.t-' + tid + r'\.ph\b', '', s)          # 画面ぜんたい → ボードのふち
                s = re.sub(r'^\.t-' + tid + r'\s*', '', s)
                sels.append(s)
            rules.append((','.join(sels), m.group(3)))
        orn = ORN_OLD.get(tid)
        if tid == 'cute':
            orn = ('0 0 44 34', re.search(r'<svg class="cbow" viewBox="0 0 44 34"[^>]*>(.*?)</svg>', judge, re.S).group(1))
        if tid == 'kids':
            orn = ('0 0 40 40', re.search(r'<svg class="felt" viewBox="0 0 40 40"[^>]*>(.*?)</svg>', judge, re.S).group(1))
        out.append(dict(id=tid, cat=cat, name=name, fonts=fonts, v=v, rules=rules, orn=orn))
    return out


def _new_themes():
    out = []
    for t in T20:
        rules = []
        for sel, decl in t['css']:
            if sel.endswith('{border-radius:0}'):          # まとめ書き（SEG_SQ）
                s0, d0 = sel.split('{', 1)
                sel, decl = s0, d0.rstrip('}')
            rules.append((sel, decl))
        out.append(dict(id=t['id'], cat=t['cat'], name=t['name'], fonts=t['fonts'], v=dict(t['v']), rules=rules, orn=('0 0 44 44', t['orn'])))
    return out


THEMES_ALL = _old_themes() + _new_themes()
BY_ID = {t['id']: t for t in THEMES_ALL}
# キャンバスと同じ並び：定番 → 季節・行事 → 競馬 → 和・アート → 帯（ミッション）→ レトロ・ポップ
CAT_ORDER = [1, 2, 3, 4, 6, 5]
ORDERED = [t for c in CAT_ORDER for t in THEMES_ALL if t['cat'] == c]


def solid(val):
    """グラデーションの色の値から、ふちの下に敷く1色（最初の色）"""
    m = re.search(r'#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b|rgba?\([^)]*\)', val)
    return m.group(0) if m else '#FFFFFF'


# ボードで使う変数（判定画面と同じ名前）。ないテーマは下の FALLBACK
KEYS = ['bg', 'ink', 'sub', 'card', 'cardB', 'cardO', 'cardS', 'radius', 'rs', 'font', 'dfont', 'dw', 'logo', 'logoS', 'hd', 'hdInk', 'hdB',
        'tagBg', 'tagInk', 'tagLine', 'zBg', 'zB', 'acc', 'h1', 'nR', 'w2B', 'sep', 'coin', 'coinInk']
FALLBACK = dict(hdB='0 solid transparent', cardO='0 solid transparent', zBg='rgba(0,0,0,.04)', zB='0 solid transparent', sep='1px solid rgba(0,0,0,.12)',
                rs='10px', nR='7px', w2B='0 solid transparent', tagBg='transparent', tagInk='var(--sub)', tagLine='currentColor')


def theme_vars(t):
    v = dict(FALLBACK)
    v.update({k: t['v'][k] for k in KEYS if k in t['v']})
    if 'h1' not in t['v']:
        v['h1'] = t['v'].get('acc', 'var(--ink)')
    v['rbFace'] = solid(v['card'])            # 3連単の行の虹色のふちの内側に敷く色（カードが単色でないテーマ用）
    return ';'.join(f'--{k}:{val}' for k, val in v.items())


def scoped(rules, root):
    """テーマの飾りのルールを、ボードの中だけに効くようにする（'' ＝ ボードのふち＝判定画面の背景のもよう）"""
    out = []
    for sel, decl in rules:
        parts = []
        for s in sel.split(','):
            s = s.strip()
            parts.append(root if s == '' else f'{root} {s}')
        out.append(','.join(parts) + '{' + decl + '}')
    return '\n'.join(out)


# ---------------------------------------------------------------- ボードの共通の形（色・字・角の丸みはテーマの変数）
BOARD_CSS = r'''
/* ===== 結果のボード（テーマの判定画面と同じ見た目・馬は出さない） =====
   ふち（.rb）＝テーマの背景のもよう → 上の帯（.hd）＝見出し → カード（.card）＝買い目。すみにテーマの飾り（.orn） */
.rb{position:relative;width:350px;padding:8px;border-radius:calc(var(--radius) + 8px);background-color:var(--bg);color:var(--ink);text-align:left;
  font-family:var(--font),"BIZ UDPGothic",sans-serif;-webkit-font-smoothing:antialiased;box-shadow:0 0 0 1.5px rgba(255,255,255,.6),0 18px 38px rgba(0,0,0,.45)}
.rb .hd{position:relative;z-index:1;display:block;flex:none;padding:13px 12px 14px;border-radius:var(--radius);background:var(--hd);color:var(--hdInk);border-bottom:var(--hdB);text-align:center}
.rb .bh{display:inline-block;max-width:100%;margin:0;font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:34px;line-height:1.12;color:var(--logo);text-shadow:var(--logoS);white-space:nowrap}
/* 見出しの大きさはそろえる（テーマのロゴの大きさの決まりより強く） */
.rb.rb .hd .bh{font-size:34px}
.rb.rb.miss .hd .bh,.rb.rb.fz .hd .bh{font-size:30px}
.rb .bh .bx3{margin-left:-.18em;letter-spacing:-.42em}
/* 見出しの字を まん中に（まさちゃん「全部の結果ボードの的中の、文字が若干左よりになってる 中心に合わせて」）：
   最後の字（.bz）の うしろに 字間を つけない・全角の「！」（.bzx）は 字の はばの 右の あき（約0.35字）を つめる（全角の「！」は 字の まん中に 細く 書いてあるので） */
.rb .bh .bz{letter-spacing:0}
.rb .bh .bzx{margin-right:-.35em}
.rb .bsub{display:block;margin-top:6px;font-size:12.5px;font-weight:700;line-height:1.3;color:var(--hdInk);white-space:nowrap}
.rb .card{position:relative;flex:none;margin-top:9px;padding:13px 11px 12px;background:var(--card);border:var(--cardB);outline:var(--cardO);outline-offset:-7px;border-radius:var(--radius);box-shadow:var(--cardS)}
.rb .orn{position:absolute;top:-15px;right:12px;width:44px;height:44px;pointer-events:none;overflow:visible;z-index:2}
.rb .orn.o34{height:34px;top:-12px}
.rb .orn.o40{width:40px;height:40px;top:-13px}
.rb .brows{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.rb .brows li{display:flex;flex-wrap:wrap;align-items:center;gap:2px 4px;padding:6px 8px;border-radius:var(--rs);background:var(--zBg);border:var(--zB);white-space:nowrap}
/* 払戻が長くて入らないときは、払戻だけ次の行へ（右によせる） */
.rb .bt{flex:none;display:inline-flex;align-items:center;justify-content:center;min-width:44px;height:22px;padding:0 8px;border-radius:999px;background:var(--tagBg);color:var(--tagInk);border:1px solid var(--tagLine);font-size:11.5px;font-weight:800}
.rb .bc{display:flex;align-items:center;gap:2px;flex:none}
.rb .n{display:inline-flex;align-items:center;justify-content:center;min-width:24px;height:24px;padding:0 5px;border-radius:var(--nR);font:700 12.5px/1 "BIZ UDPGothic",sans-serif}
.rb .w1{background:#FFFFFF;color:#1F1F1F;border:1.5px solid #9AA0A6}
.rb .w2{background:#222222;color:#FFFFFF;border:var(--w2B)}
.rb .w3{background:#E0322B;color:#FFFFFF}
.rb .w4{background:#1F5FC9;color:#FFFFFF}
.rb .w5{background:#F3C316;color:#1F1F1F}
.rb .w6{background:#1E8E3E;color:#FFFFFF}
.rb .w7{background:#F08A1C;color:#1F1F1F}
.rb .w8{background:#F27BB0;color:#1F1F1F}
.rb .ar{color:var(--sub);font-weight:700;padding:0 1px}
.rb .by{font-size:11px;color:var(--sub)}
.rb .bp{margin-left:auto;font-size:14.5px;font-weight:800;color:var(--acc)}
.rb .btot{display:flex;align-items:baseline;justify-content:flex-end;gap:8px;margin-top:10px;padding-top:9px;border-top:var(--sep);font-size:12.5px;font-weight:700;color:var(--sub)}
.rb .btot b{font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:24px;line-height:1;color:var(--ink)}
/* ハズレ：見出しは上の帯の文字の色で静かに・払戻は0円（うすく） */
.rb.miss .bh{color:var(--hdInk);text-shadow:none}
.rb.miss .bp,.rb.miss .btot b{color:var(--sub)}
.rb.miss .bp{font-weight:700}
/* デカ的中：まわりが光る・見出しは虹色（黒いふち）・3連単の行は虹色のふち */
.rb.big{box-shadow:0 0 0 3px rgba(255,255,255,.95),0 0 26px 6px rgba(255,236,160,.85),0 18px 38px rgba(0,0,0,.45)}
.rb.big .bh,.rb.fz .bh{background:linear-gradient(90deg,#FF3B3B,#FF9F1A,#FFD21A,#2DBB55,#1FA8E0,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;
  filter:drop-shadow(1.5px 0 0 #1E1030) drop-shadow(-1.5px 0 0 #1E1030) drop-shadow(0 1.5px 0 #1E1030) drop-shadow(0 -1.5px 0 #1E1030) drop-shadow(0 3px 0 rgba(0,0,0,.25))}
.rb.big .brows li.top,.rb.fz .brows li.top{position:relative;background:linear-gradient(var(--zBg),var(--zBg)) padding-box,linear-gradient(var(--rbFace),var(--rbFace)) padding-box,
  linear-gradient(90deg,#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3BB8) border-box;border:2px solid transparent;gap:2px 3px;padding:4px 5px}
/* ど的中・隠れど的中：枠は虹色（回さない）・炎に光る・見出しの下に帯（超大穴の馬／デカ的中が化けた） */
.rb.fz{padding:11px;box-shadow:0 0 0 3px #FFFFFF,0 0 28px 8px rgba(255,236,170,.9),0 0 64px 18px rgba(255,120,0,.6),0 12px 24px rgba(0,0,0,.35)}
.rb.fz::before{content:"";position:absolute;inset:0;border-radius:inherit;padding:4px;pointer-events:none;
  background:conic-gradient(from 200deg,#FF3B3B,#FF9F1A,#FFE53B,#3BE26A,#2FD6FF,#4C6BFF,#B34CFF,#FF3BB8,#FF3B3B);
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
.rb.fz .brows li.top::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;background:linear-gradient(105deg,rgba(255,255,255,0) 30%,rgba(255,255,255,.75) 50%,rgba(255,255,255,0) 70%) -130% 0/50% 100% no-repeat}
.rb.fz .btot b{background:linear-gradient(90deg,#FF3B3B,#FFE53B,#3BE26A,#2FD6FF,#B34CFF,#FF3BB8) 0 100%/100% 3px no-repeat;padding-bottom:4px}
.rb .zrib{display:flex;align-items:center;justify-content:center;gap:6px;width:max-content;max-width:100%;margin:8px auto 0;padding:3px 10px 3px 4px;border-radius:999px;background:#2A1259;color:#FFFFFF;
  font-size:12px;font-weight:700;white-space:nowrap;box-shadow:0 0 0 2px #FFFFFF,0 0 12px rgba(179,76,255,.7)}
.rb .zrib .zt{padding:3px 8px;border-radius:999px;background:linear-gradient(180deg,#FFF3B0,#FFC21A);color:#2A1259;font-weight:800;font-size:11.5px}
.rb .zrib .n{min-width:22px;height:22px;font-size:12px}
.rb .n.zx{box-shadow:0 0 0 2px #FFFFFF,0 0 0 4px #FF3BB8,0 0 10px 4px rgba(255,59,184,.6)}
'''


def board_css(ids):
    """ボードの共通の形＋テーマ（ids）の変数と飾り"""
    out = [BOARD_CSS]
    for tid in ids:
        t = BY_ID[tid]
        root = f'.rb.t-{tid}'
        out.append(f'{root}{{{theme_vars(t)}}}')
        if t['rules']:
            out.append(scoped(t['rules'], root))
    return '\n'.join(out) + '\n'


def font_links(ids, extra=()):
    fams = list(extra)
    for tid in ids:
        for f in BY_ID[tid]['fonts']:
            if f not in fams:
                fams.append(f)
    return '\n'.join(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={f}&amp;display=swap">' for f in fams)


TITLES = dict(hit='的中！', big='デカ的中!!', fz='ど的中！！！', hidden='隠れど的中！！！', miss='ハズレ',   # ど的中はまさちゃんの指定（前は「フリーズ的中!!!」）
              gd='神様的中！！！', sgd='超神様的中！！！')   # 第4.51版（まさちゃんの指定）：神様的中・超神様的中の ボードの 見出し（ボードの 形は ど的中の まま）


def title_html(kind):
    """見出しの字：全角の「！」が3つ続くところは字の間をつめる（.bx3）。最後の字は .bz（全角の「！」なら .bz.bzx：右の あきを つめて まん中に）"""
    t = TITLES[kind]
    head, last = t[:-1], t[-1]
    if t.endswith('！！！'):
        head = head[:-2] + '<span class="bx3">！！</span>'
    return f'{head}<span class="bz{" bzx" if last == "！" else ""}">{last}</span>'


def board_html(tid, kind, rows, total, race='9R', rib='', cls='', head=None):
    """kind：hit・big・fz・hidden・miss ／ rows：<li>…</li> を並べたもの ／ rib：見出しの下の帯（ど的中・隠れど的中）
       head：見出しだけ ちがう 字に する 時の TITLES の キー（神様的中＝gd・超神様的中＝sgd。ボードの 形は kind の まま）"""
    t = BY_ID[tid]
    vb, body = t['orn']
    oc = ' o34' if vb.endswith('44 34') else ' o40' if vb.endswith('40 40') else ''
    orn = f'<svg class="orn{oc}" viewBox="{vb}" aria-hidden="true">{body}</svg>' if body else ''
    k = 'fz' if kind in ('fz', 'hidden') else kind
    logo = '' if kind == 'miss' else ' logo'
    sub = f'{race} の買い目' if kind == 'miss' else f'{race} の当たった買い目'
    title = title_html(head or kind)
    return (f'<div class="rb {k} t-{tid}{cls}"><div class="hd"><div class="bh{logo}">{title}</div><div class="bsub">{sub}</div>{rib}</div>'
            f'<div class="card">{orn}<ul class="brows">{rows}</ul><div class="btot">払戻 合計<b>{total}</b></div></div></div>')
