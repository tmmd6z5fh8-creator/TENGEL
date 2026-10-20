"""バレンタイン・ホワイトデーの壁紙の 馬の コマと 動く壁紙の 絵（まさちゃんの指定「バレンタイン、ホワイトデイ エフェクト:常にハートが動いている
   常に馬がカップルを目でおっている 1〜3秒でカップルが馬を撫でにいく 3〜5秒馬を撫でる 3秒〜5秒馬が喜んで尻尾を3回縦に振る 3秒〜5秒馬の耳が前を向く
   6秒〜9秒でカップルが元に位置に戻る 6回中1回ランダムで、カップルが馬に近く、撫でる時に馬がブチギレてカップルが吹っ飛ぶ、2人とも焦って立ち上がり
   顔をあせて元の位置に戻る」「10秒に一回リピート」）。いつ どのコマを出すか・カップル・ハートは ../couple_wall.py
   - 馬は いまの絵と同じ馬（horse_flat・同じ色と リボン・同じカメラ）。体と 足は 動かさない（首と頭・耳・しっぽだけ）
   - 絵は すき通しつき（RGBA）で 分ける：空の絵（sky：空と 床と 馬の影。バレンタインの ハート・とろける チョコ・馬・カップル・手前の物なし）・
     前の絵（front：馬（頭と しっぽの 四角を ぬいた）と、バレンタインは とろける チョコ）・頭の コマの シート（head）・しっぽの コマの シート（tail）。
     ページでは 空の絵 → ハート（バレンタイン）→ 前の絵 → コマ → カップル（SVG）の順に 重ねる（ハートは 馬と チョコの うしろ＝いまの絵と同じ）
   - 頭の コマ（名前と順は frames()）：U0（いまの絵）・L1〜L24（カップルを 見下ろしていく とちゅう。L24 が いちばん下＝なでてもらう形：
     首を 前へ のばして 下げ、鼻先を 子どもの 手の高さへ）・E1〜E4（耳が 前を向く：なでてもらって 喜ぶ）・A1〜A3（耳を うしろへ ふせて おこった まゆ：ブチギレ）・
     K1〜K4（おこって 首を つきだす）。とちゅうの コマの ぐあいは 頭と首の 目印の 動く道のりが 同じ はばに なるように えらぶ（levels）
   - しっぽの コマ：T1〜T16（しっぽを 上へ 持ちあげていく とちゅう。T16 が いちばん上 50度）。3Dの 馬は U0 と同じ（しっぽは 平らな 房）
   - コマ0（U0）と 空の絵・前の絵を 重ねると いまの絵と 同じ（ハート・カップル・手前の物は ページの SVG）
   python3 flat/couple_run.py --cams <couple_cams.json>                        → 2頭の いまの カメラ
   python3 flat/couple_run.py --frames <テーマ> <コマのフォルダ> <couple_cams.json> [コマの名前…]  → コマ（RGBA の PNG・頭の コマ 1つ 約10秒）
   python3 flat/couple_run.py --build <テーマ> <コマのフォルダ> <出力フォルダ> <couple_run.json>  → <テーマ>_sky.webp・<テーマ>_front.webp・
                                                                                 <テーマ>_head.webp・<テーマ>_tail.webp・couple_run.json（テーマごとの 置く場所）"""
import sys, os, math, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
import horse3d as Hm
import horse_flat as HF
from horse_flat import POSES, TAILS

W, Hh = 780, 320
COLS = 8
PAD = 2
N_LOOK = 24                      # 見下ろす だんかい
N_EAR, N_ANGRY, N_LUNGE = 4, 3, 4
N_TAIL = 16
TAIL_LIFT = 50.0                 # しっぽを 持ちあげる いちばん上（度）
MARK_HEAD_SCALE = 1.1
# テーマごと：いまの絵の ポーズ・いちばん 見下ろした形（look：首のまげ°・首ののばし・頭の角度°）・耳（前へ／うしろへ °）・首を つきだす形（lunge）
THEMES = {
    'valentine': dict(base='stand', look=(-46.0, 1.22, -58.0), ear_fwd=50.0, ear_back=-35.0, lunge=(-52.0, 1.30, -50.0)),
    'whiteday': dict(base='stand', look=(-46.0, 1.22, -58.0), ear_fwd=50.0, ear_back=-35.0, lunge=(-52.0, 1.30, -50.0)),
}


