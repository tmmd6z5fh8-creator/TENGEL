# お世話（撫でる・呼ぶ・ごはん・おそうじ・説明書）の 効果音（11/09 まさちゃん「お世話のアイディア全部組み込んで！」）
#   ぜんぶ 計算で 作る（録音は 使わない）・やさしい 紙と 木の 音・馬の 息（トレーニングセンター＝見ているだけで 落ち着ける 場所）
#   tc_care.js の できごと（window.__events()：shot3d.py が NAME.events.json に 書く）に 合わせて 鳴らす
#   python3 sfx_care.py <出す wav> <秒> <morning|evening|night|abyss|divine> <NAME.events.json>   … 下に その 時間帯の 環境音（−11dB）・幻の馬／神様馬は BGM
#   python3 sfx_care.py parts <フォルダ>                                              … 1つずつの 音（アプリ 用）
import json, math, os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
from sfx_roulette import modes, burst, mix, put
from sfx_pop import piron_snd, bell
SR = amb.SR


def env(n, att, rel, hold=0.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(att, 1e-4)) * np.exp(-np.maximum(0, t - att - hold) / max(rel, 1e-4))
    return e


def glide(f0, f1, dur, shape=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    f = f0 + (f1 - f0) * u ** shape
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def noise(n, rng): return rng.normal(0, 1, n)


# ---------- 紙 ----------
def paper_snd(rng, dur=0.32, bright=1.0):          # ぱさっ（紙が ひらく）：ざらっと した 音 ＋ 小さな パリパリ
    n = int(dur * SR); x = amb.bp(noise(n, rng), 1200 * bright, 6500 * bright, 2) * env(n, 0.012, dur * 0.28)
    for k in range(5):                                # パリパリ
        at = int((0.02 + 0.045 * k + 0.01 * rng.random()) * SR); m = int(0.012 * SR)
        if at + m < n: x[at:at + m] += 1.6 * amb.hp(noise(m, rng), 3000) * np.exp(-np.arange(m) / (0.0025 * SR))
    return x * 0.5


def button_snd(rng):                                # ぽふ（紙の ボタン）
    return mix(modes([240, 520, 980], [1.0, 0.35, 0.12], [0.05, 0.025, 0.012], 0.25), 0.25 * burst(0.05, 600, 3000, 0.01, rng))


def rub_snd(rng):                                   # さわっ（紙の 手で なでる）
    n = int(0.42 * SR); t = np.arange(n) / SR
    x = amb.bp(noise(n, rng), 700, 3200, 2) * np.sin(np.pi * np.clip(t / 0.42, 0, 1)) ** 1.5
    return x * (0.8 + 0.2 * np.sin(2 * np.pi * 11 * t))


def pop_snd(f0=520, f1=820):                        # ぽわん（ハートが 出る）
    n = int(0.35 * SR); y = glide(f0, f1, 0.35, 0.5) * env(n, 0.004, 0.08)
    return y + 0.3 * bell(f1 * 2, 0.12, 0.35)[:n]


def chime(f, tau=0.35, dur=0.9):                    # ちりん
    return bell(f, tau, dur) + 0.35 * bell(f * 1.5, tau * 0.6, dur)


SLOT_NOTES = [1046.5, 1174.7, 1318.5, 1396.9, 1568.0, 1760.0, 1975.5, 2093.0, 2349.3, 2637.0]      # ド〜ミ（ハートが ゲージに 入る たびに 上がる）


def sparkle_snd(rng):                               # きらきら（MAX）：ド ミ ソ ド の 小さな 鈴
    out = np.zeros(int(1.4 * SR))
    for k, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)): put(out, 0.6 * chime(f, 0.3, 1.0), 0.08 * k)
    return out


# ---------- 馬の 息 ----------
def snort_snd(rng, dur=0.5):                        # ぶるるっ（くちびるを ふるわせる 息）
    n = int(dur * SR); t = np.arange(n) / SR
    fl = 0.55 + 0.45 * np.sin(2 * np.pi * (26 + 6 * t / dur) * t)
    x = amb.lp(noise(n, rng), 1400, 2) * fl + 0.5 * np.sin(2 * np.pi * 170 * t) * fl
    return x * env(n, 0.03, dur * 0.4)


