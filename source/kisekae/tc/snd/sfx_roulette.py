# ルーレットの 効果音（11/09 00:24 まさちゃん「レバーの音・ルーレットの音・ポイント確定の音 つけられる？」）
#   ぜんぶ 計算で 作る（録音は 使わない）・やさしい 紙と 木の 音（トレーニングセンター＝見ているだけで 落ち着ける 場所）
#   ・レバー：カ（叩く）→ コン（たおれ きる）→ ぼよん（ばねで もどる：レバーの ゆれと 同じ 2.2回／秒）
#   ・ルーレット：盤の ひだ（1回転 16まい）が 針の 下を 通る たびに カチッ（速い ときは カラカラ → だんだん カチ…カチ…）
#                ＋ 回って いる 間 だけ 小さな 風の 音・止まった ときに コトッ
#   ・ポイント確定：札が 出る ときに ポン ＋ きらりん（ソ・ド・ミ・ソ・ド）＋ 小さな きらきら
#   python3 sfx_roulette.py <出す wav> <秒> <a,b,win,t0> [<a,b,win,t0> …]   … roulette.html と 同じ 時間で 鳴らす（下に 朝の 環境音 −11dB）
#   python3 sfx_roulette.py parts <フォルダ>                                    … 1つずつの 音（アプリ 用：lever・tick・stop・confirm）
import math, os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
SR = amb.SR
# roulette.html と 同じ 時間（1回 ぶん：u＝始まって から の 秒）
HIT, S0 = 3.4, 3.45          # 見本で タップする 時（11/09 01:23：手を なくして「タップ」を 長めに 見せる）
S1 = S0 + 3.5
A0 = -0.5
G_LEVER, G_TICK, G_STOP, G_CONF, G_WIND = 0.26, 0.145, 0.14, 0.34, 0.045        # 山の 大きさ：レバー 0.3・カチッ 0.14・確定 0.3（環境音の 山 0.06）


def jshash(n):        # roulette.html の hash() と 同じ
    s = math.sin(n * 127.1 + 311.7) * 43758.5453
    return s - math.floor(s)


def modes(freqs, amps, taus, dur, att=0.0015):
    """減っていく 正弦波の 重ね（木・紙を 叩いた ときの 響き）。立ち上がりは やわらかく"""
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, tau in zip(freqs, amps, taus):
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau)
    k = max(1, int(att * SR)); y[:k] *= np.linspace(0, 1, k)
    return y


def burst(dur, f1, f2, tau, rng):
    n = int(dur * SR); t = np.arange(n) / SR
    return amb.bp(rng.normal(0, 1, n), f1, f2, 2) * np.exp(-t / tau)


def mix(*xs):
    """長さの ちがう 音を 頭を そろえて 足す"""
    n = max(len(x) for x in xs); y = np.zeros(n)
    for x in xs: y[:len(x)] += x
    return y


def put(out, x, at):
    i = int(at * SR)
    if i >= len(out): return
    m = min(len(x), len(out) - i); out[i:i + m] += x[:m]


def lever_snd(rng):
    out = np.zeros(int(1.0 * SR))
    k1 = mix(modes([640, 1380, 2520], [1.0, 0.5, 0.2], [0.03, 0.018, 0.01], 0.25), 0.3 * burst(0.03, 900, 4200, 0.004, rng))           # カ
    k2 = mix(modes([150, 420, 960], [1.0, 0.55, 0.25], [0.085, 0.04, 0.02], 0.45), 0.22 * burst(0.03, 350, 2200, 0.006, rng))         # コン
    n = int(0.65 * SR); t = np.arange(n) / SR
    f = 205 - 45 * t / 0.65
    boing = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.17) * (0.6 + 0.4 * np.cos(2 * np.pi * 2.2 * t))                 # ぼよん
    k = int(0.01 * SR); boing[:k] *= np.linspace(0, 1, k)
    put(out, 0.75 * k1, 0.0); put(out, k2, 0.09); put(out, 0.22 * boing, 0.12)
    return amb.lp(out, 6500, 2)


def tick_snd(rng, k=1.0):
    x = mix(modes([1500 * k, 2650 * k, 4150 * k], [1.0, 0.45, 0.15], [0.008, 0.005, 0.0028], 0.05, att=0.0005), 0.25 * burst(0.01, 1200, 5000, 0.0015, rng))
    return amb.lp(x, 6000, 2)