def head_frames():
    return (['U0'] + [f'L{i}' for i in range(1, N_LOOK + 1)] + [f'E{i}' for i in range(1, N_EAR + 1)]
            + [f'A{i}' for i in range(1, N_ANGRY + 1)] + [f'K{i}' for i in range(1, N_LUNGE + 1)])


def tail_frames():
    return [f'T{i}' for i in range(1, N_TAIL + 1)]


def pose_at(name, e=0.0, ear=0.0, brow=None, lunge=0.0, lift=0.0):
    """ポーズ（horse_flat の POSES と同じ形の dict）：e＝見下ろす ぐあい（0〜1）・ear＝耳の 向き（度）・brow＝まゆ・lunge＝首を つきだす ぐあい（0〜1・e＝1 から）・
       lift＝しっぽを 持ちあげる 角度（度）。ぜんぶ 0 なら いまの絵"""
    th = THEMES[name]
    P = POSES[th['base']]
    out = {k: (list(v) if isinstance(v, list) else v) for k, v in P.items()}
    if e > 0 or lunge > 0:
        Bd, Ld, Hd = th['look']
        if lunge > 0:
            B2, L2, H2 = th['lunge']
            Bd, Ld, Hd = Bd + (B2 - Bd) * lunge, Ld + (L2 - Ld) * lunge, Hd + (H2 - Hd) * lunge
            e = 1.0
        out['neck_bend'] = round(Bd * e, 4)
        out['neck_len'] = round(1 + (Ld - 1) * e, 5)
        out['head_ang'] = round(P['head_ang'] + (Hd - P['head_ang']) * e, 4)
    if ear:
        out['ear_rot'] = round(ear, 4)
    if brow:
        out['brow'] = brow
    if lift:
        a = math.radians(lift)
        rot = lambda q: (round(q[0] * math.cos(a) + q[1] * math.sin(a), 6), round(-q[0] * math.sin(a) + q[1] * math.cos(a), 6))
        out['tail_tufts'] = [(rot(p1), rot(p2), rot(p3), w) for p1, p2, p3, w in TAILS[P['tail_kind']]]
    return out


def skel(pose, facing):
    near, far = ('L', 'R') if facing == 'right' else ('R', 'L')
    full = dict(theta=pose['theta'], neck_rot=pose['neck_rot'], head_ang=pose['head_ang'], tail=pose['tail'],
                fore={near: pose['fore_near'], far: pose['fore_far']}, hind={near: pose['hind_near'], far: pose['hind_far']})
    if pose.get('neck_bend'):
        full['neck_bend'], full['neck_len'] = pose['neck_bend'], pose['neck_len']
    return Hm.skeleton(full)


def head_marks(name, e):
    """見下ろす ぐあい e の 頭と首の 目印（世界の xy）：鼻先・うなじ・首の上と下の まん中"""
    S = skel(pose_at(name, e), 'right')
    hs0 = Hm.HEAD_SCALE
    Hm.HEAD_SCALE = MARK_HEAD_SCALE
    try:
        pts = [Hm.head_pt(S, 0.60, -0.03), S['poll'], Hm.bez(S['crest'], np.array([0.5]))[0], Hm.bez(S['throat'], np.array([0.5]))[0]]
    finally:
        Hm.HEAD_SCALE = hs0
    return np.array([np.asarray(v, float)[:2] for v in pts])


def levels(name, n=N_LOOK, fn=None, steps=801):
    """0〜1 を 目印の いちばん大きく動く所の 道のりが 同じ はばに なるように n こに 分ける（いちばん上＝1）。小数5けた"""
    fn = fn or (lambda e: head_marks(name, e))
    es = np.linspace(0, 1, steps)
    m = np.array([fn(e) for e in es])
    step = np.linalg.norm(np.diff(m, axis=0), axis=2).max(1)
    d = np.concatenate([[0], np.cumsum(step)])
    lv = [round(float(v), 5) for v in np.interp(np.linspace(0, d[-1], n + 1), d, es)[1:]]
    lv[-1] = 1.0
    return lv


def tail_levels(name):
    """しっぽを 持ちあげる 角度（T1〜T16）：しっぽの 先が 同じ はばで 動くように（房の 先の 点を まわすだけ＝角度に 比例）"""
    return [round(TAIL_LIFT * i / N_TAIL, 4) for i in range(1, N_TAIL + 1)]


