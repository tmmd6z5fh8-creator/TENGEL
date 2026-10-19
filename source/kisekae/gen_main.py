"""着せ替えを選ぶ画面（Main.dc.html：いつもの＋定番4＋新しいテーマ）と、新しいテーマのメモ（Guide20.dc.html）を作る
   python3 gen_main.py blobs.json [Mainの高さ] [Guide20の高さ]"""
import os, re, sys, json
from themes20 import THEMES, CATS
from gen_screens import ORDER, MAIN_EXTRA, vars_css, scoped, font_links, tabs, SVG_A

K = os.path.dirname(os.path.abspath(__file__))
P = f'{K}/canvas/project' if os.path.isdir(f'{K}/canvas/project') else f'{K}/mock'
BASE = f'{K}/canvas' if os.path.isdir(f'{K}/canvas/project') else f'{K}/mock/base'   # 元の版（v17）
blobs = json.load(open(sys.argv[1]))
MAIN_H = int(sys.argv[2]) if len(sys.argv) > 2 else 0
GUIDE_H = int(sys.argv[3]) if len(sys.argv) > 3 else 0

OLD = [dict(id='default', cat=1, name='いつもの', desc='紺と金（いま）', img=''),
       dict(id='ranch', cat=1, name='牧場', desc='黄緑・芝と馬', img='/_blob/4d32303d3e8ea65630ceca0f8b0b72e6'),
       dict(id='cute', cat=1, name='かわいい', desc='ピンク・リボン', img='/_blob/465d11c7ef7de2047fdb27179b0d752b'),
       dict(id='kids', cat=1, name='子供向け', desc='ぬいぐるみ', img='/_blob/cd5641f66475221eecd307120d918b18'),
       dict(id='gold', cat=1, name='カッコいい', desc='金ピカ・ゴージャス', img='/_blob/4055cb4c8c928f84b366d05700100ca1')]
ALL = OLD + [dict(id=t['id'], cat=t['cat'], name=t['name'], desc=t['desc'], img='/_blob/' + blobs[t['id']]) for t in THEMES]

# ---------------------------------------------------------------- 今の Main から、元の5テーマの CSS とフォントを取り出す
src = open(f'{BASE}/main_v17.dc.html', encoding='utf-8').read()     # 元の版から（何度作り直しても同じ結果）
old_link = re.search(r'<link rel="stylesheet" href="https://fonts.googleapis.com/css2\?family=BIZ[^>]+>', src).group(0)
style = re.search(r'<style>\n(.*?)\n</style>', src, re.S).group(1)
cut = style.index('\n.t-default{')
base, old_themes = style[:cut], style[cut:].strip('\n')

# 選ぶ画面の土台：縦に長い全体・グループ見出し・暗いテーマ用のページ文字色
base = base.replace('.ph{width:390px;height:844px;', '.ph{width:390px;height:HEIGHT;')
base = base.replace('.hd{position:relative;z-index:2;flex:none;padding:10px 16px 12px;background:var(--hd);color:var(--hdInk)}',
                    '.hd{position:relative;z-index:2;flex:none;padding:10px 16px 12px;background:var(--hd);color:var(--hdInk);border-bottom:var(--hdB)}')
base = base.replace('.lead{font-size:12.5px;line-height:1.6;color:var(--sub);margin:5px 0 0}',
                    '.lead{font-size:12.5px;line-height:1.6;color:var(--pageSub,var(--sub));margin:5px 0 0}')
base = base.replace('.lead b{color:var(--acc)}', '.lead b{color:var(--pageAcc,var(--acc))}')
base = base.replace('.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:12px 14px 0}',
                    '.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:8px 14px 0}\n'
                    '.gh{display:flex;align-items:center;gap:8px;margin:18px 16px 0;font-size:13.5px;font-weight:800;line-height:1.3;color:var(--pageInk,var(--ink))}\n'
                    '.gh small{display:inline-flex;align-items:center;height:19px;padding:0 7px;border-radius:999px;border:1px solid currentColor;font-size:10.5px;font-weight:700;opacity:.75}\n'
                    '.gh::after{content:"";flex:1;height:1px;background:currentColor;opacity:.2}\n'
                    '.oname.sm{font-size:12px;letter-spacing:-.02em;white-space:nowrap}')
for k in ('.thumb{display:block;width:100%;height:58px;object-fit:cover}', '.thumb-d{'):
    assert k in base, k
assert 'HEIGHT' in base and '--pageSub' in base and '.gh{' in base and 'var(--hdB)' in base

new_blocks = []
for t in THEMES:
    root = '.t-' + t['id']
    new_blocks.append(root + '{' + vars_css(t['v'], ORDER + MAIN_EXTRA) + '}\n' + scoped(t['css'], root))
