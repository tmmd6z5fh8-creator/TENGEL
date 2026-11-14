# 馬バレの 絵：金の 枠の 内がわ（色の 丸）の 半径を 測る
import sys, os, math
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
from PIL import Image
import drop_art as DA
D = ROOT + '/art/in'
fs = sorted(f for f in os.listdir(D) if f.endswith('.png'))[:6]
for f in fs:
    a = np.asarray(Image.open(os.path.join(D, f)).convert('RGBA')).astype(np.float64)
    cx, cy, R = DA.fit_circle(a[..., 3].astype(np.uint8))
    # 半径ごとの 色（角度で 平均）
    prof = []
    rs = np.arange(300, int(R) + 5, 1.0)
    ang = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    for r in rs:
        x = np.clip(np.rint(cx + r * np.cos(ang)).astype(int), 0, a.shape[1] - 1); y = np.clip(np.rint(cy + r * np.sin(ang)).astype(int), 0, a.shape[0] - 1)
        c = a[y, x, :3]
        gold = (c[:, 0] > 170) & (c[:, 1] > 110) & (c[:, 2] < 110) & (c[:, 0] - c[:, 2] > 90)        # 金（黄色〜オレンジ）
        prof.append(gold.mean())
    prof = np.array(prof)
    # 外から 内へ：金の わりあいが 0.5 を 下回る ところ
    k = len(rs) - 1
    while k > 0 and prof[k] < 0.5: k -= 1      # 外の ふち（すき通る 所）を とばす
    while k > 0 and prof[k] >= 0.5: k -= 1
    print(f, f'R {R:.1f}  inner edge of gold ≈ {rs[k]:.0f}px ({rs[k] / R:.3f} R)  gold frac at r=380..440:', np.round(prof[80:141:10], 2))
