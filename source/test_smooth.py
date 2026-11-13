# 壁紙の コマ送りの 絵は 1秒に 30コマ（第4.166版：まさちゃん 2026/11/13 15:21「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）
#   python3 test_smooth.py   （壁紙の 絵 ios/kisekae_blobs/ が 手元に ある とき だけ 画面の コマも 見る。ない とき（CI）は 台帳と アニメの 時刻 だけ）
#   カクカクの もと：コマ送りの 絵（馬の シートを steps で めくる）が 1秒に 10〜20コマ だった（海賊の 船長は 9.6コマ）。画面は 1秒に 60回 描きかえる ので、
#   1コマを ちょうど 1/30秒（描きかえ 2回ぶん）に そろえた（1回りの 秒 ＝ コマの 数 ÷ 30）。
#   ・台帳：コマの 数（海賊 歩く 36・立つ 25／草競馬コース 12／宇宙 19／恐竜 15・13／未来 15・光の 尾 30／浮世絵 15／パドック 36・早歩き 24・うんち 72／競馬新聞・勝負服・夕焼け・水墨画 15）
#   ・上下の 動き：前の 動き（第4.165版の 10コマ）を なめらかな 波に して 読んだ もの（はね方は 前と 同じ・体が とばない）
#   ・アプリの 画面：なおした 壁紙の コマ送りは どれも 1コマ 1/30秒（未来の 光の 尾は 1/60秒）。まだの もの（ナイター・大理石・ドット絵・浮世絵の 大波）と、
#     わざと そう して いる もの（招き猫の 手・星空の 流れ）は 名前を 決めて のぞく（ふえたら 落ちる）
#   ・コマ：1コマずつ 進めて 写すと となりの コマと ちがう 絵（同じ コマが 2回 出ない）・1回り あとは 同じ 絵（つなぎ目で とばない）
#   ・ほかの 壁紙（17こ）の ファイルは 第4.165版と 1バイトも かわらない
#   第4.167版：のこりの 5つも（パドック 36コマ・ナイター 走る 15コマ＋止まる／走りだすは 時刻で 決めた コマ・大理石 1/30秒ごとの 形・ドット絵 全速 15コマ＋できごとの つづき・
#     浮世絵の 大波 30コマ／秒）。コマ送りで 1コマが 1/30秒で ない のは、わざとの もの（招き猫の 手・星空の 流れ）だけ。
#     パドックの 早歩きの あとの「ゆっくり 歩き」（1コマ 1/20秒・手前の 馬は 右の はしで 体の うしろが 見えて いた）は やめて、舞台を 出て 見えなく なって から 待つ
#   ・コマの さかい目（kisekae.js の phase）：コマが かわる 時刻が 画面の 描きかえの 時刻と 重なると「1回 だけ 出る コマ」と「3回 出る コマ」が まざって がたつく
#     → 上の絵の 動きの はじまりを 少し ずらして、コマが かわる 時刻を 描きかえと 描きかえの まん中に（合わせる 前は 重なって いる・合わせた あとは まん中・
#       同じ 部品の 動きは 同じ だけ ずれる・止めて いる ときは さわらない・止める／動かすは 今までどおり）
import hashlib, io, json, os, re, shutil, subprocess, sys, time
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae')
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


def wave(old, n, H=2):
    """前の 上下（len(old) コマ）を くり返しの なめらかな 波（倍音 H こ）に 合わせて n コマで 読む（kisekae/pack/make/sheets.py・flat/sea_run.py の wave_dy と 同じ 計算）"""
    import numpy as np
    m = len(old); ph = 2 * np.pi * np.arange(m) / m
    A = np.stack([np.ones(m)] + [fn(h * ph) for h in range(1, H + 1) for fn in (np.cos, np.sin)], 1)
    c = np.linalg.lstsq(A, np.array(old, float), rcond=None)[0]
    q = 2 * np.pi * np.arange(n) / n
    B = np.stack([np.ones(n)] + [fn(h * q) for h in range(1, H + 1) for fn in (np.cos, np.sin)], 1)
    return [float(v) for v in B @ c]


# ---------------------------------------------------------------- 台帳
PB = json.load(open(os.path.join(K, 'pack', 'blobs.json'), encoding='utf8'))
FR = lambda t, k: PB[t][k].get('frames')
pk = PB['paddock']
NEAR, FAR = ('n2', 'n5', 'n7'), ('f1', 'f4', 'f8')
PK36 = pk['n2']['frames'] == 36        # パドックの 36コマ（第4.167版から）
check(PK36, '台帳（パドック）：36コマに なって いる（第4.167版）')
check(FR('pirate', 'walk') == 36 and PB['pirate']['walk'].get('cols') == 12 and PB['pirate']['walk'].get('cycle') == 1.2 and FR('pirate', 'stand') == 25 and PB['pirate']['stand'].get('cols') == 13
      and [PB['pirate']['stand'].get(k) for k in ('ku', 'kd', 'kt')] == [8, 8, 8],
      '台帳（海賊）：歩く 36コマ（12×3段・1回り 1.2秒）・立つ 25コマ（正面 1＋見上げる 8＋見下ろす 8＋歩きとの つなぎ 8）')
