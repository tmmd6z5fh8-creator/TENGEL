"""ハロウィンの壁紙の馬が、ドラキュラを 顔と首で 目で追う コマ（まさちゃんの指定「ハロウィン エフェクト:ドラキュラが羽をパタパタさせて
   少しだけ飛ぶ(2.7秒)、その後上手く飛べなくて落ちてしまう。落ちたらガイコツとかぼちゃが笑う(2秒) 馬は常にドラキュラの動きを顔と首の動きで
   追っている。 5回に1回ランダムで、ドラキュラちゃんと上に飛べて画面からフェードアウト、2秒後に落ちてきてガイコツとかぼちゃが笑う。
   8秒〜11秒に一回リピート」）。いつ どのコマを出すか・ドラキュラ・かぼちゃ・ドクロは ../halloween_wall.py
   - 馬は いまの絵と同じ馬（horse_flat・同じ色と 魔女の帽子・同じカメラ・左向き＝ドラキュラの方）。体と 足と しっぽは 動かさない（首と頭だけ）
   - コマ（名前と順は frames()）：U0（いまの絵）・L1〜L32（見上げていく とちゅう。L32 が いちばん上＝ドラキュラが 画面の上へ 消える所を 見る形）。
     見上げる ぐあい e（0〜1）で 首を 起こして（neck_rot）頭を 上へ むける（head_ang）。とちゅうの コマの ぐあいは、頭と首と 帽子の 目印の
     動く道のりが 同じ はばに なるように えらぶ（levels：コマを めくる はやさが 動きの はやさに合う＝なめらか）
   - 魔女の帽子（cute_themes.hat_on_head）は 世界の かたむき（tilt）で 置くので、頭と いっしょに うしろへ かたむける（HAT_OVR の tilt を コマごとに）
   - 背景は 動く壁紙の 下の絵（flat/halloween_banner.py を HALLOWEEN_BASE=1：ドラキュラ・顔のある かぼちゃ・ドクロなし）。
     コマ0は その 下の絵と 同じ（1画素も ちがわない）。コマは 下の絵を描くのと同じ流れ（flat/step_run.py の frame_u8）で、馬のポーズだけ かえて描く
   - 動く所（すべての コマの ちがう所を まとめた四角）だけ 切りぬいて、よこ8コマずつ 並べた1まい（シート・ロスなし・背景ごと）にする
   python3 flat/halloween_run.py --cams <halloween_cams.json>                      → いまの馬の カメラ（3倍の絵で決める・約15秒）
   python3 flat/halloween_run.py --frames <コマのフォルダ> <halloween_cams.json> [コマの番号…]  → コマ（PNG・コマ0を先に・1コマ 約15秒）
   python3 flat/halloween_run.py --sheet <コマのフォルダ> <出力フォルダ> <halloween_run.json>    → halloween_look.webp（シート）・halloween_run.json"""
import sys, os, math, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
os.environ['HALLOWEEN_BASE'] = '1'               # 下の絵（ドラキュラ・顔のある かぼちゃ・ドクロなし）で 描く
import horse3d as Hm
from horse_flat import POSES
import step_run as SR

NAME = 'halloween'
W, Hh = 780, 320
COLS = 8
PAD = 2
BASE = 'stand'                                   # いまの絵の ポーズ（左向き）
LOOK = (20.0, 52.0)                              # いちばん 見上げた形：首を 起こす（neck_rot に たす・°）・頭を 上へ（head_ang に たす・°）
HAT_TILT = -12.0                                 # いまの絵の 魔女の帽子の かたむき（cute_themes.acc_halloween）。頭と いっしょに うしろへ
N_LOOK = 32                                      # 見上げる だんかい（L1〜L32。L32 が いちばん上）
MARK_HEAD_SCALE = 1.1                            # 目印の 頭の大きさ（step_run と同じ：描く順で かわらないように）


def frames():
    return ['U0'] + [f'L{i}' for i in range(1, N_LOOK + 1)]


def pose_at(e):
    """見上げる ぐあい e（0〜1）の ポーズ（horse_flat の POSES と同じ形）。e＝0 は いまの絵"""
    P = POSES[BASE]
    out = {k: (list(v) if isinstance(v, list) else v) for k, v in P.items()}
    if e > 0:
        out['neck_rot'] = round(P['neck_rot'] + LOOK[0] * e, 4)
        out['head_ang'] = round(P['head_ang'] + LOOK[1] * e, 4)
    return out


