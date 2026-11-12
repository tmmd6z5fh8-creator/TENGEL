"""シルバー帯・ゴールド帯・マスター帯の壁紙（metal_wall.py：銀・金の馬の像／テンゲルの 像が いつも キラキラ）の絵と形。flat/silver_banner.py・gold_banner.py と同じ像・同じ作り
   第4.149版：像は まさちゃんの 3D（flat/metal_glb.py：シルバー帯・ゴールド帯＝「Silver Thunder」・マスター帯＝「Tenger」）。3D が 手元に ない とき／METAL_HORSE=old は 前の 像（sdfr・シルバー帯と ゴールド帯 だけ）
   - tengel_banner.webp・tengel_base.webp：マスター帯（flat/master_banner.py：暗い 舞台・うしろからの 金の 光・金の 光の 輪・台の 上の 金の 馬と 騎手）。形と きらめきは metal_run.json の tengel（shape も 中に：像が ちがう ので）
   python3 flat/metal_run.py <出力フォルダ> --install   → できた 絵を ios/kisekae_blobs/<中身の md5>.webp に 置いて（前の 絵は 消さない）、metal_blobs.json・blobs20.json（選ぶ 画面の 小さい 絵）・metal_run.json を 書きかえる
   python3 flat/metal_run.py <出力フォルダ> --only tengel [--install]   → マスター帯 だけ 作る（第4.158版：像を 入れかえた とき）。シルバー帯・ゴールド帯の 絵・id・形（metal_run.json の shape・silver・gold）は 1字も かえない
   - silver_banner.webp・gold_banner.webp：いまの絵（きらめきつき）。顔のすじを平らにした像（silver_horse.flat_face）で 描きなおした絵
   - silver_base.webp・gold_base.webp：同じ絵から きらめき（4本の光）だけ ぬいた絵（壁紙では きらめきを ページの SVG で またたかせる）
   - metal_run.json：像の形（ふちの線：光が走るのを 像の中だけにする）・きらめきの場所と長さ（いまの絵の4つ＋またたく所）・
     こまかい光の粒の場所・うしろの光の輪（まん中・半径）・床の線（780×320 の座標）
   python3 flat/metal_run.py <出力フォルダ>（sdfr がいる・約40秒）"""
import sys, os, json, math, shutil
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import silver_banner as SB
import gold_banner as GB
import metal_glb as MG
import master_banner as MB
import style2d as S2
from style2d import save_webp

W, Hh = SB.W, SB.Hh
EXTRA = 10                 # またたく きらめき（いまの絵の4つの ほかに）
EXTRA_GAP = 30             # きらめきどうしの 間（画素）
DOTS = 26                  # こまかい光の粒


def use_glb():
    """像は まさちゃんの 3D の 馬か（第4.149版から：3D（METAL_HORSE_GLB）が 手元に あれば そちら。METAL_HORSE=old で 前の 像＝sdfr が いる）"""
    return os.environ.get('METAL_HORSE', 'glb') != 'old' and MG.available()