check(FR('course', 'horses') == 12 and FR('space', 'run') == 19 and FR('dino', 'near') == FR('dino', 'near_s') == 15 and FR('dino', 'far') == FR('dino', 'far_s') == 13
      and FR('future', 'run') == 15 and all(FR('future', f'bolt{i}') == 15 for i in range(3)) and FR('future', 'trail') == 30 and PB['future']['trail'].get('cols') == 15 and FR('ukiyoe', 'run') == 15,
      '台帳（壁紙パック）：草競馬コース 12・宇宙 19・恐竜 手前 15／おく 13・未来 15（光の 尾 30＝15×2段）・浮世絵の 馬 15コマ')
check(abs(PB['dino']['near']['spf'] * 15 - 189.05) < 0.05 and abs(PB['dino']['far']['spf'] * 13 - 160.01) < 0.05 and PB['future']['run']['speed'] == 191.68,
      '台帳（恐竜・未来）：1回りで 地面が 流れる 長さは 前と 同じ（恐竜 189.05／160.01・未来 191.68：ひづめが すべらない）')
if PK36:
    okp = all(pk[n]['frames'] == 36 and pk[n + '_f']['frames'] == 24 and all(pk[f'{n}_{k}']['frames'] == 36 for k in ('s', 'dl', 'dd', 'dr')) for n in NEAR + FAR)
    okp = okp and all(pk[n + '_p']['frames'] == 72 and pk[n + '_p'].get('rows') == 3 and pk[n].get('rows') == 2 for n in NEAR) and all(pk[n].get('rows', 1) == 1 for n in FAR)
    okp = okp and all(pk[n]['id'] != pk[n + '_f']['id'] for n in NEAR + FAR) and len({pk[n]['speed'] for n in NEAR}) == 1 and len({pk[n]['speed'] for n in FAR}) == 1
    check(okp, f'台帳（パドック）：常歩・首振り・首下げ 36コマ・早歩き用（_f）24コマ・うんち 72コマ（手前の 馬は 段に 折る：常歩 2段・うんち 3段）・歩く はやさ 手前 {pk["n2"].get("speed")}／おく {pk["f1"].get("speed")}px/秒')
    # 第4.167版：早歩きで 先に 進んだ ぶんは、舞台を 出て 見えなく なって から 待って もどす（ゆっくり 歩きは しない）。待つ 間、馬の 絵は 1画素も 舞台に 入らない
    sys.path.insert(0, K)
    import pack as _PKG
    from pack import paddock as _PD
    _B = _PKG.blobs('paddock'); wait_rows = []; other_k = set()
    for _grp, _names in (('far', _PD.FAR), ('near', _PD.NEAR)):
        for _k, _nm in enumerate(_names):
            _m = _B[_nm]; _ax = _m['at'][0]
            _lays = [_m] + [_B[f'{_nm}_{q}'] for q in ('s', 'dl', 'dd', 'dr', 'p', 'f') if f'{_nm}_{q}' in _B]
            _lo = min((l['at'][0] - _ax) / 2 for l in _lays); _hi = max((l['at'][0] - _ax) / 2 + l['cell'][0] / 2 for l in _lays)
            _evs, _segs, _pos, _D, _v, _dirn, _s0 = _PD.schedule(_nm, dict(_m, _span=(_lo, _hi)), _grp, _k)
            other_k |= {c for t, c in _evs if c in ('w',)}
            _nf = sum(1 for t, c in _evs if c == 'f')
            for t, c in _evs:
                if c != 'z': continue
                _in = max(max(0.0, min(_pos(_PD._dist(_segs, _v, t + _PD.WAIT * i / 120)) + _hi, 390.0) - max(_pos(_PD._dist(_segs, _v, t + _PD.WAIT * i / 120)) + _lo, 0.0)) for i in range(121))
                _x0, _x1 = _pos(_PD._dist(_segs, _v, t)), _pos(_PD._dist(_segs, _v, t + _PD.WAIT))
                wait_rows.append((_nm, round(t, 3), _in, abs(_x1 - _x0), abs(t * 30 - round(t * 30))))
            wait_rows.append((_nm, 'n', _nf - sum(1 for t, c in _evs if c == 'z'), 0.0, 0.0))
            wait_rows.append((_nm, 'tot', abs(_PD._dist(_segs, _v, _PD.PLAN[_nm][0]) - _v * _PD.PLAN[_nm][0]), 0.0, 0.0))
    _z = [r for r in wait_rows if r[1] not in ('n', 'tot')]
    check(len(_z) == 5 and not other_k and all(r[2] == 0.0 and r[3] < 1e-6 and r[4] < 1e-6 for r in _z) and all(r[2] == 0 for r in wait_rows if r[1] == 'n')
          and all(r[2] < 1e-6 for r in wait_rows if r[1] == 'tot') and abs(_PD.WAIT - 1.2) < 1e-9,
          f'パドック：早歩きの あと（{len(_z)}回）は 舞台を 出て 見えなく なって から 1.2秒 待つ（入れものは 止まった まま・待つ 間に 舞台へ 入る 幅 0px・1/30秒の きざみ）＝ゆっくり 歩き（1コマ 1/20秒）は ない・1回りの 道のりは 前と 同じ')
    wmax = max(pk[k]['cell'][0] * pk[k]['z'] / 2 * pk[k]['frames'] / pk[k].get('rows', 1) for k in pk if k != 'still')
    check(wmax <= 10200, f'パドックの シートの 横は いちばん 長くて {wmax:.0f}画素（いままで 出して きた 絵の 長さ 10152画素 まで：36コマで それより 長く なる 手前の 馬は 段に 折って ある）')
