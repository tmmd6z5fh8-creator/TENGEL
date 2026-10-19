"""黒板の絵（780×320）：黒板・もや・メモの字・矢印・星・「1着」・木の枠・チョークは前の chalk.py のまま、馬だけ描き直す
   走る競走馬（3Dの馬の形・右向き＝「1着」へ向かう）＋一から作ったたてがみ・しっぽを、
   チョークでぬった形（うすく・こすった筋）＋チョークの外の線＋目と鼻の小さい線で描く
   部品に分けて使える（壁紙の flat/chalk_run.py）：board()＝黒板とも や・shape(H)＝馬の形・ops(H, S)＝チョークで ぬる順の
   （色・こさ）・decor(img)＝メモの字・矢印・星・木の枠・チョーク。HORSES の 1つめが いまの絵の馬
   python3 flat/chalk_banner.py <出力.webp> [形だけの見本PNG]   → いままでと 1バイトもちがわない絵"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
from style2d import *
import horse3d as Hm
from paint import fbm

W, Hh = 780, 320
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
CHALK = '#F2F1E8'                       # チョークの白
BOARD = '#24423A'                       # 黒板
SS = 2                                  # 外の線を描く 倍率


def board():
    """黒板（前の絵と同じ）・消したあとの白いもや → (img, smudge)"""
    rng = np.random.default_rng(191)
    img = np.broadcast_to(hexc(BOARD), (Hh, W, 3)).copy()
    smudge = fbm(Hh, W, 120, 4, seed=2)
    img = img * (0.92 + 0.16 * smudge)[..., None]
    for i in range(30):                                     # 消したあとの白いもや
        x, y = rng.uniform(0, W), rng.uniform(0, Hh)
        img = over(img, hexc('#6E8A80'), soft_circle(Hh, W, x, y, rng.uniform(20, 60), 30) * 0.08)
    return img, smudge


chalk_tex = (fbm(Hh, W, 3, 2, seed=5) > 0.38).astype(np.float32)


def chalk_a(mask, k=0.92):
    """チョークで ぬる こさ（ざらざら）"""
    m = np.clip(mask, 0, 1) * (0.55 + 0.45 * chalk_tex)
    return m * k


def chalk(img, mask, col=CHALK, k=0.92):
    m = np.clip(mask, 0, 1) * (0.55 + 0.45 * chalk_tex)
    return over(img, hexc(col), m * k)


# ---------- 馬（形だけ使う。右向き） ----------
# 1：いまの絵の 走る競走馬（前足を前と うしろへ のばす）
H1 = dict(name='chalk2', box=(292, 44, 612, 258), head_scale=1.08, azim=6, elev=3, hair='run',
          pose=dict(theta=0.0, neck_rot=-38.0, head_ang=-30.0,
                    fore=dict(L=[-100, -40, -30, -18], R=[-132, -28, -150, -170]),
                    hind=dict(L=[-112, -152, -136, -156], R=[-56, -106, -76, -56]),
                    tail=[-172, -162]))
# 2：くらと ゼッケン（1）をつけた競走馬（片方の前足を 高く上げて、もう片方で ふみこむ）
H2 = dict(name='chalk3', box=(305, 50, 625, 262), head_scale=1.08, azim=0, elev=3, hair='race', cloth=True,
          pose=dict(theta=-4.0, neck_rot=-34.0, head_ang=-34.0,
                    fore=dict(L=[-84, -14, -102, -128], R=[-112, -94, -92, -58]),
                    hind=dict(L=[-122, -160, -146, -162], R=[-40, -96, -68, -44]),
                    tail=[-174, -166]))
# 3：立っている馬（首を上げて 前を見る・しっぽは下へ）
H3 = dict(name='chalk4', box=(320, 40, 600, 256), head_scale=1.08, azim=0, elev=3, hair='stand',
          pose=dict(theta=0.0, neck_rot=0.0, head_ang=-62.0, lift=0.0,
                    fore=dict(L=[-130, -94, -94, -64], R=[-118, -86, -86, -56]),
                    hind=dict(L=[-56, -113, -88, -58], R=[-68, -123, -96, -66]),
                    tail=[-118, -100]))
HORSES = [H1, H2, H3]


def _hair_run(R):
    """たてがみ（短く、うしろへなびく）・前髪・しっぽ（うしろへ長く流れる）"""
    hr = np.random.default_rng(23)
    crest = np.asarray(R['crest'], float)
    nC = len(crest)
    locks = []
    for i in range(3, nC - 6, 2):
        p = crest[i]
        tg = crest[min(i + 1, nC - 1)] - crest[i - 1]
        up = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.cos(up) > 0.3:
            up += math.pi
        L = 20 + 12 * math.sin(i / nC * math.pi)
        pts = flow(p, up - 0.9, L, 8, wind=0.35, wind_ang=math.pi + 0.15, rng=hr, wave=1.0, phase=i)
        locks.append(lock_poly(pts, 9, 0.6))
    pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
    fd = (mz - pp) / np.linalg.norm(mz - pp)
    pts = flow(pp + fd * 2, math.atan2(fd[1], fd[0]) - 1.2, 12, 6, wind=0.3, wind_ang=math.pi + 0.2, rng=hr)
    locks.append(lock_poly(pts, 6, 0.6))
    th_ = np.asarray(R['tail'][0], float)
    for k in range(5):
        a0 = math.pi + 0.10 + (k - 2) * 0.07
        L = 96 + (2 - abs(k - 2)) * 12
        pts = flow(th_ + np.array([1.0, 2.0]), a0, L, 16, wind=0.10, wind_ang=math.pi + 0.06, rng=hr, wave=1.3, phase=k * 1.1)
        locks.append(lock_poly(pts, 15 - abs(k - 2) * 2, 0.8))
    return locks


def _hair_race(R):
    """競走馬：たてがみは短く うしろへ・前髪・しっぽは うしろへ まっすぐ 長く（少し下がる）"""
    hr = np.random.default_rng(31)
    crest = np.asarray(R['crest'], float)
    nC = len(crest)
    locks = []
    for i in range(3, nC - 6, 2):
        p = crest[i]
        tg = crest[min(i + 1, nC - 1)] - crest[i - 1]
        up = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.cos(up) > 0.3:
            up += math.pi
        L = 17 + 11 * math.sin(i / nC * math.pi)
        pts = flow(p, up - 1.0, L, 8, wind=0.4, wind_ang=math.pi + 0.08, rng=hr, wave=1.0, phase=i * 0.7)
        locks.append(lock_poly(pts, 8, 0.6))
    pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
    fd = (mz - pp) / np.linalg.norm(mz - pp)
    pts = flow(pp + fd * 2, math.atan2(fd[1], fd[0]) - 1.3, 11, 6, wind=0.35, wind_ang=math.pi + 0.1, rng=hr)
    locks.append(lock_poly(pts, 6, 0.6))
    th_ = np.asarray(R['tail'][0], float)
    for k in range(5):
        a0 = math.pi - 0.02 + (k - 2) * 0.08
        L = 92 + (2 - abs(k - 2)) * 12
        pts = flow(th_ + np.array([1.0, 2.0]), a0, L, 16, wind=0.12, wind_ang=math.pi - 0.16, rng=hr, wave=1.2, phase=k * 0.9 + 0.4)
        locks.append(lock_poly(pts, 15 - abs(k - 2) * 2, 0.8))
    return locks


def _hair_stand(R):
    """立っている馬：たてがみは 首にそって 下へ たれる・前髪・しっぽは 下へ たれて 先が少し うしろへ"""
    hr = np.random.default_rng(47)
    crest = np.asarray(R['crest'], float)
    nC = len(crest)
    locks = []
    for i in range(4, nC - 5, 2):
        p = crest[i]
        tg = crest[min(i + 1, nC - 1)] - crest[i - 1]
        a_t = math.atan2(tg[1], tg[0])                          # 首にそって（のど → 頭）
        L = 18 + 10 * math.sin(i / nC * math.pi)
        pts = flow(p, a_t + math.pi + 0.9, L, 8, wind=0.3, wind_ang=math.pi / 2 + 0.55, rng=hr, wave=0.8, phase=i * 0.8)
        locks.append(lock_poly(pts, 8, 0.6))
    pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
    fd = (mz - pp) / np.linalg.norm(mz - pp)
    pts = flow(pp + fd * 2, math.atan2(fd[1], fd[0]) + 0.5, 11, 6, wind=0.2, wind_ang=math.atan2(fd[1], fd[0]), rng=hr)
    locks.append(lock_poly(pts, 6, 0.6))
    th_ = np.asarray(R['tail'][0], float)
    for k in range(5):
        a0 = math.pi - 0.75 + (k - 2) * 0.10
        L = 88 + (2 - abs(k - 2)) * 10
        pts = flow(th_ + np.array([0.0, 2.0]), a0, L, 16, wind=0.16, wind_ang=math.pi / 2 + 0.12, rng=hr, wave=0.9, phase=k * 1.3)
        locks.append(lock_poly(pts, 15 - abs(k - 2) * 2, 0.8))
    return locks


HAIR = dict(run=_hair_run, race=_hair_race, stand=_hair_stand)


def shape(H):
    """馬の形：R（3Dの目印）・body_a（体）・hair_a（たてがみ・しっぽ）・locks（毛の房）・mask（ぜんぶ）・fd（鼻の向き）"""
    Hm.HEAD_SCALE = H['head_scale']
    e, t = frame_horse(H['pose'], H['box'], W, Hh, facing='right', azim=H['azim'], elev=H['elev'])
    R = render_horse(H['pose'], e, t, 26, W, Hh, ss=2, name=H['name'])
    body_a = np.clip(R['a'], 0, 1)
    locks = HAIR[H['hair']](R)
    hair_a = poly_aa((Hh, W), locks)
    mask = np.clip(np.maximum(body_a, hair_a), 0, 1)
    pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
    fd = (mz - pp) / np.linalg.norm(mz - pp)
    S = dict(H=H, R=R, body_a=body_a, hair_a=hair_a, locks=locks, mask=mask, pp=pp, mz=mz, fd=fd)
    if H.get('cloth'):
        S.update(_cloth(H, R))
        S['mask'] = np.clip(np.maximum(mask, S['saddle_a']), 0, 1)
    return S


def _rounded(pts, r, n=6):
    """多角形の角を まるめる（r：角から はなれる長さ）"""
    pts = [np.asarray(p, float) for p in pts]
    out = []
    for i, p in enumerate(pts):
        a, b = pts[i - 1], pts[(i + 1) % len(pts)]
        da, db = (a - p) / np.linalg.norm(a - p), (b - p) / np.linalg.norm(b - p)
        p0, p1 = p + da * r, p + db * r
        for k in range(n + 1):
            t = k / n
            out.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * p + t * t * p1)
    return np.array(out)


def _cloth(H, R):
    """競走馬のゼッケン（黄色のチョーク・まん中に 黒板の色で「1」）と くら（体の上の 小さな ふくらみ）。3Dの体の上の点を 絵に うつす"""
    th = H['pose']['theta']
    piv = np.array([-0.60, 1.25])
    T = lambda p: Hm.rot2(p, piv, th)
    sc = R['scene']
    P = lambda pts, z: sc.project(np.array([[*T(p), z] for p in pts], float))[0][:, :2]
    cl = P([(0.38, 1.80), (-0.34, 1.80), (-0.36, 1.00), (0.34, 0.99)], 0.29)       # 前上・うしろ上・うしろ下・前下（上は 背中の線で切る）
    cloth = _rounded(cl, 9.0)
    sd = P([(0.30, 1.57), (0.24, 1.70), (0.08, 1.725), (-0.06, 1.71), (-0.16, 1.585)], 0.0)
    saddle_a = poly_aa((Hh, W), [_rounded(sd, 3.0, 4)])
    c = P([(0.0, 1.30)], 0.29)[0]
    hgt = np.linalg.norm(cl[2] - cl[1]) * 0.33
    num = [np.array([c + (-0.20 * hgt, -0.30 * hgt), c + (0.06 * hgt, -0.5 * hgt), c + (0.06 * hgt, 0.5 * hgt)]),
           np.array([c + (-0.16 * hgt, 0.5 * hgt), c + (0.30 * hgt, 0.5 * hgt)])]
    return dict(cloth=cloth, saddle=sd, saddle_a=saddle_a, num=num)


def cloth_parts(S):
    """ゼッケン：体の中だけの形（こさ）・ふちの線（体の外の線に かさならない所だけ：2倍の座標の点の列）"""
    cloth_a = poly_aa((Hh, W), [S['cloth']]) * S['body_a']
    m2 = cv2.resize(cloth_a, (W * SS, Hh * SS), interpolation=cv2.INTER_LINEAR)
    cs, _ = cv2.findContours((m2 > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    inner = cv2.erode((cv2.resize(S['body_a'], (W * SS, Hh * SS), interpolation=cv2.INTER_LINEAR) > 0.5).astype(np.uint8), np.ones((9, 9), np.uint8))
    keep = inner[np.clip(c[:, 1].astype(int), 0, Hh * SS - 1), np.clip(c[:, 0].astype(int), 0, W * SS - 1)] > 0
    # いちばん長い「残す」つながり（輪なので 回して さがす）
    n = len(c)
    start = int(np.argmin(keep)) if not keep.all() else 0
    runs, cur = [], []
    for i in range(n):
        j = (start + i) % n
        if keep[j]:
            cur.append(c[j])
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    edge = np.array(max(runs, key=len), np.float32)
    kk = np.arange(-6, 7); g = np.exp(-(kk / 2.4) ** 2); g /= g.sum()
    edge = np.stack([np.convolve(np.r_[[edge[0, d]] * 6, edge[:, d], [edge[-1, d]] * 6], g, 'valid') for d in (0, 1)], 1)
    return cloth_a, edge


def contours(mask):
    """外の線（2倍で ふちを たどって なめらかに）：[(点の列（2倍の座標）), …]"""
    m2 = cv2.resize(mask, (W * SS, Hh * SS), interpolation=cv2.INTER_LINEAR)
    cs, _ = cv2.findContours((m2 > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < 30 * SS * SS:
            continue
        p = c[:, 0, :].astype(np.float32)
        kk = np.arange(-6, 7); g = np.exp(-(kk / 2.4) ** 2); g /= g.sum()
        ps = np.stack([np.convolve(np.r_[p[-6:, d], p[:, d], p[:6, d]], g, 'valid') for d in (0, 1)], 1)
        out.append(ps)
    return out


def ops(S, smudge):
    """チョークで ぬる順の（名前・色（RGB か 画素ごとの色）・こさ・組）。組：fill＝ぬり（毛の線も）・line＝外の線・cline＝ゼッケンのふち・
       hole＝目（黒板の色）・board＝黒板の上（いまの絵の 鼻の穴のつもりの点）"""
    mask, hair_a, locks, R = S['mask'], S['hair_a'], S['locks'], S['R']
    out = []
    # チョークでぬる（うすく・ななめにこすった筋）
    ang = math.radians(-28)
    u = xx * math.cos(ang) + yy * math.sin(ang)
    streak = 0.5 + 0.5 * np.sin(u * 0.85 + fbm(Hh, W, 18, 3, seed=7) * 7.0)
    fill = mask * (0.52 + 0.22 * streak) * (0.75 + 0.25 * fbm(Hh, W, 40, 3, seed=9))
    if 'cloth' in S:                                        # ゼッケン：白い所を 黄色に（「1」は 黒板の色のまま）
        cloth_a, cedge = cloth_parts(S)
        num = np.zeros((Hh * SS, W * SS), np.float32)
        for q in S['num']:
            cv2.polylines(num, [(q * SS * 16).astype(np.int32)], False, 1.0, 5, cv2.LINE_AA, shift=4)
        num_a = np.clip(cv2.resize(num, (W, Hh), interpolation=cv2.INTER_AREA) * 1.15, 0, 1)
        out.append(('fill', hexc(CHALK), chalk_a(fill * (1 - cloth_a * 0.9) * (1 - num_a), k=0.84), 'fill'))
        out.append(('cloth', hexc('#F6E27F'), chalk_a(cloth_a * (0.66 + 0.2 * streak) * (1 - num_a), k=0.92), 'fill'))
    else:
        out.append(('fill', hexc(CHALK), chalk_a(fill, k=0.84), 'fill'))
    # チョークの外の線（なめらかに・少しかすれる）
    ln2 = np.zeros((Hh * SS, W * SS), np.float32)
    for ps in contours(mask):
        cv2.polylines(ln2, [(ps * 16).astype(np.int32)], True, 1.0, 3, cv2.LINE_AA, shift=4)
    ln = np.clip(cv2.resize(ln2, (W, Hh), interpolation=cv2.INTER_AREA), 0, 1)
    breaks = np.clip(0.55 + 0.6 * fbm(Hh, W, 9, 2, seed=11), 0, 1)              # ところどころかすれる
    out.append(('line', hexc(CHALK), chalk_a(ln * breaks, k=0.98), 'line'))
    if 'cloth' in S:                                        # ゼッケンのふち（黄色のチョーク）
        cl2 = np.zeros((Hh * SS, W * SS), np.float32)
        cv2.polylines(cl2, [(cedge * 16).astype(np.int32)], False, 1.0, 3, cv2.LINE_AA, shift=4)
        cln = np.clip(cv2.resize(cl2, (W, Hh), interpolation=cv2.INTER_AREA), 0, 1)
        out.append(('cline', hexc('#F6E27F'), chalk_a(cln * breaks, k=0.95), 'cline'))
    # 毛の流れ（たてがみ・しっぽの中の線）
    det = np.zeros((Hh * SS, W * SS), np.float32)
    for poly in locks:
        n2 = len(poly) // 2
        mid = (poly[:n2] + poly[::-1][:n2]) / 2
        cv2.polylines(det, [(mid[: int(n2 * 0.85)] * SS * 16).astype(np.int32)], False, 1.0, 3, cv2.LINE_AA, shift=4)
    det = cv2.resize(det, (W, Hh), interpolation=cv2.INTER_AREA)
    out.append(('det', hexc(CHALK), chalk_a(det * hair_a, k=0.75), 'fill'))
    # 目（黒板の色でぬく）・鼻の穴
    ex, ey = np.asarray(R['eye'], float)[:2]
    eye = soft_circle(Hh, W, ex, ey, 2.4, 0.8)
    out.append(('eye', hexc(BOARD) * (0.92 + 0.16 * smudge)[..., None], eye * 0.95, 'hole'))
    pp, mz, fd = S['pp'], S['mz'], S['fd']
    nx, ny = mz[:2] + (pp[:2] - mz[:2]) * 0.10
    nos = np.zeros((Hh * 4, W * 4), np.float32)
    cv2.ellipse(nos, (int(nx * 16), int(ny * 16)), (int(2.6 * 16), int(1.6 * 16)), math.degrees(math.atan2(fd[1], fd[0])), 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
    out.append(('nos', hexc(BOARD), cv2.resize(nos, (W, Hh), interpolation=cv2.INTER_AREA) * 0.8, 'board'))
    return out


def ground(S):
    """地面の線（前の絵と同じく ひづめの下）：(x0, x1, y)"""
    gy_ = max(p[1] for p in S['R']['hooves']) + 6
    return S['H']['box'][0] + 8, S['H']['box'][2] + 8, int(gy_)


def paint(img, S, smudge):
    """黒板に 馬を描く（いまの絵と同じ順）"""
    for name, col, a, grp in ops(S, smudge):
        img = over(img, col, a)
    x0, x1, gy = ground(S)
    cv2.line(img, (x0, gy), (x1, gy), (0.85, 0.85, 0.8), 2, cv2.LINE_AA)
    return img


def decor(img):
    """メモ（チョークの字）・矢印・星・木の枠・チョーク（前の絵と同じ）"""
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    F = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    d.text((26, 30), '本日の◎', font=ImageFont.truetype(F, 34), fill=(246, 226, 127))
    d.text((30, 86), '①→②→③', font=ImageFont.truetype(F, 24), fill=(242, 241, 232))
    d.text((30, 128), 'がんばれ！', font=ImageFont.truetype(F, 24), fill=(244, 166, 192))
    d.ellipse((640, 40, 740, 140), outline=(242, 241, 232), width=4)
    d.text((690, 90), '1着', font=ImageFont.truetype(F, 30), fill=(246, 226, 127), anchor='mm')
    txt = np.asarray(pil).astype(np.float32) / 255
    diff = np.abs(txt - img).max(-1) > 0.05
    img = np.where(diff[..., None], img * (1 - 0.0) + (txt - img) * (0.55 + 0.45 * chalk_tex)[..., None], img)
    st = np.zeros((Hh, W), np.float32)
    cv2.arrowedLine(st, (210 * 4, 200 * 4), (290 * 4, 160 * 4), 1.0, 12, cv2.LINE_AA, shift=2, tipLength=0.25)
    for (x, y, s) in [(120, 230, 14), (660, 220, 12), (230, 60, 10)]:
        pts = np.array([(x + math.cos(-math.pi / 2 + j * math.pi * 4 / 5) * s, y + math.sin(-math.pi / 2 + j * math.pi * 4 / 5) * s) for j in range(6)])
        cv2.polylines(st, [np.round(pts * 16).astype(np.int32)], False, 1.0, 2, cv2.LINE_AA, shift=4)
    img = chalk(img, st, '#F2F1E8', 0.85)
    img = over(img, hexc('#8A5A2B'), np.clip((yy - 300) / 1.2 + .5, 0, 1))
    img = over(img, hexc('#6E4520'), np.clip((yy - 300) / 1.2 + .5, 0, 1) * np.clip((yy - 312), 0, 1))
    for (x, c) in [(520, '#F2F1E8'), (560, '#F6E27F'), (590, '#F4A6C0')]:
        m = np.zeros((Hh, W), np.float32)
        cv2.rectangle(m, (x * 4, 292 * 4), ((x + 26) * 4, 300 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
        img = over(img, hexc(c), m)
    return img


if __name__ == '__main__':
    out = sys.argv[1]
    img, smudge = board()
    S = shape(H1)
    img = paint(img, S, smudge)
    img = decor(img)
    save_webp(np.clip(img, 0, 1), out)
    if len(sys.argv) > 2:
        cv2.imwrite(sys.argv[2], (S['mask'] * 255).astype(np.uint8))
    print(out)
