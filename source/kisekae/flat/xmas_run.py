"""クリスマスの壁紙の馬が、サンタさんの プレゼントを 食べようとする コマ（まさちゃんの指定「クリスマス エフェクト:常に雪が降っている
   5秒から12秒、ランダムにサンタさんの持っているプレゼントを食べようとしてサンタさんが焦って逃げる💨右側へフェードアウト、
   様子を見ながら元の位置に戻る 15秒に1回リピート」）。いつ どのコマを出すか・サンタさん・雪は ../xmas_wall.py
   - 馬は いまの絵と同じ馬（horse_flat・同じ色と帽子と綱・同じカメラ）。体と 足と しっぽは 動かさない（首と頭だけ）
   - コマ（名前と順は frames()）：U0（いまの絵）・R1〜R31（首を のばしていく とちゅう）・R32（のばしきった形：鼻先が サンタさんの
     プレゼントの リボンに とどく）・B1〜B4（ぱくっ：のばしきった形から 首を 少し前へ のばして 頭を 下へ＝箱の 角を かもうとする）。
     首は 根元から まげて のばす（r3d/horse3d.py の neck_bend・neck_len）。とちゅうの コマの のばしぐあいは、頭と首の 目印の 動く道のりが
     同じ はばに なるように えらぶ（levels：コマを めくる はやさが 動きの はやさに合う＝なめらか）
   - 帽子は 頭と いっしょに かたむく（cute_themes.hat_on_head の tilt を、頭の角度の かわった ぶんだけ かえる：HAT_OVR）
   - 背景は 動く壁紙の 下の絵（flat/xmas_banner.py を XMAS_BASE=1：サンタさんと 手前の 降る雪なし。どちらも ページの SVG で動かす）。
     コマ0は その 下の絵と 同じ（1画素も ちがわない）。コマは 下の絵を描くのと同じ流れ（flat/step_run.py の frame_u8）で、馬のポーズだけ かえて描く
   - 動く所（すべての コマの ちがう所を まとめた四角）だけ 切りぬいて、よこ8コマずつ 並べた1まい（シート・ロスなし・背景ごと）にする
   python3 flat/xmas_run.py --cams <xmas_cams.json>                     → いまの馬の カメラ（3倍の絵で決める・約15秒）
   python3 flat/xmas_run.py --frames <コマのフォルダ> <xmas_cams.json> [コマの番号…]  → コマ（PNG・コマ0を先に・1コマ 約13秒）
   python3 flat/xmas_run.py --sheet <コマのフォルダ> <出力フォルダ> <xmas_run.json>   → xmas_reach.webp（シート）・xmas_run.json に 置く場所と大きさ"""
import sys, os, math, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
os.environ['XMAS_BASE'] = '1'                    # 下の絵（サンタさんと 降る雪なし）で 描く
import horse3d as Hm
from horse_flat import POSES
import step_run as SR

NAME = 'xmas'
W, Hh = 780, 320
COLS = 8
PAD = 2
BASE = 'stand'                                   # いまの絵の ポーズ（右向き）
REACH = (-48.0, 1.15, -44.0)                     # のばしきった形：首のまげ（°）・首ののばし（倍）・頭の角度（°）。鼻先が プレゼントの リボンに とどく
BITE = (-5.0, 0.03, -8.0)                        # ぱくっ（いちばん先）：のばしきった形に たす（首を 少し前へ のばして 頭を 下へ）
N_REACH = 32                                     # 首を のばす だんかい（R1〜R32。R32 が のばしきった形）
N_BITE = 4                                       # ぱくっの だんかい（B1〜B4）
HAT_TILT = -12.0                                 # いまの絵の 帽子の かたむき（cute_themes.acc_xmas の tilt）
MARK_HEAD_SCALE = 1.1                            # 目印の 頭の大きさ（step_run と同じ：描く順で かわらないように）


def frames():
    return ['U0'] + [f'R{i}' for i in range(1, N_REACH + 1)] + [f'B{i}' for i in range(1, N_BITE + 1)]


def pose_at(p, q=0.0):
    """首を のばす ぐあい p（0〜1）・ぱくっ q（0〜1）の ポーズ（horse_flat の POSES と同じ形）。p＝q＝0 は いまの絵"""
    P = POSES[BASE]
    out = {k: (list(v) if isinstance(v, list) else v) for k, v in P.items()}
    if p > 0 or q > 0:
        out['neck_bend'] = round(REACH[0] * p + BITE[0] * q, 4)
        out['neck_len'] = round(1 + (REACH[1] - 1) * p + BITE[1] * q, 5)
        out['head_ang'] = round(P['head_ang'] + (REACH[2] - P['head_ang']) * p + BITE[2] * q, 4)
    return out


def hat_tilt(pose):
    """帽子の かたむき：頭が 上を向いた ぶん（頭の角度が ふえた ぶん）だけ うしろへ"""
    return round(HAT_TILT + (pose['head_ang'] - POSES[BASE]['head_ang']), 4)