def hat_tilt(e):
    """見上げる ぐあい e の 帽子の かたむき（頭と同じだけ うしろへ）"""
    return round(HAT_TILT + LOOK[1] * e, 4)


def skel(pose):
    full = dict(theta=pose['theta'], neck_rot=pose['neck_rot'], head_ang=pose['head_ang'], tail=pose['tail'],
                fore={'L': pose['fore_near'], 'R': pose['fore_far']}, hind={'L': pose['hind_near'], 'R': pose['hind_far']})
    return Hm.skeleton(full)


def head_marks(e):
    """見上げる ぐあい e の時の 頭と首と 帽子の 目印（世界の xy・右向きの 馬の 座標）：鼻先・うなじ・首の上と下の まん中・帽子の先"""
    S = skel(pose_at(e))
    hs0 = Hm.HEAD_SCALE
    Hm.HEAD_SCALE = MARK_HEAD_SCALE
    try:
        nose = Hm.head_pt(S, 0.60, -0.03)
        top = Hm.head_pt(S, 0.04, 0.07)                                     # 帽子の つけね（うなじと 前髪の あいだ）
    finally:
        Hm.HEAD_SCALE = hs0
    t = math.radians(hat_tilt(e))
    up = np.array([-math.sin(t), math.cos(t)])                              # 帽子の 上（右向きの 世界：前＝+x。tilt＞0 は うしろへ）
    pts = [nose, S['poll'], Hm.bez(S['crest'], np.array([0.5]))[0], Hm.bez(S['throat'], np.array([0.5]))[0], np.asarray(top, float)[:2] + up * 0.62]
    return np.array([np.asarray(v, float)[:2] for v in pts])


_LV = []


def levels():
    """L1〜L32 の 見上げる ぐあい：目印の いちばん大きく動く所の 道のりが 同じ はばに なるように（L32＝1）。小数5けた"""
    if not _LV:
        es = np.linspace(0, 1, 801)
        m = np.array([head_marks(e) for e in es])
        step = np.linalg.norm(np.diff(m, axis=0), axis=2).max(1)
        d = np.concatenate([[0], np.cumsum(step)])
        lv = np.interp(np.linspace(0, d[-1], N_LOOK + 1), d, es)[1:]
        _LV.extend(round(float(v), 5) for v in lv)
        _LV[-1] = 1.0
    return list(_LV)


def parse(fn):
    """コマの名前 → 見上げる ぐあい e"""
    return 0.0 if fn == 'U0' else levels()[int(fn[1:]) - 1]


def frame(e, cams, ref=None):
    """見上げる ぐあい e の コマ（u8 の 絵ぜんぶ・馬の目印）。帽子の かたむきを 頭に 合わせる"""
    import cute_themes as C
    old = C.HAT_OVR.get(NAME)
    if e > 0:
        C.HAT_OVR[NAME] = dict(old or {}, tilt=hat_tilt(e))
    try:
        return SR.frame_u8(NAME, pose_at(e), cams, ref)
    finally:
        if old is None:
            C.HAT_OVR.pop(NAME, None)
        else:
            C.HAT_OVR[NAME] = old


def render_frames(outdir, cams, idxs):
    """コマを描いて <outdir>/halloween_fNN.png に（NN は シートの順。コマ0を先に：影の目印を halloween_ref.json に）"""
    fns = frames()
    os.makedirs(outdir, exist_ok=True)
    rf = f'{outdir}/{NAME}_ref.json'
    for i in idxs:
        if i != 0 and not os.path.exists(rf):
            raise SystemExit('コマ0を先に描く（影の目印）')
        ref = None
        if i != 0:
            r = json.load(open(rf))
            ref = dict(hooves=[np.asarray(h, float) for h in r['hooves']], bottom=r['bottom'])
        u8, m = frame(parse(fns[i]), cams, ref)
        if i == 0:
            json.dump(dict(hooves=[[float(v) for v in h] for h in m['hooves']], bottom=float(m['bottom']),
                           eye=[float(v) for v in m['eye']]), open(rf, 'w'))
        SR.save_png(f'{outdir}/{NAME}_f{i:02d}.png', u8)
        print(NAME, 'frame', i, fns[i], flush=True)


NOISE_PX = 20                                    # これより 少ない画素の はなれた ちがい（3Dの 描画の 足の ふちの 1画素の ゆらぎ）は 動く所に 入れない


