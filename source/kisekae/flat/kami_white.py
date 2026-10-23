"""超神様的中の 動画：① と ② の 間の 白い 光（40コマ・1.33秒）。① の さいごの まっ白 1コマと ② の はじめの 白 4コマと あわせて 1.5秒
   まさちゃん「四枚目のシーンのあと、白い光に包まれるシーンは、1.5秒に伸ばして！」（四枚目＝① の さいごの 金の 爆発）
   白い 光の 中で、まん中が ほんのり 金色に 息を して、うすい 金の 光の すじが ゆっくり 回り、金の キラキラが ふわっと 光っては 消える（少しずつ 上へ）。
   はじめと おわりの 7コマで ① の さいごの 1まい・② の はじめの 1まいに そろえる。画面は ずっと 白に 近い 明るさ（点めつに ならない）
   python3 flat/kami_white.py <① の さいごの 1まい> <② の はじめの 1まい> <出力フォルダ> → w001.png … w040.png（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2

W, H = 1170, 2532
NW, FPS = 40, 30
C = (580.0, 1180.0)                    # 光の まん中（超神様の 動画の はじめの 光と 同じ 所）
GOLD = np.float32((1.0, .84, .5))      # うすい 金（RGB）
SPK = np.float32((1.0, .74, .26))      # キラキラの 金


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


def sparkle_list():
    rng = random.Random(4400)
    out = []
    for _ in range(46):
        out.append(dict(t0=rng.uniform(-.2, NW / FPS - .3), life=rng.uniform(.45, .9), x=rng.uniform(40, W - 40), y=rng.uniform(150, H - 150),
                        s=rng.uniform(.6, 1.4), vy=-rng.uniform(20, 60), rot=rng.uniform(0, math.pi / 4)))
    return out


SP = sparkle_list()


def frame(a, b, k):
    """a・b：① の さいご・② の はじめ（RGB 0〜1）。k：0〜NW-1"""
    t = k / FPS
    u = (k + 1) / (NW + 1)
    img = a * (1 - u) + b * u
    env = sstep(0, 7, k) * (1 - sstep(NW - 8, NW - 1, k))
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
    # キラキラ（十字の 光・ふわっと 光って 消える・少しずつ 上へ）
    m = np.zeros((H, W), np.float32)
    for p in SP:
        age = t - p['t0']
        if not 0 <= age <= p['life']:
            continue
        e = math.sin(math.pi * age / p['life']) ** 2 * env
        x, y = p['x'], p['y'] + p['vy'] * age
        L = 34 * p['s'] * (.6 + .4 * e)
        for th in (p['rot'], p['rot'] + math.pi / 2):
            dx, dy = L * math.cos(th), L * math.sin(th)
            cv2.line(m, (int((x - dx) * 8), int((y - dy) * 8)), (int((x + dx) * 8), int((y + dy) * 8)), float(e * .8), 2, cv2.LINE_AA, shift=3)
        cv2.circle(m, (int(x * 8), int(y * 8)), int(5 * p['s'] * 8), float(e), -1, cv2.LINE_AA, shift=3)
    m = np.clip(cv2.GaussianBlur(m, (0, 0), 1.2) * 1.4 + cv2.GaussianBlur(m, (0, 0), 6) * .9, 0, 1)[..., None] * .6
    img = img * (1 - m) + SPK * m
    return np.clip(img, 0, 1)


def main(pa, pb, out):
    os.makedirs(out, exist_ok=True)
    a = cv2.cvtColor(cv2.imread(pa), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    b = cv2.cvtColor(cv2.imread(pb), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    assert a.shape[:2] == (H, W) and b.shape[:2] == (H, W)
    for k in range(NW):
        im = (frame(a, b, k) * 255 + .5).astype(np.uint8)
        cv2.imwrite(os.path.join(out, f'w{k + 1:03d}.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
    print('w', NW)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
