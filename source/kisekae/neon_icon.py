"""フリーズ的中ボタンのネオンの線画：テンゲルのアイコン（icons/icon_master_en.png・App Storeのアイコンと同じ絵）の線をひろって、
   ネオンの「芯（細い線）」と「光（にじみ）」のマスクを2枚作る（白＋透明度。色は見本の画面のCSSで虹色にする）。
   python3 neon_icon.py <icon_master_en.png> <出力フォルダ>
   → fz_ncore.webp（1024×1024）・fz_nglow.webp（512×512）・neon_preview.png（黒の上に虹色で重ねた確認用）"""
import sys
import numpy as np
import cv2
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
N = 1024
im = cv2.imread(src, cv2.IMREAD_COLOR)
im = cv2.resize(im, (N, N), interpolation=cv2.INTER_AREA)
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
g = cv2.bilateralFilter(g, 7, 40, 7)
e = cv2.Canny(g, 38, 110, L2gradient=True)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
core = cv2.GaussianBlur(cv2.dilate(e, k, iterations=1).astype(np.float32) / 255, (0, 0), .9)
core = np.clip(core * 1.6, 0, 1)
glow = cv2.GaussianBlur(cv2.dilate(e, k, iterations=2).astype(np.float32) / 255, (0, 0), 7)
glow = np.clip(glow / max(float(glow.max()), 1e-6) * 1.25, 0, 1) * .75


def save(a, fn, size):
    rgba = np.zeros((N, N, 4), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').resize((size, size), Image.LANCZOS).save(f'{out}/{fn}', quality=80, method=6)


save(core, 'fz_ncore.webp', 1024)
save(glow, 'fz_nglow.webp', 512)
yy, xx = np.mgrid[0:N, 0:N]
hue = ((xx + yy) / (2 * N) * 270) % 180
hsv = np.stack([hue, np.full_like(hue, 255), np.full_like(hue, 255)], -1).astype(np.uint8)
rb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB).astype(np.float32) / 255
img = np.clip(rb * glow[..., None] + (rb * .35 + .65) * core[..., None], 0, 1)
Image.fromarray((img * 255).astype(np.uint8)).save(f'{out}/neon_preview.png')
print('ok')
