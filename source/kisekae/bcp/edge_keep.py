# 結果ボードカスタム（絵の ボード）：ボードの ふちに かかる 花・葉・リボン（ボードの 外から 中へ 少し 入る 物）を 消さない ための マスク
#   python3 edge_keep.py <デザインの フォルダ> [--sides bottom,left,right,top] [--band 45] [--out keep_edge.png]
#   → <フォルダ>/keep_edge.png（cfg の clean.keep に {"mask": "keep_edge.png"} と 書く）
#   まさちゃん 11/05 21:18「ここが花が切れてる！直して！」（的中⑧ 花束 3連勝：下の まん中の 桜・左下の バラが ボードの 下の ふちで まっすぐ 切れて いた。
#     この 絵は 前の 絵（fg）が ない ので、ボードの 中を 消す 時に ふちに かかる 花も 消えて いた）
#   えらび方：ボードの ふちから band px までの 中で、青っぽく ない（紺の 板・行の ふち 線で ない）物の かたまりの うち、ボードの 外と つながる もの
#     （中の 字・行は 外と つながらない）。元の 絵と 消した 絵が ちがう 所 だけ・ふちを 2px のばす
import json, os, sys
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image
a = sys.argv[1:]
def opt(k, d):
    if k in a: i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
    return d
SIDES = opt('--sides', 'bottom').split(','); BAND = int(opt('--band', '45')); OUTN = opt('--out', 'keep_edge.png')
D = a[0]
cfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
src = np.asarray(Image.open(os.path.join(D, cfg.get('src', 'src.png'))).convert('RGB')).astype(np.float32); H, W = src.shape[:2]
cln = np.asarray(Image.open(os.path.join(D, 'clean.png')).convert('RGB')).astype(np.float32)
R, G, B = src[..., 0], src[..., 1], src[..., 2]; V = src.max(-1)
Q = np.zeros((H, W), np.uint8); cv2.fillPoly(Q, [np.round(np.array(cfg['quad'])).astype(np.int32)], 1); Q = Q.astype(bool)
qx = np.array(cfg['quad'])[:, 0]; qy = np.array(cfg['quad'])[:, 1]
yy, xx = np.mgrid[0:H, 0:W]
side = np.zeros((H, W), bool)
if 'bottom' in SIDES: side |= yy >= qy.max() - BAND
if 'top' in SIDES: side |= yy <= qy.min() + BAND
if 'left' in SIDES: side |= xx <= qx.min() + BAND
if 'right' in SIDES: side |= xx >= qx.max() - BAND
band = Q & ~ndi.binary_erosion(Q, iterations=BAND) & side
blu = (B - R > 12) & (V < 215)                         # 紺の 板・行の ふち 線（青っぽい）
obj = ~blu & (V > 55)
area = ndi.binary_dilation(Q, iterations=6)
lab, n = ndi.label(obj & area)
outside = area & ~ndi.binary_erosion(Q, iterations=2)
touch = set(np.unique(lab[outside & obj])) - {0}
keep = np.isin(lab, list(touch)) & band
keep &= ndi.binary_dilation(np.abs(src - cln).max(-1) > 12, iterations=2)       # 消して しまった 所 だけ
keep = ndi.binary_opening(keep, iterations=1)
l2, n2 = ndi.label(keep)
if n2:
    sz = ndi.sum(keep, l2, range(1, n2 + 1)); keep = np.isin(l2, [i + 1 for i in range(n2) if sz[i] >= 30])
keep = ndi.binary_dilation(keep, iterations=2) & band
Image.fromarray((keep * 255).astype(np.uint8)).save(os.path.join(D, OUTN))
print(os.path.join(D, OUTN), int(keep.sum()), 'px')
