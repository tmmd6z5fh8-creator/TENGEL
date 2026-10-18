"""海の壁紙の動き（まさちゃんの指定「常に馬が走っている・背景が移動する、同じ模様をリピートする」）：
   - 馬：いまの絵と同じ馬（horse_flat・海の色と飾り・同じカメラ）を、ギャロップの1回分（N_FRAMES コマ）で描いて、横に並べた1枚にする（sea_horse.webp・すき通し）。
     足の動き：4本の足が順に地面について（うしろの奥 → うしろの手前 → 前の奥 → 前の手前）、最後は4本とも宙に浮く。体は前後にゆれ、首と頭も合わせて動く。しっぽは なびく
     コマごとに、地面についているひづめが砂の上にくるように上下をそろえる・ついているひづめから水しぶき・影はいつも同じ
   - 背景：いまの絵と同じ空・海・砂浜を、横につなげても切れ目がないように描き直す（3まい：空と雲とかもめ・海・波打ちぎわと砂）。
     ページでは、ちがう速さで横に流してくり返す（遠いほどゆっくり：sea_wall.py）
   python3 flat/sea_run.py <出力フォルダ>  → sea_sky.webp・sea_sea.webp・sea_shore.webp・sea_horse.webp・sea_run.json（大きさ・置き場所）
   （sdfr がいる。1コマ約10秒）"""
import sys, os, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
from style2d import grad_v, over, hexc
import cute_themes as C
from horse_flat import draw_horse, POSES, TAILS
from cute_horse import circ, V, f2

W, Hh = 780, 320                 # 絵の画素（画面の2倍）
N_FRAMES = 10                    # ギャロップ1回のコマ数
SKY_Y1, SEA_Y0, SEA_Y1, SHORE_Y0 = 148, 146, 250, 196     # 帯の切れ目（空 0〜148・海 146〜250・砂浜 196〜320）
HF_GROUND = 262.1                # 地面についているひづめの点の高さ（いまの絵の馬と同じ）
SHADOW = (416.6, 268.0, 150.0, 6.0)   # 影（いまの絵と同じ所・大きさ）

# 足の動き：(その足の位相, [4つの骨の向き°])。0＝ひづめが地面につく・0.30＝離れる。あいだは なめらかにつなぐ（くり返し）
F_KEYS = [(0.00, [-112, -74, -76, -52]), (0.15, [-125, -92, -92, -62]), (0.30, [-135, -118, -122, -110]),
          (0.50, [-122, -22, -145, -172]), (0.78, [-66, -28, -38, -22]), (0.92, [-95, -55, -60, -40])]
H_KEYS = [(0.00, [-62, -108, -80, -55]), (0.15, [-68, -122, -95, -64]), (0.30, [-116, -154, -128, -148]),
          (0.52, [-80, -150, -60, -30]), (0.78, [-60, -104, -74, -48]), (0.92, [-60, -106, -78, -52])]
STANCE = 0.27                    # 地面についている（高さをそろえる・しぶき）：離れる瞬間（0.30）は入れない（足がうしろへのびてひづめが高い）
# 足ごとの遅れ（右向き：手前＝L・奥＝R）：うしろの奥 → うしろの手前 → 前の奥 → 前の手前。0.70〜1.00 は4本とも宙
LEG_OFF = dict(HR=0.00, HL=0.10, FR=0.30, FL=0.40)
HOOF_ORDER = ('FL', 'FR', 'HL', 'HR')          # draw_horse の marks['hooves'] の順


def ease(t):
    return t * t * (3 - 2 * t)


def leg_at(keys, p):
    p %= 1.0
    ks = keys + [(keys[0][0] + 1.0, keys[0][1])]
    for (p0, a0), (p1, a1) in zip(ks, ks[1:]):
        if p0 <= p <= p1:
            t = ease((p - p0) / (p1 - p0))
            return [round(x0 + (x1 - x0) * t, 2) for x0, x1 in zip(a0, a1)]
    return keys[0][1]


