"""新しい20個の判定画面（Judge_*.dc.html）を作る ＋ 文字と背景のコントラストを調べる
   python3 gen_screens.py blobs.json   （blobs.json：{"sakura": "<blob id>", ...}。無ければ仮のid）"""
import os, re, sys, json
from themes20 import THEMES

K = os.path.dirname(os.path.abspath(__file__))
# 置き場所：作業フォルダでは canvas/project、リポジトリでは mock/
OUT = f'{K}/canvas/project' if os.path.isdir(f'{K}/canvas/project') else f'{K}/mock'
BOARD = {'sakura': 'Sakura', 'sea': 'Sea', 'sunset': 'Sunset', 'autumn': 'Autumn', 'snow': 'Snow', 'newyear': 'NewYear', 'fireworks': 'Fireworks',
         'night': 'Night', 'news': 'News', 'silks': 'Silks', 'lucky': 'Lucky', 'shogi': 'Shogi', 'ink': 'Ink', 'marble': 'Marble', 'chess': 'Chess',
         'ryuma': 'Ryuma', 'neon': 'Neon', 'pixel': 'Pixel', 'chalk': 'Chalk', 'carousel': 'Carousel', 'stars': 'Stars'}

ORDER = ['bg', 'ink', 'sub', 'card', 'cardB', 'cardO', 'cardS', 'radius', 'rs', 'font', 'dfont', 'dw', 'logo', 'logoS', 'iii', 'iiiB', 'iiiR', 'hd', 'hdInk', 'hdB',
         'mBg', 'mLine', 'mInk', 'pill', 'pillLine', 'pillInk', 'coin', 'coinInk', 'badge', 'badgeInk', 'badgeB', 'tagBg', 'tagInk', 'tagLine', 'warnBg', 'warnInk',
         'zBg', 'zB', 'znBg', 'znInk', 'znB', 'znR', 'znS', 'acc', 'nR', 'w2B', 'sep', 'btn', 'btnInk', 'btnB', 'btnR', 'btnS', 'btn2', 'btn2Ink', 'btn2B',
         'tab', 'tabB', 'tabInk', 'tabOn', 'tabOnInk', 'tabR']
MAIN_EXTRA = ['sel', 'selInk', 'h1', 'pageInk', 'pageSub', 'pageAcc']


def vars_css(v, keys):
    return ';'.join(f'--{k}:{v[k]}' for k in keys if k in v)


def scoped(css, root):
    """('.hd', 'x:y') → root が '.ph' なら '.hd{..}'、'.t-sea' なら '.t-sea .hd{..}'"""
    out = []
    for sel, decl in css:
        if sel.endswith('{border-radius:0}'):          # まとめ書き（SEG_SQ）
            s0, d0 = sel.split('{', 1)
            sel, decl = s0, d0.rstrip('}')
        parts = []
        for s in sel.split(','):
            s = s.strip()
            if root == '.ph':
                parts.append('.ph' if s == '' else s)
            else:
                parts.append(f'{root}.ph' if s == '' else f'{root} {s}')
        out.append(','.join(parts) + '{' + decl + '}')
    return '\n'.join(out)


