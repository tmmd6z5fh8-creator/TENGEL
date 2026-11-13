# ルーレットの BGM（第4.168版・まさちゃん 2026/11/14 01:26「ルーレットに入った時にBGMを変える。フィールドBGMは重ねない。」）
#   ぜんぶ 計算で 作る（録音・素材は 使わない）。つなぎ目なく くり返せる 8小節（4拍子・132 BPM ＝ 約14.5秒）。
#   イ短調：Am → F → G → E（2小節ずつ）＝「どっちが 出るかな」と どきどき しながら 待つ 感じ（こわく しない・うるさく しない）
#   ・ベース：8分の きざみ（根音と オクターブ上を 交互に）
#   ・マリンバの ような アルペジオ：16分で 和音の 音を 上がって 下がる（左右に ふる）
#   ・うらの 和音：2拍・4拍の うらに 軽い スタブ
#   ・鈴の 旋律：1〜2小節・5〜6小節に 短い ふし／7〜8小節は 上がって いく 4つの 音（つぎの 頭へ つなぐ）
#   ・打楽器：キック（1・3拍）・クラップ（2・4拍）・ハイハット（8分・うらを 少し 強く）・8小節めに スネアの ロール（だんだん 大きく）
#   大きさ：フィールドの BGM（−36dB）より 少し 大きい −34dB・山は −17dB まで（ルーレットの カチッ〈山 −15.5dB〉・レバー・止まる 音が うもれない）
#   つなぎ目なし：音の のこり と ひびき は 頭へ まわす（輪の ように）
#   python3 bgm_roulette.py <出す wav>     （アプリ用の m4a は export_app.py が 作る：tc_bgm_roulette.m4a）
import math, os, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
SR = amb.SR
BPM = 132; BEAT = 60 / BPM; BAR = 4 * BEAT; BARS = 8; LOOP = BARS * BAR
N = int(round(LOOP * SR)); TAILN = int(3.0 * SR)
RMS_DB = -34.0; PEAK_DB = -17.0
CHORDS = [(45, [57, 60, 64]), (41, [57, 60, 65]), (43, [55, 59, 62]), (40, [56, 59, 64])]      # 2小節ずつ：Am・F・G・E（ベースの 音, 和音の 3つ）


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)


class Stem:
    """音の 置き場（ループ ＋ のこり）。fold() で のこりを 頭へ まわす"""
    def __init__(self): self.b = np.zeros((2, N + TAILN))

    def put(self, x, at, pan=0.0, gain=1.0):
        x = np.asarray(x) * gain; i = int(round(at * SR)) % N
        st = np.stack([x * math.sqrt((1 - pan) / 2), x * math.sqrt((1 + pan) / 2)])
        while st.shape[1] > 0:
            m = min(st.shape[1], self.b.shape[1] - i); self.b[:, i:i + m] += st[:, :m]; st = st[:, m:]; i = 0

    def fold(self):
        y = self.b[:, :N].copy(); y[:, :TAILN] += self.b[:, N:]; return y


def fade_in(y, sec):
    k = max(1, int(sec * SR)); y[:k] *= np.linspace(0, 1, k); return y


def bass_note(m, dur=0.2):
    n = int((dur + 0.08) * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = 0.6 * signal.sawtooth(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * tt) + 0.25 * signal.square(2 * np.pi * f * tt)
    y = amb.lp(y, 520, 2) * np.exp(-tt / (dur * 0.9)); return fade_in(y, 0.004)


def marimba(m, dur=0.32):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.11) + 0.28 * np.sin(2 * np.pi * 4 * f * tt) * np.exp(-tt / 0.035) + 0.1 * np.sin(2 * np.pi * 10 * f * tt) * np.exp(-tt / 0.012)
    return fade_in(y, 0.002)


def stab(ms, dur=0.16):
    n = int((dur + 0.1) * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for m in ms:
        for d in (-0.06, 0.06):
            y += signal.sawtooth(2 * np.pi * mtof(m) * 2 ** (d / 12) * tt)
    y = amb.lp(y, 2200, 2) * np.exp(-tt / (dur * 0.55)); return fade_in(y, 0.006)


def bell(m, dur=1.1):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for r_, a_, d_ in ((1.0, 1.0, 0.42), (2.0, 0.3, 0.25), (3.01, 0.22, 0.16), (5.2, 0.08, 0.08)):
        y += a_ * np.sin(2 * np.pi * f * r_ * tt) * np.exp(-tt / d_)
    return amb.lp(fade_in(y, 0.003), 7000, 2)


def kick():
    n = int(0.26 * SR); tt = np.arange(n) / SR; f = 46 + 95 * np.exp(-tt / 0.028)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.085); return fade_in(y, 0.002)


def clap(rng):
    n = int(0.2 * SR); tt = np.arange(n) / SR; x = amb.bp(rng.normal(0, 1, n), 900, 3200, 2); e = np.zeros(n)
    for t0 in (0.0, 0.011, 0.023):
        k = int(t0 * SR); e[k:] += np.exp(-(tt[:n - k]) / (0.012 if t0 < 0.02 else 0.06))
    return x * e


def hat(rng, dur=0.035):
    n = int(0.09 * SR); tt = np.arange(n) / SR; return amb.hp(rng.normal(0, 1, n), 7000, 2) * np.exp(-tt / dur)


