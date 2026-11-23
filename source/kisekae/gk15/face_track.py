# 神様極的中：ほおの 形（3つ）を コマごとに 追う（第4.215版）→ face_track.json（face_fix.py が 使う）
#   python3 face_track.py [点検する コマ,コマ…]   （GK15_WORK＝作業フォルダ：src/ に 第14稿の コマ）
#   ※ リポジトリの face_track.json は 第4.215版で 使った もの そのまま（ほおの 形の 点を 少し 動かす 前に 追った：追う 所は 形の まわり 14px まで ＝ 変形は 同じ）
#   顔を 上げる 動きは 立体の 回り（ほおは 顔の よこの 面）＝ 1つの 変形（アフィン）では 合わない
#   → ほお 1つずつ、その 中の もよう（まだら そのもの）を となりの コマへ 追って 平面の 変形（ホモグラフィ・RANSAC）を つなぐ → さいごに もとの コマ（90）と じかに 合わせ直す（ずれの たまりを 消す）
import numpy as np, cv2, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
D = os.environ.get('GK15_WORK', '/home/claude/work/v215/gk')
import face_fix
def load(f): return cv2.imread(f'{D}/src/{f:04d}.png')
def prep(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32); g = cv2.GaussianBlur(g, (0, 0), 1.0)
    m = max(float(np.percentile(g[600:1150, 120:660], 98)), 2.0)                       # 暗い はじめの コマも 同じ 明るさに そろえる
    return np.clip(g * (190.0 / m), 0, 255).astype(np.uint8)
REF = 90
POLY = face_fix.POLY
LK = dict(winSize=(25, 25), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))


def warp_pts(H, p):
    q = np.hstack([p, np.ones((len(p), 1))]) @ H.T; return q[:, :2] / q[:, 2:3]


def region_mask(shape, H, pts, grow):
    m = np.zeros(shape, np.uint8); cv2.fillPoly(m, [np.round(warp_pts(H, np.array(pts, np.float64))).astype(np.int32)], 255)
    return cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1))) if grow else m


def step(prev, cur, mask):
    p0 = cv2.goodFeaturesToTrack(prev, 400, 0.004, 5, mask=mask)
    if p0 is None or len(p0) < 12: return None, 0, 0
    p1, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, p0, None, **LK); pb, st2, _ = cv2.calcOpticalFlowPyrLK(cur, prev, p1, None, **LK)
    ok = (st.ravel() == 1) & (st2.ravel() == 1) & (np.abs(p0 - pb).reshape(-1, 2).max(1) < 0.8)
    n = int(ok.sum())
    if n >= 24:
        H, inl = cv2.findHomography(p0[ok], p1[ok], cv2.RANSAC, 1.2)
        if H is not None and inl.sum() >= 18: return H, n, int(inl.sum())
    if n >= 10:
        M, inl = cv2.estimateAffine2D(p0[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=1.2)
        if M is not None and inl.sum() >= 8: return np.vstack([M, [0, 0, 1]]), n, -int(inl.sum())
    return None, n, 0


def track(lo=30, hi=113, grow=14):
    G = {f: prep(load(f)) for f in range(lo, hi + 1)}; out = {}; log = {}
    for name, pts in POLY.items():
        H = {REF: np.eye(3)}
        for d in (1, -1):
            f = REF
            while lo <= f + d <= hi:
                f2 = f + d; m = region_mask(G[f].shape, H[f], pts, grow)
                S, n, inl = step(G[f], G[f2], m)
                if S is None: S = np.eye(3)                                          # 追えない コマ（まっ暗）：前の コマと 同じ 所
                H[f2] = S @ H[f]; log[(name, f2)] = (n, inl); f = f2
        out[name] = H
    return out, log, G


def refine(out, G, lo=30, hi=113, grow=10):
    """もとの コマ（90）を つないだ 変形で コマ f へ うつした 絵と、コマ f を じかに くらべて のこりの ずれを 直す"""
    g0 = G[REF]; res = {}
    for name, pts in POLY.items():
        res[name] = {}
        for f in range(lo, hi + 1):
            H = out[name][f]
            if f == REF: res[name][f] = H; continue
            w = cv2.warpPerspective(g0, H, (g0.shape[1], g0.shape[0]), flags=cv2.INTER_LINEAR)
            m = region_mask(g0.shape, H, pts, grow)
            S, n, inl = step(w, G[f], m)
            if S is not None and inl >= 30:
                c = warp_pts(H, np.array(pts, np.float64)); c2 = warp_pts(S, c)
                if np.abs(c2 - c).max() < 12: H = S @ H                             # 大きく とぶ 直しは 使わない
            res[name][f] = H
    return res


if __name__ == '__main__':
    out, log, G = track()
    for name in POLY:
        print(name, ' '.join(f"{f}:{log[(name, f)][0]}/{log[(name, f)][1]}" for f in range(30, 114, 4) if (name, f) in log))
    res = refine(out, G)
    json.dump({n: {str(f): H.tolist() for f, H in d.items()} for n, d in res.items()}, open(os.path.join(D, "face_track.json"), "w"), separators=(",", ":"))      # 作業フォルダへ（リポジトリの ものは 上書きしない）
    # 点検：形の 線を かいた 一覧
    fs = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else list(range(32, 114, 6))
    tiles = []
    for f in fs:
        v = np.clip(load(f).astype(np.float32) * (190.0 / max(float(np.percentile(load(f)[600:1150, 120:660], 98)), 2.0)) * 0.9, 0, 255).astype(np.uint8)
        for name, pts in POLY.items():
            for key, col in ((out, (0, 255, 255)), (res, (255, 0, 255))):
                q = warp_pts(key[name][f], np.array(pts, np.float64)); cv2.polylines(v, [np.round(q).astype(np.int32)], True, col, 1)
        cv2.putText(v, str(f), (70, 620), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3); tiles.append(v[560:1240, 60:720])
    n = 5; rows = [np.hstack(tiles[i:i + n] + [np.zeros_like(tiles[0])] * (n - len(tiles[i:i + n]))) for i in range(0, len(tiles), n)]
    cv2.imwrite(os.path.join(D, 'face_track_check.png'), cv2.resize(np.vstack(rows), None, fx=0.55, fy=0.55, interpolation=cv2.INTER_AREA))
