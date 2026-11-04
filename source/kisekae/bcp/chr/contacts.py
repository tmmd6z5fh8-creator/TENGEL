# 見なおし用：キャラ どうしが ふれて いる 長さ（px）：python3 contacts.py <chr の 出力> …
import sys, json, os, numpy as np, cv2
for O in sys.argv[1:]:
    c = json.load(open(os.path.join(O, 'cfg.json'))); ids = [p['id'] for p in c['parts']]
    A = {i: (np.asarray(__import__('PIL.Image', fromlist=['x']).open(os.path.join(O, i + '.png')).convert('RGBA'))[..., 3] > 127).astype(np.uint8) for i in ids}
    out = []
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            ma, mb = A[ids[a]], A[ids[b]]
            ea = ma.astype(bool) & ~cv2.erode(ma, np.ones((3, 3), np.uint8)).astype(bool)
            n = int((ea & cv2.dilate(mb, np.ones((5, 5), np.uint8)).astype(bool)).sum())
            if n > 15:
                ys, xs = np.where(ea & cv2.dilate(mb, np.ones((5, 5), np.uint8)).astype(bool))
                out.append(f'{ids[a]}-{ids[b]}:{n}px@({int(xs.mean())},{int(ys.mean())})')
    print(O.split('/')[-1], ' '.join(out) if out else '(ふれて いない)')