D165 = dict(dino_near=[0.49, -5.52, -4.63, -1.86, 5.22, 1.37, 0.98, -3.64, -5.27, -3.89], dino_far=[-0.94, -4.66, -4.0, -1.84, 4.89, 1.56, 1.13, -3.89, -5.91, -4.92],
            future_run=[0.42, -4.27, -3.47, -0.85, 7.09, 3.1, 2.6, -2.45, -4.49, -3.54], space_run=[-2.12, -7.21, -6.38, -3.67, 4.23, 0.2, -0.29, -5.25, -7.21, -6.17],
            ukiyoe_run=[-2.84, -6.54, -5.93, -3.95, 1.86, -1.09, -1.45, -6.3, -8.15, -6.99])
worst = 0.0
for key, old in D165.items():
    t, k = key.split('_')
    for kk in ((k, k + '_s') if t == 'dino' else (k,)):
        new = PB[t][kk]['dy']; worst = max(worst, max(abs(a - b) for a, b in zip(new, wave(old, len(new)))))
check(worst < 0.011, f'上下の 動き（恐竜・未来・宇宙・浮世絵）：第4.165版の 10コマの 上下を なめらかな 波に して 読んだ もの（ちがい {worst:.3f}画素 まで）')
F165 = dict(news=[1.42, 2.33, 1.46, 0.79, 0.17, -2.08, -5.85, -8.28, -6.79, -2.36], sunset=[-5.0, -2.4, 0.19, 1.78, 2.27, 1.78, 0.19, -2.39, -4.98, -6.1],
            ink_far=[3.17, 3.45, 3.22, 2.4, 0.79, -1.14, -2.24, -1.67, 0.17, 2.08], ink_near=[-5.46, -5.86, -6.43, -5.72, -5.24, -7.17, -10.78, -12.68, -10.92, -7.4],
            silks=[-0.0, -2.42, -6.33, -6.33, -2.42, -0.0, -2.42, -6.33, -6.33, -2.42])
RJ = {n: json.load(open(os.path.join(K, n + '_run.json'), encoding='utf8')) for n in ('news', 'silks', 'sunset', 'ink')}
NEWDY = dict(news=RJ['news']['dy'], sunset=RJ['sunset']['horse']['dy'], ink_far=RJ['ink']['dy']['far'], ink_near=RJ['ink']['dy']['near'], silks=RJ['silks']['dy'])
worst = max(abs(NEWDY[k][3 * i] - F165[k][2 * i]) for k in F165 for i in range(5))
check(all(len(v) == 15 for v in NEWDY.values()) and RJ['news']['frames'] == RJ['silks']['frames'] == RJ['ink']['frames'] == RJ['sunset']['horse']['frames'] == 15 and worst < 0.02
      and RJ['sunset']['ground'] == {'y0': 200, 'base': 244.72, 'px_per_cycle': 226.14},
      f'台帳（競馬新聞・勝負服・夕焼け・水墨画）：15コマ・同じ 位相の コマ（0・3・6・9・12）の 上下は 前の 10コマ（0・2・4・6・8）と 同じ（ちがい {worst:.3f}画素 まで）・夕焼けの 地面の 高さと 流れる はやさも 前と 同じ')

