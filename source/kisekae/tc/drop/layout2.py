# ボタンの 形（多角形）・コップの 口・釘の 先 を 絵の 画素で 測る
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
import cv2
from scipy import ndimage as ndi
import cam as C
import world as WD
APP = ROOT + '/app/'
d = np.load(APP + 'base.npz')
z, al, alb = d['z'], d['alpha'], d['albedo'].astype(np.float32) / 255
H, W = z.shape


def poly_of(mask, eps=2.0):
    m = ndi.binary_fill_holes(ndi.binary_closing(mask, iterations=6))
    lab, n = ndi.label(m); cnt = np.bincount(lab.ravel()); cnt[0] = 0; m = lab == cnt.argmax()
    cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    ap = cv2.approxPolyDP(c, eps, True)[:, 0, :]
    ys, xs = np.nonzero(m)
    return [[int(x), int(y)] for x, y in ap], [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1], m


rows = np.zeros((H, W), bool); rows[int(C.proj(0, -0.53, 0.08)[1]):int(C.proj(0, -0.72, 0.08)[1])] = True
red = rows & (alb[..., 0] > 0.55) & (alb[..., 1] < 0.3) & (alb[..., 2] < 0.35) & (al > 200)
pr, br, mr = poly_of(red)
print('red button: poly', len(pr), 'bbox', br, pr)
rows2 = np.zeros((H, W), bool); rows2[int(C.proj(0, -0.705, 0.08)[1]):int(C.proj(0, -0.90, 0.08)[1])] = True
cols = np.zeros((H, W), bool); cols[:, int(C.proj(-0.43, 0, 0.08)[0]):int(C.proj(0.43, 0, 0.08)[0])] = True
mint = rows2 & cols & (alb[..., 1] > alb[..., 0] * 1.12) & (alb[..., 1] > alb[..., 2] * 1.02) & (alb[..., 1] > 0.5) & (al > 200) & (z > 0.06)
pm, bm, mm = poly_of(mint)
print('mint button: poly', len(pm), 'bbox', bm, pm)
lay = json.load(open(APP + 'layout1.json'))
out = dict(btn_go=dict(poly=pr, box=br), btn_see=dict(poly=pm, box=bm))
json.dump(out, open(APP + 'layout2.json', 'w'))
from PIL import Image
v = d['rgb'].copy()
for p, col in ((pr, (0, 0, 255)), (pm, (255, 0, 255))):
    cv2.polylines(v, [np.array(p, np.int32)], True, col, 2)
Image.fromarray(v[1380:1780]).save(APP + 'btn_view.png')
