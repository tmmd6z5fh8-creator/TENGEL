"""オリジナルの3Dの馬（骨格＋筋肉のかたまり）。右(+x)向き・左半身(+z)がカメラ側。単位はメートル"""
import math
import numpy as np
from h3d import nrm, basis


def adir(deg):
    r = math.radians(deg)
    return np.array([math.cos(r), math.sin(r)])


def bez(P, t):
    P = np.asarray(P, float)
    t = np.asarray(t, float)[..., None]
    return ((1 - t) ** 3) * P[0] + 3 * ((1 - t) ** 2) * t * P[1] + 3 * (1 - t) * t * t * P[2] + t ** 3 * P[3]


def rot2(p, c, deg):
    r = math.radians(deg)
    p = np.asarray(p, float) - c
    return c + np.array([p[0] * math.cos(r) - p[1] * math.sin(r), p[0] * math.sin(r) + p[1] * math.cos(r)])


def v3(p2, z=0.0):
    return np.array([p2[0], p2[1], z], float)


STAND = dict(
    theta=0.0, neck_rot=0.0, head_ang=-62.0, lift=0.0,
    fore=dict(L=[-125, -90, -90, -60], R=[-125, -90, -90, -60]),     # 上腕・前腕・管・つなぎ（世界の角度）
    hind=dict(L=[-62, -118, -92, -62], R=[-62, -118, -92, -62]),     # 大腿・すね・管・つなぎ
    tail=[-118, -100],
)


# 首を まげる時（pose の neck_bend・度／neck_len・のばす倍率）の 点ごとの まわし方と のばし方（たてがみ側・のど側の 4つの点：根元 → うなじ）。
# neck_bend が ない／0 なら いままでと 1バイトも ちがわない（草を食べる馬：flat/step_run.py）
NECK_BEND_W = ((0.0, 0.75, 0.95, 1.0), (0.0, 0.65, 0.9, 1.0))


# 首を 横に まげる 時（pose の neck_yaw・度：＋で 手前（＋z・カメラの がわ）へ まげて 頭を うしろへ／head_yaw：うなじで さらに 回す 度）。
# 首の 根もと（nb）を 通る たての 軸の まわりに、根もとから うなじへ だんだん 大きく 回す（重み t^NECK_YAW_P）。頭は うなじを 通る たての 軸で
# head_yaw 回して から、首の 先と いっしょに 回す。neck_yaw が ない／0 なら いままでと 1バイトも ちがわない（第4.96版・七夕の 首だけ 振り返る コマ）
NECK_YAW_P = 1.3


def yaw_R(deg):
    """たての 軸（y）の まわりに 回す（＋x を ＋z へ）"""
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return np.array([[c, 0.0, -s], [0.0, 1.0, 0.0], [s, 0.0, c]])


def neck_xf(Y, p, t):
    """首の t（0＝根もと〜1＝うなじ）の 所の 点 p（3D）を まげた 所へ"""
    w = float(np.clip(t, 0.0, 1.0)) ** Y['w']
    return Y['piv'] + yaw_R(Y['n'] * w) @ (np.asarray(p, float) - Y['piv'])


def head_xf(Y, p):
    """頭の 点 p（3D）を まげた 所へ（うなじで head_yaw → 首の 先と いっしょに）"""
    q = Y['hp'] + yaw_R(Y['h']) @ (np.asarray(p, float) - Y['hp'])
    return neck_xf(Y, q, 1.0)


def rot_between(a, b):
    """向き a を 向き b へ 回す いちばん 小さい 回転"""
    a, b = nrm(a), nrm(b)
    k = np.cross(a, b)
    sn, cs = np.linalg.norm(k), float(np.dot(a, b))
    if sn < 1e-9:
        return np.eye(3)
    k = k / sn
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + K * sn + K @ K * (1 - cs)


