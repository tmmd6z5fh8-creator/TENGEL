# お世話チャレンジ（玉を 落とす 台）の 音（第4.173版・まさちゃん 2026/11/15 00:48）
#   「馬バレ音 ①青:ピピィーン ②緑:ピピピィーン ③紫:ピピピピィーン ④赤:ピピピピピィーン ⑤金:ドゥゴーンとピピピピピィーン(同時)
#     ⑥虹色: キュイキュイキュイとドゥゴーンとビィボォーンとピピピピピィーン」
#   ぜんぶ 計算で 作る（録音は 使わない）。
#   ・uma_snd(n)：ピ（短い 高い 電子音）を n−1回 → さいごの 1回 だけ 4度 上で 長く のこる（ピィーン）。青 2・緑 3・紫 4・赤 5・金 5・虹 5
#   ・dogoon_snd：ドゥゴーン ＝ ドゥ（短い 低い 前打ち）→ ゴーン（腹に ひびく 低い 音 ＋ 鐘の ような うなり ＋ 空気）
#   ・kyui3_snd：キュイキュイキュイ ＝ すばやく 上がる 音が 3回
#   ・biiboon_snd：ビィボォーン ＝ ビィ（高い ぶるぶるした 音）→ ボォーン（2オクターブ 下・長く のこる）
#   ・金＝ドゥゴーン と ピ×5 を 同時に／虹＝4つを 重ねる（出だしを 少しずつ ずらして、どれも 聞こえる ように）
#   ・玉の 音：out（ポンッ：受け皿から 出る）・peg1〜3（コッ：釘に 当たる・高さ ちがい）・cup（コトン：コップに 入る）・miss（ポスッ：はずれ）・
#     hold（キラン：保留が たまる）・open（カチャ・ピロリン：保留結果を 見られる ように なった）
#   python3 sfx_drop.py <出す フォルダ>            … アプリ用の m4a（tc_se_dp_*.m4a）
#   python3 sfx_drop.py <出す フォルダ> wav        … wav（聞いて 確かめる 用）
import os, subprocess, sys, tempfile
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
from sfx_roulette import modes, put
SR = amb.SR
PIP_F, RING_F = 1975.5, 2637.0                      # ピ（シ）・ピィーン（ミ：4度 上）
PIP_STEP = 0.105                                    # ピと ピの 間（秒）
N_PIP = {1: 2, 2: 3, 3: 4, 4: 5, 5: 5, 6: 5}        # 色（1 青 … 6 虹）→ ピの 数（さいごの ピィーンも 数える）
# 山の 大きさ（片がわ）。いまの 音（ピロン 0.23・キュインキュイーン 0.27・デデーン 0.36・ドーン！！ 0.65）と ならべて 決めた：
#   青〜赤は キュインキュイーンと 同じ くらい（色が 上がる ほど 少し 大きく）・金は その 上・虹は ドーン！！の 少し 下。はじめは 青〜赤 0.36・金 0.62・虹 0.70 で、
#   よく 出る 青（10〜300P）が ピロンの 2倍の 大きさに なって いた（高い 音は 耳に 強い）
G = dict(uma1=0.25, uma2=0.26, uma3=0.27, uma4=0.28, gold=0.50, rainbow=0.58, out=0.26, peg=0.20, cup=0.30, miss=0.16, hold=0.20, open=0.24)


def pip(f, dur=0.07):
    """ピ（短い 電子音：明るい・立ち上がりが 速い）"""
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    y = np.sin(ph) + 0.32 * np.sin(2 * ph + 0.4) + 0.12 * np.sign(np.sin(ph)) + 0.10 * np.sin(3 * ph)
    e = np.minimum(1, t / 0.003) * np.minimum(1, np.maximum(0, dur - t) / 0.02) * (0.75 + 0.25 * np.exp(-t / 0.02))
    return y * e


