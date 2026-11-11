# 軽い 版（ios/lite/…：kisekae/lite_assets.py）の 画質を もとと くらべる（第4.146版）
#   python3 kisekae/lite_quality.py [出す フォルダ]     … 絵（WebP quality 75）と 動画（CRF 24：第4.155版までは 29）を 1つずつ もとと くらべて、種類ごとに まとめる。数は <出す フォルダ>/lite_quality.json にも 書く
#   絵：PSNR（色の 差・dB：大きい ほど 近い。すき通しの 絵は 見える 所 だけ＝こさで 重みを つける）と SSIM（形の 近さ・明るさで：1 が 同じ）
#   動画：コマごとの PSNR・SSIM（ffmpeg）。平均・いちばん 悪い コマ・さいごの 15コマ（動画の あとに 出る「さいごの 1まい」との つなぎ目）
#   2026/11/10 の 数（少し やわらか）：絵は PSNR の まん中 38〜42dB・SSIM 0.96〜0.99、動画は SSIM 0.971〜0.985・PSNR 平均 38.4〜42.7dB
import json, os, re, subprocess, sys
import numpy as np
from PIL import Image
import cv2
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
sys.path.insert(0, W); import assets_dir as AD
OUT = sys.argv[1] if len(sys.argv) > 1 else None


def ssim_y(a, b):
    a = a.astype(np.float64); b = b.astype(np.float64); C1, C2 = 6.5025, 58.5225
    g = lambda x: cv2.GaussianBlur(x, (11, 11), 1.5)
    ma, mb = g(a), g(b); va = g(a * a) - ma * ma; vb = g(b * b) - mb * mb; vab = g(a * b) - ma * mb
    s = ((2 * ma * mb + C1) * (2 * vab + C2)) / ((ma * ma + mb * mb + C1) * (va + vb + C2))
    return s


def pic(name, f):
    a = np.asarray(Image.open(os.path.join(AD.master(name), f)).convert('RGBA')).astype(np.float64)
    b = np.asarray(Image.open(os.path.join(AD.lite(name), f)).convert('RGBA')).astype(np.float64)
    assert a.shape == b.shape, f
    w = a[..., 3] / 255.0                                  # 見える 所 だけ（こさで 重み）
    if w.sum() < 1:
        return None
    d2 = ((a[..., :3] - b[..., :3]) ** 2).mean(-1)
    mse = float((d2 * w).sum() / w.sum())
    ya = a[..., :3] @ np.array([.299, .587, .114]); yb = b[..., :3] @ np.array([.299, .587, .114])
    s = ssim_y(ya, yb) if min(a.shape[:2]) >= 16 else np.ones(a.shape[:2])
    ss = float((s * w).sum() / w.sum())
    dmax = float((np.abs(a[..., :3] - b[..., :3]).max(-1) * (w > .5)).max())
    return {'psnr': 99.0 if mse < 1e-9 else float(10 * np.log10(255 * 255 / mse)), 'ssim': ss, 'max': dmax, 'px': int(a.shape[0] * a.shape[1])}


def film(f):
    a = os.path.join(AD.lite('fx_assets'), f); ref = os.path.join(AD.master('fx_assets'), f)
    run = lambda flt: subprocess.run(['ffmpeg', '-v', 'error', '-i', a, '-i', ref, '-lavfi', f'[0:v][1:v]{flt}=stats_file=-', '-f', 'null', '-'], capture_output=True, text=True, check=True).stdout
    ss = [float(x) for x in re.findall(r'n:\d+ .*?All:([0-9.]+) \(', run('ssim'))]
    ps = [float(x) if x != 'inf' else 99.0 for x in re.findall(r'n:\d+ mse_avg:[0-9.]+ .*?psnr_avg:([0-9.inf]+)', run('psnr'))]
    assert len(ss) == len(ps) and len(ss) > 30, (f, len(ss), len(ps))
    i = int(np.argmin(ps))
    return {'frames': len(ps), 'ssim': float(np.mean(ss)), 'ssim_min': float(min(ss)), 'psnr': float(np.mean(ps)), 'psnr_min': float(min(ps)), 'worst': i, 'worst_t': round(i / 30, 2),
            'last15_psnr': float(np.mean(ps[-15:])), 'last15_ssim': float(np.mean(ss[-15:])), 'last_psnr': ps[-1]}


def kind(name, f):
    if name == 'bcp_assets':
        if f.startswith('bcp_t_'): return '結果ボード：見本'
        im = Image.open(os.path.join(AD.master(name), f))
        if im.size == (1170, 2532): return '結果ボード：背景' if im.mode == 'RGB' else '結果ボード：前の 絵'
        return '結果ボード：キャラ・動かない 物'
    if name == 'tc_assets': return '馬の 色'
    if name == 'fig_assets': return '棚の 色' if 'shelf' in f else ('フィギュアの 色（小）' if f.endswith('_cs.webp') else 'フィギュアの 色')
    return name


if __name__ == '__main__':
    res = {'pics': {}, 'films': {}}
    for name in AD.NAMES:
        man = AD.manifest(name)
        if not man:
            print('※ 軽い 版が ない：', name); continue
        for f, e in sorted(man['files'].items()):
            if e['how'] == 'webp':
                q = pic(name, f)
                if q:
                    q.update(kind=kind(name, f), s0=e['src'][0], s1=e['size']); res['pics'][f] = q
            elif e['how'] == 'film':
                q = film(f); q.update(s0=e['src'][0], s1=e['size']); res['films'][f] = q
                print(f'動画 {f}：{q["s0"] / 1e6:.2f}→{q["s1"] / 1e6:.2f}MB  SSIM {q["ssim"]:.4f}（最小 {q["ssim_min"]:.4f}）PSNR 平均 {q["psnr"]:.2f}・最小 {q["psnr_min"]:.2f}（{q["worst_t"]}秒）・さいごの 15コマ {q["last15_psnr"]:.2f}dB／SSIM {q["last15_ssim"]:.4f}', flush=True)
    by = {}
    for f, q in res['pics'].items():
        by.setdefault(q['kind'], []).append((f, q))
    for k, l in by.items():
        ps = sorted(q['psnr'] for _f, q in l); ss = sorted(q['ssim'] for _f, q in l); s0 = sum(q['s0'] for _f, q in l); s1 = sum(q['s1'] for _f, q in l)
        worst = sorted(l, key=lambda x: x[1]['psnr'])[:3]
        print(f'絵 {k}：{len(l)}こ {s0 / 1e6:.2f}→{s1 / 1e6:.2f}MB（{(s1 - s0) / s0 * 100:+.0f}%） PSNR 最小 {ps[0]:.1f}・まん中 {ps[len(ps) // 2]:.1f}・最大 {ps[-1]:.1f}  SSIM 最小 {ss[0]:.4f}・まん中 {ss[len(ss) // 2]:.4f}  '
              f'悪い 方から：' + '・'.join(f'{f}（{q["psnr"]:.1f}dB）' for f, q in worst), flush=True)
    if OUT:
        os.makedirs(OUT, exist_ok=True); json.dump(res, open(os.path.join(OUT, 'lite_quality.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
