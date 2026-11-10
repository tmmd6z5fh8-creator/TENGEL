"""帯の 壁紙（シルバー帯・ゴールド帯・マスター帯）の 像を まさちゃんの 3D（Meshy の GLB）で 描く（第4.149版）
   - まさちゃん 2026/11/11 00:39「これシルバー帯の馬の3D これゴールド帯にゴールドに変えて使える？」
     → シルバー帯・ゴールド帯：「Silver Thunder」（全力で 駆ける 銀の 馬の 像）。銀は そのまま・金は 同じ 形を 金色に
   - まさちゃん 2026/11/11 02:14「マスター帯の壁紙変える！シルバー帯、ゴールド帯のようにこのファイルの3Dモデルが中央に合って光っているようにして！」
     → マスター帯：「Tenger」（緑の 台の 上を 駆ける 金の 馬の 像・緑の たてがみと 鞍・台に TENGER／テンゲル の 金の 字）。色は 3D の まま
   - 3D は アプリに 入れない（1つ 約26〜33MB）。ここで 絵（780×320 の 像：すき通り a・色 srgb）に して、壁紙の 絵（flat/silver_banner.py の compose・
     flat/master_banner.py の compose：地・光の 輪・みがいた 床に うつる 像・きらめき）に のせる。壁紙の 動き（metal_wall.py）は 3つ とも 同じ 作り
   - 像は 6倍の 大きさ（4680×1920）で 描いて 色を つけて から 小さく する（ふちが なめらか）。光は カメラに 合わせて 置く：
     まわりの うつりこみ（上は 明るい 空・地平に 明るい 帯・下は 暗い 床）＋大きな 照明 4つ
       シルバー帯・ゴールド帯：形と テクスチャの 明るさ から「みがいた 金属の 明るさ」を 出して、銀の 色の 段／金の 色の 段に ぬりわける
       マスター帯：3D の 色（金＝金属・緑＝つやの ある ぬり）の まま、うつりこみと 光を つける
   - **馬（主役）だけ 高画質**（まさちゃん 2026/11/11 02:36「壁紙は、馬(主役)だけ画質良くなるようにして！」）：像 だけの すき通った 絵を 2倍（1560×640 ぶん：hi_a・hi_srgb）でも 返す。
     壁紙の 絵（背景：780×320）の 上に、この 絵を 同じ 場所に 重ねる（metal_run.py が 像の 所 だけ 切りぬいて <名前>_statue.webp に・metal_wall.py が 重ねる）
   - もとの 3D（METAL_HORSE_GLB・TENGEL_STATUE_GLB：リポジトリに 入れない）は 読む だけ
   python3 flat/metal_glb.py <出力フォルダ>   → 見る 用の silver_statue.png・gold_statue.png・tengel_statue.png（すき通り）"""
import sys, os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))

W, Hh = 780, 320
HI = 2                         # 馬（主役）だけの 高画質の 絵の 大きさ（壁紙の 絵 780×320 の 何倍か：iPhone の 画面は 1.5〜1.65倍 あれば 足りる）
SS = 3                         # その 絵を 作る ときの 細かさ（倍）
K = HI * SS                    # 描く 大きさ（倍：4680×1920）
# 像ごとの 置き方：3D の 場所・カメラ（左右の 向き yaw・上から pitch・画角 fov）・左はしと 右はし span・床の 線 floor（いちばん 下）・上の あき top
MODELS = dict(
    horse=dict(glb=os.environ.get('METAL_HORSE_GLB') or '/home/claude/work/band3d/orig/silver_thunder.glb',
               yaw=88.0, pitch=4.0, fov=17.0, span=(132, 648), floor=261, top=26),          # 左向きの ほぼ 真横（前の 像は 150〜631・床 261）
    # マスター帯：右向き・台を 正面から まっすぐ（まさちゃん 11/11 02:40「テンゲルの台が正面に真っ直ぐ見えるようにして！今は台が曲がってる！」）。
    #   第4.150版（まさちゃん 11/11 03:46「マスター帯が、シルバー帯、ゴールド帯より馬のサイズが小さいのが気になる！もっと大きくできる？」→ 見本 A・B・C を 見せて 04:03「Aにして！」）：
    #   馬を シルバー帯・ゴールド帯と 同じ 大きさに（像を 1.29倍：馬の 幅 390 → 500px。シルバー帯・ゴールド帯の 馬は 507px）。台の いちばん 下（floor 359）は 絵の 外＝
    #   台は「TENGER」の 字の すぐ 下で 切れる（カタカナの「テンゲル」の 札は 絵の 外）。前（第4.149版）は 台を ぜんぶ 入れて いた（floor 286・top 12）。
    #   pad＝形を 測る ときの 上下の よゆう（はみ出した 所も 測る）・foot＝絵の いちばん 下の 行を 暗く（どこから・どこまで・強さ：札の 上の ふちが 細い 金の 線に なって のぞくのを かげに しずめる）
    tengel=dict(glb=os.environ.get('TENGEL_STATUE_GLB') or '/home/claude/work/band3d/orig/tenger.glb',
                yaw=0.0, pitch=4.0, fov=17.0, span=(60, 720), floor=359, top=5, pad=(0, 80), foot=(313.0, 318.5, 0.92)))
