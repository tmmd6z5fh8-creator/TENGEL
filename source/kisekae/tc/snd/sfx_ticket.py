# 壁紙チケット（当たり：はじめは 1/2400・第4.142版から 1/600）の 演出の 音（11/09 08:56 まさちゃん「タップすると大きな扉が開くおとと、光りに包まれる音を出しながら画面が光りで真っ白になり」）
#   ぜんぶ 計算で 作る（録音は 使わない）
#   ・落ちる：ひゅーっ（風）→ ドンッ（重い 扉が 落ちる：低い ドン＋木と 石の 響き＋ほこり）
#   ・光：金色の きらきら（小さな 鈴の 和音が ゆっくり ゆれる）… タップまで
#   ・タップ → 大きな 扉が 開く 音（ギギギ…：木が こすれる＋重い ゴゴゴ）＋ 光に 包まれる 音（シャーンと 高まる 光の 和音・合唱の ような ひびき）
#   ・真っ白 → 晴れる：明るい 和音の 鐘 → チケット 1まいごとに シュッ＋キラーン → GET：短い ファンファーレ
#   python3 sfx_ticket.py <出す wav> <秒> <フィールド> <NAME.events.json>   （ticket.html の できごと）
import json, math, os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
from sfx_roulette import modes, burst, mix, put
from sfx_pop import bell, piron_snd
from sfx_care import env, glide, noise, chime, paper_snd
SR = amb.SR


def whoosh_down(rng, dur=0.55):                     # ひゅーっ（落ちる）
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    x = np.zeros(n); seg = 2048
    for i in range(0, n, seg):                      # だんだん 低く（帯を 動かす）
        m = min(seg, n - i); f = 2600 - 2100 * (i / n)
        x[i:i + m] = amb.bp(noise(m + 512, rng), max(200, f * 0.5), f, 2)[512:512 + m]
    return x * (u ** 1.6) * np.minimum(1, (1 - u) / 0.05 + 0.2)


def land_snd(rng):                                  # ドン！！（重い 扉：10:52 まさちゃん「落ちてきた時にドン！！と重低音をつけて！」）
    n = int(2.2 * SR); t = np.arange(n) / SR
    f = 38 + 34 * np.exp(-t / 0.09)                  # 重低音（はじめ 72Hz → 38Hz へ 下がる）
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.75) * np.minimum(1, t / 0.003)
    harm = (0.55 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(3 * f) / SR)) * np.exp(-t / 0.32)      # スマホでも 聞こえる 倍音
    boom = mix(sub * 1.2 + harm, modes([62, 104, 170], [0.6, 0.35, 0.2], [0.42, 0.22, 0.12], 1.2, att=0.002))
    knock = modes([240, 520, 910], [0.55, 0.3, 0.14], [0.09, 0.05, 0.03], 0.5)
    crack = 0.5 * amb.lp(noise(int(0.08 * SR), rng), 2500) * np.exp(-np.arange(int(0.08 * SR)) / SR / 0.012)
    dust = 0.45 * amb.lp(noise(int(1.6 * SR), rng), 700) * env(int(1.6 * SR), 0.02, 0.55)      # ざざー（土ぼこり）
    return mix(boom, knock, crack, dust)


def shimmer(rng, dur, base=1568.0):                 # 金色の きらきら（タップまで ゆっくり）
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, f in enumerate((base, base * 1.25, base * 1.5, base * 2.0, base * 2.5)):
        y += np.sin(2 * np.pi * f * t + k) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.21 + 0.07 * k) * t + k * 1.7)) * (1 / (1 + k * 0.4))
    for i in range(int(dur * 2.2)):                 # ときどき 小さな 鈴
        at = rng.random() * max(0.1, dur - 0.6); f = base * rng.choice([1, 1.25, 1.5, 2, 2.5, 3])
        put(y, 0.6 * bell(f, 0.25, 0.8), at)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.25 + 0.0)
    return y * np.clip(e, 0, 1) * 0.35


def creak_snd(rng, dur=1.35):                       # ギギギ…（大きな 木の 扉が ゆっくり 開く）
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    tt = 0.0
    while tt < dur:                                  # こすれる 小さな パルス（だんだん 速く → ゆっくり）
        u = tt / dur; rate = 22 + 38 * math.sin(math.pi * min(1, u * 1.2)); i = int(tt * SR)
        if i < n: x[i] += (0.6 + 0.4 * rng.random()) * math.sin(math.pi * min(1, u * 1.4)) ** 0.7
        tt += (1 / rate) * (0.85 + 0.3 * rng.random())
    body = amb.bp(x, 150, 260, 2) * 1.6 + amb.bp(x, 340, 520, 2) * 1.0 + amb.bp(x, 760, 1100, 2) * 0.5
    rumble = amb.lp(noise(n, rng), 110, 2) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.8 * 1.4
    return body + rumble