def breath_snd(rng, dur=1.0, fc=1100, att=0.25):    # ふぅ〜（息）
    n = int(dur * SR); t = np.arange(n) / SR
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** (0.8 if att > 0.2 else 1.6)
    return amb.bp(noise(n, rng), 180, fc, 2) * e


def sneeze_snd(rng):                                # ぷしゅっ
    n = int(0.3 * SR); t = np.arange(n) / SR
    x = amb.hp(noise(n, rng), 1100) * np.exp(-t / 0.045) * np.minimum(1, t / 0.004)
    return x + 0.5 * modes([110, 260], [1.0, 0.4], [0.05, 0.03], 0.3)


def nicker_snd(rng):                                # ふふふん（甘える：やさしい いななき）
    n = int(0.9 * SR); t = np.arange(n) / SR
    saw = 2 * ((110 * t + 0.1 * np.sin(2 * np.pi * 5 * t)) % 1) - 1
    v = amb.bp(saw, 250, 900, 2)
    puls = np.zeros(n)
    for k in range(5):
        a = int((0.06 + 0.13 * k) * SR); m = int(0.09 * SR)
        if a + m < n: puls[a:a + m] += np.sin(np.pi * np.arange(m) / m) * (1 - 0.12 * k)
    return v * puls + 0.2 * amb.lp(noise(n, rng), 900) * puls


def whoosh(rng, dur=0.5, f1=300, f2=2200):          # しゅっ（しっぽ・ズーム）
    n = int(dur * SR); t = np.arange(n) / SR
    return amb.bp(noise(n, rng), f1, f2, 2) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2


def thud_snd(rng, k=1.0):                           # ドン（横に なる・着地）：やわらかい 土
    return mix(modes([70, 120, 230], [1.0, 0.6, 0.25], [0.12, 0.07, 0.04], 0.5), 0.35 * burst(0.12, 120, 900, 0.03, rng)) * k


def hoof_tap(rng):                                  # トッ（ひづめ）
    return mix(modes([180, 420], [1.0, 0.4], [0.03, 0.015], 0.12), 0.3 * burst(0.03, 400, 2500, 0.006, rng))


def boing_snd():                                    # ぴょん
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 300 + 420 * (1 - np.exp(-t / 0.08)) + 20 * np.sin(2 * np.pi * 9 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.005, 0.12)


def whistle_snd():                                  # ぴゅいっ（呼ぶ）
    n = int(0.55 * SR); t = np.arange(n) / SR
    f = np.where(t < 0.22, 1150 + 300 * t / 0.22, 1250 + 450 * np.clip((t - 0.26) / 0.12, 0, 1))
    g = np.where(t < 0.22, np.sin(np.pi * np.clip(t / 0.22, 0, 1)) ** 0.6, 0) + np.where(t > 0.25, np.sin(np.pi * np.clip((t - 0.25) / 0.3, 0, 1)) ** 0.6, 0)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * g * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))


# ---------- ごはん（11/09：エサ・リンゴ・ニンジン）----------
def knock_snd(rng, f=(300, 720, 1300), k=1.0):      # ことっ（木の バケツを 置く）
    return mix(modes(list(f), [1.0, 0.45, 0.2], [0.06, 0.035, 0.02], 0.3), 0.3 * burst(0.04, 500, 3500, 0.008, rng)) * k


def grain_snd(rng, dur=0.4):                        # さらさら（えん麦が ゆれる）
    n = int(dur * SR); x = np.zeros(n); m = int(0.004 * SR)
    for i in range(int(dur * 110)):
        at = int(rng.random() * (n - m - 1)); x[at:at + m] += (0.4 + 0.6 * rng.random()) * amb.hp(noise(m, rng), 2500) * np.exp(-np.arange(m) / (0.001 * SR))
    return amb.bp(x, 1500, 9000, 2) * env(n, 0.01, dur * 0.45) * 2.0