def pose_at(g):
    """ギャロップの位相 g（0〜1）の形（horse_flat の POSES と同じ形の dict）"""
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - LEG_OFF[k])
    w = 2 * math.pi
    tail0 = TAILS['fly']
    wave = math.sin(w * g)
    tufts = [((a[0], a[1] + .04 * wave * (i + 1) / 3), (b[0], b[1] + .07 * wave * (i + 1) / 3), (c[0], c[1] + .10 * math.sin(w * g - .8) * (i + 1) / 3), wm)
             for i, (a, b, c, wm) in enumerate(tail0)]
    return dict(theta=round(3.5 + 3.5 * math.cos(w * (g - 0.15)), 2), neck_rot=round(-22 + 5 * math.cos(w * (g - 0.55)), 2),
                head_ang=round(-46 + 3 * math.sin(w * g), 2), tail=[-160, -150], tail_kind='fly', tail_tufts=tufts,
                fore_near=leg('FL'), fore_far=leg('FR'), hind_near=leg('HL'), hind_far=leg('HR'))


def stance_legs(g):
    return [k for k in HOOF_ORDER if ((g - LEG_OFF[k]) % 1.0) < STANCE]


def splash(m, legs, seed):
    """地面についているひづめから、うしろへ水しぶき（いまの絵の しぶき と同じ白い粒・しずく）"""
    rng = np.random.default_rng(seed)
    p = m['p1u']
    k = p / 92.0
    front, back = [], []
    for key in legs:
        hx, hy = m['hooves'][HOOF_ORDER.index(key)]
        g0 = hy + 2.9
        for i in range(12):
            ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.45)
            d = rng.uniform(5, 26) * k
            x, y = hx + math.cos(ang) * d * 1.3, g0 - 1 + math.sin(ang) * d * 0.8
            front.append(circ(V(x, y), rng.uniform(1.2, 2.8) * k, '#FFFFFF', 'fill-opacity=".92"'))
        back.append(f'<ellipse cx="{f2(hx - 4 * k)}" cy="{f2(g0 + 1)}" rx="{f2(15 * k)}" ry="{f2(4 * k)}" fill="#FFFFFF" fill-opacity=".85"/>')
    return front, back