# ---- 第4.167版：ナイター・大理石・ドット絵・浮世絵の 大波
NR_ = json.load(open(os.path.join(K, 'night_run.json'), encoding='utf8'))
N165 = {'5': [-1.25, -0.09, -0.4, -0.66, -0.53, -1.34, -3.77, -6.26, -6.46, -4.06], '3': [0.7, 0.51, 1.28, 2.31, 1.98, 0.07, -1.69, -1.65, -0.23, 0.8],
        '7': [-10.09, -8.67, -6.29, -5.01, -4.91, -4.65, -3.86, -3.93, -6.01, -8.89]}
okn, worst = True, 0.0
for n_, old in N165.items():
    h_, t_ = NR_['horses'][n_], NR_['trans'][n_]
    worst = max(worst, max(abs(a - b) for a, b in zip(h_['dy'], wave(old, 15))))
    fr = t_['frames']; dec = [f['k'] for f in fr if f['kind'] == 'dec']; acc = [f['k'] for f in fr if f['kind'] == 'acc']
    okn = (okn and h_['frames'] == 15 and len(h_['dy']) == 15 and len(fr) == t_['cols'] * t_['rows'] == len(dec) + len(acc) and dec[0] == 0 and dec == sorted(set(dec)) and acc == sorted(set(acc))
           and all(isinstance(k, int) for k in dec + acc) and max(b - a for a, b in zip(dec, dec[1:])) <= 3 and max(b - a for a, b in zip(acc, acc[1:])) <= 3
           and t_['stand']['kind'] == 'stand' and dec[-1] < t_['stand']['k'] <= dec[-1] + 3 and acc[-1] == 29 and dec[37] == 37)
check(okn and worst < 0.011, f'台帳（ナイター）：走る 15コマ（上下は 第4.166版の 10コマの 波：ちがい {worst:.3f}画素 まで）・止まる／走りだすは 時刻（1/30秒の きざみ）で 決めた コマ'
      f'（止まる {len(dec)}コマ：はじめの 38コマは 1/30秒ごと・動きが 小さく なったら 2〜3きざみ／走りだす {len(acc)}コマ／立つ 絵は べつの 1まい）')
MR_ = json.load(open(os.path.join(K, 'marble_run.json'), encoding='utf8'))
check(MR_.get('FPS') == 30 and {k: (len(v['frames']), v.get('k')) for k, v in MR_['sheets'].items()} == dict(rest=(2, 1.5), look=(76, 1.0), turnB=(59, 1.0), turnD=(59, 1.0), neighL=(77, 1.0), neighR=(77, 1.0)),
      '台帳（大理石）：1/30秒ごとの 形の コマ（ふり向き 76・体が 回る 59＋59・ヒヒィーン 77＋77：画面の 2倍）・止まった 像 2コマは 画面の 3倍')
PR_ = json.load(open(os.path.join(K, 'pixel_run.json'), encoding='utf8'))
check(PR_.get('rows') == [['run', 15], ['stop', 120], ['jump', 135], ['spin', 135]] and PR_.get('cols') == 135 and PR_.get('ev') == dict(stop=60, jump=75, spin=75, start=60),
      '台帳（ドット絵）：全速 15コマ・立ち止まる／ジャンプ／一回転 ＋ 走りだし の つづき（120・135・135コマ：どれも 1コマ 1/30秒）')
WV_ = PB['ukiyoe']['wave']
check(WV_.get('fps') == 30 and len(WV_['cells']) == 61 and WV_['t_end'] == 2.05, '台帳（浮世絵の 大波）：30コマ／秒・61コマ（出て きて から 水平に なる まで 2.05秒は 前と 同じ）')

# ---------------------------------------------------------------- アプリの 画面
from playwright.sync_api import sync_playwright
SRV = os.path.join(W, 'srv_smooth'); PORT = 8803; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
have = os.path.isdir(BL) and all(os.path.exists(os.path.join(BL, PB[t][k]['id'] + '.webp')) for t, k in (('pirate', 'walk'), ('paddock', 'n2'), ('dino', 'near')))
if have:
    for f in os.listdir(BL):
        shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
stj = json.load(open(os.path.join(SRV, 'APP', 'ks_stars.json'), encoding='utf8'))['bnr']['css']
check(bool(re.search(r'@media \(-webkit-min-device-pixel-ratio:3\),\(min-resolution:3dppx\)\{[^}]*animation-timing-function:steps\(1170\)', stj)) and 'steps(780)' in stj,
      '星空：画面が 3倍の iPhone では 流れを 1/3pt（＝画面の 1画素）ずつ（steps(1170)。前は どの 画面でも 0.5pt ずつ ＝ 3倍の 画面で 1.5画素ずつ に なって がたついた）')
