# お世話の あとの PUSH の 音（第4.159版・まさちゃん 2026/11/12 10:37「ハズレは音だけで知らせて！プフォって空気が抜けるような音」
#   「10〜100p ピロン！・200〜300 デデーン！・ルーレット当選 キュインキュイーン！」）
#   ぜんぶ 計算で 作る（録音は 使わない）。ピロンは 前から ある 音（sfx_pop.py の piron_snd）
#   ・pfo_snd：プフォ（ハズレ）＝ ぷ（くちびるが はじける 低い ポン）→ ふぉ〜（息が ぬけて 下がる・ぶるぶる ふるえる）
#   ・dedeen_snd：デデーン！（200〜300P）＝ デ（短い 和音）・デーン（明るい 和音が 長く のこる）＋ 太鼓 ＋ シンバルの ような 息
#   ・kyuin_snd：キュインキュイーン！（ルーレット当選）＝ すばやく 上がる 音が 2回（2回目は 高く 長く のびて ゆれる）＋ きらきら
#   ・doon_snd：ドーン！！（まさちゃん 11/12 13:30「ドーン！！みたいな音と一緒にテロップ出して！」＝ルーレットの 高い 方で 出る「大量ポイント」の テロップ）
#     ＝ ド（腹に ひびく 低い 音が 落ちる・太鼓の 皮と 空気）＋ ーン（金管の ような 明るい 和音が 長く のこる）＋ シャーン（シンバルの ような 息）＋ きらきら
#   アプリ用の ファイル（tc_se_pfo・tc_se_dedeen・tc_se_kyuin.m4a）は export_app.py が sfx_care.render を 通して 書く：
#     python3 export_app.py <出す フォルダ> tc_se_pfo,tc_se_dedeen,tc_se_kyuin,tc_se_doon
#   python3 sfx_push.py <フォルダ>   … 3つの 音を wav で（聞いて 確かめる 用）
import os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
from sfx_roulette import modes, put
SR = amb.SR
G_DOON = 0.72                                       # ドーン！！の 山（−6.5dB ぐらい。電話の スピーカーで 聞こえる 高さ〈180Hz より 上〉の 大きさは 前の ルーレットの 確定〈−7dB〉と 同じ ぐらい・イヤホンでは 低い 音の 分 大きい）
G_PFO, G_DEDEEN, G_KYUIN = 0.24, 0.42, 0.40        # 山の 大きさ（できた 音の 山：プフォ −13dB・デデーン −9dB・キュインキュイーン −11.5dB。ピロン −13dB・ルーレットの 確定 −7dB）


def pfo_snd(rng):                                   # プフォ（空気が ぬける）
    d = 0.6; n = int(d * SR); t = np.arange(n) / SR; u = t / d
    x = rng.normal(0, 1, n)
    hi, mid, lo = amb.bp(x, 900, 2600, 2), amb.bp(x, 420, 1300, 2), amb.bp(x, 170, 620, 2)
    air = hi * (1 - u) ** 2 + 1.25 * mid * 2 * u * (1 - u) + 1.7 * lo * u ** 2              # 息の 高さが 下がって いく（しぼむ）
    flut = 1 + 0.6 * np.sin(2 * np.pi * np.cumsum(44 - 20 * u) / SR)                        # ぶるぶる（くちびる・風船の 口が ふるえる：44 → 24回／秒）
    e = np.minimum(1, t / 0.012) * np.exp(-np.maximum(0, t - 0.08) / 0.19)
    out = 1.15 * air * flut * e
    out += 0.22 * np.sin(2 * np.pi * np.cumsum(320 - 185 * u ** 0.6) / SR) * e              # ふぉ（下がる 声の ような 音を うすく）
    m = int(0.07 * SR); tm = np.arange(m) / SR
    out[:m] += 0.6 * np.sin(2 * np.pi * np.cumsum(175 - 85 * tm / 0.07) / SR) * np.exp(-tm / 0.022)       # ぷ（低い ポン）
    return amb.lp(out, 5200, 2)


