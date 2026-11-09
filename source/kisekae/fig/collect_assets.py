# 思い出フィギュアの 形・絵を アプリ用に 集める（ios/fig_assets/ に 名前だけで ならべる：build_ios.py が Resources/ に 入れる）
#   python3 kisekae/fig/collect_assets.py <作業フォルダ（out/ に figN.npz・figN_c/n/m.webp・figN_board.json・shelf.npz・shelf_c1〜7.webp／thumbs/figN.png）> [出す フォルダ ios/fig_assets]
#   ・まさちゃんの フィギュア 8体・棚の 3D と それから 作った もの は 公開の リポジトリに 入れない（.gitignore：ios/fig_assets/）。この スクリプトだけ 入れる
#   ・作り方（作業フォルダの 道具）：fig_bake.py（形を へらして 色・法線・金属／あらさ を 焼く）→ board_find.py（ボードの 板）→
#     shelf_align.py・shelf_proj.py（棚の 3D に 7色の 画像を 正面から 貼る）。くわしくは kisekae/fig/README.md
#   ・形：位置は 16bit（箱の 中の 割合）・UV 16bit・三角の 番号。絵：色 2048・法線 1024・金属／あらさ 512（WebP：1体を 大きく 見る 部屋）
#     ブース（小さく 8体）用に 半分の 絵（fgN_cs・ns・ms）・作る 時に 選ぶ 写真（fgN_t：thumbs/figN.png を 高さ 360 に）
import json, os, shutil, sys
import numpy as np
from PIL import Image
SRC = os.path.abspath(sys.argv[1]); O = os.path.join(SRC, 'out')
OUT = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', '..', 'ios', 'fig_assets'))
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
got = {}
# フィギュアの 種類（値段は アプリの 中：通常 22000P・幻の馬 30000P・神様馬 32000P・幻の馬＆神様馬 36000P）と ボードの 色
KIND = {1: 'normal', 2: 'normal', 3: 'normal', 4: 'normal', 5: 'normal', 6: 'kami', 7: 'mab', 8: 'both'}
PAL = {6: 'gold', 7: 'amethyst', 8: 'duel'}


def pack(npz, name):
    d = np.load(npz); V = d['V'].astype(np.float64); T = d['T'].astype(np.int64); UVc = d['UVc'].astype(np.float64)
    cv = T.reshape(-1); cu = UVc.reshape(-1, 2); q = np.round(np.clip(cu, 0, 1) * 65535).astype(np.int64)
    key = cv * (65536 * 65536) + q[:, 0] * 65536 + q[:, 1]
    _, first, inv = np.unique(key, return_index=True, return_inverse=True)
    P = V[cv[first]]; UV = q[first]; I = inv.astype(np.uint32)
    lo, hi = P.min(0), P.max(0); sc = np.maximum(hi - lo, 1e-9)
    qp = np.round((P - lo) / sc * 65535).astype(np.uint16)
    idx32 = len(P) > 65535
    parts = (('pos', qp.tobytes()), ('uv', UV.astype(np.uint16).tobytes()), ('idx', I.astype(np.uint32 if idx32 else np.uint16).tobytes()))
    lay = {}; buf = b''
    for k, b in parts:
        while len(buf) % 4: buf += b'\0'
        lay[k] = [len(buf), len(b)]; buf += b
    open(os.path.join(OUT, name + '.bin'), 'wb').write(buf); got[name + '.bin'] = len(buf)
    return {'v': int(len(P)), 'i': int(len(I)), 'idx32': bool(idx32), 'layout': lay, 'qo': lo.round(6).tolist(), 'qs': sc.round(6).tolist(), 'bbox': [lo.round(4).tolist(), hi.round(4).tolist()]}


def webp(src, name, size, q=90):
    im = Image.open(src).convert('RGB')
    if im.width != size: im = im.resize((size, size), Image.LANCZOS)
    p = os.path.join(OUT, name); im.save(p, 'WEBP', quality=q, method=6); got[name] = os.path.getsize(p)


def thumb(src, name, h=360):
    im = Image.open(src).convert('RGBA'); w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS); p = os.path.join(OUT, name); im.save(p, 'WEBP', quality=88, method=6); got[name] = os.path.getsize(p)
    return [w, h]


meta = {'v': 1, 'figs': {}, 'shelf': {}}
for n in range(1, 9):
    if not (os.path.exists(os.path.join(O, f'fig{n}.npz')) and os.path.exists(os.path.join(SRC, 'thumbs', f'fig{n}.png'))): print('※ まだ ない：fig', n); continue      # 作りかけでも ためせる ように
    m = pack(os.path.join(O, f'fig{n}.npz'), f'fg{n}')
    webp(os.path.join(O, f'fig{n}_c.webp'), f'fg{n}_c.webp', 2048, 90)
    webp(os.path.join(O, f'fig{n}_n.webp'), f'fg{n}_n.webp', 1024, 92)
    webp(os.path.join(O, f'fig{n}_m.webp'), f'fg{n}_m.webp', 512, 90)
    webp(os.path.join(O, f'fig{n}_c.webp'), f'fg{n}_cs.webp', 1024, 88)
    webp(os.path.join(O, f'fig{n}_n.webp'), f'fg{n}_ns.webp', 512, 92)
    webp(os.path.join(O, f'fig{n}_m.webp'), f'fg{n}_ms.webp', 256, 90)
    tsz = thumb(os.path.join(SRC, 'thumbs', f'fig{n}.png'), f'fg{n}_t.webp')
    bd = json.load(open(os.path.join(O, f'fig{n}_board.json')))
    m.update({'tex': f'fg{n}_c.webp', 'ntex': f'fg{n}_n.webp', 'mtex': f'fg{n}_m.webp', 'thumb': f'fg{n}_t.webp', 'tsz': tsz, 'board': {'c': [round(v, 4) for v in bd['c']], 'w': round(bd['w'], 4), 'h': round(bd['h'], 4)}, 'kind': KIND[n], 'pal': PAL.get(n, 'gold')})
    json.dump(m, open(os.path.join(OUT, f'fg{n}.json'), 'w')); meta['figs'][str(n)] = {'kind': KIND[n], 'pal': PAL.get(n, 'gold'), 'tsz': tsz}
if os.path.exists(os.path.join(O, 'shelf_c7.webp')):
    m = pack(os.path.join(O, 'shelf.npz'), 'fg_shelf')
    for c in range(1, 8): webp(os.path.join(O, f'shelf_c{c}.webp'), f'fg_shelf_c{c}.webp', 2048, 90)
    m.update({'tex': [f'fg_shelf_c{c}.webp' for c in range(1, 8)]})
    json.dump(m, open(os.path.join(OUT, 'fg_shelf.json'), 'w'))
else: print('※ まだ ない：棚')
json.dump(meta, open(os.path.join(OUT, 'fg_meta.json'), 'w'))
for f in os.listdir(OUT): got.setdefault(f, os.path.getsize(os.path.join(OUT, f)))
print('集めた', len(got), 'こ', round(sum(got.values()) / 1e6, 1), 'MB →', OUT)