# ほかの 壁紙の ファイル（第4.165版の ks_<id>.json の md5）：絵が 手元に ある とき（絵の 名前が 入る）だけ くらべる
SAME = dict(deepsea='b94d10960aff14f2eb8b188288455892', kirie='d874ec69837117d3dae9dd69809498ad', steam='c48013fe78ee67aaeefc4fa9feb5be9d',
            ranch='2fdfc69de72ad3fa177236943881ae62', cute='c8053f83635bdf6593e41ec8a3a9dc69', kids='e737b853237cd0672e4199594218295b',
            gold='da4ade57bb5733fac3de0212678fc1e6', fireworks='5e12b63bc9534b5a32d3b1b60b99d1aa',
            lucky='bcdc74a5f1fcad1507bd903c132d496e',
            chalk='9116ecabb050e3b0f0dac72fb08e0ec1', carousel='08168d5be91da3bb13b8652fcc9b5479', silver='f0cf1c64ce06bedd16120b570ae30018',
            golden='08dbec335ac8caec096b5bf942856c45', tengel='125e2b01dfbfb5786ed291ab957a101a')
if not PK36:
    SAME['paddock'] = '5ab6556262b690c92cf39635e491cef3'
if have:
    md = {t: hashlib.md5(open(os.path.join(SRV, 'APP', f'ks_{t}.json'), 'rb').read()).hexdigest() for t in SAME}
    dif = [t for t in SAME if SAME[t] != md[t]]
    if dif: print('    ', {t: md[t] for t in dif})
    check(not dif, f'なおして いない 壁紙 {len(SAME)}こ の ファイル（ks_<名前>.json）は 第4.165版と 1バイトも かわらない' + (f'（ちがう：{dif}）' if dif else ''))
# コマ送りの アニメ（steps・step-end）で 値が かわる 時刻を ぜんぶ 出す
SCAN = r'''() => {
  const root = document.querySelector('#ksBnr'); if (!root) return [];
  const out = [];
  for (const a of root.getAnimations({ subtree: true })) {
    const ef = a.effect; if (!ef || !ef.target) continue;
    const tm = ef.getComputedTiming(), kf = ef.getKeyframes();
    const props = new Set(); kf.forEach(k => Object.keys(k).forEach(p => { if (!['offset', 'computedOffset', 'easing', 'composite'].includes(p)) props.add(p); }));
    if (![...props].some(p => ['transform', 'translate', 'backgroundPosition', 'backgroundPositionX', 'backgroundPositionY', 'width', 'height'].includes(p))) continue;
    const dur = +tm.duration, ch = [];
    for (const p of props) {
      const ks = kf.filter(k => k[p] !== undefined);
      for (let i = 0; i + 1 < ks.length; i++) {
        const k0 = ks[i], k1 = ks[i + 1]; if (k0[p] === k1[p]) continue;
        const t0 = k0.computedOffset * dur, t1 = k1.computedOffset * dur, e = k0.easing || 'linear';
        const m = /^steps\((\d+)(?:,\s*([\w-]+))?\)/.exec(e);
        if (e === 'step-end' || (m && +m[1] === 1 && (!m[2] || m[2] === 'end' || m[2] === 'jump-end'))) ch.push(t1);
        else if (e === 'step-start' || (m && +m[1] === 1)) ch.push(t0);
        else if (m) { const n = +m[1]; for (let j = 1; j <= n; j++) ch.push(t0 + (t1 - t0) * j / n); }
        else if (t1 - t0 <= 0.5) ch.push(t1);
      }
    }
    out.push({ name: (a.animationName || '').replace(/^kb/, ''), dur, ch: [...new Set(ch.map(t => Math.round(t * 1000) / 1000))].sort((x, y) => x - y) });
  }
  return out;
}'''
# なおした 壁紙。のぞく アニメ（名前の 正規表現）：理由つき
FIXED = dict(pirate=None, course=None, space=None, dino=None, future=None, news=None, silks=None, sunset=None, ink=None, ukiyoe=None,
             night=None, marble=None, pixel=None)       # 第4.167版：ナイター・大理石・ドット絵・浮世絵の 大波も
if PK36:
    FIXED['paddock'] = None                     # 第4.167版：ゆっくり 歩き（36コマを 1.8秒＝1コマ 1/20秒）は やめた（見えない 所で 待つ）＝のぞく アニメは ない
LATER = dict()                                  # まだの 壁紙：なし（第4.167版）
if not PK36:
    LATER['paddock'] = r'^pk'                   # パドック（24コマを 1.25秒＝1秒に 19.2コマ）：つぎの 版で 36コマに
BYSPEC = dict(lucky=r'^lwS[AB]K$', stars=r'^szFlow$')        # わざと：招き猫の 手（まさちゃんの 指定の ゆれ）・星空の 流れ（画面の 1画素ずつ）


