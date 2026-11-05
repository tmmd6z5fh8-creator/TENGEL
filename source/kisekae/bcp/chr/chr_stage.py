# キャラだけ 動かす（実験）：切りぬいた 絵（chr_split.py の 出力）を アプリの 舞台（390×844pt の 3倍）の 絵に する
#   python3 chr_stage.py <デザインの フォルダ（cfg.json・geom.json・fgmask.png）> <chr の 出力（bgx.png・<id>.png）> <SRV> <キャラの 設定 json> <出す json>
#   キャラの 設定 = { parts: [{ id, kind, dp（ぷるんの 遅れ 秒）, dt（向きの 遅れ 秒）, o?（動きの まん中：絵の px。ない ときは 足もと＝いちばん 下の まん中） }] }
#   出す：bcp_<name>x.webp（キャラなしの 背景）・bcp_<name>x_fg.webp（前の 絵から キャラを のぞいた もの：前の 絵が ある デザイン だけ）・
#         bcp_<name>_c<n>.webp（キャラ：絵の ある 所 だけ 切りぬく＝小さい 絵）と window.__BCPCHR の 1つ分（box・o は 舞台の pt）
import json, os, shutil, subprocess, sys, tempfile
import numpy as np, cv2
from PIL import Image
H_ = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(os.path.dirname(H_), 'bcp_bg.py')
if not os.path.exists(BG): BG = '/home/claude/tengel/source/kisekae/bcp/bcp_bg.py'
D, O, SRV, PC, OUTJ = sys.argv[1:6]
cfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
g = json.load(open(os.path.join(D, 'geom.json')))
S, OX, OY = g['S'], g['OX'], g['OY']; K = 3; Wc, Hc = 390 * K, 844 * K
Mx = np.array([[S * K, 0, OX * K], [0, S * K, OY * K]], np.float32)
name = cfg['name']; P = json.load(open(PC, encoding='utf8')); parts = P['parts']
os.makedirs(SRV, exist_ok=True)
# 1) キャラなしの 背景（上と 下の うめ方も bcp_bg.py と 同じ）・前の 絵からも キャラを のぞく（キャラが 動いた とき、すき間に アプリの 行が 見える）
tmp = tempfile.mkdtemp()
c2 = json.loads(json.dumps(cfg)); c2['name'] = name + 'x'
shutil.copy(os.path.join(O, 'bgx.png'), os.path.join(tmp, 'clean.png'))
if os.path.exists(os.path.join(D, 'src.png')): shutil.copy(os.path.join(D, 'src.png'), os.path.join(tmp, 'src.png'))
alls = None
for p in parts:
    a = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3].astype(np.float32) / 255
    alls = a if alls is None else np.maximum(alls, a)
has_fg = bool(cfg.get('fg')) and os.path.exists(os.path.join(D, 'fgmask.png'))
fm = None
if has_fg:
    fm = np.asarray(Image.open(os.path.join(D, 'fgmask.png')).convert('L')).astype(np.float32) / 255
    # 前の 絵から キャラを のぞく：キャラが まるごと おおう 所（alpha≒1）は すき通し・キャラの やわらかい ふちは
    #   「キャラの 前の 絵（fm×キャラ）を 上に 重ねて ちょうど 元の 前の 絵の こさ（fm）」に なる こさ（止まって いる とき 元と 同じ）
    fa = np.where(alls >= 0.999, 0.0, fm * (1 - alls) / np.maximum(1 - alls * fm, 1e-6))
    fa = np.clip(fa, 0, 1)
    bgx = np.asarray(Image.open(os.path.join(O, 'bgx.png')).convert('RGB'))
    Image.fromarray(np.dstack([bgx, (fa * 255).astype(np.uint8)]), 'RGBA').save(os.path.join(tmp, 'fg.png'))
else:
    c2.pop('fg', None)
