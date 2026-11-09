# フィギュアの くりぬかれた ボードに 何も 書いて いない 板を はめた 写真（まさちゃん 11/09 21:04「ボードくり抜かれてるから、8種全部に埋め込める？何も書いてないバージョン！」）
#   python3 kisekae/fig/blank_board.py <まさちゃんの GLB> <out/figN_board.json> <板の 色 gold／amethyst／duel> <出す png> [大きさ 1000] [見下ろし 度 6]
#   → すける 背景の 写真（アプリの「デザインを 選ぶ」の 写真：collect_assets.py が thumbs/figN.png を 使う）
#   ・板の 場所：out/figN_board.json（board_find.py：高さ 2.15 に そろえた 座標）を 元の GLB の 座標に もどす（fig_bake.py の そろえ方の 逆）
#   ・板の 色：アプリの ボードと 同じ（金：①〜⑥・アメジスト：⑦・紫→金：⑧）。ふちの 線だけ（字は なし）・角は まるい
import os, sys, math, json
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'r3d', 'glb'))
import glb
from raster import Camera, render, tonemap
from PIL import Image, ImageDraw
GLB, BJ, pal, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]; R = int(sys.argv[5]) if len(sys.argv) > 5 else 1000; EL = float(sys.argv[6]) if len(sys.argv) > 6 else 6
PAL = {
    'gold': ([('#f6dc8a', 0), ('#d9a83c', 0.45), ('#b8862a', 1)], 'diag', (110, 70, 10, 140)),
    'amethyst': ([('#b65cc8', 0), ('#7d2590', 0.5), ('#4e1060', 1)], 'diag', (255, 215, 120, 153)),
    'duel': ([('#7d2590', 0), ('#a8467a', 0.45), ('#d9a83c', 1)], 'h', (255, 225, 140, 153))}
m = glb.load(GLB); prims = m.flatten()
P = np.concatenate([p.pos for p in prims]); lo, hi = P.min(0), P.max(0)
s = 2.15 / (hi[1] - lo[1]); off = np.array([(lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2])
bd = json.load(open(BJ)); c, bw, bh = bd['c'], bd['w'], bd['h']
# 板の 絵（色の 流れ・ふちの 線）と 金属／あらさ（明るい ところほど 金属：アプリの シェーダーと 同じ）
TW = 1024; TH = max(64, round(TW * bh / bw))
stops, dr, line = PAL[pal]
hx = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255
yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
if dr == 'h': t = xx / (TW - 1)
else:
    gx, gy = TW * 0.4, TH; t = (xx * gx + yy * gy) / (gx * gx + gy * gy)
t = np.clip(t, 0, 1); img = np.zeros((TH, TW, 3), np.float32)
for (c0, o0), (c1, o1) in zip(stops[:-1], stops[1:]):
    k = np.clip((t - o0) / max(1e-6, o1 - o0), 0, 1)[..., None]; msk = ((t >= o0) & (t <= o1))[..., None]
    img = np.where(msk, hx(c0) * (1 - k) + hx(c1) * k, img)
im = Image.fromarray((img * 255).astype(np.uint8), 'RGB').convert('RGBA')
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(ov)
lw = max(2, round(TH * 0.012)); dd.rectangle([TW * 0.035, TH * 0.05, TW * 0.965, TH * 0.95], outline=line, width=lw)
im = Image.alpha_composite(im, ov).convert('RGB')
A = np.asarray(im, np.float32) / 255; lum = A.mean(2)
metal = 0.85 * np.clip((lum - 0.25) / 0.35, 0, 1) ** 2 * (3 - 2 * np.clip((lum - 0.25) / 0.35, 0, 1))
MR = np.stack([np.ones_like(lum), np.full_like(lum, 0.38), metal], 2)
tex = glb.Texture(np.dstack([A, np.ones_like(lum)]).astype(np.float32), glb.CLAMP, glb.CLAMP, 'board')
mrt = glb.Texture(np.dstack([MR, np.ones_like(lum)]).astype(np.float32), glb.CLAMP, glb.CLAMP, 'board_mr')
mat = glb.Material({'pbrMetallicRoughness': {'metallicFactor': 1.0, 'roughnessFactor': 1.0}}, None, 'board')
mat.base_tex = glb.TexRef(tex); mat.mr_tex = glb.TexRef(mrt); mat.double_sided = True
# 板：長方形 2まい（扇の 細い 三角だと ソフトの 描き方で すじが 出る）・角の まるみは 絵の すける ところ（MASK）
r = min(bw, bh) * 0.07; z = c[2] + 0.008      # 面の いちばん 前（board_find.py）より 少し 前（アプリの 板と 同じ）
Vn = np.array([[c[0] - bw / 2, c[1] - bh / 2, z], [c[0] + bw / 2, c[1] - bh / 2, z], [c[0] + bw / 2, c[1] + bh / 2, z], [c[0] - bw / 2, c[1] + bh / 2, z]], np.float64)
V = (Vn / s + off).astype(np.float32)
uv = np.array([[0, 1], [1, 1], [1, 0], [0, 0]], np.float32); idx = np.array([[0, 1, 2], [0, 2, 3]], np.int32)
nrm = np.tile(np.array([[0, 0, 1]], np.float32), (4, 1))
yy2, xx2 = np.mgrid[0:TH, 0:TW].astype(np.float32); rx, ry = r / bw * TW, r / bh * TH
cxk = np.clip(xx2, rx, TW - 1 - rx); cyk = np.clip(yy2, ry, TH - 1 - ry)
alpha = ((((xx2 - cxk) / rx) ** 2 + ((yy2 - cyk) / ry) ** 2) <= 1).astype(np.float32)
tex.img[..., 3] = alpha; mat.alpha_mode = 'MASK'; mat.alpha_cutoff = 0.5
plate = glb.Prim(V, nrm, uv, idx, mat, 'board')
cen = (lo + hi) / 2; ext = hi - lo; e = math.radians(EL); dist = max(ext[0], ext[1]) * 4.2
eye = cen + dist * np.array([0, math.sin(e), math.cos(e)])
cam = Camera.look_at(eye, cen, fov_y=15, W=R, H=R)
fr = render(prims + [plate], cam, ss=2, want=('rgb', 'alpha'))
rgb = np.clip(tonemap(fr['rgb'], 1.0), 0, 1); a = np.clip(fr['alpha'], 0, 1)
o = Image.fromarray((np.dstack([rgb, a]) * 255 + 0.5).astype(np.uint8), 'RGBA'); o = o.crop(o.getbbox()); o.save(out); print(out, o.size)