def snare(rng, dur=0.05):
    n = int(0.16 * SR); tt = np.arange(n) / SR
    y = amb.bp(rng.normal(0, 1, n), 700, 5200, 2) * np.exp(-tt / dur) + 0.5 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / 0.03)
    return fade_in(y, 0.001)


def norm(x):
    r = math.sqrt(float(np.mean(x ** 2))); return x / max(r, 1e-12)


def reverb(x, rt, wet, seed, lpf):
    rng = np.random.default_rng(seed); n = int(rt * SR); y = x * (1 - 0.5 * wet)
    for c in range(2):
        ir = rng.normal(0, 1, n) * np.exp(-6.9 * np.arange(n) / n); ir = amb.lp(ir, lpf, 1); ir[:int(0.012 * SR)] = 0; ir /= np.sqrt(np.sum(ir ** 2))
        w = signal.fftconvolve(x[c], ir); out = w[:N].copy(); rest = w[N:]
        while len(rest): m = min(len(rest), N); out[:m] += rest[:m]; rest = rest[m:]          # ひびきの のこりは 頭へ（輪）
        y[c] += wet * out
    return y


def roulette():
    rng = np.random.default_rng(168)
    S8, S16 = BEAT / 2, BEAT / 4
    bass, arp, stb, mel, drum, hats = Stem(), Stem(), Stem(), Stem(), Stem(), Stem()
    for bar in range(BARS):
        root, ch = CHORDS[bar // 2]; t0 = bar * BAR
        # ベース：8分（根音・根音・オクターブ上・根音 を くり返す。4拍めの うらは 5度）
        for k in range(8):
            m = root + (12 if k % 4 == 2 else 7 if k == 7 else 0)
            bass.put(bass_note(m), t0 + k * S8, 0.0, 1.0 if k % 2 == 0 else 0.8)
        # アルペジオ：16分で 上がって 下がる（和音の 3つ ＋ 1オクターブ上の 根音）
        tones = [ch[0], ch[1], ch[2], ch[0] + 12, ch[2], ch[1]]
        for k in range(16):
            m = tones[k % len(tones)] + 12
            arp.put(marimba(m), t0 + k * S16, -0.35 if k % 2 == 0 else 0.35, 1.0 if k % 4 == 0 else 0.62)
        # うらの 和音：2拍・4拍の うら
        for b in (1.5, 3.5):
            stb.put(stab([c + 12 for c in ch]), t0 + b * BEAT, 0.12 if b < 2 else -0.12)
        # 打楽器
        for b in (0, 2): drum.put(kick(), t0 + b * BEAT, 0.0, 1.0)
        for b in (1, 3): drum.put(clap(rng), t0 + b * BEAT, 0.0, 0.5)
        for k in range(8): hats.put(hat(rng), t0 + k * S8, 0.25, 0.9 if k % 2 else 0.5)
    # 鈴の 旋律（拍, 音）
    for bar, notes in ((0, [(0, 76), (1, 81), (2, 84), (2.5, 83), (3, 81)]), (1, [(0, 79), (1, 76), (2, 81)]),
                       (4, [(0, 74), (1, 79), (2, 83), (2.5, 81), (3, 79)]), (5, [(0, 74), (1, 71), (2, 74)]),
                       (6, [(0, 76), (2, 80)]), (7, [(0, 83), (2, 88)])):
        for b, m in notes: mel.put(bell(m), bar * BAR + b * BEAT, rng.uniform(-0.25, 0.25))
    # 8小節め：スネアの ロール（16分 → 32分・だんだん 大きく）→ 頭の キックへ
    t0 = 7 * BAR; ts = [k * S16 for k in range(8)] + [2 * BEAT + k * S16 / 2 for k in range(16)]
    for i, tt in enumerate(ts):
        drum.put(snare(rng), t0 + tt, 0.0, 0.16 + 0.5 * (i / (len(ts) - 1)) ** 1.6)
    x = sum(10 ** (db / 20) * norm(s) for s, db in ((bass.fold(), -6), (arp.fold(), -8), (stb.fold(), -15), (mel.fold(), -10), (drum.fold(), -7), (hats.fold(), -19)))
    x = reverb(x, 0.55, 0.16, 9, 6000)
    x = amb.hp(np.concatenate([x[:, -8192:], x], 1), 32, 2)[:, 8192:]
    x *= 10 ** (RMS_DB / 20) / max(math.sqrt(float(np.mean(x ** 2))), 1e-12)
    pk = float(np.abs(x).max()); lim = 10 ** (PEAK_DB / 20)
    if pk > lim:                                                         # 山は −17dB まで：こえる 所 だけ なめらかに おさえる（全体は 小さく しない）
        k = 0.7 * lim; a = np.abs(x); over = a > k
        x[over] = np.sign(x[over]) * (k + (lim - k) * np.tanh((a[over] - k) / (lim - k)))
    return x


if __name__ == '__main__':
    y = roulette()
    wavfile.write(sys.argv[1], SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
    print(sys.argv[1], round(y.shape[1] / SR, 3), '秒', 'RMS %.1f dB' % (20 * math.log10(math.sqrt(float(np.mean(y ** 2))))), 'peak %.1f dB' % (20 * math.log10(float(np.abs(y).max()))))