def crunch_snd(rng, lo=1800, hi=8000, body=180, dur=0.08):      # シャクッ（1口）：かたい 実を かじる
    n = int(dur * SR); t = np.arange(n) / SR
    x = amb.bp(noise(n, rng), lo, hi, 2) * np.exp(-t / (dur * 0.3)) * np.minimum(1, t / 0.0015)
    m = int(0.006 * SR)
    for k in range(4):                                # パリパリ
        at = int((0.004 + 0.012 * k + 0.004 * rng.random()) * SR)
        if at + m < n: x[at:at + m] += 1.2 * amb.hp(noise(m, rng), 3500) * np.exp(-np.arange(m) / (0.0015 * SR))
    return mix(x, 0.45 * modes([body, body * 2.3], [1.0, 0.4], [0.025, 0.015], 0.12))


def chew_snd(rng, n_=4, gap=0.17, lo=900, hi=4500, k=0.5):      # もぐもぐ（かむ）
    out = np.zeros(int((n_ * gap + 0.2) * SR))
    for i in range(n_):
        put(out, k * (0.7 + 0.3 * rng.random()) * crunch_snd(rng, lo, hi, 140, 0.06), i * gap + 0.02 * rng.random())
    return out


def munch_snd(rng):                                  # バケツの 中で もぐもぐ（えん麦：くぐもった 音）
    return mix(amb.lp(chew_snd(rng, 5, 0.16, 700, 3800, 0.8), 3200, 2), 0.35 * grain_snd(rng, 0.5))


def lick_snd(rng):                                   # ぺろっ（しめった 短い 音）
    n = int(0.2 * SR); t = np.arange(n) / SR; x = np.zeros(n); seg = 441
    for i in range(0, n, seg):
        m = min(seg, n - i); f = 600 + 1800 * (i / n); x[i:i + m] = amb.bp(noise(m + 256, rng), f * 0.7, f * 1.4, 2)[256:256 + m]
    return x * np.sin(np.pi * np.clip(t / 0.2, 0, 1)) ** 1.5 + 0.25 * glide(500, 900, 0.2, 0.7) * env(n, 0.01, 0.06)


def sniff_snd(rng, k=2):                             # くんくん
    out = np.zeros(int((0.2 * k + 0.25) * SR))
    for i in range(k):
        n = int(0.09 * SR); t = np.arange(n) / SR
        put(out, amb.bp(noise(n, rng), 900, 5200, 2) * np.sin(np.pi * np.clip(t / 0.09, 0, 1)) ** 2, 0.2 * i)
    return out


def nibble_snd(rng):                                 # もぐっ？（ちょっと かんで みる）
    return mix(chew_snd(rng, 2, 0.14, 900, 4000, 0.6), np.concatenate([np.zeros(int(0.3 * SR)), 0.3 * glide(420, 620, 0.16, 1.5) * env(int(0.16 * SR), 0.01, 0.06)]))


def beg_snd(rng):                                    # ふん？（おかわりの目：小さく 鼻を 鳴らして 首を かしげる）
    return mix(0.6 * snort_snd(rng, 0.3), np.concatenate([np.zeros(int(0.25 * SR)), 0.35 * glide(380, 560, 0.22, 1.6) * env(int(0.22 * SR), 0.02, 0.08)]))


def gold_snd(rng):                                   # キラーン（金のニンジン）：明るい 鈴の 上り ＋ きらきら
    out = np.zeros(int(1.8 * SR))
    for k, f in enumerate((1318.5, 1568.0, 2093.0, 2637.0)): put(out, 0.55 * chime(f, 0.35, 1.2), 0.06 * k)
    put(out, 0.3 * amb.hp(noise(int(0.9 * SR), rng), 5000) * env(int(0.9 * SR), 0.05, 0.25), 0.05)
    return out


# ---------- おそうじ ----------
def sweep_snd(rng, dur=0.32):                        # さっ（ほうき：毛先が 地面を こする）
    n = int(dur * SR); t = np.arange(n) / SR
    x = amb.bp(noise(n, rng), 1200, 7500, 2) * (0.75 + 0.25 * np.sin(2 * np.pi * 70 * t)) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.2
    return x + 0.25 * amb.lp(noise(n, rng), 500, 2) * np.sin(np.pi * np.clip(t / dur, 0, 1))