def ONE(g):
    """コマの 長さ g（ms）が どれも 1/60秒の 倍数（0.05ms まで）で、まん中の 長さが 1/30秒か 1/60秒"""
    med = sorted(g)[len(g) // 2]
    return all(abs(v / (1000 / 60) - round(v / (1000 / 60))) * (1000 / 60) < 0.05 for v in g) and min(abs(med - 1000 / 30), abs(med - 1000 / 60)) < 0.05


def gaps(a):
    """動いて いる 間（次の コマまで 0.25秒 より 短い 所）の コマの 長さ（ms）"""
    ch, dur = a['ch'], a['dur']
    if len(ch) < 2: return []
    g = [b - c for c, b in zip(ch, ch[1:])] + [ch[0] + dur - ch[-1]]
    return [v for v in g if v < 250]


def open_app(ctx):
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/ks_' in r.url else None)
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=10000)
    return pg, errs, bad


def use(pg, tid):
    pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
    pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000); pg.wait_for_timeout(900)
    pg.evaluate("window.scrollTo(0, 0)")


# コマを 写す：窓（overflow:hidden の 入れもの）が 見えて いて 壁紙の 中に ある 時刻を さがす → 窓の 中の アニメ だけ 1/30秒ずつ 進めて 写す
FIND = """([sel, ts]) => { const bn = document.querySelector('#ksBnr'), as = bn.getAnimations({ subtree: true }), b = bn.getBoundingClientRect();
  for (const t of ts) { as.forEach(a => { a.pause(); a.currentTime = t * 1000; }); const e = bn.querySelector(sel); if (!e) return null;
    let op = 1, vis = true; for (let x = e; x && x !== bn; x = x.parentElement) { const c = getComputedStyle(x); op *= +c.opacity; if (c.visibility !== 'visible' || c.display === 'none') vis = false; }
    const r = e.getBoundingClientRect(); if (vis && op > 0.99 && r.width > 4 && r.left >= b.left && r.right <= b.right) return [t, r.left, r.top, r.width, r.height]; }
  return null; }"""
STEP = """([sel, t0, t]) => { const bn = document.querySelector('#ksBnr'), w = bn.querySelector(sel);
  bn.getAnimations({ subtree: true }).forEach(a => { const g = a.effect.target; a.pause(); a.currentTime = (g !== w && w.contains(g) ? t : t0) * 1000; });
  return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); }"""
#        壁紙     窓                    コマ  さがす 時刻（秒）の きざみ
FRAMES = [('pirate', '.prHw', 36, 0.6)] + ([('paddock', '.pkH.n2>.pkL.w', 36, 1.2), ('paddock', '.pkH.f1>.pkL.w', 36, 1.2)] if PK36 else []) + [('dino', '.dnH.h1', 15, 0.5), ('dino', '.dnH.h2', 13, 0.5),
          ('future', '.ftH', 15, 0.5), ('space', '.ucH', 19, 0.5), ('ukiyoe', '.ukH', 15, 0.5), ('course', '.csH.h0', 12, 0.4),
          ('news', '.nsh', 15, 0.5), ('silks', '.sbh', 15, 0.5), ('sunset', '.sxh', 15, 0.5), ('ink', '.ikh', 15, 0.5),
          ('night', '.ntc7', 15, 0.5), ('night', '.ntc5', 15, 0.5), ('pixel', '.pqh', 15, 0.5, 3.0), ('marble', '.mww', 50, 0.5, 3.1, True)]
