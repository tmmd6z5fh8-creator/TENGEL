# バナーの「TENGER」の文字だけを、背景を抜いて取り出す（前置き用）
import sys
import numpy as np
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB').crop((618, 258, 1258, 386))
a = np.asarray(im).astype(np.float32)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
# 金の文字は赤が強く、背景は暗い青緑。赤から青を引いた値でマスクを作る
key = np.clip(((R - B) - 18) / 70, 0, 1)
lum = np.clip((0.3 * R + 0.59 * G + 0.11 * B - 40) / 90, 0, 1)
alpha = np.maximum(key, lum * key ** 0.3)
alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255
rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save(out)
print(im.size, 'alpha mean', round(float(alpha.mean()), 3))
