"""桜・紅葉・雪・お正月の壁紙の馬が、ときどき 前足を動かしたり、首を下げて 草を食べたりする
   （まさちゃんの指定「この4枚の壁紙後ろ脚動かさない 前足は、6秒〜9秒のランダムで2回動かす。ゆったり 1秒〜5秒のランダムで、地面の草を食べる5秒〜10秒でリピートする。」）
   - 馬は いまの絵と同じ馬（horse_flat・同じ色と飾り・同じカメラ）。体と うしろ足と しっぽは 動かさない
   - コマ（47まい・名前と順は ../step_plan.py）：首を上げた形・首を下げていく とちゅう（11）・首を下げた形（草を食べる頭の動き 3）・
     首を上げたまま／下げたまま 手前／奥の前足を上げていく形（8ずつ）。首は 根元から まげて 少しのばす（r3d/horse3d.py の neck_bend・neck_len）
   - いつ どのコマを出すか（時間わり）は ../step_plan.py（きまった種の ランダム・約2分の くり返し）。ページの CSS は ../step_wall.py
   - コマ0は いまの絵と同じ（1画素もちがわない）：桜・雪は 立っている形、紅葉・お正月は 手前の前足を上げた形
   - コマは いまの絵を描くのと同じ流れ（flat/<テーマ>_banner.py）で、馬のポーズだけ かえて描く（背景・手前の花びらなど・影も同じ）。
     動く所（すべてのコマの ちがう所を まとめた四角）だけ 切りぬいて、たて・よこに並べた1まい（シート）にする：
       桜・紅葉・雪 … すき通しなし（背景ごと）。いまの絵の上に重ねる
       お正月 … 光より前の絵（すき通しつき）の 切りぬき。光より前の絵は その四角を すき通しにした1まい（top_hole）も作る（光が うしろで回るので）
   python3 flat/step_run.py --cams <step_cams.json>                 → 4つの馬の いまのカメラ（3倍の絵で決める・約1分）
   python3 flat/step_run.py --check [テーマ…]                        → ひづめ（うしろ足と 地面についている前足が 動かない・上げた足が 地面より下に行かない）と 鼻先の高さ（描かない）
   python3 flat/step_run.py --preview <テーマ> <out.png> <step_cams.json> [コマの名前…]  → 馬だけを 1倍で描いた一覧（形を決めるため・速い）
   python3 flat/step_run.py --frames <テーマ> <コマのフォルダ> <step_cams.json> [コマの番号…]  → コマ（PNG）を描く（コマ0を先に・sdfr がいる・1コマ 約15〜30秒）
   python3 flat/step_run.py --sheet <テーマ> <コマのフォルダ> <出力フォルダ> <step_run.json>  → <テーマ>_step.webp（シート）・お正月は newyear_top_hole.webp も・step_run.json に置く場所
   （コマ0は いまの絵と同じ書き出し方で 1バイトもちがわない：桜・紅葉・雪の いまの WebP・お正月の 光より前の WebP）"""
import sys, os, math, json, runpy, copy
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import horse3d as Hm
from horse_flat import POSES
import step_plan as SP

W, Hh = 780, 320
COLS = 8                         # シートの よこの コマ数
PAD = 2                          # シートの コマの まわりの のりしろ（絵の画素・画面の1px）
EDGE_REACH = 16                  # 切りぬく四角の へりを 外へ ずらして よい はば（絵の画素）
LEGS = ('fore_near', 'fore_far', 'hind_near', 'hind_far')

# 前足を上げた いちばん上の形（4つの骨の向き°・horse3d の角度）
F_WALK = POSES['walk']['fore_near']            # ひざを曲げて 前へ（紅葉の いまの絵の 上げた足）
F_PRANCE = POSES['prance']['fore_near']        # 高く（お正月の いまの絵の 上げた足）
EX = (2.0, .6, .8, 2.0)                        # 上げぐあい s の べき（骨ごと：上 → 下）。小さいほど 先に動く（ひざが先・ひづめは あとで たたむ）
K_DOWN = 0.65                                  # 首を下げている時は 前足を 少し低く上げる（peak までの わりあい）
NIB = {0: (0.0, 0.0), 1: (2.0, 5.0), 2: (4.0, 8.0)}    # 草を食べる頭の動き：首のまげ（°）と 頭の角度（°）に たす

