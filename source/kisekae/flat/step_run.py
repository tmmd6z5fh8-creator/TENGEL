"""桜・紅葉・雪・お正月の壁紙の馬が、いつも ゆったり 足ぶみして 首を動かす（まさちゃんの指定「この４つの壁紙、常に足と首を動かして！ゆったりめで！」）
   - 馬は いまの絵と同じ馬（horse_flat・同じ色と飾り・同じカメラ）。体は動かさず、足を1本ずつ順に上げて おろす（その場で足ぶみ）。
     地面についている足は動かさない（ひづめが すべらない）。首と頭は 足に合わせて ゆっくり上下する（1回りで2回）
   - 足の順（左右は馬の手前・奥）：前の手前 → うしろの奥 → 前の奥 → うしろの手前（1本ずつ、すきまなく つづく）
     お正月は 前足を高く上げる（いまの絵の ポーズ）・紅葉は 前足を上げて歩く ポーズ・桜と雪は 立っている ポーズから
   - 1回り CYCLE 秒を N コマ（0.1秒ずつ）。コマ0は いまの絵と同じ（1画素もちがわない）
   - コマは いまの絵を描くのと同じ流れ（flat/<テーマ>_banner.py）で、馬のポーズだけ かえて描く（背景・手前の花びらなど・影も同じ）。
     動く所（すべてのコマの ちがう所を まとめた四角）だけ 切りぬいて、たて・よこに並べた1まい（シート）にする：
       桜・紅葉・雪 … すき通しなし（背景ごと）。いまの絵の上に重ねる
       お正月 … 光より前の絵（すき通しつき）の 切りぬき。光より前の絵は その四角を すき通しにした1まい（top_hole）も作る（光が うしろで回るので）
   python3 flat/step_run.py --cams <step_cams.json>                 → 4つの馬の いまのカメラ（3倍の絵で決める・約1分）
   python3 flat/step_run.py --check <テーマ>                        → 足の動き（ひづめの高さ）を たしかめる（描かない）
   python3 flat/step_run.py --preview <テーマ> <out.png> <step_cams.json> [コマ数]  → 馬だけを 1倍で描いた一覧（形を決めるため・速い）
   python3 flat/step_run.py --frames <テーマ> <コマのフォルダ> <step_cams.json> [コマの番号…]  → コマ（PNG）を描く（コマ0を先に・sdfr がいる・1コマ 約13〜25秒）
   python3 flat/step_run.py --sheet <テーマ> <コマのフォルダ> <出力フォルダ> <step_run.json>  → <テーマ>_step.webp（シート）・お正月は newyear_top_hole.webp も・step_run.json に置く場所
   （コマ0は いまの絵と同じ書き出し方で 1バイトもちがわない：桜・紅葉・雪の いまの WebP・お正月の 光より前の WebP）"""
import sys, os, math, json, runpy, copy
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
import horse3d as Hm
from horse_flat import POSES

W, Hh = 780, 320
CYCLE = 4.0                      # 1回りの秒（足4本で1回り・首は2回 上下）
N = 40                           # 1回りの コマ数（0.1秒ずつ）
COLS = 8                         # シートの よこの コマ数（たて N/COLS 段・1段 0.8秒）
PAD = 2                          # シートの コマの まわりの のりしろ（絵の画素・画面の1px）
EDGE_REACH = 16                  # 切りぬく四角の へりを 外へ ずらして よい はば（絵の画素）
LEGS = ('fore_near', 'fore_far', 'hind_near', 'hind_far')

# 足を上げた いちばん上の形（4つの骨の向き°・horse3d の角度）
F_WALK = POSES['walk']['fore_near']            # 前足：ひざを曲げて 前へ（紅葉の いまの絵の 上げた足）
F_PRANCE = POSES['prance']['fore_near']        # 前足を高く（お正月の いまの絵の 上げた足）
H_STEP = [-45, -125, -60, -95]                 # うしろ足：ひざ（飛節）を曲げて 少し前へ
EX = dict(F=(2.0, .6, .8, 2.0), H=(1.0, 1.0, 1.0, 1.0))    # 上げぐあい s の べき（骨ごと：上 → 下）。小さいほど 先に動く（前足は ひざが先・ひづめは あとで たたむ）

