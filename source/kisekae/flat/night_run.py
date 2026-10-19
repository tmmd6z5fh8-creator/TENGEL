"""ナイターの壁紙の動き（まさちゃんの指定「常に走ってる、背景が常に右から左に模様が動く同じ模様をリピートする、
   1秒〜5秒の間に3頭の順位が前後する、20秒に一回ゴールする馬はランダムにする」）：動く絵の部品
   - 背景を 横に くり返せる3まいに描き直す（色と描き方は いまの絵＝flat/anime_night.py と同じ。はしに かかる形は 反対がわにも描く：
     3まいぶんの はばで描いて まん中を切りぬく）：
       far   … 空・うすい雲・星・スタンド（屋根のふちの光・窓・観客の光・ぼけた光の玉）・照明3本（等間かくに置きなおす） 0〜FAR_H
       track … 奥の柵・ダート（光だまり・はけの筋・ひづめのあと・柵の下の暗がり）TRACK_Y〜320・すき通しつき（上は柵だけ）
       rail  … 手前の柵（支柱を 等間かくに・支柱の影）RAIL_Y〜320・すき通しつき
     ページで 遠いほど ゆっくり 右から左へ流す（night_wall.py）
   - 3頭：いまの絵と同じ馬と騎手（anime_rider・同じカメラ・同じ塗り・同じ乱数）を、ギャロップ1回 N_FRAMES コマで描く
     （足の動きは 海の馬と同じ・体と首と頭は いまの絵の形を中心に少しゆれる・しっぽと たてがみは コマごとに なびく）。
     地面についている ひづめを いまの絵の地面にそろえる（宙のコマは山なり）。影（いまの絵と同じ大きさ）と、
     うしろへ流れる砂けむり（コマ0 と さいごが つながる）も入れて、すき通しつきの1頭ずつのシートにする
   python3 flat/night_run.py <出力フォルダ> [far] [track] [rail] [horses|h5|h3|h7]  → night_far.webp・night_track.webp・night_rail.webp・night_h<番号>.webp・night_run.json
   （horses・h<番号> は sdfr がいる。1コマ 約30〜80秒。描いたコマは <出力フォルダ>/cache に のこして 2回目は描かない）"""
import sys, os, math, json
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from anime_rider import *            # hexc・blur・over・grad_v・soft_circle・render_anime・paint_anime・LINE・ss_ など
from sea_run import F_KEYS, H_KEYS, LEG_OFF, STANCE, leg_at

W, Hh = 780, 320
H = hexc
FAR_H = 196                          # far の下のはし（スタンドの下・ダートの上のはしより少し下）
TRACK_Y = 186                        # track の上のはし（奥の柵の上）
RAIL_Y = 288                         # rail の上のはし
TOWERS = [(130, 40), (390, 20), (650, 34)]      # 照明（くり返しの はばの中に 等間かく・高さは いまの絵と同じ）
POOLS = (130, 390, 650)                          # ダートの光だまり（照明と同じ間かく）
FENCE_N = 32                         # 奥の柵の支柱の数（はば W に）
RAIL_N = 6                           # 手前の柵の支柱の数（はば W に）
N_FRAMES = 10                        # ギャロップ1回のコマ数
LIFT = 6.0                           # 宙に浮くコマの いちばん高い所（画素）
PHASE = {5: 0.0, 3: 0.37, 7: 0.71}   # 3頭の足の運びのずれ
DUST_RUN = 118.0                     # 砂けむりが ギャロップ1回で うしろへ流れる はば（画素・ダートの流れに合わせる）
HOOF_KEYS = ('FL', 'FR', 'HL', 'HR')

# いまの絵（anime_night.py）の3頭（奥 → 手前）
HORSES = [
    dict(box=(486, 120, 652, 238), num=5, seed=5, tail=0.85, mane=0.72, coat='chestnut', legs='socks', silk='blue', sleeve='white', helmet='blue', lw=0.85,
         pose=dict(theta=-2.0, neck_rot=-34.0, head_ang=-34.0, fore=dict(L=[-84, -24, -50, -30], R=[-112, -52, -128, -155]),
                   hind=dict(L=[-122, -158, -140, -160], R=[-82, -120, -96, -76]), tail=[-168, -156]), haze=0.20),
    dict(box=(46, 126, 268, 268), num=3, seed=3, padx=140, tail=1.22, tail_ang=178, tail_spread=0.025, tail_wave=0.8,
         tail_prof=(1.0, 1.0, 0.98, 0.96, 0.93, 0.90, 0.86), mane=0.72, coat='darkbay', legs='black', silk='green', sleeve='yellow', helmet='yellow', lw=0.92,
         roll=True,
         pose=dict(theta=1.0, neck_rot=-32.0, head_ang=-34.0, fore=dict(L=[-96, -48, -44, -28], R=[-128, -36, -140, -165]),
                   hind=dict(L=[-118, -150, -128, -150], R=[-70, -112, -84, -62]), tail=[-166, -154]), haze=0.10),
    dict(box=(256, 104, 556, 300), num=7, seed=7, tail=1.52, tail_ang=153, tail_spread=0.055, tail_wave=1.0, mane=0.72, coat='bay', legs='black', silk='red', sleeve='white', helmet='red', lw=1.0,
         pose=dict(theta=0.0, neck_rot=-36.0, head_ang=-32.0, fore=dict(L=[-100, -40, -30, -18], R=[-132, -28, -150, -170]),
                   hind=dict(L=[-112, -152, -136, -156], R=[-56, -106, -76, -56]), tail=[-170, -158]), haze=0.0),
]
HAZE = H('#2E2C66')
Y0 = 150                             # ダートの遠近の基準（anime_night.py と同じ）


