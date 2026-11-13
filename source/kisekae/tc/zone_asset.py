# ポイント特化ゾーンの レバーの 絵を アプリ用に 置く（第4.165版・まさちゃん 2026/11/13 12:51「トレーニングセンターの抽選に ・ポイントの特化ゾーンを作る
#   (レバーを押し込め！で、60%で上乗せ) … レバーの画像は、一個目のファイル」＋ Meshy の 3D（Golden_Lever_Prize_Banner：金の 台に 赤い 玉の レバー・上に 金の 矢印・
#   きらめき 2つ・ピンクの P 2つ・手前に リボン「レバーを押し込め！」。1つの メッシュ・約85万 三角形・つながった かたまりは 6つ＝台と レバーと リボン／矢印／きらめき×2／P×2））
#   python3 kisekae/tc/zone_asset.py <まさちゃんの GLB> [ios/tc_assets]
#   → 絵 3まい ＋ 置き場所の 表（アプリの tc/tc_fx.js の zone が 重ねて 描く：下から back → ball → arrow）
#       tc_zn_back.webp ：赤い 玉と 矢印を のぞいた ぜんぶ（台・輪・軸・リボン・きらめき・P）
#       tc_zn_ball.webp ：赤い 玉 だけ（押すと 下へ push ぶん 動く ＝ 軸が 短く 見えて 玉が 輪に 乗る ＝ 押しこんだ 見え方）
#       tc_zn_arrow.webp：上の 金の 矢印（「押して」の 合図で 上下に ゆれる）
#       tc_zn_geom.json ：{ w, h（絵 ぜんぶの 大きさ）, parts:{ back|ball|arrow:{ x, y, w, h } }, push（押しこむ 長さ px）, ball:[まん中 x, y, 半径] }
#     玉は 輪より 大きい（輪の 中へは 沈まない）：押しこんだ 玉は どこでも 台より 手前（奥行きを くらべて 確かめた）＝ 玉を 台の 上に 重ねる だけで 正しい 見え方
#   ・玉は 台と つながった 1つの かたまり（溶けて いる）→ 色（赤）と 場所（玉の まわりの だ円体）で 三角形を えらんで 切り分ける。玉を 外した 台には 軸の 切り口が のこる（いつも 玉の うしろ）
#   ・カメラ：正面から 少し 上（まさちゃんの 絵の 見え方）・画角 20°。3倍で 描いて ちぢめる。ふちの すき通り具合も 3倍の 細かさで 数える
#   ・描くのは kisekae/r3d/glb（numpy ＋ 小さな C の ラスタライザ）。3D・できた 絵は リポジトリに 入れない（ios/tc_assets/ は .gitignore）
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc/tc_fx.js の 名前も かえる）
#   ・kisekae/tc/collect_assets.py は 出す フォルダを 作り直す ので、走らせた あとは これを もう一度。足した あとは python3 kisekae/lite_assets.py
import io, json, os, sys, time
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'r3d', 'glb'))
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

W_R, H_R, SS = 1200, 860, 3            # 描く 大きさ（絵は 幅 1040px ほど ＝ 画面の 幅 347pt の 3倍）・細かさの 倍
ELEV, FOV, DIST = 0.16, 20.0, 1.9      # カメラ：上への かたむき（tan）・画角・はなれ具合（絵の 対角線の 何倍）
BALL_C, BALL_A = (0.0, 0.12, 0.088), (0.30, 0.30, 0.26)      # 玉を えらぶ だ円体（まん中・半径）
PUSH_K = 0.0425                        # 押しこむ 長さ（描く 幅の 何倍）＝ 玉が 輪に 乗る ところ まで
PAD, Q = 6, 90
NAMES = ('tc_zn_back.webp', 'tc_zn_ball.webp', 'tc_zn_arrow.webp', 'tc_zn_geom.json')


