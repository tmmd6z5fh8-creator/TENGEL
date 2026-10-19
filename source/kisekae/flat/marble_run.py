"""大理石の壁紙の動き（まさちゃんの指定「1〜2でゆっくり向きを逆向きへ振り向き（馬の首で逆方向を２度見、3秒で一気に逆向きへ振り向く、
   8秒に一度リピートで繰り返す」「一気に振り向くのは2秒くらいかけて」「9秒〜17秒の中で、ランダムでヒヒィーン（文字はなし）って
   首と前脚動かす・現実の馬っぽく」「または9秒くらいかけて、後ろ脚の大理石を ずっ！ずっ！…って画面からフェードアウト（右を向いている時限定）・
   画面右から左へ同じ手順で戻って」）：動く絵
   - いまの絵（flat/marble_banner.py）と同じ場面・同じカメラ・同じ光・同じ乱数で、像の馬を 3D のまま動かして描く：
       ふり向き（look）… 首と頭を、首の根元を通る たての軸のまわりに うしろへ まわす（頭は ぜんぶ・首は 根元から うなじへ だんだん：
                          marble_horse.Look）。左向きの像は こちら（カメラ）がわを通って 右へ（＋）、右向きの像は 左へ（−）
       くるっと（psi）… 像（馬と岩）を 台のまん中の たての軸のまわりに まわす（marble_horse.Spin）。左向き psi=0 → 右向き psi=PSI_R
                          （上から見て 16°こちらを向いた像が、こちらを向きながら回って、右向きで 16°こちらを向く）。
                          頭は先に うしろを見ているので、体が回るあいだ 頭の向きは ほとんど そのまま（look を psi と反対に もどす）
       ヒヒィーン（NEIGH_KEYS）… 後ろ足は そのまま、体を少し起こして 首を上げ 頭をふり上げ、前足を 交互に 前へ 打ち出して（かく）、
                          頭を少し ふって、もとの形へ。骨組みの角度（theta・neck_rot・head_ang・前足）を なめらかに つないで NEIGH_FPS コマ/秒
   - コマ（frame_list）：A＝左向きの ふり向き（look 0 → LOOK・2度見の LOOK_OVER）／B＝左 → 右（体が回る N_TURN−1 コマ）／
                         C＝右向きの ふり向き（look 0 → −LOOK・−LOOK_OVER）／D＝右 → 左／NL・NR＝左向き・右向きの ヒヒィーン。A00 は いまの絵と 1画素もちがわない
   - 像と台のまわりだけ 背景ごと切りぬいた コマ（すき通しなし）を シート（SHEETS ごとに1まい・よこ COLS）に（ロスあり）。ページで コマを めくる（kisekae/marble_wall.py）
   - ずっ！ずっ！で動く時：像と台と 台の影だけの絵（すき通しつき）を 右向き（spR）・左向き（spL）の2まい と、像も台も影もない 背景だけの絵（plate）。
     ページで 背景の上を 絵ごと すべらせる
   python3 flat/marble_run.py <出力フォルダ>  → marble_<シート>.webp・marble_spR.webp・marble_spL.webp・marble_plate.webp・marble_run.json
   （sdfr がいる・1コマ 約15秒。描いたコマは <出力フォルダ>/cache に のこして 2回目は描かない）"""
import sys, os, json, math
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import marble_banner as MB
import marble_horse as MH

