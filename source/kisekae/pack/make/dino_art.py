"""恐竜時代の 壁紙（壁紙パック）の 馬：いままでの 壁紙と 同じ 馬（horse_flat）が 2頭 ならんで ギャロップ。
   第4.93版（まさちゃん「馬の脚がしっかり地面について走るようにして！ 馬からゼッケンを消して、立髪と尻尾をもっと長くして、原始人が馬の上に乗ってる演出にして！」）：
   - ゼッケン・鞍・番号は なし（はだかの 背中に 乗る）。頭の ひもは 草の なわ・はみの 輪は 骨の 色。
   - たてがみ（mane_len）と しっぽ（房の のび 1.6倍）を 長く・なびく。
   - 背中に 原始人（オリジナル：毛皮の 服・ぼさぼさの 髪・まるい 鼻・にっこり）。手前の 馬＝骨の こん棒を ふり上げる 原始人・おくの 馬＝石の やりを かかげる 原始人。
     コマごとに 馬の 背中に のせて 描く（体は 少し 前かがみ・ギャロップに 合わせて 上下に ゆれて、こん棒と やりを ふる）。手前の 手は 手綱（草の なわ）を にぎる。
   - ひづめ：地面に ついて いる ひづめを 地面の 線に そろえる（sheets.ground_dy）。地面に ついた ひづめが うしろへ 進む はやさ（spf：2倍の 画素／コマ）も 出す
     → ページは 地面を その はやさで 流し、おくの 馬は 1回りの 秒を かえて 同じ はやさに する（すべらない）。
   手前＝鹿毛（黒い たてがみ）・おく＝芦毛（灰色の たてがみ・少し 小さく）。
   python3 kisekae/pack/make/dino_art.py [near far]   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の dino.near・dino.far（コマの シート）"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import render, gallop_poses, gallop_stance, ground_dy, make_sheet, save_webp, record, preview_png, HOOF_ORDER  # noqa: E402
from cute_horse import path, stroke, circ, ell, smooth, unit, V, f2  # noqa: E402

BARE = dict(cloth='none', clothTrim='none', num='none', tack='#8A6A3E', ring='#EDE3C8')     # 布・番号は 描かない（鞍は 体の 色＝見えない）
NEAR = dict(body='#9A552C', shade='#6E3818', muzzle='#C9906A', mane='#231612', maneD='#120A08', hoof='#2E2420', eye='#1A100A',
            blush='#EE9070', bodyShade='#8A4A24', saddle='#9A552C', saddleFlap='#9A552C', **BARE)
FAR = dict(body='#E4E0D8', shade='#B3ABA0', muzzle='#F3F0EA', mane='#56504C', maneD='#36322F', hoof='#4A4440', eye='#1A1414',
           blush='#E8A898', bodyShade='#D2CBC1', saddle='#E4E0D8', saddleFlap='#E4E0D8', **BARE)
SPOT_NEAR = dict(pose='gallop', facing='right', box=(176, 112, 444, 300), azim=6, shadow=('#5A3A1A', 0.0), mane_len=1.75)
SPOT_FAR = dict(pose='gallop', facing='right', box=(262, 96, 486, 254), azim=6, shadow=('#5A3A1A', 0.0), mane_len=1.75)
N = 10
TAIL_K, TAIL_W = 1.5, 1.12          # しっぽの 長さ・太さ


def long_tail(poses):
    """ギャロップの コマの しっぽの 房を 長く 太く"""
    out = []
    for p in poses:
        q = dict(p)
        q['tail_tufts'] = [((a[0] * TAIL_K, a[1] * TAIL_K), (b[0] * TAIL_K, b[1] * TAIL_K), (c[0] * TAIL_K, c[1] * TAIL_K), wm * TAIL_W)
                           for a, b, c, wm in p['tail_tufts']]
        out.append(q)
    return out


# ---------------------------------------------------------------- 原始人（オリジナル）
SKIN = ('#F0BE90', '#D49668')
LOOK = dict(
    near=dict(hair=('#3E2618', '#2A180E'), fur=('#E2A658', '#B87A34'), spot='#6E3A18', weapon='club', beard=True),
    far=dict(hair=('#9A4422', '#6A2A12'), fur=('#C9A26A', '#9C7A46'), spot='#5E4424', weapon='spear', beard=False),
)


def rot(v, deg):
    a = math.radians(deg)
    return V(v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def limb(a, b, w0, w1, col):
    """太さの かわる 手足（a → b・はしは まるい）"""
    d = unit(b - a)
    n = V(-d[1], d[0])
    pts = [a + n * w0 / 2, b + n * w1 / 2, b - n * w1 / 2, a - n * w0 / 2]
    o = path(f'M{f2(pts[0][0])},{f2(pts[0][1])} L{f2(pts[1][0])},{f2(pts[1][1])} L{f2(pts[2][0])},{f2(pts[2][1])} L{f2(pts[3][0])},{f2(pts[3][1])} Z', col)
    return o + circ(a, w0 / 2, col) + circ(b, w1 / 2, col)


def bone(c, ang, L, w, col='#F4EBD4', edge='#B09A70'):
    """骨（両はしが こぶ 2つ）：まん中 c・向き ang・長さ L・太さ w"""
    u = rot(V(1, 0), ang)
    n = V(-u[1], u[0])
    a, b = c - u * L / 2, c + u * L / 2
    o = limb(a, b, w, w * 0.9, edge)
    for e, s_ in ((a, -1), (b, 1)):
        for k in (-1, 1):
            q = e + n * k * w * 0.62 + u * s_ * w * 0.12
            o += circ(q, w * 0.66, edge)
    o += limb(a + u * w * 0.1, b - u * w * 0.1, w * 0.74, w * 0.66, col)
    for e, s_ in ((a, -1), (b, 1)):
        for k in (-1, 1):
            q = e + n * k * w * 0.62 + u * s_ * w * 0.12
            o += circ(q, w * 0.5, col)
    o += stroke(f'M{f2((a + u * w * 0.8 - n * w * 0.12)[0])},{f2((a + u * w * 0.8 - n * w * 0.12)[1])} L{f2((b - u * w * 0.8 - n * w * 0.12)[0])},{f2((b - u * w * 0.8 - n * w * 0.12)[1])}', '#FFFFFF', w * 0.16)
    return o


def caveman(m, i, kind):
    """原始人を 馬の 背中に。front＝手前の 足・体・頭・手前の 手（馬の 上）／back＝おくの 手と 武器（馬の うしろに しく＝体と 頭の うしろ）。
       m：draw_horse の 目印（p1u・wx・cloth_top）・i：コマ（ギャロップに 合わせて 上下・こん棒と やりを ふる）"""
    p = m['p1u']
    shock = kind.endswith('_s')                                         # 第4.94版：ティラノに びっくり（両手を 上げて 口を あける）
    kind = kind[:-2] if shock else kind
    L = LOOK[kind]
    g = i / N
    wave = math.sin(2 * math.pi * g)
    wx, top = m['wx'], m['cloth_top']
    xs = wx(-0.40)
    ys = top(xs) + 0.005 * p
    xa, xb = wx(-0.16), wx(-0.60)
    slope = math.degrees(math.atan2(top(xa) - top(xb), xa - xb))
    lean = (2 + slope + 3.0 * wave) if shock else (20 + slope + 4.0 * wave)   # 前へ かがむ（度）・びっくりは のけぞる
    S = V(xs, ys)
    up = rot(V(0, -1), lean)
    fwd = rot(V(1, 0), lean)
    C = S + up * 0.36 * p                                                # 肩の まん中
    hr = 0.165 * p
    Hc = C + up * 0.20 * p + fwd * 0.06 * p                              # 頭の まん中
    sk, skd = SKIN
    fur, furd = L['fur']
    hair, haird = L['hair']
    front, back = [], []
    # ---- おくの 手（手綱を にぎる）：馬の うしろに しく（体に かくれる・手は き甲の 上）
    Hn = V(wx(-0.10), top(wx(-0.10)) - 0.06 * p)
    Cf = C + fwd * 0.05 * p
    En = (Cf + Hn) / 2 + up * -0.06 * p
    if shock:
        En = Cf + rot(up, 34 + 6 * wave) * 0.16 * p
        Hn = En + rot(up, 14 + 6 * wave) * 0.15 * p
    back.append(limb(Cf, En, 0.11 * p, 0.09 * p, skd))
    back.append(limb(En, Hn, 0.09 * p, 0.075 * p, skd))
    back.append(circ(Hn, 0.06 * p, skd))
    # ---- 手前の 足（馬の 横に そって 前へ・ひざから 下へ たれる）
    K = S + rot(V(0.25 * p, 0.10 * p), 4 * wave)
    F = K + V(-0.06 * p, 0.25 * p)
    front.append(limb(S + V(0, 0.01 * p), K, 0.17 * p, 0.13 * p, sk))
    front.append(limb(K, F, 0.12 * p, 0.095 * p, sk))
    front.append(path(smooth([F + V(-0.05 * p, -0.03 * p), F + V(0.12 * p, -0.015 * p), F + V(0.135 * p, 0.04 * p), F + V(-0.04 * p, 0.05 * p)]), sk))
    for k in range(3):                                                   # 足の ゆび
        q = F + V(0.10 * p + k * 0.012 * p, 0.0)
        front.append(stroke(f'M{f2(q[0])},{f2(q[1] - 0.012 * p)} l{f2(0.01 * p)},{f2(0.03 * p)}', skd, 0.01 * p))
    front.append(limb(F + V(-0.03 * p, -0.06 * p), F + V(0.06 * p, -0.07 * p), 0.05 * p, 0.05 * p, furd))       # 足首の 毛皮
    # ---- 体（まるい おなか・毛皮の 服）
    hb = S - fwd * 0.12 * p
    hf = S + fwd * 0.15 * p + up * 0.02 * p
    sb = C - fwd * 0.15 * p
    sf = C + fwd * 0.12 * p
    belly = (hf + sf) / 2 + fwd * 0.07 * p
    front.append(path(smooth([hb, sb, C + up * 0.04 * p, sf, belly, hf]), sk))
    hem = []
    n_ = 8
    for k in range(n_ + 1):
        t = k / n_
        q = hb * (1 - t) + (hf + fwd * 0.08 * p) * t - up * 0.05 * p
        hem.append(q - up * (0.0 if k % 2 else -0.05 * p) - up * 0.03 * p)
    furp = [sb + up * 0.02 * p + fwd * 0.08 * p, C + up * 0.035 * p + fwd * 0.04 * p, sf - up * 0.04 * p, belly + fwd * 0.012 * p] + hem[::-1] + [hb + up * 0.12 * p]
    front.append(path(smooth(furp, sharp=list(range(4, 4 + len(hem)))), fur))
    import random
    R = random.Random(7 if kind == 'near' else 11)
    for k in range(7):
        u_ = R.uniform(0.15, 0.85)
        v_ = R.uniform(0.25, 0.9)
        q = C * (1 - v_) + (hb * (1 - u_) + hf * u_) * v_ + up * 0.02 * p
        front.append(ell(q, 0.03 * p, 0.02 * p, R.uniform(0, 180), L['spot']))
    front.append(stroke(smooth([sb + fwd * 0.05 * p + up * 0.03 * p, (C + belly) / 2 + fwd * 0.03 * p], closed=False), furd, 0.035 * p))   # 片がけの ひも
    # ---- 頭（ぼさぼさの 髪・大きな 目・まるい 鼻・にっこり）
    front.append(limb(C, Hc - up * 0.10 * p, 0.10 * p, 0.10 * p, sk))
    nh = 13
    hair_pts = []
    for k in range(nh):
        a = 95 + 250 * k / (nh - 1)
        r = hr * (1.34 if k % 2 == 0 else 1.06) * (1.0 + 0.05 * math.sin(k * 1.7 + g * 6.28))
        hair_pts.append(Hc + rot(V(r, 0), a - lean * 0.3))
    front.append(path(smooth([Hc + rot(V(hr * 0.6, 0), 90)] + hair_pts + [Hc + rot(V(hr * 0.5, 0), -15)], sharp=list(range(1, nh + 1, 2))), haird))
    front.append(circ(Hc, hr, sk))
    front.append(ell(Hc + V(-0.07 * p, 0.0), 0.04 * p, 0.05 * p, 0, skd))                     # 耳
    front.append(ell(Hc + V(-0.07 * p, 0.0), 0.022 * p, 0.03 * p, 0, '#E8A07A'))
    fr_ = [Hc + rot(V(hr * 1.06, 0), a) for a in (-160, -138, -118, -98, -78, -58, -36)]
    front.append(path(smooth([Hc + rot(V(hr * 0.45, 0), -165)] + fr_ + [Hc + rot(V(hr * 0.55, 0), -30)] +
                             [Hc + rot(V(hr * 0.74, 0), a) for a in (-55, -80, -104, -130, -150)], sharp=[1, 3, 5, 7]), hair))
    for a in (-128, -100, -72):
        q0 = Hc + rot(V(hr * 1.02, 0), a)
        q1 = Hc + rot(V(hr * 1.4, 0), a - 10)
        front.append(path(smooth([q0 + rot(V(0.025 * p, 0), a + 90), q1, q0 - rot(V(0.025 * p, 0), a + 90)]), hair))
    ec = Hc + V(0.07 * p, -0.015 * p)
    if shock:                                                            # 目を まるく 見ひらく・まゆが 上がる
        front.append(ell(ec, 0.042 * p, 0.05 * p, 0, '#FFFFFF') + ell(ec, 0.042 * p, 0.05 * p, 0, 'none', f'stroke="#2A1A10" stroke-width="{f2(0.012 * p)}"')
                     + circ(ec + V(0.006 * p, 0.0), 0.016 * p, '#2A1A10'))
        front.append(stroke(smooth([ec + V(-0.055 * p, -0.085 * p), ec + V(0.0, -0.11 * p), ec + V(0.05 * p, -0.09 * p)], closed=False), haird, 0.026 * p))
    else:
        front.append(ell(ec, 0.03 * p, 0.036 * p, 0, '#2A1A10') + circ(ec + V(0.009 * p, -0.012 * p), 0.012 * p, '#FFFFFF'))
        front.append(stroke(smooth([ec + V(-0.05 * p, -0.05 * p), ec + V(0.0, -0.068 * p), ec + V(0.045 * p, -0.055 * p)], closed=False), haird, 0.026 * p))
    nz = Hc + V(0.165 * p, 0.035 * p)
    front.append(circ(nz, 0.045 * p, skd) + circ(nz + V(-0.006 * p, -0.008 * p), 0.034 * p, sk))
    front.append(circ(Hc + V(0.045 * p, 0.065 * p), 0.03 * p, '#F29A7A'))
    mo = Hc + V(0.10 * p, 0.095 * p)
    mouth = (lambda: [ell(mo + V(0.005 * p, 0.012 * p), 0.04 * p, 0.05 * p, 0, '#5A1A10'), ell(mo + V(0.008 * p, 0.035 * p), 0.026 * p, 0.018 * p, 0, '#E86A5A')]) if shock else \
        (lambda: [path(smooth([mo + V(-0.05 * p, -0.012 * p), mo + V(0.055 * p, -0.02 * p), mo + V(0.03 * p, 0.035 * p), mo + V(-0.02 * p, 0.03 * p)]), '#7A2A1A'),
                  path(smooth([mo + V(-0.01 * p, 0.012 * p), mo + V(0.03 * p, 0.008 * p), mo + V(0.015 * p, 0.03 * p)]), '#E86A5A')])
    front += mouth()
    if L['beard']:
        bd = [Hc + rot(V(hr * 0.98, 0), a) for a in (8, 34, 60, 86, 112, 132)]
        front.append(path(smooth([Hc + rot(V(hr * 0.78, 0), 2)] + bd + [Hc + rot(V(hr * 0.7, 0), 140)], sharp=[2, 4, 6]), hair))
        front += mouth()
    else:
        front.append(bone(Hc + rot(V(hr * 1.1, 0), -118), -24, 0.22 * p, 0.045 * p))           # 髪に 骨の 飾り
    # ---- 手前の 手（ふり上げた 武器）：頭の 横・うしろへ ふり上げて ギャロップに 合わせて ふる
    Sh = C - fwd * 0.03 * p + up * 0.01 * p
    if L['weapon'] == 'club':
        sw = 22 * wave
        En = Sh + rot(up, -78 + sw * 0.4) * 0.16 * p
        Hw = En + rot(up, -28 + sw) * 0.15 * p
        ang = lean - 90 - 38 + sw
        if shock:
            sw = 8 * wave
            En = Sh + rot(up, -30 + sw) * 0.16 * p
            Hw = En + rot(up, -12 + sw) * 0.16 * p
            ang = lean - 90 - 14 + sw
        front.append(bone(Hw + rot(V(1, 0), ang) * 0.20 * p, ang, 0.54 * p, 0.10 * p))
    else:
        sw = 7 * wave
        En = Sh + rot(up, -70 + sw * 0.4) * 0.16 * p
        Hw = En + rot(up, -12 + sw) * 0.15 * p
        ang = lean - 90 + 26 + sw
        if shock:
            En = Sh + rot(up, -26 + sw) * 0.16 * p
            Hw = En + rot(up, -8 + sw) * 0.16 * p
            ang = lean - 90 + 8 + sw
        u = rot(V(1, 0), ang)
        nrm = V(-u[1], u[0])
        a_, b_ = Hw - u * 0.26 * p, Hw + u * 0.50 * p
        front.append(limb(a_, b_, 0.045 * p, 0.038 * p, '#7A5430'))
        tip = [b_ + u * 0.17 * p, b_ + nrm * 0.06 * p - u * 0.015 * p, b_ - u * 0.03 * p, b_ - nrm * 0.06 * p - u * 0.015 * p]
        front.append(path(smooth(tip), '#6E6864') + path(smooth([b_ + u * 0.13 * p, b_ + nrm * 0.028 * p, b_ - nrm * 0.028 * p]), '#A49E98'))
        front.append(limb(b_ - u * 0.05 * p, b_ + u * 0.02 * p, 0.07 * p, 0.07 * p, '#C49A5E'))
    front.append(limb(Sh, En, 0.115 * p, 0.095 * p, sk))
    front.append(limb(En, Hw, 0.095 * p, 0.085 * p, sk))
    front.append(circ(Hw, 0.068 * p, sk))
    front.append(stroke(smooth([Hw + V(-0.04 * p, 0.0), Hw + V(0.0, 0.035 * p), Hw + V(0.04 * p, 0.01 * p)], closed=False), skd, 0.016 * p))
    return dict(front=front, back=back)


def acc_for(kind):
    def mk(i):
        def acc(m):
            return caveman(m, i, kind)
        return acc
    return mk


def spf(frames, stance):
    """地面に ついた ひづめが 1コマで うしろへ 進む 量（2倍の 画素）の 平均"""
    vals = []
    n = len(frames)
    for i in range(n):
        j = (i + 1) % n
        for k in stance[i]:
            if k in stance[j]:
                vals.append(frames[i][2][HOOF_ORDER.index(k)][0] - frames[j][2][HOOF_ORDER.index(k)][0])
    return sum(vals) / len(vals)


def build(name, out=None):
    base = name[:-2] if name.endswith('_s') else name
    pal, spot = (NEAR, SPOT_NEAR) if base == 'near' else (FAR, SPOT_FAR)
    poses = long_tail(gallop_poses(N))
    frames, cam = render(pal, spot, poses, acc=acc_for(name), number='', tag='pkdn2' + name, workers=2)
    st = gallop_stance(N)
    g = spot['box'][3] - 4
    dys = ground_dy(frames, st, g, lift=6.0)
    xs = [h[0] for fr in frames for h in fr[2]]
    sh = ('#4A2E12', (min(xs) + max(xs)) / 2, g + 4, (max(xs) - min(xs)) * 0.5, 6.4, 0.26)
    u8, meta = make_sheet(frames, dys, shadow=sh)
    meta['dy'] = [round(float(d), 2) for d in dys]
    meta['spf'] = round(spf(frames, st), 3)
    meta['ground'] = int(g - meta['at'][1])                              # シートの 中の 地面（ひづめの 点）の 高さ（2倍の 画素）
    if out:
        preview_png(u8, os.path.join(out, f'dino_{name}.png'), bg=(200, 170, 120))
    bid = save_webp(u8, quality=90)
    record('dino', name, bid, meta)
    print(name, bid, meta, flush=True)


if __name__ == '__main__':
    for nm in (sys.argv[1:] or ['near', 'far', 'near_s', 'far_s']):
        build(nm, os.environ.get('OUT'))
