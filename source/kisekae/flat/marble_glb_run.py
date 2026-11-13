"""大理石の 壁紙の 絵を まさちゃんの 3D の 馬（flat/marble_glb.py：「Marble Majesty」）で 作る（第4.155版）。壁紙の 動き（kisekae/marble_wall.py）は 前と 同じ・絵と 置く 場所 だけ かわる
   - コマ（frame_list：前の flat/marble_run.py と 同じ 名前・同じ 数 162）：A＝左向きの ふり向き（look 0 → LOOK・2度見の LOOK_OVER）／B＝左 → 右（体が 回る N_TURN−1 コマ）／
     C＝右向きの ふり向き／D＝右 → 左／NL・NR＝左向き・右向きの ヒヒィーン
   - **馬（主役）だけ 高画質**：コマは 画面の 3倍（壁紙の 絵 780×320 の K＝1.5倍）。背景（あたたかい 白・大理石の すじ・金の 月桂樹）は 前の 絵の まま
     （flat/marble_banner.py の background・laurel：780×320）で、コマの 下じきに する ときだけ 1.5倍に のばす
   - シート（look・turnB・turnD・neighL・neighR：よこ COLS コマ）：像が 動く はんい（ぜんぶの コマの 像を 合わせた 四角＋よゆう MARGIN）だけ 背景ごと 切りぬいた コマ
     （すき通しなし・ロスあり）。切りぬく 場所は 画面の 点（pt）の 境目に 合わせる（marble_run.json の crop・frame は 前と 同じ「壁紙の 絵の 画素」＝2で わって pt）
   - 止まった 絵（base：780×320）：背景＋台の 影＋左向きの 像（A00 を 小さく した もの）。動きを 減らす 設定の とき・選ぶ 画面の 小さい 絵にも 使う
   - ずっ！ずっ！で 動く 絵：像と 台と 台の 影（すき通しつき・画面の 3倍）の 右向き spR・左向き spL と、像も 台も 影も ない 背景 だけの 絵 plate（780×320 の 中の 四角・ロスなし）
   - 3D（MARBLE_HORSE_GLB）・コマ・できた 絵は リポジトリに 入れない。リポジトリに 入れる のは marble_run.json・marble_blobs.json・blobs20.json（絵の id）だけ
   python3 flat/marble_glb_run.py <出力フォルダ>            → コマを 描いて（<出力フォルダ>/cache・もう ある コマは 描かない：1コマ 約3秒）、シート・すべる 絵・背景 だけの 絵・止まった 絵・marble_run.json
   python3 flat/marble_glb_run.py <出力フォルダ> --install  → できた 絵を ios/kisekae_blobs/<中身の md5>.webp に 置いて（前の 絵は 消さない・上書きしない）、
                                                              kisekae/marble_blobs.json・blobs20.json（選ぶ 画面の 小さい 絵）・marble_run.json を 書きかえる
   3D を 入れかえた ときは <出力フォルダ>（cache・rig）を 空に して から（コマの 名前は 形 だけで 決まる）
   第4.167版（まさちゃん 2026/11/13「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）：コマは 1/30秒の きざみ。
   - コマ（frame_list）：kisekae/marble_wall.py の 予定（look_frames・turn_frames：1/30秒ごとの 時刻の 形）を そのまま 描く。
     rest＝止まった 像（左向き A・右向き C）／look＝ふり向き（片がわ 37コマ＋動きの とちゅうの 止まった 形 1）／turnB・turnD＝体が 回る 59コマ／neighL・neighR＝ヒヒィーン 77コマ
   - 細かさ：止まった 像（rest）は 画面の 3倍（K＝1.5）の まま。動いて いる 間の コマ（look・turn・neigh）は 画面の 2倍（K_MOVE＝1.0：3倍で 描いた コマを 小さく する）
     ＝コマが 2倍より 多く なっても 1まいの シートの 画素は 前と 同じ くらい（アプリが 絵を 読む 重さを ふやさない）。3倍の コマは cache に のこる"""
import sys, os, json, math, shutil
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import marble_glb as MG
import marble_wall as MWL                        # コマの 予定（1/30秒の きざみ）は ページと 同じ ものを 使う

