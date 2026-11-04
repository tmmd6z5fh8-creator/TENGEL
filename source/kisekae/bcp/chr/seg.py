# アニメの 絵の キャラを 切りぬく（isnet-anime・onnxruntime）：python3 seg.py <絵> <x0,y0,x1,y1> <出す mask.png>
import sys
import numpy as np
import onnxruntime as ort
from PIL import Image
src, box, out = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], sys.argv[3]
im = Image.open(src).convert('RGB'); W, H = im.size
crop = im.crop(box); cw, ch = crop.size
x = np.asarray(crop.resize((1024, 1024), Image.LANCZOS), np.float32)
x = x / max(float(x.max()), 1e-6)
x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([1.0, 1.0, 1.0], np.float32)
x = x.transpose(2, 0, 1)[None].astype(np.float32)
s = ort.InferenceSession('/home/claude/work/models/isnet-anime.onnx', providers=['CPUExecutionProvider'])
p = s.run(None, {'img': x})[0][0, 0]
p = (p - p.min()) / max(float(p.max() - p.min()), 1e-6)
m = Image.fromarray((p * 255).astype(np.uint8)).resize((cw, ch), Image.LANCZOS)
full = Image.new('L', (W, H), 0); full.paste(m, (box[0], box[1])); full.save(out)
print('mask', out, 'mean', round(float(np.asarray(m).mean()) / 255, 3))