def brass(f, dur, att=0.018, rel=0.25, bright=1.0, rng=None):
    """金管の ような 音（倍音を 重ねる・立ち上がりで 明るく・少し ゆれる）"""
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.4 * t) * np.clip((t - 0.15) / 0.2, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    y = np.zeros(n)
    for k in range(1, 11):
        a = 1 / k ** (1.25 / bright) * np.exp(-t * 0.9 * (k - 1) / 4)                      # 高い 倍音ほど 早く 消える
        y += a * np.sin(k * ph + 0.4 * k)
    e = np.minimum(1, t / att) * np.minimum(1, np.maximum(0, dur - t) / rel)
    return y * e


def dedeen_snd(rng):                                # デデーン！
    out = np.zeros(int(1.7 * SR))
    G3, C3, C4, D4, E4, G4, C5 = 196.0, 130.81, 261.63, 293.66, 329.63, 392.0, 523.25

    def drum(f=92, tau=0.11):                       # ドン（太鼓）
        n = int(0.4 * SR); t = np.arange(n) / SR
        return np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t / 0.02))) / SR) * np.exp(-t / tau) + 0.25 * amb.lp(rng.normal(0, 1, n), 900, 2) * np.exp(-t / 0.03)
    # デ（短く）：ソ・レ・ソ
    for f, a in ((G3, 0.45), (D4, 0.45), (G4, 0.45)):
        put(out, a * brass(f, 0.15, 0.012, 0.07, 1.35), 0.0)
    put(out, 0.7 * drum(98, 0.08), 0.0)
    # デーン（長く）：ド（低い）・ド・ミ・ソ・ド ＝ 明るい 和音
    t1 = 0.19
    for f, a in ((C3, 0.42), (C4, 0.5), (E4, 0.44), (G4, 0.46), (C5, 0.4)):
        x = brass(f, 1.25, 0.02, 0.75, 1.4)
        put(out, a * x * np.exp(-np.arange(len(x)) / SR / 0.75), t1)
    put(out, 0.85 * drum(82, 0.16), t1)
    n = int(0.9 * SR); t = np.arange(n) / SR                                                # シャーン（シンバルの ような 息）
    put(out, 0.16 * amb.hp(rng.normal(0, 1, n), 4200) * np.minimum(1, t / 0.006) * np.exp(-t / 0.28), t1)
    for j, f in enumerate((2093.0, 2637.0, 3136.0)):                                        # きらっ（小さな 鈴）
        put(out, 0.05 * modes([f], [1.0], [0.25], 0.7), t1 + 0.05 + 0.06 * j)
    return amb.lp(out, 7800, 2) * 0.27


def kyuin_snd(rng):                                 # キュインキュイーン！
    out = np.zeros(int(1.5 * SR))

    def kyu(dur, f0, f1, tail=0.0):
        n = int((dur + tail) * SR); t = np.arange(n) / SR; u = np.clip(t / dur, 0, 1)
        f = f0 * (f1 / f0) ** (u ** 0.75)                                                   # すばやく 上がる（のびる ほど ゆっくり）
        f = f * (1 + 0.018 * np.sin(2 * np.pi * 9 * t) * np.clip((t - dur) / 0.08, 0, 1))  # のびた 所は ゆれる
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = np.sin(ph) + 0.3 * np.sin(2 * ph + 0.5) + 0.1 * np.sin(3 * ph) + 0.06 * np.sign(np.sin(ph))
        y *= 1 + 0.22 * np.sin(2 * np.pi * 34 * t)                                          # こまかい ふるえ（電子音の キュイン）
        e = np.minimum(1, t / 0.008) * (np.exp(-np.maximum(0, t - dur) / 0.16) if tail else np.minimum(1, np.maximum(0, dur - t) / 0.03))
        return y * e
    put(out, 0.5 * kyu(0.2, 560, 2000), 0.0)                                                # キュイン
    put(out, 0.55 * kyu(0.34, 560, 2500, 0.55), 0.27)                                       # キュイーン（高く 長く）
    for j in range(8):                                                                      # きらきら
        f = rng.uniform(3200, 5200); put(out, 0.035 * modes([f], [1.0], [0.05], 0.16), 0.55 + 0.07 * j + rng.uniform(0, 0.03))
    return amb.lp(out, 7000, 2) * 0.66


