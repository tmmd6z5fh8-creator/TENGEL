# ナイターの 馬 3頭（走る コマ・止まる／立つ／走りだす コマ・表彰の 絵）：いまと 同じ 絵を 1.5倍の 細かさ（iPhone の 3倍の 画面に ぴったり）で
#   第4.157版（まさちゃん 2026/11/12 04:20「Aにして！あと、課金の壁紙は全部馬の画質が悪いから同じように画質を上げてほしい！」＝馬の 絵を 画面の 3倍に。
#   競馬新聞・勝負服・夕焼け〈第4.156版〉の つづき）
#   ・馬と 騎手：3倍で 描いて ぬった 絵（anime_rider.paint_anime の debug の col3・A3）を 1倍へ 小さく する 所を 1.5倍に（同じ カメラ・同じ 形・同じ 乱数）
#   ・影：4倍で 描いた 同じ だ円を 1.5倍へ（night_run.shadow_mask の k）／砂けむり：3倍で 描いた 同じ 絵を 1.5倍へ（night_run.dust_flow の k）
#   ・上下の ずれ・もや・重ねる 順・切りぬく 場所は いまと 同じ（night_run.horse_frames・trans_frames と 同じ 式を 1.5倍の 画素で）。台帳（night_run.json）は かえない
#   ・表彰の 絵：うしろ（暗い コース・スポットライト）は いまの 絵（1倍）を なめらかに 広げた もの。馬・騎手・レイ・足もとの 影・まわりの 光・ふちの 光は 1.5倍で
#   ・コースの 絵（far・track・rail）は かえない
#   python3 flat/hq_night.py <出す フォルダ> [h5 h3 h7 t5 t3 t7 a5 a3 a7]   （なにも 書かなければ ぜんぶ）
#   いくつか 同時に 走らせる とき：先に「python3 flat/hq_night.py <出す フォルダ> base」（3頭の カメラを 決めて のこす）。表彰（a…）は 同時に 2つ 走らせない
#   （カメラを さがす 下絵の 名前が 1つ なので、同時だと ちがう 馬の 下絵を 読む）
#     → night_h<番号>_hq.webp・night_t<番号>_hq.webp（すき通しつき・ロスなし）・night_award<番号>_hq.webp、
#        night_h<番号>_1x.webp・night_t<番号>_1x.webp・night_award<番号>_1x.webp（いまと 同じ 作り方：入って いる 絵と 見くらべる 用）
#     描いた コマは <出す フォルダ>/cache15 に のこして 2回目は 描かない
#   第4.167版（まさちゃん 2026/11/13「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）：コマを 1/30秒に
#   ・走る コマ：10 → 15コマ（night_h<番号>_hq.webp・1.5倍・ロスなし：いままでどおり）。上下の ずれは 第4.166版までの 動きの まま（night_run.gallop_dy）
#   ・止まる／走りだす コマ：時刻で 決める（night_run.trans_list：動きが 大きい 間は 1/30秒ごと）＝1頭 18 → 72コマ。コマが 4倍に なる ので、
#     この シート（night_t<番号>_m.webp）は 1倍・ロスあり（Q_TRANS）に する（動いて いる 間 だけ 見える 絵）。止まって 立つ 絵 だけ 1.5倍・ロスなしで
#     べつの 1まい（night_s<番号>_hq.webp）＝止まって いる 間は いままでどおり くっきり
#   ・台帳（night_run.json の horses・trans）は ここで 書く（<出す フォルダ>/night_run.json）。切りぬく 場所は 新しい コマの 絵から 決め直す
#   ・馬の いる 所 だけ 描く（anime_rider.render_anime の rect：中の 絵は ぜんぶ 描いた ときと 同じ。四角の ふちに 絵が かかったら 止まる）
import os, sys, json, math
import numpy as np, cv2
from PIL import Image
K = os.environ.get('HQ_K') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K + '/flat'); sys.path.insert(0, K)      # HQ_K＝kisekae を まるごと 写した 作業用の フォルダ（3D の 下絵を r3d/tmp に たくさん 書く ので、写しで 走らせると リポジトリが よごれない）
import night_run as NR
OUT = 1.5; W, Hh = NR.W, NR.Hh; H = NR.H
kx = lambda v: int(round(v * OUT))
out = sys.argv[1]; os.makedirs(out, exist_ok=True); cache = os.path.join(out, 'cache15'); os.makedirs(cache, exist_ok=True)
what = set(sys.argv[2:]) or {f'{c}{h["num"]}' for c in 'hta' for h in NR.HORSES}
info = json.load(open(K + '/night_run.json'))
Q_TRANS = int(os.environ.get('Q_TRANS', '90'))                # 止まる／走りだす コマの シートの 画質（ロスあり）
PAD = 14                                                      # 描く 四角：前の 版の 切りぬく 場所（走る コマ・止まる コマ）より この 画素（1倍）だけ 広く
NEW = {}                                                      # 新しい 台帳（horses・trans）