#        （5つめ：さがし はじめる 秒〈なければ 1.0〉・6つめ：True＝くり返さない つづき〈1回り あとの 絵は 見ない〉）
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg, errs, bad = open_app(ctx)
        ids = pg.evaluate("() => TengelKisekae.list().map(t => t.id)")
        res = {}
        for tid in ids:
            if tid == 'default': continue
            use(pg, tid); res[tid] = pg.evaluate(SCAN)
        slow = {}; n_ok = 0
        for tid, skip in FIXED.items():
            for a in res.get(tid, []):
                g = gaps(a)
                if len(g) < 3 or (skip and re.search(skip, a['name'])): continue
                # 1コマは 1/30秒（33.33ms）か 1/60秒（16.67ms）ちょうど（0.05ms まで）。形を 止めて 見せる 間（海賊の 船長が 見上げた まま 0.23秒 など）は
                #   その 倍数（コマが かわる 時刻は いつも 1/60秒の きざみの 上）で、ふつうの コマ（まん中の 長さ）は 1/30秒か 1/60秒
                if ONE(g): n_ok += 1
                else: slow.setdefault(tid, []).append((a['name'], round(1000 / sorted(g)[len(g) // 2], 1), round(max(g), 2)))
        if slow: print('    ', json.dumps(slow, ensure_ascii=False)[:1500])
        check(not slow and n_ok >= 70 and all(tid in res for tid in FIXED),
              f'アプリ：なおした 壁紙 {len(FIXED)}こ（海賊・草競馬コース・宇宙・恐竜・未来・浮世絵・パドック・競馬新聞・勝負服・夕焼け・水墨画・ナイター・大理石・ドット絵）の コマ送り {n_ok}こ は どれも 1コマ 1/30秒（か 1/60秒）ちょうど')
        sl = [a for a in res.get('paddock', []) if re.search(r'^pk[nf]\dFsl$', a['name'])]
        pkf = [a for a in res.get('paddock', []) if re.search(r'^pk[nf]\dF', a['name'])]
        wv = [a for a in res.get('ukiyoe', []) if a['name'] == 'ukWv']
        use(pg, 'paddock'); n_sl = pg.evaluate("() => document.querySelectorAll('#ksBnr .pkL.sl').length"); n_lay = pg.evaluate("() => document.querySelectorAll('#ksBnr .pkL').length")
        check(not sl and n_sl == 0 and n_lay == 38 and len(pkf) == 38 and all(ONE(gaps(a)) for a in pkf) and len(wv) >= 1 and all(len(gaps(a)) >= 60 and ONE(gaps(a)) for a in wv),
              f'のぞく もの なし：パドックの ゆっくり 歩きの シート（.pkL.sl）は ない（馬の シート {n_lay}まい・コマ送り {len(pkf)}こ は どれも 1コマ 1/30秒）／浮世絵の 大波（{len(wv)}こ）は 1コマ 1/30秒に なった')
        other = {}
        for tid, lst in res.items():
            if tid in FIXED: continue
            pat = LATER.get(tid) or BYSPEC.get(tid)
            for a in lst:
                g = gaps(a)
                if len(g) < 3 or ONE(g): continue
                if not (pat and re.search(pat, a['name'])): other.setdefault(tid, []).append((a['name'], round(1000 / sorted(g)[len(g) // 2], 1)))
        if other: print('    ', json.dumps(other, ensure_ascii=False)[:1500])
        check(not other, f'アプリ：ほかの 壁紙で 1コマが 1/30秒で ない コマ送りは、わざとの もの（招き猫の 手・星空の 流れ）だけ' + (f'（ほかに：{other}）' if other else ''))
        if have:
            import numpy as np
            from PIL import Image
            cur = None
            for tid, sel, n, dt, *opt in FRAMES:
                start, once = (opt[0] if opt else 1.0), (len(opt) > 1 and opt[1])
                if tid != cur: use(pg, tid); cur = tid
                dur = max((a['dur'] for a in res[tid]), default=60000) / 1000
                f = pg.evaluate(FIND, [sel, [round(start + dt * i, 3) for i in range(int(min(dur, 130) / dt))]])
                if not f:
                    check(False, f'コマ（{tid} {sel}）：窓が 見える 時刻が ない'); continue
                t0, x, y, w, h = f
                shots = []
                for k in range(n + 2):
                    pg.evaluate(STEP, [sel, t0, t0 + (k + 0.5) / 30])
                    shots.append(np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=dict(x=x, y=y, width=w, height=h)))).convert('RGB')).astype(np.float32))
                d = [float(np.abs(shots[k + 1] - shots[k]).mean()) for k in range(n)]
                loop = 0.0 if once else max(float(np.abs(shots[n] - shots[0]).mean()), float(np.abs(shots[n + 1] - shots[1]).mean()))
                med = sorted(d)[n // 2]
                ok = min(d) > 0.25 * med and med > 0.15 and loop < 0.05 * med + 0.02 and float(shots[0].std()) > 2
                if not ok: print('    ', tid, sel, 't0', t0, [round(v, 2) for v in d], 'loop', round(loop, 3))
                check(ok, f'コマ（{tid} {sel}・{n}コマ）：となりの コマと ちがう 絵（ちがい {min(d):.2f}〜{max(d):.2f}・まん中 {med:.2f}）' + ('' if once else f'・1回り あとは 同じ 絵（ちがい {loop:.3f}）'))
        # ---- コマの さかい目を 描きかえの まん中に（kisekae.js の phase）
        PH = """() => new Promise(res => { const out = []; let k = 0; const P = 1000 / 60, b = document.querySelector('#ksBnr');
          const f = () => { const t = document.timeline.currentTime;
            out.push(b.getAnimations({ subtree: true }).filter(a => a.playState === 'running' && typeof a.startTime === 'number').map(a => { const dl = +a.effect.getComputedTiming().delay || 0; return (((t - a.startTime - dl) % P) + P) % P; }));
            if (++k < 6) requestAnimationFrame(f); else res(out); }; requestAnimationFrame(f); })"""
        # 同じ 部品の 中で、おくれ（1/60秒で わった あまり）が 同じ 動きは 同じ はじまりの まま（＝同じ だけ ずれた）。おくれの あまりが ちがう 動きは べつべつに まん中へ 合わせる
        GRP = """(sels) => sels.map(s => { const e = document.querySelector('#ksBnr ' + s); if (!e) return -1; const P = 1000 / 60, m = new Map();
          e.getAnimations({ subtree: true }).forEach(a => { const dl = +a.effect.getComputedTiming().delay || 0, k = Math.round((((dl % P) + P) % P) * 20); if (!m.has(k)) m.set(k, new Set()); m.get(k).add(Math.round(a.startTime * 1e3)); });
          return Math.max(0, ...[...m.values()].map(v => v.size)); })"""
        pg2 = ctx.new_page(); pg2.goto(APP); pg2.wait_for_timeout(1500)
        if pg2.locator('#gateGo').count(): pg2.click('#gateGo'); pg2.wait_for_timeout(700)
        pg2.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=10000)
        rows = []
        for tid, groups in (('pirate', ['.prw']), ('paddock', ['.pkH.n2', '.pkH.n5', '.pkH.n7', '.pkH.f1', '.pkH.f4', '.pkH.f8']), ('dino', ['.dnH.h1', '.dnH.h2']), ('news', ['.nsw']), ('silks', ['.sbh']),
                            ('night', ['.nth7', '.nth5', '.nth3']), ('pixel', ['.pqh']), ('marble', ['.mww'])):
            pg2.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
            pg2.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000); pg2.wait_for_timeout(250)
            r1 = pg2.evaluate("() => TengelKisekae.phase()"); m1 = pg2.evaluate(PH); r2 = pg2.evaluate("() => TengelKisekae.phase()"); g = pg2.evaluate(GRP, groups)
            flat = [v for fr in m1 for v in fr]
            rows.append((tid, r1, r2, len(m1[0]), min(flat) if flat else 0, max(flat) if flat else 0, g))
        if any(not (r[1] and abs(r[1]['P'] - 1000 / 60) < 0.01 and r[1]['n'] == r[3] > 0 and r[2] and r[2]['moved'] == 0 and 5.6 <= r[4] and r[5] <= 11.1 and all(x == 1 for x in r[6])) for r in rows): print('    ', rows)
        check(all(r[1] and abs(r[1]['P'] - 1000 / 60) < 0.01 and r[1]['n'] == r[3] > 0 and r[2] and r[2]['moved'] == 0 and 5.6 <= r[4] and r[5] <= 11.1 and all(x == 1 for x in r[6]) for r in rows),
              'コマの さかい目：合わせた あと、動いて いる アニメは どれも 描きかえと 描きかえの まん中（1/60秒＝16.7ms の きざみの 5.6〜11.1ms：' + '／'.join(f'{r[0]} {r[3]}こ {r[4]:.1f}〜{r[5]:.1f}' for r in rows)
              + '）・もう 1回 合わせても 動かない・同じ 部品（船長／馬 1頭ずつ）の 同じ おくれの 動きは 同じ はじまりの まま')
        pg2.evaluate("() => document.querySelector('#ksBnr').classList.add('pause')"); pg2.wait_for_timeout(250)
        r0 = pg2.evaluate("() => TengelKisekae.phase()"); ps = pg2.evaluate("() => [...new Set(document.querySelector('#ksBnr').getAnimations({ subtree: true }).map(a => a.playState))]")
        pg2.evaluate("() => document.querySelector('#ksBnr').classList.remove('pause')"); pg2.wait_for_timeout(250)
        ps2 = pg2.evaluate("() => [...new Set(document.querySelector('#ksBnr').getAnimations({ subtree: true }).map(a => a.playState))]")
        check(r0 is None and ps == ['paused'] and ps2 == ['running'], f'コマの さかい目：止めて いる とき（.pause）は さわらない（{r0}）・合わせた あとも 止める／動かすは CSS の まま（{ps} → {ps2}）')
        # 止めて いる ときに 1回 よばれた あとも、動きだしたら また 合わせられる（前は 終わった 約束が のこって、そのあと ずっと 何も しなかった）
        pg2.evaluate("() => document.querySelector('#ksBnr').getAnimations({ subtree: true }).forEach(a => { if (typeof a.startTime === 'number') a.startTime += 7; })")
        r3 = pg2.evaluate("() => TengelKisekae.phase()"); r4 = pg2.evaluate("() => TengelKisekae.phase()")
        check(bool(r3) and r3['n'] > 0 and r3['moved'] > 0 and bool(r4) and r4['moved'] == 0,
              f'コマの さかい目：止めて いる ときに よばれた あとでも、動きだしたら また 合わせる（わざと 7ms ずらす → {r3} → もう 1回 {r4}）')
        pg2.close()
        check(not errs and not bad, f'エラー なし・読めない 絵 なし {errs[:2]} {bad[:3]}')
        ctx.close(); b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
