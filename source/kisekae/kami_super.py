"""超神様的中（第4.51版・まさちゃんの指定）：神様的中の さらに 上の ボタン。押したあとは 1コマずつ 描いた 動画（①②③）→ 超神様的中の ボード
   まさちゃん「これを超神様的中ボタンにして！ 神様的中 結果ボード、ど的中から神様的中に変える 超神様的中ボタンを新しく作成して！
   このエフェクトは、超神様的中ボタンのエフェクトね！ 元々の神様的中ボタンも今のまま残して！」
   → 神様的中（kami.py・Fx_God）は そのまま（ボードの 見出しだけ「神様的中！！！」）。超神様的中（Fx_SuperGod）を 新しく：
     出るのは 神様的中の 8回に1回（ランダム）※仮（超プレミアムど的中＝プレミアムの 8回に1回と 同じ 形）・PUSHは ど的中と 同じ ※仮
     押すと 動画（flat/kami_film.py ① 金の 嵐 1.6秒 → flat/kami_film2.py ② 金の 立体の 字 4.7秒 → flat/kami_film3.py ③ 雷を まとった
     神・様・的・中 と 小判 → 朱ぬりの 鳥居の 中に 神様的中 おめでとう御座います 6.2秒）＝ 12.5秒 → 超神様的中の ボード（見出し「超神様的中！！！」）
   動画だけは 1コマずつ 描いた 絵（1170×2532・30コマ/秒）なので アプリでも 動画（H.264・音なし）。音は ほかと 同じ 効果音（gen_sfx.py の sfx_sgd）
   見本の ページ：動画は 押す 前から ページに 置いて 先に 読む・押した 瞬間に 再生 → 動画が 動きだした 時に 音を その 時刻から（絵と 音が ずれない）
     → 動画の 12.6秒に 白い 光 → ボード（ボードの 時計も 動きだした 時から）。視差効果を減らす：動画は 出さず さいごの 1まい（鳥居の 中の 神様的中）→ 1.3秒から ボード"""
import os

FPS = 30
N1, N2, N3 = 48, 141, 186                  # ①②③ の コマ数（flat/kami_film.py・kami_film2.py・kami_film3.py の N）
NW = 40                                    # ① と ② の 間に 足す 白い 光の コマ（flat/kami_white.py）：まさちゃん「四枚目のシーンのあと、白い光に包まれるシーンは、1.5秒に伸ばして！」
                                           # → ① の さいごの まっ白 1コマ＋この 40コマ＋② の はじめの 白 4コマ ＝ 1.5秒
OFS = (0.0, (N1 + NW) / FPS, (N1 + NW + N2) / FPS)     # ①②③ の はじまり（押した 瞬間が 0秒）
FILM = (N1 + NW + N2 + N3) / FPS           # 動画の 長さ 13.83秒（白い 光を 足す 前は 12.5秒）
RES = FILM + .1                            # ボード（動画の さいごの 1まいの 上に）
T0B = RES + .45                            # ボードの 買い目の はじまり（--t0）
# 視差効果を減らす（・動画が 動かない）時：さいごの 1まい → 押して 1秒後に 音の STILL_FROM 秒から → ボードの ポンッ（音の RES＋0.2秒）で ボードが ふわっと・買い目も 音に そろえる
STILL_WAIT = 1.0
STILL_FROM = RES - .1
STILL_BOARD = STILL_WAIT + (RES + .2 - STILL_FROM)      # 1.3秒
STILL_T0 = STILL_WAIT + (T0B - STILL_FROM)               # 1.55秒


