"""演出の 重さ（合成の 層の 画素）を はかる：python3 layer_mem.py <ページ（file の パス か URL）> [秒 …]
   （まさちゃん「プレミアムど的中ボタンだけ試すと落ちちゃう！」→ iPhone で 落ちない ように、作り直したら はかる）

   iPhone と 同じ 390×844・画素 3倍で 開いて、読みこんだ すぐ あとに ページの アニメを ぜんぶ 止め、その 秒に 合わせて
   ・合成の 層（composited layer）の 数・絵の ある 層の 数
   ・層の 画素の 目安（MB）：絵の ある 層の 面積 × 層の 拡大² × 3² × 4バイト（画面の 外は 2倍の 所まで）
   を 出し、入れものの class ごとに 多い 順に ならべる（入れもの＝ SEL（ふつう .ov.pm）の 直下の 子）。
   ページは 演出が 読みこみと 同時に 始まる もの（見本の .dc.html を ふつうの HTML に して 押した あとの 画面に した もの・アプリの テスト ページ など）。
   めやす：プレミアムど的中は いちばん 多い 時で 250MB 以下（2026/10/21 に 1075MB → 225MB に した）。
   SEL=<CSS セレクタ> で 入れものを かえられる。Chrome（Playwright）で はかるので iPhone の 数字とは ちがうが、ふえた・へったは わかる"""
import sys, os, math, collections
from playwright.sync_api import sync_playwright

src = sys.argv[1]
times = [float(t) for t in sys.argv[2:]] or [0.5, 2.0, 2.8, 3.4, 4.6, 5.8, 7.0, 8.2, 9.6, 12.0]
SEL = os.environ.get('SEL', '.ov.pm')
DPR = 3
VW, VH = 390, 844

TAG_JS = r'''sel => {
  const ov = document.querySelector(sel);
  if (!ov) return 0;
  let n = 0;
  for (const c of ov.children) {
    const cat = (c.getAttribute('class') || c.tagName).trim().split(/\s+/).join('.');
    c.setAttribute('data-lm', cat);
    c.querySelectorAll('*').forEach(e => { e.setAttribute('data-lm', cat); n++; });
  }
  return n;
}'''

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': VW, 'height': VH}, device_scale_factor=DPR)
    cdp = pg.context.new_cdp_session(pg)
    layers = {'v': []}
    cdp.on('LayerTree.layerTreeDidChange', lambda e: layers.__setitem__('v', e.get('layers') or layers['v']))
    cdp.send('DOM.enable')
    cdp.send('LayerTree.enable')
    pg.goto(src if '://' in src else 'file://' + os.path.abspath(src), wait_until='load')
    # 読みこんだ すぐ あとに ぜんぶ 止めて とっておく（すぐ 終わる アニメも あとで 秒を 合わせられる ように）
    n_anim = pg.evaluate('() => { window.__lmA = document.getAnimations(); window.__lmA.forEach(a => a.pause()); return window.__lmA.length; }')
    pg.wait_for_timeout(1000)
    n_tag = pg.evaluate(TAG_JS, SEL)
    cdp.send('DOM.getDocument', {'depth': -1})
    print(f'アニメ {n_anim}・部品 {n_tag}（{SEL} の 中）')
    peak = (0.0, 0.0)
    for t in times:
        pg.evaluate('t => window.__lmA.forEach(a => { a.pause(); a.currentTime = t * 1000; })', t)
        pg.evaluate('() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
        pg.wait_for_timeout(600)
        L = layers['v']
        by = {l['layerId']: l for l in L}
        memo = {}

        def scale(l):
            k = l['layerId']
            if k not in memo:
                tf = l.get('transform')
                s = math.sqrt(abs(tf[0] * tf[5] - tf[1] * tf[4])) if tf else 1.0
                par = by.get(l.get('parentLayerId'))
                memo[k] = (s or 1.0) * (scale(par) if par else 1.0)
            return memo[k]

        draws = [l for l in L if l.get('drawsContent')]
        cats = {}
        ids = [l['backendNodeId'] for l in draws if l.get('backendNodeId')]
        if ids:
            r = cdp.send('DOM.pushNodesByBackendIdsToFrontend', {'backendNodeIds': ids})
            for bid, nid in zip(ids, r['nodeIds']):
                if not nid:
                    continue
                try:
                    d = cdp.send('DOM.describeNode', {'nodeId': nid})['node']
                    at = d.get('attributes', [])
                    at = dict(zip(at[::2], at[1::2]))
                    if 'data-lm' in at:
                        cats[bid] = at['data-lm']
                    elif d.get('pseudoType'):
                        cats[bid] = '::' + d['pseudoType']
                    else:
                        cats[bid] = d['nodeName'].lower()
                except Exception:
                    cats[bid] = '?'
        cn, cm = collections.Counter(), collections.Counter()
        for l in draws:
            c = cats.get(l.get('backendNodeId'), '?')
            s = scale(l)
            ew, eh = min(l['width'] * s, VW * 2), min(l['height'] * s, VH * 2)
            cn[c] += 1
            cm[c] += ew * eh * DPR * DPR * 4 / 1e6
        tot = sum(cm.values())
        peak = max(peak, (tot, t))
        print(f'--- {t:.1f}秒  層 {len(L)}  絵の層 {len(draws)}  画素 {tot:.0f}MB')
        for c, m in cm.most_common(8):
            print(f'    {c:30s} 層 {cn[c]:5d}  {m:7.0f}MB')
    print(f'いちばん 多い 時：{peak[1]:.1f}秒 {peak[0]:.0f}MB')
    b.close()
