# 音の「耳に 聞こえる 大きさ」を 測る 道具（第4.174版）：A特性（耳の 感じ方に 合わせた 重み：低い 音・とても 高い 音は 小さく 数える）を かけて、0.125秒ごとの 大きさの 山を dB で
#   python3 loud.py <wav か m4a> …            … ファイルごとの 山（dBA）と 片がわの 山（peak）
#   import loud; loud.dba(y, sr)               … y＝(n,) か (2, n) か (n, 2)
#   ねらい：低い 音（ドゥ・ドーン）は 波の 山が 大きく 出る わりに 小さく 聞こえる。山（peak）で そろえると 高い 音（ピ）が 大きく 聞こえ すぎる ので、聞こえる 大きさで そろえる
import subprocess, sys
import numpy as np


def a_weight(f):
    f2 = np.maximum(f, 1e-6) ** 2
    ra = 12194.0 ** 2 * f2 ** 2 / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194.0 ** 2))
    return ra * 10 ** (2.0 / 20)


def mono(y):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim == 2: y = y.mean(0 if y.shape[0] <= 2 else 1)
    return y


def weighted(y, sr):
    y = mono(y); n = len(y)
    return np.fft.irfft(np.fft.rfft(y) * a_weight(np.fft.rfftfreq(n, 1 / sr)), n)


def series(y, sr, win=0.125, hop=0.01):
    """→ (時刻, dBA)：win 秒の 窓の 大きさ"""
    w = weighted(y, sr); m = int(win * sr); h = int(hop * sr)
    c = np.concatenate([[0.0], np.cumsum(w * w)])
    i = np.arange(0, max(1, len(w) - m), h)
    return i / sr, 10 * np.log10(np.maximum((c[i + m] - c[i]) / m, 1e-12))


def dba(y, sr, win=0.125):
    return float(series(y, sr, win)[1].max())


def read(path, sr=44100):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(sr), '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2).T


if __name__ == '__main__':
    for p in sys.argv[1:]:
        y = read(p)
        print(f'{p.split("/")[-1]:28s} {dba(y, 44100):6.1f} dBA  peak {np.abs(y).max():.3f}  {y.shape[1] / 44100:.2f}秒')