LOOK, LOOK_OVER, PSI_R = 150.0, 160.0, 148.0    # ふり向く角度・2度見で 少し行きすぎる角度・右向きの psi
N_LOOK, N_TURN = 12, 30                          # ふり向き（0 → LOOK）・体が回る（2秒で 15コマ/秒）の きざみ
NEIGH_S, NEIGH_FPS = 2.6, 15                     # ヒヒィーンの秒・コマ/秒
_TUCK, _STRIKE = [-30, 60, -40, -85], [-75, -30, -60, -75]       # 前足：高く たたむ／前へ 打ち出す（大腕・前腕・管・つなぎ の角度）
NEIGH_KEYS = (                                   # (秒, theta, neck_rot, head_ang, 右の前足, 左の前足, 頭をふる look)：右の前足＝こちらがわ（左向きの時）
    (0.00, 44.0, -26.0, -50.0, [-62, 10, -98, -130], [-48, 38, -62, -100], 0.0),       # いまの形
    (0.30, 43.0, -30.0, -58.0, [-55, 25, -90, -120], [-45, 45, -55, -95], 0.0),        # ためる（首を少し引いて 前足を たたむ）
    (0.75, 50.0, -8.0, -12.0, _STRIKE, _TUCK, 0.0),                                     # 体を起こして 首を上げ 頭をふり上げる・右を打ち出す
    (1.07, 50.5, -6.0, -8.0, _TUCK, _STRIKE, 6.0),                                      # いちばん高く（いななく）・左を打ち出す
    (1.40, 50.0, -7.0, -10.0, _STRIKE, _TUCK, -10.0),                                   # 頭を ふる
    (1.72, 49.0, -9.0, -14.0, _TUCK, _STRIKE, 8.0),
    (2.10, 46.0, -20.0, -40.0, [-55, 25, -90, -120], [-45, 45, -60, -98], 0.0),        # おりてくる
    (2.60, 44.0, -26.0, -50.0, [-62, 10, -98, -130], [-48, 38, -62, -100], 0.0),       # いまの形
)
RX1 = 600                                        # 描く範囲の右のはし（左は 0 から：いまの絵と同じ乱数になるように 行の はじめから描く）
COLS = 10                                        # シートの よこの コマ数
MARGIN = 6                                       # 切りぬきの よゆう（画素）
Q = 90                                           # シートの ロスありの質
SP_HALF = 280                                    # すべる絵の はば（台のまん中から 左右へ：台の影が とどく所まで）


def _cat(p0, p1, p2, p3, u):
    """なめらかな つなぎ（Catmull-Rom）"""
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


def neigh_pose(t):
    """ヒヒィーンの 時刻 t（秒）の 骨組み（pose）と 頭をふる角度（look）"""
    K = NEIGH_KEYS
    vec = [np.array([k[1], k[2], k[3]] + list(k[4]) + list(k[5]) + [k[6]], float) for k in K]
    ts = [k[0] for k in K]
    t = min(max(t, 0.0), ts[-1])
    i = max(j for j in range(len(ts) - 1) if ts[j] <= t)
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    v = _cat(vec[max(i - 1, 0)], vec[i], vec[i + 1], vec[min(i + 2, len(K) - 1)], u)
    pose = dict(MH.POSE)
    pose.update(theta=float(v[0]), neck_rot=float(v[1]), head_ang=float(v[2]))
    pose['fore'] = dict(R=[float(x) for x in v[3:7]], L=[float(x) for x in v[7:11]])
    return pose, float(v[11])


def frame_list():
    """{シート: [(名前, psi, look, ヒヒィーンの時刻 or None)]}：シートごとの コマ"""
    nk = int(round(NEIGH_S * NEIGH_FPS))
    look = [(f'A{k:02d}', 0.0, LOOK * k / N_LOOK, None) for k in range(N_LOOK + 1)] + [(f'A{N_LOOK + 1:02d}', 0.0, LOOK_OVER, None)]
    look += [(f'C{k:02d}', PSI_R, -LOOK * k / N_LOOK, None) for k in range(N_LOOK + 1)] + [(f'C{N_LOOK + 1:02d}', PSI_R, -LOOK_OVER, None)]
    return dict(look=look,
                turnB=[(f'B{k:02d}', PSI_R * k / N_TURN, LOOK * (1 - k / N_TURN), None) for k in range(1, N_TURN)],
                turnD=[(f'D{k:02d}', PSI_R * (1 - k / N_TURN), -LOOK * (1 - k / N_TURN), None) for k in range(1, N_TURN)],
                neighL=[(f'NL{k:02d}', 0.0, 0.0, k / NEIGH_FPS) for k in range(1, nk)],
                neighR=[(f'NR{k:02d}', PSI_R, 0.0, k / NEIGH_FPS) for k in range(1, nk)])


def _state(psi, look, tn):
    pose = None
    if tn is not None:
        pose, shake = neigh_pose(tn)
        look = look + (shake if psi == 0 else -shake)
    return pose, look