W, Hh, K = MG.W, MG.Hh, MG.K
COLS = 10                                        # シートの よこの コマ数
MARGIN = 8                                       # 切りぬきの よゆう（壁紙の 絵の 画素：4pt。ふちの ぼかし 3pt が 像に かからない ように）
Q = int(os.environ.get('MARBLE_Q', 90))          # シートの ロスありの 質
BASE_Q = 90                                      # 止まった 絵の 質
SP_Q = 92                                        # すべる 絵（すき通しつき）の 質
SP_HALF = 280                                    # すべる 絵の はば（台の まん中から 左右へ：台の 影が とどく 所まで）
W3, H3 = int(W * K), int(Hh * K)
FPS = MWL.FPS                                    # コマは 1/30秒の きざみ
K_MOVE = 1.0                                     # 動いて いる 間の コマの 細かさ（壁紙の 絵の 何倍か）：1.0 ＝ 画面の 2倍
SCALE = dict(rest=K)                             # シートごとの 細かさ（書いて いない シートは K_MOVE）


def frame_list():
    """{シート: [(名前, psi, look, ヒヒィーンの 時刻 or None)]}：シートごとの コマ。名前は kisekae/marble_wall.py の base_at・tracks と 同じ
       （A・C＝止まった 像／A<しっぽ>・C<しっぽ>＝ふり向き／B<きざみ>・D<きざみ>＝体が 回る／NL<番号>・NR<番号>＝ヒヒィーン）"""
    L, LO, PR = MG.LOOK, MG.LOOK_OVER, MG.PSI_R
    lf = MWL.look_frames(dict(LOOK=L, LOOK_OVER=LO))
    tf = MWL.turn_frames()
    nk = int(round(MG.NEIGH_S * FPS))
    return dict(rest=[('A', 0.0, 0.0, None), ('C', PR, 0.0, None)],
                look=[('A' + tail, 0.0, v, None) for tail, v in lf] + [('C' + tail, PR, -v, None) for tail, v in lf],
                turnB=[('B' + tail, PR * e, L * (1 - e), None) for tail, e in tf],
                turnD=[('D' + tail, PR * (1 - e), -L * (1 - e), None) for tail, e in tf],
                neighL=[(f'NL{k:02d}', 0.0, 0.0, k / FPS) for k in range(1, nk)],
                neighR=[(f'NR{k:02d}', PR, 0.0, k / FPS) for k in range(1, nk)])


def render_frames(out):
    """まだ ない コマを 描いて <out>/cache/<形の 名前>.png に（窓 MG.WIN の 絵・すき通り・ロスなし）"""
    cache = os.path.join(out, 'cache')
    os.makedirs(cache, exist_ok=True)
    todo = []
    for fl in frame_list().values():
        for name, psi, look, tn in fl:
            fp = os.path.join(cache, MG.key(psi, look, tn) + '.png')
            if not os.path.exists(fp) and fp not in [t[0] for t in todo]:
                todo.append((fp, name, psi, look, tn))
    if not todo:
        return 0
    assert MG.available(), '3D（' + MG.GLB + '）が ない'
    st = MG.Stage(os.path.join(out, 'rig'))
    for i, (fp, name, psi, look, tn) in enumerate(todo):
        st.frame(psi, look, tn).save(fp)
        if i % 20 == 19 or i == len(todo) - 1:
            print(f'  コマ {i + 1}/{len(todo)}（{name}）', flush=True)
    json.dump(dict(fov=st.fov, tgt=st.tgt.tolist(), K=K, win=MG.WIN, foot=MG.FOOT), open(os.path.join(out, 'stage.json'), 'w'))
    return len(todo)


def load_frame(out, psi, look, tn):
    """コマ → (色 0〜1：まっすぐな α, α 0〜1)（窓の 絵の 大きさ）"""
    u8 = np.asarray(Image.open(os.path.join(out, 'cache', MG.key(psi, look, tn) + '.png')).convert('RGBA'))
    assert u8.shape == (MG.FH, MG.FW, 4), u8.shape
    return u8[..., :3].astype(np.float32) / 255, u8[..., 3].astype(np.float32) / 255