def parse(name, fn):
    """コマの名前 → pose_at の 引数"""
    th = THEMES[name]
    if fn == 'U0':
        return {}
    k, i = fn[0], int(fn[1:])
    if k == 'L':
        return dict(e=levels(name)[i - 1])
    if k == 'E':
        return dict(e=1.0, ear=th['ear_fwd'] * i / N_EAR)
    if k == 'A':
        return dict(e=1.0, ear=th['ear_back'] * i / N_ANGRY, brow='angry')
    if k == 'K':
        return dict(e=1.0, ear=th['ear_back'], brow='angry', lunge=i / N_LUNGE)
    if k == 'T':
        return dict(lift=tail_levels(name)[i - 1])
    raise KeyError(fn)


_R3D = {}


def cached_render_body():
    """3Dの 描画を おぼえておく（しっぽの コマは 3Dの 馬が 同じ：同じ ポーズと カメラなら 2回目からは 描かない）"""
    real = HF.render_body

    def rb(pose, eye, tgt, fov, W_, H_, name, tmp, throat=None):
        key = (repr(sorted(pose.items())), tuple(np.round(eye, 9)), tuple(np.round(tgt, 9)), fov, W_, H_, repr(throat))
        if key not in _R3D:
            _R3D[key] = real(pose, eye, tgt, fov, W_, H_, name, tmp, throat)
        return _R3D[key]
    HF.render_body = rb


def spec_of(name, pose, cams):
    import cute_themes as C
    sp = dict(C.SPOTS[name])
    sp['pose'] = pose
    e, t = cams[name]
    sp['cam'] = (np.asarray(e, float), np.asarray(t, float))
    return sp


def horse_rgba(name, kw, cams):
    """馬だけの 絵（1倍・すき通しつき：rgb と a）と 目印"""
    import cute_themes as C
    sp = spec_of(name, pose_at(name, **kw), cams)
    rgb, a, m = C.draw_horse(sp, C.PALS[name], W, Hh, acc=C.ACC[name], number='1', name=f'couple_{name}')
    return rgb, a, m


def to_u8(rgb, a):
    """すき通しつきの 8ビット（RGBA・まっすぐの 色）"""
    out = np.zeros((Hh, W, 4), np.uint8)
    out[..., :3] = (np.clip(rgb, 0, 1) * 255 + .5).astype(np.uint8)
    out[..., 3] = (np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return out


def render_frames(name, outdir, cams, names):
    """コマを描いて <outdir>/<テーマ>_<コマの名前>.png に（RGBA）。U0 の 目印を <テーマ>_marks.json に"""
    os.makedirs(outdir, exist_ok=True)
    cached_render_body()
    for fn in names:
        rgb, a, m = horse_rgba(name, parse(name, fn), cams)
        u8 = to_u8(rgb, a)
        save_png(f'{outdir}/{name}_{fn}.png', u8)
        if fn == 'U0':
            json.dump(dict(hooves=[[float(v) for v in h] for h in m['hooves']], bottom=float(m['bottom']), eye=[float(v) for v in m['eye']],
                           muzzle=[float(v) for v in m['muzzle']], poll=[float(v) for v in m['poll']]), open(f'{outdir}/{name}_marks.json', 'w'))
        if fn == f'L{N_LOOK}':
            json.dump(dict(eye=[float(v) for v in m['eye']], muzzle=[float(v) for v in m['muzzle']], poll=[float(v) for v in m['poll']]),
                      open(f'{outdir}/{name}_marks_look.json', 'w'))
        print(name, 'frame', fn, flush=True)


def save_png(path, u8):
    import cv2
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA))


def load_png(path):
    import cv2
    return cv2.cvtColor(cv2.imread(path, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)


EDGE = 2                         # 前の絵で のこす 四角の ふち（画素：diff_box の まわり 2画素は どのコマも コマ0と 同じ）
NOISE_PX = 20                    # これより 少ない画素の はなれた ちがい（3Dの 描画の 体や 足の 1画素の ゆらぎ）は 動く所に 入れない（flat/halloween_run.py と同じ）


def main_region(d):
    """ちがう画素のうち、いちばん大きい かたまり（首と頭・しっぽ）と、NOISE_PX 画素 以上の かたまりだけ のこす"""
    import cv2
    lab_n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(d.astype(np.uint8), np.ones((5, 5), np.uint8)), 8)
    big = 1 + int(np.argmax(st[1:, 4]))
    keep = np.zeros(d.shape, bool)
    for k in range(1, lab_n):
        part = d & (lab == k)
        if k == big or part.sum() >= NOISE_PX:
            keep |= part
    return keep