def render_frames(cache, names=None):
    """コマを描いて cache に（<名前>.png：絵の 0〜RX1・ロスなし／<名前>.json：形の決まりと 像と台の はんい）。同じ決まりで もう あるコマは描かない"""
    todo = []
    for fl in frame_list().values():
        for name, psi, look, tn in fl:
            if names is not None and name not in names:
                continue
            key = dict(psi=round(psi, 6), look=round(look, 6), neigh=None if tn is None else round(tn, 6))
            jf = os.path.join(cache, name + '.json')
            if os.path.exists(os.path.join(cache, name + '.png')) and os.path.exists(jf):
                old = json.load(open(jf))
                if all(old.get(k) == v for k, v in key.items()):
                    continue
            todo.append((name, psi, look, tn, key))
    if not todo:
        return
    cam = MB.camera()
    bg = MB.background()
    try:
        for name, psi, look, tn, key in todo:
            pose, lk = _state(psi, look, tn)
            sc = MB.scene(cam, ss=2, rect=(0, 0, RX1, MB.Hh), psi=psi, look=lk, pose=pose)
            R = MB.render(sc, f'run{os.getpid()}')
            img = MB.compose(bg.copy(), R, sc, cam)
            u8 = (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)[:, :RX1]
            ys, xs = np.nonzero(R['a'][:, :RX1] > 0)
            cv2.imwrite(os.path.join(cache, name + '.png'), cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))
            json.dump(dict(key, box=[int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]), open(os.path.join(cache, name + '.json'), 'w'))
            print(name, round(psi, 2), round(lk, 2), tn, flush=True)
    finally:
        MB.cleanup()


def render_sprites(out_dir, cache):
    """ずっ！ずっ！で動く絵：右向き（spR）・左向き（spL）の 像と台と 台の影（すき通しつき・まっすぐな α）と、背景だけの絵（plate）"""
    cam = None
    meta = {}
    try:
        for name, psi in (('spR', PSI_R), ('spL', 0.0)):
            npz = os.path.join(cache, name + '.npz')
            if not os.path.exists(npz):
                cam = cam or MB.camera()
                sc = MB.scene(cam, ss=2, rect=(0, 0, RX1, MB.Hh), psi=psi)
                R = MB.render(sc, f'sp{os.getpid()}')
                e, t, PX, gy = cam
                cx = sc.project(np.array([[PX, gy, 0.0]]))[0][0][0]
                yb = int(np.nonzero(R['a'].sum(1) > 0)[0].max())
                np.savez_compressed(npz, rgb=R['rgb'], a=R['a'], cx=cx, yb=yb)
    finally:
        if cam:
            MB.cleanup()
    for name, psi in (('spR', PSI_R), ('spL', 0.0)):
        npz = os.path.join(cache, name + '.npz')
        d = np.load(npz)
        rgb = MB.to_srgb(MB.aces(d['rgb'] / np.maximum(d['a'], 1e-4)[..., None] * 1.05))
        A = d['a']
        cx, yb = float(d['cx']), int(d['yb'])
        sh = 0.25 * np.exp(-(((MB.xx - round(cx)) / 140) ** 2 + ((MB.yy - yb) / 8) ** 2))      # 台の影（compose と同じ）
        alpha = A + sh * (1 - A)
        col = rgb * (A / np.maximum(alpha, 1e-6))[..., None]                            # 影は黒（まっすぐな α）
        x0, x1 = int(round(cx)) - SP_HALF, int(round(cx)) + SP_HALF
        x0, x1 = x0 - x0 % 2, x1 + x1 % 2
        rgba = np.dstack([np.clip(col, 0, 1), np.clip(alpha, 0, 1)])[:, x0:x1]
        u8 = (rgba * 255 + .5).astype(np.uint8)
        Image.fromarray(u8, 'RGBA').save(os.path.join(out_dir, f'marble_{name}.webp'), 'WEBP', lossless=True, method=6)   # ロスなし（止まった所で コマと同じ絵）
        xs = np.nonzero(A[yb - 3] > 0.5)[0]                                            # 台の下のはしの 左右（粉を出す所）
        meta[name] = dict(box=[x0, 0, x1, MB.Hh], foot=[round(cx, 2), yb], base=[int(xs.min()), int(xs.max()) + 1])
    return meta