def neck_Q(S, Y, t, eps=0.01):
    """首の t の 所の 形の 向きの 回転（まげた 首の 線の 向きに そろえる）"""
    C = lambda tt: v3((bez(S['crest'], tt) + bez(S['throat'], tt)) / 2)
    t0, t1 = max(0.0, t - eps), min(1.0, t + eps)
    Tu = nrm(C(t1) - C(t0))
    Tb = nrm(neck_xf(Y, C(t1), t1) - neck_xf(Y, C(t0), t0))
    R = yaw_R(Y['n'] * float(np.clip(t, 0.0, 1.0)) ** Y['w'])
    return rot_between(R @ Tu, Tb) @ R


def neck_pts3(S, key, ts):
    """首の 線（'crest'・'throat'）の 点（3D・まげた 所）"""
    P = bez(S[key], np.asarray(ts, float))
    Y = S.get('yaw')
    if not Y:
        return np.array([v3(p) for p in P])
    return np.array([neck_xf(Y, v3(p), t) for p, t in zip(P, ts)])


class _YawSc:
    """首を 横に まげる 時の sc の かわり：形の 位置と 向きを まげた 所へ（mode：首の t・'head'＝頭）"""

    def __init__(self, sc, S, Y):
        self.sc, self.S, self.Y, self.mode = sc, S, Y, 0.0

    def _p(self, p):
        return head_xf(self.Y, p) if self.mode == 'head' else neck_xf(self.Y, p, self.mode)

    def _Q(self):
        return yaw_R(self.Y['n'] + self.Y['h']) if self.mode == 'head' else neck_Q(self.S, self.Y, self.mode)

    def ell(self, c, radii, R=None, **kw):
        R = np.eye(3) if R is None else np.asarray(R, float)
        self.sc.ell(self._p(c), radii, R @ self._Q().T, **kw)

    def rbox(self, c, half, rnd, R=None, **kw):
        R = np.eye(3) if R is None else np.asarray(R, float)
        self.sc.rbox(self._p(c), half, rnd, R @ self._Q().T, **kw)

    def sph(self, c, r, **kw):
        self.sc.sph(self._p(c), r, **kw)

    def rcone(self, a, b, ra, rb, **kw):
        self.sc.rcone(self._p(a), self._p(b), ra, rb, **kw)

    def __getattr__(self, k):
        return getattr(self.sc, k)