def render_horse_frames(out):
    sp0 = dict(C.SPOTS['sea'])
    sp0['cam_out'] = []
    draw_horse(sp0, C.PALS['sea'], W, Hh, acc=C.acc_sea, number='1', name='sea_ref')     # いまの絵と同じカメラを決める
    cam = sp0['cam_out']
    frames = []
    for f in range(N_FRAMES):
        g = f / N_FRAMES
        legs = stance_legs(g)

        def acc(m, legs=legs, f=f):
            d = C.acc_sea(m)
            d['front'], d['back'] = splash(m, legs, 700 + f)
            return d
        sp = dict(sp0, pose=pose_at(g), cam=cam)
        sp.pop('cam_out', None)
        rgb, a, m = draw_horse(sp, C.PALS['sea'], W, Hh, acc=acc, number='1', name=f'sea_run{f}')
        ys = [m['hooves'][HOOF_ORDER.index(k)][1] for k in legs]
        dy = HF_GROUND - max(ys) if ys else None
        frames.append(dict(rgb=rgb, a=a, dy=dy, legs=legs))
        print('frame', f, 'stance', legs, 'dy', None if dy is None else round(dy, 1), flush=True)
    # 宙に浮いているコマ：前に地面についていたコマと、次に地面につくコマの高さを結んで、まん中がいちばん高い山なり（LIFT）
    n = len(frames)
    LIFT = 6.0
    for i, fr in enumerate(frames):
        if fr['dy'] is None:
            jp = next(j for j in range(1, n) if frames[(i - j) % n]['legs'])
            jn = next(j for j in range(1, n) if frames[(i + j) % n]['legs'])
            t = jp / (jp + jn)
            prev, nxt = frames[(i - jp) % n]['dy'], frames[(i + jn) % n]['dy']
            fr['dy_air'] = prev + (nxt - prev) * t - LIFT * 4 * t * (1 - t)
    for fr in frames:
        if fr['dy'] is None:
            fr['dy'] = fr.pop('dy_air')
    # 影（いつも同じ）＋ 馬（上下をそろえる）→ 横に並べる
    cells = []
    for fr in frames:
        M = np.float32([[1, 0, 0], [0, 1, fr['dy']]])
        rgb = cv2.warpAffine(fr['rgb'] * fr['a'][..., None], M, (W, Hh), flags=cv2.INTER_LINEAR)
        a = cv2.warpAffine(fr['a'], M, (W, Hh), flags=cv2.INTER_LINEAR)
        sm = np.zeros((Hh * 4, W * 4), np.float32)
        cx, cy, rx, ry = SHADOW
        cv2.ellipse(sm, (int(cx * 4), int(cy * 4)), (int(rx * 4), int(ry * 4)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        sm = cv2.GaussianBlur(cv2.resize(sm, (W, Hh), interpolation=cv2.INTER_AREA), (0, 0), 3.4) * 0.22
        sc = hexc('#8A6A3A')
        pre = rgb + sc[None, None, :] * (sm * (1 - a))[..., None]
        A = a + sm * (1 - a)
        cells.append((pre, A))
    allA = np.max([A for _, A in cells], axis=0)
    ys, xs = np.nonzero(allA > 0.004)
    x0, x1 = max(0, xs.min() - 4), min(W, xs.max() + 5)
    y0, y1 = max(0, ys.min() - 4), min(Hh, ys.max() + 5)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2                 # 画面の画素（半分）にそろえる
    x1, y1 = x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2
    cw, ch = x1 - x0, y1 - y0
    sheet = np.zeros((ch, cw * n, 4), np.float32)
    for i, (pre, A) in enumerate(cells):
        rgb = np.where(A[..., None] > 1e-4, pre / np.maximum(A, 1e-4)[..., None], 0)
        sheet[:, i * cw:(i + 1) * cw, :3] = rgb[y0:y1, x0:x1]
        sheet[:, i * cw:(i + 1) * cw, 3] = A[y0:y1, x0:x1]
    u8 = (np.clip(sheet, 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(f'{out}/sea_horse.webp', cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_WEBP_QUALITY, 90])
    return dict(frames=n, cell=[int(cw), int(ch)], at=[int(x0), int(y0)], dy=[round(float(fr['dy']), 2) for fr in frames], stance=[fr['legs'] for fr in frames])


# ---------------- 背景（横につなげても切れ目がない） ----------------
def wrap_x(xs, w=W, pad=60):
    """くり返しの左右のはしにかかる所は、ずらしたものも描く"""
    out = []
    for x in xs:
        for dx in (-w, 0, w):
            if -pad <= x + dx <= w + pad:
                out.append(x + dx)
    return out


def backgrounds(out):
    rng = np.random.default_rng(31)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    base = grad_v(Hh, W, [(0, '#3FA9EC'), (0.45, '#9AD8F6'), (0.47, '#1E86CF'), (0.7, '#46B7E2'), (0.72, '#F6E3B8'), (1, '#EBCB8E')])
    # 空：雲（いまの絵と同じ数と場所の決め方・はしは反対がわにも）・かもめ
    sky = base.copy()
    cl = np.zeros((Hh * 4, W * 4), np.float32)
    for cx, cy, n in [(110, 46, 7), (640, 36, 8), (430, 70, 4)]:
        for i in range(n):
            x = cx + rng.uniform(-50, 50); y = cy + rng.uniform(-10, 8); r = rng.uniform(14, 26)
            for xw in wrap_x([x]):
                cv2.circle(cl, (int(xw * 16), int(y * 16)), int(r * 16), 1.0, -1, cv2.LINE_AA, shift=2)
    cl = cv2.resize(np.clip(cl, 0, 1), (W, Hh), interpolation=cv2.INTER_AREA)
    sky = over(sky, hexc('#D9EEFA'), np.roll(cl, 4, 0) * 0.9)
    sky = over(sky, hexc('#FFFFFF'), cl)
    for (x, y, s) in [(150, 96, 9), (190, 80, 7), (700, 110, 8)]:
        m = np.zeros((Hh * 4, W * 4), np.uint8)
        for xw in wrap_x([x], pad=12):
            pts = np.array([(xw - s, y), (xw - s * .45, y - s * .5), (xw, y), (xw + s * .45, y - s * .5), (xw + s, y)])
            cv2.polylines(m, [np.round(pts * 64).astype(np.int32)], False, 255, 5, cv2.LINE_AA, shift=4)
        sky = over(sky, hexc('#2C5672'), cv2.resize(m, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255)
    # 海：きらめき・波の線
    sea = base.copy()
    hz = 0.46 * Hh
    for i in range(70):
        y = rng.uniform(hz + 4, 0.71 * Hh); x = rng.uniform(0, W); L = rng.uniform(10, 40) * (y - hz) / 60
        for xw in wrap_x([x], pad=45):
            cv2.line(sea, (int(xw * 16), int(y * 16)), (int((xw + L) * 16), int(y * 16)), (1, 1, 1), 1, cv2.LINE_AA, shift=4)
    sea = np.clip(sea, 0, 1)
    # 波打ちぎわ（ぬれた砂・白い泡）と砂：くり返しの幅で ちょうど1周する波（2・5・4・14回）
    k2 = 2 * math.pi / W
    shore = 0.715 * Hh + 5 * np.sin(xx * k2 * 2) + 3 * np.sin(xx * k2 * 5 + 1)
    land = np.clip((yy - shore) / 2 + .5, 0, 1)                                    # 波打ちぎわより下＝砂
    wet = land * np.clip((shore + 22 - yy) / 6, 0, 1)
    foam = np.exp(-((yy - shore) / 3.0) ** 2)
    foam2 = np.exp(-((yy - (shore - 14 + 3 * np.sin(xx * k2 * 4))) / 2.0) ** 2) * (np.sin(xx * k2 * 14) > -0.3)
    sand = base.copy()
    sand = over(sand, hexc('#D9BC86'), wet * 0.8)
    sh_rgb = sand
    sh_a = land
    sh_rgb, sh_a = over_a(sh_rgb, sh_a, hexc('#FFFFFF'), foam * 0.95)
    sh_rgb, sh_a = over_a(sh_rgb, sh_a, hexc('#E8F8FF'), foam2 * 0.7)
    save = lambda name, img: cv2.imwrite(f'{out}/{name}', cv2.cvtColor((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_WEBP_QUALITY, 88])
    save('sea_sky.webp', sky[:SKY_Y1])
    save('sea_sea.webp', sea[SEA_Y0:SEA_Y1])
    rgba = np.dstack([sh_rgb, sh_a])[SHORE_Y0:]
    cv2.imwrite(f'{out}/sea_shore.webp', cv2.cvtColor((np.clip(rgba, 0, 1) * 255 + .5).astype(np.uint8), cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_WEBP_QUALITY, 88])
    return dict(sky=[0, SKY_Y1], sea=[SEA_Y0, SEA_Y1], shore=[SHORE_Y0, Hh])


def over_a(rgb, a, col, al):
    """すき通しのある絵に、色をアルファ al で重ねる"""
    al = np.clip(al, 0, 1)
    na = a + al * (1 - a)
    nrgb = (rgb * (a * (1 - al))[..., None] + col[None, None, :] * al[..., None]) / np.maximum(na, 1e-4)[..., None]
    return nrgb, na


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    info = dict(size=[W, Hh], bands=backgrounds(out))
    if '--bg-only' not in sys.argv:
        info['horse'] = render_horse_frames(out)
    json.dump(info, open(f'{out}/sea_run.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False))
