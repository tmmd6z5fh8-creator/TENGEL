# CM用の例：架空のオッズ画面（example_odds.html）を撮る → assets/ex_odds1.png（レース情報と単勝・複勝オッズ）・assets/ex_odds2.png（3連単オッズ）
#   python3 example_odds.py
# どこかの会社のアプリの画面のまねではない、独自のデザイン。レース名・馬名は架空
# 撮ったあと、この2枚の文字と位置（DOMから。Visionの代わり）をアプリの読み取り（ocr_local.js）に通して、
# CMのアプリの画面（cm2_shots.py の F9）と同じ数字が入るか確かめる（ちがったら止まる）
import json, os, subprocess, tempfile
from playwright.sync_api import sync_playwright
CM = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(CM)
LEAF_JS = '''() => {
  const out = []; const H = document.documentElement.scrollHeight, W = document.documentElement.scrollWidth;
  const walk = n => { for (const c of n.childNodes) { if (c.nodeType === 3) { const t = c.textContent.trim(); if (!t) continue; const r = document.createRange(); r.selectNodeContents(c); const b = r.getBoundingClientRect();
      if (b.width > 0 && b.height > 0) out.push({ text: t, x: (b.left + scrollX) / W, y: (b.top + scrollY) / H, w: b.width / W, h: b.height / H }); } else walk(c); } };
  walk(document.body); return out;
}'''
CHECK = r'''
const O = require(process.argv[2]); const L = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));
const merged = ls => O.rows(ls).map(r => ({ text: r.items.map(i => i.text).join(' '), x: r.items[0].x, y: r.items[0].y, w: r.items[r.items.length - 1].x + r.items[r.items.length - 1].w - r.items[0].x, h: r.h }));
const NOS = [6, 2, 10, 7, 1, 4, 11, 5, 9, 3, 8, 12], TAN = [2.1, 3.4, 5.2, 7.8, 9.5, 12.4, 16.8, 22.5, 31.0, 45.6, 58.3, 82.1], FL = [1.1, 1.3, 1.6, 2.0, 2.4, 2.9, 3.6, 4.5, 5.8, 7.9, 9.8, 13.5];
let bad = 0;
for (const [nm, imgs] of [['セルごと', L], ['行ごと', L.map(merged)]]) {
  const r = O.parse(imgs), hs = r.horses || [];
  const okH = hs.length === 12 && NOS.every((no, i) => { const h = hs.find(x => x.no === no); return h && h.tan === TAN[i] && parseFloat(h.fuku) === FL[i]; });
  const ok = r.r === 9 && r.dist === 1400 && r.surface === 'ダ' && r.baba === '良' && r.n === 12 && r.date === '2026-10-14' && r.venue === null
    && r.s1 && r.s1.combo === '6-2-10' && r.s1.odds === 18.5 && r.s5 && r.s5.odds === 42.6 && r.s10 && r.s10.odds === 78.9 && okH;
  console.log((ok ? '  ✅ ' : '  ❌ ') + '読み取り（' + nm + '）', JSON.stringify({ r: r.r, dist: r.dist, baba: r.baba, n: r.n, s1: r.s1, s5: r.s5, s10: r.s10, h0: hs[0] }));
  if (!ok) bad++;
}
process.exit(bad ? 1 : 0);
'''
pages = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2.5)
    for n in ('1', '2'):
        pg.goto('file://' + CM + '/example_odds.html?p=' + n)
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
        pg.screenshot(path=f'{CM}/assets/ex_odds{n}.png', animations='disabled')
        pages.append(pg.evaluate(LEAF_JS))
        print('ok', f'assets/ex_odds{n}.png')
    b.close()
with tempfile.TemporaryDirectory() as d:
    open(d + '/lines.json', 'w', encoding='utf8').write(json.dumps(pages, ensure_ascii=False))
    open(d + '/check.js', 'w', encoding='utf8').write(CHECK)
    subprocess.run(['node', d + '/check.js', SRC + '/ocr_local.js', d + '/lines.json'], check=True)
