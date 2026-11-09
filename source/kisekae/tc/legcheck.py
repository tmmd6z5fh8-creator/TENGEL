# 寝る・起きる 動きで 足が 胴（body・neck）の 中に 入って いないか 計算で しらべる（第4.133版・2026/11/09）
#   python3 legcheck.py <作業フォルダ（preview3d.html・tc_horse.js・馬の 形 が ある 所）> <馬の 名前,...> [lie|rise|both] [コマ数 200]
#   例：python3 legcheck.py /home/claude/work/tc/h3d_dev tc_horse_bk_brown_s1,tc_horse_bk_brown_s5,tc_horse_bk_kamisama both
#   ・骨で 動かした 頂点を そのまま 計算する（画面には 出さない）。すね・ひづめ と うでの 下半分の 点が、胴の 面に
#     上下・前後・左右の 6方向 から かこまれて いれば「中」。足ごとに 中に 入った コマ数と いちばん 深い 所を 出す
#   ・作業フォルダに しらべる 用の 写し（_legcheck_*.js・.html）を 作って、おわったら 消す（本物の ファイルは かえない）
import os, sys, subprocess, time, json, re
from playwright.sync_api import sync_playwright
D = os.path.abspath(sys.argv[1]); HNS = sys.argv[2].split(','); SEQ = sys.argv[3] if len(sys.argv) > 3 else 'both'; N = int(sys.argv[4]) if len(sys.argv) > 4 else 200
SEQS = ['lie', 'rise'] if SEQ == 'both' else [SEQ]; PORT = int(os.environ.get('PORT', '8899'))
src = open(os.path.join(D, 'tc_horse.js'), encoding='utf-8').read()
src, n1 = re.subn(r'window\.TCHorse = \{ create, ', 'window.TCHorse = { _lie: { LIE_SEQ, RISE_SEQ }, create, ', src)
src, n2 = re.subn(r'    return \{ sampP, sampB, anchors, gl,', '    return { _cpu: { pos, bone, bone2, bwt, idx }, sampP, sampB, anchors, gl,', src)
assert n1 == 1 and n2 == 1, 'tc_horse.js の 形が かわった（写しを 作れない）'
page = open(os.path.join(D, 'preview3d.html'), encoding='utf-8').read().replace('<script src="tc_horse.js"></script>', '<script src="_legcheck_horse.js"></script>')
JF, PF = os.path.join(D, '_legcheck_horse.js'), os.path.join(D, '_legcheck_preview.html')
open(JF, 'w', encoding='utf-8').write(src); open(PF, 'w', encoding='utf-8').write(page)
JS = r"""
([seq, N]) => {
  const h = HORSE, C = h._cpu, nv = C.pos.length / 3, bi = h.bi, LEGS = ['FL', 'FR', 'HL', 'HR'];
  const partOf = new Int8Array(64).fill(0);          // 0：胴（body・neck） 1：頭 2：しっぽ 3〜6：足
  for (const b of h.bones) { const i = bi[b.name]; if (/^(head|jaw)/.test(b.name)) partOf[i] = 1; else if (/^tail/.test(b.name)) partOf[i] = 2; }
  LEGS.forEach((L, li) => ['_u', '_k', '_f'].forEach(s => { partOf[bi[L + s]] = 3 + li; }));
  const idx = C.idx, nt = idx.length / 3, tor = [];
  for (let i = 0; i < nt; i++) if (partOf[C.bone[idx[3 * i]]] === 0 && partOf[C.bone[idx[3 * i + 1]]] === 0 && partOf[C.bone[idx[3 * i + 2]]] === 0) tor.push(i);
  const test = LEGS.map(L => {             // すね・ひづめ（k・f の 骨）と うでの 下半分（骨の 線に そって 55% より 先・線から 0.13 以内）
    const u = h.bones[bi[L + '_u']].head, k = h.bones[bi[L + '_k']].head, Lu = Math.hypot(k[0] - u[0], k[1] - u[1], k[2] - u[2]), ax = [0, 1, 2].map(j => (k[j] - u[j]) / Lu), o = [];
    for (let i = 0; i < nv; i++) {
      const b = C.bone[i];
      if (b === bi[L + '_k'] || b === bi[L + '_f']) o.push(i);
      else if (b === bi[L + '_u']) {
        const q = [0, 1, 2].map(j => C.pos[3 * i + j] - u[j]), tp = q[0] * ax[0] + q[1] * ax[1] + q[2] * ax[2], rr = Math.hypot(q[0] - tp * ax[0], q[1] - tp * ax[1], q[2] - tp * ax[2]);
        if (tp > 0.55 * Lu && tp < 1.15 * Lu && rr < 0.13) o.push(i);
      }
    }
    return o;
  });
  const W = new Float32Array(nv * 3);
  const skin = (mats, blend) => {
    for (let i = 0; i < nv; i++) {
      const x = C.pos[3 * i], y = C.pos[3 * i + 1], z = C.pos[3 * i + 2], A = mats[C.bone[i]], B = mats[C.bone2[i]], w = (C.bwt[i] / 255) * blend, v = 1 - w, m = j => A[j] * v + B[j] * w;
      W[3 * i] = m(0) * x + m(4) * y + m(8) * z + m(12); W[3 * i + 1] = m(1) * x + m(5) * y + m(9) * z + m(13); W[3 * i + 2] = m(2) * x + m(6) * y + m(10) * z + m(14);
    }
  };
  const G = 48;
  const mkGrid = ax => {                  // 光線の 向きの 軸 ax・のこりの 2軸で 三角を 格子に わける
    const a1 = (ax + 1) % 3, a2 = (ax + 2) % 3; let lo1 = 1e9, hi1 = -1e9, lo2 = 1e9, hi2 = -1e9;
    for (const t of tor) for (let k = 0; k < 3; k++) { const v = idx[3 * t + k]; lo1 = Math.min(lo1, W[3 * v + a1]); hi1 = Math.max(hi1, W[3 * v + a1]); lo2 = Math.min(lo2, W[3 * v + a2]); hi2 = Math.max(hi2, W[3 * v + a2]); }
    const cells = Array.from({ length: G * G }, () => []), s1 = G / (hi1 - lo1 + 1e-6), s2 = G / (hi2 - lo2 + 1e-6);
    for (const t of tor) {
      let m1 = 1e9, M1 = -1e9, m2 = 1e9, M2 = -1e9;
      for (let k = 0; k < 3; k++) { const v = idx[3 * t + k]; m1 = Math.min(m1, W[3 * v + a1]); M1 = Math.max(M1, W[3 * v + a1]); m2 = Math.min(m2, W[3 * v + a2]); M2 = Math.max(M2, W[3 * v + a2]); }
      for (let i = Math.max(0, Math.floor((m1 - lo1) * s1)); i <= Math.min(G - 1, Math.floor((M1 - lo1) * s1)); i++)
        for (let j = Math.max(0, Math.floor((m2 - lo2) * s2)); j <= Math.min(G - 1, Math.floor((M2 - lo2) * s2)); j++) cells[i * G + j].push(t);
    }
    return { ax, a1, a2, lo1, lo2, s1, s2, cells };
  };
  const hits = (g, P) => {                // P から ＋・− の 向きに いちばん 近い 胴の 面まで
    const i = Math.floor((P[g.a1] - g.lo1) * g.s1), j = Math.floor((P[g.a2] - g.lo2) * g.s2);
    if (i < 0 || j < 0 || i >= G || j >= G) return [Infinity, Infinity];
    let up = Infinity, dn = Infinity;
    for (const t of g.cells[i * G + j]) {
      const a = idx[3 * t], b = idx[3 * t + 1], c = idx[3 * t + 2], ax = W[3 * a + g.a1], ay = W[3 * a + g.a2], bx = W[3 * b + g.a1], by = W[3 * b + g.a2], cx = W[3 * c + g.a1], cy = W[3 * c + g.a2];
      const px = P[g.a1], py = P[g.a2], d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy); if (Math.abs(d) < 1e-12) continue;
      const l1 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / d, l2 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / d, l3 = 1 - l1 - l2;
      if (l1 < 0 || l2 < 0 || l3 < 0) continue;
      const dd = l1 * W[3 * a + g.ax] + l2 * W[3 * b + g.ax] + l3 * W[3 * c + g.ax] - P[g.ax];
      if (dd > 0) up = Math.min(up, dd); else dn = Math.min(dn, -dd);
    }
    return [up, dn];
  };
  const out = [], st = BR;
  for (let s = 0; s <= N; s++) {
    const u = s / N;
    Object.assign(st, { mode: 'sleep', sl: seq === 'rise' ? 1 : Math.max(0.0011, u), rise: seq === 'rise' ? Math.max(1e-4, u) : 0, doze: 0, flop: null, reacts: [], graze: 0 });
    skin(TCHorse.pose(h, st, 10 + u * 0.01), TCHorse.blendOf(st));
    const gr = [0, 1, 2].map(mkGrid), row = { u };
    LEGS.forEach((L, li) => {
      let n = 0, dmax = 0;
      for (const v of test[li]) {
        const P = [W[3 * v], W[3 * v + 1], W[3 * v + 2]], r = gr.map(g => hits(g, P)); let c = 0, dep = Infinity;
        for (const [a, b] of r) { if (a < Infinity) c++; if (b < Infinity) c++; dep = Math.min(dep, a, b); }
        if (r[1][0] < Infinity && r[1][1] < Infinity && c >= 5) { n++; dmax = Math.max(dmax, dep); }
      }
      row[L] = [n, +dmax.toFixed(4)];
    });
    out.push(row);
  }
  return out;
}
"""
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', D], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.7)
res = {}
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        for hn in HNS:
            pg = b.new_page(viewport={'width': 390, 'height': 614}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            ex = '&stance=1' if 'kamisama' in hn else ''          # 神様馬は 肩幅を 合わせた 形（アプリと 同じ）
            pg.goto(f'http://localhost:{PORT}/_legcheck_preview.html?cap=1&seed=3&h={hn}&stage=1{ex}'); pg.wait_for_function('() => window.__ready && window.__ready()', timeout=90000)
            for seq in SEQS:
                rows = pg.evaluate(JS, [seq, N]); res[f'{hn}:{seq}'] = rows
                cnt = {L: sum(1 for r in rows if r[L][0] > 0) for L in ('FL', 'FR', 'HL', 'HR')}
                dep = {L: max(r[L][1] for r in rows) for L in ('FL', 'FR', 'HL', 'HR')}
                print(f'{hn:26s} {seq:4s} 胴の中の コマ {cnt}  いちばん深い {dep}' + (f'  エラー {errs[:1]}' if errs else ''), flush=True)
            pg.close()
        b.close()
finally:
    srv.terminate()
    for f in (JF, PF):
        try: os.remove(f)
        except OSError: pass
if os.environ.get('OUT'): json.dump(res, open(os.environ['OUT'], 'w'))
