# 結果ボードカスタム「出世馬」（7段）の 絵を 3D の 絵に 入れかえる（第4.153版・まさちゃん 2026/11/11 13:59「出世馬の結果ボードカスタム3Dに絵を入れ替えて！」・14:23「ボードは何も書いていないように編集して！」
#   ・15:29「立体感はすごいいい！あとは、色合いを自然に合わせて欲しい！・出世馬スタート・何連続的中 みたいなやつだけ全部消せる？」）
#   まさちゃんの 3D（Meshy の GLB 7つ：花＝1連勝・メダル＝2・トロフィー＝3・王冠＝4・紫の 馬＝8・金の 馬＝16・2頭＝24）は ボードに 見本の 字が 入って いる。
#   3D は 1つ 18〜100MB なので アプリには 入れない → 正面から 写した 絵に して、前の 絵（bcp_shusseN.webp）の 上に のせる。
#   **GLB・写した 絵・できた 絵は リポジトリに 入れない**（この スクリプト だけ）。前の 絵（bcp_shusseN.webp）は 消さない・上書きしない（新しい 名前 bcp_shusseN_3d.webp で 足す）
#
#   python3 kisekae/bcp/shusse3d.py render  <作業フォルダ>                         … <作業フォルダ>/src/shusseN.glb（N＝1・2・3・4・8・16・24）を 正面から 写す → hi/shusseN.png・hi/shusseN_buf.npz（場所・もとの 色・面の 向き）
#   python3 kisekae/bcp/shusse3d.py compose <作業フォルダ> <前の 絵の フォルダ> <出す フォルダ> [名前…]   … bcp_shusseN_3d.webp（1170×2532・WebP quality 90）
#
#   作り方：
#     ・色：3D の「もとの 色」（albedo：前の 絵から 作った 3D なので 前の 絵と 同じ 色あい＝黒い 馬に 紫の たてがみ・こい 金）に 光を 当て直す（relight）。
#       白い 光で 写した 絵（hi/shusseN.png）は 白っぽく なる（黒い 馬が 灰色・金が レモン色）ので、板の 中を 見つける ため だけに 使う。
#       金（オレンジ〜黄色の 所）は 明るさで 色が かわる 金属の 色（こげ茶 → オレンジ → 黄色 → 白）。ふちには 場面の 光（紫・金）と、うしろの 背景の 光を 少し のせる
#     ・ボード：3D の ボードの 中（暗い 板の いちばん 大きな かたまり → 穴を うめる）を **何も 書いて いない 板**に（板の 色を なめらかに のばす・ふちの 内がわを 少し 暗く）。
#       板に かぶさる 飾り（メダル・花・わくの 宝石と 蹄鉄）は 残す。板の 中の 月桂樹・ハンコ・しおり は 消す。板の 色は 前の 絵の 板の 色に 合わせる
#     ・札（「出世馬 スタート！」「2連続的中！」「3連続的中！」）は 消す：1連勝＝札の 所に 花を うめて、リボンの たれを 上に つなぐ／2連勝＝ボードの 下の 札を とる／3連勝＝台の 色と 形で うめる
#     ・板の 四すみは **前の 絵と 同じ 場所**（designs/shusseN.json の quad）：横は 大きさを 合わせ、たては 何も ない 帯（band）を のばして 合わせる → アプリの 字の 置き方は そのまま
#     ・キャラ（馬・トロフィー）は ボードと 分けて（馬＝板の 面より 奥・トロフィー＝ボードより 下）、**前の 絵の キャラと 同じ 場所・同じ くらいの 大きさ**に 置く（馬は 口の 場所：光線が 口から 出る）
#       ボードに かくれて 切れた 馬の 首は 少し のばす（切れ目が 新しい ボードの うしろに 入る）
#     ・背景：前の 絵の まま。新しい 部品の 下と まわり（ring）と、前の 絵の 札（erase）だけ、外がわの 背景から うめる（前の 絵の キャラ・わくの ふち・札が のこらない）
import numpy as np, sys, os, math, cv2
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import bcp_app as B
cv2.setNumThreads(1)                                # いつも 同じ 絵が 出る ように（うめる 道具の 順番を そろえる）
STAGES = ('shusse1', 'shusse2', 'shusse3', 'shusse4', 'shusse8', 'shusse16', 'shusse24')
CW, CH = 1170, 2532; W3 = None; A = None          # 作業フォルダ・前の 絵の フォルダ（main で 入れる）
LW = np.array([0.2126, 0.7152, 0.0722], np.float32)


def render(work, R=2600):
    """GLB を 正面から 写す（kisekae/r3d/glb の 描く 道具）。白い 光の 絵（板の 中を 見つける 用）と、場所・もとの 色・面の 向き（光を 当て直す 用）"""
    sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
    import glb
    from raster import Camera, render as rnd, tonemap
    os.makedirs(os.path.join(work, 'hi'), exist_ok=True)
    for name in STAGES:
        m = glb.load(os.path.join(work, 'src', name + '.glb')); prims = m.flatten()
        lo, hi = m.bbox(); lo = np.array(lo); hi = np.array(hi); c = (lo + hi) / 2; ext = hi - lo
        fov = 12.0; dist = max(ext[0], ext[1]) * 1.22 / 2 / math.tan(math.radians(fov) / 2)          # まわりに 2割の あき（CFG の 点の 場所は この 大きさ 2600² の 絵の 上）
        cam = Camera.look_at(c + np.array([0, 0, dist]), c, fov_y=fov, W=R, H=R)
        fr = rnd(prims, cam, ss=1, want=('rgb', 'alpha', 'depth', 'pos', 'albedo', 'normal', 'ao'), ambient=((0.80, 0.80, 0.82), (0.30, 0.29, 0.28)), env_spec=(0.95, 0.95, 0.95), rim=((1.0, 0.97, 0.92), 0.35, 2.5))
        rgb = np.clip(tonemap(fr['rgb'], 1.0), 0, 1); a = np.clip(fr['alpha'], 0, 1)
        Image.fromarray((np.dstack([rgb, a]) * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(work, 'hi', name + '.png'))
        np.savez_compressed(os.path.join(work, 'hi', name + '_buf.npz'), pos=fr['pos'].astype(np.float16), albedo=(np.clip(fr['albedo'], 0, 1) * 255 + 0.5).astype(np.uint8),
                            normal=(fr['normal'] * 127).astype(np.int8), alpha=(a * 255 + 0.5).astype(np.uint8), ext=ext)
        print(name, '写した', rgb.shape[:2], flush=True)


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return x * x + y * y <= r * r


def lin(x):
    x = np.asarray(x, np.float32); return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4).astype(np.float32)


def srgb(x):
    x = np.clip(x, 0, None); return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055).astype(np.float32)


def unit(v):
    v = np.array(v, np.float32); return v / np.linalg.norm(v)


