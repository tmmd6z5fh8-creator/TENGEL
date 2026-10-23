"""超神様的中の 動画：① と ② の 間の 白い 光（40コマ・1.33秒）。① の さいごの まっ白 1コマと ② の はじめの 白 4コマと あわせて 1.5秒
   まさちゃん「四枚目のシーンのあと、白い光に包まれるシーンは、1.5秒に伸ばして！」（四枚目＝① の さいごの 金の 爆発）
   白い 光の 中で、まん中が ほんのり 金色に 息を して、うすい 金の 光の すじが ゆっくり 回る。
   まさちゃん「三枚目のシーンは、キラキラの演出を金粉が舞ってる豪華な演出にして！」→ キラキラを 金粉に：こまかい 金の 粒（遠い ほど 小さい）・
   ひらひら 回る 金箔（向きが かわると キラッと 光る）・手前を ぼけた 大きな 金箔が とおる。ゆっくり 落ちながら ゆれて、まん中の まわりを 少し 回る
   はじめの 7コマで ① の さいごの 1まいに そろえる。画面は ずっと 白に 近い 明るさ（点めつに ならない）
   まさちゃん「この金粉のシーンから画面白くなるシーンいらない！ 金粉のシーンから次のシーンに入って！」→ 金粉は さいごまで 消さずに、
   ② の はじめの 8コマ（白 → ② の 絵）にも 金粉を かさねて（だんだん 消える）、白だけの 画面を はさまずに ② へ 入る（TAIL）
   python3 flat/kami_white.py <① の さいごの 1まい> <出力フォルダ> <② の 1コマめ> … <② の 8コマめ> → w001.png … w040.png・x001.png … x008.png（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2

W, H = 1170, 2532
NW, FPS = 40, 30
C = (580.0, 1180.0)                    # 光の まん中（超神様の 動画の はじめの 光と 同じ 所）
GOLD = np.float32((1.0, .84, .5))      # うすい 金（RGB）


def sstep(e0, e1, x):
    u = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return u * u * (3 - 2 * u)


_G = {}


def grid():
    if 'g' not in _G:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx, dy = xx - C[0], yy - C[1]
        _G['g'] = (np.hypot(dx, dy), np.arctan2(dy, dx))
    return _G['g']


GOLDS = (np.float32((.8, .56, .14)), np.float32((.9, .68, .2)), np.float32((.97, .79, .3)), np.float32((1.0, .88, .45)), np.float32((1.0, .95, .7)))   # 金の 色（向きで かわる：こい 金 → 明るい 金 → 光る）


def dust_list():
    """金粉：(種類, x, y, 大きさ, 落ちる 速さ, ゆれ（はば・速さ・位相）, 回る 角度・速さ, かたむき・速さ, こさ)。far＝こまかい 粒・mid＝粒・leaf＝金箔・fg＝手前の ぼけた 金箔"""
    rng = np.random.default_rng(4500)
    out = []
    for kind, n, s0, s1, a0, a1 in (('far', 1800, .9, 2.0, .5, .8), ('mid', 800, 2.0, 4.2, .65, .95), ('leaf', 160, 8.0, 22.0, .85, 1.0), ('fg', 14, 26.0, 46.0, .22, .32)):
        for _ in range(n):
            out.append(dict(kind=kind, x=rng.uniform(-60, W + 60), y=rng.uniform(-120, H + 60), s=rng.uniform(s0, s1),
                            vy=rng.uniform(18, 80) * (1.8 if kind == 'fg' else 1.0), sw=rng.uniform(5, 28), sf=rng.uniform(1.2, 3.5), sp=rng.uniform(0, 2 * math.pi),
                            rot=rng.uniform(0, math.pi), vr=rng.uniform(-5, 5), tl=rng.uniform(0, 2 * math.pi), vt=rng.uniform(3, 12),
                            a=rng.uniform(a0, a1), pts=rng.uniform(.6, 1.0, 5)))
    return out


DUST = dust_list()


def dust(img, t, env):
    """金粉を 重ねる（同じ 色の 粒を まとめて 描いて 色ごとに 重ねる）"""
    masks = [np.zeros((H, W), np.float32) for _ in GOLDS]
    glint = np.zeros((H, W), np.float32)
    fg = [np.zeros((H, W), np.float32) for _ in GOLDS]
    sw = .1 * t                                                      # まん中の まわりを 少し 回る
    cs, sn = math.cos(sw), math.sin(sw)
    for p in DUST:
        x = p['x'] + p['sw'] * math.sin(p['sf'] * t + p['sp'])
        y = p['y'] + p['vy'] * t
        dx, dy = x - C[0], y - C[1]
        x, y = C[0] + dx * cs - dy * sn, C[1] + dx * sn + dy * cs
        if not (-60 < x < W + 60 and -60 < y < H + 60):
            continue
        c = math.cos(p['tl'] + p['vt'] * t)                           # 向き（-1〜1）：表が こっちを 向くと 明るく
        ci = min(len(GOLDS) - 1, int((c * .5 + .5) * (len(GOLDS) - .01)))
        g = abs(c) ** 12                                             # キラッ
        a = p['a'] * env
        s = p['s']
        w = max(.6, s * (.22 + .78 * abs(c)))
        ang = math.degrees(p['rot'] + p['vr'] * t)
        if p['kind'] in ('far', 'mid'):
            cv2.ellipse(masks[ci], (int(x * 8), int(y * 8)), (int(s * 8), int(w * 8)), ang, 0, 360, float(a), -1, cv2.LINE_AA, shift=3)
        else:
            th = math.radians(ang)
            pts = []
            for j, rr in enumerate(p['pts']):
                q = 2 * math.pi * j / 5 + .3
                px, py = math.cos(q) * s * rr, math.sin(q) * w * rr
                pts.append((x + px * math.cos(th) - py * math.sin(th), y + px * math.sin(th) + py * math.cos(th)))
            if p['kind'] == 'fg':                                     # 手前の ぼけた 金（まるい 光）
                cv2.circle(fg[min(len(GOLDS) - 1, ci + 1)], (int(x * 8), int(y * 8)), int(s * 8), float(a), -1, cv2.LINE_AA, shift=3)
            else:
                cv2.fillPoly(masks[ci], [np.int32(np.array(pts) * 8)], float(a), cv2.LINE_AA, shift=3)
                if g > .35:                                         # 光る 時は ふちも 光る
                    cv2.polylines(glint, [np.int32(np.array(pts) * 8)], True, float(g * env * .8), 2, cv2.LINE_AA, shift=3)
        if p['kind'] in ('mid', 'leaf') and g > .35:                 # 光る 時の 十字の 光
            L = (s * 2.2 + 10) * g
            for q in (math.radians(ang), math.radians(ang + 90)):
                cv2.line(glint, (int((x - L * math.cos(q)) * 8), int((y - L * math.sin(q)) * 8)), (int((x + L * math.cos(q)) * 8), int((y + L * math.sin(q)) * 8)),
                         float(g * env), 2, cv2.LINE_AA, shift=3)
            cv2.circle(glint, (int(x * 8), int(y * 8)), int((s * .6 + 2) * 8), float(g * env), -1, cv2.LINE_AA, shift=3)
    for m, col in zip(masks, GOLDS):
        m = cv2.GaussianBlur(m, (0, 0), .7)[..., None]
        img = img * (1 - m) + col * m
    for m, col in zip(fg, GOLDS):                                    # 手前の ぼけた 金（まるい 光）
        m = cv2.GaussianBlur(m, (0, 0), 10)[..., None]
        img = img * (1 - m) + col * m
    g1 = cv2.GaussianBlur(glint, (0, 0), 1.0)
    g2 = cv2.GaussianBlur(glint, (0, 0), 6)
    ag = np.clip(g1 * 1.1 + g2 * .5, 0, .9)[..., None]                # 光る 金の 十字（白の 上でも 見える 金色）
    img = img * (1 - ag) + np.float32((1.0, .78, .26)) * ag
    ac = np.clip(cv2.GaussianBlur(glint, (0, 0), .6) * 1.4 - .35, 0, 1)[..., None]   # まん中は 白く 光る
    return img * (1 - ac) + np.float32((1.0, .99, .94)) * ac


TAIL = 8                               # ② の はじめの コマにも 金粉を かさねる 数（白だけの 画面を はさまない）


def frame(a, b, k):
    """a・b：① の さいご・② の はじめ（RGB 0〜1）。k：0〜NW-1"""
    t = k / FPS
    u = (k + 1) / (NW + 1)
    img = a * (1 - u) + b * u
    return np.clip(glitter(img, t, sstep(0, 7, k)), 0, 1)


def tail_frame(c, j):
    """② の j コマめ（0〜）に 金粉を かさねる（② の 絵が 出て くると だんだん 消える）"""
    env = 1 - sstep(2, TAIL - 1, j)
    if env <= 0:
        return c
    return np.clip(glitter(c, (NW + j) / FPS, env), 0, 1)


def glitter(img, t, env):
    """白い 光の 中の 金：まん中の ほんのり 金色・光の すじ・金粉（env：こさ）"""
    if env <= 0:
        return img
    rr, ang = grid()
    # まん中の ほんのり 金色（ゆっくり 息を する）＋光の すじ（まん中から 外へ・ゆっくり 回る）
    g = np.exp(-(rr / 950.0) ** 2) * (.13 + .03 * math.sin(2 * math.pi * t / 1.1)) + np.exp(-(rr / 260.0) ** 2) * .04
    w1 = np.cos(9 * ang + 1.2 * t) * .5 + .5
    w2 = np.cos(14 * ang - .8 * t + 1.3) * .5 + .5
    rays = (w1 ** 6 * .6 + w2 ** 8 * .4) * np.exp(-rr / 1700.0) * np.clip(rr / 160.0, 0, 1) * .1
    k_ = ((g + rays) * env)[..., None]
    img = img * (1 - k_) + GOLD * k_
    # 金粉（ひらひら 落ちながら キラッ）
    return dust(img, t, env)


def load(p):
    x = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    assert x.shape[:2] == (H, W), (p, x.shape)
    return x


def save(p, x):
    cv2.imwrite(p, cv2.cvtColor((np.clip(x, 0, 1) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))


def main(pa, out, pbs):
    os.makedirs(out, exist_ok=True)
    assert len(pbs) == TAIL, len(pbs)
    a = load(pa)
    bs = [load(p) for p in pbs]
    for k in range(NW):
        save(os.path.join(out, f'w{k + 1:03d}.png'), frame(a, bs[0], k))
    for j, c in enumerate(bs):
        save(os.path.join(out, f'x{j + 1:03d}.png'), tail_frame(c, j))
    print('w', NW, 'x', TAIL)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