def stop_snd(rng):
    return amb.lp(mix(modes([190, 520, 1150], [1.0, 0.45, 0.15], [0.06, 0.03, 0.015], 0.3), 0.15 * burst(0.02, 300, 1800, 0.005, rng)), 4000, 2)


def bell(f, dur=1.7):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for m, a, tau in ((1.0, 1.0, 0.85), (2.0, 0.25, 0.42), (3.01, 0.08, 0.22), (4.17, 0.05, 0.12)):
        y += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / tau)
    k = int(0.004 * SR); y[:k] *= np.linspace(0, 1, k)
    return y


def confirm_snd(rng):
    out = np.zeros(int(2.6 * SR))
    n = int(0.2 * SR); t = np.arange(n) / SR
    pon = np.sin(2 * np.pi * np.cumsum(340 - 150 * t / 0.2) / SR) * np.exp(-t / 0.05)                  # ポン（札が 出る）
    k = int(0.003 * SR); pon[:k] *= np.linspace(0, 1, k)
    put(out, 0.55 * pon, 0.0)
    for i, f in enumerate((783.99, 1046.5, 1318.5, 1568.0, 2093.0)):                                    # きらりん（ソ・ド・ミ・ソ・ド）
        put(out, bell(f) * (0.36 if i < 4 else 0.26), 0.06 + 0.075 * i)
    for j in range(9):                                                                                 # 小さな きらきら
        f = rng.uniform(4300, 7000); put(out, modes([f], [1.0], [0.045], 0.15) * 0.045, 0.4 + rng.uniform(0, 0.8))
    return amb.lp(out, 9000, 2)


def wheel_angle(u, a, b, win):
    off = (jshash(a + b + win) - 0.5) * 0.9; fin = win * math.pi + off
    turns = 2 + (fin - A0) / (2 * math.pi)
    p = np.clip((u - S0) / (S1 - S0), 0, 1); e = 1 - (1 - p) ** 2.5
    return fin - turns * 2 * math.pi * (1 - e)


def run_sound(T, a, b, win, t0):
    """1回 ぶんの 効果音（ステレオ）"""
    rng = np.random.default_rng(int(a + b + win))
    buf = np.zeros((2, int(T * SR)))
    amb.add(buf, amb.place(lever_snd(rng), 0.35, G_LEVER, 0.08, wet0=.14), t0 + HIT)
    # カチッ：盤の ひだの さかい（π/8 ごと）が 上の 針（−π/2）を 通る とき
    u = np.arange(S0, S1 + 0.001, 0.0002); ang = wheel_angle(u, a, b, win)
    idx = np.floor((ang + math.pi / 2) / (math.pi / 8))
    hits = np.nonzero(np.diff(idx) != 0)[0]
    vel = np.gradient(ang, u); vmax = vel.max()
    for h in hits:
        v = vel[h] / vmax
        amp = G_TICK * (0.72 + 0.28 * (1 - v)) * rng.uniform(0.9, 1.05)
        amb.add(buf, amb.place(tick_snd(rng, rng.uniform(0.97, 1.03)), -0.12, amp, 0.05, wet0=.1), t0 + u[h])
    # 回って いる 間の 小さな 風
    n = int((S1 - S0) * SR); tt = np.arange(n) / SR
    vv = np.interp(tt + S0, u, vel) / vmax
    wind = amb.bp(rng.normal(0, 1, n), 260, 1300, 2) * vv ** 1.5 * amb.env_ar(n, 0.05, 0.4)
    amb.add(buf, amb.place(wind, -0.12, G_WIND, 0.1, wet0=.05), t0 + S0)
    amb.add(buf, amb.place(stop_snd(rng), -0.12, G_STOP, 0.08, wet0=.12), t0 + S1 + 0.02)
    amb.add(buf, amb.place(confirm_snd(rng), 0.0, G_CONF, 0.1, wet0=.2), t0 + S1 + 0.4)
    print('run', a, b, win, 'カチッ', len(hits), '回')
    return buf


def kick_snd(rng):
    """神様馬の「最後の一回転」が 始まる とき：きらん（高い 鈴 ソ・ド）＋ 小さな きらきら"""
    out = np.zeros(int(1.8 * SR))
    for i, f in enumerate((1567.98, 2093.0)):
        put(out, bell(f, 1.4) * (0.3 if i == 0 else 0.36), 0.07 * i)
    for j in range(6):
        f = rng.uniform(4500, 7000); put(out, modes([f], [1.0], [0.04], 0.12) * 0.04, 0.12 + rng.uniform(0, 0.5))
    return amb.lp(out, 9000, 2)