def diff_box(frs, f0):
    """コマ（RGBA）の どれかが コマ0と ちがう 画素を まとめた 四角（偶数に そろえる・まわり 2画素）"""
    d = np.zeros(f0.shape[:2], bool)
    for f in frs:
        d |= np.abs(f.astype(np.int16) - f0.astype(np.int16)).max(2) > 0
    ys, xs = np.nonzero(main_region(d))
    x0, x1 = max(0, xs.min() - 2), min(W, xs.max() + 3)
    y0, y1 = max(0, ys.min() - 2), min(Hh, ys.max() + 3)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2
    x1, y1 = x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2
    return int(x0), int(y0), int(min(W, x1)), int(min(Hh, y1))


def make_sheet(frs, box, out):
    """コマ → 四角 box を 切りぬいて よこ COLS に 並べた 1まい（RGBA・ロスなし）。のりしろ PAD は となりの 画素"""
    from PIL import Image
    x0, y0, x1, y1 = box
    cw, ch = x1 - x0, y1 - y0
    rows = math.ceil(len(frs) / COLS)
    P = PAD
    sh = np.zeros((rows * (ch + 2 * P), COLS * (cw + 2 * P), 4), np.uint8)
    for i, f in enumerate(frs):
        r, c = divmod(i, COLS)
        fp = np.pad(f, ((P, P), (P, P), (0, 0)), mode='edge')
        sh[r * (ch + 2 * P):(r + 1) * (ch + 2 * P), c * (cw + 2 * P):(c + 1) * (cw + 2 * P)] = fp[y0:y1 + 2 * P, x0:x1 + 2 * P]
    Image.fromarray(sh, 'RGBA').save(out, 'WEBP', lossless=True, quality=100, method=6)
    return dict(cols=COLS, rows=rows, cell=[cw, ch], pad=P, at=[x0, y0], frames=len(frs))


def sky_image(name, marks):
    """空の絵：いまの絵の 流れ（flat/<テーマ>_banner.py を EVENT_SKY=1・CUTE_NO_HORSE=1）に 馬の 影を たす（0〜1 の RGB）"""
    import style2d
    import cute_themes as C
    script = os.path.join(HERE, f'{name}_banner.py')
    got = {}
    env0 = {k: os.environ.get(k) for k in ('EVENT_SKY', 'CUTE_NO_HORSE')}
    save0, argv0 = style2d.save_webp, sys.argv
    os.environ['EVENT_SKY'], os.environ['CUTE_NO_HORSE'] = '1', '1'
    style2d.save_webp = lambda img, path, q=88: got.setdefault('img', img)
    sys.argv = [script, os.devnull]
    try:
        try:
            exec(compile(open(script, encoding='utf-8').read(), script, 'exec'), {'__name__': '__main__', '__file__': script})
        except SystemExit:
            pass
    finally:
        style2d.save_webp, sys.argv = save0, argv0
        for k, v in env0.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    ms = dict(hooves=[np.asarray(h, float) for h in marks['hooves']], bottom=marks['bottom'])
    return C.horse_shadow(got['img'], name, W, Hh, C.SPOTS[name], ms)


def drip_rgba():
    """バレンタインの とろける チョコ（いまの絵と 同じ 形：乱数の 種 14・空の ハートの あと）。(rgb, a)"""
    import event_art as A
    from cute_horse import svg_layer
    rng = np.random.default_rng(14)
    A.sky_hearts(rng, W)
    return svg_layer(A.choco_drip_svg(A.choco_drip(rng)), W, Hh)