# テーマごと：いまの絵のポーズ（base）・地面につく形（plant：いまの絵で上げている足だけ）・足を上げる まん中の時と はば（1回りを1）・
#   上げた形（peak：前 F／うしろ H）と 上げる大きさ（k：1＝peak まで）・首（nod：'mid'＝いまの形を まん中に上下／'top'＝いまの形が いちばん上）
THEMES = {
    'sakura': dict(base='stand', facing='left',
                   lift={'fore_near': (.125, .25), 'hind_far': (.375, .25), 'fore_far': (.625, .25), 'hind_near': (.875, .25)},
                   peak=dict(F=F_WALK, H=H_STEP), k=dict(F=.8, H=.85), nod=('mid', 6.0, 4.0)),
    'snow': dict(base='stand', facing='left',
                 lift={'fore_near': (.125, .25), 'hind_far': (.375, .25), 'fore_far': (.625, .25), 'hind_near': (.875, .25)},
                 peak=dict(F=F_WALK, H=H_STEP), k=dict(F=.8, H=.85), nod=('mid', 6.0, 4.0)),
    'autumn': dict(base='walk', facing='right', plant={'fore_near': [-124, -91, -90, -60]},
                   lift={'fore_near': (0.0, .3), 'hind_far': (.25, .25), 'fore_far': (.5, .3), 'hind_near': (.75, .25)},
                   peak=dict(F=F_WALK, H=H_STEP), k=dict(F=1.0, H=1.0), nod=('top', 8.0, 4.0)),
    'newyear': dict(base='prance', facing='left', plant={'fore_near': [-120, -94, -90, -62]},
                    lift={'fore_near': (0.0, .36), 'hind_far': (.25, .2), 'fore_far': (.5, .36), 'hind_near': (.75, .2)},
                    peak=dict(F=F_PRANCE, H=[-48, -122, -70, -98]), k=dict(F=1.0, H=1.0), nod=('top', 8.0, 4.0)),
}


def bump(u):
    """0 → 1 → 0（はじめと おわりは ゆっくり）"""
    return math.sin(math.pi * u) ** 2


def lift_amount(t, c, w):
    """時 t（1回りを1）に、まん中 c・はば w で上げる足の 上げぐあい（0〜1）"""
    d = ((t - c + .5) % 1.0) - .5
    u = d / w + .5
    return bump(u) if 0.0 < u < 1.0 else 0.0


def pose_at(name, t):
    """時 t（0〜1）の ポーズ（horse_flat の POSES と同じ形の dict）。t＝0 は いまの絵と同じ"""
    th = THEMES[name]
    P = POSES[th['base']]
    out = dict(theta=P['theta'], tail=list(P['tail']), tail_kind=P['tail_kind'])
    kind, A, B = th['nod']
    if kind == 'mid':                                   # いまの形を まん中に、上下（1回りで2回）
        f = math.sin(4 * math.pi * t)
    else:                                               # いまの形が いちばん上（足を上げた時）→ 下がって もどる
        f = -math.sin(2 * math.pi * t) ** 2
    out['neck_rot'] = round(P['neck_rot'] + A * f, 3)
    out['head_ang'] = round(P['head_ang'] + B * f, 3)
    for leg in LEGS:
        plant = th.get('plant', {}).get(leg, P[leg])
        c, w = th['lift'][leg]
        s = lift_amount(t, c, w)
        fh = 'F' if leg.startswith('fore') else 'H'
        k = th['k'][fh]
        peak = [p + (q - p) * k for p, q in zip(plant, th['peak'][fh])]
        ex = EX[fh]                                     # 骨ごとの 動きはじめ（ひづめが地面に めりこまない）
        out[leg] = [round(p + (q - p) * s ** e, 3) for p, q, e in zip(plant, peak, ex)]
    return out


