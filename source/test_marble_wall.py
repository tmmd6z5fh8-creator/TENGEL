# 大理石の 壁紙：像は まさちゃんの 3D の 馬（第4.155版・まさちゃん 2026/11/11・動きの 見本を 見て「大理石OK！」）
#   python3 test_marble_wall.py   （壁紙の 絵 ios/kisekae_blobs/ が 手元に ある とき だけ 絵と 画面も。ない とき（CI）は 台帳と ページの 形 だけ）
#   ・台帳：marble_blobs.json に 9まい（止まった 絵・シート 5・すべる 絵 2・背景 だけの 絵）・前の 絵とは ちがう・選ぶ 画面の 小さい 絵（blobs20.json）は 止まった 絵
#   ・marble_run.json：コマは 162（名前と ならびは 前と 同じ）・切りぬく 場所は pt の 境目・絵の 細かさ 1.5倍（＝画面の 3倍）・像は 3D（src＝glb）
#   ・ページ（marble_wall.py）：コマの 置き場所と シートの 大きさ（pt）・出来事の 予定は 前と 同じ（動きは かえて いない）・止めた ときも 像は 高画質
#   ・3D（GLB）と 壁紙の 絵は リポジトリに 入って いない
#   ・絵：シートは 画面の 3倍・止まった 絵と さいしょの コマは 同じ 像・すべる 絵（＋背景 だけの 絵）は 休みの コマと 同じ 絵（入れかわりが 見えない）・
#     像は コマの ふちの ぼかしに かからない・前の 絵 9まいも 手元に のこって いる（消して いない）
#   ・アプリの 画面（iPhone と 同じ 3倍）：コマが 絵の 3px を 1pt に 出す・つなぎ目が 見えない・くるっと／ヒヒィーン／ずっ！ずっ！（出て いく・いない・もどる）・
#     ずっ！ずっ！の はじめと おわりの 入れかえ・視差効果を 減らす とき（動かさない・像は 高画質の まま）・選ぶ 画面の 小さい 絵
#   第4.167版（まさちゃん 2026/11/13「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）：コマは 1/30秒の きざみ。
#   ・台帳：10まい（止まった 像 2コマの シート rest が 足された）・コマは 350（1/30秒ごとの 時刻の 形：ふり向き 76・体が 回る 59＋59・ヒヒィーン 77＋77・止まった 像 2）
#   ・動いて いる 間の コマ（look・turnB・turnD・neighL・neighR）は 画面の 2倍・止まった 像（rest）は 画面の 3倍。出来事の はじめは 1/30秒の きざみ（前の 予定から 0.017秒 まで）
import hashlib, io, json, os, re, shutil, subprocess, sys, time
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae')
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


MB = json.load(open(os.path.join(K, 'marble_blobs.json'))); B20 = json.load(open(os.path.join(K, 'blobs20.json'))); RUN = json.load(open(os.path.join(K, 'marble_run.json')))
KEYS = ['base', 'rest', 'look', 'turnB', 'turnD', 'neighL', 'neighR', 'spR', 'spL', 'plate']
SHEETS = ['rest', 'look', 'turnB', 'turnD', 'neighL', 'neighR']
MOVE = SHEETS[1:]                                                # 動いて いる 間の コマ（画面の 2倍）
OLD = ['5cae4afa07fcb5c9cb03488bcbb2ccd6', 'cd9f3399720ce0156c55c5f96547cfd1', '47b2ab94ddf449f59d099e0893dd1ecc', '0ca6e971340fe017bde2d8c3f29822d3', '3927e32f4d8c38ce7e306801bb86933f',
       '9cc18173b049394f27d1858335b8b319', 'de4ed1833e1832eedb77aa3ddbc2487e', '7ffc7c4e9e720537c2fea449145eb12f', '32a47b55d2330c01c10ba42edbeeb671']      # 前の 絵（sdfr の 像：第4.154版まで）
check(list(MB) == KEYS and len(set(MB.values())) == 10 and all(re.fullmatch(r'[0-9a-f]{32}', v) for v in MB.values()) and not (set(MB.values()) & set(OLD)) and B20['marble'] == MB['base'],
      '台帳：marble_blobs.json に 10まい（止まった 絵・止まった 像の シート・動く コマの シート 5・すべる 絵 2・背景 だけの 絵）・前の 絵とは ちがう・選ぶ 画面の 小さい 絵（blobs20.json）は 止まった 絵')