# band：ボードを たてに のばす 帯（写した 絵の 行）／rect＋keep：金の わくの ボード（中は 角の まるい 四角・わくの 飾り だけ 残す）
# split：部品の 分け方（'z'＝深さで 馬と ボード・('y', 行)＝その 行から 下が キャラ）
# chars：[{ pick：部品の えらび方, s：大きさ, at：(写した 絵の 点, 前の 絵の 点), neck：(帯, 足す 行), front：ボードの 前か, look：光, mouth：(口の 場所, 光の 色, 強さ) }]
# gold：金属の 金に する 強さ（0＝しない：花の 黄色は 金属に しない）・gold_t：金の 明るさの ずらし
# look（ボードは CFG の look・キャラは chars の look）：
#   exp：明るさ／neutral：白い 光で 写した 絵を まぜる 割合（0〜1：白い 馬・花・お札は 白い 光の 絵の ほうが 前の 絵に 近い）・tint：その 絵に 掛ける 光の 色／
#   emis：あざやかな 所（ネオン・たてがみ）を 光らせる 強さ／fill：(色, 強さ)＝かげに のせる 場面の 光／rim：(ふちの 光の 色, 強さ, 細さ)／sat：あざやかさ
# halo：(左の 色, 右の 色, 強さ, にじみの 大きさ)＝わくの まわりの 光／side：(左, 右)＝わくに 掛ける 光の 色
# unlabel：札を 消す（kind：'bow'＝1連勝・'hang'＝2連勝・'fill'＝3連勝）／erase：前の 絵の 札の 四角（今の 絵の 点。5つ目が 'h' なら 横に つなぐ：台の 光の 帯）
PURPLE = dict(exp=1.15, emis=0.9, fill=((120, 40, 220), 0.035), rim=((200, 120, 255), 0.75, 2.0))        # 紫の 馬（黒い 体に 紫の 光）
WHITE = dict(exp=1.0, neutral=1.0, tint=(1.0, 0.95, 0.85), rim=((255, 205, 120), 0.28, 2.4))               # 白い 馬（金の 光）
CFG = {
    'shusse1': dict(band=(1150, 1500), gold=0, look=dict(exp=1.15, neutral=0.5), unlabel=dict(kind='bow', z=0.052, ytop=1885, seed=(1300, 1990)), erase=[(360, 1250, 800, 1525)]),
    'shusse2': dict(band=(1300, 1750), halo=((255, 200, 90), (255, 200, 90), 0.45, (10, 28)), look=dict(exp=1.1), unlabel=dict(kind='hang', box=(650, 1890, 1950, 2260), z=0.004), erase=[(318, 1335, 890, 1495, 'h')]),
    'shusse3': dict(band=(520, 1050), ring=85, split=('y', 1256), halo=((255, 200, 90), (255, 200, 90), 0.4, (10, 28)), look=dict(exp=1.1), unlabel=dict(kind='fill', box=(930, 2190, 1640, 2410)),
                    chars=[dict(pick='all', s=0.75, at=((1300, 1282), (585, 1166)), front=True, look=dict(exp=1.15))]),
    'shusse4': dict(band=(1380, 1760), gold_t=-0.06, look=dict(exp=1.3, neutral=0.4, tint=(1.0, 0.95, 0.86))),
    'shusse8': dict(band=(1820, 2100), split='z', margin=(45, 45, 45), gold=0, bloom=0.7, halo=((190, 90, 255), (190, 90, 255), 0.85, (8, 24)), look=dict(exp=1.25, emis=0.9),
                    chars=[dict(pick='all', s=0.86, at=((1154, 915), (411, 934)), neck=((1085, 1160), 40), mouth=((1150, 915), (255, 120, 255), 0.85), look=PURPLE)]),
    'shusse16': dict(band=(1760, 2040), rect=True, keep=[(0.40, -0.1, 0.60, 0.07), (0.36, 0.92, 0.64, 1.1)], split='z', gold_t=-0.08, halo=((255, 200, 90), (255, 200, 90), 0.35, (10, 28)), look=dict(exp=1.0),
                     chars=[dict(pick='all', s=0.85, at=((1475, 725), (700, 895)), neck=((985, 1055), 30), mouth=((1470, 720), (255, 225, 140), 0.6), look=WHITE)]),
    'shusse24': dict(band=(1560, 1800), rect=True, keep=[(0.40, -0.1, 0.60, 0.07), (0.36, 0.92, 0.64, 1.1)], split='z', gold_t=-0.08, halo=((200, 100, 255), (255, 190, 80), 0.5, (10, 28)), side=((0.84, 0.66, 1.1), (1.0, 1.0, 1.0)), look=dict(exp=1.0),
                     chars=[dict(pick='left', s=0.86, at=((871, 801), (271, 962)), neck=((975, 1045), 30), mouth=((875, 800), (255, 120, 255), 0.85), look=PURPLE),
                            dict(pick='right', s=0.86, at=((1713, 801), (931, 966)), neck=((975, 1045), 30), mouth=((1710, 800), (255, 225, 140), 0.6), look=WHITE)]),
}


def load(name):
    d = np.load(f'{W3}/hi/{name}_buf.npz')
    buf = dict(z=d['pos'][..., 2].astype(np.float32), al8=d['alpha'].copy(), alb=d['albedo'].copy(), nrm=d['normal'].copy(), ext=float(np.max(d['ext'])))
    im = np.asarray(Image.open(f'{W3}/hi/{name}.png').convert('RGB'), np.float32)
    zc = buf['z'][buf['al8'] > 128]; hist, edges = np.histogram(zc, bins=400); k = np.argmax(hist); z0 = (edges[k] + edges[k + 1]) / 2
    return im, buf, float(z0)


# ── 光を 当て直す：もとの 色（albedo）× 光。金は 明るさで 色が かわる（前の 絵の 金：こげ茶 → オレンジ → 黄色 → 白）
RAMP_T = np.array([0.00, 0.25, 0.50, 0.70, 0.85, 1.00, 1.25], np.float32)
RAMP_C = lin(np.array([(62, 32, 6), (146, 84, 18), (224, 148, 38), (250, 196, 70), (255, 226, 120), (255, 246, 196), (255, 254, 240)], np.float32) / 255)


