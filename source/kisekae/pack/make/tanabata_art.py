"""七夕の 壁紙（壁紙パック・第4.93版）の 織姫の 馬と 彦星の 馬：いままでの 壁紙と 同じ 馬（horse_flat）の ギャロップ（flat/sea_run.py と 同じ 足の 動き）と
   立って 顔を 少し 前へ 出した 1コマ（まん中で 会った とき）。どちらも 右を 向いて 描く（左へ 走る ときは ページで 左右に うらがえす）。
   ・織姫の 馬（o）：白い 体・桃色が かった 白い たてがみ・桃色の 布（白い 花の もよう・金の ふち）・前髪の 上に 花の かざり（桃色・白・うす桃の 花と 葉）・
     き甲から 背中を こえて うしろへ ふわっと なびく 羽衣（うすい 桃色の すきとおる 布・走る コマごとに ゆれる）
   ・彦星の 馬（h）：明るい 栗毛・こげ茶の たてがみ・青い 布（金の 星）・首に 青い ひもと 金の 鈴（牛かいの 鈴）
   ・まわりに やわらかい 星の 光（ぼかした ふち）・走る コマは 地面に ついた ひづめの うしろに 小さな 星の 粉
   python3 kisekae/pack/make/tanabata_art.py [o h]   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の tanabata.o_run・o_stand・h_run・h_stand
     （meta の anchor＝ひづめの まん中と 地面：780×320 の 絵の 中の 場所。ページは ここを 天の川の 道に 合わせる）"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import render, gallop_poses, gallop_stance, ground_dy, make_sheet, save_webp, record, preview_png, HOOF_ORDER  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402
from cute_horse import smooth, path, stroke, circ, ell, unit, V, f2  # noqa: E402

N = 10
GROUND = 218
SPOT = dict(pose='gallop', facing='right', box=(40, 40, 296, 222), azim=6, shadow=('#000000', 0.0))
PALS = dict(
    o=dict(body='#FFFFFF', shade='#DCCFE6', muzzle='#FBF5FA', mane='#FBE6F0', maneD='#EBC3D8', hoof='#B8A0BC', eye='#2A2040',
           blush='#F6B2C8', tack='#E2B04E', ring='#FFF1C8', cloth='#EE8CB6', clothTrim='#F7D27A', num='#FFF6D8', saddle='#7E3A62',
           bodyShade='#F2EBF5'),
    h=dict(body='#D9A66C', shade='#A9753F', muzzle='#ECC89C', mane='#5A3620', maneD='#3A2214', hoof='#4A3A30', eye='#1A120E',
           blush='#E9A27E', tack='#E2B04E', ring='#FFF1C8', cloth='#3567CF', clothTrim='#F7D27A', num='#FFF6D8', saddle='#1E2E6E',
           bodyShade='#CD9A60'))
GLOW = dict(o='#FFE8F3', h='#FFF0C4')
# 立って 鼻を よせる 形（horse_flat の stand を もとに、首を 少し 前へ・頭を 少し 下へ）
STAND = dict(theta=0.0, neck_rot=-13.0, head_ang=-52.0, tail=[-122, -104], tail_kind='hang',
             fore_near=[-122, -88, -90, -60], fore_far=[-126, -92, -90, -60],
             hind_near=[-62, -118, -92, -62], hind_far=[-58, -116, -92, -62])


def star_path(cx, cy, r, r2):
    pts = [(cx + math.cos(math.radians(-90 + k * 36)) * (r if k % 2 == 0 else r2), cy + math.sin(math.radians(-90 + k * 36)) * (r if k % 2 == 0 else r2)) for k in range(10)]
    return 'M' + ' L'.join(f'{f2(x)},{f2(y)}' for x, y in pts) + ' Z'


def sparkle(c, r, col, k=0.2):
    q = r * k
    x, y = c
    d = (f'M{f2(x)},{f2(y - r)} Q{f2(x + q)},{f2(y - q)} {f2(x + r)},{f2(y)} Q{f2(x + q)},{f2(y + q)} {f2(x)},{f2(y + r)} '
         f'Q{f2(x - q)},{f2(y + q)} {f2(x - r)},{f2(y)} Q{f2(x - q)},{f2(y - q)} {f2(x)},{f2(y - r)} Z')
    return path(d, col)


def flower(c, r, col, mid='#F6C945', edge='#E58AB4'):
    """5まいの 花びらの 花（中心 c・大きさ r）"""
    out = []
    for k in range(5):
        a = math.radians(-90 + k * 72)
        q = V(c[0] + math.cos(a) * r * 0.55, c[1] + math.sin(a) * r * 0.55)
        out.append(ell(q, r * 0.52, r * 0.36, math.degrees(a), col, f'stroke="{edge}" stroke-width="{f2(r * 0.07)}"'))
    out.append(circ(c, r * 0.26, mid))
    return out


def top_y(m, x):
    """体の 上の ふち（x の 所・1倍の 画素）"""
    s = m['s']
    ins = m['inside']
    xi = int(round(x * s))
    xi = min(max(xi, 0), ins.shape[1] - 1)
    col = np.nonzero(ins[:, xi])[0]
    return float(col.min()) / s if len(col) else None


def hagoromo(m, ph):
    """羽衣：き甲から 背中に そって、こしの うしろから ふわっと 上へ なびく うすい 布（ph：ゆれの 位相 0〜1）"""
    p, fx = m['p1u'], m['fx']
    xs = [m['wx'](t) for t in (0.10, -0.25, -0.6, -0.95, -1.18)]
    top = []
    for x in xs:
        y = top_y(m, x)
        top.append(V(x, (y if y is not None else m['cloth'][2]) - 0.025 * p))
    w = 2 * math.pi
    tail = []
    last = top[-1]
    for k in range(1, 6):
        x = last[0] - fx * 0.2 * k * p
        y = last[1] - 0.05 * k * p + 0.055 * p * math.sin(w * ph - k * 1.1) * (k / 5)
        tail.append(V(x, y))
    center = top + tail
    n = len(center)
    left, right = [], []
    for i, c in enumerate(center):
        a = center[max(0, i - 1)]
        b = center[min(n - 1, i + 1)]
        d = unit(b - a)
        nv = V(-d[1], d[0])
        hw = (0.022 + 0.05 * (i / (n - 1))) * p
        if i == n - 1:
            hw *= 0.35
        left.append(c + nv * hw)
        right.append(c - nv * hw)
    poly = left + right[::-1]
    out = [path(smooth(poly), '#F7C3DC', 'fill-opacity=".62"'),
           stroke(smooth(center, closed=False), '#FFFFFF', 0.012 * p, 'stroke-opacity=".55"'),
           stroke(smooth(left, closed=False), '#F08DB6', 0.008 * p, 'stroke-opacity=".55"')]
    return out


def acc_factory(who, stance=None):
    def factory(i):
        def acc(m):
            p, fx = m['p1u'], m['fx']
            out = dict(cloth=[], head=[], neck=[], front=[])
            x0, x1, yt, yb, trim = m['cloth']
            if who == 'o':
                for tx, ty, r in ((0.28, 0.42, 0.052), (0.62, 0.34, 0.044), (0.48, 0.72, 0.036)):
                    out['cloth'] += flower(V(x0 + (x1 - x0) * tx, yt + (trim - yt) * ty), r * p, '#FFFFFF', '#F6C945', '#F7C3DC')
                up = V(0, -1)
                hd = unit(m['head_dir'])
                base = m['forelock'] + (m['poll'] - m['forelock']) * 0.35 + up * 0.03 * p
                for a in (-30, 40):                                                  # 葉
                    r = math.radians(a)
                    q = base + V(math.cos(r), math.sin(r)) * 0.05 * p * fx - up * 0.01 * p
                    out['head'].append(ell(q, 0.045 * p, 0.018 * p, a * fx, '#5DBB6A'))
                out['head'] += flower(base + hd * 0.035 * p, 0.05 * p, '#F49AC1', '#F6C945', '#D9709E')
                out['head'] += flower(base - hd * 0.035 * p + up * 0.03 * p, 0.044 * p, '#FFFFFF', '#F6C945', '#E8A6C6')
                out['head'] += flower(base - hd * 0.005 * p - up * 0.035 * p, 0.036 * p, '#FBD0E2', '#F6C945', '#E8A6C6')
                out['front'] += hagoromo(m, i / N if stance is not None else 0.3)
            else:
                cx, cy = (x0 + x1) / 2, (yt + trim) / 2 + 0.03 * p
                out['cloth'].append(f'<path d="{star_path(cx, cy, 0.085 * p, 0.036 * p)}" fill="#F7D27A" stroke="#B8902E" stroke-width="{f2(0.008 * p)}"/>')
                for dx, dy, r in ((-0.16, -0.05, 0.03), (0.15, 0.03, 0.024)):
                    out['cloth'].append(f'<path d="{star_path(cx + dx * p, cy + dy * p, r * p, r * 0.42 * p)}" fill="#FFF1C2"/>')
                top, bot, ax = m['collar'](0.70)
                dv = unit(bot - top)
                mid = (top + bot) / 2 - ax * 0.025 * p
                out['neck'].append(stroke(smooth([top - dv * 0.01 * p, mid, bot + dv * 0.01 * p], closed=False), '#3567CF', 0.03 * p))
                bc = bot + dv * 0.06 * p
                out['neck'] += [stroke(f'M{f2(bot[0])},{f2(bot[1])} L{f2(bc[0])},{f2(bc[1])}', '#3567CF', 0.016 * p),
                                circ(bc + dv * 0.02 * p, 0.048 * p, '#E9B44C', f'stroke="#9A6A1A" stroke-width="{f2(0.008 * p)}"'),
                                circ(bc + dv * 0.0 * p - ax * 0.014 * p, 0.014 * p, '#FFF2C4'),
                                stroke(f'M{f2((bc + dv * 0.045 * p - ax * 0.03 * p)[0])},{f2((bc + dv * 0.045 * p - ax * 0.03 * p)[1])} '
                                       f'L{f2((bc + dv * 0.045 * p + ax * 0.03 * p)[0])},{f2((bc + dv * 0.045 * p + ax * 0.03 * p)[1])}', '#7A5212', 0.01 * p)]
            if stance is not None:                                                   # 星の 粉（地面に ついた ひづめの うしろ）
                rng = np.random.default_rng(100 + i * 7 + (0 if who == 'o' else 50))
                for key in stance[i]:
                    hx, hy = m['hooves'][HOOF_ORDER.index(key)]
                    for k in range(3):
                        c = V(hx - fx * rng.uniform(0.04, 0.2) * p, hy + 0.01 * p - rng.uniform(0.0, 0.08) * p)
                        out['front'].append(sparkle(c, rng.uniform(0.018, 0.034) * p, '#FFF4D6'))
                    out['front'].append(circ(V(hx - fx * rng.uniform(0.08, 0.24) * p, hy - rng.uniform(0.0, 0.05) * p), 0.01 * p, '#FFFFFF'))
            return out
        return acc
    return factory


def hexc(c):
    c = c.lstrip('#')
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def glow_fn(col):
    gc = hexc(col)

    def glow(i, pre, A):
        """まわりの やわらかい 星の 光"""
        g = np.clip(cv2.GaussianBlur(A, (0, 0), 6.0) * 0.42 + cv2.GaussianBlur(A, (0, 0), 16.0) * 0.22, 0, 1)
        pre = pre + gc[None, None, :] * (g * (1 - A))[..., None]
        return pre, A + g * (1 - A)
    return glow


def build(who, out=None):
    pal = PALS[who]
    stance = gallop_stance(N)
    frames, cam = render(pal, SPOT, gallop_poses(N), acc=acc_factory(who, stance), number='', tag=f'pktn{who}', workers=2)
    dys = ground_dy(frames, stance, GROUND, 7.0)
    u8, meta = make_sheet(frames, dys, extra=glow_fn(GLOW[who]))
    meta['dy'] = [round(float(d), 2) for d in dys]
    xs = [h[0] for fr in frames for h in fr[2]]
    meta['anchor'] = [round((min(xs) + max(xs)) / 2, 1), GROUND]
    if out:
        preview_png(u8, os.path.join(out, f'tn_{who}_run.png'), bg=(20, 28, 70))
    bid = save_webp(u8, quality=90)
    record('tanabata', f'{who}_run', bid, meta)
    print(f'{who}_run', bid, meta, flush=True)
    # 立って 鼻を よせる 1コマ（同じ カメラ）
    sp = dict(SPOT, pose=STAND)
    fr2, _ = render(pal, sp, [STAND], acc=acc_factory(who, None), number='', tag=f'pktn{who}s', workers=1, cam=cam)
    hy = max(h[1] for h in fr2[0][2])
    u8s, ms = make_sheet(fr2, [GROUND - hy], extra=glow_fn(GLOW[who]))
    ms['anchor'] = meta['anchor']
    if out:
        preview_png(u8s, os.path.join(out, f'tn_{who}_stand.png'), bg=(20, 28, 70))
    bid2 = save_webp(u8s, quality=90)
    record('tanabata', f'{who}_stand', bid2, ms)
    print(f'{who}_stand', bid2, ms, flush=True)


if __name__ == '__main__':
    for who in (sys.argv[1:] or ['o', 'h']):
        build(who, os.environ.get('OUT'))