def inpan_snd(rng):                                  # ことん（ちりとりに 入る）
    return mix(modes([520, 1180, 2100], [1.0, 0.4, 0.15], [0.05, 0.03, 0.015], 0.25), 0.35 * burst(0.06, 800, 5000, 0.012, rng))


def kira_snd(rng):                                   # キラッ（きれい！）
    out = np.zeros(int(1.2 * SR))
    for k, f in enumerate((1568.0, 2093.0, 2637.0)): put(out, 0.5 * chime(f, 0.25, 0.9), 0.07 * k)
    return out


def luck_snd(rng):                                   # 運がついた！（高確ゾーン）：きらきら ＋ 明るい 和音
    out = np.zeros(int(2.0 * SR)); put(out, sparkle_snd(rng), 0.0)
    for k, f in enumerate((523.3, 659.3, 784.0, 1046.5)): put(out, 0.35 * bell(f, 0.6, 1.4), 0.12 + 0.03 * k)
    return out


# ---------- 降臨の バナー（幻の馬・神様馬の フィールド）----------
def harp_up(fs, gap=0.07, tau=0.7):                 # ポロロロン（上って いく）
    out = np.zeros(int((gap * len(fs) + 1.6) * SR))
    for k, f in enumerate(fs):
        n = int(1.5 * SR); t = np.arange(n) / SR
        y = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.08 * np.sin(2 * np.pi * 3 * f * t)) * np.exp(-t / tau) * np.minimum(1, t / 0.003)
        put(out, y * (0.9 - 0.04 * k), gap * k)
    return out


def banin_snd(rng, kind):                            # 降臨！：神様馬＝明るい 光の 和音・幻の馬＝ふしぎな 音
    if kind == 'kamisama':
        out = harp_up([523.3, 659.3, 784.0, 1046.5, 1318.5, 1568.0, 2093.0], 0.06, 0.8)
        put(out, 0.45 * chime(2637.0, 0.4, 1.2), 0.42)
        n = int(1.4 * SR); t = np.arange(n) / SR; pad = np.zeros(n)
        for f in (523.3, 659.3, 784.0): pad += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
        put(out, 0.18 * pad * np.sin(np.pi * np.clip(t / 1.4, 0, 1)) ** 1.5, 0.05)
    else:
        out = harp_up([392.0, 466.2, 587.3, 698.5, 932.3, 1174.7], 0.08, 0.9)
        n = int(1.2 * SR); t = np.arange(n) / SR
        put(out, 0.5 * amb.lp(noise(n, rng), 400, 2) * np.sin(np.pi * np.clip(t / 1.2, 0, 1)) ** 2, 0.0)
        put(out, 0.35 * chime(1864.7, 0.5, 1.3), 0.5)
    put(out, 0.5 * whoosh(rng, 0.5, 400, 3000), 0.0)
    return out