SC = RUN.get('scale')
x0, y0, x1, y1 = RUN['crop']; fw, fh = RUN['frame']
sys.path.insert(0, K)
import marble_wall as MW
LF, TF = MW.look_frames(RUN), MW.turn_frames()                    # コマの 予定（1/30秒の きざみ）は ページの もの
names = dict(rest=['A', 'C'], look=['A' + t for t, _ in LF] + ['C' + t for t, _ in LF], turnB=['B' + t for t, _ in TF], turnD=['D' + t for t, _ in TF],
             neighL=[f'NL{k:02d}' for k in range(1, 78)], neighR=[f'NR{k:02d}' for k in range(1, 78)])
COLS = {k: min(10, len(v)) for k, v in names.items()}
ROWS = {k: -(-len(v) // COLS[k]) for k, v in names.items()}
KS = {k: (1.5 if k == 'rest' else 1.0) for k in names}            # シートの 細かさ（壁紙の 絵の 何倍か）
sp = RUN['sprites']; pl = RUN['plate']
check(RUN['size'] == [780, 320] and SC == 1.5 and RUN.get('src') == 'glb' and all(v % 2 == 0 for v in RUN['crop'] + pl + sp['spR']['box']) and [fw, fh] == [x1 - x0, y1 - y0]
      and 0 <= x0 < x1 <= 780 and 0 <= y0 < y1 <= 320 and fw * fh < 296 * 320
      and list(RUN['sheets']) == SHEETS and all(RUN['sheets'][s]['frames'] == names[s] and RUN['sheets'][s]['cols'] == COLS[s] and RUN['sheets'][s]['rows'] == ROWS[s] and RUN['sheets'][s]['k'] == KS[s] for s in SHEETS)
      and [len(names[s]) for s in SHEETS] == [2, 76, 59, 59, 77, 77] and len(LF) == 38 and LF[0] == ('r', 0.0) and max(v for _, v in LF) == 140.0
      and (RUN['LOOK'], RUN['LOOK_OVER'], RUN['PSI_R'], RUN['NEIGH_S'], RUN['FPS'], RUN.get('scale_move')) == (130.0, 140.0, 140.0, 2.6, 30, 1.0)
      and sp['spR'] == sp['spL'] and sp['spR']['box'][0] <= x0 and sp['spR']['box'][2] >= x1 and sp['spR']['box'][1] == 0 and sp['spR']['box'][3] == 320
      and x0 < sp['spR']['base'][0] < sp['spR']['foot'][0] < sp['spR']['base'][1] < x1 and y1 - 16 < sp['spR']['foot'][1] < y1
      and pl[0] <= x0 and pl[1] <= y0 and pl[2] >= x1 and pl[3] >= y1 and pl[3] == 320,
      f'marble_run.json：コマ 350（1/30秒ごとの 時刻の 形：止まった 像 2・ふり向き 76・体が 回る 59＋59・ヒヒィーン 77＋77）・切りぬく 場所 {RUN["crop"]}（pt の 境目・前の 296×310 より 小さい）・'
      f'止まった 像と すべる 絵の 細かさ {SC}倍（画面の 3倍）・動く コマは 1倍（画面の 2倍）・像は 3D・すべる 絵と 背景 だけの 絵は コマの 四角を おおう')
html, css = MW.inline(MW.load_blobs(os.path.join(K, 'marble_blobs.json')), RUN)
plan = MW.schedule(RUN)
check(f'.mww .mwF{{left:{x0 // 2}px;top:{y0 // 2}px;width:{fw // 2}px;height:{fh // 2}px;' in css
      and all(f'background-image:url(/_blob/{MB[s]});background-size:{COLS[s] * (fw // 2)}px {ROWS[s] * (fh // 2)}px;' in css for s in SHEETS)
      and f'<img class="bnr" src="/_blob/{MB["base"]}" alt="">' in html and html.count('<i class="mwF ') == 6 and all(f'url(/_blob/{MB[k]})' in css for k in ('spR', 'spL', 'plate')),
      f'ページ：コマの 置き場所（左 {x0 // 2}・上 {y0 // 2}・{fw // 2}×{fh // 2}pt）と シートの 大きさは pt（絵は その 3倍の 細かさ）・止まった 絵・すべる 絵・背景 だけの 絵は 新しい 絵')
plan = [(round(t, 3), k, sd) for t, k, sd in plan]
P165 = [(6.178, 'neigh', 'R'), (21.142, 'slide', 'R'), (54.082, 'neigh', 'R'), (70.205, 'neigh', 'R'), (85.391, 'neigh', 'R'), (101.326, 'slide', 'R'), (133.618, 'neigh', 'R'), (149.182, 'neigh', 'R'),
        (158.333, 'neigh', 'L'), (173.512, 'neigh', 'L'), (189.117, 'neigh', 'L')]                                  # 第4.166版までの 予定
check(len(plan) == 11 and [(k, sd) for _, k, sd in plan] == [(k, sd) for _, k, sd in P165] and all(abs(a[0] - b[0]) <= 1 / 60 + 1e-6 for a, b in zip(plan, P165))
      and all(abs(t * 30 - round(t * 30)) < 0.02 for t, _, _ in plan) and plan[0] == (6.167, 'neigh', 'R')      # plan は 小数 3けたに まるめて ある（きざみの 0.015 まで ずれる）
      and MW.SIDE_S == 8.0 and MW.T_TURN == (3.0, 5.0) and MW.T_SLOW == (1.0, 2.0) and MW.T_BACK == (2.1, 2.3) and MW.T_SNAP == (74 / 30, 78 / 30, 82 / 30) and MW.FPS == 30
      and (MW.OUT_S, MW.AWAY_S, MW.BACK_S) == (9.5, 5.0, 9.5) and MW.OUT_X[-1] == 292,
      '出来事の 予定は 前と 同じ 順（8秒ごとに ふり向いて くるっと・ヒヒィーン 9回・ずっ！ずっ！ 2回／192秒）・はじめの 時刻は 1/30秒の きざみ（前の 予定から 0.017秒 まで）・2度見の 時刻も きざみの 上')
check('.mww i{display:none}.mww .mwS{display:block;animation:none}}' in css and '岩' not in MW.ALT and '後ろ足で立ち上がる白い大理石の馬の像' in MW.ALT,
      '視差効果を 減らす：重ねる 絵は 出さない・さいしょの コマ（左向きの 像・高画質）だけ 動かさずに 出す／絵の 説明（前の 像の「岩」は ない）')
have = os.path.isdir(BL) and all(os.path.exists(os.path.join(BL, MB[k] + '.webp')) for k in KEYS)
gi = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
src = open(os.path.join(K, 'flat', 'marble_glb.py'), encoding='utf8').read()
check(not any(f.lower().endswith(('.glb', '.gltf', '.npy')) for f in gi) and not any(f.startswith('ios/kisekae_blobs/') for f in gi) and 'MARBLE_HORSE_GLB' in src
      and os.path.exists(os.path.join(K, 'flat', 'marble_glb_run.py')),
      '3D（GLB）・場（npy）・壁紙の 絵は リポジトリに 入って いない（flat/marble_glb.py は 場所（MARBLE_HORSE_GLB）だけ）')
if not have:
    print('※ 壁紙の 絵（ios/kisekae_blobs）が ない ので、絵と アプリの 画面の 確かめは しない')
    print('結果：', 'NG ' + str(len(fails)) if fails else 'OK'); sys.exit(1 if fails else 0)
import numpy as np
from PIL import Image
P = lambda k: os.path.join(BL, MB[k] + '.webp')
IM = {k: Image.open(P(k)) for k in KEYS}
cw, ch = int(fw * SC), int(fh * SC)
ok = (all(hashlib.md5(open(P(k), 'rb').read()).hexdigest() == MB[k] and IM[k].format == 'WEBP' for k in KEYS)
      and all(IM[s].mode == 'RGB' and IM[s].size == (COLS[s] * int(fw * KS[s]), ROWS[s] * int(fh * KS[s])) for s in SHEETS) and IM['base'].mode == 'RGB' and IM['base'].size == (780, 320)
      and all(IM[k].mode == 'RGBA' and IM[k].size == (int((sp[k]['box'][2] - sp[k]['box'][0]) * SC), int(320 * SC)) for k in ('spR', 'spL'))
      and IM['plate'].mode == 'RGBA' and IM['plate'].size == (pl[2] - pl[0], pl[3] - pl[1]))
tot = sum(os.path.getsize(P(k)) for k in KEYS)
OLD165 = ['eae469c6', 'dca48b70', '842ffc1f', 'c67b494e', 'c14dbb38']                 # 第4.155〜4.166版の シート 5まい（id の はじめ：手元に のこって いる）
check(ok and cw == 3 * (fw // 2) and ch == 3 * (fh // 2) and 1_000_000 < tot < 2_300_000 and all(os.path.exists(os.path.join(BL, o + '.webp')) for o in OLD)
      and all(any(f.startswith(o) for f in os.listdir(BL)) for o in OLD165),
      f'絵 10まい：名前は 中身の md5・止まった 像の 1コマは {cw}×{ch}px（{fw // 2}×{fh // 2}pt の 3倍）・動く コマは {fw}×{fh}px（2倍）・すべる 絵は 3倍・止まった 絵と 背景 だけの 絵は 780×320 の まま・'
      f'ぜんぶで {tot / 1e3:.0f}KB（第4.166版は 1325KB）・前の 絵も 手元に のこって いる')
A = {k: np.asarray(IM[k].convert('RGBA' if IM[k].mode == 'RGBA' else 'RGB')).astype(np.float32) for k in KEYS}


def cell(name):
    for s in SHEETS:
        if name in names[s]:
            r, c = divmod(names[s].index(name), COLS[s]); w_, h_ = int(fw * KS[s]), int(fh * KS[s])
            return A[s][r * h_:(r + 1) * h_, c * w_:(c + 1) * w_]


def up(a, size):      # 画面が 絵を のばす のと 同じ ように（なめらかに）
    return np.asarray(Image.fromarray(a.astype(np.uint8)).resize(size, Image.BILINEAR)).astype(np.float32)


# 止まった 絵と さいしょの コマ（A00）は 同じ 像（コマを 小さく して くらべる）
a00s = np.asarray(Image.fromarray(cell('A').astype(np.uint8)).resize((fw, fh), Image.LANCZOS)).astype(np.float32)
d0 = np.abs(a00s - A['base'][y0:y1, x0:x1]).max(2)
# すべる 絵（＋背景 だけの 絵）と 休みの コマ：右向き C00 ＝ spR・左向き A00 ＝ spL
plate3 = up(A['plate'][..., :3], (int((pl[2] - pl[0]) * SC), int((pl[3] - pl[1]) * SC)))
seam = {}
for k, nm in (('spR', 'C'), ('spL', 'A')):
    bx = sp[k]['box']; s3 = A[k]
    px, py = int((x0 - pl[0]) * SC), int((y0 - pl[1]) * SC); sx, sy = int((x0 - bx[0]) * SC), int((y0 - bx[1]) * SC)
    al = s3[sy:sy + ch, sx:sx + cw, 3:4] / 255
    comp = plate3[py:py + ch, px:px + cw] * (1 - al) + s3[sy:sy + ch, sx:sx + cw, :3] * al
    d = np.abs(comp - cell(nm)).max(2)[4:-4, 4:-4]; seam[k] = (float(d.mean()), int((d > 30).sum()))      # ふちの 4px は 見ない（ここでは すき通しを かけずに のばす ので、四角の 外の 色が まざる）
check(d0.mean() < 3.0 and all(m < 2.5 and n < 60 for m, n in seam.values()),
      f'止まった 絵と さいしょの コマは 同じ 像（差の 平均 {d0.mean():.2f}）・すべる 絵＋背景 だけの 絵は 休みの コマと 同じ 絵（右向き：平均 {seam["spR"][0]:.2f}・大きな 差 {seam["spR"][1]}画素／左向き：{seam["spL"][0]:.2f}・{seam["spL"][1]}画素）')
# 像は コマの ふちの ぼかし（3pt＝9px）に かからない：どの コマも ふちの 帯は 背景 だけ（さいしょの コマと 同じ）／となりの コマは ちがう 形
rd = []; same = 0; small = []
for s in SHEETS:
    m_ = 9 if KS[s] == 1.5 else 6                                   # ふちの ぼかし 3pt（3倍の 絵で 9px・2倍の 絵で 6px）
    ref = cell('A' if s == 'rest' else 'Ar'); ring = np.ones(ref.shape[:2], bool); ring[m_:-m_, m_:-m_] = False
    prev = None
    for n in names[s]:
        c = cell(n); rd.append(float(np.abs(c - ref).max(2)[ring].mean()))
        if prev is not None:
            dv = float(np.abs(c - prev).max(2).mean()); small.append(dv)
            if np.array_equal(c, prev):
                same += 1
        prev = c
# 動く コマの 2倍の 止まった 形（Ar・Cr）は 3倍の 止まった 像（A・C）を 小さく した 絵と 同じ（細かさが かわる だけ・場所は 同じ）
rr = [float(np.abs(np.asarray(Image.fromarray(cell(a_).astype(np.uint8)).resize((fw, fh), Image.LANCZOS)).astype(np.float32) - cell(b_)).mean()) for a_, b_ in (('A', 'Ar'), ('C', 'Cr'))]
check(max(rr) < 1.5, f'動きの とちゅうの 止まった 形（2倍：Ar・Cr）は 止まった 像（3倍：A・C）を 小さく した 絵と 同じ（差の 平均 {rr[0]:.2f}・{rr[1]:.2f}）＝3倍 ↔ 2倍の 入れかわりで 像が ずれない')
pa = A['plate'][..., 3]; pin = A['plate'][y0 - pl[1]:y1 - pl[1], x0 - pl[0]:x1 - pl[0]]
check(max(rd) < 2.0 and same == 0 and (pin[..., 3] == 255).all() and pin[..., :3].std(axis=(0, 1)).max() < 8 and np.abs(pin[..., :3].mean((0, 1)) - A['base'][y0:y1, x0 - 14:x0 - 2].mean((0, 1))).max() < 8
      and set(np.unique(pa)) <= {0, 255},
      f'350コマ：像は ふちの ぼかしに かからない（ふちの 帯は どの コマも 背景 だけ：差の 平均 いちばん 大きい コマで {max(rd):.2f}）・となりの コマは ぜんぶ ちがう 絵（同じ 絵 {same}組）／背景 だけの 絵の 四角の 中に 像は ない')

from playwright.sync_api import sync_playwright
SRV = os.path.join(W, 'srv_marble'); PORT = 8798; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
for f in os.listdir(BL):
    shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
kj = json.load(open(os.path.join(SRV, 'APP', 'ks_marble.json'), encoding='utf8'))
check(all(f'ks_{MB[k]}.webp' in kj['bnr']['html'] + kj['bnr']['css'] for k in KEYS) and not any(o in json.dumps(kj) for o in OLD) and '#ksBnr.calm .mww .mwS{display:block;animation:none}' in kj['bnr']['css'],
      '大理石の ファイル（ks_marble.json）：新しい 絵 10まい・前の 絵は 入って いない・「演出を 控えめに」でも 像は 高画質の まま 止まる')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
ST = """async () => { const bn = document.querySelector('#ksBnr'), w = bn && bn.querySelector('.mww'); if (!w) return null; const b = bn.getBoundingClientRect();
  const q = (s) => { const e = w.querySelector(s), r = e.getBoundingClientRect(), c = getComputedStyle(e); return { box: [r.left - b.left, r.top - b.top, r.width, r.height].map(v => +v.toFixed(2)), disp: c.display, an: c.animationName, bp: c.backgroundPosition, bi: c.backgroundImage }; };
  const el = { S: q('.mwS'), M: q('.mwM'), B: q('.mwB'), D: q('.mwD'), NL: q('.mwNL'), NR: q('.mwNR'), G: q('.mwG'), P: q('.mwP'), R: q('.mwR'), L: q('.mwL') };
  const nat = {}; for (const k of ['S', 'M', 'B', 'D', 'NL', 'NR', 'R', 'L', 'P']) { const u = (el[k].bi.match(/url\\("?([^")]+)"?\\)/) || [])[1];
    nat[k] = u ? await new Promise(res => { const im = new Image(); im.onload = () => res([im.naturalWidth, im.naturalHeight]); im.onerror = () => res(null); im.src = u; }) : null; }
  const im = w.querySelector('img.bnr'); const an = bn.getAnimations({ subtree: true });
  return { box: [b.width, b.height], el: el, nat: nat, still: [im.getAttribute('src'), im.naturalWidth, im.naturalHeight], anims: an.length, run: an.filter(a => a.playState === 'running').length, aria: w.getAttribute('aria-label') || '', sw: document.documentElement.scrollWidth }; }"""
SEEK = "(T) => { for (const a of document.querySelector('#ksBnr').getAnimations({ subtree: true })) { a.pause(); a.currentTime = T * 1000; } }"


def open_app(ctx):
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/ks_' in r.url else None)
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=10000)
    pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'marble')
    pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg='marble', timeout=8000); pg.wait_for_timeout(1200)
    pg.evaluate("window.scrollTo(0, 0)")
    return pg, errs, bad