def hooves(pose, facing):
    """ひづめの点（horse3d の世界の座標・手前／奥の名前で）"""
    near, far = ('L', 'R') if facing == 'right' else ('R', 'L')
    full = dict(theta=pose['theta'], neck_rot=pose['neck_rot'], head_ang=pose['head_ang'], tail=pose['tail'],
                fore={near: pose['fore_near'], far: pose['fore_far']}, hind={near: pose['hind_near'], far: pose['hind_far']})
    S = Hm.skeleton(full)
    return {'fore_near': S['F' + near]['hf'], 'fore_far': S['F' + far]['hf'], 'hind_near': S['H' + near]['hf'], 'hind_far': S['H' + far]['hf']}


def check(name, n=200):
    """足の動きを たしかめる：地面についている ひづめが動かないか・上げた ひづめが地面より下に行かないか・いちばん高い所"""
    th = THEMES[name]
    h0 = hooves(pose_at(name, 0.0), th['facing'])
    ground = {}
    for leg in LEGS:                                    # 地面についている時の ひづめ（上げていない時）
        c, w = th['lift'][leg]
        t_off = (c + .5) % 1.0
        ground[leg] = hooves(pose_at(name, t_off), th['facing'])[leg]
    worst = {leg: dict(lo=0.0, hi=0.0, dx=0.0) for leg in LEGS}
    for i in range(n):
        t = i / n
        hv = hooves(pose_at(name, t), th['facing'])
        for leg in LEGS:
            dy = hv[leg][1] - ground[leg][1]
            dx = hv[leg][0] - ground[leg][0]
            wv = worst[leg]
            wv['lo'] = min(wv['lo'], dy)
            wv['hi'] = max(wv['hi'], dy)
            wv['dx'] = max(wv['dx'], abs(dx)) if abs(dy) < 1e-9 else wv['dx']
    gy = {leg: round(float(ground[leg][1]), 4) for leg in LEGS}
    print(name, 'ground y', gy)
    for leg in LEGS:
        wv = worst[leg]
        print(f'  {leg:10s} 上げた高さ max {wv["hi"]:.3f} m・地面より下 {wv["lo"]:.4f} m・ついている時の よこずれ {wv["dx"]:.4f} m')


def ref_cams(out_json):
    """4つの馬の いまのカメラ（いまの絵と同じ：3倍の絵で frame_horse が決める）"""
    import cute_themes as C
    from horse_flat import draw_horse
    cams = {}
    for name in THEMES:
        sp = dict(C.SPOTS[name])
        sp['cam_out'] = []
        draw_horse(sp, C.PALS[name], W, Hh, acc=C.ACC[name], number='1', name=f'step_ref_{name}')
        e, t = sp['cam_out']
        cams[name] = [[float(v) for v in e], [float(v) for v in t]]
        print(name, cams[name], flush=True)
    json.dump(cams, open(out_json, 'w'), indent=1)


def spec_at(name, t, cams):
    """時 t の draw_horse の spec（いまの絵の spec の ポーズだけ かえて、カメラは いまの絵と同じ）"""
    import cute_themes as C
    sp = dict(C.SPOTS[name])
    sp['pose'] = pose_at(name, t)
    e, tg = cams[name]
    sp['cam'] = (np.asarray(e, float), np.asarray(tg, float))
    return sp