def ring(f, dur=1.25, tau=0.42):
    """ピィーン（長く のこる：少し ずれた 2本 ＋ 上の 倍音 ＋ ゆっくり ゆれる）"""
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.0035 * np.sin(2 * np.pi * 6.2 * t) * np.clip((t - 0.12) / 0.2, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    y = np.sin(ph) + 0.55 * np.sin(1.004 * ph + 0.7) + 0.30 * np.sin(2 * ph) * np.exp(-t / 0.16) + 0.12 * np.sign(np.sin(ph)) * np.exp(-t / 0.05) + 0.16 * np.sin(3.01 * ph) * np.exp(-t / 0.09)
    e = np.minimum(1, t / 0.003) * np.exp(-t / tau) * np.minimum(1, np.maximum(0, dur - t) / 0.08)
    return y * e


def uma_snd(n, rng=None):
    """ピ×(n−1) ＋ ピィーン"""
    out = np.zeros(int((PIP_STEP * (n - 1) + 1.35) * SR))
    for i in range(n - 1):
        put(out, 0.80 * pip(PIP_F), PIP_STEP * i)
    put(out, 1.0 * ring(RING_F), PIP_STEP * (n - 1))
    if rng is not None:                              # きらっ（小さな 鈴を うすく）
        for j in range(3):
            put(out, 0.05 * modes([rng.uniform(4200, 6200)], [1.0], [0.12], 0.4), PIP_STEP * (n - 1) + 0.08 + 0.09 * j)
    return amb.lp(out, 9500, 2)


def dogoon_snd(rng):
    """ドゥゴーン"""
    out = np.zeros(int(2.3 * SR))
    m = int(0.14 * SR); tm = np.arange(m) / SR                                              # ドゥ（前打ち：短い 低い 音）
    put(out, 0.55 * np.sin(2 * np.pi * np.cumsum(70 + 150 * np.exp(-tm / 0.018)) / SR) * np.minimum(1, tm / 0.002) * np.exp(-tm / 0.045), 0.0)
    put(out, 0.25 * amb.bp(rng.normal(0, 1, m), 200, 1800, 2) * np.exp(-tm / 0.02), 0.0)
    t0 = 0.085                                                                              # ゴーン
    n = int(1.9 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(40 + 95 * np.exp(-t / 0.06)) / SR                            # 腹に ひびく（135 → 40Hz）
    put(out, 0.62 * np.tanh(2.6 * (np.sin(ph) + 0.35 * np.sin(2 * ph))) * np.minimum(1, t / 0.003) * np.exp(-t / 0.55), t0)
    n2 = int(1.0 * SR); t2 = np.arange(n2) / SR                                             # 電話の スピーカーでも 聞こえる 高さ（420 → 130Hz）
    ph2 = 2 * np.pi * np.cumsum(130 + 290 * np.exp(-t2 / 0.04)) / SR
    put(out, 0.62 * np.tanh(1.9 * np.sin(ph2)) * np.minimum(1, t2 / 0.002) * np.exp(-t2 / 0.26), t0)
    k = int(1.1 * SR); tk = np.arange(k) / SR; nz = rng.normal(0, 1, k)                     # 打った 瞬間の 空気（バン）と ひくい うなり
    put(out, 0.95 * amb.bp(nz, 240, 3000, 2) * np.exp(-tk / 0.06) + 0.34 * amb.lp(nz, 480, 2) * np.exp(-tk / 0.36), t0)
    put(out, 0.50 * modes([164.8, 247.0, 331.0, 415.5, 554.0], [1.0, 0.8, 0.62, 0.42, 0.25], [1.15, 0.95, 0.75, 0.55, 0.38], 1.9, 0.004), t0 + 0.004)      # 鐘の ような うなり（ゴーン）
    out = amb.lp(out, 7800, 2); out = out / np.abs(out).max()
    return np.tanh(2.2 * out) / np.tanh(2.2)


def kyui3_snd(rng):
    """キュイキュイキュイ"""
    out = np.zeros(int(0.62 * SR))

    def kyu(dur, f0, f1):
        n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
        f = f0 * (f1 / f0) ** (u ** 0.7)
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = np.sin(ph) + 0.3 * np.sin(2 * ph + 0.5) + 0.1 * np.sin(3 * ph) + 0.07 * np.sign(np.sin(ph))
        y *= 1 + 0.22 * np.sin(2 * np.pi * 36 * t)
        return y * np.minimum(1, t / 0.006) * np.minimum(1, np.maximum(0, dur - t) / 0.02)
    for i in range(3):
        put(out, (0.85 + 0.075 * i) * kyu(0.115, 640 + 40 * i, 2500 + 220 * i), 0.14 * i)
    return amb.lp(out, 7200, 2)


def biiboon_snd(rng):
    """ビィボォーン"""
    out = np.zeros(int(1.75 * SR))

    def buzz(f, dur, tau, wob):
        n = int(dur * SR); t = np.arange(n) / SR
        y = np.zeros(n)
        for d in (0.994, 1.0, 1.007):                                                       # 3本を 少し ずらして 太く
            ph = 2 * np.pi * f * d * t
            for h in range(1, 13):
                if f * h > 6500: break
                y += np.sin(h * ph + 0.3 * h) / h ** 0.95
        y *= 1 + 0.30 * np.sin(2 * np.pi * wob * t)                                         # ぶるぶる
        return y * np.minimum(1, t / 0.006) * np.exp(-np.maximum(0, t - 0.03) / tau) * np.minimum(1, np.maximum(0, dur - t) / 0.03)
    put(out, 0.50 * amb.lp(buzz(740.0, 0.21, 0.5, 31), 5200, 2), 0.0)                       # ビィ
    b = buzz(185.0, 1.5, 0.52, 23)                                                          # ボォーン（2オクターブ 下）
    n = len(b); t = np.arange(n) / SR
    b = amb.lp(b, 3400, 2) * 0.62 + 0.5 * np.sin(2 * np.pi * 92.5 * t) * np.exp(-t / 0.5)   # 下の オクターブを うすく（重さ）
    put(out, b, 0.21)
    return out / np.abs(out).max()


def gold_snd(rng):
    """金：ドゥゴーン と ピピピピピィーン（同時）"""
    out = np.zeros(int(2.4 * SR))
    put(out, 1.0 * dogoon_snd(rng), 0.0)
    put(out, 0.50 * uma_snd(5, rng), 0.0)
    return out


def rainbow_snd(rng):
    """虹：キュイキュイキュイ・ドゥゴーン・ビィボォーン・ピピピピピィーン を 重ねる"""
    out = np.zeros(int(2.6 * SR))
    put(out, 1.0 * dogoon_snd(rng), 0.0)
    put(out, 0.42 * kyui3_snd(rng), 0.0)
    put(out, 0.50 * biiboon_snd(rng), 0.05)
    put(out, 0.46 * uma_snd(5, rng), 0.02)
    for j in range(10):                                                                     # きらきら（うしろに のこる）
        put(out, 0.04 * modes([rng.uniform(3000, 5600)], [1.0], [0.22], 0.6), 0.7 + 0.11 * j + rng.uniform(0, 0.04))
    return out


def out_snd(rng):
    """ポンッ（玉が 受け皿から とび出す）"""
    n = int(0.16 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(360 + 620 * (1 - np.exp(-t / 0.03))) / SR) * np.minimum(1, t / 0.002) * np.exp(-t / 0.045)
    y += 0.3 * amb.bp(rng.normal(0, 1, n), 900, 4200, 2) * np.exp(-t / 0.008)
    return amb.lp(y, 6000, 2)


def peg_snd(rng, k=1.0):
    """コッ（釘に 当たる：紙の 玉と 紙の 釘）"""
    y = modes([1180 * k, 1830 * k, 2950 * k, 520 * k], [1.0, 0.6, 0.3, 0.5], [0.014, 0.010, 0.006, 0.02], 0.09, 0.0008)
    n = len(y); t = np.arange(n) / SR
    y += 0.5 * amb.bp(rng.normal(0, 1, n), 1500, 6000, 2) * np.exp(-t / 0.004)
    return amb.lp(y, 7500, 2)


def cup_snd(rng):
    """コトン（コップに 入る）"""
    out = np.zeros(int(0.42 * SR))
    put(out, 0.8 * modes([820, 1290, 410], [1.0, 0.5, 0.6], [0.022, 0.014, 0.03], 0.12, 0.001), 0.0)
    put(out, 1.0 * modes([345, 690, 1040], [1.0, 0.45, 0.2], [0.07, 0.04, 0.02], 0.3, 0.0015), 0.075)
    n = int(0.05 * SR); t = np.arange(n) / SR
    put(out, 0.4 * amb.bp(rng.normal(0, 1, n), 700, 3500, 2) * np.exp(-t / 0.006), 0.0)
    return amb.lp(out, 5200, 2)


def miss_snd(rng):
    """ポスッ（はずれ：やわらかく 小さく）"""
    n = int(0.22 * SR); t = np.arange(n) / SR
    y = amb.lp(rng.normal(0, 1, n), 900, 2) * np.minimum(1, t / 0.006) * np.exp(-t / 0.05)
    y += 0.7 * np.sin(2 * np.pi * np.cumsum(210 - 90 * t / 0.22) / SR) * np.exp(-t / 0.05)
    return y


def hold_snd(rng):
    """キラン（保留が ますに 入る）"""
    out = np.zeros(int(0.8 * SR))
    put(out, 0.7 * modes([2637.0, 5274.0], [1.0, 0.3], [0.10, 0.05], 0.4), 0.0)
    put(out, 1.0 * modes([3951.0, 7902.0], [1.0, 0.25], [0.26, 0.10], 0.75), 0.07)
    return amb.lp(out, 9500, 2)


def open_snd(rng):
    """カチャ（かぎが あく）→ ピロリン（保留結果を 見られる）"""
    out = np.zeros(int(1.0 * SR))
    n = int(0.03 * SR); t = np.arange(n) / SR
    put(out, 0.7 * amb.bp(rng.normal(0, 1, n), 1800, 6000, 2) * np.exp(-t / 0.004), 0.0)
    put(out, 0.6 * modes([1250, 2130, 3320], [1.0, 0.6, 0.3], [0.02, 0.014, 0.008], 0.1, 0.0008), 0.004)
    put(out, 0.5 * modes([760, 1480], [1.0, 0.5], [0.03, 0.02], 0.12, 0.001), 0.06)
    for j, f in enumerate((1568.0, 1975.5, 2637.0)):
        put(out, (0.55 + 0.15 * j) * modes([f, 2 * f], [1.0, 0.22], [0.16 + 0.09 * j, 0.06], 0.75), 0.16 + 0.085 * j)
    return amb.lp(out, 9000, 2)


def render():
    """→ { 名前: (2, n) の 音 }（アプリの ファイルの 名前：tc_se_dp_<名前>.m4a）"""
    rng = np.random.default_rng(15)
    S = {}
    for c in (1, 2, 3, 4):
        S[f'uma{c}'] = amb.place(uma_snd(N_PIP[c], rng), 0.0, G[f'uma{c}'] * 1.41, 0.05)
    S['uma5'] = amb.place(gold_snd(rng), 0.0, G['gold'] * 1.41, 0.05)
    S['uma6'] = amb.place(rainbow_snd(rng), 0.0, G['rainbow'] * 1.41, 0.05)
    S['out'] = amb.place(out_snd(rng), 0.0, G['out'] * 1.41, 0.05, wet0=0.08)
    for i, k in enumerate((0.9, 1.0, 1.13), 1):
        S[f'peg{i}'] = amb.place(peg_snd(rng, k), 0.0, G['peg'] * 1.41, 0.04, wet0=0.06)
    S['cup'] = amb.place(cup_snd(rng), 0.0, G['cup'] * 1.41, 0.05, wet0=0.08)
    S['miss'] = amb.place(miss_snd(rng), 0.0, G['miss'] * 1.41, 0.05, wet0=0.06)
    S['hold'] = amb.place(hold_snd(rng), 0.0, G['hold'] * 1.41, 0.05)
    S['open'] = amb.place(open_snd(rng), 0.0, G['open'] * 1.41, 0.05)
    out = {}
    for k, y in S.items():
        pk = float(np.abs(y).max()); g = G['rainbow' if k == 'uma6' else 'gold' if k == 'uma5' else k if k.startswith('uma') else k.rstrip('123')]
        y = y * (g / pk)                                # 山を きめた 大きさに そろえる
        a = np.abs(y).max(0); nz = np.nonzero(a > 1e-4)[0]
        y = y[:, :min(y.shape[1], nz[-1] + int(0.06 * SR))].copy()
        m = min(int(0.02 * SR), y.shape[1]); y[:, -m:] *= np.linspace(1, 0, m)
        out[k] = y
    return out


if __name__ == '__main__':
    D = sys.argv[1]; os.makedirs(D, exist_ok=True); wav = len(sys.argv) > 2 and sys.argv[2] == 'wav'
    tmp = tempfile.mkdtemp()
    for k, y in render().items():
        w = os.path.join(D if wav else tmp, f'tc_se_dp_{k}.wav'); wavfile.write(w, SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
        if not wav:
            o = os.path.join(D, f'tc_se_dp_{k}.m4a')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', o], check=True)
        print(k, round(y.shape[1] / SR, 2), '秒', 'peak', round(float(np.abs(y).max()), 3), '' if wav else f'{os.path.getsize(o)} B', flush=True)