# できごと → 音（名前・音・大きさ・遠さ）
def render(T, evs, t0, seed=11):
    rng = np.random.default_rng(seed); buf = np.zeros((2, int(T * SR) + SR))
    def add(x, g, t, pan=0.0, dist=0.1, wet=0.18):
        if 0 <= t < T: amb.add(buf, amb.place(x, pan, g, dist, wet0=wet), t)
    for e in evs:
        k, t = e['k'], e['t'] - t0
        if k == 'button': add(button_snd(rng), 0.16, t)
        elif k == 'unfold': add(paper_snd(rng), 0.13, t)
        elif k == 'fold': add(paper_snd(rng, 0.24, 0.85), 0.09, t)
        elif k == 'rub': add(rub_snd(rng), 0.075, t - 0.12); add(pop_snd(620 + 40 * e.get('n', 1), 900 + 60 * e.get('n', 1)), 0.05, t + 0.02)
        elif k == 'heart': add(pop_snd(560, 880), 0.11, t)
        elif k == 'slot': add(chime(SLOT_NOTES[min(9, max(0, e.get('n', 1) - 1))], 0.25, 0.8), 0.09, t)
        elif k == 'nod': add(snort_snd(rng, 0.5), 0.1, t + 0.15, -0.1)
        elif k == 'swish': add(whoosh(rng, 0.45, 250, 1800), 0.05, t + 0.1, -0.2); add(whoosh(rng, 0.45, 250, 1800), 0.04, t + 0.85, -0.2)
        elif k == 'nuzzle': add(rub_snd(rng), 0.06, t + 0.2); add(breath_snd(rng, 0.8, 900), 0.06, t + 0.5)
        elif k == 'stretch': add(breath_snd(rng, 1.4, 800), 0.08, t + 0.3)
        elif k == 'sneeze': add(sneeze_snd(rng), 0.14, t + 0.6)
        elif k == 'tilt': add(glide(600, 920, 0.18, 2) * env(int(0.18 * SR), 0.005, 0.06), 0.08, t + 0.25)
        elif k == 'calm': add(breath_snd(rng, 1.1, 1000), 0.06, t + 0.4)
        elif k == 'frisk':
            for q in range(4): add(hoof_tap(rng), 0.08, t + 0.15 + 0.19 * q, 0.1)
            add(snort_snd(rng, 0.4), 0.06, t + 0.3)
        elif k == 'yawn': add(breath_snd(rng, 1.6, 700), 0.08, t + 0.2)
        elif k == 'lie': add(thud_snd(rng), 0.1, t + 4.6)
        elif k == 'nope': add(modes([392, 330], [0.6, 0.6], [0.08, 0.1], 0.4), 0.07, t)
        elif k == 'wait': add(mix(glide(330, 300, 0.09) * env(int(0.09 * SR), 0.004, 0.04), np.concatenate([np.zeros(int(0.11 * SR)), glide(262, 250, 0.1) * env(int(0.1 * SR), 0.004, 0.05)])), 0.06, t)
        elif k == 'ready': add(mix(chime(1318.5, 0.15, 0.5), np.concatenate([np.zeros(int(0.08 * SR)), chime(1760, 0.2, 0.6)])), 0.06, t)
        elif k in ('zoomin', 'zoomout'): add(whoosh(rng, 0.9, 200, 1400), 0.03, t)
        elif k == 'max': add(sparkle_snd(rng), 0.11, t)
        elif k == 'gather': add(breath_snd(rng, 0.7, 600), 0.05, t)
        elif k == 'hop': add(boing_snd(), 0.09, t + 0.02); add(thud_snd(rng, 0.7), 0.07, t + 0.58)
        elif k == 'flop': add(thud_snd(rng), 0.1, t + 2.1); add(breath_snd(rng, 1.2, 900), 0.06, t + 2.4)
        elif k == 'goron': add(mix(chime(784, 0.2, 0.6), np.concatenate([np.zeros(int(0.14 * SR)), chime(659.3, 0.25, 0.7)])), 0.05, t)
        elif k == 'unlock': add(piron_snd(), 0.3, t)
        elif k == 'stock': add(pop_snd(700, 1050), 0.06, t)
        elif k == 'call': add(whistle_snd(), 0.09, t + 0.05)
        elif k == 'turn': add(snort_snd(rng, 0.35), 0.06, t + 0.2)
        elif k == 'amae': add(nicker_snd(rng), 0.09, t + 0.2)
        elif k == 'heartpop': add(pop_snd(600, 940), 0.06, t)
        elif k == 'ready2': add(mix(chime(1318.5, 0.15, 0.5), np.concatenate([np.zeros(int(0.08 * SR)), chime(1760, 0.2, 0.6)])), 0.06, t)
        elif k == 'paper': add(paper_snd(rng, 0.3, 1.1), 0.1, t)
        elif k == 'chooser':
            for q in range(3): add(paper_snd(rng, 0.22, 1.0 + 0.1 * q), 0.07, t + 0.07 * q, -0.3 + 0.3 * q)
        elif k == 'pick': add(button_snd(rng), 0.12, t); add(chime(1318.5, 0.2, 0.6), 0.05, t + 0.05)
        elif k == 'token': add(pop_snd(480, 640), 0.05, t)
        elif k == 'bucket': add(knock_snd(rng), 0.11, t); add(grain_snd(rng, 0.45), 0.05, t + 0.05)
        elif k == 'munch': add(munch_snd(rng), 0.17, t)
        elif k == 'lick': add(lick_snd(rng), 0.11, t)
        elif k == 'bite':
            kd = e.get('kind', 'apple')
            if kd == 'apple': add(crunch_snd(rng, 2000, 9000, 200), 0.17, t + 0.05); add(chew_snd(rng, 3, 0.18, 1400, 6000, 0.45), 0.08, t + 0.3)
            else: add(crunch_snd(rng, 1500, 7000, 160), 0.18, t + 0.05); add(chew_snd(rng, 3, 0.17, 1100, 5200, 0.5), 0.08, t + 0.28)
        elif k == 'yummy': add(nicker_snd(rng), 0.09, t + 0.1); add(chime(1568.0, 0.25, 0.8), 0.05, t)
        elif k == 'beg': add(beg_snd(rng), 0.16, t + 0.2)
        elif k == 'gold': add(gold_snd(rng), 0.1, t)
        elif k == 'sweep': add(sweep_snd(rng), 0.11, t, 0.1 * math.sin(t * 3))
        elif k == 'inpan': add(inpan_snd(rng), 0.1, t)
        elif k == 'kira': add(kira_snd(rng), 0.09, t)
        elif k == 'luck': add(luck_snd(rng), 0.12, t)
        elif k == 'piron': add(piron_snd(), 0.3, t)
        elif k == 'sniff': add(sniff_snd(rng, 2), 0.09, t + 0.1); add(sniff_snd(rng, 2), 0.08, t + 0.9)
        elif k == 'nibble': add(nibble_snd(rng), 0.16, t)
        elif k == 'banin': add(banin_snd(rng, e.get('kind', 'kamisama')), 0.09, t - 0.05)
        elif k == 'banout': add(whoosh(rng, 0.4, 500, 3500), 0.06, t)
    return buf[:, :int(T * SR)]