def preview(name, out_png, cams, n=16):
    """馬だけを 1倍（速い）で n コマ描いて 一覧にする（地面の線・いまの ひづめの所に 印）"""
    import cute_themes as C
    import horse_flat
    horse_flat.S3 = 1
    x0, y0, x1, y1 = C.SPOTS[name]['box']
    x0, y0, x1, y1 = x0 - 24, y0 - 24, x1 + 24, y1 + 10
    cells = []
    for i in range(n):
        t = i / n
        rgb, a, m = horse_flat.draw_horse(spec_at(name, t, cams), C.PALS[name], W, Hh, acc=C.ACC[name], number='1', name=f'step_pv{i}')
        bg = np.ones((Hh, W, 3), np.float32) * np.array([.86, .9, .84], np.float32)
        img = bg * (1 - a[..., None]) + rgb * a[..., None]
        img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        g = int(round(m['bottom']))
        cv2.line(img, (0, g), (W, g), (90, 120, 90), 1)
        c = np.ascontiguousarray(img[y0:y1, x0:x1])
        cv2.putText(c, f'{i} t={t:.3f}', (4, 14), cv2.FONT_HERSHEY_SIMPLEX, .42, (40, 40, 40), 1, cv2.LINE_AA)
        cells.append(c)
        print('preview', i, flush=True)
    cols = 4
    rows = [np.hstack(cells[r * cols:(r + 1) * cols]) for r in range(math.ceil(n / cols))]
    rows[-1] = np.hstack([rows[-1], np.full((rows[-1].shape[0], rows[0].shape[1] - rows[-1].shape[1], 3), 255, np.uint8)]) if rows[-1].shape[1] < rows[0].shape[1] else rows[-1]
    cv2.imwrite(out_png, cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))


_PARTS = {}


def banner_parts(name):
    """flat/<name>_banner.py を 馬の所で2つに分ける：馬より前（背景・乱数）は1回だけ動かして のこし、そのあと（tail）は コマごとに動かす
       （同じ乱数の つづきから描くので、いまの絵を描く流れと 1画素もちがわない）"""
    if name not in _PARTS:
        script = os.path.join(HERE, f'{name}_banner.py')
        src = open(script, encoding='utf-8').read()
        key = f"img = draw_cute(img, '{name}', W, Hh)"
        i = src.index("if os.environ.get('CUTE_NO_HORSE') != '1':")
        j = src.index(key, i) + len(key)
        g = {'__name__': '__main__', '__file__': script}
        argv = sys.argv
        sys.argv = [script, os.devnull]
        try:
            exec(compile(src[:i], script, 'exec'), g)
        finally:
            sys.argv = argv
        _PARTS[name] = (g, compile('\n' * src[:j].count('\n') + src[j:], script, 'exec'))
    return _PARTS[name]


def frame_u8(name, t, cams, ref=None):
    """時 t の コマ：いまの絵を描く流れ（flat/<name>_banner.py）で、馬だけ かえた絵（u8）と 馬の目印。
       桜・紅葉・雪は 絵ぜんぶ（RGB）、お正月は 光より前の絵（RGBA：黒と白の上に描いた差から すき通し＝newyear_banner.layers と同じ）。
       ref：影を決める目印（コマ0の ひづめ・いちばん下）。None なら この コマの目印で（＝いまの絵と同じ）"""
    import cute_themes as C
    import style2d
    script = os.path.join(HERE, f'{name}_banner.py')
    spec = spec_at(name, t, cams)
    cache = {}
    real_dh, real_dc = C.draw_horse, C.draw_cute

    def dh(*a, **kw):                                   # 馬は 1コマに1回だけ描く（お正月は 黒と白の上に2回 つかう）
        if 'r' not in cache:
            cache['r'] = real_dh(*a, **kw)
        return cache['r']

    def dc(img, theme, W_, H_):
        assert theme == name
        return real_dc(img, theme, W_, H_, spec=spec, shadow_marks=ref)

    C.draw_horse, C.draw_cute = dh, dc
    try:
        if name == 'newyear':
            g = runpy.run_path(script, run_name='step_run')
            k, w = g['render']('fg', (0, 0, 0)), g['render']('fg', (1, 1, 1))
            a = np.clip(1 - (w - k).mean(axis=2), 0, 1)
            col = np.where(a[..., None] > 1e-4, k / np.maximum(a, 1e-4)[..., None], 0)
            u8 = (np.dstack([np.clip(col, 0, 1), a]) * 255 + .5).astype(np.uint8)
        else:                                           # 馬より前（背景）は1回だけ描いて、馬と そのあと（手前の花びらなど）を コマごとに
            g, tail = banner_parts(name)
            got = {}
            g2 = dict(g, rng=copy.deepcopy(g['rng']), save_webp=lambda img, path, q=88: got.setdefault('img', img))
            g2['img'] = dc(g['img'].copy(), name, W, Hh)
            exec(tail, g2)
            u8 = (np.clip(got['img'], 0, 1) * 255 + .5).astype(np.uint8)
    finally:
        C.draw_horse, C.draw_cute = real_dh, real_dc
    return u8, cache['r'][2]


