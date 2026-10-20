"""桜・紅葉・雪の壁紙の馬が、ときどき 首を下げて 草を食べる（足は 4本とも 動かさない）
   （まさちゃんの指定「この4枚の壁紙後ろ脚動かさない 前足は、6秒〜9秒のランダムで2回動かす。ゆったり 1秒〜5秒のランダムで、地面の草を食べる5秒〜10秒でリピートする。」
    →「やっぱり4枚とも前脚も動かさなくていいよ！ あと首の動きもっとスムーズにして！」。お正月は「一枚目太陽の位置を富士山の真ん中に合わせて！馬の動きは無くして！」で 馬を動かさない＝ここから外した）
   - 馬は いまの絵と同じ馬（horse_flat・同じ色と飾り・同じカメラ）。体と 足と しっぽは 動かさない（紅葉は 前足を上げた いまの形のまま）
   - コマ（名前と順は ../step_plan.py）：首を上げた形（いまの絵）・首を下げていく とちゅう・首を下げた形・草を食べる頭の動き。
     首は 根元から まげて 少しのばす（r3d/horse3d.py の neck_bend・neck_len）。とちゅうの コマの 下げぐあいは、頭の動く道のりが 同じ はばになるように
     えらぶ（lower_levels：コマを めくる はやさが 動きの はやさに合う＝なめらか）
   - いつ どのコマを出すか（時間わり）は ../step_plan.py（きまった種の ランダム・約2分の くり返し）。ページの CSS は ../step_wall.py
   - コマ0は いまの絵と同じ（1画素もちがわない）
   - コマは いまの絵を描くのと同じ流れ（flat/<テーマ>_banner.py）で、馬のポーズだけ かえて描く（背景・手前の花びらなど・影も同じ）。
     動く所（すべてのコマの ちがう所を まとめた四角）だけ 切りぬいて、たて・よこに並べた1まい（シート）にする（すき通しなし・背景ごと。いまの絵の上に重ねる）
   python3 flat/step_run.py --cams <step_cams.json>                 → 3つの馬の いまのカメラ（3倍の絵で決める・約1分）
   python3 flat/step_run.py --check [テーマ…]                        → 足（4本の ひづめが 動かない）と 首を下げた時の 鼻先の高さ・下げぐあい（描かない）
   python3 flat/step_run.py --preview <テーマ> <out.png> <step_cams.json> [コマの名前…]  → 馬だけを 1倍で描いた一覧（形を決めるため・速い）
   python3 flat/step_run.py --frames <テーマ> <コマのフォルダ> <step_cams.json> [コマの番号…]  → コマ（PNG）を描く（コマ0を先に・sdfr がいる・1コマ 約13秒）
   python3 flat/step_run.py --sheet <テーマ> <コマのフォルダ> <出力フォルダ> <step_run.json>  → <テーマ>_step.webp（シート）・step_run.json に置く場所
   （コマ0は いまの絵と同じ書き出し方で 1バイトもちがわない：桜・紅葉・雪の いまの WebP）"""
import sys, os, math, json, copy
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
NOD = (5.0, 10.0)                # 草を食べる頭の動き（いちばん上）：首のまげ（°）と 頭の角度（°）に たす

# テーマごと：いまの絵のポーズ（base）・首を下げた形（down：首のまげ°・首ののばし・頭の角度°。鼻先が 前足の 約0.8m前の 地面の すぐ上に来る）
THEMES = {
    'sakura': dict(base='stand', facing='left', down=(-98.0, 1.20, -92.0)),
    'snow': dict(base='stand', facing='left', down=(-98.0, 1.20, -92.0)),
    'autumn': dict(base='walk', facing='right', down=(-96.0, 1.20, -92.0)),
}