def skeleton(pose):
    th = pose['theta']
    piv = np.array([-0.60, 1.25])
    T = lambda p: rot2(p, piv, th)
    S = {}
    # 胴の目印
    for k, p in dict(withers=(0.40, 1.62), back=(0.0, 1.53), loin=(-0.32, 1.56), croup=(-0.55, 1.61), tailhead=(-0.86, 1.52),
                     buttock=(-0.93, 1.30), hip=(-0.60, 1.25), sternum=(0.30, 0.86), chest=(0.66, 1.10), scap=(0.34, 1.52)).items():
        S[k] = T(p)
    # 首：たてがみ側（上）とのど側（下）の線
    crest = [(0.34, 1.60), (0.54, 1.82), (0.76, 2.10), (0.95, 2.16)]
    throat = [(0.70, 1.22), (0.86, 1.46), (0.93, 1.76), (1.05, 1.93)]
    nb = T((0.52, 1.40))
    nr = pose['neck_rot']
    crest = [rot2(T(p), nb, nr) for p in crest]
    throat = [rot2(T(p), nb, nr) for p in throat]
    bend = pose.get('neck_bend', 0.0)
    if bend:                                    # 首を まげる（草を食べる：き甲と 胸の根元は そのまま、先ほど 大きく まわす。NECK_BEND_W）
        L = pose.get('neck_len', 1.0)           # 首を少し のばす（首が 短いので、のばさないと 口が 地面に とどかない）
        crest = [nb + (rot2(p, nb, bend * w) - nb) * (1 + (L - 1) * w) for p, w in zip(crest, NECK_BEND_W[0])]
        throat = [nb + (rot2(p, nb, bend * w) - nb) * (1 + (L - 1) * w) for p, w in zip(throat, NECK_BEND_W[1])]
    S['crest'] = np.array(crest)
    S['throat'] = np.array(throat)
    S['poll'] = crest[3] + (adir(th + nr + bend + 40) * 0.03)
    S['head_ang'] = pose['head_ang']
    yaw = pose.get('neck_yaw', 0.0)
    if yaw:                                     # 首を 横に まげる（第4.96版・七夕の 振り返り。なければ いままでと 1バイトも ちがわない）
        S['yaw'] = dict(n=float(yaw), h=float(pose.get('head_yaw', 0.0)), piv=np.array([nb[0], 0.0, 0.0]),
                        hp=np.array([S['poll'][0], 0.0, 0.0]), w=float(pose.get('yaw_pow', NECK_YAW_P)))
    # 前足
    # cannon_ext：足ごとに 管（ひざ〜球節）を のばす m（{'FL': …}）。ない／0 なら いままでと 1バイトも ちがわない
    #   （第4.87版・まさちゃん「青丸の脚が地面から浮いてしまってるから直して！」：立つ馬の 前足の ひづめが うしろ足より 7〜9画素 上に 浮いていた。
    #    ひざから 上は かえないので、頭や 首の コマ（ハロウィン・ホワイトデー）は そのまま 重なる）
    cext = pose.get('cannon_ext') or {}
    for side, z in (('L', 1), ('R', -1)):
        a = pose['fore'][side]
        s0 = S['scap']
        ps = s0 + adir(th - 58) * 0.42
        el = ps + adir(a[0]) * 0.30
        kn = el + adir(a[1]) * 0.41
        ft = kn + adir(a[2]) * (0.28 + cext.get('F' + side, 0.0))
        co = ft + adir(a[3]) * 0.13
        hf = co + adir(a[3] - 30) * 0.085
        S['F' + side] = dict(s0=s0, ps=ps, el=el, kn=kn, ft=ft, co=co, hf=hf, z=z, ang=a)
    for side, z in (('L', 1), ('R', -1)):
        a = pose['hind'][side]
        hj = S['hip']
        st = hj + adir(a[0]) * 0.43
        hk = st + adir(a[1]) * 0.47
        ft = hk + adir(a[2]) * (0.29 + cext.get('H' + side, 0.0))
        co = ft + adir(a[3]) * 0.13
        hf = co + adir(a[3] - 28) * 0.09
        S['H' + side] = dict(hj=hj, st=st, hk=hk, ft=ft, co=co, hf=hf, z=z, ang=a)
    # 地面の高さ：いちばん低いひづめ
    low = min(S[k]['hf'][1] for k in ('FL', 'FR', 'HL', 'HR')) - 0.035
    S['ground'] = low
    return S


HEAD_SCALE = 1.1


def ear_vec(U3, V3, z, rot=0.0):
    """耳の 向き（U3：頭の向き・V3：ひたいの向き・z：左右 ±1）。rot：耳を 前へ 向ける 角度（度。＋＝前へ・−＝うしろへ ふせる）。
       rot が 0 なら いままでと 1バイトも ちがわない（pose の ear_rot：バレンタイン・ホワイトデーの 動く壁紙 flat/couple_run.py）"""
    if not rot:
        return nrm(-U3 * 0.9 + V3 * 0.25 + np.array([0, 0, 0.30 * z]))
    a = math.atan2(0.25, -0.9) - math.radians(rot)
    r = math.hypot(0.9, 0.25)
    return nrm(U3 * (r * math.cos(a)) + V3 * (r * math.sin(a)) + np.array([0, 0, 0.30 * z]))


def head_pt(S, s, w, z=0.0):
    u = adir(S['head_ang'])
    vv = np.array([-u[1], u[0]])
    p = S['poll'] + (u * s + vv * w) * HEAD_SCALE
    if S.get('yaw'):                            # 首を 横に まげた 時は 頭も（head_xf）
        return head_xf(S['yaw'], np.array([p[0], p[1], z * HEAD_SCALE]))
    return np.array([p[0], p[1], z * HEAD_SCALE])