def main_region(d):
    """ちがう画素のうち、首と頭の まとまり（いちばん大きい かたまり）と、NOISE_PX 画素 以上の かたまりだけ のこす（flat/xmas_run.py と同じ）"""
    import cv2
    lab_n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(d.astype(np.uint8), np.ones((5, 5), np.uint8)), 8)
    big = 1 + int(np.argmax(st[1:, 4]))
    keep = np.zeros(d.shape, bool)
    for k in range(1, lab_n):
        part = d & (lab == k)
        if k == big or part.sum() >= NOISE_PX:
            keep |= part
    return keep


def make_sheet(frdir, outdir, run_json):
    """コマ → 動く所（どれかの コマで コマ0と ちがう画素を まとめた四角）を 切りぬいて よこ COLS に並べた1まい（<outdir>/halloween_look.webp・ロスなし）。
       コマの まわりには のりしろ（PAD：絵の となりの画素）。置く場所と大きさ・見上げる ぐあい・馬の目（いまの絵）・頭の まわる 角度（turn）を run_json に書く"""
    from PIL import Image
    fns = frames()
    N = len(fns)
    fr = [SR.load_png(f'{frdir}/{NAME}_f{i:02d}.png') for i in range(N)]
    f0 = fr[0].astype(np.int16)
    d = np.zeros(f0.shape[:2], bool)
    for f in fr[1:]:
        d |= np.abs(f.astype(np.int16) - f0).max(2) > 0
    d = main_region(d)
    ys, xs = np.nonzero(d)
    pad = 2
    x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + 1 + pad)
    y0, y1 = max(0, ys.min() - pad), min(Hh, ys.max() + 1 + pad)
    x0, y0, x1, y1 = SR.calm_edges(fr[0], x0, y0, x1, y1)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2                  # 画面の画素（半分）に そろえる
    x1, y1 = x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2
    cw, ch = int(x1 - x0), int(y1 - y0)
    rows = math.ceil(N / COLS)
    P = PAD
    cw2, ch2 = cw + 2 * P, ch + 2 * P
    sh = np.zeros((rows * ch2, COLS * cw2, fr[0].shape[2]), np.uint8)
    for i, f in enumerate(fr):
        r, c = divmod(i, COLS)
        fp = np.pad(f, ((P, P), (P, P), (0, 0)), mode='edge')
        sh[r * ch2:(r + 1) * ch2, c * cw2:(c + 1) * cw2] = fp[y0:y1 + 2 * P, x0:x1 + 2 * P]
    os.makedirs(outdir, exist_ok=True)
    Image.fromarray(sh, 'RGB').save(f'{outdir}/{NAME}_look.webp', 'WEBP', lossless=True, quality=100, method=6)
    eye = json.load(open(f'{frdir}/{NAME}_ref.json'))['eye']
    run = dict(frames=N, names=fns, look=levels(), eye=[round(v, 2) for v in eye], turn=LOOK[1], cols=COLS, rows=rows, cell=[cw, ch], pad=P, at=[int(x0), int(y0)], size=[W, Hh])
    txt = json.dumps(run, ensure_ascii=False, indent=1)
    for key in ('names', 'look', 'eye'):
        txt = txt.replace(json.dumps(run[key], ensure_ascii=False, indent=1).replace('\n', '\n '), json.dumps(run[key], ensure_ascii=False))
    open(run_json, 'w').write(txt + '\n')
    kb = os.path.getsize(f'{outdir}/{NAME}_look.webp') / 1024
    print(NAME, 'sheet', sh.shape[1], 'x', sh.shape[0], f'{kb:.0f}KB', {k: v for k, v in run.items() if k not in ('names', 'look')})


def ref_cams(out_json):
    """いまの馬の カメラ（いまの絵と同じ：3倍の絵で frame_horse が決める）"""
    import cute_themes as C
    from horse_flat import draw_horse
    sp = dict(C.SPOTS[NAME])
    sp['cam_out'] = []
    draw_horse(sp, C.PALS[NAME], W, Hh, acc=C.ACC[NAME], number='1', name='halloween_ref')
    e, t = sp['cam_out']
    json.dump({NAME: [[float(v) for v in e], [float(v) for v in t]]}, open(out_json, 'w'), indent=1)


if __name__ == '__main__':
    if sys.argv[1] == '--cams':
        ref_cams(sys.argv[2])
    elif sys.argv[1] == '--frames':
        outdir, cams = sys.argv[2], json.load(open(sys.argv[3]))
        idxs = [int(v) for v in sys.argv[4:]] or list(range(len(frames())))
        render_frames(outdir, cams, idxs)
    elif sys.argv[1] == '--sheet':
        make_sheet(sys.argv[2], sys.argv[3], sys.argv[4])
