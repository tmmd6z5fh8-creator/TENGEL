# ルーレット ゾーン 以外の 当たり：お世話の 演出が 終わった ところで ポイントが「ピロン」と 出る ときの 音（11/09 00:33 まさちゃん）
#   ぜんぶ 計算で 作る（録音は 使わない）：ぽっ（紙の 札が 出る・小さく）＋ ピ（シ）・ロン（ミ）
#   python3 sfx_pop.py <出す wav> <秒> <出る 秒> [<出る 秒> …]   … pointpop.html と 同じ 時間で 鳴らす（下に 朝の 環境音 −11dB）
#   python3 sfx_pop.py parts <フォルダ>                             … アプリ 用の 1つの 音（pop_piron.wav）
import math, os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
from sfx_roulette import put
SR = amb.SR
G_PIRON = 0.3          # 山の 大きさ 0.25 くらい（環境音の 山 0.06・ルーレットの 確定 0.3）


def bell(f, tau, dur):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for m, a, tm in ((1.0, 1.0, 1.0), (2.0, 0.2, 0.5), (3.01, 0.05, 0.3)):
        y += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (tau * tm))
    k = int(0.003 * SR); y[:k] *= np.linspace(0, 1, k)
    return y


def piron_snd():
    out = np.zeros(int(1.4 * SR))
    n = int(0.09 * SR); t = np.arange(n) / SR
    po = np.sin(2 * np.pi * np.cumsum(560 - 220 * t / 0.09) / SR) * np.exp(-t / 0.022)
    k = int(0.002 * SR); po[:k] *= np.linspace(0, 1, k)
    put(out, 0.3 * po, 0.0)                                  # ぽっ（札が 出る）
    put(out, 0.55 * bell(987.77, 0.11, 0.5), 0.02)           # ピ（シ）
    put(out, 0.75 * bell(1318.51, 0.42, 1.3), 0.105)         # ロン（ミ）
    return amb.lp(out, 9000, 2)


if __name__ == '__main__':
    if sys.argv[1] == 'parts':
        D = sys.argv[2]; os.makedirs(D, exist_ok=True)
        y = amb.place(piron_snd(), 0.0, G_PIRON * 1.41, 0.06, wet0=.15)
        wavfile.write(os.path.join(D, 'pop_piron.wav'), SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
        print('piron peak', round(float(np.abs(y).max()), 3)); sys.exit()
    OUT, T = sys.argv[1], float(sys.argv[2])
    buf = amb.scene(T, 'morning', 105)[:, :int(T * SR)].copy()
    x = amb.place(piron_snd(), 0.0, G_PIRON, 0.06, wet0=.15)
    for at in sys.argv[3:]:
        amb.add(buf, x, float(at))
    pk = float(np.abs(buf).max()); print('peak', round(pk, 3), round(20 * math.log10(pk), 1), 'dB')
    if pk > .95: buf *= .95 / pk
    wavfile.write(OUT, SR, (buf.T * 32767).astype(np.int16)); print(OUT, buf.shape[1] / SR)