def swell_snd(rng, dur):                            # シャーン（光に 包まれる：高まる 光の 和音と 合唱の ような ひびき）
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    y = np.zeros(n)
    for k, f in enumerate((261.6, 329.6, 392.0, 523.3, 659.3, 784.0)):        # ド ミ ソ ド ミ ソ（少し ずつ 上がる）
        ff = f * (1 + 0.012 * u) * (1 + 0.003 * np.sin(2 * np.pi * (4.5 + 0.3 * k) * t))
        saw = 2 * ((np.cumsum(ff) / SR) % 1) - 1
        y += saw * (0.9 - 0.08 * k)
    voice = amb.bp(y, 500, 1400, 2) * 0.5 + amb.bp(y, 2200, 3400, 2) * 0.25          # 合唱の ような「アー」
    air = amb.hp(noise(n, rng), 3500) * 0.5                                           # 光の さらさら
    e = u ** 2.2
    return (voice + air) * e


def chord_bells(fs, gap=0.0, tau=0.9, dur=2.2):
    out = np.zeros(int((dur + gap * len(fs)) * SR))
    for k, f in enumerate(fs): put(out, chime(f, tau, dur), gap * k)
    return out


def fanfare():                                      # GET！：ド ミ ソ ド ー（明るく 短く）
    out = np.zeros(int(1.8 * SR))
    for k, (f, d) in enumerate(((523.3, 0.12), (659.3, 0.12), (784.0, 0.12), (1046.5, 0.9))):
        n = int(d * SR); t = np.arange(n) / SR
        tone = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)) * env(n, 0.006, d * (0.5 if k < 3 else 0.6))
        put(out, tone, 0.11 * k)
    put(out, 0.5 * bell(2093.0, 0.4, 1.2), 0.33)
    return out


def render(T, evs, seed=21):
    rng = np.random.default_rng(seed); buf = np.zeros((2, int(T * SR) + 4 * SR))
    def add(x, g, t, pan=0.0, dist=0.1, wet=0.2):
        if t < T: amb.add(buf, amb.place(x, pan, g, dist, wet0=wet), max(0, t))
    land = {}
    for e in evs:
        if e['k'] == 'land': land[len(land)] = e['t']
    taps = [e['t'] for e in evs if e['k'] == 'tap']
    for e in evs:
        k, t = e['k'], e['t']
        if k == 'dim': add(amb.lp(noise(int(0.8 * SR), rng), 300) * env(int(0.8 * SR), 0.4, 0.3), 0.04, t)
        elif k == 'fall': add(whoosh_down(rng), 0.09, t)
        elif k == 'land':
            add(land_snd(rng), 0.3, t, wet=0.22)
            nt = min([x for x in taps if x > t], default=t + 3)                 # タップまで きらきら
            add(shimmer(rng, max(0.5, nt - t - 0.1)), 0.06, t + 0.15, wet=0.3)
        elif k == 'tapshow': add(chime(1568, 0.2, 0.6), 0.05, t)
        elif k == 'tap': add(mix(modes([300, 700], [1.0, 0.3], [0.04, 0.02], 0.2), 0.3 * burst(0.03, 800, 4000, 0.006, rng)), 0.13, t)
        elif k == 'open': add(creak_snd(rng), 0.13, t + 0.05, wet=0.3); add(swell_snd(rng, 1.3), 0.12, t, wet=0.35)
        elif k == 'white': add(chord_bells((1046.5, 1318.5, 1568.0, 2093.0), 0.0, 0.7, 2.0), 0.1, t, wet=0.35); add(amb.hp(noise(int(1.2 * SR), rng), 3000) * env(int(1.2 * SR), 0.01, 0.35), 0.05, t)
        elif k == 'reveal': add(chord_bells((523.3, 659.3, 784.0, 1046.5), 0.09, 0.9, 2.2), 0.13, t + 0.1, wet=0.3)
        elif k == 'ticket': add(paper_snd(rng, 0.28, 1.1), 0.1, t); add(mix(glide(1400, 2400, 0.25, 0.6) * env(int(0.25 * SR), 0.005, 0.1), np.concatenate([np.zeros(int(0.12 * SR)), bell(2637.0, 0.35, 0.9)])), 0.1, t + 0.5)
        elif k == 'get': add(fanfare(), 0.24, t, wet=0.22)
    return buf[:, :int(T * SR)]


if __name__ == '__main__':
    OUT, T, TOD, EV = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
    evs = json.load(open(EV))
    if isinstance(evs, dict): evs = evs.get('events', [])
    base = amb.scene(T, TOD, 105)[:, :int(T * SR)].copy() * 0.6
    fx = render(T, evs)
    fx = 0.5 * np.tanh(fx / 0.5)                        # やわらかく 頭を おさえる（ドン！！は 大きく・ほかの 音は そのまま）
    buf = base + fx
    pk = float(np.abs(buf).max()); print(OUT, 'できごと', len(evs), 'peak', round(pk, 3), round(20 * math.log10(max(pk, 1e-6)), 1), 'dB')
    if pk > .95: buf *= .95 / pk
    wavfile.write(OUT, SR, (buf.T * 32767).astype(np.int16))