def relight(buf, gold=1.0, gold_t=0.0, spec=0.5, amb=0.50, key=0.80, ao_k=0.7):
    """→ ng（もとの 色 × 光・リニア）・gc／gm（金の 色と 金の 所）・fres（ふちの 強さ：面が 横を 向く ほど 1）・viv（あざやかな 所）"""
    al = buf['al8'] > 128; A = lin(buf['alb'].astype(np.float32) / 255); N = buf['nrm'].astype(np.float32) / 127; N /= np.maximum(np.linalg.norm(N, axis=2, keepdims=True), 1e-4)
    z = buf['z']; w = al.astype(np.float32); ao = np.ones_like(z)
    for sg, k in ((8, 0.45), (30, 0.55)):                          # くぼみの かげ（まわりを ぼかした 深さより 奥に ある 所を 暗く）
        zb = cv2.GaussianBlur(np.where(al, z, 0), (0, 0), sg) / np.maximum(cv2.GaussianBlur(w, (0, 0), sg), 1e-3)
        ao *= 1 - ao_k * k * np.clip((zb - z) / (0.010 * buf['ext']), 0, 1)
    L1 = unit((-0.42, 0.60, 0.68)); L2 = unit((0.70, 0.10, 0.50)); V = np.array([0, 0, 1], np.float32)
    ndl1 = np.clip(N @ L1, 0, 1); ndl2 = np.clip(N @ L2, 0, 1); hemi = 0.5 + 0.5 * N[..., 1]
    dif = (amb * (0.62 + 0.38 * hemi) + key * ndl1 + 0.18 * ndl2) * ao
    nh1 = np.clip(N @ unit(L1 + V), 0, 1); nh2 = np.clip(N @ unit(L2 + V), 0, 1); sp = nh1 ** 60 + 0.4 * nh2 ** 30; sheen = nh1 ** 5
    fres = np.clip(1 - np.abs(N[..., 2]), 0, 1)
    mx = A.max(2); mn = A.min(2); sat = (mx - mn) / np.maximum(mx, 1e-4); lumA = A @ LW
    R = dict(ng=(A * dif[..., None]).astype(np.float32), sp=(sp * spec * 0.5 * ao).astype(np.float32), fres=fres.astype(np.float32), gm=None, gc=None,
             viv=(np.clip((sat - 0.55) / 0.3, 0, 1) * np.clip((mx - 0.08) / 0.2, 0, 1)).astype(np.float32))
    if gold > 0:
        g = al & (A[..., 0] > A[..., 1]) & (A[..., 1] > A[..., 2] * 2.2) & (sat > 0.72) & (mx > 0.10)       # 金・オレンジ（クリーム色の たてがみは 入れない）
        if g.any():
            R['gm'] = cv2.GaussianBlur(g.astype(np.float32), (0, 0), 1.5) * gold
            ref = float(np.median(lumA[g])); tA = np.clip(lumA / max(ref, 1e-4), 0.25, 1.5)                  # 絵に 描いて ある こさ（馬の 形・ふち取り）は そのまま
            t = np.clip((0.20 + 0.36 * dif) * tA ** 0.8 + 0.26 * sheen + 0.70 * sp + 0.16 * fres ** 3 * (0.4 + 0.6 * hemi) + gold_t, 0, 1.25) * ao ** 0.5
            R['gc'] = np.stack([np.interp(t, RAMP_T, RAMP_C[:, i]) for i in range(3)], 2).astype(np.float32)
    return R


def finish(R, im, m, look):
    """部品（m）の 色を 仕上げる → sRGB 0〜255。im＝白い 光で 写した 絵（0〜255）"""
    col = R['ng'][m] * look.get('exp', 1.0)
    if look.get('emis'): col = col * (1 + look['emis'] * R['viv'][m])[:, None]                              # ネオン・たてがみ
    col = col + R['sp'][m][:, None]                                                                         # 白い 小さな てかり
    if look.get('fill'):
        fc, fk = look['fill']; col = col + lin(np.array(fc, np.float32) / 255) * fk
    if look.get('neutral'):
        col = col * (1 - look['neutral']) + lin(im[m] / 255) * np.array(look.get('tint', (1, 1, 1)), np.float32) * look['neutral']
    if R['gm'] is not None:
        gm = R['gm'][m][:, None]; col = col * (1 - gm) + R['gc'][m] * gm
    if look.get('rim'):
        rc, rk, rp = look['rim']; col = col + (R['fres'][m] ** rp)[:, None] * lin(np.array(rc, np.float32) / 255) * rk
    if look.get('sat', 1.0) != 1.0:
        l = (col @ LW)[:, None]; col = l + (col - l) * look['sat']
    mxv = col.max(1, keepdims=True); col = col * np.where(mxv > 0.85, (0.85 + (1 - np.exp(-(mxv - 0.85) / 0.35)) * 0.35) / np.maximum(mxv, 1e-4), 1.0)   # 明るすぎる 所を ゆるく おさえる（色は そのまま）
    return np.clip(srgb(col), 0, 1) * 255


# ── 札を 消す
def unlabel_hang(buf, box, zthr):
    """ボードの 下に さがる 札（2連勝）：札を とって、札が かかって いた わくの 下の ふちを となりの 列の 形で もどす"""
    x0, y0, x1, y1 = box; al = buf['al8'] > 128; m = np.zeros_like(al); m[y0:y1, x0:x1] = al[y0:y1, x0:x1] & (buf['z'][y0:y1, x0:x1] > zthr)
    lab, n = ndimage.label(m); sz = ndimage.sum(m, lab, range(1, n + 1)); pm = ndimage.binary_dilation(lab == (int(np.argmax(sz)) + 1), disk(6))
    ys, xs = np.nonzero(pm); cx0, cx1, ty = int(xs.min()), int(xs.max()), int(ys.min()); xc = cx0 - 30                      # xc：札の すぐ 左の きれいな 列（わくの 下の ふちは 横に 同じ 形）
    assert not pm[:, xc].any() and (buf['al8'][ty - 4:y1, xc] > 128).any(), '札の となりの 列が きれいで ない'
    for k in ('alb', 'nrm', 'z', 'al8'):
        src = buf[k][ty - 4:y1, xc]; buf[k][ty - 4:y1, cx0 - 8:cx1 + 9] = src[:, None] if src.ndim == 1 else src[:, None, :]
    return (cx0, ty, cx1, int(ys.max()))


def unlabel_fill(buf, box, sag_k=1.1):
    """台の 前に はって ある 札（3連勝）：札の 左右の 台の 色・面の 向き・深さを、台の まるみ（下の ふちの 弓なり）に そって つなぐ"""
    x0, y0, x1, y1 = box; al = buf['al8'] > 128; sub = buf['alb'][y0:y1, x0:x1].astype(np.int32)
    pm = ndimage.binary_fill_holes(ndimage.binary_closing(sub[..., 1] > 105, disk(5))); lab, n = ndimage.label(pm); sz = ndimage.sum(pm, lab, range(1, n + 1))
    pm = ndimage.binary_dilation(lab == (int(np.argmax(sz)) + 1), disk(9)); M = np.zeros_like(al); M[y0:y1, x0:x1] = pm
    ys, xs = np.nonzero(M); xa, xb, ya, yb = int(xs.min()) - 4, int(xs.max()) + 4, int(ys.min()), int(ys.max())
    # 台の 下の ふち（同じ 高さの 線）の 弓なり：列ごとの いちばん 下の 行を 2次式で ならす
    cols = np.arange(xa - 150, xb + 151); bot = np.array([np.nonzero(al[:, x])[0].max() for x in cols], np.float64); pf = np.polyfit(cols, bot, 2); yo = lambda x: np.polyval(pf, x)
    yref = min(yb + 14, int(bot.min()) - 6); zrow = buf['z'][yref].astype(np.float64)                                       # 札の すぐ 下の 行の 深さ（台の まるみ）
    xsr = np.arange(xa, xb + 1); u = (xsr - xa) / float(xb - xa)
    bulge = zrow[xsr] - ((1 - u) * zrow[xa] + u * zrow[xb])
    dl = (yo(xsr) - yo(xa)) * sag_k; dr = (yo(xsr) - yo(xb)) * sag_k
    new = {k: buf[k].astype(np.float32).copy() for k in ('alb', 'nrm', 'z')}
    for y in range(ya, yb + 1):
        row = M[y, xa:xb + 1]
        if not row.any(): continue
        yl = np.clip(np.round(y - dl).astype(int), 0, al.shape[0] - 1); yr = np.clip(np.round(y - dr).astype(int), 0, al.shape[0] - 1)
        for k in ('alb', 'nrm', 'z'):
            a = buf[k][yl, xa].astype(np.float32); b = buf[k][yr, xb].astype(np.float32)
            v = (a * (1 - u) + b * u) if a.ndim == 1 else (a * (1 - u)[:, None] + b * u[:, None])
            if k == 'z': v = v + bulge
            new[k][y, xa:xb + 1][row] = v[row]
    buf['alb'] = np.clip(new['alb'] + 0.5, 0, 255).astype(np.uint8); buf['nrm'] = np.clip(np.round(new['nrm']), -127, 127).astype(np.int8); buf['z'] = new['z']
    return (xa, ya, xb, yb)