OF = dict(silver='horse', gold='horse', tengel='tengel')

# 色の 段（金属の 明るさ 0〜1 → sRGB）：シルバー帯・ゴールド帯
RAMP = dict(
    silver=[(0, (18, 21, 30)), (.10, (72, 79, 96)), (.26, (150, 159, 177)), (.44, (208, 215, 227)), (.66, (241, 245, 251)), (1, (255, 255, 255))],
    gold=[(0, (30, 13, 2)), (.20, (112, 62, 9)), (.45, (200, 134, 24)), (.68, (244, 194, 66)), (.87, (255, 231, 148)), (1, (255, 252, 232))])
# 大きな 照明（カメラから 見た 向き：右・上・手前）・強さ・広さ
LAMPS = (((-0.30, 0.78, 0.55), 3.4, 0.050),      # 上・手前・少し 左の 大きな 光
         ((0.68, 0.20, 0.70), 1.25, 0.075),      # 右・手前の 光
         ((-0.55, 0.62, -0.55), 1.5, 0.06),      # 左・うしろの ふちの 光
         ((-0.85, -0.25, 0.45), 0.55, 0.09))     # 左・下の 弱い 光


def available(name='silver'):
    return os.path.isfile(MODELS[OF[name]]['glb'])


def _sm(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _env(R, basis, wide=1.0):
    """まわりの 光の うつりこみ（向き R ごとの 明るさ）。wide＝照明の 広さの 倍（つやが 少し にぶい 面は 広く）"""
    ry = R[:, 1]
    e = np.where(ry > 0, 0.16 + 0.62 * _sm(-0.05, 0.95, ry), 0.05 + 0.12 * _sm(-1, 0, ry))      # 空（上ほど 明るい）と 床（暗い）
    e = e + 1.25 * np.exp(-((ry - 0.05) / (0.075 * wide)) ** 2)                                # 地平線の 明るい 帯（みがいた 金属らしさ）
    right, up, back = basis
    for (lx, ly, lz), s, w in LAMPS:
        d = lx * right + ly * up + lz * back
        d = (d / np.linalg.norm(d)).astype(np.float32)
        e = e + (s / wide) * np.exp(-((1 - R @ d) / (w * wide)))
    return e.astype(np.float32)


_CACHE = {}


def _gbuf(model):
    """3D を 4倍の 大きさで 写して、色を つける もと（すき通り・法線・見る 向き・テクスチャの 色・すきまの 影・金属か・つや）を 返す。像ごとに 1回 だけ"""
    if model in _CACHE:
        return _CACHE[model]
    import glb
    from raster import Camera, render, normalize, linear_to_srgb
    M = MODELS[model]
    m = glb.load(M['glb'])
    prims = m.flatten()
    lo, hi = m.bbox()
    c = (np.array(lo) + np.array(hi)) / 2
    y, p = math.radians(M['yaw']), math.radians(M['pitch'])
    back = np.array([math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)])           # カメラの ほう（手前）
    right = np.cross(np.array([0, 1.0, 0]), back); right /= np.linalg.norm(right)
    up = np.cross(back, right)
    span, floor, top = M['span'], M['floor'], M['top']

    pad = tuple(M.get('pad') or (0, 0))                  # 形を 測る ときの よゆう（左右・上下 px）：像が 絵の 外に はみ出す 置き方（台の 下を 切る）の とき

    def shot(dist, target, k, want=('alpha', 'normal', 'albedo', 'pos', 'ao'), pad=(0, 0)):
        eye = target + dist * back
        if pad == (0, 0):
            cam = Camera.look_at(eye, target, fov_y=M['fov'], W=W * k, H=Hh * k)
        else:                                            # まわりに よゆうを つけた 大きな 絵（1px の 大きさと まん中は 同じ：はみ出した 所も 写る）
            hp = Hh + 2 * pad[1]
            fov = math.degrees(2 * math.atan(math.tan(math.radians(M['fov']) / 2) * hp / Hh))
            cam = Camera.look_at(eye, target, fov_y=fov, W=(W + 2 * pad[0]) * k, H=hp * k)
        return render(prims, cam, ss=1, want=want), eye

    dist, target = 6.0, c.copy()
    for _ in range(4):                                   # ためしに 写して 形の 箱を 測る → 幅・床の 線・左右の まん中を 合わせる
        fr, eye = shot(dist, target, 1, pad=pad)
        ys, xs = np.nonzero(fr['alpha'] > 0.5)
        x0, x1, y0, y1 = xs.min() - pad[0], xs.max() + 1 - pad[0], ys.min() - pad[1], ys.max() + 1 - pad[1]
        assert x0 > -pad[0] and x1 < W + pad[0] and y0 > -pad[1] and y1 < Hh + pad[1], ('像が 測る 絵から はみ出した（pad を 大きく）', model, x0, x1, y0, y1)
        k = min((span[1] - span[0]) / (x1 - x0), (floor - top) / (y1 - y0))
        dist = dist / k
        px = 2 * dist * math.tan(math.radians(M['fov']) / 2) / Hh          # 画面の 1px が 世界の どれだけか（ねらう 点の 奥行きで）
        cx = W / 2 + ((x0 + x1) / 2 - W / 2) * k
        by = Hh / 2 + (y1 - Hh / 2) * k
        target = target + right * ((cx - (span[0] + span[1]) / 2) * px) - up * ((by - (floor + 1)) * px)
    if pad != (0, 0):                                    # はみ出す 置き方：さいごの カメラで もう一度 測る（台の いちばん 下の ほんとうの 場所）
        fr, eye = shot(dist, target, 1, want=('alpha',), pad=pad)
        ys, xs = np.nonzero(fr['alpha'] > 0.5)
        x0, x1, y0, y1 = xs.min() - pad[0], xs.max() + 1 - pad[0], ys.min() - pad[1], ys.max() + 1 - pad[1]
    fr, eye = shot(dist, target, K)
    N = fr['normal'].reshape(-1, 3)
    V = normalize(eye[None, :].astype(np.float32) - fr['pos'].reshape(-1, 3))
    NdV = np.clip(np.sum(N * V, -1), 0, 1)
    G = dict(a=np.clip(fr['alpha'], 0, 1).astype(np.float32), N=N, NdV=NdV, R=normalize(2 * NdV[:, None] * N - V), alb=fr['albedo'].reshape(-1, 3), ao=fr['ao'].reshape(-1),
             basis=(right, up, back), fit=(int(x0), int(y0), int(x1), int(y1)))                    # fit＝さいごに 測った 形の 箱（絵の 外に はみ出した 所も 入る）
    # 金属か（metal）・つや（rough）：テクスチャ（金属と つやの 地図）を 色の 地図の かわりに 写して 読む（色の 地図は すぐ もどす）
    mats = {id(pr.mat): pr.mat for pr in prims}.values()
    if all(mt.mr_tex is not None for mt in mats):
        keep = [(mt, mt.base_tex) for mt in mats]
        try:
            for mt in mats:
                mt.base_tex = mt.mr_tex
            fr2, _e = shot(dist, target, K, want=('albedo',))
        finally:
            for mt, bt in keep:
                mt.base_tex = bt
        mr = linear_to_srgb(fr2['albedo'].reshape(-1, 3))
        G['metal'] = np.clip(mr[:, 2], 0, 1).astype(np.float32)
        G['rough'] = np.clip(mr[:, 1], 0.03, 1).astype(np.float32)
    _CACHE[model] = G
    return G