def save_png(path, u8):
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA if u8.shape[2] == 4 else cv2.COLOR_RGB2BGR))


def load_png(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    return cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA if im.shape[2] == 4 else cv2.COLOR_BGR2RGB)


def render_frames(name, outdir, cams, idxs):
    """コマを描いて <outdir>/<name>_fNN.png に（コマ0を先に：影の目印を <name>_ref.json に）"""
    os.makedirs(outdir, exist_ok=True)
    rf = f'{outdir}/{name}_ref.json'
    for i in idxs:
        if i != 0 and not os.path.exists(rf):
            raise SystemExit('コマ0を先に描く（影の目印）')
        ref = None
        if i != 0:
            r = json.load(open(rf))
            ref = dict(hooves=[np.asarray(h, float) for h in r['hooves']], bottom=r['bottom'])
        u8, m = frame_u8(name, i / N, cams, ref)
        if i == 0:
            json.dump(dict(hooves=[[float(v) for v in h] for h in m['hooves']], bottom=float(m['bottom'])), open(rf, 'w'))
        save_png(f'{outdir}/{name}_f{i:02d}.png', u8)
        print(name, 'frame', i, flush=True)


def calm_edges(f0, x0, y0, x1, y1, reach=EDGE_REACH):
    """切りぬく四角の 4つの へりを、外へ reach 画素まで ずらして、絵の こまかい所（しっぽの毛・ふち）を通らない所にする
       （へりの 内と外で ちがう書き出しの絵が となりあうので、こまかい所を通ると 細い線が見える）。へりの まわり3画素の 明るさの変わりで くらべる"""
    a = f0.astype(np.float32)
    if a.shape[2] == 4:                                # すき通しつき：色に こさを かけて、すき通しの 変わりも入れる
        a = np.dstack([a[..., :3] * a[..., 3:] / 255, a[..., 3:]])
    gx = np.abs(np.diff(a, axis=1)).max(2)             # よこの となりとの ちがい（x と x+1）
    gy = np.abs(np.diff(a, axis=0)).max(2)

    def cost_v(x, ya, yb):                             # たての へり x（x−1 と x のあいだ）
        lo, hi = max(0, x - 2), min(gx.shape[1], x + 1)
        return float(gx[ya:yb, lo:hi].mean())

    def cost_h(y, xa, xb):
        lo, hi = max(0, y - 2), min(gy.shape[0], y + 1)
        return float(gy[lo:hi, xa:xb].mean())
    best = lambda cands: min(cands, key=lambda c: (round(c[1], 1), c[2]))[0]
    x0 = best([(x, cost_v(x, y0, y1), x0 - x) for x in range(x0, max(2, x0 - reach) - 1, -1)])
    x1 = best([(x, cost_v(x, y0, y1), x - x1) for x in range(x1, min(W - 2, x1 + reach) + 1)])
    y0 = best([(y, cost_h(y, x0, x1), y0 - y) for y in range(y0, max(2, y0 - reach) - 1, -1)])
    y1 = best([(y, cost_h(y, x0, x1), y - y1) for y in range(y1, min(Hh - 2, y1 + reach) + 1)])
    return x0, y0, x1, y1