def _seam(E):
    """E（行 × 列）の 上から 下へ、ちがいが いちばん 小さい 道（列の 番号）"""
    h, w = E.shape; cum = E.astype(np.float64).copy(); back = np.zeros((h, w), np.int8)
    for y in range(1, h):
        prev = cum[y - 1]; c = np.stack([np.r_[np.inf, prev[:-1]], prev, np.r_[prev[1:], np.inf]]); k = np.argmin(c, 0); back[y] = k - 1; cum[y] += c[k, np.arange(w)]
    path = np.zeros(h, np.int32); path[-1] = int(np.argmin(cum[-1]))
    for y in range(h - 1, 0, -1): path[y - 1] = np.clip(path[y] + back[y, path[y]], 0, w - 1)
    return path


def unlabel_bow(buf, im, u):
    """花の わくの 下の 札（1連勝）：札の ある はんいの 花の 帯を、左右の 花の 帯の かけらを ならべ直して 作り直す（上から 下まで まるごと＝花は 切れずに 丸ごと 入る）。
       左右の つなぎ目は、もとの 絵と いちばん 合う 道で つなぐ。リボンの 輪と 結び目は そのまま 上に のこし、札の 下に 出て いた たれは 結び目から ハの字に 出る 形に する。
       もとの 色・面の 向き・深さ・白い 光の 絵を ぜんぶ 同じ ずらしで うめる（あとで 光を 当て直す）"""
    al8 = buf['al8']; al = al8 > 128; z = buf['z']; alb = buf['alb'].astype(np.int32); H, W = al.shape
    m = al & (z > u['z']); m[:u['ytop']] = False; lab, n = ndimage.label(m); pm = ndimage.binary_dilation(lab == lab[u['seed'][1], u['seed'][0]], disk(7))
    ys, xs = np.nonzero(pm); px0, px1, py0, py1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()); cxk = (px0 + px1) / 2.0
    isred = lambda a: (a[..., 0] > 170) & (a[..., 1] < 80) & (a[..., 2] < 110)
    red = al & ~pm & isred(alb); red[:py1 - 14] = False; red[:, :px0] = False; red[:, px1:] = False
    lab, n = ndimage.label(red); sz = ndimage.sum(red, lab, range(1, n + 1)); tails = ndimage.binary_dilation(np.isin(lab, [i + 1 for i in range(n) if sz[i] > 3000]), disk(2)) & al & ~pm
    tl, tn = ndimage.label(tails); tbuf = {k: buf[k].copy() for k in ('alb', 'nrm', 'z', 'al8')}; tim = im.copy()                      # たれ（あとで 形を かえて のせる）
    gone = ndimage.binary_dilation(red, disk(6)); gone[:py1 - 14] = False
    # 花の 帯（板の 面より 前）の 上の はし・リボンの 輪と 結び目（札より 上・まん中）
    zb = float(np.median(z[py0 - 400:py0 - 250, px0:px1][al[py0 - 400:py0 - 250, px0:px1]])); gar = al & (z > zb + 0.012); rows = np.nonzero(gar[py0 - 330:py0, px0:px1].any(1))[0]; ytop = py0 - 330 + int(rows.min()) - 12
    bow = al & (z > 0.022); bow[:ytop] = False; bow[py0:] = False; bow[:, :px0 + 150] = False; bow[:, px1 - 150:] = False
    by, bx = np.nonzero(bow); hull = cv2.convexHull(np.stack([bx, by], 1).astype(np.int32)); hm = np.zeros((H, W), np.uint8); cv2.fillConvexPoly(hm, hull, 1)
    bow = ndimage.binary_dilation(hm > 0, disk(2)); bow[py0:] = False                                      # 輪の 中と 輪の あいだ（結び目の 上）も もとの まま（輪を つつむ 形）
    edge = al[py0 - 2] & (z[py0 - 2] > 0.022); el, en = ndimage.label(edge)                                  # 札で まっすぐ 切れて いた 輪の 下の ふち：はしを まるく（結び目の 所は あとで のばす）
    for o in ndimage.find_objects(el):
        a_, b_ = o[0].start, o[0].stop
        if b_ - a_ < 20 or (a_ < cxk + 48 and b_ > cxk - 48): continue
        xs_ = np.arange(a_ - 4, b_ + 4); hh = np.round(18 * (2 * np.abs(xs_ - (a_ + b_) / 2.0) / (b_ - a_ + 8)) ** 2.2).astype(int)
        for x_, h_ in zip(xs_, hh): bow[py0 - h_:py0, x_] = False
    ov = u.get('overlap', 130); hx0, hx1 = px0 - ov, px1 + ov; cx0, cy0, cx1, cy1 = max(0, hx0 - 420), max(0, ytop - 60), min(W, hx1 + 420), min(H, py1 + 230); keyc = np.array([0, 255, 0], np.float32)
    alc = al & ~gone; comp = np.clip(np.where(alc[cy0:cy1, cx0:cx1, None], im[cy0:cy1, cx0:cx1], keyc), 0, 255).astype(np.uint8); src = cv2.cvtColor(comp, cv2.COLOR_RGB2Lab)
    hole = np.zeros((H, W), bool); hole[ytop:cy1, hx0:hx1 + 1] = True; hc = hole[cy0:cy1, cx0:cx1]; dst = np.zeros_like(src)
    import hashlib; ck = os.path.join(W3, 'cache', 'bow_' + hashlib.md5(src.tobytes() + hc.tobytes()).hexdigest() + '.npy')
    if os.path.exists(ck): dst = np.load(ck)
    else:
        cv2.xphoto.inpaint(src, (~hc).astype(np.uint8) * 255, dst, cv2.xphoto.INPAINT_SHIFTMAP)               # まわりの 絵の かけらを ずらして はる（色を まぜない ので 花の 形が そのまま）。2分 くらい
        os.makedirs(os.path.dirname(ck), exist_ok=True); np.save(ck, dst)
    # どこから 持って きたか（ずらし）を さがす：うめた 点と 同じ 値の 点
    h, w = hc.shape; key = (src[..., 0].astype(np.uint32) << 16) | (src[..., 1].astype(np.uint32) << 8) | src[..., 2]; dk = (dst[..., 0].astype(np.uint32) << 16) | (dst[..., 1].astype(np.uint32) << 8) | dst[..., 2]
    valid = ~hc; vals, idx, cnt = np.unique(key[valid], return_index=True, return_counts=True); vy, vx = np.nonzero(valid); uq = cnt == 1; uv = vals[uq]; uy = vy[idx[uq]]; ux = vx[idx[uq]]
    hy, hx = np.nonzero(hc); hv = dk[hy, hx]; pos = np.minimum(np.searchsorted(uv, hv), len(uv) - 1); hit = uv[pos] == hv
    sh, c = np.unique(np.stack([uy[pos[hit]] - hy[hit], ux[pos[hit]] - hx[hit]], 1), axis=0, return_counts=True); o = np.argsort(-c, kind='stable'); sh = sh[o]; c = c[o]
    shift = np.zeros((h, w, 2), np.int32); done = np.zeros((h, w), bool)
    for strict in (True, False):
        for (dy, dx), nvote in zip(sh, c):
            if nvote < 8: break
            ry, rx = np.nonzero(hc & ~done); yy = ry + dy; xx = rx + dx; ok = (yy >= 0) & (yy < h) & (xx >= 0) & (xx < w); ok[ok] &= valid[yy[ok], xx[ok]]
            eq = np.zeros(len(ry), bool); eq[ok] = dk[ry[ok], rx[ok]] == key[yy[ok], xx[ok]]
            if strict:
                em = np.zeros((h, w), np.uint8); em[ry[eq], rx[eq]] = 1; em = cv2.erode(em, np.ones((3, 3), np.uint8)) > 0; shift[em] = (dy, dx); done |= em
            else: shift[ry[eq], rx[eq]] = (dy, dx); done[ry[eq], rx[eq]] = True
    rest = hc & ~done
    if rest.any():                                                # のこり（ごく 少し）：いちばん 近い 点の ずらし
        _, (iy, ix) = ndimage.distance_transform_edt(~done, return_indices=True); shift[rest] = shift[iy[rest], ix[rest]]
    sy = np.clip(np.arange(h)[:, None] + shift[..., 0], 0, h - 1) + cy0; sx = np.clip(np.arange(w)[None, :] + shift[..., 1], 0, w - 1) + cx0
    F = {k: buf[k][sy, sx] for k in ('alb', 'nrm', 'z')}; F['al8'] = np.where(alc[sy, sx], 255, 0).astype(np.uint8); Fim = im[sy, sx]
    # つなぎ目：左右の 重なり（もとの 絵が ある 所）で、もとの 絵と うめた 絵の ちがいが いちばん 小さい 道
    use = hc.copy(); O3 = comp.astype(np.float32); F3 = np.where(F['al8'][..., None] > 0, Fim, keyc)
    for side in (0, 1):
        a0, a1 = (hx0 - cx0, px0 - 12 - cx0) if side == 0 else (px1 + 12 - cx0, hx1 + 1 - cx0); r0, r1 = ytop - cy0, h
        path = _seam(np.abs(O3[r0:r1, a0:a1] - F3[r0:r1, a0:a1]).sum(2) + 1.0); xx = np.arange(a1 - a0)[None, :]
        use[r0:r1, a0:a1] = (xx >= path[:, None]) if side == 0 else (xx <= path[:, None])
    use &= ~bow[cy0:cy1, cx0:cx1]                                 # 輪と 結び目は もとの まま（花の 前）
    for k in ('alb', 'nrm', 'z', 'al8'): buf[k][cy0:cy1, cx0:cx1][use] = F[k][use]
    im[cy0:cy1, cx0:cx1][use] = Fim[use]
    out = ~use & ~bow[cy0:cy1, cx0:cx1] & gone[cy0:cy1, cx0:cx1]; buf['al8'][cy0:cy1, cx0:cx1][out] = 0      # うめない 所に のこった たれ
    # リボンの たれ：結び目から ハの字に 出る 形に（上を 結び目の 所へ 細く しぼる・下は 少し 上へ）。札より 上では 輪と 結び目の うしろ
    yk = py0 - 18; wsum = np.zeros((H, W), np.float32); acc = {k: np.zeros(buf[k].shape, np.float32) for k in ('alb', 'nrm', 'z')}; accim = np.zeros(im.shape, np.float32)
    for i, o in enumerate(ndimage.find_objects(tl)):
        one = (tl == i + 1)
        if one.sum() < 3000: continue
        x0, x1, y0, y1 = o[1].start, o[1].stop, o[0].start, o[0].stop; left = (x0 + x1) / 2 < cxk; yb = y1 - u.get('tail_up', 60)
        srcq = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
        dstq = np.float32([[cxk - 60, yk], [cxk - 3, yk], [x1, yb], [x0, yb]]) if left else np.float32([[cxk + 3, yk], [cxk + 60, yk], [x1, yb], [x0, yb]])
        M = cv2.getPerspectiveTransform(srcq, dstq); wa = (one * (tbuf['al8'] / 255.0)).astype(np.float32); wsum += cv2.warpPerspective(wa, M, (W, H), flags=cv2.INTER_LINEAR)
        for k in ('alb', 'nrm', 'z'): acc[k] += cv2.warpPerspective(tbuf[k].astype(np.float32) * (wa if tbuf[k].ndim == 2 else wa[..., None]), M, (W, H), flags=cv2.INTER_LINEAR)
        accim += cv2.warpPerspective(tim * wa[..., None], M, (W, H), flags=cv2.INTER_LINEAR)
    put = (wsum > 0.5) & ~bow
    for k in ('alb', 'nrm', 'z'):
        v = acc[k] / np.maximum(wsum if acc[k].ndim == 2 else wsum[..., None], 1e-4); buf[k][put] = (np.clip(np.round(v), -127 if k == 'nrm' else 0, 127 if k == 'nrm' else 255).astype(buf[k].dtype) if k != 'z' else v)[put]
    im[put] = (accim / np.maximum(wsum[..., None], 1e-4))[put]; buf['al8'][put] = 255
    # 結び目を 下へ のばす（札で 切れて いた 下の ふちと、たれの つけ根を かくす）
    kb = al & isred(alb); kb[:py0 - 70] = False; kb[py0:] = False; kb[:, :int(cxk) - 48] = False; kb[:, int(cxk) + 48:] = False; ky, kx = np.nonzero(kb)
    if len(ky):
        kx0, kx1, ky1 = int(kx.min()), int(kx.max()) + 1, int(ky.max()) + 1; hs, hd = 16, 44; yy2, xx2 = np.mgrid[0:hd, 0:kx1 - kx0]; r = 12
        dx = np.maximum(np.maximum(r - xx2, xx2 - (kx1 - kx0 - 1 - r)), 0); dyc = np.maximum(yy2 - (hd - 1 - r), 0); ka = (dx * dx + dyc * dyc <= r * r) | (dyc == 0)
        for k in ('alb', 'nrm', 'z'):
            st = cv2.resize(buf[k][ky1 - hs:ky1, kx0:kx1].astype(np.float32), (kx1 - kx0, hd), interpolation=cv2.INTER_LINEAR); tg = buf[k][ky1 - hs:ky1 - hs + hd, kx0:kx1]
            tg[ka] = (np.round(st) if k != 'z' else st).astype(buf[k].dtype)[ka]
        st = cv2.resize(im[ky1 - hs:ky1, kx0:kx1], (kx1 - kx0, hd), interpolation=cv2.INTER_LINEAR); im[ky1 - hs:ky1 - hs + hd, kx0:kx1][ka] = st[ka]; buf['al8'][ky1 - hs:ky1 - hs + hd, kx0:kx1][ka] = 255
    return (px0, py0, px1, py1)