def font_links(fonts):
    return '\n'.join(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={f}&amp;display=swap">' for f in fonts)


BASE_CSS = r'''body{margin:0}
*{box-sizing:border-box}
.ph{VARS}
.ph{width:390px;height:844px;position:relative;overflow:hidden;display:flex;flex-direction:column;background-color:var(--bg);color:var(--ink);font-family:var(--font),sans-serif;-webkit-font-smoothing:antialiased}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.hd{position:relative;z-index:2;flex:none;padding:10px 16px 12px;background:var(--hd);color:var(--hdInk);border-bottom:var(--hdB)}
.hd-r1{display:flex;align-items:center;justify-content:space-between;height:42px}
.logo{display:flex;align-items:center;font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:26px;line-height:1;color:var(--logo);text-shadow:var(--logoS)}
.iii{display:inline-flex;gap:3px;margin-left:6px}
.iii i{display:block;width:5.5px;height:21px;background:var(--iii);border:var(--iiiB);border-radius:var(--iiiR)}
.mbtn{display:inline-flex;align-items:center;gap:6px;height:38px;padding:0 15px;border-radius:999px;border:1.5px solid var(--mLine);background:var(--mBg);color:var(--mInk);font-family:var(--font),sans-serif;font-weight:700;font-size:14px;cursor:pointer}
.mbtn svg{width:18px;height:18px}
.hd-r2{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:6px}
.pill{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 11px;border-radius:999px;background:var(--pill);border:1px solid var(--pillLine);color:var(--pillInk);font-weight:700;font-size:12.5px;white-space:nowrap}
.coin{width:17px;height:17px;border-radius:50%;background:var(--coin);color:var(--coinInk);display:inline-flex;align-items:center;justify-content:center;font:900 10px/1 "BIZ UDPGothic",sans-serif}
.gdot{width:8px;height:8px;border-radius:50%;background:#3CCB84;flex:none}
.bnr{flex:none;display:block;width:390px;height:160px;object-fit:cover}
.ct{flex:1;min-height:0;overflow:hidden;padding:14px 14px 0;display:flex;flex-direction:column;gap:12px}
.card{position:relative;flex:none;background:var(--card);border:var(--cardB);outline:var(--cardO);outline-offset:-7px;border-radius:var(--radius);box-shadow:var(--cardS);padding:14px}
.ch{margin:0 0 9px;font-size:13px;font-weight:700;color:var(--sub)}
.mrow{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.seg{display:inline-flex;align-items:center;gap:4px;height:31px;padding:0 12px;border-radius:999px;border:1.5px dashed var(--tagLine);color:var(--sub);font-size:12.5px;font-weight:700;background:var(--tagBg)}
.seg.on{background:var(--btn);color:var(--btnInk);border:1.5px solid transparent}
.seg small{font-size:10.5px;font-weight:400;opacity:.85}
.ocr{display:inline-flex;align-items:center;gap:8px;height:42px;margin-top:11px;padding:0 16px;border-radius:var(--btnR);border:var(--btnB);background:var(--btn);color:var(--btnInk);box-shadow:var(--btnS);font-family:var(--font),sans-serif;font-weight:700;font-size:14.5px;cursor:pointer}
.ocr svg{width:19px;height:19px}
.hint{margin:7px 0 0;font-size:12px;color:var(--sub)}
.vh{display:flex;gap:12px;align-items:flex-start}
.lb{flex:none;width:66px;height:80px;border-radius:var(--rs);background:var(--badge);color:var(--badgeInk);border:var(--badgeB);display:flex;flex-direction:column;align-items:center;justify-content:center}
.lb b{font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:40px;line-height:1}
.lb small{font-size:12px;font-weight:700;margin-top:4px}
.vi{min-width:0;flex:1}
.vt{font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:20px;line-height:1.25;margin:0;color:var(--ink)}
.vs{font-size:12px;line-height:1.55;color:var(--sub);margin:4px 0 7px}
.vs b{color:var(--ink);font-size:13.5px}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tag{display:inline-flex;align-items:center;height:24px;padding:0 9px;border-radius:999px;font-size:11.5px;font-weight:700;background:var(--tagBg);color:var(--tagInk);border:1px solid var(--tagLine)}
.tag.warn{background:var(--warnBg);color:var(--warnInk);border-color:transparent}
.zs{list-style:none;margin:12px 0 0;padding:0;display:flex;flex-direction:column;gap:9px}
.z{background:var(--zBg);border:var(--zB);border-radius:var(--rs);padding:10px 12px}
.zh{display:flex;align-items:center;gap:10px}
.zn{display:inline-flex;align-items:center;justify-content:center;height:22px;padding:0 8px;border-radius:var(--znR);background:var(--znBg);color:var(--znInk);border:var(--znB);font-size:12px;font-weight:800;box-shadow:var(--znS)}
.zf{font-family:var(--dfont),sans-serif;font-weight:var(--dw);font-size:18px;line-height:1.2;color:var(--acc)}
.nums{display:flex;align-items:center;gap:5px;margin-top:8px}
.ar{color:var(--sub);font-weight:700;padding:0 3px}
.zr{font-size:12px;line-height:1.5;color:var(--sub);margin-top:7px}
.zr b{color:var(--ink);font-size:13px}
.n{display:inline-flex;align-items:center;justify-content:center;min-width:30px;height:30px;padding:0 6px;border-radius:var(--nR);font:700 15px/1 "BIZ UDPGothic",sans-serif}
.w1{background:#FFFFFF;color:#1F1F1F;border:1.5px solid #9AA0A6}
.w2{background:#222222;color:#FFFFFF;border:var(--w2B)}
.w4{background:#1F5FC9;color:#FFFFFF}
.w5{background:#F3C316;color:#1F1F1F}
.w6{background:#1E8E3E;color:#FFFFFF}
.w7{background:#F08A1C;color:#1F1F1F}
.third{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:11px;padding-top:11px;border-top:var(--sep)}
.tl{font-size:13px;font-weight:800;color:var(--ink)}
.tl small{display:block;font-size:11px;font-weight:500;color:var(--sub);margin-top:2px}
.third .nums{margin-top:0;gap:4px}
.third .n{min-width:26px;height:26px;font-size:13px}
.sl{color:var(--sub);font-weight:700;padding:0 2px}
.acts{display:flex;gap:8px;margin-top:14px}
.btn{flex:1;height:42px;display:inline-flex;align-items:center;justify-content:center;gap:6px;border-radius:var(--btnR);border:var(--btnB);background:var(--btn);color:var(--btnInk);box-shadow:var(--btnS);font-family:var(--font),sans-serif;font-weight:700;font-size:14px;cursor:pointer}
.btn.sub{background:var(--btn2);color:var(--btn2Ink);border:var(--btn2B);box-shadow:none}
.btn svg{width:17px;height:17px}
.tb{flex:none;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:2px;padding:6px 6px 22px;background:var(--tab);border-top:var(--tabB)}
.tb button{display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 0 5px;margin:0;border:0;background:transparent;color:var(--tabInk);font-family:var(--font),sans-serif;font-size:10.5px;font-weight:700;border-radius:var(--tabR);cursor:pointer;white-space:nowrap}
.tb button.on{background:var(--tabOn);color:var(--tabOnInk)}
.tb svg{width:23px;height:23px}
.orn{position:absolute;top:-15px;right:14px;width:44px;height:44px;pointer-events:none;overflow:visible}'''

SVG_A = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
BODY = '''<div class="ph">
  <header class="hd">
    <div class="hd-r1">
      <div class="logo">テンゲル<span class="sr">Ⅲ</span><span class="iii" aria-hidden="true"><i></i><i></i><i></i></span></div>
      <button class="mbtn" type="button"><svg SVGA><path d="M3.5 5.5h6a2.5 2.5 0 0 1 2.5 2.5v11a2 2 0 0 0-2-2H3.5z"></path><path d="M20.5 5.5h-6A2.5 2.5 0 0 0 12 8v11a2 2 0 0 1 2-2h6.5z"></path></svg>説明書</button>
    </div>
    <div class="hd-r2">
      <span class="pill"><span class="coin">P</span>1,100 P</span>
      <span class="pill"><span class="gdot"></span>マザーデータ1 290走・記録 0件</span>
    </div>
  </header>
  <img class="bnr" src="/_blob/BLOB" alt="ALT">
  <main class="ct">
    <section class="card">
      <h2 class="ch">レース情報</h2>
      <div class="mrow"><span class="seg on">マザーデータ1 <small>290走</small></span><span class="seg">マザーデータ2 <small>空</small></span></div>
      <button class="ocr" type="button"><svg SVGA><path d="M4 8.5h3l1.6-2.5h6.8L17 8.5h3v10H4z"></path><circle cx="12" cy="13.2" r="3.4"></circle></svg>オッズ画像から読み取る</button>
      <p class="hint">単勝・複勝と3連単人気順のスクショを1〜3枚</p>
    </section>
    <section class="card">
      <svg class="orn" viewBox="0 0 44 44" aria-hidden="true">ORN</svg>
      <div class="vh">
        <div class="lb"><b>A</b><small>堅</small></div>
        <div class="vi">
          <h2 class="vt">9R　A層（固定）</h2>
          <p class="vs">比 <b>8.8</b>（3連単1位 18.5 ÷ 単勝1位 2.1）・12頭・1400m ダ・良</p>
          <div class="tags"><span class="tag">マザー：マザーデータ1</span><span class="tag warn">【薄】</span></div>
        </div>
      </div>
      <ol class="zs">
        <li class="z">
          <div class="zh"><span class="zn">第1</span><span class="zf">人気 → 人気</span></div>
          <div class="nums"><span class="n w5">6</span><span class="n w2">2</span><span class="n w7">10</span><span class="ar">→</span><span class="n w5">6</span><span class="n w2">2</span><span class="n w7">10</span></div>
          <div class="zr">参考的中率 <b>56.1%</b>（A層での実測／n=164）</div>
        </li>
        <li class="z">
          <div class="zh"><span class="zn">第2</span><span class="zf">人気 → 中穴</span></div>
          <div class="nums"><span class="n w5">6</span><span class="n w2">2</span><span class="n w7">10</span><span class="ar">→</span><span class="n w6">7</span><span class="n w1">1</span><span class="n w4">4</span></div>
          <div class="zr">参考的中率 <b>20.7%</b>（A層での実測／n=164）</div>
        </li>
      </ol>
      <div class="third">
        <div class="tl">3着：人気・中穴<small>2本で84.1%</small></div>
        <div class="nums"><span class="n w5">6</span><span class="n w2">2</span><span class="n w7">10</span><span class="sl">／</span><span class="n w6">7</span><span class="n w1">1</span><span class="n w4">4</span></div>
      </div>
      <div class="acts">
        <button class="btn sub" type="button"><svg SVGA><rect x="8" y="8" width="11" height="12" rx="2"></rect><path d="M5 15.5V5.5a1.5 1.5 0 0 1 1.5-1.5H15"></path></svg>全文コピー</button>
        <button class="btn" type="button"><svg SVGA><path d="M5 4.5h11l3 3v12H5z"></path><path d="M8 4.5v5h7v-5M8 19.5v-5h8v5"></path></svg>判定と結果を保存</button>
      </div>
    </section>
  </main>
  TABS
</div>'''

TABS = '''<nav class="tb" aria-label="タブ">
    <button type="button" ONCLS><svg SVGA><path d="M4 10.5 12 4l8 6.5V20h-5.5v-5.5h-5V20H4z"></path></svg>判定</button>
    <button type="button"><svg SVGA><path d="M3.5 7h17v3a2 2 0 0 0 0 4v3h-17v-3a2 2 0 0 0 0-4z"></path><path d="M14.5 7.5v9" stroke-dasharray="1.6 2"></path></svg>単勝5連予想</button>
    <button type="button"><svg SVGA><path d="M6.5 3.5h8l4 4v13h-12z"></path><path d="M14.5 3.5v4h4M9.5 12h6M9.5 16h6"></path></svg>記録</button>
    <button type="button"><svg SVGA><path d="M4 20h16M7.5 16.5v-4M12 16.5V7.5M16.5 16.5v-6.5"></path></svg>実測・回収</button>
    <button type="button" SETCLS><svg SVGA><circle cx="12" cy="12" r="3.2"></circle><path d="M12 3.5v2.6M12 17.9v2.6M3.5 12h2.6M17.9 12h2.6M6 6l1.8 1.8M16.2 16.2 18 18M6 18l1.8-1.8M16.2 7.8 18 6"></path></svg>設定</button>
  </nav>'''


def tabs(on='judge'):
    a = 'class="on" aria-current="page"'
    return (TABS.replace('ONCLS', a if on == 'judge' else '').replace('SETCLS', a if on == 'set' else '')
            .replace('<button type="button" >', '<button type="button">'))


def judge_html(t, blob):
    css = BASE_CSS.replace('VARS', vars_css(t['v'], ORDER)) + '\n' + scoped(t['css'], '.ph')
    body = (BODY.replace('TABS', tabs('judge')).replace('SVGA', SVG_A).replace('BLOB', blob).replace('ALT', t['alt']).replace('ORN', t['orn']))
    return f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>判定画面・{t['name']}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{font_links(['BIZ+UDPGothic:wght@700'] + t['fonts'])}
<style>
{css}
</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":390,"height":844}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


# ---------------------------------------------------------------- コントラスト
def hexes(s):
    return re.findall(r'#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b', s)


def rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lum(c):
    f = lambda x: x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def solid(val, base):
    """色の値（#hex・rgba・transparent）を base の上に重ねた色（候補のリスト）"""
    val = val.strip()
    if val == 'transparent':
        return list(base) if isinstance(base, list) else [base]
    m = re.match(r'rgba\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)', val.replace(' ', ''))
    if m:
        r, g, b, a = (float(x) for x in m.groups())
        out = []
        for bb in base if isinstance(base, list) else [base]:
            br = rgb(bb) if isinstance(bb, str) else bb
            out.append(tuple((c / 255) * a + bc * (1 - a) for c, bc in zip((r, g, b), br)))
        return out
    hx = hexes(val)
    return [rgb(h) for h in hx] if hx else None


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def check(t):
    v, ck = t['v'], t.get('chk', {})

    def col(key, base):
        if key in ck:
            return [rgb(h) for h in ck[key]]
        return solid(v[key], base)
    bg = col('bg', rgb('#FFFFFF'))[0]
    card = col('card', bg)[0]
    hd = col('hd', bg)
    pairs = [('ink', 'card', card, 4.5), ('sub', 'card', card, 4.5), ('acc', 'zBg', card, 4.5), ('tagInk', 'tagBg', card, 4.5), ('sub', 'tagBg', card, 4.5),
             ('warnInk', 'warnBg', card, 4.5), ('znInk', 'znBg', card, 4.5), ('btnInk', 'btn', card, 4.5), ('btn2Ink', 'btn2', card, 4.5),
             ('badgeInk', 'badge', card, 4.5), ('tabInk', 'tab', bg, 4.5), ('tabOnInk', 'tabOn', None, 4.5), ('pillInk', 'pill', None, 4.5),
             ('mInk', 'mBg', None, 4.5), ('logo', 'hd', None, 3.0), ('ink', 'zBg', card, 4.5), ('sub', 'zBg', card, 4.5)]
    bad = []
    for fg, bk, base, th in pairs:
        if bk == 'tabOn':
            base = col('tab', bg)
        elif bk in ('pill', 'mBg', 'hd'):
            base = hd
        bcols = col(bk, base if isinstance(base, list) else [base])
        if bk == 'zBg':
            bcols = col('zBg', [card])
        if fg == 'logo' and 'logoBg' in ck:
            bcols = [rgb(h) for h in ck['logoBg']]
        fcols = col(fg, bcols) if fg != 'logo' else col('logo', bcols)
        worst = min(ratio(f, b) for f in fcols for b in bcols)
        if worst < th:
            bad.append(f'{fg}/{bk} {worst:.2f}')
    return bad


if __name__ == '__main__':
    blobs = json.load(open(sys.argv[1])) if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else {}
    for t in THEMES:
        name = 'Judge_' + BOARD[t['id']] + '.dc.html'
        open(f'{OUT}/{name}', 'w', encoding='utf-8').write(judge_html(t, blobs.get(t['id'], '0' * 32)))
        bad = check(t)
        print(f"{t['id']:10s} {name:26s}", 'OK' if not bad else 'LOW: ' + ', '.join(bad))