def parts(p):
    """メッシュを 部品に：つながった かたまり（6つ）＋ いちばん 大きい かたまりの 中の 赤い 玉 → { back, ball, arrow } の 三角形の しるし"""
    pos, idx = p.pos, p.idx
    key = np.round(pos * 1e5).astype(np.int64); _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.ravel(); nw = int(inv.max()) + 1
    ti = inv[idx]
    g = coo_matrix((np.ones(len(ti) * 3, np.int8), (np.concatenate([ti[:, 0], ti[:, 1], ti[:, 2]]), np.concatenate([ti[:, 1], ti[:, 2], ti[:, 0]]))), shape=(nw, nw))
    nc, lab = connected_components(g, directed=False); tl = lab[ti[:, 0]]
    cnt = np.bincount(tl, minlength=nc); main = int(np.argmax(cnt))
    cen = pos[idx].mean(1)
    top = [k for k in range(nc) if k != main]
    arrow = max(top, key=lambda k: cen[tl == k][:, 1].mean())            # いちばん 上の かたまり＝矢印
    assert nc == 6 and cnt[main] > 0.9 * len(idx) and abs(cen[tl == arrow][:, 0].mean()) < 0.05, ('かたまりの 数が ちがう（3D が かわった？）', nc, cnt.tolist())
    tex = p.mat.base_tex.tex.img; th, tw = tex.shape[:2]; uvc = p.uv[idx].mean(1)
    col = tex[np.clip((uvc[:, 1] % 1) * th, 0, th - 1).astype(int), np.clip((uvc[:, 0] % 1) * tw, 0, tw - 1).astype(int), :3]
    red = (col[:, 0] > 0.45) & (col[:, 1] < 0.42) & (col[:, 2] < 0.42) & (col[:, 0] > col[:, 1] * 1.6)
    ball = (tl == main) & red & ((((cen - np.array(BALL_C)) / np.array(BALL_A)) ** 2).sum(1) < 1)
    assert 8000 < int(ball.sum()) < 14000, ('玉の 三角形の 数が おかしい', int(ball.sum()))
    return {'back': (tl != arrow) & ~ball, 'ball': ball, 'arrow': tl == arrow}


def webp(rgb, a):
    """色（0〜1）と すき通り具合（0〜1）→ WebP の 中身。すき通った 所の 色は 0"""
    im = np.dstack([np.clip(rgb, 0, 1) * 255 + 0.5, np.clip(a, 0, 1)[..., None] * 255 + 0.5]).astype(np.uint8); im[im[..., 3] == 0] = 0
    buf = io.BytesIO(); Image.fromarray(im, 'RGBA').save(buf, 'WEBP', quality=Q, method=6, alpha_quality=100); return buf.getvalue()


def box(a, pad=PAD):
    ys, xs = np.nonzero(a > 0.004)
    return max(int(xs.min()) - pad, 0), max(int(ys.min()) - pad, 0), min(int(xs.max()) + 1 + pad, a.shape[1]), min(int(ys.max()) + 1 + pad, a.shape[0])