def pose_at(name, p, q=0.0):
    """首の下げぐあい p（0〜1）・草を食べる頭の動き q（0〜1）の ポーズ（horse_flat の POSES と同じ形の dict）。p＝q＝0 は いまの絵"""
    th = THEMES[name]
    P = POSES[th['base']]
    out = {k: (list(v) if isinstance(v, list) else v) for k, v in P.items()}
    if p > 0 or q > 0:
        Bd, Ld, Hd = th['down']
        out['neck_bend'] = round(Bd * p + NOD[0] * q, 4)
        out['neck_len'] = round(1 + (Ld - 1) * p, 5)
        out['head_ang'] = round(P['head_ang'] + (Hd - P['head_ang']) * p ** 1.25 + NOD[1] * q, 4)   # 頭は 少し おくれて 下を向く
    return out


def skel(pose, facing):
    near, far = ('L', 'R') if facing == 'right' else ('R', 'L')
    full = dict(theta=pose['theta'], neck_rot=pose['neck_rot'], head_ang=pose['head_ang'], tail=pose['tail'],
                fore={near: pose['fore_near'], far: pose['fore_far']}, hind={near: pose['hind_near'], far: pose['hind_far']})
    if pose.get('neck_bend'):
        full['neck_bend'], full['neck_len'] = pose['neck_bend'], pose['neck_len']
    return Hm.skeleton(full), near, far


MARK_HEAD_SCALE = 1.1           # 目印の 頭の大きさ（horse3d の はじめの HEAD_SCALE）。horse_flat.draw_horse は Hm.HEAD_SCALE を 1.14 に かえたままにするので、
                                # 描いたあとでも 同じ 下げぐあいに なるように ここで決める（決めないと コマを描く順で 下げぐあいが かわる）


def head_marks(name, p):
    """首の下げぐあい p の時の 頭と首の 目印（世界の xy）：鼻先・うなじ・首の上と下の まん中"""
    S, _, _ = skel(pose_at(name, p), THEMES[name]['facing'])
    hs0 = Hm.HEAD_SCALE
    Hm.HEAD_SCALE = MARK_HEAD_SCALE
    try:
        pts = [Hm.head_pt(S, 0.60, -0.03), S['poll'], Hm.bez(S['crest'], np.array([0.5]))[0], Hm.bez(S['throat'], np.array([0.5]))[0]]
    finally:
        Hm.HEAD_SCALE = hs0
    return np.array([np.asarray(v, float)[:2] for v in pts])


def lower_levels(name, n=SP.LOWER_N):
    """首を下げていく とちゅうの コマ（L1〜L{n−1}）の 下げぐあい：頭と首の 目印の いちばん大きく動く所の 道のりが 同じ はばに なるように
       （コマの あいだの 動きが どこでも 同じくらい＝なめらか）。小数5けた"""
    ps = np.linspace(0, 1, 801)
    m = np.array([head_marks(name, p) for p in ps])
    step = np.linalg.norm(np.diff(m, axis=0), axis=2).max(1)
    d = np.concatenate([[0], np.cumsum(step)])
    lv = np.interp(np.linspace(0, d[-1], n + 1), d, ps)[1:-1]
    return [round(float(v), 5) for v in lv]


_LV = {}


def levels(name):
    if name not in _LV:
        _LV[name] = lower_levels(name)
    return _LV[name]


def parse(name, fn):
    """コマの名前 → (首の下げぐあい p, 頭の動き q)"""
    if fn == 'U0':
        return 0.0, 0.0
    if fn[0] == 'L':
        return levels(name)[int(fn[1:]) - 1], 0.0
    if fn == 'D0':
        return 1.0, 0.0
    return 1.0, int(fn[1:]) / SP.NOD_N


def pose_of(name, fn):
    """コマの名前の ポーズ"""
    return pose_at(name, *parse(name, fn))


def first_pose_is_now(name):
    """コマ0の ポーズが いまの絵の ポーズと 同じか"""
    P = POSES[THEMES[name]['base']]
    q = pose_of(name, SP.frames(name)[0])
    return all(q[k] == P[k] for k in P) and set(q) == set(P)