def interior(name, im, al, z, z0):
    c = CFG[name]; lum = im.mean(2); r, g, b = im[..., 0], im[..., 1], im[..., 2]
    D = al & ((lum < 70) | ((b > r + 10) & (b >= g - 2) & (lum < 135))) & (np.abs(z - z0) < 0.08)
    D = ndimage.binary_opening(D, disk(3)); lab, n = ndimage.label(D); sz = ndimage.sum(D, lab, range(1, n + 1))
    if c.get('rect'):
        keepc = [i + 1 for i in range(n) if sz[i] > 0.12 * sz.max()]; U = np.isin(lab, keepc); U = ndimage.binary_fill_holes(ndimage.binary_closing(U, disk(28)))
        ys, xs = np.nonzero(U); x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
        q = U[y0:y0 + 200, x0:x0 + 200]; rr = int(np.sqrt((~q).sum() / (1 - np.pi / 4))); rr = max(20, min(rr, 160))
        I = np.zeros_like(U); yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]; dx = np.maximum(np.maximum(x0 + rr - xx, xx - (x1 - rr)), 0); dy = np.maximum(np.maximum(y0 + rr - yy, yy - (y1 - rr)), 0)
        I[y0:y1 + 1, x0:x1 + 1] = dx * dx + dy * dy <= rr * rr
        gold = al & ~D
        for kx0, ky0, kx1, ky1 in c.get('keep', []):
            bx0, by0, bx1, by1 = int(x0 + kx0 * (x1 - x0)), int(y0 + ky0 * (y1 - y0)), int(x0 + kx1 * (x1 - x0)), int(y0 + ky1 * (y1 - y0))
            sub = np.zeros_like(U); sub[max(0, by0):by1, bx0:bx1] = gold[max(0, by0):by1, bx0:bx1]; l2, n2 = ndimage.label(sub); out = np.unique(l2[sub & ~I]); out = out[out > 0]
            I &= ~np.isin(l2, out)
        I = ndimage.binary_opening(I, disk(3))
    else:
        big = lab == (int(np.argmax(sz)) + 1); I = ndimage.binary_fill_holes(ndimage.binary_closing(big, disk(9))); I = ndimage.binary_opening(I, disk(6))
    return I, D