def plate_u8():
    """背景 だけの 絵（780×320）：あたたかい 白・うすい 大理石の すじ・金の 月桂樹（左右）。前の 絵（flat/marble_banner.py）と 同じ"""
    import marble_banner as MB
    p = MB.background()
    p = MB.laurel(p, 160, 170, 120, math.radians(110), math.radians(250), 1)
    p = MB.laurel(p, 620, 170, 120, math.radians(110), math.radians(250), -1)
    return (np.clip(p, 0, 1) * 255 + .5).astype(np.uint8)


def shadow(k):
    """台の 下の 影（こさ 0〜0.25）：壁紙の 絵の k倍の 大きさで（画素の まん中で はかる ＝ 1倍と 1.5倍で 同じ 場所）。台の 下の はしの 2画素 上が まん中（前の 絵と 同じ 形）"""
    yy, xx = np.mgrid[0:int(Hh * k), 0:int(W * k)].astype(np.float32)
    x, y = (xx + 0.5) / k - 0.5, (yy + 0.5) / k - 0.5
    return 0.25 * np.exp(-(((x - MG.FOOT[0]) / 140) ** 2 + ((y - (MG.FOOT[1] - 2)) / 8) ** 2))


def _resize(a, size):
    """1まいの 数の 絵（float）を なめらかに 大きさを かえる"""
    return np.asarray(Image.fromarray(a.astype(np.float32), 'F').resize(size, Image.LANCZOS), np.float32)


def _save_rgb(u8, path, q):
    Image.fromarray(u8, 'RGB').save(path, 'WEBP', quality=q, method=6)


def _save_rgba(u8, path, q):
    """すき通しつき（ロスあり・すき通しは 1点も かえない）"""
    Image.fromarray(u8, 'RGBA').save(path, 'WEBP', quality=q, method=6, alpha_quality=100, exact=False)
    back = np.asarray(Image.open(path).convert('RGBA'))
    assert back.shape == u8.shape and np.array_equal(back[..., 3], u8[..., 3]), path + '：すき通りが かわった'