def make_sheet(name, frdir, outdir, run_json):
    """コマ（<frdir>/<name>_fNN.png）→ 動く所（どれかの コマで コマ0と ちがう画素をまとめた四角）を切りぬいて、
       よこ COLS・たて N/COLS に並べた1まい（<outdir>/<name>_step.webp・ロスなし）。コマの まわりには のりしろ（PAD・絵の となりの画素）をつける
       （3倍の画面などで 絵を大きくして見る時に、となりのコマが ふちに にじまない）。お正月は 光より前の絵の その四角を すき通しにした1まい
       （<outdir>/newyear_top_hole.webp）も。置く場所と大きさを run_json（テーマごと）に書く"""
    from PIL import Image
    fr = [load_png(f'{frdir}/{name}_f{i:02d}.png') for i in range(N)]
    f0 = fr[0].astype(np.int16)
    d = np.zeros(f0.shape[:2], bool)
    for f in fr[1:]:
        d |= np.abs(f.astype(np.int16) - f0).max(2) > 0
    ys, xs = np.nonzero(d)
    pad = 2
    x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + 1 + pad)
    y0, y1 = max(0, ys.min() - pad), min(Hh, ys.max() + 1 + pad)
    x0, y0, x1, y1 = calm_edges(fr[0], x0, y0, x1, y1)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2                  # 画面の画素（半分）にそろえる
    x1, y1 = x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2
    cw, ch = int(x1 - x0), int(y1 - y0)
    rows = N // COLS
    P = PAD                                            # コマの まわりに 本当の となりの画素を P ずつ（大きくして見る画面で となりのコマが にじまない）
    cw2, ch2 = cw + 2 * P, ch + 2 * P
    sh = np.zeros((rows * ch2, COLS * cw2, fr[0].shape[2]), np.uint8)
    for i, f in enumerate(fr):
        r, c = divmod(i, COLS)
        fp = np.pad(f, ((P, P), (P, P), (0, 0)), mode='edge')       # 絵の はしに かかる時だけ はしの画素をのばす
        sh[r * ch2:(r + 1) * ch2, c * cw2:(c + 1) * cw2] = fp[y0:y1 + 2 * P, x0:x1 + 2 * P]
    os.makedirs(outdir, exist_ok=True)
    # シートは ロスなし（ロスありだと、コマごとに 動かない所の にじみ方が ちがって、めくるたびに ちらちらする）
    Image.fromarray(sh, 'RGBA' if sh.shape[2] == 4 else 'RGB').save(f'{outdir}/{name}_step.webp', 'WEBP', lossless=True, quality=100, method=6)
    if sh.shape[2] == 4:                               # お正月：光より前の絵の 穴あき（光より前の絵と同じ書き出し方）
        top = fr[0].copy()
        top[y0 + P:y1 - P, x0 + P:x1 - P, 3] = 0       # ふちの P は のこす（3倍の画面で 穴のふちが すけない。そこは シートと同じ絵）・色も のこす
        Image.fromarray(top, 'RGBA').save(f'{outdir}/{name}_top_hole.webp', 'WEBP', quality=90, method=6)
    run = json.load(open(run_json)) if os.path.exists(run_json) else {}
    run[name] = dict(frames=N, cols=COLS, rows=rows, cell=[cw, ch], pad=P, at=[int(x0), int(y0)], cycle=CYCLE, size=[W, Hh])
    json.dump(run, open(run_json, 'w'), ensure_ascii=False, indent=1)
    kb = os.path.getsize(f'{outdir}/{name}_step.webp') / 1024
    print(name, 'sheet', sh.shape[1], 'x', sh.shape[0], f'{kb:.0f}KB', run[name])


if __name__ == '__main__':
    if sys.argv[1] == '--check':
        for nm in sys.argv[2:] or list(THEMES):
            check(nm)
    elif sys.argv[1] == '--cams':
        ref_cams(sys.argv[2])
    elif sys.argv[1] == '--preview':
        preview(sys.argv[2], sys.argv[3], json.load(open(sys.argv[4])), int(sys.argv[5]) if len(sys.argv) > 5 else 16)
    elif sys.argv[1] == '--sheet':
        make_sheet(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == '--frames':
        nm, outdir, cams = sys.argv[2], sys.argv[3], json.load(open(sys.argv[4]))
        idxs = [int(v) for v in sys.argv[5:]] or list(range(N))
        render_frames(nm, outdir, cams, idxs)