def paint2(R, look, dbg=None):
    """ぬった 絵：1倍（いまと 同じ）と 1.5倍（小さく する 前の 3倍の 絵から）"""
    d = {} if dbg is None else dbg
    rgb1, a1 = NR.paint_anime(R, look, debug=d)
    col3, A3 = d['col3'], d['A3']; h3, w3 = A3.shape
    assert R['s'] == 3 and h3 % 2 == 0 and w3 % 2 == 0
    a2 = cv2.resize(A3, (w3 // 2, h3 // 2), interpolation=cv2.INTER_AREA)
    pre = cv2.resize(col3 * A3[..., None], (w3 // 2, h3 // 2), interpolation=cv2.INTER_AREA)
    rgb2 = pre / np.maximum(a2[..., None], 1e-4)
    return rgb1.astype(np.float32), a1.astype(np.float32), np.clip(rgb2, 0, 1).astype(np.float32), np.clip(a2, 0, 1).astype(np.float32)


def moved(rgb, a, dy, w, h):
    """上下に ずらす（色×不透明度で：night_run と 同じ）"""
    M = np.float32([[1, 0, 0], [0, 1, float(dy)]])
    aw = cv2.warpAffine(a, M, (w, h), flags=cv2.INTER_LINEAR)
    rp = cv2.warpAffine(rgb * a[..., None], M, (w, h), flags=cv2.INTER_LINEAR)
    return np.where(aw[..., None] > 1e-4, rp / np.maximum(aw, 1e-4)[..., None], 0), aw


def stack(sh, dust, rgb, a, haze):
    """影 → 砂けむり → 馬（night_run と 同じ 順）→ premultiplied RGBA"""
    rgb = rgb * (1 - haze) + NR.HAZE * haze
    pre = np.zeros(rgb.shape, np.float32); A = np.zeros(a.shape, np.float32)
    al = sh * 0.38
    pre, A = pre * (1 - al[..., None]), A + al * (1 - A)
    if dust is not None:
        dr, da = dust
        pre, A = pre * (1 - da[..., None]) + dr * da[..., None], A + da * (1 - A)
    pre, A = pre * (1 - a[..., None]) + rgb * a[..., None], A + a * (1 - A)
    return pre, A


def base(h):
    """いまの 絵の 馬（カメラ・地面・影を 決める）。カメラを さがす 所（style2d.frame_horse）は 下絵の 名前が 1つ（frame）なので、
       いくつか 同時に 走らせる ときは 先に「base」だけ 1回 走らせて のこして おく（のこした 数を 読めば 同じ 結果）"""
    num = h['num']; px = h.get('padx', 0); wc = W + 2 * px
    cf = os.path.join(cache, f'base{num}.npz')
    if not os.path.exists(cf):
        R0 = NR.render_anime(h['pose'], h['box'], W, Hh, name=f'nrun{num}'); NR.drop_tmp(f'nrun{num}')
        np.savez(cf + '.tmp.npz', eye=np.asarray(R0['cam'][0], float), tgt=np.asarray(R0['cam'][1], float), hooves=np.asarray(R0['hooves'], float), s=R0['s'])
        os.replace(cf + '.tmp.npz', cf)
    z = np.load(cf)
    cam, s = (z['eye'], z['tgt']), int(z['s'])
    hv0 = z['hooves'] / s + np.array([px, 0.0])
    gy = hv0[:, 1].max() + 1.5; scl = (gy - NR.Y0) / (Hh - NR.Y0)
    e, t = info['horses'][str(num)], info['trans'][str(num)]
    bx = (min(e['at'][0], t['at'][0]) + px - PAD, min(e['at'][1], t['at'][1]) - PAD,
          max(e['at'][0] + e['cell'][0], t['at'][0] + t['cell'][0]) + px + PAD, max(e['at'][1] + e['cell'][1], t['at'][1] + t['cell'][1]) + PAD)
    rect = (max(0, bx[0] * s), max(0, bx[1] * s), min(wc * s, bx[2] * s), min(Hh * s, bx[3] * s))
    return dict(num=num, px=px, wc=wc, cam=cam, s=s, hv0=hv0, gy=gy, scl=scl, hx_d=hv0[2:, 0].min(), g0=hv0[:, 1].max(), rect=rect,
                sh1=NR.shadow_mask(hv0, gy, scl, wc), sh2=NR.shadow_mask(hv0, gy, scl, wc, k=OUT), dim=1.0 - h['haze'] * 0.8, seed=200 + NR.HORSES.index(h))


def inside(a1, b):
    """描いた 絵が 四角（rect）の ふちに かかって いない（かかって いたら 馬の 一部が 切れて いる）"""
    x0, y0, x1, y1 = (v // b['s'] for v in b['rect'])
    m = 2
    edge = max(float(a1[y0:y0 + m, x0:x1].max()) if y0 > 0 else 0.0, float(a1[y1 - m:y1, x0:x1].max()) if y1 < a1.shape[0] else 0.0,
               float(a1[y0:y1, x0:x0 + m].max()) if x0 > 0 else 0.0, float(a1[y0:y1, x1 - m:x1].max()) if x1 < a1.shape[1] else 0.0)
    assert edge < 0.01, ('描く 四角の ふちに 絵が かかった', b['num'], b['rect'], edge)


def painted(cf, make):
    """描いた コマ（1倍・1.5倍・ひづめ）を フォルダに のこす"""
    if os.path.exists(cf):
        z = np.load(cf)
        return z['rgb1'].astype(np.float32), z['a1'].astype(np.float32), z['rgb2'].astype(np.float32), z['a2'].astype(np.float32), z['hv']
    rgb1, a1, rgb2, a2, hv = make()
    np.savez_compressed(cf + '.tmp.npz', rgb1=rgb1.astype(np.float16), a1=a1.astype(np.float16), rgb2=rgb2.astype(np.float16), a2=a2.astype(np.float16), hv=hv)
    os.replace(cf + '.tmp.npz', cf)
    return painted(cf, make)                                                # のこした 数（16bit）で 作る：2回目と 同じ 結果に する


def sheet(frames, x0, y0, cw, ch, cols, k, path):
    """切りぬいて ならべた 1まい（すき通しつき・ロスなし：night_run.save_rgba と 同じ）。frames：premultiplied (pre, A)"""
    X0, Y0, CW, CH = (int(round(v * k)) for v in (x0, y0, cw, ch))
    rows = -(-len(frames) // cols)
    S = np.zeros((CH * rows, CW * cols, 4), np.float32); spill = 0.0
    for i, (pre, A) in enumerate(frames):
        r, c = divmod(i, cols)
        rgb = np.where(A[..., None] > 1e-4, pre / np.maximum(A, 1e-4)[..., None], 0)
        S[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW, :3] = rgb[Y0:Y0 + CH, X0:X0 + CW]; S[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW, 3] = A[Y0:Y0 + CH, X0:X0 + CW]
        o = A.copy(); o[Y0:Y0 + CH, X0:X0 + CW] = 0; spill = max(spill, float(o.max()))
    NR.save_rgba(path, S[..., :3], S[..., 3])
    return os.path.getsize(path), round(spill, 4)


def run_frames(h, b):
    """走る コマ（night_run.horse_frames と 同じ）：15コマ。上下は 第4.166版までの 動きの まま（NR.gallop_dy）"""
    num, wc, n = b['num'], b['wc'], NR.N_FRAMES
    P = []
    for f in range(n):
        g = (f / n + NR.PHASE[num]) % 1.0

        def make(f=f, g=g):
            R = NR.render_anime(NR.horse_pose(g, h['pose']), h['box'], wc, Hh, name=f'nrun{num}_{f}', cam=b['cam'], rect=b['rect'])
            r = paint2(R, dict(h, hair_phase=2 * math.pi * f / n)); NR.drop_tmp(f'nrun{num}_{f}')
            inside(r[1], b)
            return r + (np.asarray(R['hooves'], float) / b['s'],)
        rgb1, a1, rgb2, a2, hv = painted(os.path.join(cache, f'h{num}_g{f:02d}.npz'), make)
        P.append(dict(rgb1=rgb1, a1=a1, rgb2=rgb2, a2=a2))
        print('horse', num, 'frame', f, flush=True)
    dys = [NR.gallop_dy(num, f / n) for f in range(n)]
    F1, F2 = [], []
    for f, (fr, dy) in enumerate(zip(P, dys)):
        F1.append(stack(b['sh1'], NR.dust_flow(b['hx_d'], b['gy'], b['scl'], b['dim'], b['seed'], f / n, wc), *moved(fr['rgb1'], fr['a1'], dy, wc, Hh), h['haze']))
        F2.append(stack(b['sh2'], NR.dust_flow(b['hx_d'], b['gy'], b['scl'], b['dim'], b['seed'], f / n, wc, k=OUT), *moved(fr['rgb2'], fr['a2'], dy * OUT, kx(wc), kx(Hh)), h['haze']))
    return F1, F2, [round(float(v), 2) for v in dys]


def trans_frames(h, b):
    """止まる・立つ・走りだす コマ（night_run.trans_frames と 同じ）：1倍の コマ ぜんぶ と、立つ コマの 1.5倍"""
    num, wc, ph = b['num'], b['wc'], NR.PHASE[b['num']]
    F1, meta, stand2 = [], [], None
    for i, (kind, k, phi, g, a) in enumerate(NR.trans_list(num)):
        def make(i=i, g=g, a=a, kind=kind, k=k):
            look = dict(h, hair_phase=2 * math.pi * (g - ph), hair_wind=0.4 + 0.6 * a, hair_drop=0.85 * (1 - a))
            if 'tail_ang' in h:
                look['tail_ang'] = NR.STAND_TAIL + (h['tail_ang'] - NR.STAND_TAIL) * a
            R = NR.render_anime(NR.blend_pose(g, a, h['pose']), h['box'], wc, Hh, name=f'ntr{num}_{kind}{k}', cam=b['cam'], rect=b['rect'])
            r = paint2(R, look); NR.drop_tmp(f'ntr{num}_{kind}{k}')
            inside(r[1], b)
            return r + (np.asarray(R['hooves'], float) / b['s'],)
        rgb1, a1, rgb2, a2, hv = painted(os.path.join(cache, f'h{num}_{kind}{k:02d}.npz'), make)
        raw = b['g0'] - hv[:, 1].max()
        if not NR.stance_legs(g % 1.0):
            u = ((g % 1.0) - 0.67) / 0.33
            raw -= NR.LIFT * a * 4 * u * (1 - u)
        dy = NR.trans_dy(num, g, a, raw)
        d1 = d2 = None
        if a > 0.02:
            dr, da = NR.dust_flow(b['hx_d'], b['gy'], b['scl'], b['dim'], b['seed'], (g - ph) % 1.0, wc); d1 = (dr, da * a * a)
        F1.append(stack(b['sh1'], d1, *moved(rgb1, a1, dy, wc, Hh), h['haze']))
        if kind == 'stand':
            stand2 = stack(b['sh2'], None, *moved(rgb2, a2, dy * OUT, kx(wc), kx(Hh)), h['haze'])
        meta.append(dict(kind=kind, k=k, phi=round(phi, 4), amp=round(a, 4), dy=round(float(dy), 2)))
        print('horse', num, 'trans', i, kind, k, round(phi, 2), round(a, 3), flush=True)
    return F1, meta, stand2


def box_of(frames, px, keep=None):
    """切りぬく 場所（night_run.horse_sheet と 同じ 決め方：見える 所 ぜんぶ ＋ 4画素・偶数に そろえる）。keep：これも 入る ように（前の 版の 場所）"""
    A_all = np.max(np.stack([A for _, A in frames]), 0)
    wc = A_all.shape[1]
    ys, xs = np.nonzero(A_all > 0.002)
    x0, y0 = max(0, int(xs.min()) - 4), max(0, int(ys.min()) - 4)
    x1, y1 = min(wc, int(xs.max()) + 5), min(Hh, int(ys.max()) + 5)
    if keep:
        x0, y0, x1, y1 = min(x0, keep[0] + px), min(y0, keep[1]), max(x1, keep[0] + px + keep[2]), max(y1, keep[1] + keep[3])
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2
    x1, y1 = x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2
    return x0, y0, x1 - x0, y1 - y0


def sheet_q(frames, x0, y0, cw, ch, cols, path, q):
    """1倍の コマを 切りぬいて ならべた 1まい（すき通しつき・ロスあり：動いて いる 間 だけ 見える コマ）"""
    rows = -(-len(frames) // cols)
    S = np.zeros((ch * rows, cw * cols, 4), np.float32)
    for i, (pre, A) in enumerate(frames):
        r, c = divmod(i, cols)
        rgb = np.where(A[..., None] > 1e-4, pre / np.maximum(A, 1e-4)[..., None], 0)
        S[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw, :3] = rgb[y0:y0 + ch, x0:x0 + cw]; S[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw, 3] = A[y0:y0 + ch, x0:x0 + cw]
    u8 = (np.clip(S, 0, 1) * 255 + .5).astype(np.uint8)
    Image.fromarray(u8, 'RGBA').save(path, 'WEBP', quality=q, method=6, alpha_quality=100)
    Image.fromarray(u8, 'RGBA').save(path[:-5] + '_lossless.webp', 'WEBP', lossless=True, quality=100, method=6)      # 見くらべる 用（アプリには 入れない）
    return os.path.getsize(path), rows


_back = []


def award(h):
    """表彰の 絵（night_run.award_picture と 同じ）：1倍（いまと 同じ）と 1.5倍"""
    num = h['num']
    if not _back:
        _back.append(NR.award_back())
    back = _back[0]
    look = dict(h, hair_wind=0.4, hair_drop=0.85, hair_phase=0.6)
    if 'tail_ang' in h:
        look['tail_ang'] = NR.STAND_TAIL
    R = NR.render_anime(NR.AWARD_POSE, NR.AWARD_BOX, W, Hh, name=f'naw{num}', jockey='win')
    dbg = {}
    rgb1, a1, rgb2, a2 = paint2(R, look, dbg); NR.drop_tmp(f'naw{num}')
    s = R['s']
    jock = ((dbg['part'] >= 10) & (dbg['part'] <= 17)).astype(np.float32)
    hv = np.asarray(R['hooves'], float) / s
    gy = hv[:, 1].max() + 1.0
    x0, x1 = hv[:, 0].min() - 26, hv[:, 0].max() + 30
    ld = {}
    lr1, la1 = NR.lei_layer(R, s, (Hh, W), debug=ld)
    res = {}
    for k, rgb, a, bk in ((1, rgb1, a1, back), (OUT, rgb2, a2, cv2.resize(back, (kx(W), kx(Hh)), interpolation=cv2.INTER_LINEAR))):
        w, hh = int(round(W * k)), int(round(Hh * k))
        yy, xx = np.mgrid[0:hh, 0:w].astype(np.float32)
        yy, xx = (yy + 0.5) / k - 0.5, (xx + 0.5) / k - 0.5                    # 画素の まん中の 場所（1倍の 場所で）
        jm = cv2.resize(jock, (w, hh), interpolation=cv2.INTER_AREA)
        shd = np.exp(-((xx - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 4 - ((yy - gy) / 7.0) ** 2)
        img = bk * (1 - 0.62 * shd)[..., None]
        glow = np.clip(NR.blur(a, 7 * k) - a, 0, 1) * NR.ss_(0.0, 1.0, (NR.GROUND_Y - yy) / 120.0)
        img = img + glow[..., None] * H('#FFD9A0') * 0.40
        img = img * (1 - a[..., None]) + rgb * a[..., None]
        if k == 1:
            lr, la = lr1, la1
        else:
            pre = cv2.resize(ld['col'] * ld['al'][..., None], (w, hh), interpolation=cv2.INTER_AREA); la = cv2.resize(ld['al'], (w, hh), interpolation=cv2.INTER_AREA)
            lr = np.where(la[..., None] > 1e-4, pre / np.maximum(la, 1e-4)[..., None], 0)
        la = la * (1 - np.clip(jm * 1.4, 0, 1))
        img = img * (1 - la[..., None]) + lr * la[..., None]
        rim = np.clip(a - cv2.warpAffine(a, np.float32([[1, 0, 0], [0, 1, 2.2 * k]]), (w, hh)), 0, 1)
        img = img + rim[..., None] * H('#FFE8C0') * 0.35
        res[k] = np.clip(img, 0, 1)
    led = info['award'][str(num)]; fist = np.asarray(R.get('fist', R['hand_near']), float) / s
    assert abs(led['ground'] - gy) < 0.06 and abs(led['fist'][0] - fist[0]) < 0.06 and abs(led['fist'][1] - fist[1]) < 0.06, ('differs from night_run.json', led, gy, fist)
    NR.save_rgb(f'{out}/night_award{num}_1x.webp', res[1], q=92); NR.save_rgb(f'{out}/night_award{num}_hq.webp', res[OUT], q=92)
    Image.fromarray((res[OUT] * 255 + .5).astype(np.uint8)).save(f'{out}/night_award{num}_hq.png')      # 圧縮の 強さを 決める 用（ロスなし）
    print('award', num, {n_: os.path.getsize(f'{out}/night_award{num}_{n_}.webp') for n_ in ('1x', 'hq')}, flush=True)


for h in NR.HORSES:
    num = h['num']; b = None
    if 'base' in what:
        base(h); print('base', num, flush=True)
    if f'h{num}' in what:
        b = b or base(h); F1, F2, dys = run_frames(h, b)
        e = info['horses'][str(num)]
        x0, y0, cw, ch = box_of(F1, b['px'], keep=(e['at'][0], e['at'][1], e['cell'][0], e['cell'][1]))
        print('run', num, 'cell', (x0 - b['px'], y0, cw, ch), '前', e['at'], e['cell'], 'sizes (bytes, light outside the cell)',
              sheet(F1, x0, y0, cw, ch, len(F1), 1, f'{out}/night_h{num}_1x.webp'), sheet(F2, x0, y0, cw, ch, len(F2), OUT, f'{out}/night_h{num}_hq.webp'), flush=True)
        NEW.setdefault('horses', {})[str(num)] = dict(frames=len(F1), cell=[cw, ch], at=[x0 - b['px'], y0], phase=NR.PHASE[num], nose=e['nose'], ground=e['ground'], dy=dys)
    if f't{num}' in what:
        b = b or base(h); F1, meta, stand2 = trans_frames(h, b)
        x0, y0, cw, ch = box_of(F1, b['px'])
        mv = [(fr, m) for fr, m in zip(F1, meta) if m['kind'] != 'stand']                  # シートは 動く コマ だけ（立つ コマは 1.5倍の 1まい）
        cols = NR.TRANS_COLS
        size, rows = sheet_q([fr for fr, _ in mv], x0, y0, cw, ch, cols, f'{out}/night_t{num}_m.webp', Q_TRANS)
        st = [m for m in meta if m['kind'] == 'stand'][0]
        print('trans', num, 'cell', (x0 - b['px'], y0, cw, ch), len(mv), 'コマ', size, 'bytes（ロスなしなら', os.path.getsize(f'{out}/night_t{num}_m_lossless.webp'), '）・立つ 絵',
              sheet([stand2], x0, y0, cw, ch, 1, OUT, f'{out}/night_s{num}_hq.webp'), flush=True)
        NEW.setdefault('trans', {})[str(num)] = dict(cell=[cw, ch], at=[x0 - b['px'], y0], cols=cols, rows=rows, frames=[m for _, m in mv], stand=st)
    if f'a{num}' in what:
        award(h)
    if NEW:                                                                                # 台帳：できた 分を 書く（馬ごとに べつの ファイル：同時に 走らせても ぶつからない）
        json.dump({k: {str(num): v[str(num)]} for k, v in NEW.items() if str(num) in v}, open(f'{out}/night_new{num}.json', 'w'), ensure_ascii=False)
print('done', sorted(what), flush=True)
# 入れ方：python3 flat/hq_install.py night <出す フォルダ>（手元の 絵の フォルダ ios/kisekae_blobs と 台帳へ。前の 絵は 消さない）
