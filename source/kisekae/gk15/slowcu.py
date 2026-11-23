# 神様極的中：「神」「様」「的」「中」の 寄り（1つ 11コマ＝0.37秒）を ゆっくり（1つ 24コマ＝0.8秒）に（第4.215版・まさちゃん 2026/11/24 01:35 ③）
#   「神様的中の 違う 角度の カットイン 映像、一つ一つの カットイン 早すぎるから、ゆっくり 字が わかる ように」
#   もとの 3D は もう ない ので、できた 動画（第14稿）の コマの 間を 作る：となりの コマの 動き（DIS の 動きの 場）を 追って、前の コマと 後の コマを その 時刻の 所へ よせて 重ねる。
#   動画の 明るさ・色の 面（Y・U・V）の まま 計算する（RGB に 直さない ＝ 色と 明るさが ずれない）
import numpy as np, cv2
N_SRC, N_OUT = 11, 24
CUS = (155, 166, 177, 188)                                      # 第14稿の コマ（0 から）：寄りの はじまり
_dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM); _dis.setFinestScale(0)


def flow(Ya, Yb):
    return cv2.GaussianBlur(_dis.calc(Ya, Yb, None), (0, 0), 1.5)


def _warp(P, fl, k):
    """面 P の 点 x の 値を、P の x + k·fl(x) から 持って くる"""
    h, w = P.shape[:2]; X, Y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(P, X + k * fl[..., 0], Y + k * fl[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def _half(fl):
    h, w = fl.shape[:2]; return cv2.resize(fl, (w // 2, h // 2), interpolation=cv2.INTER_AREA) * 0.5


def between(A, B, al, F=None, Bk=None):
    """コマ A と B（どちらも (Y, U, V)）の 間（al＝0〜1）。al が 0 か 1 に ごく 近ければ もとの コマ"""
    if al < 0.02: return A
    if al > 0.98: return B
    F = flow(A[0], B[0]) if F is None else F; Bk = flow(B[0], A[0]) if Bk is None else Bk
    # 行きと 帰りの 動きが 合わない 所（かくれる・出て くる 所・速い 小さな つぶ）は、近い 方の コマを 多く 使う（二重に 写さない）
    Bw = _warp(Bk, F, -al); err = np.hypot(F[..., 0] + Bw[..., 0], F[..., 1] + Bw[..., 1])
    c = np.clip((err - 1.5) / 4.0, 0, 1)
    wgt = (1 - al) * (1 - c) + (1.0 if al < 0.5 else 0.0) * c
    out = []
    for i in range(3):
        f, b, w = (F, Bk, wgt) if i == 0 else (_half(F), _half(Bk), cv2.resize(wgt, (wgt.shape[1] // 2, wgt.shape[0] // 2), interpolation=cv2.INTER_AREA))
        # 間の コマの 点 x：コマ A では x − al·F、コマ B では x − (1−al)·Bk に あった（動きは なめらか と 見る）
        wa = _warp(A[i], f, -al).astype(np.float32); wb = _warp(B[i], b, -(1 - al)).astype(np.float32)
        out.append(np.clip(wa * w + wb * (1 - w) + 0.5, 0, 255).astype(np.uint8))
    return tuple(out)


def slow(frames):
    """寄り 1つ（11コマ・(Y, U, V) の 並び）→ 24コマ：はじめと おわりは もとの コマ（間は ひとしく）"""
    assert len(frames) == N_SRC
    fw = [flow(frames[i][0], frames[i + 1][0]) for i in range(N_SRC - 1)]; bw = [flow(frames[i + 1][0], frames[i][0]) for i in range(N_SRC - 1)]
    out = []
    for j in range(N_OUT):
        p = j * (N_SRC - 1) / (N_OUT - 1); a = min(int(np.floor(p)), N_SRC - 2); out.append(between(frames[a], frames[a + 1], p - a, fw[a], bw[a]))
    return out