# テーマごと：いまの絵のポーズ（base）・地面につく形（plant：いまの絵で上げている足だけ）・前足を上げた形（peak）と 上げる大きさ（k：1＝peak まで）・
#   首を下げた形（down：首のまげ°・首ののばし・頭の角度°。鼻先が 前足の 約0.8m前の 地面の すぐ上に来る）
THEMES = {
    'sakura': dict(base='stand', facing='left', peak=F_WALK, k=.8, down=(-98.0, 1.20, -92.0)),
    'snow': dict(base='stand', facing='left', peak=F_WALK, k=.8, down=(-98.0, 1.20, -92.0)),
    'autumn': dict(base='walk', facing='right', plant={'fore_near': [-124, -91, -90, -60]}, peak=F_WALK, k=1.0, down=(-96.0, 1.20, -92.0)),
    'newyear': dict(base='prance', facing='left', plant={'fore_near': [-120, -94, -90, -62]}, peak=F_PRANCE, k=1.0, down=(-108.0, 1.30, -90.0)),
}


def ease(u):
    """0 → 1（はじめと おわりは ゆっくり）"""
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, u)))


def parse(fn):
    """コマの名前 → (首の下げぐあい 0〜1, 頭の動き 0〜2, 上げる前足 or None, 上げぐあい 0〜1)"""
    if fn == 'U0':
        return 0.0, 0, None, 0.0
    if fn[0] == 'L':
        return int(fn[1:]) / SP.LOWER_N, 0, None, 0.0
    if fn in ('D0', 'D1', 'D2'):
        return 1.0, int(fn[1]), None, 0.0
    head = 0.0 if fn[0] == 'U' else 1.0
    leg = 'fore_near' if fn[1] == 'N' else 'fore_far'
    return head, 0, leg, ease(int(fn[2:]) / SP.LIFT_N)


def pose_of(name, fn):
    """コマの名前の ポーズ（horse_flat の POSES と同じ形の dict）"""
    th = THEMES[name]
    P = POSES[th['base']]
    out = {k: (list(v) if isinstance(v, list) else v) for k, v in P.items()}
    for leg, v in th.get('plant', {}).items():
        out[leg] = list(v)
    head, nib, leg, s = parse(fn)
    if head > 0:
        Bd, Ld, Hd = th['down']
        e, eh = ease(head), ease(head) ** 1.25            # 頭の向きは 少し おくれて 下を向く
        db, dh = NIB[nib]
        out['neck_bend'] = round(Bd * e + db, 3)
        out['neck_len'] = round(1 + (Ld - 1) * e, 4)
        out['head_ang'] = round(P['head_ang'] + (Hd - P['head_ang']) * eh + dh, 3)
    if leg:
        plant = out[leg]
        k = th['k'] if head == 0 else K_DOWN
        peak = [p + (q - p) * k for p, q in zip(plant, th['peak'])]
        out[leg] = [round(p + (q - p) * s ** ex, 3) for p, q, ex in zip(plant, peak, EX)]
    return out


def first_pose_is_now(name):
    """コマ0の ポーズが いまの絵の ポーズと 同じか"""
    P = POSES[THEMES[name]['base']]
    q = pose_of(name, SP.frames(name)[0])
    return all(q[k] == P[k] for k in P) and set(q) == set(P)


def skel(pose, facing):
    near, far = ('L', 'R') if facing == 'right' else ('R', 'L')
    full = dict(theta=pose['theta'], neck_rot=pose['neck_rot'], head_ang=pose['head_ang'], tail=pose['tail'],
                fore={near: pose['fore_near'], far: pose['fore_far']}, hind={near: pose['hind_near'], far: pose['hind_far']})
    if pose.get('neck_bend'):
        full['neck_bend'], full['neck_len'] = pose['neck_bend'], pose['neck_len']
    return Hm.skeleton(full), near, far