def head_marks(p):
    """のばす ぐあい p の時の 頭と首の 目印（世界の xy）：鼻先・うなじ・首の上と下の まん中"""
    S, _, _ = skel(pose_at(p))
    hs0 = Hm.HEAD_SCALE
    Hm.HEAD_SCALE = MARK_HEAD_SCALE
    try:
        pts = [Hm.head_pt(S, 0.60, -0.03), S['poll'], Hm.bez(S['crest'], np.array([0.5]))[0], Hm.bez(S['throat'], np.array([0.5]))[0]]
    finally:
        Hm.HEAD_SCALE = hs0
    return np.array([np.asarray(v, float)[:2] for v in pts])


def skel(pose):
    full = dict(theta=pose['theta'], neck_rot=pose['neck_rot'], head_ang=pose['head_ang'], tail=pose['tail'],
                fore={'L': pose['fore_near'], 'R': pose['fore_far']}, hind={'L': pose['hind_near'], 'R': pose['hind_far']})
    if pose.get('neck_bend'):
        full['neck_bend'], full['neck_len'] = pose['neck_bend'], pose['neck_len']
    return Hm.skeleton(full), 'L', 'R'


_LV = []


def levels():
    """R1〜R32 の のばしぐあい：頭と首の 目印の いちばん大きく動く所の 道のりが 同じ はばに なるように（R32＝1）。小数5けた"""
    if not _LV:
        ps = np.linspace(0, 1, 801)
        m = np.array([head_marks(p) for p in ps])
        step = np.linalg.norm(np.diff(m, axis=0), axis=2).max(1)
        d = np.concatenate([[0], np.cumsum(step)])
        lv = np.interp(np.linspace(0, d[-1], N_REACH + 1), d, ps)[1:]
        _LV.extend(round(float(v), 5) for v in lv)
        _LV[-1] = 1.0
    return list(_LV)


def bites():
    return [round(i / N_BITE, 5) for i in range(1, N_BITE + 1)]


def parse(fn):
    """コマの名前 → (のばすぐあい p, ぱくっ q)"""
    if fn == 'U0':
        return 0.0, 0.0
    if fn[0] == 'R':
        return levels()[int(fn[1:]) - 1], 0.0
    return 1.0, bites()[int(fn[1:]) - 1]


def render_frames(outdir, cams, idxs):
    """コマを描いて <outdir>/xmas_fNN.png に（NN は シートの順。コマ0を先に：影の目印を xmas_ref.json に）"""
    import cute_themes as C
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
        pose = pose_at(*parse(fns[i]))
        C.HAT_OVR.clear()
        if i != 0:
            C.HAT_OVR[NAME] = {'tilt': hat_tilt(pose)}
        try:
            u8, m = SR.frame_u8(NAME, pose, cams, ref)
        finally:
            C.HAT_OVR.clear()
        if i == 0:
            json.dump(dict(hooves=[[float(v) for v in h] for h in m['hooves']], bottom=float(m['bottom'])), open(rf, 'w'))
        SR.save_png(f'{outdir}/{NAME}_f{i:02d}.png', u8)
        print(NAME, 'frame', i, fns[i], flush=True)


NOISE_PX = 20                                    # これより 少ない画素の はなれた ちがい（3Dの 描画の 足の ふちの 1画素の ゆらぎ）は 動く所に 入れない


def main_region(d):
    """ちがう画素のうち、首と頭の まとまり（いちばん大きい かたまり）と、NOISE_PX 画素 以上の かたまりだけ のこす
       （足の ふちに 1画素ずつ 出る 描画の ゆらぎ（明るさ 50/255 まで）で 四角が 足もとまで のびないように。のこらない所は 下の絵の まま）"""
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
    """コマ → 動く所（どれかの コマで コマ0と ちがう画素を まとめた四角）を 切りぬいて よこ COLS に並べた1まい（<outdir>/xmas_reach.webp・ロスなし）。
       コマの まわりには のりしろ（PAD：絵の となりの画素）。置く場所と大きさ・のばしぐあいを run_json に書く"""
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
    Image.fromarray(sh, 'RGB').save(f'{outdir}/{NAME}_reach.webp', 'WEBP', lossless=True, quality=100, method=6)
    run = dict(frames=N, names=fns, reach=levels(), bite=bites(), cols=COLS, rows=rows, cell=[cw, ch], pad=P, at=[int(x0), int(y0)], size=[W, Hh])
    txt = json.dumps(run, ensure_ascii=False, indent=1)
    for key in ('names', 'reach', 'bite'):
        txt = txt.replace(json.dumps(run[key], ensure_ascii=False, indent=1).replace('\n', '\n '), json.dumps(run[key], ensure_ascii=False))
    open(run_json, 'w').write(txt + '\n')
    kb = os.path.getsize(f'{outdir}/{NAME}_reach.webp') / 1024
    print(NAME, 'sheet', sh.shape[1], 'x', sh.shape[0], f'{kb:.0f}KB', {k: v for k, v in run.items() if k not in ('names', 'reach', 'bite')})


def ref_cams(out_json):
    """いまの馬の カメラ（いまの絵と同じ：3倍の絵で frame_horse が決める）"""
    import cute_themes as C
    from horse_flat import draw_horse
    sp = dict(C.SPOTS[NAME])
    sp['cam_out'] = []
    draw_horse(sp, C.PALS[NAME], W, Hh, acc=C.ACC[NAME], number='1', name='xmas_ref')
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