def check(name):
    """4本の ひづめが 動かないか・首を下げた時の 鼻先の高さ・下げぐあいの はば"""
    th = THEMES[name]
    ref, near, far = skel(pose_of(name, 'U0'), th['facing'])
    key = {'fore_near': 'F' + near, 'fore_far': 'F' + far, 'hind_near': 'H' + near, 'hind_far': 'H' + far}
    g0 = {leg: np.asarray(ref[key[leg]]['hf'], float) for leg in LEGS}
    ground = min(v[1] for v in g0.values())
    moved, mz = 0.0, []
    for fn in SP.frames(name):
        S, _, _ = skel(pose_of(name, fn), th['facing'])
        for leg in LEGS:
            moved = max(moved, float(np.abs(np.asarray(S[key[leg]]['hf'], float) - g0[leg]).max()))
        if parse(name, fn)[0] == 1.0:
            mz.append(float(np.asarray(Hm.head_pt(S, 0.60, -0.03), float)[1] - ground))
    lv = [0.0] + levels(name) + [1.0]
    m = np.array([head_marks(name, p) for p in lv])
    stp = np.linalg.norm(np.diff(m, axis=0), axis=2).max(1)
    print(f'{name}: コマ0＝いまの絵 {first_pose_is_now(name)}・ひづめの ずれ max {moved:.6f} m・首を下げた時の 鼻先 {min(mz):.3f}〜{max(mz):.3f} m（地面から）'
          f'・コマの あいだの 動き {stp.min() * 100:.2f}〜{stp.max() * 100:.2f} cm（{len(lv) - 1} だんかい）')


def ref_cams(out_json):
    """3つの馬の いまのカメラ（いまの絵と同じ：3倍の絵で frame_horse が決める）"""
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
    """ポーズ pose の コマ：いまの絵を描く流れ（flat/<name>_banner.py）で、馬だけ かえた絵（u8・RGB の 絵ぜんぶ）と 馬の目印。
       ref：影を決める目印（コマ0の ひづめ・いちばん下）。None なら この コマの目印で（＝いまの絵と同じ）"""
    import cute_themes as C
    script = os.path.join(HERE, f'{name}_banner.py')
    spec = spec_of(name, pose, cams)
    cache = {}
    real_dh, real_dc = C.draw_horse, C.draw_cute

    def dh(*a, **kw):                                   # 馬は 1コマに1回だけ描く
        if 'r' not in cache:
            cache['r'] = real_dh(*a, **kw)
        return cache['r']

    def dc(img, theme, W_, H_):
        assert theme == name
        return real_dc(img, theme, W_, H_, spec=spec, shadow_marks=ref)

    C.draw_horse, C.draw_cute = dh, dc
    try:
        g, tail = banner_parts(name)                    # 馬より前（背景）は1回だけ描いて、馬と そのあと（手前の花びらなど）を コマごとに
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
       （3倍の画面などで 絵を大きくして見る時に、となりのコマが ふちに にじまない）。置く場所と大きさ・時間わり（step_plan の種の番号）を run_json（テーマごと）に書く"""
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
    Image.fromarray(sh, 'RGB').save(f'{outdir}/{name}_step.webp', 'WEBP', lossless=True, quality=100, method=6)
    k, _ = SP.plan(name)
    loop_ms, tl = SP.timeline(name, levels(name), k=k)
    run = json.load(open(run_json)) if os.path.exists(run_json) else {}
    run[name] = dict(frames=N, names=fns, lower=levels(name), cols=COLS, rows=rows, cell=[cw, ch], pad=P, at=[int(x0), int(y0)], size=[W, Hh],
                     plan=dict(seed=SP.SEEDS[name], k=k, loop_ms=loop_ms, changes=len(tl)))
    txt = json.dumps(run, ensure_ascii=False, indent=1)
    for nm in run:                                     # コマの名前・下げぐあいの 並びは 1行に
        for key in ('names', 'lower'):
            if key in run[nm]:
                txt = txt.replace(json.dumps(run[nm][key], ensure_ascii=False, indent=1).replace('\n', '\n  '),
                                  json.dumps(run[nm][key], ensure_ascii=False))
    open(run_json, 'w').write(txt)
    kb = os.path.getsize(f'{outdir}/{name}_step.webp') / 1024
    print(name, 'sheet', sh.shape[1], 'x', sh.shape[0], f'{kb:.0f}KB', {k_: v for k_, v in run[name].items() if k_ not in ('names', 'lower')})


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
