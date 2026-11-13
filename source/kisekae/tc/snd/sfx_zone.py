# ポイント特化ゾーンの 音（第4.165版・まさちゃん 2026/11/13 12:51「上乗せの場合は、虹色の光とドゥルルルン！ギュウィーンンン！の効果音
#   は上乗せ失敗の場合は、ピューン…とエネルギーが落ちた時のような効果音つけて！」）
#   ぜんぶ 計算で 作る（録音は 使わない）
#   ・zup_snd：ドゥルルルン！ギュウィーンンン！（上乗せ）
#       ドゥルルルン＝ 低い 音が ころがりながら 上がる（太鼓の 連打 8つ ＋ ふるえる 低い 音 150 → 430Hz・さいごに「ン」と 少し のびる）
#       ギュウィーンンン＝ ギュ（ざらっと した 立ち上がり）→ ウィーン（260 → 1,900Hz へ 加速して 上がる・ふるえも 速く なる ＝ 力が たまって いく）
#         → ンンン（上がりきった 高さで 明るい 和音が ゆれながら 長く のこる）＋ きらきら
#   ・zdown_snd：ピューン…（上乗せ 失敗）＝ ピュ（高い 音が 少し 上がって）→ ーン…（1,900 → 190Hz へ 落ちて いく・だんだん 小さく・ゆれが 大きく なる ＝ エネルギーが 落ちる）＋ うすい 空気の 音
#   python3 kisekae/tc/snd/sfx_zone.py <出す フォルダ> [ios/tc_assets]   → tc_se_zn_up.m4a・tc_se_zn_down.m4a（アプリ用）と 同じ 名前の .wav（聞いて 確かめる 用）
#     2つめの フォルダを 書くと、できた m4a を そこへ 写す（**上書きしない**：同じ 名前で 中身の ちがう ものが あれば 止まる → 新しい 名前に して tc/tc_fx.js の 名前も かえる）→ python3 kisekae/lite_assets.py
#   ・できた 音は リポジトリに 入れない（ios/tc_assets/ は .gitignore）
import os, subprocess, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
from sfx_roulette import modes, put
SR = amb.SR
G_UP, G_DOWN = 0.42, 0.28              # 山の 大きさ（上乗せ −7.5dB ぐらい：デデーンと 同じ ぐらい・失敗 −11dB ぐらい：ひかえめ）


def saw(ph, n=9, tilt=1.0):
    """のこぎりの ような 音（倍音を 重ねる）"""
    y = np.zeros(len(ph))
    for k in range(1, n + 1): y += np.sin(k * ph) / k ** tilt
    return y


def zup_snd(rng):                                   # ドゥルルルン！ギュウィーンンン！
    out = np.zeros(int(2.3 * SR))
    # ---- ドゥルルルン（0〜0.5秒）----
    d = 0.44; n = int(d * SR); t = np.arange(n) / SR; u = t / d
    f = 150 * (430 / 150) ** (u ** 1.15)                                                    # 150 → 430Hz
    ph = 2 * np.pi * np.cumsum(f) / SR
    roll = 0.25 + 0.75 * (0.5 + 0.5 * np.sin(2 * np.pi * 21 * t - 1.2)) ** 2.2              # ルルル（1秒に 21回の ふるえ）
    body = np.tanh(1.6 * saw(ph, 7, 1.1)) * roll * np.minimum(1, t / 0.006) * np.minimum(1, (d - t) / 0.03)
    put(out, 0.5 * amb.lp(body, 3200, 2), 0.0)
    for j in range(8):                                                                      # 太鼓の 連打（だんだん 高く・だんだん 強く）
        m = int(0.12 * SR); tm = np.arange(m) / SR; f0 = 120 + 26 * j
        hit = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.7 * np.exp(-tm / 0.012))) / SR) * np.exp(-tm / 0.05) + 0.3 * amb.bp(rng.normal(0, 1, m), 300, 2400, 2) * np.exp(-tm / 0.012)
        put(out, (0.34 + 0.05 * j) * hit, 0.012 + 0.052 * j)
    m = int(0.2 * SR); tm = np.arange(m) / SR                                               # ン（430Hz が 少し のびる）
    put(out, 0.3 * (np.sin(2 * np.pi * 430 * tm) + 0.35 * np.sin(2 * np.pi * 860 * tm)) * np.minimum(1, tm / 0.01) * np.exp(-tm / 0.06), d - 0.01)
    # ---- ギュウィーンンン（0.52〜）----
    t0 = 0.52
    m = int(0.07 * SR); tm = np.arange(m) / SR                                              # ギュ（ざらっと）
    put(out, 0.5 * amb.bp(rng.normal(0, 1, m), 700, 3400, 2) * np.exp(-tm / 0.018) + 0.5 * np.tanh(3 * np.sin(2 * np.pi * np.cumsum(210 + 300 * tm / 0.07) / SR)) * np.exp(-tm / 0.03), t0)
    d2, hold = 0.56, 1.1; n2 = int((d2 + hold) * SR); t2 = np.arange(n2) / SR; u2 = np.clip(t2 / d2, 0, 1)
    f2 = 260 * (1900 / 260) ** (u2 ** 1.7)                                                  # ウィーン：加速して 上がる
    f2 = f2 * (1 + 0.012 * np.sin(2 * np.pi * 6.5 * t2) * np.clip((t2 - d2) / 0.12, 0, 1))  # 上がりきったら ゆれる
    ph2 = 2 * np.pi * np.cumsum(f2) / SR
    trem = 1 + 0.3 * np.sin(2 * np.pi * np.cumsum(16 + 44 * u2) / SR) * (1 - 0.7 * np.clip((t2 - d2) / 0.3, 0, 1))      # ふるえが 速く なる（16 → 60回／秒）→ のびた 所は おさまる
    y2 = (saw(ph2, 6, 1.25) + 0.35 * np.sin(0.5 * ph2)) * trem
    e2 = np.minimum(1, t2 / 0.03) * (0.55 + 0.45 * u2) * np.exp(-np.maximum(0, t2 - d2) / 0.42)
    put(out, 0.5 * amb.lp(y2 * e2, 6800, 2), t0 + 0.03)
    for fq, a in ((950.0, 0.26), (1425.0, 0.2), (1900.0, 0.26), (2850.0, 0.1)):             # ンンン：上がりきった 所で 明るい 和音（1度・5度・8度）
        k = int(hold * SR); tk = np.arange(k) / SR
        put(out, a * np.sin(2 * np.pi * fq * tk * (1 + 0.0015 * np.sin(2 * np.pi * 5.5 * tk))) * np.minimum(1, tk / 0.02) * np.exp(-tk / 0.45), t0 + 0.03 + d2 - 0.02)
    k = int(0.9 * SR); tk = np.arange(k) / SR                                               # シャーン（うすい 息）
    put(out, 0.1 * amb.hp(rng.normal(0, 1, k), 4500) * np.minimum(1, tk / 0.01) * np.exp(-tk / 0.3), t0 + d2)
    for j in range(9):                                                                      # きらきら
        fq = rng.uniform(2600, 5200); put(out, 0.045 * modes([fq], [1.0], [0.22], 0.6), t0 + d2 + 0.03 + 0.085 * j + rng.uniform(0, 0.03))
    out = amb.lp(out, 8200, 2)
    return out / np.abs(out).max()