def build(out):
    fls = frame_list()
    wx, wy = MG.WIN[0], MG.WIN[1]
    # 像が 動く はんい（窓の 絵の 画素）→ 切りぬく 四角（壁紙の 絵の 画素・偶数 ＝ pt の 境目）
    bb = [10 ** 9, 10 ** 9, -1, -1]
    for fl in fls.values():
        for _, psi, look, tn in fl:
            ys, xs = np.nonzero(load_frame(out, psi, look, tn)[1] > 0)
            bb = [min(bb[0], int(xs.min())), min(bb[1], int(ys.min())), max(bb[2], int(xs.max()) + 1), max(bb[3], int(ys.max()) + 1)]
    x0 = max(MG.WIN[0], wx + int(math.floor(bb[0] / K)) - MARGIN)
    y0 = max(MG.WIN[1], wy + int(math.floor(bb[1] / K)) - MARGIN)
    x1 = min(MG.WIN[2], wx + int(math.ceil(bb[2] / K)) + MARGIN)
    y1 = min(MG.WIN[3], wy + int(math.ceil(bb[3] / K)) + MARGIN)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2
    x1, y1 = x1 + x1 % 2, y1 + y1 % 2
    fw, fh = x1 - x0, y1 - y0
    cw, ch = int(fw * K), int(fh * K)                                   # シートの 中の 1コマ（画面の 3倍）
    cx0, cy0 = int((x0 - wx) * K), int((y0 - wy) * K)                   # 窓の 絵の 中の 切りぬく 所
    assert cw == fw * K and ch == fh * K and cx0 == (x0 - wx) * K and cy0 == (y0 - wy) * K
    assert bb[0] - cx0 >= 9 and bb[1] - cy0 >= 9 and cx0 + cw - bb[2] >= 9 and cy0 + ch - bb[3] >= 9, ('像が ふちの ぼかしに かかる', bb, (cx0, cy0, cw, ch))
    # 下じき：背景＋台の 影（1倍・1.5倍）
    plate = plate_u8()
    under2 = plate.astype(np.float32) / 255 * (1 - shadow(1)[..., None])
    bg3 = np.asarray(Image.fromarray(plate, 'RGB').resize((W3, H3), Image.LANCZOS), np.float32) / 255
    sh3 = shadow(K)
    under3 = bg3 * (1 - sh3[..., None])
    wx3, wy3 = int(wx * K), int(wy * K)
    cell_under = under3[wy3 + cy0:wy3 + cy0 + ch, wx3 + cx0:wx3 + cx0 + cw]
    sheets = {}
    for sname, fl in fls.items():
        k = SCALE.get(sname, K_MOVE)                                    # この シートの 細かさ
        kw, kh = int(fw * k), int(fh * k)
        assert kw == fw * k and kh == fh * k
        cols = min(COLS, len(fl))
        rows = (len(fl) + cols - 1) // cols
        sheet = np.zeros((rows * kh, cols * kw, 3), np.uint8)
        for i, (n, psi, look, tn) in enumerate(fl):
            rgb, a = load_frame(out, psi, look, tn)
            rgb, a = rgb[cy0:cy0 + ch, cx0:cx0 + cw], a[cy0:cy0 + ch, cx0:cx0 + cw, None]
            cell = (np.clip(cell_under * (1 - a) + rgb * a, 0, 1) * 255 + .5).astype(np.uint8)
            if k != K:                                                  # 3倍で 描いた コマを 小さく する
                cell = np.asarray(Image.fromarray(cell, 'RGB').resize((kw, kh), Image.LANCZOS))
            r, c = divmod(i, cols)
            sheet[r * kh:(r + 1) * kh, c * kw:(c + 1) * kw] = cell
        _save_rgb(sheet, os.path.join(out, f'marble_{sname}.webp'), Q)
        sheets[sname] = dict(cols=cols, rows=rows, frames=[n for n, _, _, _ in fl], k=k)
    # 止まった 絵（780×320）：背景＋影＋左向きの 像（A00 を 1.5 で わって 小さく：色は α を かけて から）
    rgb, a = load_frame(out, 0.0, 0.0, None)
    size2 = (MG.WIN[2] - MG.WIN[0], MG.WIN[3] - MG.WIN[1])
    a2 = np.clip(_resize(a, size2), 0, 1)
    pm2 = np.dstack([_resize(rgb[..., c] * a, size2) for c in range(3)])
    base = under2.copy()
    base[wy:wy + size2[1], wx:wx + size2[0]] = base[wy:wy + size2[1], wx:wx + size2[0]] * (1 - a2[..., None]) + pm2
    _save_rgb((np.clip(base, 0, 1) * 255 + .5).astype(np.uint8), os.path.join(out, 'marble_base.webp'), BASE_Q)
    # ずっ！ずっ！で 動く 絵（画面の 3倍・すき通しつき）：右向き spR（psi＝PSI_R）・左向き spL（psi＝0）。影は 黒（まっすぐな α）
    sprites = {}
    sx0, sx1 = int(round(MG.FOOT[0])) - SP_HALF, int(round(MG.FOOT[0])) + SP_HALF
    sx0, sx1 = sx0 - sx0 % 2, sx1 + sx1 % 2
    assert sx0 >= 0 and sx1 <= W and sx0 <= MG.WIN[0] and sx1 >= MG.WIN[2]
    for name, psi in (('spR', MG.PSI_R), ('spL', 0.0)):
        rgb, a = load_frame(out, psi, 0.0, None)
        A = np.zeros((H3, W3), np.float32)
        C = np.zeros((H3, W3, 3), np.float32)
        A[wy3:wy3 + MG.FH, wx3:wx3 + MG.FW] = a
        C[wy3:wy3 + MG.FH, wx3:wx3 + MG.FW] = rgb
        alpha = A + sh3 * (1 - A)
        col = C * (A / np.maximum(alpha, 1e-6))[..., None]
        u8 = (np.clip(np.dstack([col, alpha]), 0, 1) * 255 + .5).astype(np.uint8)[:, int(sx0 * K):int(sx1 * K)]
        u8[u8[..., 3] == 0] = 0
        _save_rgba(u8, os.path.join(out, f'marble_{name}.webp'), SP_Q)
        row = np.nonzero(a[int((MG.FOOT[1] - 3 - wy) * K)] > 0.5)[0]                    # 台の 下の はしの 左右（粉を 出す 所）
        sprites[name] = dict(box=[sx0, 0, sx1, Hh], foot=[MG.FOOT[0], MG.FOOT[1]],
                             base=[wx + int(math.floor(row.min() / K)), wx + int(math.ceil((row.max() + 1) / K))])
    # 背景 だけの 絵（plate）：コマの 四角と 台の 影の 所だけ（ほかは すき通し＝止まった 絵が そのまま 見える）・ロスなし
    mask = shadow(1) > 0.5 / 255
    mask[y0:y1, x0:x1] = True
    ys, xs = np.nonzero(mask)
    bx0, by0 = int(xs.min()) - int(xs.min()) % 2, int(ys.min()) - int(ys.min()) % 2
    bx1, by1 = int(xs.max()) + 1, int(ys.max()) + 1
    bx1, by1 = bx1 + bx1 % 2, by1 + by1 % 2
    rgba = np.dstack([plate, (mask * 255).astype(np.uint8)])[by0:by1, bx0:bx1]
    Image.fromarray(rgba, 'RGBA').save(os.path.join(out, 'marble_plate.webp'), 'WEBP', lossless=True, method=6)
    meta = dict(size=[W, Hh], crop=[x0, y0, x1, y1], frame=[fw, fh], sheets=sheets, sprites=sprites, plate=[bx0, by0, bx1, by1],
                LOOK=MG.LOOK, LOOK_OVER=MG.LOOK_OVER, PSI_R=MG.PSI_R, NEIGH_S=MG.NEIGH_S, FPS=FPS,
                scale=K, scale_move=K_MOVE, src='glb')                 # scale＝止まった 像と すべる 絵の 細かさ（壁紙の 絵の 何倍か）・scale_move＝動いて いる 間の コマ・src＝像は 3D
    json.dump(meta, open(os.path.join(out, 'marble_run.json'), 'w'), ensure_ascii=False, indent=1)
    return meta