def f1(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s


def outline(A, eps=0.6):
    """像の ふちの線（2倍で ふちを たどって なめらかに）→ SVG の d（いちばん大きい輪＋小さい輪も）"""
    SS = 2
    m2 = cv2.resize(A, (W * SS, Hh * SS), interpolation=cv2.INTER_LINEAR)
    cs, _ = cv2.findContours((m2 > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    d = ''
    for c in sorted(cs, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(c) < 20 * SS * SS:
            continue
        p = c[:, 0, :].astype(np.float32)
        kk = np.arange(-4, 5); g = np.exp(-(kk / 1.8) ** 2); g /= g.sum()
        ps = np.stack([np.convolve(np.r_[p[-4:, k], p[:, k], p[:4, k]], g, 'valid') for k in (0, 1)], 1) / SS
        q = cv2.approxPolyDP(ps.reshape(-1, 1, 2).astype(np.float32), eps, True)[:, 0, :]
        d += 'M' + 'L'.join(f'{f1(x)} {f1(y)}' for x, y in q) + 'Z'
    return d


def glints(R, spark, n=EXTRA, gap=EXTRA_GAP, ymax=None):
    """いまの絵の きらめき（spark）の ほかに、像の明るい所から n か所（たがいに gap 以上 はなす）。ymax＝これより 上 だけ（マスター帯：台と 台の 字の 上には 出さない）。
       R['metal']（金の 所：マスター帯）が あれば 金の 上 だけ（騎手の 白い ズボン・緑の 服には 出さない）"""
    A = np.clip(R['a'], 0, 1)
    rgb = SB.statue_srgb(R)
    lum = rgb.max(2) * A
    if 'metal' in R:
        lum = lum * (R['metal'] > 0.5)
    if ymax is not None:
        lum[ymax:] = 0
    lum_s = cv2.GaussianBlur(lum, (0, 0), 1.0)
    inner = cv2.erode((A > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    taken = [(x, y) for x, y, L in spark]
    out = []
    for idx in np.argsort((lum_s * inner).ravel())[::-1][:60000]:
        y, x = divmod(int(idx), W)
        if lum_s[y, x] < 0.72:
            break
        if all((x - tx) ** 2 + (y - ty) ** 2 > gap ** 2 for tx, ty in taken):
            taken.append((x, y))
            out.append((int(x), int(y), round(float(8 + 6 * (lum_s[y, x] - 0.72) / 0.28), 1)))
        if len(out) >= n:
            break
    return out


def dots(R, n=DOTS, seed=17, ymax=None):
    """こまかい光の粒：像の上の 明るめの所から ばらばらに"""
    A = np.clip(R['a'], 0, 1)
    rgb = SB.statue_srgb(R)
    lum = rgb.max(2) * A
    if 'metal' in R:                                       # 金の 上 だけ（マスター帯）
        lum = lum * (R['metal'] > 0.5)
    if ymax is not None:
        lum[ymax:] = 0
    inner = cv2.erode((A > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    ys, xs = np.nonzero(inner & (lum > 0.55))
    rng = np.random.default_rng(seed)
    pick, out = rng.permutation(len(xs)), []
    for i in pick:
        x, y = int(xs[i]), int(ys[i])
        if all((x - a) ** 2 + (y - b) ** 2 > 22 ** 2 for a, b in out):
            out.append((x, y))
        if len(out) >= n:
            break
    return out


STATUE_Q = 92                  # 馬（主役）だけの 高画質の 絵の 質（WebP・すき通りは 劣化なし）
STATUE_PAD = 4                 # 切りぬきの よゆう（高画質の 絵の 画素）


def save_statue(R, path):
    """馬（主役）だけの 高画質の 絵（まさちゃん 2026/11/11 02:36「壁紙は、馬(主役)だけ画質良くなるようにして！」）：像の 所 だけ 切りぬいた すき通った WebP。
       返り値：壁紙の 絵（780×320）の 中で 置く 場所 [x, y, 幅, 高さ]（metal_wall.py が <image> で 重ねる）。高画質の 絵が ない 像（前の sdfr の 馬）は None"""
    if 'hi_a' not in R:
        return None
    from PIL import Image
    a, rgb = R['hi_a'], R['hi_srgb']
    k = a.shape[1] // W
    ys, xs = np.nonzero(a > 1 / 255)
    x0, y0 = max(int(xs.min()) - STATUE_PAD, 0), max(int(ys.min()) - STATUE_PAD, 0)
    x1, y1 = min(int(xs.max()) + 1 + STATUE_PAD, a.shape[1]), min(int(ys.max()) + 1 + STATUE_PAD, a.shape[0])
    x0, y0 = x0 - x0 % k, y0 - y0 % k                       # 壁紙の 絵の 画素の 境目に 合わせる
    x1, y1 = x1 + (-x1) % k, y1 + (-y1) % k
    u8 = (np.dstack([rgb * (a > 0)[..., None], a])[y0:y1, x0:x1] * 255 + .5).astype(np.uint8)
    Image.fromarray(u8, 'RGBA').save(path, 'WEBP', quality=STATUE_Q, method=6, alpha_quality=100, exact=False)
    back = np.array(Image.open(path).convert('RGBA'))
    assert back.shape == u8.shape and np.array_equal(back[..., 3], u8[..., 3]), path + '：すき通りが かわった'
    return [x0 // k, y0 // k, (x1 - x0) // k, (y1 - y0) // k]


def build(outdir, only=None):
    """only＝作る 像の 名前（'silver'・'gold'・'tengel'）。None なら 3つ とも。only の とき、作らない 像の 形と きらめきは いま 入って いる kisekae/metal_run.json の まま"""
    os.makedirs(outdir, exist_ok=True)
    run = dict(size=[W, Hh])
    if only:
        run = json.load(open(os.path.join(os.path.dirname(HERE), 'metal_run.json')))
        assert run['size'] == [W, Hh] and not (set(only) - {'silver', 'gold', 'tengel'}), only
        assert not ({'silver', 'gold'} & set(only)) or {'silver', 'gold'} <= set(only), 'シルバー帯と ゴールド帯は 同じ 形（shape）なので いっしょに 作る'
        if 'silver' in only:
            run.pop('shape', None)
    glb = use_glb()
    if not only or 'silver' in only:
        print('像：' + ('まさちゃんの 3D の 馬（' + MG.MODELS['horse']['glb'] + '）' if glb else '前の 像（sdfr）'))
    for name, pal in (('silver', SB.SILVER), ('gold', GB.GOLD)):
        if only and name not in only:
            continue
        if glb:
            R = MG.render(name)                    # まさちゃんの 3D の 馬（銀：そのまま・金：同じ 形を 金色に）
        else:
            tmp = os.path.join(S2.TMP, f'metal{os.getpid()}{name}')
            os.makedirs(tmp, exist_ok=True)
            try:
                R, S = SB.render3d(tmp, pal)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        info = {}
        save_webp(SB.compose(R, pal=pal, info=info), os.path.join(outdir, f'{name}_banner.webp'))
        save_webp(SB.compose(R, pal=pal, sparkle=False), os.path.join(outdir, f'{name}_base.webp'))
        A = np.clip(R['a'], 0, 1)
        ys, xs = np.nonzero(A > 0.5)
        if 'shape' not in run:
            gy = info['gy']
            run['shape'] = dict(d=outline(A), box=[int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)], floor=int(gy),
                                ring=[round(W * .5, 1), round(gy * 0.52, 1), 150])
        run[name] = dict(spark=[[x, y, round(L, 2)] for x, y, L in info['spark']], glint=[list(g) for g in glints(R, info['spark'])],
                         dots=[list(p) for p in dots(R)])
        sb = save_statue(R, os.path.join(outdir, f'{name}_statue.webp'))
        if sb:
            run[name]['statue'] = sb
        print(name, 'きらめき', run[name]['spark'], 'またたく', len(run[name]['glint']), '粒', len(run[name]['dots']), '馬 だけの 高画質の 絵', sb)
    # マスター帯（第4.149版）：まさちゃんの 3D の 像（台の 上の 金の 馬）。像が ちがう ので 形（shape）も tengel の 中に。ped＝台の 上の はし（きらめき・光の 粒は 馬の 所 だけ）
    if only and 'tengel' not in only:
        pass
    elif MG.available('tengel'):
        R = MG.render('tengel')
        info = {}
        save_webp(MB.compose(R, info=info), os.path.join(outdir, 'tengel_banner.webp'), q=MB.QUALITY)
        save_webp(MB.compose(R, sparkle=False), os.path.join(outdir, 'tengel_base.webp'), q=MB.QUALITY)
        A = np.clip(R['a'], 0, 1)
        ys, xs = np.nonzero(A > 0.5)
        ped = info['ped'] - 6
        # floor＝床の はじまり（台の 奥：光の 輪を 回る 光は ここより 上 だけ）・base＝台の いちばん 下・ped＝台の 上の はし
        run['tengel'] = dict(shape=dict(d=outline(A), box=[int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)], floor=int(info['hy']), base=int(info['gy']), ring=info['ring'], ped=int(info['ped'])),
                             spark=[[x, y, round(L, 2)] for x, y, L in info['spark']], glint=[list(g) for g in glints(R, info['spark'], ymax=ped)],
                             dots=[list(p) for p in dots(R, ymax=ped)])
        sb = save_statue(R, os.path.join(outdir, 'tengel_statue.webp'))
        if sb:
            run['tengel']['statue'] = sb
        print('tengel', 'きらめき', run['tengel']['spark'], 'またたく', len(run['tengel']['glint']), '粒', len(run['tengel']['dots']), '台の 上', info['ped'], '台の 下', info['gy'], '床の はじまり', info['hy'], '輪', info['ring'])
    else:
        print('※ マスター帯の 3D（' + MG.MODELS['tengel']['glb'] + '）が ない ので、マスター帯の 絵は 作らない')
    json.dump(run, open(os.path.join(outdir, 'metal_run.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    return run


def install(outdir, only=None):
    """できた 絵（<名前>_banner.webp・<名前>_base.webp）を 手元の 絵の フォルダ（ios/kisekae_blobs/<中身の md5>.webp）に 置いて、id を metal_blobs.json・blobs20.json
       （選ぶ 画面の 小さい 絵＝いまの 絵）に 書く。形と きらめき（metal_run.json）も kisekae/ に。前の 絵（もと）は 消さない・上書きしない（同じ 名前＝同じ 中身）。
       only＝入れる 像の 名前（ほかの 像の id は さわらない）"""
    import hashlib
    K = os.path.dirname(HERE)
    blob_dir = os.environ.get('KISEKAE_ASSETS') or os.path.join(os.path.dirname(K), 'ios', 'kisekae_blobs')
    mb_path, b20_path = os.path.join(K, 'metal_blobs.json'), os.path.join(K, 'blobs20.json')
    mb, b20 = json.load(open(mb_path)), json.load(open(b20_path))
    for key in ('silver_banner', 'silver_base', 'silver_statue', 'gold_banner', 'gold_base', 'gold_statue', 'tengel_banner', 'tengel_base', 'tengel_statue'):
        if only and key.split('_')[0] not in only:
            continue
        src = os.path.join(outdir, key + '.webp')
        if not os.path.exists(src):
            mb.pop(key, None)
            continue
        data = open(src, 'rb').read()
        bid = hashlib.md5(data).hexdigest()
        dst = os.path.join(blob_dir, bid + '.webp')
        if os.path.exists(dst):
            assert open(dst, 'rb').read() == data, dst
        else:
            open(dst, 'wb').write(data)
        mb[key] = bid
        print(key, bid, len(data))
    for theme, key in (('silver', 'silver_banner'), ('golden', 'gold_banner'), ('tengel', 'tengel_banner')):
        if key in mb:
            b20[theme] = mb[key]
    open(mb_path, 'w').write(json.dumps(mb, ensure_ascii=False) + '\n')                 # 今までと 同じ 書き方（1行）
    open(b20_path, 'w').write(json.dumps(b20, ensure_ascii=False, indent=1) + '\n')
    shutil.copy(os.path.join(outdir, 'metal_run.json'), os.path.join(K, 'metal_run.json'))


if __name__ == '__main__':
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
    build(sys.argv[1], only)
    if '--install' in sys.argv:
        install(sys.argv[1], only)