def build(sc, pose, mats=None, detail=1.0, parts='all'):
    """形を sc に出す。mats: body / neck / hoof / eye"""
    M = dict(body=1, neck=1, hoof=1, eye=5, head=1)
    if mats: M.update(mats)
    S = skeleton(pose)
    B, N, HO, EY, HD = M['body'], M['neck'], M['hoof'], M['eye'], M['head']
    th = pose['theta']
    piv = np.array([-0.60, 1.25])
    T = lambda p: rot2(p, piv, th)
    fx = basis(v3(adir(th)), (0, 1, 0))          # 胴の向き

    def ellT(c, r, k=0.12, mat=B, tilt=0.0, z=0.0):
        sc.ell(v3(T(c), z), r, basis(v3(adir(th + tilt)), (0, 1, 0)), k=k, mat=mat)

    if parts != 'all':
        return _bust(sc, pose, S, M, T, th)
    # ---------- 胴 ----------
    ellT((0.05, 1.22), (0.56, 0.36, 0.30), k=0.0)            # あばら
    ellT((0.40, 1.16), (0.30, 0.32, 0.27), k=0.14)           # 胸
    ellT((0.36, 1.46), (0.25, 0.16, 0.14), k=0.14, tilt=-18)  # き甲
    ellT((-0.20, 1.40), (0.46, 0.17, 0.26), k=0.14)          # 背中
    ellT((-0.04, 1.05), (0.48, 0.20, 0.29), k=0.14)          # おなか
    ellT((-0.60, 1.37), (0.34, 0.26, 0.27), k=0.14, tilt=-8)  # しり（腰）
    for z in (1, -1):
        ellT((-0.77, 1.25), (0.19, 0.28, 0.16), k=0.12, z=0.12 * z)   # しりの丸み
        ellT((-0.52, 1.44), (0.28, 0.20, 0.15), k=0.12, z=0.15 * z, tilt=-10)  # 腰の筋肉
        ellT((0.60, 1.04), (0.11, 0.17, 0.10), k=0.12, z=0.12 * z, tilt=10)   # 胸の筋肉
    # しっぽの根元
    ta = S['tailhead']
    t1 = ta + adir(pose['tail'][0]) * 0.20
    t2 = t1 + adir(pose['tail'][1]) * 0.16
    sc.rcone(v3(ta), v3(t1), 0.075, 0.055, k=0.06, mat=B)
    sc.rcone(v3(t1), v3(t2), 0.055, 0.04, k=0.03, mat=B)
    S['tail_pts'] = [ta, t1, t2]

    _neck_head(sc, pose, S, M)

    # ---------- 前足 ----------
    spread = pose.get('fore_spread', 1.0)          # 1より大きいと、ひざから下を外へ広げる（ボードを持つ形など）
    LDZ = pose.get('leg_dz') or {}                 # 足ごとに ひじ（後ろ足は ひざ）から 下を 横へ（ひづめで dz・m）。ない／0 なら いままでと 1バイトも ちがわない（ノーマルど的中：カーブで ひづめを すべらせない）
    for side in ('R', 'L'):
        F = S['F' + side]
        z = F['z']
        ldz = LDZ.get('F' + side, 0.0)
        zs = 0.20 * z
        zl = 0.155 * z
        s0, ps, el, kn, ft, co, hf = (F[k] for k in ('s0', 'ps', 'el', 'kn', 'ft', 'co', 'hf'))
        # 肩
        mid = s0 * 0.5 + ps * 0.5 + adir(th + 180) * 0.03
        sc.ell(v3(mid, 0.165 * z), (0.27, 0.13, 0.075), basis(v3(ps - s0), (0, 0, 1)), k=0.16, mat=B)
        # 上腕＋上腕三頭筋
        sc.rcone(v3(ps, zl + 0.02 * z), v3(el, zl), 0.11, 0.085, k=0.08, mat=B)
        dpe = nrm(el - ps)
        back = np.array([-dpe[1], dpe[0]]) if dpe[0] * 0 + 1 else None
        # 上腕の後ろ側（ひじの上の大きな筋肉）
        perp = np.array([dpe[1], -dpe[0]])
        if perp[0] > 0: perp = -perp
        tc = ps * 0.42 + el * 0.58 + perp * 0.07
        sc.ell(v3(tc, zl * 0.92), (0.16, 0.10, 0.085), basis(v3(el - ps), (0, 0, 1)), k=0.10, mat=B)
        # 前腕
        zk = zl * 0.93 * (1 + (spread - 1) * 0.55)
        zf = zl * 0.9 * (1 + (spread - 1) * 0.9)
        dfk = nrm(kn - el)
        sc.rcone(v3(el, zl), v3(kn, zk + ldz * .45), 0.085, 0.048, k=0.05, mat=B)
        fwd = np.array([-dfk[1], dfk[0]]) if True else None
        # 前腕の前の筋肉
        fm = el + (kn - el) * 0.32
        side_f = np.array([dfk[1], -dfk[0]])
        if np.dot(side_f, adir(F['ang'][1] + 90)) < 0: side_f = -side_f
        sc.ell(v3(fm + adir(F['ang'][1] + 90) * 0.018, zl + ldz * .144), (0.16, 0.07, 0.068), basis(v3(kn - el), (0, 0, 1)), k=0.05, mat=B)
        # ひざ
        sc.ell(v3(kn, zk + ldz * .45), (0.062, 0.058, 0.052), basis(v3(ft - kn), (0, 0, 1)), k=0.04, mat=B)
        # 管＋けん
        dkf = nrm(ft - kn)
        bk = adir(F['ang'][2] - 90)
        sc.rcone(v3(kn, zk + ldz * .45), v3(ft, zf + ldz * .76), 0.044, 0.04, k=0.03, mat=B)
        sc.rcone(v3(kn + bk * 0.026 + dkf * 0.05, zk + ldz * .5), v3(ft + bk * 0.022 - dkf * 0.03, zf + ldz * .73), 0.028, 0.026, k=0.02, mat=B)
        # 球節
        sc.ell(v3(ft + bk * 0.008, zf + ldz * .76), (0.06, 0.062, 0.054), basis(v3(dkf), (0, 0, 1)), k=0.03, mat=B)
        # つなぎ
        sc.rcone(v3(ft, zf + ldz * .76), v3(co, zf + ldz * .91), 0.045, 0.05, k=0.03, mat=B)
        # ひづめ
        sc.ccone(v3(co, zf + ldz * .91), v3(hf, zf + ldz), 0.056, 0.074, rnd=0.008, side=v3(adir(F['ang'][3] - 30 + 90)), k=0.012, mat=HO)

    # ---------- 後ろ足 ----------
    for side in ('R', 'L'):
        Hh = S['H' + side]
        z = Hh['z']
        zl = 0.165 * z
        ldz = LDZ.get('H' + side, 0.0)
        hj, st, hk, ft, co, hf = (Hh[k] for k in ('hj', 'st', 'hk', 'ft', 'co', 'hf'))
        # もも
        sc.rcone(v3(hj, 0.17 * z), v3(st, zl), 0.16, 0.105, k=0.10, mat=B)
        # ももの後ろ（しりから下へ）
        pb = S['buttock']
        g0 = st + (hk - st) * 0.38 + adir(Hh['ang'][1] - 90) * 0.06
        mid = (pb + g0) / 2
        sc.ell(v3(mid, 0.14 * z), (np.linalg.norm(g0 - pb) / 2 + 0.06, 0.13, 0.12), basis(v3(g0 - pb), (0, 0, 1)), k=0.15, mat=B)
        # ひざ（スタイフル）
        sc.ell(v3(st + adir(Hh['ang'][0] + 90) * -0.02, zl * 1.02), (0.08, 0.09, 0.075), basis(v3(hk - st), (0, 0, 1)), k=0.10, mat=B)
        # すね（ガスキン）
        dsh = nrm(hk - st)
        sc.rcone(v3(st, zl), v3(hk, zl * 0.92 + ldz * .48), 0.095, 0.055, k=0.06, mat=B)
        bk = adir(Hh['ang'][1] - 90)
        if bk[0] > 0: bk = -bk
        gm = st + (hk - st) * 0.36 + bk * 0.035
        sc.ell(v3(gm, zl + ldz * .17), (0.16, 0.085, 0.075), basis(v3(hk - st), (0, 0, 1)), k=0.06, mat=B)
        # 飛節＋かかと
        sc.ell(v3(hk, zl * 0.92 + ldz * .48), (0.068, 0.07, 0.056), basis(v3(ft - hk), (0, 0, 1)), k=0.04, mat=B)
        hb = adir(Hh['ang'][2] - 90)
        if hb[0] > 0: hb = -hb
        heel = hk + hb * 0.07 + nrm(hk - ft) * 0.035
        sc.sph(v3(heel, zl * 0.92 + ldz * .48), 0.038, k=0.04, mat=B)
        sc.rcone(v3(gm + bk * 0.04, zl + ldz * .17), v3(heel, zl * 0.92 + ldz * .48), 0.045, 0.03, k=0.04, mat=B)   # アキレスけん
        # 管・球節・つなぎ・ひづめ
        dkf = nrm(ft - hk)
        sc.rcone(v3(hk, zl * 0.92 + ldz * .48), v3(ft, zl * 0.88 + ldz * .78), 0.048, 0.042, k=0.03, mat=B)
        sc.rcone(v3(hk + hb * 0.03 + dkf * 0.07, zl * 0.92 + ldz * .52), v3(ft + hb * 0.024 - dkf * 0.03, zl * 0.88 + ldz * .75), 0.03, 0.027, k=0.02, mat=B)
        sc.ell(v3(ft + hb * 0.008, zl * 0.88 + ldz * .78), (0.062, 0.064, 0.055), basis(v3(dkf), (0, 0, 1)), k=0.03, mat=B)
        sc.rcone(v3(ft, zl * 0.88 + ldz * .78), v3(co, zl * 0.88 + ldz * .91), 0.046, 0.051, k=0.03, mat=B)
        sc.ccone(v3(co, zl * 0.88 + ldz * .91), v3(hf, zl * 0.88 + ldz), 0.057, 0.076, rnd=0.008, side=v3(adir(Hh['ang'][3] - 28 + 90)), k=0.012, mat=HO)
    return S