if __name__ == '__main__':
    if sys.argv[1] == 'parts':
        D = sys.argv[2]; os.makedirs(D, exist_ok=True); rng = np.random.default_rng(7)
        for nm, x, g in (('unfold', paper_snd(rng), 0.13), ('rub', rub_snd(rng), 0.075), ('heart', pop_snd(560, 880), 0.11), ('max', sparkle_snd(rng), 0.11),
                         ('hop', boing_snd(), 0.09), ('thud', thud_snd(rng), 0.1), ('snort', snort_snd(rng), 0.1), ('nicker', nicker_snd(rng), 0.09), ('whistle', whistle_snd(), 0.09), ('sneeze', sneeze_snd(rng), 0.14)):
            y = amb.place(x, 0.0, g * 1.41, 0.08)
            wavfile.write(os.path.join(D, f'care_{nm}.wav'), SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
            print(nm, 'peak', round(float(np.abs(y).max()), 3))
        sys.exit()
    OUT, T, TOD, EV = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
    d = json.load(open(EV)); evs, t0 = d['events'], d.get('t0', 1.5)
    if TOD in ('abyss', 'divine'):                      # 幻の馬・神様馬の フィールドは BGM（bgm.py の 60秒 ループ）
        import bgm
        L = bgm.abyss() if TOD == 'abyss' else bgm.divine(); reps = int(np.ceil(T / bgm.LOOP)) + 1
        base = np.tile(L, reps)[:, :int(T * SR)].copy()
    else: base = amb.scene(T, TOD, 105)[:, :int(T * SR)].copy()
    buf = base + render(T, evs, t0)
    pk = float(np.abs(buf).max()); print(OUT, 'できごと', len(evs), 'peak', round(pk, 3), round(20 * math.log10(max(pk, 1e-6)), 1), 'dB')
    if pk > .95: buf *= .95 / pk
    wavfile.write(OUT, SR, (buf.T * 32767).astype(np.int16))