KEYS = ('base', 'rest', 'look', 'turnB', 'turnD', 'neighL', 'neighR', 'spR', 'spL', 'plate')


def install(out):
    """できた 絵を 手元の 絵の フォルダ（ios/kisekae_blobs/<中身の md5>.webp）に 置いて、id を marble_blobs.json・blobs20.json（選ぶ 画面の 小さい 絵＝止まった 絵）に 書く。
       切りぬく 場所と コマの ならび（marble_run.json）も kisekae/ に。前の 絵（もと）は 消さない・上書きしない（同じ 名前＝同じ 中身）"""
    import hashlib
    Kd = os.path.dirname(HERE)
    blob_dir = os.environ.get('KISEKAE_ASSETS') or os.path.join(os.path.dirname(Kd), 'ios', 'kisekae_blobs')
    mb_path, b20_path = os.path.join(Kd, 'marble_blobs.json'), os.path.join(Kd, 'blobs20.json')
    b20 = json.load(open(b20_path))
    mb = {}
    for key in KEYS:
        data = open(os.path.join(out, f'marble_{key}.webp'), 'rb').read()
        bid = hashlib.md5(data).hexdigest()
        dst = os.path.join(blob_dir, bid + '.webp')
        if os.path.exists(dst):
            assert open(dst, 'rb').read() == data, dst
        else:
            open(dst, 'wb').write(data)
        mb[key] = bid
        print(key, bid, len(data))
    b20['marble'] = mb['base']
    open(mb_path, 'w').write(json.dumps(mb, ensure_ascii=False, indent=1))                # 今までと 同じ 書き方
    open(b20_path, 'w').write(json.dumps(b20, ensure_ascii=False, indent=1) + '\n')
    shutil.copy(os.path.join(out, 'marble_run.json'), os.path.join(Kd, 'marble_run.json'))


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    n = render_frames(out)
    m = build(out)
    print('描いた コマ', n, '・crop', m['crop'], '・frame', m['frame'], '・plate', m['plate'], '・台の 下', m['sprites']['spR']['base'],
          {k: (v['cols'], v['rows']) for k, v in m['sheets'].items()})
    tot = 0
    for key in KEYS:
        fp = os.path.join(out, f'marble_{key}.webp')
        tot += os.path.getsize(fp)
        print(f'  {key:7s} {Image.open(fp).size} {os.path.getsize(fp):,}')
    print('  あわせて', f'{tot:,}')
    if '--install' in sys.argv:
        install(out)
