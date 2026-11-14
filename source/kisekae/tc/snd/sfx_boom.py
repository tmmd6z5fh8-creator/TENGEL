# ルーレットの 高い 方の 爆発の 音（第4.171版・まさちゃん 2026/11/14 16:18
#   「④トレーニングセンターの神様馬、幻の馬ルーレットで高い方が当選し、プチュンした後は、リアルな爆発と一緒に獲得ポイントの表示するようにして！」）
#   爆発の 動画（kisekae/tc/boom.py：tc_rt_boom.mp4）と いっしょに 鳴らす 音（tc_se_boom.m4a）。ぜんぶ 計算で 作る（録音・素材は 使わない）。
#   ・バン（はじめの 一瞬：空気が はじける・0.02秒）→ ドォン（腹に ひびく 低い 音：95 → 34Hz・0.5秒）→ ゴォォ（火の 玉の うなり：だんだん こもって 消える・1.5秒）
#     → パチ パチ（火花・かけら：ばらばらに・だんだん まばらに）→ 遠くへ ひびく のこり
#   ・電話の 小さい スピーカー（200Hz より 下は ほとんど 出ない）でも 聞こえる ように、バンと ゴォォは 300〜2500Hz にも 中身が ある・ドォンに 110〜340Hz の 音を 重ねる
#   ・山は −7dB（G_BOOM）で 作る。m4a に 圧縮すると ざらざらした 音の 山は 高く なる（ファイルの 山は −1.6dB）→ アプリは 0.75倍で 鳴らす（tc/tc_fx.js の BOOM.gain）。
#     テロップの ドーン！！（tc_se_doon）は 0.6秒 あと（テロップが 飛びこむ 時）に 鳴らす ＝ 山どうしが 重ならない
#   python3 sfx_boom.py <出す wav>      （アプリ用は export_app.py <フォルダ> tc_se_boom）
import math, os, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
SR = amb.SR
G_BOOM = 0.45       # 山（−7dB）
DUR = 2.6           # 秒（動画と 同じ 長さ）


def boom_snd(seed=171):
    """爆発の 音 → ステレオ（2, n）"""
    rng = np.random.default_rng(seed); n = int(DUR * SR); t = np.arange(n) / SR
    out = np.zeros((2, n)); up = lambda a: np.minimum(1, t / a)
    # バン：はじけた 空気（広い 帯の 雑音が 一瞬）と、そのあとの 短い ざらつき
    for c in range(2):
        out[c] += 2.2 * amb.bp(rng.normal(0, 1, n), 180, 7000, 2) * np.exp(-t / 0.022) * up(0.0012) + 1.8 * amb.bp(rng.normal(0, 1, n), 300, 2600, 2) * np.exp(-t / 0.09) * up(0.002)
    # ドォン：低い 音が 落ちる（少し ひずませて 太く）＋ 低い 雑音の かたまり ＋ 小さい スピーカーでも 聞こえる 高さの 音
    ph = 2 * np.pi * np.cumsum(34 + 61 * np.exp(-t / 0.07)) / SR
    thump = np.tanh(2.2 * (np.sin(ph) + 0.35 * np.sin(2 * ph + 0.4))) * up(0.004) * np.exp(-t / 0.42)
    sub = amb.lp(rng.normal(0, 1, n), 140, 2) * np.exp(-t / 0.55) * up(0.01) * 2.2
    mid = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(110 + 230 * np.exp(-t / 0.04)) / SR)) * np.exp(-t / 0.16) * up(0.002)
    out += (0.7 * thump + 0.35 * sub + 1.3 * mid)[None, :]
    # ゴォォ：火の 玉の うなり（帯ごとの 雑音を 重ねる：上の 帯から 順に 消えて いく ＝ だんだん こもる・ゆらぐ）
    fc = 380 + 4200 * np.exp(-t / 0.36)                                     # いちばん 上の 帯の 高さ（4.6kHz → 380Hz）
    for c in range(2):
        nz = rng.normal(0, 1, n); roar = np.zeros(n)
        for (lo, hi), g_ in zip(((70, 300), (300, 700), (700, 1500), (1500, 3200), (3200, 7000)), (1.0, 0.8, 0.6, 0.45, 0.3)):
            roar += g_ * amb.bp(nz, lo, hi, 2) * np.clip((fc - lo) / (hi - lo), 0, 1)
        flut = np.clip(1 + 2.4 * amb.lp(rng.normal(0, 1, n), 14, 2), 0.35, 1.8)      # ゆらぎ（1秒に 10回 くらいまでの ゆっくりした 波）
        out[c] += 5.5 * roar * up(0.03) * (0.75 * np.exp(-t / 0.45) + 0.25 * np.exp(-t / 1.1)) * flut
    # パチ パチ：火花・かけら（短い 雑音の 粒・だんだん まばらに・左右に ちらばる）
    for _ in range(46):
        tt = 0.06 + rng.exponential(0.42)
        if tt > DUR - 0.3: continue
        m = int(rng.uniform(0.004, 0.018) * SR)
        x = amb.bp(rng.normal(0, 1, m + 256), rng.uniform(1200, 2600), rng.uniform(4200, 8000), 2)[256:] * np.exp(-np.arange(m) / SR / rng.uniform(0.002, 0.006))
        a = rng.uniform(0.05, 0.16) * math.exp(-tt / 1.0); pan = rng.uniform(-0.8, 0.8); i0 = int(tt * SR)
        out[0, i0:i0 + m] += a * x * math.sqrt((1 - pan) / 2); out[1, i0:i0 + m] += a * x * math.sqrt((1 + pan) / 2)
    # 遠くへ ひびく のこり
    k = int(1.3 * SR); wet = np.zeros((2, n))
    for c in range(2):
        ir = rng.normal(0, 1, k) * np.exp(-6.2 * np.arange(k) / k); ir = amb.lp(ir, 2600, 1); ir[:int(0.02 * SR)] = 0; ir /= math.sqrt(float(np.sum(ir ** 2)))
        wet[c] = signal.fftconvolve(out[c], ir)[:n]
    out = amb.lp(out + 0.3 * wet, 9000, 2)
    out = out / np.abs(out).max(); out = np.tanh(3.6 * out) / math.tanh(3.6)      # 山を おさえて 胴を 太く（はじめの 一瞬 だけ 大きくて あとが 小さい 音に ならない ように）
    f = int(0.35 * SR); out[:, -f:] *= np.linspace(1, 0, f) ** 2
    return out * G_BOOM


if __name__ == '__main__':
    y = boom_snd()
    wavfile.write(sys.argv[1], SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
    m = y.mean(0)
    def band(f1, f2):
        b, a = signal.butter(3, [f1 / (SR / 2), f2 / (SR / 2)], 'band'); return 20 * math.log10(max(1e-9, math.sqrt(float(np.mean(signal.lfilter(b, a, m) ** 2)))))
    print(sys.argv[1], round(y.shape[1] / SR, 2), '秒', 'peak %.1f dB' % (20 * math.log10(float(np.abs(y).max()))), 'RMS %.1f dB' % (20 * math.log10(math.sqrt(float(np.mean(y ** 2))))),
          '帯', {nm: round(band(a, b), 1) for nm, a, b in (('40-200', 40, 200), ('200-800', 200, 800), ('800-3k', 800, 3000), ('3k-9k', 3000, 9000))})
    k = int(0.1 * SR); print('0.1秒ごとの 大きさ(dB):', ' '.join('%.0f' % (20 * math.log10(max(1e-9, math.sqrt(float(np.mean(y[:, i:i + k] ** 2)))))) for i in range(0, y.shape[1], k)))
