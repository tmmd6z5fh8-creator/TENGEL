"""見本の ページ（mock/○○.dc.html）を 手元の ブラウザ（Playwright の Chromium）で 動かして、PUSH を 押した 瞬間から 1コマずつ 止めて 写す（1170×2532）。
   超神様的中の「昇格」の 絵の もとに 使う：超プレミアムど的中（Fx_SuperPremium）の 0〜6.0秒（③「き！」まで）と、バグの もとの 1まい（6.0秒）。
   ・ページの しくみ（{{穴}}・sc-if・onXxx・ref・class）だけを 小さく まねて 動かす（テスト用。キャンバスの ものとは 別）
   ・字の 形は 手元に ある 字（Google Fonts は 読まない）。超プレミアムの「ど！」「て！」「き！」は 絵なので 変わらない
   ・/_blob/ の 絵と 音は 読まない（超プレミアムの 0〜6秒の 絵には 使って いない）
   ・押した あと すべての 動き（CSS の アニメーション）を 止めて、時刻を 合わせて 写す（何回 写しても 同じ）
   python3 flat/capture_page.py <page.dc.html> <出力フォルダ> <はじめの 秒> <おわりの 秒> [コマ/秒＝30] → f001.png …
   例：python3 flat/capture_page.py mock/Fx_SuperPremium.dc.html /tmp/zp 0 6.0   （f181.png が き！の 1まい）"""
import os, re, sys, json, tempfile

RT = r'''
<script>
class DCLogic { constructor(p) { this.props = p; this.state = {}; } setState(s) { Object.assign(this.state, s); window.__sched(); } forceUpdate() { window.__sched(); } }
</script>
<script>
__JS__
</script>
<script>
(function () {
  var root = document.getElementById('root');
  var comp = new Component(__PROPS__);
  var vals = {}, binds = [], refs = [], first = true;
  function look(p) {
    p = p.trim();
    if (p === 'true') return true; if (p === 'false') return false;
    return p.split('.').reduce(function (o, k) { return o == null ? undefined : o[k]; }, vals);
  }
  var walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
  var n;
  while ((n = walker.nextNode())) {
    if (n.nodeType === 3) {
      if (n.nodeValue.indexOf('{{') >= 0) binds.push({ t: 'text', el: n, tpl: n.nodeValue });
      continue;
    }
    Array.prototype.slice.call(n.attributes).forEach(function (a) {
      if (a.value.indexOf('{{') < 0) return;
      var m = a.value.match(/^\{\{([^}]*)\}\}$/);
      if (a.name === 'ref') { refs.push({ el: n, p: m[1] }); n.removeAttribute('ref'); return; }
      if (/^on/.test(a.name)) {
        var ev = a.name.slice(2).toLowerCase(), p = m[1], el = n;
        n.removeAttribute(a.name);
        el.addEventListener(ev, function (e) { var f = look(p); if (typeof f === 'function') f(e); });
        return;
      }
      if (n.tagName.toLowerCase() === 'sc-if' && a.name === 'value') { binds.push({ t: 'if', el: n, p: m[1] }); return; }
      if (a.name.indexOf('hint-') === 0) return;
      binds.push({ t: 'attr', el: n, name: a.name, tpl: a.value });
    });
  }
  function interp(tpl) { return tpl.replace(/\{\{([^}]*)\}\}/g, function (_, p) { var v = look(p); return v == null ? '' : v; }); }
  function render() {
    vals = comp.renderVals();
    binds.forEach(function (b) {
      if (b.t === 'text') b.el.nodeValue = interp(b.tpl);
      else if (b.t === 'if') b.el.style.display = look(b.p) ? 'contents' : 'none';
      else b.el.setAttribute(b.name, interp(b.tpl));
    });
    if (first) { first = false; refs.forEach(function (r) { var f = look(r.p); if (typeof f === 'function') f(r.el); }); }
  }
  var q = false;
  window.__sched = function () { if (q) return; q = true; Promise.resolve().then(function () { q = false; render(); }); };
  window.__comp = comp;
  render();
})();
</script>'''


def build(dc_path, out_html):
    """mock の .dc.html → 手元で 動く 1まいの html"""
    src = open(dc_path, encoding='utf-8').read()
    xdc = re.search(r'<x-dc>([\s\S]*?)</x-dc>', src).group(1)
    hm = re.search(r'<helmet>[\s\S]*?</helmet>', xdc)
    helmet = re.search(r'<helmet>([\s\S]*?)</helmet>', hm.group(0)).group(1)
    body = xdc.replace(hm.group(0), '')
    js = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', src).group(1)
    props = json.loads(re.search(r"data-props='([^']*)'", src).group(1))
    defaults = {k: v.get('default') for k, v in props.items() if isinstance(v, dict) and 'default' in v}
    defaults['start'] = defaults.get('start', 'form')
    html = ('<!doctype html>\n<html lang="ja"><head><meta charset="utf-8"><style>sc-if{display:contents} body{margin:0;background:#222}</style>\n'
            + helmet + '\n</head><body>\n<div id="root">' + body + '</div>\n'
            + RT.replace('__JS__', js).replace('__PROPS__', json.dumps(defaults)) + '\n</body></html>')
    open(out_html, 'w', encoding='utf-8').write(html)
    return out_html


def capture(html, out, t_from, t_to, fps=30.0):
    from playwright.sync_api import sync_playwright
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, reduced_motion='no-preference')
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: print('pageerror:', e))
        pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
        pg.route('**/_blob/**', lambda r: r.abort())
        pg.goto('file://' + os.path.abspath(html))
        pg.wait_for_timeout(400)
        pg.locator('button', has_text='記録').first.click()
        pg.wait_for_timeout(500)
        pg.locator('button.push').first.click(force=True)
        pg.wait_for_timeout(120)
        pg.evaluate("() => { document.getAnimations().forEach(function (x) { x.pause(); }); }")
        k = 0
        while True:
            t = t_from + k / fps
            if t > t_to + 1e-6:
                break
            pg.evaluate("(ms) => { document.getAnimations().forEach(function (x) { x.currentTime = ms; }); }", t * 1000)
            pg.wait_for_timeout(15)
            k += 1
            pg.screenshot(path=os.path.join(out, f'f{k:03d}.png'))
        b.close()
    return k


if __name__ == '__main__':
    dc, out, a, z = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    fps = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
    with tempfile.TemporaryDirectory() as td:
        n = capture(build(dc, os.path.join(td, 'page.html')), out, a, z, fps)
    print('frames', n)