def blank(im, I, D, target=None):
    """ボードの 中を 何も 書いて いない 板に：板の 色（字で ない 所）を なめらかに のばす・ふちの 内がわは 少し 暗く。target＝前の 絵の 板の 色（まん中の 値を これに 合わせる）"""
    good = I & D & ndimage.binary_erosion(I, disk(8))
    med = np.median(im[good], 0); dc = np.abs(im - med).max(2); good &= dc < 26                      # 板の 色に 近い 点 だけ（字・ハンコ・飾りの 色を まぜない）
    good = ndimage.binary_erosion(good, disk(2))
    # 板の 色を「なめらかな 面」（x・y の 2次式）に する：行や ボタンの あとの まだらが のこらない。はずれた 点（字の ふち・かげ）は 2回 はぶいて 当てはめ直す
    out = im.copy(); ys, xs = np.nonzero(good); sel = np.random.RandomState(1).choice(len(ys), min(len(ys), 200000), replace=False); ys, xs = ys[sel], xs[sel]
    yi, xi = np.nonzero(I); cx, cy, sx, sy = xi.mean(), yi.mean(), max(1.0, np.ptp(xi) / 2), max(1.0, np.ptp(yi) / 2)
    def basis(x, y):
        u, v = (x - cx) / sx, (y - cy) / sy; return np.stack([np.ones_like(u), u, v, u * u, v * v, u * v], 1)
    Bm = basis(xs.astype(np.float64), ys.astype(np.float64)); col = im[ys, xs].astype(np.float64); keep = np.ones(len(ys), bool)
    for _ in range(3):
        coef = np.linalg.lstsq(Bm[keep], col[keep], rcond=None)[0]; res = np.abs(Bm @ coef - col).max(1); keep = res < max(6.0, np.percentile(res, 85))
    surf = np.clip(basis(xi.astype(np.float64), yi.astype(np.float64)) @ coef, 0.5, 255)
    if target is not None:                                        # 前の 絵の 板の 色に（面の むら＝明るい 所と 暗い 所の 比 は そのまま・比は 0.75〜1.3 に おさえる）
        sm = np.median(surf, 0); rel = np.clip(surf / sm, 0.75, 1.3); surf = rel * np.asarray(target, np.float64)
    out[yi, xi] = surf.astype(np.float32)
    dist = ndimage.distance_transform_edt(I); sh = 1 - 0.30 * np.exp(-dist / 14.0); out[I] *= sh[I][:, None]
    return out


def slice9(arr, band, add):
    a, b = band; nh = max(1, (b - a) + int(round(add))); mid = cv2.resize(arr[a:b], (arr.shape[1], nh), interpolation=cv2.INTER_LANCZOS4 if arr.dtype != bool else cv2.INTER_NEAREST)
    if mid.ndim < arr.ndim: mid = mid[..., None]
    return np.concatenate([arr[:a], mid, arr[b:]], 0)


def bloom(rgba_f, strength=0.32):
    """明るい 所を にじませる（rgba：0〜1・すき通りを 掛けた 色で 計算）"""
    rgb = rgba_f[..., :3] * rgba_f[..., 3:4]; lum = rgb.max(2, keepdims=True); hi = rgb * np.clip((lum - 0.84) / 0.16, 0, 1)
    g = sum(cv2.GaussianBlur(hi, (0, 0), s) for s in (6, 16, 40)) / 3.0
    return g * strength


def place(layer, s, ar, ap):
    """layer（RGBA uint8・写した 絵の 大きさ）を s 倍に して、写した 絵の 点 ar が 前の 絵の 点 ap に 来る ように 置く → 前の 絵の 大きさの RGBA（float 0〜1）"""
    ys, xs = np.nonzero(layer[..., 3] > 0); x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1; crop = layer[y0:y1, x0:x1]
    w, h = max(1, int(round((x1 - x0) * s))), max(1, int(round((y1 - y0) * s)))
    pm = crop.astype(np.float32) / 255; pm[..., :3] *= pm[..., 3:4]                                   # すき通りを 掛けて から 小さく する（ふちに 色が にじまない）
    sm = cv2.resize(pm, (w, h), interpolation=cv2.INTER_AREA)
    ox = int(round(ap[0] - (ar[0] - x0) * s)); oy = int(round(ap[1] - (ar[1] - y0) * s))
    out = np.zeros((CH, CW, 4), np.float32); sx0, sy0 = max(0, -ox), max(0, -oy); dx0, dy0 = max(0, ox), max(0, oy); ww, hh = min(w - sx0, CW - dx0), min(h - sy0, CH - dy0)
    if ww > 0 and hh > 0: out[dy0:dy0 + hh, dx0:dx0 + ww] = sm[sy0:sy0 + hh, sx0:sx0 + ww]
    return out                                                                                         # すき通りを 掛けた 色