def events_sound(T, ev):
    """ページ（roulette2.html）が 出した できごと（レバー・カチッ・止まる・確定・最後の一回転）の 時間に 音を 置く"""
    rng = np.random.default_rng(11)
    buf = np.zeros((2, int(T * SR)))
    ticks = np.array(sorted(e['t'] for e in ev if e['k'] == 'tick'))
    # 回る 速さ（カチッの こさ）→ 速い ときは カチッを 少し 小さく・風の 音
    imp = np.zeros(int(T * SR)); ii = (ticks * SR).astype(int); ii = ii[ii < len(imp)]; np.add.at(imp, ii, 1.0)
    from scipy.ndimage import gaussian_filter1d
    rate = gaussian_filter1d(imp, 0.06 * SR) * SR                  # 1秒 あたりの カチッ
    rmax = max(float(rate.max()), 1e-6)
    for t in ticks:
        v = rate[min(int(t * SR), len(rate) - 1)] / rmax
        amp = G_TICK * (0.72 + 0.28 * (1 - v)) * rng.uniform(0.9, 1.05)
        amb.add(buf, amb.place(tick_snd(rng, rng.uniform(0.97, 1.03)), -0.12, amp, 0.05, wet0=.1), t)
    wind = amb.bp(rng.normal(0, 1, len(rate)), 260, 1300, 2) * (rate / rmax) ** 1.5
    buf += amb.place(wind, -0.12, G_WIND, 0.1, wet0=.05)[:, :buf.shape[1]]
    for e in ev:
        k, t = e['k'], e['t']
        if k == 'lever': amb.add(buf, amb.place(lever_snd(rng), 0.35, G_LEVER, 0.08, wet0=.14), t)
        elif k == 'stop': amb.add(buf, amb.place(stop_snd(rng), -0.12, G_STOP, 0.08, wet0=.12), t)
        elif k == 'confirm': amb.add(buf, amb.place(confirm_snd(rng), 0.0, G_CONF, 0.1, wet0=.2), t)
        elif k == 'kick': amb.add(buf, amb.place(kick_snd(rng), 0.0, G_CONF * 0.8, 0.1, wet0=.25), t)
    print('できごと', len(ev), 'カチッ', len(ticks))
    return buf


if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[3] == '--events':      # python3 sfx_roulette.py <出す wav> <秒> --events <xxx.events.json>
        import json
        OUT, T = sys.argv[1], float(sys.argv[2])
        buf = amb.scene(T, 'morning', 105)[:, :int(T * SR)].copy() + events_sound(T, json.load(open(sys.argv[4])))
        pk = float(np.abs(buf).max()); print('peak', round(pk, 3), round(20 * math.log10(pk), 1), 'dB')
        if pk > .95: buf *= .95 / pk
        wavfile.write(OUT, SR, (buf.T * 32767).astype(np.int16)); print(OUT, buf.shape[1] / SR)
        sys.exit()
    if sys.argv[1] == 'parts':
        D = sys.argv[2]; os.makedirs(D, exist_ok=True); rng = np.random.default_rng(7)
        for nm, x, g in (('lever', lever_snd(rng), G_LEVER), ('tick', tick_snd(rng), G_TICK), ('stop', stop_snd(rng), G_STOP), ('confirm', confirm_snd(rng), G_CONF)):
            y = amb.place(x, 0.0, g * 1.41, 0.08)
            wavfile.write(os.path.join(D, f'rt_{nm}.wav'), SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
            print(nm, 'peak', round(float(np.abs(y).max()), 3), round(len(x) / SR, 2), '秒')
        sys.exit()
    OUT, T = sys.argv[1], float(sys.argv[2])
    buf = amb.scene(T, 'morning', 105)[:, :int(T * SR)].copy()            # 朝の 環境音（−11dB：場内と 同じ）
    for spec in sys.argv[3:]:
        a, b, win, t0 = spec.split(','); buf += run_sound(T, float(a), float(b), int(win), float(t0))
    pk = float(np.abs(buf).max()); print('peak', round(pk, 3), round(20 * math.log10(pk), 1), 'dB')
    if pk > .95: buf *= .95 / pk
    wavfile.write(OUT, SR, (buf.T * 32767).astype(np.int16)); print(OUT, buf.shape[1] / SR)