def check(name):
    """うしろ足・地面についている前足の ひづめが 動かないか・上げた ひづめが 地面より下に行かないか・鼻先の高さ（首を下げた時）"""
    th = THEMES[name]
    fr = SP.frames(name)
    ref, near, far = skel(pose_of(name, 'U0'), th['facing'])
    key = {'fore_near': 'F' + near, 'fore_far': 'F' + far, 'hind_near': 'H' + near, 'hind_far': 'H' + far}
    g0 = {leg: np.asarray(ref[key[leg]]['hf'], float) for leg in LEGS}
    ground = min(v[1] for v in g0.values())
    worst = dict(moved=0.0, below=0.0, hi=0.0, mz_lo=9.0, mz_hi=-9.0)
    for fn in fr:
        S, _, _ = skel(pose_of(name, fn), th['facing'])
        _, _, lifted, _ = parse(fn)
        for leg in LEGS:
            h = np.asarray(S[key[leg]]['hf'], float)
            if leg == lifted:
                worst['below'] = min(worst['below'], h[1] - g0[leg][1])
                worst['hi'] = max(worst['hi'], h[1] - g0[leg][1])
            else:
                worst['moved'] = max(worst['moved'], float(np.abs(h - g0[leg]).max()))
        if parse(fn)[0] == 1.0:
            mz = np.asarray(Hm.head_pt(S, 0.60, -0.03), float)
            worst['mz_lo'] = min(worst['mz_lo'], mz[1] - ground)
            worst['mz_hi'] = max(worst['mz_hi'], mz[1] - ground)
    print(f'{name}: コマ0＝いまの絵 {first_pose_is_now(name)}・地面の足の ずれ max {worst["moved"]:.6f} m・上げた ひづめ 高さ max {worst["hi"]:.3f} m'
          f'（地面より下 {worst["below"]:.4f} m）・首を下げた時の 鼻先 {worst["mz_lo"]:.3f}〜{worst["mz_hi"]:.3f} m（地面から）')


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


def spec_of(name, pose, cams):
    """draw_horse の spec（いまの絵の spec の ポーズだけ かえて、カメラは いまの絵と同じ）"""
    import cute_themes as C
    sp = dict(C.SPOTS[name])
    sp['pose'] = pose
    e, tg = cams[name]
    sp['cam'] = (np.asarray(e, float), np.asarray(tg, float))
    return sp


def preview(name, out_png, cams, fns=None):
    """馬だけを 1倍（速い）で描いて 一覧にする（地面の線つき）"""
    import cute_themes as C
    import horse_flat
    horse_flat.S3 = 1
    fns = fns or SP.frames(name)
    x0, y0, x1, y1 = C.SPOTS[name]['box']
    x0, y0, x1, y1 = x0 - 60, y0 - 30, x1 + 60, y1 + 14
    cells = []
    for i, fn in enumerate(fns):
        rgb, a, m = horse_flat.draw_horse(spec_of(name, pose_of(name, fn), cams), C.PALS[name], W, Hh, acc=C.ACC[name], number='1', name=f'step_pv{i}')
        bg = np.ones((Hh, W, 3), np.float32) * np.array([.86, .9, .84], np.float32)
        img = bg * (1 - a[..., None]) + rgb * a[..., None]
        img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        g = int(round(m['bottom']))
        cv2.line(img, (0, g), (W, g), (90, 120, 90), 1)
        c = np.ascontiguousarray(img[y0:y1, x0:x1])
        cv2.putText(c, fn, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, .42, (40, 40, 40), 1, cv2.LINE_AA)
        cells.append(c)
        print('preview', fn, flush=True)
    cols = 6
    rows = []
    for r in range(math.ceil(len(cells) / cols)):
        row = cells[r * cols:(r + 1) * cols]
        row += [np.full_like(cells[0], 255)] * (cols - len(row))
        rows.append(np.hstack(row))
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