def over(dst, src):                      # 掛けた 色の 重ね
    return src + dst * (1 - src[..., 3:4])


def wrap(L, bgb, k):
    """部品の ふちに、うしろの 背景の 光を 少し のせる（明るい 背景の 前で 切りぬきに 見えない ように）。bgb＝ぼかした 背景"""
    a = L[..., 3]; e = np.clip((a - cv2.GaussianBlur(a, (0, 0), 7)) * 2, 0, 1) * a
    L = L.copy(); L[..., :3] = np.minimum(L[..., :3] + bgb * (e * k)[..., None], a[..., None]); return L


def compose(name, dbg=False):
    c = CFG[name]; P = np.asarray(Image.open(f'{A}/bcp_{name}.webp').convert('RGB'), np.float32) / 255; P = P.copy()
    q = np.array(B.design(name)['q']) * 3; qx0, qy0, qx1, qy1 = q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max()
    im, buf, z0 = load(name); u = c.get('unlabel')
    if u and u['kind'] == 'hang': unlabel_hang(buf, u['box'], u['z'])
    if u and u['kind'] == 'fill': unlabel_fill(buf, u['box'])
    al8 = buf['al8']; al = al8 > 128; z = buf['z']; H, W = al.shape
    I, D = interior(name, im, al, z, z0); ys, xs = np.nonzero(I); ix0, iy0, ix1, iy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1      # 板の 中の 箱（前の 絵の 板に 合わせる もと）
    if u and u['kind'] == 'bow':                                  # 花の 帯を 作り直す → 板の 中（ぬりつぶす 所）は 作り直した 絵で 見つけ直す（箱は もとの まま：アプリの 字の 場所が かわらない）
        unlabel_bow(buf, im, u); al8 = buf['al8']; al = al8 > 128; z = buf['z']; I, D = interior(name, im, al, z, z0)
    # 部品に 分ける
    char = np.zeros_like(al)
    if c.get('split') == 'z':                                     # ボード＝板の 箱（わくと 飾りの 分 ひろげる）の 中で 板の 面より 前に ある もの・のこりが 馬
        ys_, xs_ = np.nonzero(I); mx, mt, mb = c.get('margin', (110, 190, 220)); yy, xx = np.mgrid[0:H, 0:W]
        inbox = (xx >= xs_.min() - mx) & (xx <= xs_.max() + mx) & (yy >= ys_.min() - mt) & (yy <= ys_.max() + mb)
        char = al & ~(inbox & (z > z0 - c.get('zt', 0.03)))
        lab_, n_ = ndimage.label(char); sz_ = ndimage.sum(char, lab_, range(1, n_ + 1)); small = np.isin(lab_, [i + 1 for i in range(n_) if sz_[i] < 1500]); char &= ~small      # 小さな かけらは ボードへ
        bl_, bn_ = ndimage.label(al & ~char); bs_ = ndimage.sum(al & ~char, bl_, range(1, bn_ + 1)); char |= (al & ~char) & (bl_ != (int(np.argmax(bs_)) + 1))                      # ボードは いちばん 大きな かたまり だけ（はなれた かけら＝馬の あご など は 馬へ）
        lab_, n_ = ndimage.label(char); sz_ = ndimage.sum(char, lab_, range(1, n_ + 1)); zm_ = ndimage.median(z, lab_, range(1, n_ + 1))
        char &= ~np.isin(lab_, [i + 1 for i in range(n_) if sz_[i] < 0.05 * sz_.max() and zm_[i] > z0 - 0.07])                    # 板の 面の 近くに ある 小さな かけら（わくの 飾りの 先）は ボード（馬と いっしょに 動かさない）
    elif c.get('split'): char = al.copy(); char[:c['split'][1]] = False
    cms = []
    for ch in c.get('chars', []):
        m = char.copy()
        if ch['pick'] in ('left', 'right'):
            lab, n = ndimage.label(m); com = ndimage.center_of_mass(m, lab, range(1, n + 1)); szs = ndimage.sum(m, lab, range(1, n + 1)); m2 = np.zeros_like(m)
            for i in range(n):
                if szs[i] > 2000 and ((com[i][1] < W / 2) == (ch['pick'] == 'left')): m2 |= lab == i + 1
            m = m2
        cms.append(m)
    # 色：もとの 色に 光を 当て直す（部品ごとに 明るさ・ふちの 光）
    R = relight(buf, gold=c.get('gold', 1.0), gold_t=c.get('gold_t', 0.0)); rgbf = np.zeros((H, W, 3), np.float32)
    rest = al.copy()
    for m, ch in zip(cms, c.get('chars', [])): rgbf[m] = finish(R, im, m, ch.get('look', {})); rest &= ~m
    rgbf[rest] = finish(R, im, rest, c.get('look', {})); del R
    board = al & ~char
    # 板の 中：何も 書いて いない 板・前の 絵の 板の 色
    ins = np.zeros((CH, CW), np.uint8); cv2.fillConvexPoly(ins, np.round((q - q.mean(0)) * 0.72 + q.mean(0)).astype(np.int32), 1); told = np.median(P[ins > 0], 0) * 255
    imb = blank(rgbf, I, D, told)
    rgba = np.dstack([np.clip(imb, 0, 255).astype(np.uint8), al8])
    # ── ボード：板の 中の 箱を 前の 絵の 板に 合わせる
    s = (qx1 - qx0) / (ix1 - ix0); add = (qy1 - qy0) / s - (iy1 - iy0)
    bl = rgba.copy(); bl[..., 3] = np.where(board, al8, 0); bl = slice9(bl, c['band'], add)
    Lb = place(bl, s, (ix0, iy0), (qx0, qy0))
    if c.get('side'):                                             # 場面の 光が 左右で ちがう（24連勝：左＝紫・右＝金）→ わくに その 色を 掛ける
        tl_, tr_ = c['side']; xs_ = np.clip((np.arange(CW) - qx0) / (0.6 * (qx1 - qx0)), 0, 1); xs_ = (xs_ * xs_ * (3 - 2 * xs_))[None, :, None]; Lb[..., :3] *= np.array(tl_, np.float32) * (1 - xs_) + np.array(tr_, np.float32) * xs_; Lb[..., :3] = np.minimum(Lb[..., :3], Lb[..., 3:4])
    Lf = None
    if c.get('halo'):                                             # わく（板の 中を のぞいた ボード）の 形：まわりに 光を にじませる
        fr_ = bl.copy(); fr_[..., 3] = np.where(slice9(I, c['band'], add), 0, fr_[..., 3]); fr_[..., :3] = 255; Lf = place(fr_, s, (ix0, iy0), (qx0, qy0))[..., 3]
    layers = []
    for m, ch in zip(cms, c.get('chars', [])):
        cl = rgba.copy(); cl[..., 3] = np.where(m, al8, 0); ar = list(ch['at'][0])
        if ch.get('neck'):                                        # ボードに かくれて 切れた 首を 少し のばす（切れ目が 新しい ボードの うしろに 入る ように）
            (a, b), addn = ch['neck']; cl = slice9(cl, (a, b), addn)
            if ar[1] > b: ar[1] += addn
        layers.append((place(cl, ch['s'], ar, ch['at'][1]), ch))
    # ── 背景：新しい 部品の まわり だけ うめる
    cov = Lb[..., 3].copy()
    for Lc, _ in layers: cov = np.maximum(cov, Lc[..., 3])
    ring = int(c.get('ring', 30)); k = 2 * ring + 1
    obj = (cov > 0.05).astype(np.uint8); dil = cv2.dilate(obj, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    for e in c.get('erase', []):                                                                            # 前の 絵の 札
        ex0, ey0, ex1, ey1 = e[:4]
        if len(e) > 4 and e[4] == 'h':                           # 横に 長い 光の 帯の 上の 札：左右の 色を 行ごとに つなぐ（上下から うめると たての 光の すじに なる）
            la = P[ey0:ey1, ex0 - 14:ex0 - 2].mean(1); rb = P[ey0:ey1, ex1 + 2:ex1 + 14].mean(1); t = np.linspace(0, 1, ex1 - ex0, dtype=np.float32)[None, :, None]
            fl = cv2.GaussianBlur(la[:, None, :] * (1 - t) + rb[:, None, :] * t, (0, 0), 6); mk = np.zeros((CH, CW), np.float32); mk[ey0 + 6:ey1 - 6, ex0 + 6:ex1 - 6] = 1; mk = cv2.GaussianBlur(mk, (0, 0), 9)[ey0 - 16:ey1 + 16, ex0 - 16:ex1 + 16, None]
            pad = P[ey0 - 16:ey1 + 16, ex0 - 16:ex1 + 16].copy(); full = pad.copy(); full[16:-16, 16:-16] = fl; P[ey0 - 16:ey1 + 16, ex0 - 16:ex1 + 16] = pad * (1 - mk) + full * mk
        else: dil[ey0:ey1, ex0:ex1] = 1
    # 新しい 部品の 下と まわり（ring）を、その 外がわの 背景から うめる（前の 絵の キャラ・わくの ふちが のこらない）
    # うめる 所の さかいに またがる 小さな もの（紙ふぶき・星）は まるごと うめる（半分 だけ ぼけた 紙ふぶきが のこらない）
    P8 = (P * 255).astype(np.uint8); feat = (np.abs(P8.astype(np.int16) - cv2.medianBlur(P8, 41).astype(np.int16)).max(2) > 42).astype(np.uint8)
    nl, lab, stats, _ = cv2.connectedComponentsWithStats(feat, 8); inside = np.bincount(lab[dil > 0], minlength=nl); tot = stats[:, cv2.CC_STAT_AREA]
    cross = [i for i in range(1, nl) if 0 < inside[i] < tot[i] and tot[i] < 5000]
    if cross: dil = np.maximum(dil, cv2.dilate(np.isin(lab, cross).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))))
    sc = 3; small = cv2.resize((P * 255).astype(np.uint8), (CW // sc, CH // sc), interpolation=cv2.INTER_AREA); msk = cv2.resize(dil, (CW // sc, CH // sc), interpolation=cv2.INTER_NEAREST)
    fill = cv2.inpaint(small, msk, 6, cv2.INPAINT_TELEA); fill = cv2.resize(fill, (CW, CH), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255; fill = cv2.GaussianBlur(fill, (0, 0), 5)
    w = cv2.GaussianBlur(dil.astype(np.float32), (0, 0), 9)[..., None]; bg = P * (1 - w) + fill * w
    # ふちに 背景の 光を のせる
    wk = c.get('wrap', 0.55)
    if wk:
        bgb = cv2.GaussianBlur(bg, (0, 0), 22); Lb = wrap(Lb, bgb, wk * c.get('wrap_board', 0.4)); layers = [(wrap(Lc, bgb, wk), ch) for Lc, ch in layers]
    out = np.dstack([bg, np.ones((CH, CW), np.float32)])
    back = [L for L in layers if not L[1].get('front')]; front = [L for L in layers if L[1].get('front')]
    for Lc, ch in back: out = over(out, Lc)
    out = over(out, Lb)
    for Lc, ch in front: out = over(out, Lc)
    # 明るい 所の にじみ（3D の 部品 だけ）
    allL = Lb.copy()
    for Lc, _ in layers: allL = over(allL, Lc)
    st = allL.copy(); a = np.maximum(st[..., 3:4], 1e-4); st[..., :3] = st[..., :3] / a
    rgb = out[..., :3] + bloom(st, c.get('bloom', 0.4))
    if Lf is not None:                                            # わくの 光（前の 絵の わくは 光って いる）
        hl_, hr_, hk_, hs_ = c['halo']; g_ = sum(cv2.GaussianBlur(Lf, (0, 0), s_) for s_ in hs_) / len(hs_); xs_ = np.linspace(0, 1, CW, dtype=np.float32)[None, :, None]
        rgb = 1 - (1 - np.clip(rgb, 0, 1)) * (1 - hk_ * g_[..., None] * (np.array(hl_, np.float32) * (1 - xs_) + np.array(hr_, np.float32) * xs_) / 255)
    # 口の 中の 光（馬）
    for Lc, ch in layers:
        if ch.get('mouth'):
            (mx, my), col, mk_ = ch['mouth']; ar = ch['at'][0]; ap = ch['at'][1]; px = ap[0] + (mx - ar[0]) * ch['s']; py = ap[1] + (my - ar[1]) * ch['s']
            yy, xx = np.mgrid[0:CH, 0:CW]; r2 = ((xx - px) ** 2 + (yy - py) ** 2) / (70.0 * ch['s'] / 0.85) ** 2; g = np.exp(-r2 * 1.6)[..., None] * np.array(col, np.float32) / 255
            rgb = 1 - (1 - np.clip(rgb, 0, 1)) * (1 - mk_ * g)
    res = (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    print(name, 'board scale', round(float(s), 4), 'add rows', round(float(add), 1), 'chars', len(layers), '板の 色', np.round(told).astype(int).tolist(), flush=True)
    return res


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'render':
        render(sys.argv[2])
    elif len(sys.argv) >= 5 and sys.argv[1] == 'compose':
        W3, A, out = sys.argv[2], sys.argv[3], sys.argv[4]; os.makedirs(out, exist_ok=True)
        for n in (sys.argv[5:] or STAGES):
            res = compose(n); f = os.path.join(out, f'bcp_{n}_3d.webp'); Image.fromarray(res).save(f, 'WEBP', quality=90, method=6); print('  →', f, os.path.getsize(f), flush=True)
    else:
        print('使い方：shusse3d.py render <作業フォルダ>／compose <作業フォルダ> <前の 絵の フォルダ> <出す フォルダ> [名前…]')