def build(src):
    import glb
    from raster import Camera, render, tonemap
    t0 = time.time(); m = glb.load(src); p = m.flatten()[0]; mk = parts(p)
    sub = lambda k: glb.Prim(p.pos, p.nrm, p.uv, p.idx[mk[k]], p.mat, tangent=p.tangent, color=p.color)
    lo, hi = p.pos.min(0), p.pos.max(0); c = (lo + hi) / 2; diag = float(np.linalg.norm(hi - lo))
    d = np.array([0, ELEV, 1.0]); d /= np.linalg.norm(d)
    cam = Camera.look_at(c + d * diag * DIST, c + np.array([0, -0.01, 0]), fov_y=FOV, W=W_R, H=H_R)
    L = {}
    for k in ('back', 'ball', 'arrow'):
        o = render([sub(k)], cam, ss=SS, want=('rgb', 'alpha')); L[k] = (tonemap(o['rgb']), o['alpha'].astype(np.float32))
    full = render([p], cam, ss=SS, want=('rgb', 'alpha')); F = (tonemap(full['rgb']), full['alpha'].astype(np.float32))
    push = int(round(PUSH_K * W_R))
    # 押しこんだ 玉は どこでも 台より 手前（玉を 台の 上に 重ねる だけで よい）：粗い 細かさで 奥行きを くらべて 確かめる
    lc = cam.scaled(0.5); D = {k: render([sub(k)], lc, ss=1, want=('depth',))['depth'] for k in ('back', 'ball')}
    sh = int(round(push * 0.5)); bd = np.full_like(D['ball'], np.inf); bd[sh:] = D['ball'][:-sh]
    both = np.isfinite(bd) & np.isfinite(D['back']); assert both.sum() > 1000 and not (D['back'][both] < bd[both]).any(), '押しこんだ 玉より 手前に 台が ある（重ねる 順を 見直す）'
    # 重ねた 絵（back → ball → arrow）が、まるごと 描いた 絵と 同じ 形（すき通り具合が 同じ ＝ 玉を 切り分けた さかいに すきまが ない）。
    #   色は 玉の 下の 台（輪の まわり）だけ 少し ちがう：まるごとの 絵には 玉の 影が 台に 落ちる・重ねる 絵の 台には 落ちない（玉が 動く ので 影は つけない）
    comp = np.zeros((H_R, W_R, 3), np.float32); ca = np.zeros((H_R, W_R), np.float32)
    for k in ('back', 'ball', 'arrow'):
        rgb, a = L[k]; comp = comp * (1 - a[..., None]) + rgb * a[..., None]; ca = ca + a * (1 - ca)
    err = np.abs(comp - F[0] * F[1][..., None]); bad = float((err.max(-1) > 0.08).mean())
    assert bad < 0.03 and float(np.abs(ca - F[1]).mean()) < 0.002, ('重ねた 絵が まるごとの 絵と ちがう', bad, float(np.abs(ca - F[1]).mean()))
    X0, Y0, X1, Y1 = box(F[1]); geom = {'w': X1 - X0, 'h': Y1 - Y0, 'push': push, 'parts': {}}
    out = {}
    for k in ('back', 'ball', 'arrow'):
        rgb, a = L[k]; x0, y0, x1, y1 = box(a, 2)
        out[f'tc_zn_{k}.webp'] = webp(rgb[y0:y1, x0:x1], a[y0:y1, x0:x1]); geom['parts'][k] = {'x': x0 - X0, 'y': y0 - Y0, 'w': x1 - x0, 'h': y1 - y0}
    ys, xs = np.nonzero(L['ball'][1] > 0.5); geom['ball'] = [round(float(xs.mean()) - X0, 1), round(float(ys.mean()) - Y0, 1), round(float(xs.max() - xs.min()) / 2, 1)]
    out['tc_zn_geom.json'] = (json.dumps(geom, separators=(',', ':')) + '\n').encode()
    print(f'描いた：{time.time() - t0:.0f}秒・絵 {geom["w"]}×{geom["h"]}・押しこむ 長さ {push}px・まるごとの 絵と 色が ちがう 所（玉の 影）{bad * 100:.2f}%')
    return out, geom


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(HERE)), 'ios', 'tc_assets')
    assert os.path.isdir(out_dir), out_dir
    out, geom = build(src)
    for n in NAMES:                      # 先に ぜんぶ 見る（とちゅうで 止まって 半分 だけ 置かれない ように）
        dst = os.path.join(out_dir, n)
        if os.path.exists(dst) and open(dst, 'rb').read() != out[n]: raise SystemExit(f'もう ある ファイルと 中身が ちがう（上書きしない）：{dst}')
    for n in NAMES:
        dst = os.path.join(out_dir, n)
        if os.path.exists(dst): print('同じ ものが もう ある：', n); continue
        with open(dst, 'xb') as f: f.write(out[n])
        print(f'{n}：{len(out[n]):,}B' + (f'（{geom["parts"][n[6:-5]]}）' if n.endswith('.webp') else ''))


if __name__ == '__main__':
    main()