def _down(lin, a):
    """色（線形・すき通りを かけた もの）と すき通りを 小さく して sRGB に（ふちに 白い 点が 出ない）：780×320（a・srgb）と、馬 だけ 高画質の 1560×640（hi_a・hi_srgb）"""
    from raster import linear_to_srgb
    out = {}
    for pre, f in (('hi_', SS), ('', K)):
        l2 = lin.reshape(Hh * K // f, f, W * K // f, f, 3).mean((1, 3))
        a2 = a.reshape(Hh * K // f, f, W * K // f, f).mean((1, 3))
        out[pre + 'a'] = a2.astype(np.float32)
        out[pre + 'srgb'] = np.clip(linear_to_srgb(l2 / np.maximum(a2, 1e-4)[..., None]), 0, 1).astype(np.float32)
    return out


def ramp(t, stops):
    xs = [s[0] for s in stops]
    out = np.zeros(t.shape + (3,), np.float32)
    for k in range(3):
        out[..., k] = np.interp(t, xs, [s[1][k] / 255 for s in stops])
    return out


def _horse(name):
    """シルバー帯・ゴールド帯：みがいた 金属の 明るさ → 銀／金の 色の 段"""
    from raster import srgb_to_linear
    G = _gbuf('horse')
    L = G['alb'] @ np.array([0.2126, 0.7152, 0.0722], np.float32)                               # テクスチャの 明るさ（すじ・くぼみ）
    F = L + (1 - L) * (1 - G['NdV']) ** 5 * 0.6                                                 # ふちの 白い 光は ひかえめに
    lum = F * _env(G['R'], G['basis']) * (0.35 + 0.65 * G['ao'])
    t = np.clip(1 - np.exp(-lum * 1.15), 0, 1).reshape(Hh * K, W * K)                          # 明るい 所を なだらかに つぶす
    return _down(srgb_to_linear(ramp(t, RAMP[name])) * G['a'][..., None], G['a'])


def _tengel():
    """マスター帯：3D の 色の まま（金＝金属：色の ついた うつりこみ・緑＝つやの ある ぬり：色＋うすい うつりこみ）"""
    G = _gbuf('tengel')
    alb, m, r = G['alb'], G['metal'][:, None], G['rough']
    F0 = 0.022 * (1 - m) + alb * m                                                              # ぬりの うつりこみは うすく（緑が 灰色に ならない）
    F = F0 + (1 - F0) * ((1 - G['NdV']) ** 5 * 0.5)[:, None]
    spec = F * _env(G['R'], G['basis'], wide=1.18)[:, None]                                      # みがいた 金（照明は 少し だけ 広く）
    N = G['N']
    right, up, back = G['basis']
    key = (-0.30 * right + 0.78 * up + 0.55 * back); key = (key / np.linalg.norm(key)).astype(np.float32)
    irr = 0.70 + 0.40 * np.clip(N[:, 1], -1, 1) + 1.3 * np.clip(N @ key, 0, 1)                    # ぬりの 面に 当たる 光（空・床・大きな 光）
    diff = alb * (1 - m) * irr[:, None]
    col = (spec * 1.55 + diff) * (0.35 + 0.65 * G['ao'])[:, None]
    lin = np.clip(1 - np.exp(-col * 1.3), 0, 1)                                                 # 明るい 所を なだらかに つぶす（金の 光は 白っぽく）
    a = G['a']
    out = _down(lin.reshape(Hh * K, W * K, 3) * a[..., None], a)
    out['fit'] = G['fit']                                                                       # 形の 箱（台の いちばん 下が 絵の 外に ある ときも ほんとうの 場所）
    foot = MODELS['tengel'].get('foot')
    if foot:                                                                                    # 絵の いちばん 下の 行を かげに しずめる（台が 絵の 下で 切れる 所）
        for key, k in (('srgb', 1), ('hi_srgb', HI)):
            y = (np.arange(out[key].shape[0], dtype=np.float32) + 0.5) / k
            out[key] = out[key] * (1 - foot[2] * _sm(foot[0], foot[1], y))[:, None, None]
    return out


def render(name):
    """name：'silver'・'gold'・'tengel' → 壁紙の 絵の compose に 渡す 形（a＝すき通り・srgb＝像の 色：780×320）＋馬 だけ 高画質の 絵（hi_a・hi_srgb：1560×640）"""
    if name not in _CACHE:
        _CACHE[name] = _tengel() if name == 'tengel' else _horse(name)
    return _CACHE[name]


if __name__ == '__main__':
    from PIL import Image
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for nm in sys.argv[2:] or ('silver', 'gold', 'tengel'):
        R = render(nm)
        Image.fromarray((np.dstack([R['srgb'], R['a']]) * 255 + .5).astype(np.uint8), 'RGBA').save(os.path.join(out, f'{nm}_statue.png'))
        ys, xs = np.nonzero(R['a'] > 0.5)
        print(nm, '箱', int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1))