def zdown_snd(rng):                                 # ピューン…
    out = np.zeros(int(1.6 * SR))
    d = 1.25; n = int(d * SR); t = np.arange(n) / SR
    up = 0.05; u = np.clip((t - up) / (d - up), 0, 1)
    f = np.where(t < up, 1500 + 400 * (t / up), 1900 * (190 / 1900) ** (u ** 0.72))         # ピュ（少し 上がって）→ 落ちる
    f = f * (1 + (0.004 + 0.035 * u ** 2) * np.sin(2 * np.pi * (7 - 2.5 * u) * t))          # ゆれが だんだん 大きく・おそく（力が ぬける）
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.22 * np.sin(2 * ph + 0.3) + 0.07 * np.sin(3 * ph)
    e = np.minimum(1, t / 0.008) * (1 - 0.82 * u ** 0.8) * np.minimum(1, (d - t) / 0.12)
    put(out, 0.8 * y * e, 0.0)
    x = rng.normal(0, 1, n)                                                                 # 空気が ぬける（高い ざわめきが 低く なる）
    air = amb.bp(x, 1800, 5200, 2) * (1 - u) ** 2 + amb.bp(x, 500, 1700, 2) * 2 * u * (1 - u)
    put(out, 0.1 * air * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.2), 0.0)
    m = int(0.3 * SR); tm = np.arange(m) / SR                                               # …（さいごに 小さく ポスッ）
    put(out, 0.16 * np.sin(2 * np.pi * np.cumsum(190 - 70 * tm / 0.3) / SR) * np.minimum(1, tm / 0.01) * np.exp(-tm / 0.07), d - 0.03)
    out = amb.lp(out, 7000, 2)
    return out / np.abs(out).max()


def main():
    D = sys.argv[1]; os.makedirs(D, exist_ok=True); rng = np.random.default_rng(7)
    for nm, x, g in (('tc_se_zn_up', zup_snd(rng), G_UP), ('tc_se_zn_down', zdown_snd(rng), G_DOWN)):
        y = amb.place(x, 0.0, g * 1.41, 0.08)
        a = np.abs(y).max(0); nz = np.nonzero(a > 1e-4)[0]; y = y[:, :min(y.shape[1], nz[-1] + int(0.08 * SR))]
        k = int(0.01 * SR); y[:, -k:] *= np.linspace(1, 0, k)
        w = os.path.join(D, nm + '.wav'); wavfile.write(w, SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
        o = os.path.join(D, nm + '.m4a')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', o], check=True)
        print(nm, round(y.shape[1] / SR, 2), '秒', os.path.getsize(o) // 1024, 'KB', 'peak', round(float(np.abs(y).max()), 3))
    if len(sys.argv) > 2:                # アプリの 絵と 音の フォルダへ 写す（上書きしない）
        A = sys.argv[2]; assert os.path.isdir(A), A
        fs = [(os.path.join(D, n + '.m4a'), os.path.join(A, n + '.m4a')) for n in ('tc_se_zn_up', 'tc_se_zn_down')]
        for src, dst in fs:
            if os.path.exists(dst) and open(dst, 'rb').read() != open(src, 'rb').read(): raise SystemExit(f'もう ある ファイルと 中身が ちがう（上書きしない）：{dst}')
        for src, dst in fs:
            if os.path.exists(dst): print('同じ ものが もう ある：', os.path.basename(dst)); continue
            with open(dst, 'xb') as f: f.write(open(src, 'rb').read())
            print('置いた：', dst)


if __name__ == '__main__':
    main()
