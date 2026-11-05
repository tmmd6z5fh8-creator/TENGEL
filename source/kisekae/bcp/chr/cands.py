# 見なおし用：背景に のこった キャラの かけら（耳・ひづめ・しっぽ・腕）の 候補を さがして ならべる
#   候補 = モデルが キャラと 見る 所（M > thr）で、キャラの 層に 入って いない（背景に のこる）所の うち、ぬいた 所の すぐ そば（dist px 以内）
#   python3 cands.py <出す png> <chr の 出力>:<元の clean.png> … [--thr 0.35] [--dist 30] [--min 25]
#   1つの 候補 = 元の 絵（赤＝ぬいた 所の さかい・水色＝候補）｜キャラなしの 背景
import sys, json, os
import numpy as np, cv2
import scipy.ndimage as ndi
from PIL import Image, ImageDraw
a = sys.argv[1:]
def opt(k, d):
    if k in a: i = a.index(k); v = float(a[i + 1]); del a[i:i + 2]; return v
    return d
THR, DIST, MIN = opt('--thr', 0.35), opt('--dist', 30), opt('--min', 25)
out = a[0]; tiles = []
for arg in a[1:]:
    O, cl = arg.split(':')
    c = json.load(open(os.path.join(O, 'cfg.json')))
    src = np.asarray(Image.open(cl).convert('RGB')).astype(np.int32); H, W = src.shape[:2]
    bg = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB')).astype(np.int32)
    M = np.zeros((H, W), np.float32)
    for f in c['masks']: M = np.maximum(M, np.asarray(Image.open(f).convert('L')).astype(np.float32) / 255)
    lay = np.zeros((H, W), bool)
    for p in c['parts']:
        lay |= np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3] > 40
    hole = (np.abs(src - bg).max(-1) > 2) | lay
    if os.path.exists(os.path.join(O, 'occl.png')):          # ボードの うしろの キャラ：ボードの 前に 重ねる 所は のこって いて よい
        hole |= np.asarray(Image.open(os.path.join(O, 'occl.png')).convert('L')) > 127
    hole = cv2.morphologyEx(hole.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)
    d = ndi.distance_transform_edt(~hole)
    cand = (M > THR) & ~ndi.binary_dilation(hole, iterations=2) & (d <= DIST)
    if c.get('board') and os.environ.get('SKIP_BOARD'):     # 前は 板の 中を 見なかった（今は 板に かかる キャラも キャラに 入れる ので 見る）
        q = np.array(c['board']['quad'], np.float64); bm = np.zeros((H, W), np.uint8); cv2.fillPoly(bm, [np.round(q).astype(np.int32)], 1)
        fm = np.asarray(Image.open(c['board']['fgmask']).convert('L')) > 127 if c['board'].get('fgmask') else np.zeros((H, W), bool)
        cand &= ~(bm.astype(bool) & ~fm)
    lab, n = ndi.label(cand)
    if not n: print(O.split('/')[-1], 'no cands'); continue
    sz = ndi.sum(cand, lab, range(1, n + 1)); objs = ndi.find_objects(lab)
    e = hole & ~cv2.erode(hole.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    ce = cand & ~cv2.erode(cand.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    vis = src.copy(); vis[e] = [255, 40, 40]; vis[ce] = [0, 255, 255]
    order = sorted(range(n), key=lambda k: -sz[k])
    k_ = 0
    for k in order:
        if sz[k] < MIN: continue
        sl = objs[k]; cy, cx = (sl[0].start + sl[0].stop) // 2, (sl[1].start + sl[1].stop) // 2
        hh = max(40, (sl[0].stop - sl[0].start) // 2 + 25); ww = max(40, (sl[1].stop - sl[1].start) // 2 + 25); r = max(hh, ww)
        y0, y1, x0, x1 = max(0, cy - r), min(H, cy + r), max(0, cx - r), min(W, cx + r)
        A = Image.fromarray(vis[y0:y1, x0:x1].astype(np.uint8)); B = Image.fromarray(bg[y0:y1, x0:x1].astype(np.uint8))
        s = 150 / max(A.width, A.height); A = A.resize((max(1, int(A.width * s)), max(1, int(A.height * s))), Image.LANCZOS); B = B.resize(A.size, Image.LANCZOS)
        t = Image.new('RGB', (306, 166), 'white'); t.paste(A, (0, 16)); t.paste(B, (156, 16))
        ImageDraw.Draw(t).text((2, 2), f'{O.split("/")[-1]} ({cx},{cy}) {int(sz[k])}px', fill=(0, 0, 0)); tiles.append(t); k_ += 1
        if k_ >= 12: break
    print(O.split('/')[-1], 'cands', int((sz >= MIN).sum()))
if tiles:
    NC = 4; R = (len(tiles) + NC - 1) // NC
    S = Image.new('RGB', (NC * 312, R * 170), (230, 230, 230))
    for i, t in enumerate(tiles): S.paste(t, ((i % NC) * 312, (i // NC) * 170))
    S.save(out); print(out, S.size, len(tiles))