json.dump(c2, open(os.path.join(tmp, 'cfg.json'), 'w'), ensure_ascii=False)
subprocess.run(['python3', BG, tmp], env=dict(os.environ, SRV=SRV), check=True, stdout=subprocess.DEVNULL)
shutil.rmtree(tmp, ignore_errors=True)
ent = {'bgx': f'bcp_{name}x.webp', 'fgx': (f'bcp_{name}x_fg.webp' if has_fg else None), 'layers': []}
# 2) キャラ：舞台の 3倍に 置いて、絵の ある 所 だけ 切りぬく（3 の 倍数で 切る＝pt が きっちり）
for n, p in enumerate(parts, 1):
    L = np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA')).astype(np.float32)
    al0 = L[..., 3] / 255
    pm = L[..., :3] * al0[..., None]
    w4 = cv2.warpAffine(np.dstack([pm, L[..., 3]]), Mx, (Wc, Hc), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    al = np.clip(w4[..., 3], 0, 255); rgb = np.clip(w4[..., :3] / np.maximum(al[..., None] / 255.0, 1e-3), 0, 255); rgb[al < 1] = 0
    ys, xs = np.where(al > 2)
    x0 = max(0, (xs.min() - 6) // 3 * 3); y0 = max(0, (ys.min() - 6) // 3 * 3)
    x1 = min(Wc, -(-(xs.max() + 7) // 3) * 3); y1 = min(Hc, -(-(ys.max() + 7) // 3) * 3)
    crop = np.dstack([rgb, al])[y0:y1, x0:x1].astype(np.uint8)
    fn = f'bcp_{name}_c{n}.webp'
    Image.fromarray(crop, 'RGBA').save(os.path.join(SRV, fn), quality=90)
    # キャラの 前の 絵（ボードの 前に 出る 所 だけ＝前の 絵の マスク×キャラ）：アプリの ボードの 上に 同じ 動きで 重ねる
    ffn = None
    if fm is not None:
        fmw = cv2.warpAffine(fm, Mx, (Wc, Hc), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        alf = np.clip(al * fmw, 0, 255)
        if (alf > 8).sum() > 30:
            ffn = f'bcp_{name}_c{n}f.webp'
            cf = np.dstack([rgb, alf])[y0:y1, x0:x1].astype(np.uint8)
            Image.fromarray(cf, 'RGBA').save(os.path.join(SRV, ffn), quality=90)
    yy_, xx_ = np.where(al0 > 0.5)
    if isinstance(p.get('o'), list):
        ox, oy = p['o']
    elif p.get('o') == 'contact' and os.path.exists(os.path.join(O, 'board.png')):   # ボードに ふれる 所の まん中（そこは 動かない＝ボードの ふちで 切れて 見えない）
        bmk = np.asarray(Image.open(os.path.join(O, 'board.png')).convert('L')) > 127
        selc = (al0 > 0.5) & cv2.dilate(bmk.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        if selc.sum() < 20: selc = (al0 > 0.5) & cv2.dilate(bmk.astype(np.uint8), np.ones((25, 25), np.uint8)).astype(bool)
        cy_, cx_ = np.where(selc); ox, oy = float(cx_.mean()), float(cy_.mean())
    elif p.get('o') == 'bottom_center':   # まとめた キャラ：はばの まん中・いちばん 下（まん中から 左右に 同じだけ 動く）
        ox, oy = float((xx_.min() + xx_.max()) / 2), float(yy_.max())
    elif p.get('o') == 'top':      # 上の はし（ボードを 持つ 手 など：そこは 動かない）
        yt = yy_.min(); sel = yy_ <= yt + 6; ox, oy = float(xx_.mean()), float(yt)
    else:                          # 足もと：いちばん 下の 6行の まん中（たての まん中は キャラの まん中）
        yb = yy_.max(); sel = yy_ >= yb - 6; ox, oy = float(xx_[sel].mean()), float(yb)
    o_pt = [round(OX + S * ox, 2), round(OY + S * oy, 2)]
    # 大きさ：ぷるんの つぶれは キャラの 高さ 205pt まで 3.8%（それより 大きい キャラは 同じ pt に）・向きは はば 300pt まで 4度
    w_pt = (xx_.max() - xx_.min()) * S; h_pt = (yy_.max() - yy_.min()) * S
    amp = round(min(1.0, 205.0 / max(h_pt, 1)), 3); deg = round(4.0 * min(1.0, 300.0 / max(w_pt, 1)), 2)
    lay = {'src': fn, 'box': [x0 / 3, y0 / 3, (x1 - x0) / 3, (y1 - y0) / 3], 'o': o_pt, 'amp': p.get('amp', amp), 'deg': p.get('deg', deg)}
    if ffn: lay['f'] = ffn
    for k in ('dp', 'dt', 'ax'):
        if k in p: lay[k] = p[k]
    ent['layers'].append(lay)
    print(p['id'], fn, 'box pt', [round(v, 1) for v in lay['box']], 'o', o_pt, 'amp', lay['amp'], 'deg', lay['deg'], os.path.getsize(os.path.join(SRV, fn)))
# 3) キャラの 前に ある 動かない 物（occl の 形 × キャラでない 所）：キャラの 上・アプリの ボードの 下に 重ねる（キャラが その うしろに まわりこむ）
OCP = os.path.join(O, 'occl.png')
if os.path.exists(OCP) or P.get('occl'):
    Hh, Ww = alls.shape
    if os.path.exists(OCP):      # chr_split.py の ボードの うしろの キャラ（behind）の そばの ボード
        oa = np.asarray(Image.open(OCP).convert('L')).astype(np.float32) / 255
    else:
        om = np.zeros((Hh, Ww), np.uint8)
        for sh in P['occl']:
            if 'poly' in sh: cv2.fillPoly(om, [np.round(np.array(sh['poly'], np.float64) * 8).astype(np.int32)], 1, shift=3)
            elif 'rect' in sh: x0_, y0_, x1_, y1_ = sh['rect']; om[y0_:y1_, x0_:x1_] = 1
            elif 'mask' in sh:
                mm_ = np.asarray(Image.open(sh['mask']).convert('L')) > 127; h_, w_ = min(Hh, mm_.shape[0]), min(Ww, mm_.shape[1]); om[:h_, :w_] |= mm_[:h_, :w_].astype(np.uint8)
        oa = om.astype(np.float32) * np.clip(1 - alls / 0.02, 0, 1)                      # キャラの 所（やわらかい ふちも）は 入れない
    src_ = np.asarray(Image.open(os.path.join(D, 'clean.png')).convert('RGB')).astype(np.float32)   # 元の 絵（ふちの 光の 所は キャラの 上に 元の 絵を 重ねる）
    pm = np.dstack([src_ * oa[..., None], oa * 255])
    w4 = cv2.warpAffine(pm, Mx, (Wc, Hc), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    al = np.clip(w4[..., 3], 0, 255); rgb = np.clip(w4[..., :3] / np.maximum(al[..., None] / 255.0, 1e-3), 0, 255); rgb[al < 1] = 0
    ys, xs = np.where(al > 2)
    if len(xs):
        x0 = max(0, (xs.min() - 6) // 3 * 3); y0 = max(0, (ys.min() - 6) // 3 * 3)
        x1 = min(Wc, -(-(xs.max() + 7) // 3) * 3); y1 = min(Hc, -(-(ys.max() + 7) // 3) * 3)
        fn = f'bcp_{name}x_oc.webp'
        Image.fromarray(np.dstack([rgb, al])[y0:y1, x0:x1].astype(np.uint8), 'RGBA').save(os.path.join(SRV, fn), quality=92)
        ent['oc'] = {'src': fn, 'box': [x0 / 3, y0 / 3, (x1 - x0) / 3, (y1 - y0) / 3]}
        print('occluder', fn, 'px', int((oa > 0.5).sum()))
    # ボードの 前（前の 絵の マスク）に かかる 所：アプリの ボードと キャラの 前の 絵（f）の 上にも 重ねる（いちばん 上・動かない）＝occl_top
    #   （二人でしょんぼりの 青い 線：ボードの 前で 耳に かかる 所も 動かない）
    if P.get('occl_top') and fm is not None:
        ot = oa * fm
        pm = np.dstack([src_ * ot[..., None], ot * 255])
        w4 = cv2.warpAffine(pm, Mx, (Wc, Hc), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        al = np.clip(w4[..., 3], 0, 255); rgb = np.clip(w4[..., :3] / np.maximum(al[..., None] / 255.0, 1e-3), 0, 255); rgb[al < 1] = 0
        ys, xs = np.where(al > 2)
        if len(xs):
            x0 = max(0, (xs.min() - 6) // 3 * 3); y0 = max(0, (ys.min() - 6) // 3 * 3)
            x1 = min(Wc, -(-(xs.max() + 7) // 3) * 3); y1 = min(Hc, -(-(ys.max() + 7) // 3) * 3)
            fn = f'bcp_{name}x_ot.webp'
            Image.fromarray(np.dstack([rgb, al])[y0:y1, x0:x1].astype(np.uint8), 'RGBA').save(os.path.join(SRV, fn), quality=92)
            ent['ot'] = {'src': fn, 'box': [x0 / 3, y0 / 3, (x1 - x0) / 3, (y1 - y0) / 3]}
            print('top occluder', fn, 'px', int((ot > 0.5).sum()))
allj = json.load(open(OUTJ, encoding='utf8')) if os.path.exists(OUTJ) else {}
allj[name] = ent
json.dump(allj, open(OUTJ, 'w'), ensure_ascii=False, indent=1)
print('stage', name, 'bgx', ent['bgx'], 'fgx', ent['fgx'], 'layers', len(ent['layers']))