def build(name, frdir, outdir, run_json):
    """シート（頭・しっぽ）・前の絵・空の絵を 作って、置く場所を run_json の テーマの 所に 書く"""
    from PIL import Image
    import style2d
    os.makedirs(outdir, exist_ok=True)
    f0 = load_png(f'{frdir}/{name}_U0.png')
    heads = [load_png(f'{frdir}/{name}_{fn}.png') for fn in head_frames()]
    tails = [f0] + [load_png(f'{frdir}/{name}_{fn}.png') for fn in tail_frames()]
    hb, tb = diff_box(heads[1:], f0), diff_box(tails[1:], f0)
    assert hb[2] <= tb[0] or tb[2] <= hb[0] or hb[3] <= tb[1] or tb[3] <= hb[1], ('頭と しっぽの 四角が かさなる', hb, tb)
    run = dict(head=make_sheet(heads, hb, f'{outdir}/{name}_head.webp'), tail=make_sheet(tails, tb, f'{outdir}/{name}_tail.webp'))
    run['head']['names'] = head_frames()
    run['tail']['names'] = ['U0'] + tail_frames()
    # 前の絵：馬（頭と しっぽの 四角は ぬく。ふちの EDGE 画素は のこす：四角の さかいめで 前の絵と コマが どちらも すき通って 細い線が 出ない。
    # ふちは どのコマも コマ0と 同じなので 重なっても 同じ絵）と、バレンタインは とろける チョコ（馬の うしろ）
    hor = f0.astype(np.float32) / 255
    for x0, y0, x1, y1 in (hb, tb):
        hor[y0 + EDGE:y1 - EDGE, x0 + EDGE:x1 - EDGE] = 0
    ah = hor[..., 3]
    if name == 'valentine':
        drgb, da = drip_rgba()
    else:
        drgb, da = np.zeros((Hh, W, 3), np.float32), np.zeros((Hh, W), np.float32)
    a = ah + da * (1 - ah)
    rgb = (hor[..., :3] * ah[..., None] + drgb * (da * (1 - ah))[..., None]) / np.maximum(a, 1e-6)[..., None]
    Image.fromarray(to_u8(rgb, a), 'RGBA').save(f'{outdir}/{name}_front.webp', 'WEBP', lossless=True, quality=100, method=6)
    marks = json.load(open(f'{frdir}/{name}_marks.json'))
    sky = sky_image(name, marks)
    style2d.save_webp(sky, f'{outdir}/{name}_sky.webp')
    look = json.load(open(f'{frdir}/{name}_marks_look.json'))
    run.update(look=levels(name), tail_lift=tail_levels(name), eye=[round(v, 2) for v in marks['eye']], muzzle=[round(v, 2) for v in marks['muzzle']],
               eye_look=[round(v, 2) for v in look['eye']], muzzle_look=[round(v, 2) for v in look['muzzle']], size=[W, Hh])
    allrun = json.load(open(run_json)) if os.path.exists(run_json) else {}
    allrun[name] = run
    txt = json.dumps(allrun, ensure_ascii=False, indent=1)
    for t in allrun.values():
        for key in ('look', 'tail_lift', 'eye', 'muzzle', 'eye_look', 'muzzle_look', 'size'):
            txt = txt.replace(json.dumps(t[key], ensure_ascii=False, indent=1).replace('\n', '\n  '), json.dumps(t[key], ensure_ascii=False))
        for part in ('head', 'tail'):
            for key in ('names', 'cell', 'at'):
                txt = txt.replace(json.dumps(t[part][key], ensure_ascii=False, indent=1).replace('\n', '\n   '), json.dumps(t[part][key], ensure_ascii=False))
    open(run_json, 'w').write(txt + '\n')
    for k in ('head', 'tail', 'front', 'sky'):
        print(name, k, f'{os.path.getsize(f"{outdir}/{name}_{k}.webp") / 1024:.0f}KB', run.get(k, {}).get('cell', ''), run.get(k, {}).get('at', ''))


def ref_cams(out_json):
    """2頭の いまの カメラ（いまの絵と同じ：3倍の絵で frame_horse が決める）"""
    import cute_themes as C
    out = {}
    for name in THEMES:
        sp = dict(C.SPOTS[name])
        sp['cam_out'] = []
        C.draw_horse(sp, C.PALS[name], W, Hh, acc=C.ACC[name], number='1', name=f'{name}_ref')
        e, t = sp['cam_out']
        out[name] = [[float(v) for v in e], [float(v) for v in t]]
    json.dump(out, open(out_json, 'w'), indent=1)


if __name__ == '__main__':
    if sys.argv[1] == '--cams':
        ref_cams(sys.argv[2])
    elif sys.argv[1] == '--frames':
        name, outdir, cams = sys.argv[2], sys.argv[3], json.load(open(sys.argv[4]))
        render_frames(name, outdir, cams, sys.argv[5:] or head_frames() + tail_frames())
    elif sys.argv[1] == '--build':
        name = sys.argv[2]
        build(name, sys.argv[3], sys.argv[4], sys.argv[5])