REAR = dict(
    theta=48.0, neck_rot=-42.0, head_ang=-36.0,
    fore=dict(L=[-72, 18, -104, -140], R=[-84, 4, -112, -150]),
    hind=dict(L=[-44, -126, -80, -56], R=[-50, -122, -84, -58]),
    tail=[-108, -96],
)

PRANCE = dict(
    theta=10.0, neck_rot=-6.0, head_ang=-70.0,
    fore=dict(L=[-86, -6, -96, -132], R=[-122, -92, -90, -62]),
    hind=dict(L=[-55, -112, -88, -60], R=[-66, -122, -95, -64]),
    tail=[-150, -110],
)

GALLOP = dict(
    theta=-2.0, neck_rot=-30.0, head_ang=-40.0,
    fore=dict(L=[-98, -38, -30, -18], R=[-128, -18, -142, -165]),
    hind=dict(L=[-108, -150, -128, -150], R=[-52, -102, -72, -50]),
    tail=[-168, -150],
)

def _neck_head(sc, pose, S, M):
    B, N, HO, EY, HD = M['body'], M['neck'], M['hoof'], M['eye'], M['head']
    Y = S.get('yaw')
    S0 = S
    if Y:                                       # 首を 横に まげる：まげる 前の 形を 作って、sc の かわり（_YawSc）が まげた 所へ 置く
        S0 = dict(S)
        S0['yaw'] = None
        sc = _YawSc(sc, S, Y)
    # ---------- 首 ----------
    n = 30
    ts = np.linspace(0, 1, n)
    top = bez(S['crest'], ts)
    bot = bez(S['throat'], ts)
    hw = np.interp(ts, [0, .35, .8, 1], [0.19, 0.14, 0.095, 0.075])
    for i in range(n):
        c2 = (top[i] + bot[i]) / 2
        upv = top[i] - bot[i]
        hh = np.linalg.norm(upv) / 2
        tang = np.array([upv[1], -upv[0]])
        tang = tang / np.linalg.norm(tang)
        L = 0.07 if i < n - 1 else 0.06
        if Y:
            sc.mode = float(ts[i])
        sc.ell(v3(c2), (L, hh, hw[i]), basis(v3(tang), v3(upv)), k=0.12 if i else 0.16, mat=N)
    # たてがみの下の盛り上がり（クレスト）
    for tt in (0.35, 0.6):
        p = bez(S['crest'], tt)
        q = bez(S['throat'], tt)
        d = nrm(bez(S['crest'], tt + 0.05) - bez(S['crest'], tt - 0.05))
        c2 = p + (q - p) * 0.2
        if Y:
            sc.mode = tt
        sc.ell(v3(c2), (0.16, 0.07, 0.085 if tt < .5 else 0.07), basis(v3(d), v3(p - q)), k=0.06, mat=N)
    # 首の横の筋（あごから肩へ）
    for z in (1, -1):
        a = head_pt(S0, 0.26, -0.12)[:2]
        b = S['FL']['ps'] + np.array([0.0, 0.06])
        if Y:                                   # まげた 首に そって 8つに 分ける（あご → 肩）
            pa, pb = np.array([a[0], a[1], 0.075 * z]), np.array([b[0], b[1], 0.11 * z])
            pts = []
            for j in range(9):
                s_ = j / 8
                p = pa + (pb - pa) * s_
                wgt = (1 - s_) ** 3
                pts.append(neck_xf(Y, p, 1.0 - s_) * (1 - wgt) + head_xf(Y, p) * wgt)
            for j in range(8):
                sc.sc.rcone(pts[j], pts[j + 1], 0.04 + 0.02 * j / 8, 0.04 + 0.02 * (j + 1) / 8, k=0.09, mat=N)
            continue
        sc.rcone(np.array([a[0], a[1], 0.075 * z]), np.array([b[0], b[1], 0.11 * z]), 0.04, 0.06, k=0.09, mat=N)

    # ---------- 頭 ----------
    u = adir(S['head_ang'])
    U3 = v3(u)
    V3 = v3(np.array([-u[1], u[0]]))
    HR = basis(U3, V3)
    hp = lambda s, w, z=0.0: head_pt(S0, s, w, z)
    if Y:
        sc.mode = 'head'
    HS = HEAD_SCALE
    def hdir(rot):
        a = math.radians(rot)
        return U3 * math.cos(a) + V3 * math.sin(a), -U3 * math.sin(a) + V3 * math.cos(a)

    def E(s_, w, z, r, k, op='U', rot=0.0, mat=HD):
        dx, dy = hdir(rot)
        sc.ell(hp(s_, w, z), tuple(x * HS for x in r), basis(dx, dy), op=op, k=k, mat=mat)

    def RB(s_, w, z, half, rnd, k, rot=0.0, op='U', mat=HD):
        dx, dy = hdir(rot)
        sc.rbox(hp(s_, w, z), tuple(x * HS for x in half), rnd * HS, basis(dx, dy), op=op, k=k, mat=mat)

    def RC(a, b, ra, rb, k, mat=HD):
        sc.rcone(hp(*a), hp(*b), ra * HS, rb * HS, k=k, mat=mat)

    E(0.07, -0.005, 0, (0.10, 0.085, 0.092), k=0.07)                       # 頭蓋
    RB(0.17, 0.03, 0, (0.10, 0.032, 0.088), 0.03, k=0.05)                  # ひたい（平ら）
    RB(0.36, 0.02, 0, (0.13, 0.03, 0.062), 0.028, k=0.05, rot=-3)          # 鼻すじ
    E(0.33, -0.045, 0, (0.16, 0.065, 0.078), k=0.05)                       # 顔の横
    for z in (1, -1):
        E(0.215, -0.115, 0.058 * z, (0.125, 0.115, 0.05), k=0.05)          # ほお（丸い板）
        E(0.255, -0.02, 0.083 * z, (0.075, 0.013, 0.016), k=0.02, rot=-14)  # 顔のすじ
        E(0.132, 0.062, 0.080 * z, (0.046, 0.017, 0.026), k=0.022, rot=8)   # まゆ
        E(0.170, 0.010, 0.086 * z, (0.034, 0.010, 0.018), k=0.016, rot=-10)  # 下まぶた
        RC((0.25, -0.20, 0.045 * z), (0.49, -0.10, 0.03 * z), 0.035, 0.026, k=0.04)  # 下あごの骨
    E(0.525, -0.02, 0, (0.075, 0.072, 0.064), k=0.05)                      # 鼻先
    E(0.575, -0.042, 0, (0.042, 0.04, 0.052), k=0.03)                      # 上くちびる
    E(0.555, -0.088, 0, (0.045, 0.028, 0.044), k=0.02)                     # 下くちびる
    E(0.505, -0.105, 0, (0.045, 0.03, 0.04), k=0.03)                       # あご先
    for z in (1, -1):
        E(0.53, 0.042, 0.043 * z, (0.035, 0.014, 0.02), k=0.015, rot=-20)  # 鼻の穴のふち
        # 耳（平たい形＋内側のくぼみ）
        d = ear_vec(U3, V3, z, pose.get('ear_rot', 0.0))
        o = nrm(V3 * 0.7 + np.array([0, 0, 0.7 * z]))
        o = nrm(o - d * np.dot(o, d))
        b0 = hp(0.0, 0.02, 0.058 * z)
        sc.ell(b0 + d * 0.07 * HS, (0.08 * HS, 0.022 * HS, 0.034 * HS), basis(d, o), k=0.025, mat=HD)
        sc.rcone(b0 + d * 0.10 * HS, b0 + d * 0.175 * HS, 0.022 * HS, 0.004 * HS, k=0.02, mat=HD)
        sc.ell(b0 + d * 0.08 * HS + o * 0.03 * HS, (0.06 * HS, 0.014 * HS, 0.02 * HS), basis(d, o), op='S', k=0.008, mat=HD)
    for z in (1, -1):
        E(0.535, 0.022, 0.05 * z, (0.03, 0.011, 0.02), k=0.01, op='S', rot=-25)   # 鼻の穴
    E(0.565, -0.064, 0, (0.065, 0.005, 0.07), k=0.004, op='S')                    # 口
    for z in (1, -1):
        sc.ell(hp(0.152, 0.036, 0.091 * z), (0.030 * HS, 0.022 * HS, 0.024 * HS), basis(*hdir(-12)), k=0.003, mat=EY)  # 目（アーモンド形）
    S['eye'] = hp(0.152, 0.036, 0.091 + 0.02)
    S['eyes'] = [hp(0.152, 0.036, 0.091), hp(0.152, 0.036, -0.091)]
    S['head_u'] = U3; S['head_v'] = V3
    if Y:                                       # 首を 横に まげた 時の 目・頭の 向き
        Qh = yaw_R(Y['n'] + Y['h'])
        S['eye'] = head_xf(Y, S['eye'])
        S['eyes'] = [head_xf(Y, e) for e in S['eyes']]
        S['head_u'], S['head_v'] = Qh @ U3, Qh @ V3


def _bust(sc, pose, S, M, T, th):
    _neck_head(sc, pose, S, M)
    return S