def render_plate(out_dir, crop, foot):
    """背景だけの絵（plate）：像と台（コマの切りぬき crop）と 台の影の所だけ（ほかは すき通し＝いまの絵が そのまま見える）・ロスなし → 置く場所"""
    plate = MB.background()
    plate = MB.laurel(plate, 160, 170, 120, math.radians(110), math.radians(250), 1)
    plate = MB.laurel(plate, 620, 170, 120, math.radians(110), math.radians(250), -1)
    u8 = (np.clip(plate, 0, 1) * 255 + .5).astype(np.uint8)
    sh = 0.25 * np.exp(-(((MB.xx - round(foot[0])) / 140) ** 2 + ((MB.yy - foot[1]) / 8) ** 2))
    mask = sh > 0.5 / 255
    x0, y0, x1, y1 = crop
    mask[y0:y1, x0:x1] = True
    ys, xs = np.nonzero(mask)
    bx0, by0 = int(xs.min()) - int(xs.min()) % 2, int(ys.min()) - int(ys.min()) % 2
    bx1, by1 = int(xs.max()) + 1, int(ys.max()) + 1
    bx1, by1 = bx1 + bx1 % 2, by1 + by1 % 2
    rgba = np.dstack([u8, (mask * 255).astype(np.uint8)])[by0:by1, bx0:bx1]
    Image.fromarray(rgba, 'RGBA').save(os.path.join(out_dir, 'marble_plate.webp'), 'WEBP', lossless=True, method=6)
    return [bx0, by0, bx1, by1]


def build_sheets(out_dir, cache, sprites):
    fls = frame_list()
    boxes = [json.load(open(os.path.join(cache, n + '.json')))['box'] for fl in fls.values() for n, _, _, _ in fl]
    x0 = min(b[0] for b in boxes) - MARGIN
    y0 = max(0, min(b[1] for b in boxes) - MARGIN)
    x1 = max(b[2] for b in boxes) + MARGIN
    y1 = min(MB.Hh, max(b[3] for b in boxes) + MARGIN)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2                            # 2倍の絵 → ページの画素が 整数になるように
    x1, y1 = x1 + x1 % 2, y1 + y1 % 2
    assert x1 <= RX1, (x1, RX1)
    fw, fh = x1 - x0, y1 - y0
    sheets = {}
    for sname, fl in fls.items():
        rows = (len(fl) + COLS - 1) // COLS
        sheet = np.zeros((rows * fh, COLS * fw, 3), np.uint8)
        for i, (n, _, _, _) in enumerate(fl):
            im = cv2.imread(os.path.join(cache, n + '.png'))
            r, c = divmod(i, COLS)
            sheet[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw] = im[y0:y1, x0:x1]
        cv2.imwrite(os.path.join(out_dir, f'marble_{sname}.webp'), sheet, [cv2.IMWRITE_WEBP_QUALITY, Q])
        sheets[sname] = dict(cols=COLS, rows=rows, frames=[n for n, _, _, _ in fl])
    plate = render_plate(out_dir, [x0, y0, x1, y1], sprites['spR']['foot'])
    meta = dict(size=[MB.W, MB.Hh], crop=[x0, y0, x1, y1], frame=[fw, fh], sheets=sheets, sprites=sprites, plate=plate,
                LOOK=LOOK, LOOK_OVER=LOOK_OVER, PSI_R=PSI_R, N_LOOK=N_LOOK, N_TURN=N_TURN, NEIGH_S=NEIGH_S, NEIGH_FPS=NEIGH_FPS)
    json.dump(meta, open(os.path.join(out_dir, 'marble_run.json'), 'w'), ensure_ascii=False, indent=1)
    return meta


if __name__ == '__main__':
    out = sys.argv[1]
    cache = os.path.join(out, 'cache')
    os.makedirs(cache, exist_ok=True)
    render_frames(cache, set(sys.argv[2:]) or None)
    if not sys.argv[2:]:
        sp = render_sprites(out, cache)
        m = build_sheets(out, cache, sp)
        print('crop', m['crop'], 'frame', m['frame'], {k: (v['cols'], v['rows']) for k, v in m['sheets'].items()})