# ---------------- くり返せる絵の道具：3まいぶんの はば（WW）で描いて、まん中を切りぬく ----------------
WW = 3 * W


def copies(x, pad=None):
    """もとの x（0〜W）→ 3まいぶんの絵の x（まん中が もとの位置）。はしに かからない形は まん中だけ（pad を わたした時）"""
    xs = [x, x + W, x + 2 * W]
    if pad is None:
        return xs
    return [v for v in xs if -pad <= v - W <= W + pad]


def mid(img):
    return img[:, W:2 * W]


def aa(h, scale=4):
    return np.zeros((h * scale, WW * scale), np.float32)


def down(c, h):
    return cv2.resize(c, (WW, h), interpolation=cv2.INTER_AREA)


def soft_dot(img, x, y, r, feather, col):
    """小さな丸い光を足す（まわりだけ計算する）"""
    h, w = img.shape[:2]
    R_ = r + feather * 2 + 1
    x0, x1 = max(0, int(x - R_)), min(w, int(x + R_) + 2)
    y0, y1 = max(0, int(y - R_)), min(h, int(y + R_) + 2)
    if x1 <= x0 or y1 <= y0:
        return
    yy_, xx_ = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt((xx_ - x) ** 2 + (yy_ - y) ** 2)
    img[y0:y1, x0:x1] += np.clip((r - d) / feather + 0.5, 0, 1)[..., None] * col