css = base + '\n\n' + old_themes + '\n\n' + '\n\n'.join(new_blocks)

fonts = []
for t in THEMES:
    for f in t['fonts']:
        if f not in fonts:
            fonts.append(f)
links = old_link + '\n' + font_links(fonts)


def card_btn():
    return '''      <button type="button" class="{{t.cls}}" onClick="{{t.pick}}" aria-pressed="{{t.pressed}}" aria-label="{{t.label}}">
        <sc-if value="{{t.hasImg}}" hint-placeholder-val="{{true}}"><img class="thumb" src="{{t.img}}" alt=""></sc-if>
        <sc-if value="{{t.noImg}}" hint-placeholder-val="{{false}}"><span class="thumb-d"><img src="/_blob/c1fccd55173e28903228b7256479cc32" alt=""></span></sc-if>
        <span class="ob"><span class="{{t.ncls}}">{{t.name}}</span><span class="odesc">{{t.desc}}</span></span>
        <sc-if value="{{t.sel}}" hint-placeholder-val="{{false}}"><span class="badge">使用中</span></sc-if>
      </button>'''


groups = ''
for c in sorted(CATS):
    n = sum(1 for t in ALL if t['cat'] == c)
    if n == 0:
        continue
    groups += (f'  <h2 class="gh">{CATS[c]}<small>{n}</small></h2>\n  <div class="grid">\n'
               f'    <sc-for list="{{{{g{c}}}}}" as="t" hint-placeholder-count="{n}">\n' + card_btn() + '\n    </sc-for>\n  </div>\n')

js_list = ',\n'.join(f"      {{ id: '{t['id']}', g: {t['cat']}, name: '{t['name']}', desc: '{t['desc']}', img: '{t['img']}' }}" for t in ALL)
enum = json.dumps([t['id'] for t in ALL], ensure_ascii=False)

main = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>設定 › 着せ替え</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{links}
<style>
{css}
</style>
</helmet>
<div class="{{{{rootCls}}}}">
  <header class="hd">
    <div class="hd-r1">
      <div class="logo">テンゲル<span class="sr">Ⅲ</span><span class="iii" aria-hidden="true"><i></i><i></i><i></i></span></div>
      <button class="mbtn" type="button"><svg {SVG_A}><path d="M3.5 5.5h6a2.5 2.5 0 0 1 2.5 2.5v11a2 2 0 0 0-2-2H3.5z"></path><path d="M20.5 5.5h-6A2.5 2.5 0 0 0 12 8v11a2 2 0 0 1 2-2h6.5z"></path></svg>説明書</button>
    </div>
    <div class="hd-r2">
      <span class="pill"><span class="coin">P</span>1,100 P</span>
      <span class="pill"><span class="gdot"></span>マザーデータ1 290走・記録 0件</span>
    </div>
  </header>
  <section class="sec">
    <h1 class="h1">着せ替え</h1>
    <p class="lead">いまのテーマ：<b>{{{{curName}}}}</b>。見た目だけが変わるよ。判定・記録・ポイントはそのまま。</p>
  </section>
{groups}  <div class="note">
    <p>馬番の枠の色は、どのテーマでも同じだよ（読み間違えないように）</p>
    <div class="nums"><span class="n w1">1</span><span class="n w2">2</span><span class="n w3">3</span><span class="n w4">4</span><span class="n w5">5</span><span class="n w6">6</span><span class="n w7">7</span><span class="n w8">8</span></div>
  </div>
  <div class="sp"></div>
  {tabs('set').replace('SVGA', SVG_A)}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"startTheme":{{"editor":"enum","options":{enum},"default":"sakura"}},"$preview":{{"width":390,"height":{MAIN_H or 1700}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    var st = this.state || {{}};
    var theme = st.theme || this.props.startTheme || 'sakura';
    var self = this;
    var list = [
{js_list}
    ];
    var cur = list.filter(function (t) {{ return t.id === theme; }})[0] || list[5];
    var items = list.map(function (t) {{
      var on = t.id === cur.id;
      return {{
        g: t.g, id: t.id, name: t.name, desc: t.desc, img: t.img,
        hasImg: !!t.img, noImg: !t.img, sel: on, ncls: t.name.length > 6 ? 'oname sm' : 'oname',
        cls: on ? 'opt on' : 'opt',
        pressed: on ? 'true' : 'false',
        label: t.name + '（' + t.desc + '）に着せ替える',
        pick: function () {{ self.setState({{ theme: t.id }}); }}
      }};
    }});
    function grp(n) {{ return items.filter(function (t) {{ return t.g === n; }}); }}
    return {{ rootCls: 'ph t-' + cur.id, curName: cur.name, GROUPS }};
  }}
}}
</script>
</body>
</html>
'''
main = main.replace('GROUPS', ', '.join(f'g{c}: grp({c})' for c in sorted(CATS) if any(t['cat'] == c for t in ALL)))
main = main.replace('HEIGHT', f'{MAIN_H}px' if MAIN_H else 'auto;min-height:844px')
open(f'{P}/Main.dc.html', 'w', encoding='utf-8').write(main)

# ---------------------------------------------------------------- Guide20（新しいテーマのメモ）
gsrc = open(f'{BASE}/guide_v17.dc.html', encoding='utf-8').read()
gstyle = re.search(r'<style>\n(.*?)\n</style>', gsrc, re.S).group(1)
gstyle = gstyle.replace('.gd{width:1320px;height:900px;', '.gd{width:1320px;height:GH;')
gstyle += ('\n.cat{display:inline-flex;align-items:center;height:20px;padding:0 8px;border-radius:999px;background:#EEEAE0;color:#5C6272;font-size:11px;font-weight:700;margin-bottom:6px}'
           '\n.cols{row-gap:14px}')


NNEW = len(THEMES)
NCATS = '／'.join(f"{CATS[c]}{sum(1 for t in THEMES if t['cat'] == c)}" for c in sorted(CATS) if any(t['cat'] == c for t in THEMES))


GCOL = dict(tengel='#13505E', sakura='#A3355C', sea='#0B5E96', sunset='#6A2E8E', autumn='#A33A16', snow='#23608F', newyear='#B0141B', fireworks='#D63A6E',
            night='#9A6200', news='#141414', silks='#1A3FB8', lucky='#B71C1C', shogi='#6B4423', ink='#1A1A1A', marble='#8A6A38', ryuma='#A87C22', silver='#3A424B', golden='#8A6514', chess='#111111',
            neon='#C81FB0', pixel='#1D2B53', chalk='#24423A', carousel='#B83A74', stars='#4A3F8F')


def guide_col(t):
    g = t['guide']
    sw = ''.join(f'<div class="sw"><i style="background:{c}"></i><span>{lab}　{c}</span></div>' for c, lab in g['colors'])
    v = t['v']
    nm_col = GCOL[t['id']]
    fam = v['dfont'].replace('"', "'")
    return f'''    <section class="col">
      <img class="th" src="/_blob/{blobs[t['id']]}" alt="{t['name']}の絵">
      <div class="cb">
        <div><span class="cat">{CATS[t['cat']]}</span><h2 class="nm" style="font-family:{fam},sans-serif;font-weight:{v['dw']};color:{nm_col}">{t['name']}</h2><div class="sub">{t['desc']}</div></div>
        <div><div class="lab">色</div><div class="sws">{sw}</div></div>
        <div><div class="lab">文字</div><p class="tx">{g['fonts']}</p></div>
        <div><div class="lab">形</div><p class="tx">{g['shape']}</p></div>
        <div><div class="lab">絵</div><p class="tx">{g['pic']}</p></div>
      </div>
    </section>'''


cols = '\n'.join(guide_col(t) for t in THEMES)
dfonts = []
for t in THEMES:
    if t['fonts'][0] not in dfonts:
        dfonts.append(t['fonts'][0])
guide = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>新しい{NNEW}個のテーマのメモ</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{font_links(['BIZ+UDPGothic:wght@400;700', 'Dela+Gothic+One'] + dfonts)}
<style>
{gstyle.replace('GH', f'{GUIDE_H}px' if GUIDE_H else 'auto')}
</style>
</helmet>
<div class="gd">
  <div class="top">
    <div>
      <h1 class="t1">新しい{NNEW}個のテーマのメモ（仮）</h1>
      <p class="t2">{NCATS}。絵はぜんぶ一から描いたオリジナル（テンゲルだけはアプリの説明書の絵）。色・文字・形は判定画面の見本と同じ。</p>
    </div>
    <div class="chg">
      <div class="box"><h3>どのテーマも同じところ</h3><p>判定の中身・画面の並び（上の帯 → 絵 → レース情報 → 判定の結果）・馬番の枠の色・タブの並び</p></div>
      <div class="box"><h3>テーマごとに変わるところ</h3><p>色・背景のもよう・文字・角の丸さ・枠と影・「第1」の札・Aの札・帯の飾り・カードのすみの小さな飾り</p></div>
    </div>
  </div>
  <div class="cols">
{cols}
  </div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1320,"height":{GUIDE_H or 2400}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''
open(f'{P}/Guide20.dc.html', 'w', encoding='utf-8').write(guide)
print('Main', len(main), 'Guide20', len(guide))