def shot(pg, t=None):
    if t is not None:
        pg.evaluate(SEEK, t); pg.wait_for_timeout(200)
    r = pg.evaluate("() => { const r = document.querySelector('#ksBnr').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
    return np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=dict(x=r[0], y=r[1], width=r[2], height=r[3])))).convert('RGB')).astype(np.float32)


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg, errs, bad = open_app(ctx)
        s = pg.evaluate(ST)
        cb = [x0 / 2, y0 / 2, fw / 2, fh / 2]
        okS = (bool(s) and s['box'] == [390, 160] and all(s['el'][k]['box'] == cb for k in ('S', 'M', 'B', 'D', 'NL', 'NR')) and s['still'] == [f'ks_{MB["base"]}.webp', 780, 320]
               and all(s['nat'][k] == list(IM[n].size) for k, n in (('S', 'rest'), ('M', 'look'), ('B', 'turnB'), ('D', 'turnD'), ('NL', 'neighL'), ('NR', 'neighR'), ('R', 'spR'), ('L', 'spL'), ('P', 'plate')))
               and s['nat']['S'][0] / (2 * fw / 2) == 3.0 and s['nat']['M'][0] / (10 * fw / 2) == 2.0 and s['nat']['R'][0] / s['el']['R']['box'][2] == 3.0
               and s['el']['P']['box'] == [pl[0] / 2, pl[1] / 2, (pl[2] - pl[0]) / 2, (pl[3] - pl[1]) / 2]
               and s['anims'] == 16 and s['run'] == 16 and s['sw'] <= 390 and '大理石の馬の像' in s['aria'])
        check(okS and not errs, f'アプリ：上の 絵は 大理石（mww）・コマ 6まいは {cb}pt に 置く・止まった 像は **絵の 3px を 1pt に**（シート {s and s["nat"]["S"]}px）・動く コマは 絵の 2px を 1pt に・すべる 絵も 3倍・動き 16こ・横に はみ出さない' + ('' if okS else f'（{s}）'))
        X0, Y0, X1, Y1 = [int(v * 1.5) for v in RUN['crop']]
        inc = np.zeros((480, 1170), bool); inc[Y0:Y1, X0:X1] = True
        n05 = shot(pg, 0.5)
        pg.evaluate("() => document.querySelectorAll('#ksBnr .mww > i').forEach(e => { e.style.display = 'none'; })"); pg.wait_for_timeout(200)
        still = shot(pg)
        pg.evaluate("() => document.querySelectorAll('#ksBnr .mww > i').forEach(e => { e.style.display = ''; })"); pg.wait_for_timeout(200)
        d = np.abs(n05 - still).max(2)
        edge = inc.copy(); edge[Y0 + 12:Y1 - 12, X0 + 12:X1 - 12] = False
        check(d[~inc].max() <= 2 and d[edge].mean() < 1.5 and d[edge].max() < 20 and d[inc].mean() > 0.8,
              f'つなぎ目：コマの 四角の 外は 止まった 絵の まま（差 {d[~inc].max():.0f}）・四角の ふち（ぼかしの 所）は 下の 絵と なじむ（差の 平均 {d[edge].mean():.2f}・最大 {d[edge].max():.0f}）・中の 像は 3倍の 絵に かわる')
        f40, f69, f240, f330 = shot(pg, 4.0), shot(pg, 6.9), shot(pg, 24.0), shot(pg, 33.0)
        dt, dn = np.abs(f40 - n05).max(2), np.abs(f69 - f40).max(2)
        right = np.zeros_like(inc); right[60:420, X1 + 60:X1 + 330] = True          # コマの 四角の 右（すべって いく 先）
        bg2 = A['base'].copy(); pm = A['plate'][..., 3] > 0                        # 背景 だけ（止まった 絵の 上に 背景 だけの 絵を 重ねた もの）
        bg2[pl[1]:pl[3], pl[0]:pl[2]][pm] = A['plate'][..., :3][pm]
        gone = np.abs(f330 - up(bg2, (1170, 480))).max(2)                           # いない 間：四角の 中は 背景 だけ（止まった 絵の 像が 見えない）
        check(dt[inc].mean() > 3 and dt[~inc].max() <= 2 and dn[inc].mean() > 2 and dn[~inc].max() <= 2
              and np.abs(f240 - n05).max(2)[right].mean() > 4 and gone[inc].max() < 16 and gone[inc].mean() < 2.0 and np.abs(f330 - n05).max(2)[inc].mean() > 8,
              f'動き：くるっと（4.0秒）・ヒヒィーン（6.9秒）は 四角の 中だけ かわる／ずっ！ずっ！（24.0秒）は 台ごと 右へ／いない 間（33.0秒）は 背景 だけ（四角の 中の 差：いちばん 大きくて {gone[inc].max():.0f}・平均 {gone[inc].mean():.2f}）')
        j = [np.abs(shot(pg, a) - shot(pg, c)).max(2) for a, c in ((21.05, 21.50), (45.10, 45.80))]
        check(all(v.mean() < 1.2 and (v > 30).sum() < 60 for v in j),
              f'ずっ！ずっ！の はじめと おわりの 入れかえ：コマ と すべる 絵は 同じ 絵に 見える（はじめ：差の 平均 {j[0].mean():.2f}・大きな 差 {int((j[0] > 30).sum())}画素／おわり：{j[1].mean():.2f}・{int((j[1] > 30).sum())}画素）')
        # 選ぶ 画面の 小さい 絵
        pg.locator('.tabbar [data-tab=set]').click(); pg.wait_for_timeout(500)
        th = pg.evaluate("""async () => { const im = document.querySelector('#setKisekae .kst[data-ks="marble"] img.ksth'); if (!im) return null; im.loading = 'eager'; im.scrollIntoView({ block: 'center' });
          for (let i = 0; i < 40 && !(im.complete && im.naturalWidth); i++) await new Promise(r => setTimeout(r, 100)); return [im.getAttribute('src'), im.naturalWidth, im.naturalHeight]; }""")
        check(th == [f'ks_{MB["base"]}.webp', 780, 320] and not bad and not errs, f'選ぶ 画面の 小さい 絵が 新しい 絵で 読める・読めない 絵 なし・ページの エラー なし（{th}・{bad[:3]}・{errs[:2]}）')
        ctx.close()
        # 視差効果を 減らす：動かさない・像は 高画質の まま
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='reduce')
        p2, e2, _b2 = open_app(ctx2)
        s2 = p2.evaluate(ST); r2 = shot(p2)
        okR = (bool(s2) and s2['run'] == 0 and s2['el']['S']['disp'] == 'block' and s2['el']['S']['an'] == 'none' and s2['el']['S']['bp'] in ('0% 0%', '0px 0px')
               and all(s2['el'][k]['disp'] == 'none' for k in ('M', 'B', 'D', 'NL', 'NR', 'G')) and np.abs(r2 - n05).max() <= 2)
        check(okR and not e2, f'視差効果を 減らす：動かさない（重ねる 絵は 出さない）・左向きの 像は 高画質の まま（ふつうの 0.5秒の 絵と 同じ：差 {np.abs(r2 - n05).max():.0f}）' + ('' if okR else f'（{s2}）'))
        ctx2.close()
        b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
