"""ネオンの絵（780×320）：夜空・しまの太陽・格子の床・星は前の neon.py のまま、馬だけ描き直す
   ななめ前から見た、騎手を乗せて走ってくる競走馬（3Dの馬＋3Dの形で作った騎手）を、ネオンの線（色は部分ごと）で。
   うしろにネオンの光のつぶ（砂ぼこりのかわり）
   python3 flat/neon_banner.py <出力.webp> [色分けの見本PNG]
   （壁紙の動き（flat/neon_run.py）のために、背景（background）・馬と騎手（rider）・重ねる所（compose）に分けた。
     いつもの絵は前と1バイトもちがわない）"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from neon_rider import *          # style2d・Hm・render_rider・素材の番号

W, Hh = 780, 320
BOX = (176, 16, 462, 304)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
HORSE, SILK, PANTS, BOOT, CLOTH = '#2EEBFF', '#FF2BD6', '#F4E9FF', '#B36BFF', '#FFE45C'


def background():
    """夜空・太陽・格子・星（前の絵と同じ）"""
    rng = np.random.default_rng(131)
    img = grad_v(Hh, W, [(0, '#05030F'), (0.55, '#1A0833'), (0.62, '#2B0A3D'), (1, '#07030F')])
    hz = 196
    sun = soft_circle(Hh, W, 520, hz - 6, 92, 1.0) * (yy < hz)
    stripes = ((yy > hz - 60) & (((yy - (hz - 60)) % 14) > 14 - (yy - (hz - 60)) / 8)).astype(np.float32)
    sun = sun * (1 - stripes)
    scol = grad_v(Hh, W, [(0, '#FFE45C'), (0.35, '#FFE45C'), (0.62, '#FF3EA5'), (1, '#FF3EA5')])
    img = img + blur(sun, 22)[..., None] * hexc('#FF3EA5') * 0.5
    img = over(img, scol, sun)
    gl = np.zeros((Hh, W), np.float32)
    for k in range(-16, 17):
        x_far = W / 2 + k * 18; x_near = W / 2 + k * 130
        cv2.line(gl, (int(x_far * 16), int(hz * 16)), (int(x_near * 16), int(Hh * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
    for j in range(1, 14):
        y = hz + (Hh - hz) * (j / 13) ** 2.2
        cv2.line(gl, (0, int(y * 16)), (W * 16, int(y * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
    gl = gl * (yy >= hz)
    img = over(img, hexc('#0A0418'), (yy >= hz).astype(np.float32))
    img = img + blur(gl, 3)[..., None] * hexc('#FF2BD6') * 0.6 + gl[..., None] * hexc('#FF7AE6') * 0.8
    cv2.line(img, (0, hz), (W, hz), (1.0, 0.5, 0.9), 2, cv2.LINE_AA)
    for i in range(80):
        x, y = rng.uniform(0, W), rng.uniform(0, hz - 20)
        m = soft_circle(Hh, W, x, y, rng.uniform(0.6, 1.4), 1.0)
        img = img + m[..., None] * 0.8
    return img


def rider(pose=None, cam=None, name='neon2'):
    """競走馬と騎手（3D）。pose・cam を決めると、いまの絵と同じカメラで別の形を描ける"""
    return render_rider(BOX, W, Hh, azim=55, elev=6, ss=2, name=name, js=1.15, pose=pose, cam=cam)


NO_DUST = os.environ.get('NEON_NO_DUST') == '1'    # 光のつぶを 絵に 入れない（壁紙では 別の 層で 動かす）
DUST_COLS = ('#FF2BD6', '#2EEBFF', '#B36BFF', '#FFE45C')


def dust_particles(hip):
    """光のつぶ 240こ の もと（いまの絵と 同じ 乱数の 順・seed 57）：(x, y, 種類 'dot'／'line', 大きさ s か 長さ L, 色の 番号, こさ w)。絵の 画素 780×320。
       hip：光のつぶの 中心（腰）"""
    pr = np.random.default_rng(57)
    cx_, cy_ = hip
    out = []
    for i in range(240):
        r = abs(pr.normal(0, 1)) * 95 + 8
        a = math.pi + pr.normal(0, 0.55)
        x = cx_ + math.cos(a) * r * 1.25 + 10
        y = cy_ + math.sin(a) * r * 0.55 + 30 + pr.normal(0, 12)
        if not (0 <= x < W and 0 <= y < Hh):
            continue
        s = max(0.6, pr.normal(1.3, 0.5)) * (1.25 - r / 300)
        if pr.random() < 0.3:                                          # 短い光の筋
            L = 4 + pr.random() * 8
            kind, size = 'line', L
        else:
            kind, size = 'dot', s
        w = float(np.clip(1.15 - r / 260, 0.25, 1))
        ci = int(pr.integers(0, 4))
        out.append((float(x), float(y), kind, float(size), ci, w))
    return out


def dust_light(hip):
    """光のつぶの 足す光（RGB・0〜1）：いまの絵の img = img + dust_light(hip) と 同じ"""
    dots = np.zeros((Hh, W), np.float32); dcol = np.zeros((Hh, W, 3), np.float32)
    pcols = [hexc(c) for c in DUST_COLS]
    for x, y, kind, size, ci, w in dust_particles(hip):
        d = np.zeros((Hh, W), np.float32)
        if kind == 'line':
            L = size
            cv2.line(d, (int(x * 16), int(y * 16)), (int((x - L) * 16), int((y + L * 0.12) * 16)), 1.0, 2, cv2.LINE_AA, shift=4)
        else:
            cv2.circle(d, (int(x * 16), int(y * 16)), int(size * 16), 1.0, -1, cv2.LINE_AA, shift=4)
        dots = np.maximum(dots, d * w)
        dcol += d[..., None] * pcols[ci] * w
    dcol = np.where(dots[..., None] > 1e-4, dcol / np.maximum(dcol.max(-1, keepdims=True), 1e-4) * dots[..., None], 0)
    return blur(dcol, 3.5) * 0.9 + dcol * 0.9


def hip_px(R):
    """光のつぶの中心（腰）"""
    return R['scene'].project(np.array([np.array([R['S']['hip'][0], R['S']['hip'][1], 0.0])]))[0][0][:2]


def compose(img, R, hip=None, hair=0.0, dbg=None):
    """馬と騎手（ネオンの線）と、うしろの光のつぶを重ねる。hip：光のつぶの中心（なければ この馬の腰）・hair：たてがみとしっぽの波のずれ"""
    S, scn, J = R['S'], R['scene'], R['J']
    A = np.clip(R['a'], 0, 1)
    mat = np.round(R['m']).astype(int)
    proj = lambda p3: scn.project(np.array([p3]))[0][0][:2]

    # たてがみ（首すじからうしろへ短くなびく）・しっぽ（うしろへ流れる）
    hr = np.random.default_rng(31)
    crest = np.asarray(R['crest'], float)
    nC = len(crest)
    locks = []
    for i in range(4, nC - 8, 2):
        p = crest[i]
        tg = crest[min(i + 1, nC - 1)] - crest[i - 1]
        up = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.cos(up) > 0.3:
            up += math.pi
        pts = flow(p, up - 0.7, 22 + 10 * math.sin(i / nC * math.pi), 8, wind=0.35, wind_ang=math.pi + 0.35, rng=hr, wave=1.0, phase=i + hair)
        locks.append(lock_poly(pts, 10, 0.6))
    th_ = np.asarray(R['tail'][0], float)
    for k in range(5):                                          # しっぽ：うしろ下へ波打ちながら流れる
        pts = flow(th_, math.pi + 0.55 + (k - 2) * 0.12, 54 + (2 - abs(k - 2)) * 8, 14, wind=0.16, wind_ang=math.pi + 0.05, rng=hr, wave=2.2, phase=k * 0.8 + hair)
        locks.append(lock_poly(pts, 12 - abs(k - 2) * 2, 0.8))
    hair_a = poly_aa((Hh, W), locks)
    sil = np.clip(np.maximum(A, hair_a), 0, 1)

    # 部分ごとの色（線の色）：外がわの線にも いちばん近い部分の色をつける
    cols = {1: HORSE, 5: HORSE, 6: HORSE, M_SILK: SILK, M_HELMET: SILK, M_PANTS: PANTS, M_BOOT: BOOT, M_CLOTH: CLOTH}
    cimg = np.zeros((Hh, W, 3), np.float32)
    inside = (A > 0.5)
    for k, c in cols.items():
        cimg[(mat == k) & inside] = hexc(c)
    cimg[(hair_a > 0.5) & ~inside] = hexc(HORSE)
    known = ((A > 0.5) | (hair_a > 0.5)).astype(np.uint8)
    dist, lab = cv2.distanceTransformWithLabels(1 - known, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(known == 1)
    lut = np.zeros((lab.max() + 1, 3), np.float32)
    lut[lab[ys, xs]] = cimg[ys, xs]
    cfull = lut[lab]                                     # どの画素も、いちばん近い馬・騎手の色

    # 線：外の形（なめらか）＋重なり・折れ目（3Dの形から）＋部分のさかい目
    ln = edges(R, width=2.0, crease=0.62)
    mb = np.zeros((Hh, W), np.float32)
    for k in (M_SILK, M_PANTS, M_BOOT, M_CLOTH, M_HELMET):
        reg = ((mat == k) & inside).astype(np.uint8)
        mb = np.maximum(mb, cv2.morphologyEx(reg, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32))
    hl = cv2.morphologyEx((hair_a > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) * (A < 0.5)
    line = np.clip(ln + mb * 0.9 + hl, 0, 1)
    line = cv2.GaussianBlur(line, (3, 3), 0.5)

    # 手綱（手 → 口）
    mz = np.asarray(R['muzzle'], float)[:2]
    rein = np.zeros((Hh * 4, W * 4), np.float32)
    for z in (1, -1):
        h2 = proj(J[f'hand{z}'])
        mid = (h2 + mz) / 2 + np.array([0, 6.0])
        curve = np.array([(1 - u) ** 2 * h2 + 2 * (1 - u) * u * mid + u ** 2 * mz for u in np.linspace(0, 1, 16)])
        cv2.polylines(rein, [(curve * 4 * 16).astype(np.int32)], False, 1.0, 5, cv2.LINE_AA, shift=4)
    rein = cv2.resize(rein, (W, Hh), interpolation=cv2.INTER_AREA)

    # ---------- うしろのネオンの光のつぶ（砂ぼこりのかわり） ----------
    #   NEON_NO_DUST=1 なら ここでは 描かない：壁紙（neon_wall.py）が 光のつぶだけの 絵（dust_layer）と きらめく 粒を 別の 層で 重ねて 動かす
    #   （2026/10/25 まさちゃん「ネオンの黄色丸の中の小さな光は常にキラキラと光りながら動いているようにして！」）
    if not NO_DUST:
        img = img + dust_light(hip_px(R) if hip is None else hip)                    # 光のつぶ（馬のうしろ・足す光）

    # ---------- 重ねる ----------
    img = over(img, hexc('#060312'), sil * 0.88)                                     # 形の中は暗く（うしろの格子をかくす）
    img = img + blur(sil, 10)[..., None] * hexc('#4A1A8A') * 0.18                   # 形のまわりのうすい光
    glow_c = cfull * line[..., None]
    img = img + blur(glow_c, 6) * 1.1 + blur(glow_c, 2) * 0.8
    img = np.maximum(img, line[..., None] * (0.55 * cfull + 0.45))                   # 線のしん（白っぽく）
    rc = hexc('#FFE45C')
    img = img + blur(rein, 2.5)[..., None] * rc * 0.7
    img = np.maximum(img, rein[..., None] * (0.6 * rc + 0.4))
    ex, ey = np.asarray(R['eye'], float)[:2]                                          # 目
    img = np.maximum(img, soft_circle(Hh, W, ex, ey, 1.8, 0.8)[..., None] * hexc('#E6FDFF'))
    if dbg is not None:
        dbg['cfull'], dbg['line'], dbg['sil'] = cfull, line, sil
    return img


if __name__ == '__main__':
    out = sys.argv[1]
    img = background()
    R = rider()
    dbg = {}
    img = compose(img, R, dbg=dbg)
    save_webp(np.clip(img, 0, 1), out)
    if len(sys.argv) > 2:
        cv2.imwrite(sys.argv[2], cv2.cvtColor((np.clip(dbg['cfull'] * 0.4 + dbg['line'][..., None], 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    print(out)