def frame_u8(name, pose, cams, ref=None):
    """ポーズ pose の コマ：いまの絵を描く流れ（flat/<name>_banner.py）で、馬だけ かえた絵（u8）と 馬の目印。
       桜・紅葉・雪は 絵ぜんぶ（RGB）、お正月は 光より前の絵（RGBA：黒と白の上に描いた差から すき通し＝newyear_banner.layers と同じ）。
       ref：影を決める目印（コマ0の ひづめ・いちばん下）。None なら この コマの目印で（＝いまの絵と同じ）"""
    import cute_themes as C
    script = os.path.join(HERE, f'{name}_banner.py')
    spec = spec_of(name, pose, cams)
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
    """コマを描いて <outdir>/<name>_fNN.png に（NN は シートの順＝step_plan.frames の番号。コマ0を先に：影の目印を <name>_ref.json に）"""
    assert first_pose_is_now(name)
    fns = SP.frames(name)
    os.makedirs(outdir, exist_ok=True)
    rf = f'{outdir}/{name}_ref.json'
    for i in idxs:
        if i != 0 and not os.path.exists(rf):
            raise SystemExit('コマ0を先に描く（影の目印）')
        ref = None
        if i != 0:
            r = json.load(open(rf))
            ref = dict(hooves=[np.asarray(h, float) for h in r['hooves']], bottom=r['bottom'])
        u8, m = frame_u8(name, pose_of(name, fns[i]), cams, ref)
        if i == 0:
            json.dump(dict(hooves=[[float(v) for v in h] for h in m['hooves']], bottom=float(m['bottom'])), open(rf, 'w'))
        save_png(f'{outdir}/{name}_f{i:02d}.png', u8)
        print(name, 'frame', i, fns[i], flush=True)


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
       よこ COLS に並べた1まい（<outdir>/<name>_step.webp・ロスなし）。コマの まわりには のりしろ（PAD・絵の となりの画素）をつける
       （3倍の画面などで 絵を大きくして見る時に、となりのコマが ふちに にじまない）。お正月は 光より前の絵の その四角を すき通しにした1まい
       （<outdir>/newyear_top_hole.webp）も。置く場所と大きさ・時間わり（step_plan の種の番号）を run_json（テーマごと）に書く"""
    from PIL import Image
    fns = SP.frames(name)
    N = len(fns)
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
    rows = math.ceil(N / COLS)
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
    k, (T, _, _) = SP.plan(name)
    loop_ms, tl = SP.timeline(name, k=k)
    run = json.load(open(run_json)) if os.path.exists(run_json) else {}
    run[name] = dict(frames=N, names=fns, cols=COLS, rows=rows, cell=[cw, ch], pad=P, at=[int(x0), int(y0)], size=[W, Hh],
                     plan=dict(seed=SP.SEEDS[name], k=k, loop_ms=loop_ms, changes=len(tl)))
    txt = json.dumps(run, ensure_ascii=False, indent=1)
    for nm in run:                                     # コマの名前の並びは 1行に
        if 'names' in run[nm]:
            txt = txt.replace(json.dumps(run[nm]['names'], ensure_ascii=False, indent=1).replace('\n', '\n  '),
                              json.dumps(run[nm]['names'], ensure_ascii=False))
    open(run_json, 'w').write(txt)
    kb = os.path.getsize(f'{outdir}/{name}_step.webp') / 1024
    print(name, 'sheet', sh.shape[1], 'x', sh.shape[0], f'{kb:.0f}KB', {k_: v for k_, v in run[name].items() if k_ != 'names'})


if __name__ == '__main__':
    if sys.argv[1] == '--check':
        for nm in sys.argv[2:] or list(THEMES):
            check(nm)
    elif sys.argv[1] == '--cams':
        ref_cams(sys.argv[2])
    elif sys.argv[1] == '--preview':
        preview(sys.argv[2], sys.argv[3], json.load(open(sys.argv[4])), sys.argv[5:] or None)
    elif sys.argv[1] == '--sheet':
        make_sheet(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == '--frames':
        nm, outdir, cams = sys.argv[2], sys.argv[3], json.load(open(sys.argv[4]))
        idxs = [int(v) for v in sys.argv[5:]] or list(range(len(SP.frames(nm))))
        render_frames(nm, outdir, cams, idxs)