# ---------------- far：空・雲・星・スタンド・照明 ----------------
def far_band():
    hh = FAR_H
    yy, xx = np.mgrid[0:hh, 0:WW].astype(np.float32)
    img = grad_v(Hh, WW, [(0, '#060A2C'), (0.30, '#101654'), (0.48, '#262A78'), (0.58, '#43358C'), (0.62, '#4E3A90')])[:hh].copy()
    cl = np.random.default_rng(3)
    cloud = np.zeros((hh, WW), np.float32)
    for i in range(7):                                                # うすい雲（横長・下のふちが照明で明るい）
        cx, cy = cl.uniform(0, W), cl.uniform(70, 125)
        for j in range(9):
            ex, ey = cx + cl.normal(0, 60), cy + cl.normal(0, 5)
            ax, ay = cl.uniform(40, 110), cl.uniform(5, 11)
            for X in copies(ex):
                cv2.ellipse(cloud, (int(X * 16), int(ey * 16)), (int(ax * 16), int(ay * 16)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
    cloud = blur(np.clip(cloud, 0, 1), 4)
    img = over(img, H('#3A3A8E'), cloud * 0.45)
    img = img + (np.clip(cloud - np.roll(cloud, -5, axis=0), 0, 1))[..., None] * H('#8E86D8') * 0.35
    srng = np.random.default_rng(11)
    sp = aa(hh)
    for i in range(120):                                              # 星（点・ときどき十字のきらめき）
        x, y = srng.uniform(0, W), srng.uniform(0, 140)
        r = srng.uniform(0.45, 1.1)
        b = srng.uniform(0.45, 0.95)
        for X in copies(x, 4):
            soft_dot(img, X, y, r, 0.8, np.ones(3, np.float32) * b)
        if srng.random() < 0.10:
            L = srng.uniform(3.5, 6.5)
            for X in copies(x, 10):
                cv2.line(sp, (int((X - L) * 64), int(y * 64)), (int((X + L) * 64), int(y * 64)), 1.0, 2, cv2.LINE_AA, shift=4)
                cv2.line(sp, (int(X * 64), int((y - L) * 64)), (int(X * 64), int((y + L) * 64)), 1.0, 2, cv2.LINE_AA, shift=4)
    sp = down(sp, hh)
    img = img + sp[..., None] * H('#EAF0FF') * 0.75 + blur(sp, 1.5)[..., None] * H('#9DB4FF') * 0.5
    # スタンド（まん中が少し高い屋根・くり返し）
    hump = np.exp(-((np.sin(np.pi * (xx - W - 390) / W) * W / np.pi) / 320) ** 2)
    top_s = 145 - 13 * hump
    stand = np.clip((yy - top_s) * 1.2 + 0.5, 0, 1) * (yy < 191)
    img = over(img, H('#191846'), stand)
    img = over(img, H('#24225E'), stand * np.clip((yy - 158) / 20, 0, 1) * 0.8)
    roofline = np.exp(-((yy - top_s - 0.5) / 0.9) ** 2) * (yy < 191)
    img = img + roofline[..., None] * H('#A9B8FF') * 0.65                          # 屋根のふちの光
    kw = 2 * np.pi * 106 / W                                                       # 窓（はば W に ちょうど106こ）
    for row, (yo, ph, col_) in enumerate(((9, 0.0, '#FFE2A0'), (15, 1.7, '#FFD490'))):
        win = ((np.sin(xx * kw + ph) > 0.62) & (np.abs(yy - (top_s + yo)) < 1.1)).astype(np.float32)
        img = img + blur(win * stand, 0.6)[..., None] * H(col_) * 0.6
    crowd = np.random.default_rng(12)
    for i in range(520):                                              # 観客の光の粒
        x = crowd.uniform(0, W); y = crowd.uniform(163, 189)
        cc = crowd.integers(0, 5)
        rr = crowd.uniform(0.5, 0.9)
        if stand[int(y), int(x + W)] > .5:
            c = [H('#FFE7A8'), H('#FFFFFF'), H('#A8C8FF'), H('#FF9AC8'), H('#9CF0FF')][cc]
            for X in copies(x, 3):
                soft_dot(img, X, y, rr, 0.7, c * 0.85)
    bk = np.random.default_rng(13)
    for i in range(26):                                               # ぼけた光の玉（ふちが少し明るい）
        x, y = bk.uniform(0, W), bk.uniform(150, 192)
        r = bk.uniform(3, 8)
        c = [H('#FFD9A0'), H('#A8C4FF'), H('#FFB0D8'), H('#B8FFF0')][bk.integers(0, 4)]
        for X in copies(x, 12):
            soft_dot(img, X, y, r, 1.2, c * 0.12)
            dd = np.zeros_like(img)
            soft_dot(dd, X, y, r, 1.2, c)
            soft_dot(dd, X, y, r - 1.0, 1.2, -c)
            img += dd * 0.05
    # 照明（ランプの粒・十字と横に長い光・下へ広がる光）
    for tx0, ty in TOWERS:
        for tx in copies(tx0):
            pole = aa(hh)
            cv2.line(pole, (int(tx * 64), int((ty + 8) * 64)), (int(tx * 64), int(190 * 64)), 1.0, 12, cv2.LINE_AA, shift=4)
            for yb in range(ty + 22, 186, 16):                                     # 柱の横棒
                cv2.line(pole, (int((tx - 3) * 64), int(yb * 64)), (int((tx + 3) * 64), int((yb + 8) * 64)), 1.0, 5, cv2.LINE_AA, shift=4)
            img = over(img, H('#0C0D28'), down(pole, hh))
            ang = np.arctan2(xx - tx, yy - ty)                                      # 下へ広がる光
            cone = np.clip(1 - np.abs(ang) / 0.62, 0, 1) ** 1.5 * (yy > ty) * np.exp(-(yy - ty) / 240)
            img = img + blur(cone, 5)[..., None] * H('#7F96FF') * 0.14
            lamp = aa(hh)
            for i in range(3):
                for j in range(5):
                    cv2.circle(lamp, (int((tx - 16 + j * 8) * 64), int((ty - 7 + i * 7) * 64)), int(3.1 * 64), 1.0, -1, cv2.LINE_AA, shift=4)
            frame = aa(hh)
            cv2.rectangle(frame, (int((tx - 21) * 64), int((ty - 11) * 64)), (int((tx + 21) * 64), int((ty + 11) * 64)), 1.0, -1, cv2.LINE_AA, shift=4)
            img = over(img, H('#1A1C40'), down(frame, hh))
            lamp = down(lamp, hh)
            img = img + blur(lamp, 30)[..., None] * H('#6E84FF') * 0.75 + blur(lamp, 10)[..., None] * H('#B8C8FF') * 0.9
            img = np.maximum(img, lamp[..., None] * H('#FFFFFF'))
            fl = aa(hh)
            for (dx, dy, L, wd) in ((1, 0, 150, 3), (0, 1, 44, 3), (0.7, 0.7, 20, 2), (0.7, -0.7, 20, 2)):
                cv2.line(fl, (int((tx - dx * L) * 64), int((ty - dy * L) * 64)), (int((tx + dx * L) * 64), int((ty + dy * L) * 64)), 1.0, wd * 4, cv2.LINE_AA, shift=4)
            fl = down(fl, hh)
            fall = np.exp(-np.sqrt((xx - tx) ** 2 * 0.6 + ((yy - ty) * 2.4) ** 2) / 60)
            img = img + (blur(fl, 0.8) * fall)[..., None] * H('#E2E8FF') * 1.1 + (blur(fl, 3) * fall)[..., None] * H('#8EA2FF') * 0.5
    return np.clip(mid(img), 0, 1)


# ---------------- track：奥の柵・ダート（すき通しつき・y は TRACK_Y から） ----------------
def track_band():
    TOP = 194
    yy, xx = np.mgrid[0:Hh, 0:WW].astype(np.float32)
    trk = np.clip((yy - TOP) + 0.5, 0, 1)
    dirt = grad_v(Hh, WW, [(0, '#3C2A34'), (0.60, '#3C2A34'), (0.61, '#5C4040'), (0.75, '#74503E'), (1, '#8E6248')])
    pool = np.zeros((Hh, WW), np.float32)
    for tx0 in POOLS:
        for tx in copies(tx0):
            pool += np.exp(-(((xx - tx) / 200) ** 2 + ((yy - 254) / 50) ** 2))
    pool = np.clip(pool, 0, 1.2)
    dirt = dirt * (0.70 + 0.42 * pool)[..., None] + (pool * 0.08)[..., None] * H('#C4B4FF')
    br = np.random.default_rng(21)
    lite = np.zeros((Hh * 4, WW * 4), np.float32); dark = np.zeros((Hh * 4, WW * 4), np.float32)
    for i in range(170):                                              # はけの筋（遠いほど細く短く）
        y = TOP + 3 + (Hh - TOP - 3) * br.random() ** 0.85
        sc_ = (y - Y0) / (Hh - Y0)
        x = br.uniform(0, W); L = (br.uniform(20, 110) * sc_ + 8)
        tgt = lite if br.random() < 0.5 else dark
        v, th = br.uniform(0.4, 1.0), max(1, int(round(6 * sc_)))
        for X in copies(x - 60):
            pts = np.array([[X + L * t, y + math.sin(t * math.pi) * -0.6 * sc_] for t in np.linspace(0, 1, 8)])
            cv2.polylines(tgt, [np.round(pts * 64).astype(np.int32)], False, v, th, cv2.LINE_AA, shift=4)
    dn = lambda c: cv2.resize(c, (WW, Hh), interpolation=cv2.INTER_AREA)
    dirt = dirt + blur(dn(lite), 0.5)[..., None] * H('#B08C70') * 0.20 - blur(dn(dark), 0.5)[..., None] * 0.06
    hp = np.zeros((Hh * 2, WW * 2), np.float32)
    pr = np.random.default_rng(7)
    for i in range(260):                                              # ひづめのあと
        y = TOP + 6 + (Hh - TOP - 6) * pr.random() ** 0.8
        x = pr.uniform(0, W)
        sc_ = (y - Y0) / (Hh - Y0)
        v = pr.uniform(0.4, 1.0)
        for X in copies(x, 8):
            cv2.ellipse(hp, (int(X * 2 * 16), int(y * 2 * 16)), (int(max(1.0, 3.6 * sc_) * 2 * 16), int(max(0.5, 1.3 * sc_) * 2 * 16)), 0, 0, 360,
                        v, -1, cv2.LINE_AA, shift=4)
    hp = cv2.resize(hp, (WW, Hh), interpolation=cv2.INTER_AREA)
    dirt = dirt * (1 - hp * 0.25)[..., None] + np.roll(hp, -1, axis=0)[..., None] * H('#C8A88C') * 0.10
    dirt = dirt * (1 - (np.exp(-(yy - TOP) / 6) * 0.35))[..., None]               # 柵の下の暗がり
    # すき通しつきに重ねる（色は 先にかけた形：premultiplied）
    pre = dirt * trk[..., None]
    A = trk.copy()
    fr = np.zeros((Hh * 4, WW * 4), np.float32)                                    # 奥の柵
    cv2.line(fr, (0, 190 * 64), (WW * 64, 190 * 64), 1.0, 9, cv2.LINE_AA, shift=4)
    for k in range(3 * FENCE_N):
        x = 6 + k * W / FENCE_N
        cv2.line(fr, (int(x * 64), 190 * 64), (int(x * 64), 201 * 64), 1.0, 5, cv2.LINE_AA, shift=4)
    fr = dn(fr)

    def ov(pre, A, col, al):
        al = np.clip(al, 0, 1)
        return pre * (1 - al[..., None]) + col * al[..., None], A + al * (1 - A)
    pre, A = ov(pre, A, H('#E8ECFF'), fr)
    pre, A = ov(pre, A, H('#9EA6D4'), fr * np.clip(yy - 190.3, 0, 1) * 0.9)
    pre, A = mid(pre)[TRACK_Y:], mid(A)[TRACK_Y:]
    rgb = np.where(A[..., None] > 1e-4, pre / np.maximum(A, 1e-4)[..., None], 0)
    return np.clip(rgb, 0, 1), np.clip(A, 0, 1)


# ---------------- rail：手前の柵（すき通しつき・y は RAIL_Y から） ----------------
def rail_band():
    RY = 302
    yy, xx = np.mgrid[0:Hh, 0:WW].astype(np.float32)
    post = np.zeros((Hh * 4, WW * 4), np.float32); rail = np.zeros((Hh * 4, WW * 4), np.float32)
    sp = W / RAIL_N
    for k in range(3 * RAIL_N):
        x = 30 + k * sp
        cv2.rectangle(post, (int((x - 4) * 64), int(RY * 64)), (int((x + 4) * 64), int(Hh * 64)), 1.0, -1, cv2.LINE_AA, shift=4)
    cv2.rectangle(rail, (0, int((RY - 4) * 64)), (WW * 64, int((RY + 5) * 64)), 1.0, -1, cv2.LINE_AA, shift=4)
    dn = lambda c: cv2.resize(c, (WW, Hh), interpolation=cv2.INTER_AREA)
    post, rail = dn(post), dn(rail)
    pre = np.zeros((Hh, WW, 3), np.float32); A = np.zeros((Hh, WW), np.float32)

    def ov(pre, A, col, al):
        al = np.clip(al, 0, 1)
        col = np.broadcast_to(col, pre.shape)
        return pre * (1 - al[..., None]) + col * al[..., None], A + al * (1 - A)
    pre, A = ov(pre, A, np.zeros(3, np.float32), np.roll(post, 4, axis=1) * 0.30)          # 支柱の影
    pshade = (np.clip(((xx - 30) % sp) - 0.5, 0, 1) * (((xx - 30) % sp) < sp / 2))[..., None]   # 支柱の右半分は影
    pre, A = ov(pre, A, H('#F2F4FF') * (1 - pshade) + H('#AAB2DC') * pshade, post)
    rshade = np.clip(yy - (RY + 0.5), 0, 1)[..., None]
    pre, A = ov(pre, A, H('#F6F8FF') * (1 - rshade) + H('#B0B8E0') * rshade, rail)
    gl = (np.exp(-((yy - (RY - 2.6)) / 0.7) ** 2) * (rail > 0.5))[..., None]               # レールのつや
    rgb_ = np.where(A[..., None] > 1e-4, pre / np.maximum(A, 1e-4)[..., None], 0)
    rgb_ = np.maximum(rgb_, gl * 1.0)
    pre = rgb_ * A[..., None]
    um = ((post + rail) > 0.5).astype(np.uint8)
    ol = cv2.morphologyEx(um, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32) * (yy < Hh - 1)
    pre, A = ov(pre, A, LINE, cv2.GaussianBlur(ol, (3, 3), 0.5) * 0.8)
    pre, A = mid(pre)[RAIL_Y:], mid(A)[RAIL_Y:]
    rgb = np.where(A[..., None] > 1e-4, pre / np.maximum(A, 1e-4)[..., None], 0)
    return np.clip(rgb, 0, 1), np.clip(A, 0, 1)


# ---------------- 3頭：ギャロップのコマ・影・砂けむり ----------------
def horse_pose(g, P0):
    """ギャロップの位相 g（0〜1）の形（3Dは右向き：手前＝L・奥＝R）。足は海の馬と同じ・体と首と頭は いまの絵の形 P0 を中心にゆれる"""
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - LEG_OFF[k])
    w = 2 * math.pi
    return dict(theta=round(P0['theta'] + 3.0 * math.cos(w * (g - 0.15)), 2), neck_rot=round(P0['neck_rot'] + 5 * math.cos(w * (g - 0.55)), 2),
                head_ang=round(P0['head_ang'] + 3 * math.sin(w * g), 2), tail=P0['tail'],
                fore=dict(L=leg('FL'), R=leg('FR')), hind=dict(L=leg('HL'), R=leg('HR')))


def stance_legs(g):
    return [k for k in HOOF_KEYS if ((g - LEG_OFF[k]) % 1.0) < STANCE]


def smooth_dy(dys):
    """上下のずれを なめらかに（くり返しの2つの波に合わせる）"""
    n = len(dys)
    ph = 2 * math.pi * np.arange(n) / n
    A = np.stack([np.ones(n), np.cos(ph), np.sin(ph), np.cos(2 * ph), np.sin(2 * ph)], 1)
    return A @ np.linalg.lstsq(A, np.asarray(dys, float), rcond=None)[0]


def shadow_mask(hv, gy, scl, wc=W):
    """いまの絵と同じ影（横長の影と、地面に近いひづめの下の小さな影）：1倍の 0〜1（はば wc）"""
    x0, x1 = hv[:, 0].min(), hv[:, 0].max()
    sh = np.zeros((Hh * 4, wc * 4), np.float32)
    cv2.ellipse(sh, (int((x0 + x1) / 2 * 64), int(gy * 64)), (int((x1 - x0) / 2 * 1.02 * 64), int((5.5 * scl + 1.2) * 64)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
    for hx_, hy_ in hv:
        if gy - hy_ < 10 * scl + 2:
            cv2.ellipse(sh, (int(hx_ * 64), int(gy * 64)), (int(7 * scl * 64 + 64), int(2 * scl * 64 + 32)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
    return cv2.resize(sh, (wc, Hh), interpolation=cv2.INTER_AREA)


def dust_flow(hx, gy, scl, dim, seed, ph, wc=W):
    """けり上げた砂けむり（anime_night.py の dust_puffs と同じ塗り）。雲の丸は ph（ギャロップの位相 0〜1）で うしろへ流れながら大きくなり、
       足もとで うまれて うしろで消える（ph の 0 と 1 で つながる）。とぶ砂の粒も うしろへ流れる。戻り値：1倍の絵ぜんたいの (rgb, alpha)"""
    r_ = np.random.default_rng(seed)
    S2 = 3
    x0, x1 = int(max(0, hx - 160 * scl - 40)), int(min(wc, hx + 26))
    y0, y1 = int(max(0, gy - 100 * scl - 24)), int(min(Hh, gy + 10))
    rgbF, aF = np.zeros((Hh, wc, 3), np.float32), np.zeros((Hh, wc), np.float32)
    if x1 <= x0 or y1 <= y0:
        return rgbF, aF
    cw, ch = (x1 - x0) * S2, (y1 - y0) * S2
    base, shade, lite = H('#BC9E8A'), H('#86685E'), H('#F2E2D0')
    M = np.zeros((ch, cw), np.float32)
    n = 22
    for i in range(n):
        t0 = (i + r_.uniform(0, 1)) / n
        dr, nx, hk = r_.uniform(-2.5, 3.5), r_.normal(0, 3), r_.uniform(0, 1) ** 1.2
        t = (t0 + ph) % 1.0                                           # うしろへの きょり（0：足もと 〜 1：うしろ）
        vis = float(ss_(0.0, 0.10, t) * (1 - ss_(0.80, 1.0, t)))      # うまれる・消える
        r = (8 + 13 * t + dr) * scl
        px = hx - 2 * scl - t * 115 * scl + nx * scl
        hmax = (4 + 40 * t) * scl
        py = gy - r * 0.50 - hk * hmax
        c1 = np.zeros((ch, cw), np.uint8)
        cv2.circle(c1, (int((px - x0) * S2 * 16), int((py - y0) * S2 * 16)), int(max(2, r) * S2 * 16), 255, -1, cv2.LINE_AA, shift=4)
        M = np.maximum(M, c1.astype(np.float32) / 255 * vis)
    xs_ = (np.arange(cw)[None, :] / S2 + x0)
    fade = np.clip(1.0 - (hx - xs_) / (125 * scl) * 0.66, 0.26, 0.95) * np.ones((ch, 1), np.float32)
    sig = 2.2 * scl * S2
    Mb = cv2.GaussianBlur(M, (0, 0), sig)
    gx = cv2.Sobel(Mb, cv2.CV_32F, 1, 0, ksize=3); gyy = cv2.Sobel(Mb, cv2.CV_32F, 0, 1, ksize=3)
    gn = np.sqrt(gx * gx + gyy * gyy) + 1e-6
    face = (-gx * 0.62 + gyy * 0.78) / gn                            # 外向きが右上（光の方）なら＋
    edge = ss_(0.02, 0.10, gn / (gn.max() + 1e-6) * 4)
    lit = ss_(0.30, 0.42, face) * edge * M
    shd = ss_(-0.20, -0.32, face) * edge * M
    c = np.zeros((ch, cw, 3), np.float32) + base
    c = c * (1 - shd[..., None]) + shade * shd[..., None]
    c = c * (1 - lit[..., None]) + lite * lit[..., None]
    al = M * fade
    col = c
    nclod = int(30 * scl) + 6
    for i in range(nclod):                                            # とぶ砂の粒（小さなかたまり・うしろへ短い筋）
        u0, vy, rr0, rot = r_.uniform(0, 1), r_.uniform(3, 64), r_.uniform(0.7, 1.8), r_.uniform(0, 180)
        u = (u0 + ph) % 1.0
        vis = float(ss_(0.0, 0.08, u) * (1 - ss_(0.85, 1.0, u)))
        px = (hx - (-8 + u * 118) * scl - x0) * S2; py = (gy - vy * scl - y0) * S2
        rr = rr0 * S2 * max(0.6, scl)
        clod = np.zeros((ch, cw), np.uint8)
        cv2.ellipse(clod, (int(px * 16), int(py * 16)), (int(rr * 1.25 * 16), int(rr * 16)), rot, 0, 360, 255, -1, cv2.LINE_AA, shift=4)
        cv2.line(clod, (int(px * 16), int(py * 16)), (int((px + rr * 3.5) * 16), int((py + rr * 0.8) * 16)), 110, max(1, int(rr * 0.7)), cv2.LINE_AA, shift=4)
        cm = clod.astype(np.float32) / 255 * vis
        col = over(col, H('#5A3E36'), cm); al = np.maximum(al, cm)
        hl = np.zeros((ch, cw), np.uint8)
        cv2.circle(hl, (int((px - rr * 0.3) * 16), int((py - rr * 0.35) * 16)), int(rr * 0.42 * 16), 255, -1, cv2.LINE_AA, shift=4)
        col = over(col, H('#D8BCA4'), hl.astype(np.float32) / 255 * cm)
    colS = cv2.resize(col * al[..., None], (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    alS = cv2.resize(al, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    rgbF[y0:y1, x0:x1] = colS / np.maximum(alS[..., None], 1e-4) * dim
    aF[y0:y1, x0:x1] = alS
    return rgbF, aF


def horse_frames(h, cache=None):
    """1頭の N_FRAMES コマ（1倍の絵ぜんたいの premultiplied RGBA のリスト）と 目印。cache：描いた馬を おいておく フォルダ（つぎは 描かない）"""
    num = h['num']
    px = h.get('padx', 0)                                              # 絵の はしで 切れないように、左右を px ずつ広く描く（カメラは同じ）
    wc = W + 2 * px
    R0 = render_anime(h['pose'], h['box'], W, Hh, name=f'nrun{num}')
    cam = R0['cam']
    s = R0['s']
    hv0 = np.asarray(R0['hooves'], float) / s + np.array([px, 0.0])
    gy = hv0[:, 1].max() + 1.5
    scl = (gy - Y0) / (Hh - Y0)
    sh = shadow_mask(hv0, gy, scl, wc)
    hx_d = hv0[2:, 0].min()
    nose = float(np.asarray(R0['muzzle'], float)[0] / s)
    n = N_FRAMES
    frames = []
    for f in range(n):
        g = (f / n + PHASE[num]) % 1.0
        cf = cache and os.path.join(cache, f'h{num}_f{f:02d}.npz')
        if cf and os.path.exists(cf):
            z = np.load(cf)
            rgb, a, hv = z['rgb'], z['a'], z['hv']
        else:
            R = render_anime(horse_pose(g, h['pose']), h['box'], wc, Hh, name=f'nrun{num}_{f}', cam=cam)
            rgb, a = paint_anime(R, dict(h, hair_phase=2 * math.pi * f / n))
            hv = np.asarray(R['hooves'], float) / s
            if cf:
                np.savez_compressed(cf, rgb=rgb.astype(np.float32), a=a.astype(np.float32), hv=hv)
        legs = stance_legs(g)
        low = max(hv[HOOF_KEYS.index(q), 1] for q in legs) if legs else None
        frames.append(dict(rgb=rgb, a=a, low=low, legs=legs))
        print('horse', num, 'frame', f, 'stance', legs, flush=True)
    g0 = hv0[:, 1].max()
    for fr in frames:
        fr['dy'] = None if fr['low'] is None else g0 - fr['low']
    for i, fr in enumerate(frames):
        if fr['dy'] is None:
            jp = next(j for j in range(1, n) if frames[(i - j) % n]['low'] is not None)
            jn = next(j for j in range(1, n) if frames[(i + j) % n]['low'] is not None)
            t = jp / (jp + jn)
            prev, nxt = frames[(i - jp) % n]['dy'], frames[(i + jn) % n]['dy']
            fr['dy_air'] = prev + (nxt - prev) * t - LIFT * 4 * t * (1 - t)
    for fr in frames:
        if fr['dy'] is None:
            fr['dy'] = fr.pop('dy_air')
    out = []
    for f, (fr, dy) in enumerate(zip(frames, smooth_dy([fr['dy'] for fr in frames]))):
        M = np.float32([[1, 0, 0], [0, 1, float(dy)]])
        a = cv2.warpAffine(fr['a'], M, (wc, Hh), flags=cv2.INTER_LINEAR)
        rp = cv2.warpAffine(fr['rgb'] * fr['a'][..., None], M, (wc, Hh), flags=cv2.INTER_LINEAR)
        rgb = np.where(a[..., None] > 1e-4, rp / np.maximum(a, 1e-4)[..., None], 0)
        rgb = rgb * (1 - h['haze']) + HAZE * h['haze']
        pre = np.zeros((Hh, wc, 3), np.float32); A = np.zeros((Hh, wc), np.float32)
        al = sh * 0.38                                                   # 影
        pre, A = pre * (1 - al[..., None]), A + al * (1 - A)
        dr, da = dust_flow(hx_d, gy, scl, 1.0 - h['haze'] * 0.8, 200 + HORSES.index(h), f / n, wc)
        pre, A = pre * (1 - da[..., None]) + dr * da[..., None], A + da * (1 - A)
        pre, A = pre * (1 - a[..., None]) + rgb * a[..., None], A + a * (1 - A)
        out.append((pre, A))
    return out, dict(nose=round(nose, 2), ground=round(float(gy), 2), padx=px, dy=[round(float(v), 2) for v in smooth_dy([fr['dy'] for fr in frames])])


def horse_sheet(h, out_dir):
    """1頭のコマ → 切りぬいて横に並べた1まい（すき通しつき・ロスなし）。コマの まわりは すき通しの のりしろ"""
    cache = os.path.join(out_dir, 'cache')
    os.makedirs(cache, exist_ok=True)
    frames, marks = horse_frames(h, cache)
    A_all = np.max(np.stack([A for _, A in frames]), 0)
    wc = A_all.shape[1]
    ys, xs = np.nonzero(A_all > 0.002)
    x0, y0 = max(0, int(xs.min()) - 4), max(0, int(ys.min()) - 4)
    x1, y1 = min(wc, int(xs.max()) + 5), min(Hh, int(ys.max()) + 5)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2
    x1, y1 = x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2
    cw, ch = x1 - x0, y1 - y0
    n = len(frames)
    sheet = np.zeros((ch, cw * n, 4), np.float32)
    for i, (pre, A) in enumerate(frames):
        rgb = np.where(A[..., None] > 1e-4, pre / np.maximum(A, 1e-4)[..., None], 0)
        sheet[:, i * cw:(i + 1) * cw, :3] = rgb[y0:y1, x0:x1]
        sheet[:, i * cw:(i + 1) * cw, 3] = A[y0:y1, x0:x1]
    save_rgba(f'{out_dir}/night_h{h["num"]}.webp', sheet[..., :3], sheet[..., 3])
    px = marks.pop('padx')
    return dict(frames=n, cell=[cw, ch], at=[x0 - px, y0], phase=PHASE[h['num']], **marks)


def save_rgba(path, rgb, a):
    u8 = (np.dstack([np.clip(rgb, 0, 1), np.clip(a, 0, 1)]) * 255 + .5).astype(np.uint8)
    Image.fromarray(u8, 'RGBA').save(path, 'WEBP', lossless=True, quality=100, method=6)


def save_rgb(path, rgb, q=None):
    u8 = (np.clip(rgb, 0, 1) * 255 + .5).astype(np.uint8)
    if q is None:
        Image.fromarray(u8, 'RGB').save(path, 'WEBP', lossless=True, quality=100, method=6)
    else:
        Image.fromarray(u8, 'RGB').save(path, 'WEBP', quality=q, method=6)


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    what = set(sys.argv[2:]) or {'far', 'track', 'rail', 'horses'}
    jf = f'{out}/night_run.json'
    info = json.load(open(jf)) if os.path.exists(jf) else {}
    info.update(size=[W, Hh], far=[0, FAR_H], track=[TRACK_Y, Hh], rail=[RAIL_Y, Hh])
    if 'far' in what:
        save_rgb(f'{out}/night_far.webp', far_band())
        print('far', flush=True)
    if 'track' in what:
        save_rgba(f'{out}/night_track.webp', *track_band())
        print('track', flush=True)
    if 'rail' in what:
        save_rgba(f'{out}/night_rail.webp', *rail_band())
        print('rail', flush=True)
    for h in HORSES:
        if 'horses' in what or f'h{h["num"]}' in what:
            info.setdefault('horses', {})[str(h['num'])] = horse_sheet(h, out)
            json.dump(info, open(jf, 'w'), ensure_ascii=False, indent=1)
    json.dump(info, open(jf, 'w'), ensure_ascii=False, indent=1)
