# トレーニングセンターの 環境音（朝：小鳥・夕方：遠くの 鳥と 少しの 虫・夜：鈴虫と コオロギ）を 作る（ぜんぶ 計算で 作る＝録音は 使わない）
#   ・風（やさしい 風・葉の さらさら）は くり返せる 下地（ループ）
#   ・鳥と 虫は 1回ずつの 音（アプリが ばらばらに 鳴らす：場所・大きさ・高さを かえて）
#   python3 amb.py preview <出す wav> [秒]   … 見本（朝→夕方→夜）
import json, os, sys
import numpy as np
from scipy import signal
SR = 44100
TAU = 2 * np.pi


def lp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'low'); return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high'); return signal.lfilter(b, a, x)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), f2 / (SR / 2)], 'band'); return signal.lfilter(b, a, x)


def env_ar(n, att, rel):
    """なめらかな 立ち上がりと 消え方（hann の 半分ずつ）"""
    e = np.ones(n)
    a = max(1, int(att * SR)); r = max(1, int(rel * SR))
    a = min(a, n // 2); r = min(r, n - a)
    e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    e[n - r:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return e


def tone(f, amp, harm=(1.0, 0.12, 0.05)):
    """周波数の 線 f（Hz・1サンプルごと）と 大きさ amp の 音（倍音 少し）"""
    ph = TAU * np.cumsum(f) / SR
    y = np.zeros_like(f)
    for k, h in enumerate(harm, 1):
        if h:
            y += h * np.sin(k * ph) * (f * k < SR * 0.45)
    return y * amp


# ---------------- 鳥 ----------------
def chirp_note(dur, f0, f1, f2, rng):
    """1つの 音：f0 → f1（30%）→ f2（へ の 字）"""
    n = int(dur * SR); t = np.linspace(0, 1, n)
    f = np.where(t < .3, f0 + (f1 - f0) * np.sin(np.pi / 2 * t / .3), f1 + (f2 - f1) * (1 - np.cos(np.pi / 2 * (t - .3) / .7)))
    f = f * (1 + 0.006 * np.sin(TAU * 38 * t * dur + rng.uniform(0, 6)))
    return tone(f, env_ar(n, .03, dur * .7), (1.0, .04, 0))


def bird_chip(rng, ps=1.0):      # チュン チュン（スズメの ような）
    out = []
    for i in range(rng.integers(2, 6)):
        d = rng.uniform(.045, .07); p = ps * rng.uniform(.96, 1.04)
        out += [chirp_note(d * 1.25, 4500 * p, 4950 * p, 4000 * p, rng), np.zeros(int(rng.uniform(.11, .19) * SR))]
    return np.concatenate(out)


def bird_tsupi(rng, ps=1.0):     # ツツピー（シジュウカラの ような）
    out = []
    for r in range(rng.integers(2, 4)):
        out += [chirp_note(.045, 6300 * ps, 6100 * ps, 5700 * ps, rng), np.zeros(int(.04 * SR)),
                chirp_note(.04, 6100 * ps, 6000 * ps, 5600 * ps, rng), np.zeros(int(.04 * SR)),
                chirp_note(.15, 3700 * ps, 3650 * ps, 3450 * ps, rng), np.zeros(int(rng.uniform(.13, .18) * SR))]
    return np.concatenate(out)


def bird_warble(rng, ps=1.0):    # ちょこちょこ さえずる（メジロの ような）
    dur = rng.uniform(.7, 1.25); n = int(dur * SR); t = np.arange(n) / SR
    walk = np.cumsum(rng.normal(0, 1, n)); walk = lp(walk - walk.mean(), 6, 1); walk = walk / (np.abs(walk).max() + 1e-9)
    f = ps * (4300 + 350 * walk + 300 * np.sin(TAU * rng.uniform(5, 7) * t + rng.uniform(0, 6)))
    gate = 0.5 + 0.5 * np.tanh(2 * np.sin(TAU * rng.uniform(6, 8) * t + rng.uniform(0, 6)))   # 小さな 切れ目（やわらかく）
    return tone(f, env_ar(n, .04, .18) * (.45 + .55 * gate), (1.0, .04, 0))


def bird_whistle(rng, ps=1.0):   # ピーヨ（遠くの 口笛の ような 鳥）
    a = chirp_note(.22, 3300 * ps, 3250 * ps, 2950 * ps, rng)
    b = chirp_note(.26, 2650 * ps, 2750 * ps, 2850 * ps, rng)
    return np.concatenate([a, np.zeros(int(.1 * SR)), b])


BIRDS = [(bird_chip, .35), (bird_tsupi, .25), (bird_warble, .25), (bird_whistle, .15)]


# ---------------- 虫 ----------------
def suzumushi(rng, f0):          # 鈴虫「リーン」：4〜6この パルスが つながった 鳴る 音
    out = []; npl = rng.integers(4, 7)
    for i in range(npl):
        d = rng.uniform(.045, .06); n = int(d * SR); t = np.linspace(0, 1, n)
        f = f0 * (1 - .012 * i / npl) * (1 + .002 * np.sin(TAU * 3 * t))
        a = np.sin(np.pi * t) ** .8 * (0.6 + 0.4 * np.sin(np.pi * (i + .5) / npl))
        out += [tone(f, a, (1.0, .03, 0)), np.zeros(int(.004 * SR))]
    return np.concatenate(out)


def korogi(rng, f0):             # コオロギ「コロコロ リー」：パルスの トリル → 長い リー
    out = []; rate = rng.uniform(22, 28); npl = int(rng.uniform(.45, .9) * rate)
    for i in range(npl):
        d = .6 / rate; n = int(d * SR); t = np.linspace(0, 1, n)
        out += [tone(np.full(n, f0 * (1 + .01 * np.sin(i))), np.sin(np.pi * t) ** 1.5 * .8, (1.0, .04, 0)), np.zeros(int(.4 / rate * SR))]
    n = int(rng.uniform(.25, .4) * SR); t = np.linspace(0, 1, n)
    out.append(tone(np.full(n, f0 * .99), env_ar(n, .02, .1) * (.75 + .25 * np.sin(TAU * 45 * t * n / SR)), (1.0, .04, 0)))
    return np.concatenate(out)


# ---------------- 下地（風・葉・遠くの 虫の 声）：くり返せる ----------------
def bed(T, tod, seed):
    rng = np.random.default_rng(seed); X = 4.0
    N = int((T + X) * SR); t = np.arange(N) / SR
    fc = {'morning': 700, 'evening': 600, 'night': 420}[tod]
    lvl = {'morning': .034, 'evening': .04, 'night': .022}[tod]
    out = np.zeros((2, N))
    for ch in range(2):
        w = rng.normal(0, 1, N)
        wind = lp(hp(w, 60), fc, 2)
        wind /= np.sqrt(np.mean(wind ** 2)) + 1e-9
        ph = rng.uniform(0, TAU, 4)
        g = .58 + .22 * np.sin(TAU * t * 2 / T + ph[0]) + .12 * np.sin(TAU * t * 4 / T + ph[1]) + .06 * np.sin(TAU * t * 9 / T + ph[2])
        rus = bp(rng.normal(0, 1, N), 1800, 6000, 2)
        grain = lp(np.abs(rng.normal(0, 1, N)), 25, 1); grain /= grain.mean()
        rus = rus / (np.sqrt(np.mean(rus ** 2)) + 1e-9) * np.clip(g - .5, 0, None) * grain
        out[ch] = lvl * g * wind + lvl * .22 * rus
    if tod == 'evening':      # 遠くの 虫の 声（小さく）。夜は 虫なし（11/08 09:22 まさちゃん「夜は虫の鳴き声いらない」）
        nins = 4
        lvl_i = .0025
        for i in range(nins):
            f0 = rng.uniform(3900, 5200); rate = rng.uniform(18, 40); duty = rng.uniform(.35, .6)
            ph0 = rng.uniform(0, 1)
            pulse = (np.mod(t * rate + ph0, 1.0) < duty).astype(float)
            pulse = lp(pulse, 120, 1)
            song = .5 + .5 * np.sin(TAU * t * rng.integers(3, 9) / T + rng.uniform(0, TAU))     # 鳴いたり やんだり
            s = np.sin(TAU * f0 * t + rng.uniform(0, TAU)) * pulse * np.clip(song * 1.4 - .2, 0, 1)
            s = lp(s, 4500, 1)
            pan = rng.uniform(-.8, .8)
            out[0] += lvl_i * s * np.sqrt((1 - pan) / 2); out[1] += lvl_i * s * np.sqrt((1 + pan) / 2)
    # はじめと おわりを 重ねて くり返せる ように
    n = int(T * SR); x = int(X * SR)
    fade = np.sin(np.linspace(0, np.pi / 2, x)) ** 2
    loop = out[:, :n].copy()
    loop[:, :x] = out[:, :x] * fade + out[:, n:n + x] * (1 - fade)
    return loop


# ---------------- 場所に おく（左右・遠さ・ひびき） ----------------
def reverb_ir(rt=.7, seed=1):
    rng = np.random.default_rng(seed); n = int(rt * SR)
    ir = rng.normal(0, 1, n) * np.exp(-6.9 * np.arange(n) / n)
    ir = lp(ir, 3500, 1); ir[0] = 0
    return ir / np.sqrt(np.sum(ir ** 2))


IR = reverb_ir()


def place(x, pan, gain, dist, wet0=.18):
    """モノの 音 x を 左右 pan（−1〜1）・大きさ gain・遠さ dist（0〜1：遠いほど こもって ひびく）"""
    y = lp(x, 9000 - 5200 * dist, 2) if dist > .05 else x
    wet = signal.fftconvolve(y, IR)[:len(y) + len(IR) // 2] * (wet0 + .3 * dist)
    yy = np.zeros(len(wet)); yy[:len(y)] += y * (1 - .35 * dist); yy += wet
    yy *= gain
    return np.stack([yy * np.sqrt((1 - pan) / 2), yy * np.sqrt((1 + pan) / 2)])


def add(buf, x, at):
    i = int(at * SR)
    if i >= buf.shape[1]: return
    m = min(x.shape[1], buf.shape[1] - i); buf[:, i:i + m] += x[:, :m]


# ---------------- 鳴らし方（アプリと 同じ：ばらばらに） ----------------
def events(T, tod, rng):
    """鳥・虫は それぞれ 自分の 場所に いて、ときどき 鳴く（同じ 鳥は 同じ 場所・同じ 高さ）"""
    ev = []
    if tod in ('morning', 'evening'):
        sps = list(range(len(BIRDS))) if tod == 'morning' else list(rng.choice(len(BIRDS), 2, replace=False))
        for sp in sps:
            ps = rng.uniform(.93, 1.07) * .8; pan = rng.uniform(-.8, .8)           # 低く（やさしい 音：11/08 09:25・09:27 まさちゃん「少し優しく」「もう少し優しく」）
            dist = rng.uniform(.3, .7) if tod == 'morning' else rng.uniform(.6, .95)
            gain = (.13 if tod == 'morning' else .085) * (1 - .5 * dist) * (.4 if sp == 2 else 1.0)
            t = rng.uniform(0, 4) if tod == 'morning' else rng.uniform(0, 6)
            gap = 6.5 if tod == 'morning' else 9.0
            while t < T:
                for r in range(int(rng.integers(1, 4))):         # 同じ 鳥が 1〜3回 くり返す
                    ev.append(('bird', t, sp, ps * rng.uniform(.985, 1.015), pan, gain * rng.uniform(.85, 1.1), dist, int(rng.integers(1 << 30))))
                    t += rng.uniform(1.1, 2.2)
                t += 1.5 + rng.exponential(gap)
    if tod == 'evening':
        # 鈴虫（夕方に 遠くで 1匹）（同じ 場所・同じ 高さで しばらく 鳴いて 休む）
        nins = 1
        for k in range(nins):
            f0 = rng.uniform(4100, 4650); pan = rng.uniform(-.75, .75); dist = rng.uniform(.25, .6) if tod == 'night' else .85
            gain = (.08 if tod == 'night' else .03) * (1 - .4 * dist)
            t = rng.uniform(0, 3)
            while t < T:
                run = rng.uniform(6, 16); t1 = t + run
                while t < min(t1, T):
                    ev.append(('suzu', t, f0, pan, gain, dist, int(rng.integers(1 << 30))))
                    t += rng.uniform(1.0, 1.5)
                t += rng.uniform(3, 8)
        if False:      # コオロギ（夜の 虫は なし）
            t = rng.uniform(2, 5)
            while t < T:
                ev.append(('koro', t, rng.uniform(4500, 5000), rng.uniform(-.8, .8), .05, rng.uniform(.3, .7), int(rng.integers(1 << 30))))
                t += rng.uniform(3.5, 9)
    return ev


def render_event(e):
    k = e[0]
    if k == 'bird':
        _, t, sp, ps, pan, gain, dist, sd = e
        x = lp(BIRDS[sp][0](np.random.default_rng(sd), ps), 5000, 2)
        return place(x, pan, gain, dist, wet0=.32)
    if k == 'suzu':
        _, t, f0, pan, gain, dist, sd = e
        return place(suzumushi(np.random.default_rng(sd), f0), pan, gain, dist)
    if k == 'koro':
        _, t, f0, pan, gain, dist, sd = e
        return place(korogi(np.random.default_rng(sd), f0), pan, gain, dist)


VOL = 10 ** (-11 / 20)         # 11/08 まさちゃん 09:22「ボリューム少しだけ下げて」・09:23「もう少しボリューム下げて」・09:24「もう少しだけ下げて」・09:25「もう少し下げて」：−11dB


def scene(T, tod, seed):
    rng = np.random.default_rng(seed)
    b = bed(30.0, tod, seed)
    reps = int(np.ceil(T / 30.0)) + 1
    buf = np.tile(b, reps)[:, :int(T * SR)].copy()
    for e in events(T, tod, rng):
        add(buf, render_event(e), e[1])
    return buf * VOL


if __name__ == '__main__':
    if sys.argv[1] == 'seq':        # python3 amb.py seq <出す wav> morning:40 night:14 evening:17 … 動画の じゅんに 合わせる
        sys.argv = [sys.argv[0], 'preview', sys.argv[2], *sys.argv[3:]]
        SEQ = [(a.split(':')[0], float(a.split(':')[1])) for a in sys.argv[3:]]
    else:
        SEQ = None
    if sys.argv[1] == 'preview' and SEQ:
        out = sys.argv[2]
        parts = [scene(sec, tod, 100 + i) for i, (tod, sec) in enumerate(SEQ)]
        x = int(.4 * SR)
        for i, p in enumerate(parts):
            if i > 0: p[:, :x] *= np.linspace(0, 1, x)
            if i < len(parts) - 1: p[:, -x:] *= np.linspace(1, 0, x)
        total = np.concatenate(parts, 1)
        from scipy.io import wavfile
        pk = np.abs(total).max()
        print('peak', pk, 'rms dB', 20 * np.log10(np.sqrt(np.mean(total ** 2)) + 1e-12))
        if pk > .95: total *= .95 / pk
        wavfile.write(out, SR, (total.T * 32767).astype(np.int16))
        print(out, total.shape[1] / SR)
    elif sys.argv[1] == 'preview':
        out = sys.argv[2]; seg = float(sys.argv[3]) if len(sys.argv) > 3 else 12
        parts = [scene(seg, tod, 100 + i) for i, tod in enumerate(('morning', 'evening', 'night'))]
        # つなぎ目は 0.4秒で 消えて 0.4秒で 出る（動画の 切りかわりに 合わせる）
        x = int(.4 * SR)
        for i, p in enumerate(parts):
            if i > 0: p[:, :x] *= np.linspace(0, 1, x)
            if i < len(parts) - 1: p[:, -x:] *= np.linspace(1, 0, x)
        total = np.concatenate(parts, 1)
        from scipy.io import wavfile
        pk = np.abs(total).max()
        print('peak', pk, 'rms dB', 20 * np.log10(np.sqrt(np.mean(total ** 2)) + 1e-12))
        if pk > .95: total *= .95 / pk
        wavfile.write(out, SR, (total.T * 32767).astype(np.int16))
        print(out, total.shape[1] / SR)
