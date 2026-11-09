# ルーレット なしの 当たり（100P・200P・300P）の「ピロン」（11/09 00:29 まさちゃん「当選したポイントがピロンと出てくる演出にして！」）
#   ぜんぶ 計算で 作る（録音は 使わない）。ぱたっ（札が 開く 紙の 音・小さく）＋ ピ（ミ）→ ロン（ラ：長く 残る）
#   python3 sfx_piron.py <出す wav> <秒> <ポイント:時間> …   … piron.html と 同じ 時間で 鳴らす（下に 朝の 環境音 −11dB）
#   python3 sfx_piron.py parts <フォルダ>                      … 1つの 音（アプリ 用：piron）
import math, os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
from sfx_roulette import modes, burst, mix, put, bell
SR = amb.SR
G_PIRON = 0.3          # 山の 大きさ 0.2 くらい（ルーレットの 確定の 音より 少し 小さく）


def piron_snd(rng):
    out = np.zeros(int(1.4 * SR))
    put(out, 0.18 * amb.lp(burst(0.05, 700, 3500, 0.01, rng), 3500, 2), 0.0)       # ぱたっ（札が 開く）
    put(out, 0.5 * bell(1318.5, 0.5) * np.exp(-np.arange(int(0.5 * SR)) / SR / 0.09), 0.02)        # ピ（ミ：短く）
    put(out, 0.55 * bell(1760.0, 1.2), 0.11)                                                          # ロン（ラ：長く 残る）
    return amb.lp(out, 8000, 2)


if __name__ == '__main__':
    if sys.argv[1] == 'parts':
        D = sys.argv[2]; os.makedirs(D, exist_ok=True)
        y = amb.place(piron_snd(np.random.default_rng(3)), 0.0, G_PIRON * 1.41, 0.08)
        wavfile.write(os.path.join(D, 'rt_piron.wav'), SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16)); print('piron peak', round(float(np.abs(y).max()), 3))
        sys.exit()
    OUT, T = sys.argv[1], float(sys.argv[2])
    buf = amb.scene(T, 'morning', 107)[:, :int(T * SR)].copy()
    for i, spec in enumerate(sys.argv[3:]):
        pt, at = spec.split(':')
        amb.add(buf, amb.place(piron_snd(np.random.default_rng(i)), -0.1, G_PIRON, 0.08, wet0=.18), float(at))
    pk = float(np.abs(buf).max()); print('peak', round(pk, 3))
    if pk > .95: buf *= .95 / pk
    wavfile.write(OUT, SR, (buf.T * 32767).astype(np.int16)); print(OUT, buf.shape[1] / SR)
