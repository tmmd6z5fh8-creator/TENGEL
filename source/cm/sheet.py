# 確認用：コマを縮めて横に並べる
import sys
from PIL import Image
out, *fs = sys.argv[1:]
W = 400; H = int(W * 1920 / 1080)
sheet = Image.new('RGB', (W * len(fs) + 8 * (len(fs) - 1), H), (255, 255, 255))
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGB').resize((W, H), Image.LANCZOS)
    sheet.paste(im, (i * (W + 8), 0))
sheet.save(out)
