# 馬バレ（まるい メダル）・保留（八角の 宝石）の 形を 測る
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import sys, os, math
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
D = ROOT + '/art/in'
NAMES = ['blue', 'green', 'purple', 'red', 'gold', 'rainbow']


def main_blob(al):
    """いちばん 大きい かたまり（まわりの 小さな ごみを 外す）"""
    lab, n = ndi.label(al > 128)
    if n <= 1:
        return al > 128
    cnt = np.bincount(lab.ravel()); cnt[0] = 0
    return lab == cnt.argmax()


def radial(mask, cx, cy, n=720):
    H, W = mask.shape
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = np.arange(0, 720, 0.5)
        x = np.clip(np.rint(cx + r * math.cos(a)).astype(int), 0, W - 1); y = np.clip(np.rint(cy + r * math.sin(a)).astype(int), 0, H - 1)
        ins = mask[y, x]
        k = np.nonzero(ins)[0]
        out.append(r[k.max()] if len(k) else 0)
    return np.array(out)


if __name__ == '__main__':
    fs = sorted(os.listdir(D))
    for i, f in enumerate(fs):
        a = np.asarray(Image.open(os.path.join(D, f)).convert('RGBA'))
        al = a[..., 3]
        mb = main_blob(al)
        junk = int(((al > 128) & ~mb).sum())
        ys, xs = np.nonzero(mb)
        cx, cy = xs.mean(), ys.mean()
        for _ in range(3):
            rr = radial(mb, cx, cy)
            ang = 2 * math.pi * np.arange(len(rr)) / len(rr)
            px, py = cx + rr * np.cos(ang), cy + rr * np.sin(ang)
            if i < 6:      # 円の あてはめ
                A = np.c_[2 * px, 2 * py, np.ones(len(px))]; b = px ** 2 + py ** 2
                sol, *_ = np.linalg.lstsq(A, b, rcond=None)
                cx, cy = sol[0], sol[1]; R = math.sqrt(sol[2] + cx * cx + cy * cy)
            else:
                cx, cy = (px.min() + px.max()) / 2, (py.min() + py.max()) / 2
        rr = radial(mb, cx, cy)
        kind = '馬バレ' if i < 6 else '保留'
        if i < 6:
            print(f'{f} {kind} {NAMES[i % 6]}: center ({cx:.1f},{cy:.1f}) R {R:.1f}  radius p1 {np.percentile(rr,1):.1f} p50 {np.percentile(rr,50):.1f} p99 {np.percentile(rr,99):.1f} min {rr.min():.1f} max {rr.max():.1f}  junk px {junk}')
        else:
            # 八角：角度ごとの 半径（上下左右＝辺の まん中・ななめ＝辺の まん中）
            n = len(rr); r0 = [rr[int(n * k / 8)] for k in range(8)]; r1 = [rr[int(n * (k + 0.5) / 8)] for k in range(8)]
            print(f'{f} {kind} {NAMES[i % 6]}: center ({cx:.1f},{cy:.1f}) bbox w {xs.max()-xs.min()+1} h {ys.max()-ys.min()+1}  r at 0/45/90…: {[round(x) for x in r0]}  r at 22.5…: {[round(x) for x in r1]}  junk px {junk}')
