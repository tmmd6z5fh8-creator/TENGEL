"""紫電（第4.69版〜）：画面を 切り裂く 馬の 蹄（ひづめ）の 3D の 形（sdfr）
   まさちゃん「画面を切るのをコーンじゃなくて馬の蹄にして！」（見本の 写真は 黒い 馬の 足と 蹄：形の イメージだけ・写真は 使わない）
   黒い 馬の 前足の 下（管・球節・つなぎ・蹄・蹄鉄）。足は 左から のび、蹄の 裏（蹄鉄）が 右を 向く（前へ 打ちだす 形・つま先は 上）。
   第4.70版：形だけ（光・つや・焼けた 蹄鉄の 光・毛・ぶれ・カメラは flat/shiden_film.py の hoof_layer：動画の コマごとに 描く）。
   第4.69版の 1まいの 絵（sd_w_hoof）は やめた"""
import math
import numpy as np

TH = math.radians(28)                    # 蹄と つなぎの 軸の うしろへの かたむき（立った とき）
TANA = 0.09                              # 蹄の 広がり（下ほど 太い）
R0 = 0.056                               # 地面での 蹄の 太さ（半径）
HT = 0.064                               # 蹄の 高さ（軸に そって）
M_COAT, M_HOOF, M_BAND, M_SHOE, M_SOLE = 1, 2, 3, 4, 6


def Rw(p):
    """立った 足の 座標（x 前・y 上・z 横）→ 絵の 世界：90° 左回り（足の 下 → 右・つま先 → 上）"""
    p = np.asarray(p, float)
    return np.array([-p[1], p[0], p[2]])


RL = np.array([[0, 1.0, 0], [-1.0, 0, 0], [0, 0, 1.0]])   # 立った 座標の 軸（x・y・z）が 世界で どこを 向くか（行）＝ ell の 回転


def sole_outline(n=64):
    """地面（y=0）で 切った 蹄の ふち（立った 座標・つま先が φ=0）"""
    u = np.array([-math.sin(TH), math.cos(TH), 0.0])
    e1 = np.array([math.cos(TH), math.sin(TH), 0.0])
    e2 = np.array([0, 0, 1.0])
    pts = []
    for ph in np.linspace(-math.pi, math.pi, n, endpoint=False):
        c = math.cos(ph)
        s = -R0 * c * math.sin(TH) / (math.cos(TH) - TANA * c * math.sin(TH))
        r = R0 - s * TANA
        pts.append(u * s + r * (c * e1 + math.sin(ph) * e2))
    return np.array(pts), u, e1