def doon_snd(rng):                                  # ドーン！！
    out = np.zeros(int(2.4 * SR))
    n = int(1.6 * SR); t = np.arange(n) / SR                                                # ド（腹に ひびく）：低い 音が 150 → 46Hz に 落ちる（少し ひずませて 太く）
    ph = 2 * np.pi * np.cumsum(46 + 104 * np.exp(-t / 0.05)) / SR
    put(out, 0.5 * np.tanh(2.4 * (np.sin(ph) + 0.4 * np.sin(2 * ph))) * np.minimum(1, t / 0.003) * np.exp(-t / 0.5), 0.0)
    n2 = int(0.8 * SR); t2 = np.arange(n2) / SR                                             # ドン（電話の 小さい スピーカーでも 聞こえる 高さ）：380 → 124Hz
    ph2 = 2 * np.pi * np.cumsum(124 + 256 * np.exp(-t2 / 0.035)) / SR
    put(out, 0.6 * np.tanh(1.8 * np.sin(ph2)) * np.minimum(1, t2 / 0.002) * np.exp(-t2 / 0.22), 0.0)
    m = int(0.9 * SR); tm = np.arange(m) / SR; nz = rng.normal(0, 1, m)                     # 打った 瞬間の 皮と 空気（バン）
    put(out, 1.0 * amb.bp(nz, 260, 3400, 2) * np.exp(-tm / 0.055) + 0.3 * amb.lp(nz, 520, 2) * np.exp(-tm / 0.3), 0.0)
    for fq, a in ((65.41, 0.5), (130.81, 0.62), (196.0, 0.6), (261.63, 0.7), (329.63, 0.6), (392.0, 0.62), (523.25, 0.56), (659.25, 0.3)):      # ーン：ド・ド・ソ・ド・ミ・ソ・ド・ミ（明るい 和音が 長く のこる）
        x = brass(fq, 2.0, 0.012, 1.2, 1.6); put(out, 1.2 * a * x * np.exp(-np.arange(len(x)) / SR / 1.2), 0.008)
    k = int(1.6 * SR); tk = np.arange(k) / SR                                               # シャーン（シンバルの ような 息）
    put(out, 0.35 * amb.hp(rng.normal(0, 1, k), 3600) * np.minimum(1, tk / 0.004) * np.exp(-tk / 0.45), 0.006)
    for j in range(7):                                                                      # きらきら
        fq = rng.uniform(2400, 4600); put(out, 0.06 * modes([fq], [1.0], [0.3], 0.8), 0.25 + 0.09 * j + rng.uniform(0, 0.03))
    out = amb.lp(out, 8600, 2); out = out / np.abs(out).max()
    out = np.tanh(2.5 * out) / np.tanh(2.5)                                                 # 山を おさえて 胴を 太く（打った 瞬間 だけ 大きく、あとが 小さい 音に ならない ように）
    return out * 0.95                                                                       # 山を そろえる（× G_DOON × 置き方 0.7 で −6.5dB ぐらい）


if __name__ == '__main__':
    D = sys.argv[1]; os.makedirs(D, exist_ok=True); rng = np.random.default_rng(7)
    for nm, x, g in (('pfo', pfo_snd(rng), G_PFO), ('dedeen', dedeen_snd(rng), G_DEDEEN), ('kyuin', kyuin_snd(rng), G_KYUIN), ('doon', doon_snd(rng), G_DOON)):
        y = amb.place(x, 0.0, g * 1.41, 0.08)
        wavfile.write(os.path.join(D, f'push_{nm}.wav'), SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
        print(nm, round(len(x) / SR, 2), '秒', 'peak', round(float(np.abs(y).max()), 3))