def sec(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') + 's'


def sgd_video(film_url):
    """動画（押す 前から ページに 置いて 先に 読む：押した 瞬間に 再生できる ように）。音は 入れない（効果音で 鳴らす）"""
    return (f'<video class="{{{{sgvCls}}}}" src="{film_url}" muted="true" playsinline="true" webkit-playsinline="true" preload="auto" '
            f'aria-hidden="true" ref="{{{{vref}}}}" onPlaying="{{{{onPlay}}}}"></video>')


def sgd_layers(board_html, last_url):
    """押したあと（下から）：（動画は ページの video）→ さいごの 1まい（視差効果を減らす 時）→ 白い 光 → ボードの うしろを 少し 暗く → ボード（board_html）"""
    return f'''<img class="sgs" src="{last_url}" alt="">
    <div class="sgw" aria-hidden="true"></div>
    <div class="sgk" aria-hidden="true"></div>
    <div class="hb">{board_html}</div>
    <p class="sr">超神様的中！金色の 嵐の 中で 光の 玉が はじけ、金色の 立体の 字で「万馬券（きせき）は偶然にあらず 天眼（テンゲル）が導く必然なり」。雷を まとった 神・様・的・中 と 小判が とびかい、朱ぬりの 鳥居の 中に 神様的中 おめでとう御座います</p>'''


def sgd_css():
    return f'''
/* ---------- 超神様的中：kami_super.py（動画は flat/kami_film*.py の ①②③ を つないだ もの・{sec(FILM)}） ---------- */
.ph .sgv{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;background:#000;z-index:30;opacity:0;pointer-events:none}}
.ph .sgv.on{{opacity:1}}
/* 押してから 動画が 動きだす まで（読みこみ）は 黒（動画の はじめも 黒）。動きだしたら 上の 幕は すきとおって 動画が 見える */
.ov.fz.sgd{{--t0:{sec(T0B)};--tc:.3s;z-index:31;background:#000}}
.ov.fz.sgd.go{{background:transparent}}
.ov.fz.sgd .sgs{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;display:none}}
.ov.fz.sgd.still .sgs{{display:block}}
.ov.fz.sgd .sgw{{position:absolute;inset:0;background:#FFFFFF;opacity:0;pointer-events:none}}
.ov.fz.sgd.go .sgw{{animation:sgW .7s ease-out {sec(RES - .15)} both}}
@keyframes sgW{{0%{{opacity:0}}30%{{opacity:.55}}100%{{opacity:0}}}}
.ov.fz.sgd .sgk{{position:absolute;inset:0;background:rgba(10,3,0,.6);opacity:0;pointer-events:none}}
.ov.fz.sgd.go .sgk{{animation:fadeIn .5s ease-out {sec(RES)} both}}
.ov.fz.sgd .hb{{z-index:10;visibility:hidden}}
.ov.fz.sgd.go .hb{{visibility:visible;animation:sgBoard .5s cubic-bezier(.2,.9,.3,1.1) {sec(RES)} both}}
@keyframes sgBoard{{0%{{opacity:0;transform:translateY(40px) scale(.7)}}55%{{opacity:1;transform:translateY(-8px) scale(1.04)}}100%{{opacity:1;transform:none}}}}
.ov.fz.sgd:not(.go):not(.still) *{{animation-play-state:paused!important}}
/* 視差効果を減らす（・動画が 読めない 時）：動画は 出さず さいごの 1まい（鳥居の 中の 神様的中）→ {sec(STILL_BOARD)}から ボードを ふわっと（音の ポンッと 同じ 時） */
.ov.fz.sgd.still{{--t0:{sec(STILL_T0)}}}
.ov.fz.sgd.still .sgk{{animation:fadeIn .5s ease-out {sec(STILL_BOARD - .15)} both}}
.ov.fz.sgd.still .hb{{visibility:visible;animation:fadeIn .5s ease-out {sec(STILL_BOARD)} both!important}}
'''


def sgd_js(res_from, snd):
    """ページの スクリプト（Component に 足す 所）：動画の 参照・押した 瞬間に 再生・動きだした 時に 音・とじる 時に 止める。
       snd：音が ある（sfx が ある）"""
    wake = '''  sgdWake() {
    // 押した 瞬間に 音の 準備（iPhone は タップの 中で 起こす）
    var sx = this.sfxInit();
    var AC = typeof window === 'undefined' ? null : (window.AudioContext || window.webkitAudioContext);
    if (!sx.ctx && AC) { try { sx.ctx = new AC(); } catch (e) { sx.ctx = null; } }
    if (sx.ctx && sx.ctx.state !== 'running' && sx.ctx.resume) { try { sx.ctx.resume(); } catch (e) {} }
    if (sx.ctx && !sx.ok) {
      sx.ok = 1;
      try { var s0 = sx.ctx.createBufferSource(); s0.buffer = sx.ctx.createBuffer(1, 1, 22050); s0.connect(sx.ctx.destination); s0.start(0); } catch (e) {}
    }
  }
''' if snd else ''
    return wake + '''  sgdVid(el) {
    this._sv = el || null;
  }
  sgdGo() {
    // 押した 瞬間（タップの 中で 再生：iPhone でも 動く）。視差効果を減らす・動画が 動かない 時は さいごの 1まい → ボード
    var self = this, v = this._sv;
    this._sgdOn = 0;
''' + ("    this.sgdWake();\n    this.hush();\n" if snd else '') + '''    if (!v || this.slow()) { this.sgdStill(); return; }
    try { v.currentTime = 0; } catch (e) {}
    var p = null;
    try { p = v.play(); } catch (e) { this.sgdStill(); return; }
    if (p && p.catch) p.catch(function () { self.sgdStill(); });
    clearTimeout(this._sgT);
    this._sgT = setTimeout(function () { if (!self._sgdOn) self.sgdStill(); }, 4000);
  }
  sgdPlaying() {
    // 動画が 動きだした 時：音は その 時刻から・ボードの 時計も ここから（絵と 音が ずれない）
    var v = this._sv, st = this.state || {};
    if (this._sgdOn || !v || st.ph !== 'reveal') return;
    this._sgdOn = 1;
    clearTimeout(this._sgT);
''' + ("    this.sfx('tap', v.currentTime || 0);\n" if snd else '') + '''    this.setState({ go: 1 });
  }
  sgdStill() {
    clearTimeout(this._sgT);
    this._sgdOn = 2;
    if (this._sv) { try { this._sv.pause(); } catch (e) {} }
''' + (f"    this.sfx('tap', {res_from:g}, {STILL_WAIT:g});\n" if snd else '') + '''    this.setState({ go: 2 });
  }
  sgdStop() {
    clearTimeout(this._sgT);
    this._sgdOn = 0;
    var v = this._sv;
    if (v) { try { v.pause(); v.currentTime = 0; } catch (e) {} }
  }
'''


def film_times():
    """①②③ の 時刻の 表（絵の スクリプトを 読みこまずに、書いて ある 値だけ 読む：軽い。効果音の メモ Fx_Sound の 中身に 使う）
       → {'kami_film.py': {'T':…, 'RIBS':…, …}, 'kami_film2.py': {'TT':…, 'HEAVY1':…, 'HEAVY2':…}, 'kami_film3.py': {'TT':…, 'ELEC_LOGO0':…}}"""
    import ast
    flat = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flat')
    want = {'kami_film.py': ('T', 'RIBS', 'ROCKS', 'LIFT_T', 'SHRINK'), 'kami_film2.py': ('TT', 'HEAVY1', 'HEAVY2'), 'kami_film3.py': ('TT', 'ELEC_LOGO0')}
    out = {}
    for fn, names in want.items():
        vals = {}
        for node in ast.parse(open(os.path.join(flat, fn), encoding='utf-8').read()).body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
                v = node.value
                if isinstance(v, ast.Call) and getattr(v.func, 'id', '') == 'dict':
                    vals[node.targets[0].id] = {kw.arg: ast.literal_eval(kw.value) for kw in v.keywords}
                else:
                    vals[node.targets[0].id] = ast.literal_eval(v)
        assert set(vals) == set(names), (fn, set(names) - set(vals))
        out[fn] = vals
    return out


def film_events():
    """音の ための 時刻：①②③ の 絵の スクリプトから そのまま 読む（絵を かえたら 音も 作り直すだけで そろう）。
       秒は それぞれの 場面の はじめが 0（押した 瞬間からの 秒は OFS を 足す）・左右は -1（左）〜 1（右）。③ の 雷は 字の 形から 場所を 出すので 10秒ほど かかる"""
    import sys
    import math
    import numpy as np
    flat = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flat')
    sys.path.insert(0, flat)
    import kami_film as F1
    import kami_film2 as F2
    import kami_film3 as F3
    assert (F1.N, F2.N, F3.N) == (N1, N2, N3), ((F1.N, F2.N, F3.N), (N1, N2, N3))
    # ① 上から 下への 雷：(出る 秒, 消える 秒, 左右, 形が かわる 秒)
    ribs = []
    for j, t0, t1 in F1.RIBS:
        p = F1.KM.RIBBONS[j][0]
        f0, f1 = int(math.ceil(t0 * FPS)), int(t1 * FPS)
        ribs.append((t0, t1, (p[-1][0] / 195 - 1) * .8, [f / FPS for f in F1.vbolt_changes(j, f0, f1)[1:]]))
    # ① 玉から 画面の はしへの 雷：(出る 秒, 左右, 長さ 秒)
    sb = [(f / FPS, math.cos(math.radians(a)) * .8, life / FPS) for f, a, _, _, life in F1.sphere_bolt_events()]
    el1 = F1.elec_events()
    arcs = [(f / FPS, side * .45) for f, side, *_ in el1['arcs']]
    # ③ 字の 雷：(出る 秒, 種（run＝ふちを はしる・out＝外へ・jump＝字から 字へ）, 長さ 秒, 左右)
    el3 = []
    for e in F3.elec_events():
        o = F3.obj_of(e['key'])
        R, Tv = F3.obj_pose(e['key'], e['f0'] / FPS)
        c = o['outl'][e['ci']]
        if e['kind'] == 'run':
            p, n = F3.ol_at(c, e['s0'])
        else:
            p, n = c['P'][e['i']], c['N'][e['i']]
        a, _ = F3.ol_screen(np.asarray(p, float)[None], np.asarray(n, float)[None], R, Tv)
        el3.append((e['f0'] / FPS, e['kind'], e['life'] / FPS, float(np.clip(a[0][0] / (F3.W / 2) - 1, -1, 1))))
    return dict(T1=F1.T, RIBS=ribs, ROCKS=F1.ROCKS, LIFT_T=F1.LIFT_T, LIFT_BURSTS=F1.LIFT_BURSTS, SHRINK=F1.SHRINK, SB=sb, ARCS=arcs,
                CRACK=(el1['f0'] / FPS, el1['f1'] / FPS),
                T2=F2.TT, HEAVY=(F2.HEAVY1['t'], F2.HEAVY2['t']), T3=F3.TT, EL3=el3, LOGO0=F3.ELEC_LOGO0)