def build(sc):
    """形を 出す（世界の 座標）。もどり値：だいじな 点（世界）"""
    out, u, e1 = sole_outline(96)
    g = np.zeros(3)
    U = lambda s: g + u * s
    # ---------- 蹄（ひづめ）：かたむいた 円すい台を 地面で 平らに 切る ----------
    sc.begin('U', 0.004, M_HOOF)
    a, b = U(-0.03), U(HT)
    sc.ccone(Rw(a), Rw(b), R0 + 0.03 * TANA, R0 - HT * TANA, rnd=0.006, side=Rw(e1), mat=M_HOOF)
    sc.rbox(Rw((0, -0.15, 0)), (0.15, 0.4, 0.4), 0.0, op='S', k=0.003, mat=M_HOOF)          # 地面で 切る（裏は 平ら）
    sc.end()
    cx0 = out[:, 0].mean()
    sc.ell(Rw((cx0, 0.0004, 0)), (0.058, 0.0016, 0.052), RL, k=0.002, mat=M_SOLE)                 # 裏（うすい 灰色）
    sc.begin('U', 0.003, M_SOLE)                                                           # 裏の かえる（つま先へ とがる V の ふくらみ）
    sc.ell(Rw((cx0 - 0.026, -0.0008, 0)), (0.046, 0.0055, 0.022), RL, mat=M_SOLE)
    sc.ell(Rw((cx0 - 0.04, -0.004, 0)), (0.03, 0.004, 0.0055), RL, op='S', k=0.002, mat=M_SOLE)
    sc.end()
    # ---------- 蹄鉄：裏の ふちに そった U の 形（かかとは あく） ----------
    sc.begin('U', 0.003, M_SHOE)
    n = len(out)
    first = True
    for inset, rr in ((0.0042, 0.0038), (0.0102, 0.004), (0.016, 0.0037)):
        P = []
        for i in range(n):
            ph = -math.pi + 2 * math.pi * i / n
            if abs(ph) > math.radians(140):
                continue
            q = out[i].copy()
            q2 = np.array([q[0], 0, q[2]])
            ctr = np.array([out[:, 0].mean(), 0, 0])
            d = q2 - ctr
            q2 = q2 - d / (np.linalg.norm(d) + 1e-9) * inset
            q2[1] = -0.0038
            P.append(q2)
        for p0, p1 in zip(P[:-1], P[1:]):
            sc.rcone(Rw(p0), Rw(p1), rr, rr, k=0.0 if first else 0.003, mat=M_SHOE)
            first = False
    sc.end()
    # ---------- 毛の 足：かんむり（毛の ふち）・つなぎ・球節・管・腱・かかと ----------
    ct = U(HT)
    f = U(HT + 0.105) + np.array([-0.004, 0.0, 0.0])
    sc.begin('U', 0.02, M_COAT)
    sc.ell(Rw(ct + u * 0.004), (R0 - HT * TANA + 0.003, 0.013, R0 - HT * TANA + 0.003), np.array([Rw(e1), Rw(u), Rw((0, 0, 1))]), mat=M_COAT)       # かんむり（蹄の 上の 毛の ふち）
    sc.rcone(Rw(ct + u * 0.01), Rw(f - u * 0.02), 0.041, 0.034, k=0.022, mat=M_COAT)                              # つなぎ（球節より 細い）
    sc.ell(Rw(f + np.array([-0.016, 0.0, 0])), (0.064, 0.052, 0.05), RL, k=0.022, mat=M_COAT)                       # 球節（まるい 関節）
    sc.ell(Rw(f + np.array([-0.058, -0.026, 0])), (0.02, 0.017, 0.017), RL, k=0.015, mat=M_COAT)                # けづめ（球節の うしろ）
    kn = f + np.array([0.012, 0.40, 0])
    sc.rcone(Rw(f + np.array([0.004, 0.035, 0])), Rw(kn), 0.031, 0.033, k=0.025, mat=M_COAT)                      # 管（骨）
    sc.rcone(Rw(f + np.array([-0.026, 0.045, 0])), Rw(kn + np.array([-0.028, -0.04, 0])), 0.022, 0.021, k=0.015, mat=M_COAT)   # 腱（うしろの すじ）
    for z in (1, -1):
        hb = U(0.058) + e1 * -0.04 + np.array([0, 0, 0.021 * z])
        sc.ell(Rw(hb), (0.024, 0.02, 0.021), RL, k=0.02, mat=M_COAT)                                          # かかと（ふくらみ）
    sc.end()
    sc.torus(Rw(ct + u * 0.003), Rw(u), R0 - HT * TANA + 0.001, 0.0042, k=0.004, mat=M_BAND)                  # 蹄の 上の 毛の ふち（明るい すじ）
    toe = out[np.argmin(np.abs(np.arctan2(out[:, 2], out[:, 0] - out[:, 0].mean())))]
    return dict(sole=Rw(np.array([out[:, 0].mean(), -0.012, 0])), toe=Rw(toe), fet=Rw(f), knee=Rw(kn), crown=Rw(ct),
                ergot=Rw(f + np.array([-0.06, -0.026, 0])), ax=Rw(u), e1=Rw(e1), outline=np.array([Rw(np.array([p[0], -0.012, p[2]])) for p in out]))
