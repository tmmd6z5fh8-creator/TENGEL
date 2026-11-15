# 激馬熱馬（第4.175版・まさちゃん 2026/11/15 13:56「トレーニングセンターに激馬熱馬当選を追加　1/299999 … 新しいプチュン一個目の動画と同じ速度、線の細さで線を赤と金で作成」・
#   14:04「プチュンの音は、動画の音にかなり近く作成して！」）の 音 3つ。ぜんぶ 計算で 作る（録音は 使わない）。
#   ・pchun（プチュゥゥーーン）：見本の 動画の 音を 数で 測って（kisekae/tc/snd/README は なし：測った 道具は 作業フォルダ）、同じ 形に なる ように 作った 音。
#       見本の 音そのもの（波形）は 1つも 入って いない ＝ 測った 数字（高さの 下がり方・倍音の 強さ・大きさの 形・こだま）だけを 使う
#       測った 形：
#         0〜0.07秒   プ：低い 音（190→95Hz）と 短い ざらざら ＋ 1.2kHz の 短い 音・上がる 細い 音（4.2k→9.6kHz）
#         0.075〜0.125秒  チュ：7.2kHz から 1.15kHz まで 一気に 下がる（0.023秒 ごとに 1/e）
#         0.125〜0.205秒  1.15kHz の まま
#         0.205〜1.67秒   ゥゥーーン：倍音の 多い 音が 下がる（高さ＝530 − 143t ＋ 273·exp(−(t−0.30)/0.109) Hz：0.3秒 743・0.5秒 502・1.0秒 387・1.66秒 293）。
#                         倍音は 450〜4500Hz が ほぼ 同じ 強さ・その 上は 急に 弱い。大きさは 0.6秒 まで だんだん 大きく なる。1.67秒で ぷつっと 切れる
#         こだま：0.355秒 おくれ・−14dB（切れた あとも 残る）
#   ・heaven（天国の 場面：2.4秒）：光の 和音（アー）と 上って いく ハープ ＋ カットの たびに シャキーン（0.6・1.07秒）＋ ぜんぶが 見える 場面（1.5秒）で ドーン ＋ テデーン（1.97秒）へ 上がって いく 音
#   ・tedeen（テ・デーン！）：短い 音 → 長い 和音（金管 ＋ 太鼓 ＋ シンバル ＋ 鈴）。「40000P獲得」の 字と いっしょ
#   python3 sfx_geki.py <出す フォルダ>            … アプリ用の m4a（tc_se_gk_*.m4a）
#   python3 sfx_geki.py <出す フォルダ> wav        … wav（数で 確かめる 用）
import os, subprocess, sys, tempfile
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
from sfx_roulette import modes, put
SR = amb.SR
PCHUN_LEN = 1.67                                    # プチュンの 音が 切れる 時（秒）：ここで 次の 場面（天国・馬バレの 絵）へ（tc/tc_fx.js の GK.dark・tc/tc_drop.js の PC_DARK と 同じ）
ECHO = (0.355, 0.2)                                 # こだま：おくれ（秒）・大きさ
FILM = dict(cuts=(18 / 30, 32 / 30, 45 / 30), text=59 / 30, len=2.4)   # 天国の 場面の カット（「40」→「00」→「0P」→ ぜんぶ：0.6・1.067・1.5秒）と テデーンの 時（1.967秒）：kisekae/tc/geki_film.py の CUTS・TEXT_F と 同じ
# 聞こえる 大きさ（A特性・0.125秒の 山・dBA：loud.py）。ほかの 大きな 音：ドーン！！ −17.5・虹の 馬バレ音 −16.8
GB = dict(pchun=-17.6, heaven=-18.4, tedeen=-16.6)
PEAK_MAX = 0.7


def f0_main(t):
    """下がって いく 音の 高さ（Hz）：見本を 測った 形"""
    zap = 7224 * np.exp(-(t - 0.075) / 0.0231)
    glide = 530 - 143 * t + 273 * np.exp(-(t - 0.30) / 0.109)
    return np.where(t < 0.125, np.maximum(1150, zap), np.minimum(1150, glide))


def _interp(t, pts):
    xs, ys = zip(*pts); return np.interp(t, xs, ys)


def pchun_snd(rng):
    n = int(2.9 * SR); t = np.arange(n) / SR; out = np.zeros(n)
    # --- プ：低い 音（190→95Hz）・短い ざらざら・1.2kHz の 短い 音 ---
    m = int(0.3 * SR); tm = t[:m]
    ph = 2 * np.pi * np.cumsum(95 + 95 * np.exp(-tm / 0.03)) / SR
    put(out, 0.15 * np.sin(ph) * np.minimum(1, tm / 0.004) * np.exp(-tm / 0.07), 0.008)
    put(out, 0.07 * np.sin(2 * np.pi * 52 * tm) * np.minimum(1, tm / 0.01) * np.exp(-tm / 0.16), 0.01)
    nz = rng.normal(0, 1, m)
    put(out, 0.085 * amb.bp(nz, 180, 700, 2) * np.minimum(1, tm / 0.003) * np.exp(-tm / 0.05), 0.008)
    put(out, 0.10 * amb.lp(amb.bp(nz, 4200, 9000, 2), 9500, 4) * np.minimum(1, tm / 0.004) * np.exp(-tm / 0.11), 0.008)      # チの ざらざら（5〜9kHz：0.1秒 ほど）
    put(out, 0.085 * amb.bp(nz, 1800, 5000, 2) * np.minimum(1, tm / 0.004) * np.exp(-tm / 0.045), 0.008)                    # はじめの 0.05秒は 2〜5kHz も
    # 低めの 音（275Hz：はじめから 0.4秒 ほど のこる。見本の 150〜600Hz の 帯）
    k4 = int(0.5 * SR); t4 = t[:k4]; p4 = 2 * np.pi * np.cumsum(278 - 18 * t4 / 0.4) / SR
    put(out, 0.045 * (np.sin(p4) + 0.35 * np.sin(2 * p4 + 1.0)) * np.minimum(1, t4 / 0.006) * _interp(t4, [(0, 1.0), (0.16, 0.95), (0.24, 0.55), (0.36, 0.6), (0.44, 0.0), (0.5, 0.0)]), 0.008)
    k = int(0.07 * SR); tk = t[:k]
    put(out, 0.085 * np.sin(2 * np.pi * 1200 * tk) * np.minimum(1, tk / 0.004) * np.minimum(1, np.maximum(0, 0.062 - tk) / 0.025), 0.008)
    # --- 上がる 細い 音（4.2k→9.6kHz：0.02〜0.04秒・0.07秒 まで のこる）---
    k = int(0.06 * SR); tk = t[:k]; fr = np.minimum(9600, 4200 * np.exp(tk / 0.0242))
    put(out, 0.05 * np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.minimum(1, tk / 0.003) * np.minimum(1, np.maximum(0, 0.058 - tk) / 0.02), 0.018)
    # --- チュ → ゥゥーーン：1つの 音が 7.2kHz から 下がる。倍音を 足して 作る ---
    a = int(0.075 * SR); b = int(PCHUN_LEN * SR); tt = t[a:b]; f0 = f0_main(tt); phi = 2 * np.pi * np.cumsum(f0) / SR
    # 大きさ（倍音 ぜんぶの 合計・dB）：見本の 600Hz〜10kHz の 帯の 大きさから（チュ −19 → 0.14〜0.36秒は −18 → 0.4秒から 3dB ほど 大きく −13.5〜−17）
    E = 10 ** (_interp(tt, [(0.075, -30), (0.082, -22), (0.10, -18.5), (0.125, -19), (0.14, -20.5), (0.20, -18.5), (0.30, -17.8), (0.36, -17), (0.40, -15.5), (0.50, -16), (0.60, -16),
                            (0.68, -13.8), (0.82, -13.5), (0.90, -16.5), (1.00, -14.8), (1.10, -17), (1.20, -17.2), (1.30, -15.6), (1.40, -17), (1.50, -16.7), (1.60, -15.5), (PCHUN_LEN, -15.5)]) / 20)
    # 奇数の 倍音の 強さ（1＝ぜんぶ 同じ・小さい＝1オクターブ 上に 聞こえる）：見本は 時々 偶数 だけに なる
    odd = _interp(tt, [(0.0, 1), (0.39, 1), (0.42, 0.12), (0.46, 0.12), (0.50, 0.9), (0.58, 0.9), (0.64, 0.14), (0.84, 0.14), (0.88, 0.85), (1.56, 0.85), (1.61, 0.2), (PCHUN_LEN, 0.2)])
    # 倍音が どれだけ 開いて いるか（0＝もとの 音 だけ・1＝ぜんぶ）：チュの 間は ほぼ もとの 音 だけ → 0.15秒から 開く
    opn = _interp(tt, [(0.0, 0.08), (0.12, 0.12), (0.15, 0.8), (0.19, 1.0)])
    def H(f):                                        # 周波数の 形（dB）：450〜4500Hz は 同じ 強さ・下は 少し 弱い・上は 急に 弱い（見本：5〜10kHz は 2〜5kHz の −10〜−12dB）
        return 10 ** (np.interp(f, [0, 300, 450, 600, 2000, 2600, 4500, 5500, 7000, 9000, 11000, 14000], [-6, -3, 0, 2, 2, 0, 0, -13, -19, -28, -40, -80]) / 20)
    def H0(f):                                       # 0.3秒 までは 上の 方も 強い（見本：倍音の 線が 5〜10kHz を 通る）
        return 10 ** (np.interp(f, [0, 300, 450, 600, 2000, 2600, 4500, 5500, 7000, 9000, 11000, 14000], [-6, -3, 0, 2, 2, 0, 0, -6, -9, -15, -26, -80]) / 20)
    early = _interp(tt, [(0.0, 1), (0.27, 1), (0.33, 0), (9, 0)])
    two = 10 ** (_interp(tt, [(0.0, 0), (0.36, 0), (0.39, 6), (0.46, 6), (0.49, 0), (9, 0)]) / 20)      # 0.38〜0.47秒：2つめの 倍音が 強い（見本の 1150Hz の 明るい 線）
    tone = np.zeros(len(tt)); sq = np.zeros(len(tt))
    for kh in range(1, 40):
        fk = kh * f0
        if fk.min() > 12500: break
        g = (H(fk) * (1 - early) + H0(fk) * early) * (1.0 if kh == 1 else opn) * (1.0 if kh % 2 == 0 else odd if kh > 1 else np.maximum(odd, 0.35)) * (two if kh == 2 else 1.0)
        # ざらつき：倍音 1本ずつ 大きさが 細かく ゆれる（見本の 線は つぶつぶ：±5dB ほど・1秒に 10〜20回）。ゆっくりした 乱数を なめらかに つないで 作る
        nj = len(tt) // 1470 + 3; wob = 10 ** (np.interp(np.arange(len(tt)) / 1470.0, np.arange(nj), rng.normal(0, 4.5, nj)) / 20)
        tone += g * wob * np.sin(kh * phi + rng.uniform(0, 2 * np.pi)); sq += g ** 2
    tone *= E / np.sqrt(np.maximum(sq, 1e-9))        # 倍音の 合計の 大きさを E に そろえる
    grit = amb.bp(rng.normal(0, 1, len(tt)), 450, 4600, 2); grit *= 0.42 * E / np.sqrt(np.mean(grit ** 2))      # 倍音の 間を うめる ざらざら（音の 大きさに ついて 動く・−7.5dB）
    tone += grit * _interp(tt, [(0.0, 0.3), (0.13, 1.0), (9, 1.0)])
    k = int(0.022 * SR); tone[-k:] *= np.linspace(1, 0, k) ** 1.5                                              # ぷつっと 切れる（0.02秒）
    put(out, tone, 0.075)
    put(out, 0.012 * amb.bp(rng.normal(0, 1, b), 5000, 11000, 2) * np.minimum(1, t[:b] / 0.1) * np.minimum(1, np.maximum(0, PCHUN_LEN - t[:b]) / 0.03), 0.0)      # うすい ざらざら（上の 方）
    # --- こだま（0.355秒 おくれ・−14dB：くり返す）---
    d = int(ECHO[0] * SR); y = out.copy()
    for i in range(1, 6): y[i * d:] += out[:n - i * d] * ECHO[1] ** i
    return amb.lp(y, 12000, 2)


def choir(freqs, dur, att=0.25, rel=0.5, rng=None):
    """光の 和音（アー：声の ような ゆれる 音）"""
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for f in freqs:
        for d in (0.994, 1.0, 1.007):
            vib = 1 + 0.004 * np.sin(2 * np.pi * (5.1 + 0.6 * d) * t + 7 * d)
            ph = 2 * np.pi * np.cumsum(f * d * vib) / SR
            for h, a in ((1, 1.0), (2, 0.5), (3, 0.34), (4, 0.16), (5, 0.1)): y += a * np.sin(h * ph + h * d)
    fm = sum(amb.bp(y, c - w, c + w, 2) * g for c, w, g in ((800, 180, 1.0), (1150, 200, 0.7), (2900, 400, 0.35)))      # ア の 口の 形
    return fm * np.minimum(1, t / att) * np.minimum(1, np.maximum(0, dur - t) / rel)


def shing(rng, f=3200, dur=0.5):
    """シャキーン（金属の 光る 音 ＋ 短い 風）"""
    n = int(dur * SR); t = np.arange(n) / SR
    y = modes([f, f * 1.504, f * 2.01, f * 2.76, f * 3.4], [1.0, 0.7, 0.6, 0.4, 0.3], [0.20, 0.16, 0.13, 0.1, 0.08], dur, 0.002)
    nz = amb.bp(rng.normal(0, 1, n), 2500, 9000, 2) * np.minimum(1, t / 0.012) * np.exp(-t / 0.07)
    return y / max(1e-9, np.abs(y).max()) + 0.6 * nz / max(1e-9, np.abs(nz).max())


def thump(rng, f=70, dur=0.5):
    """ドン（カットの 重さ）"""
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f + 2.2 * f * np.exp(-t / 0.03)) / SR
    return np.tanh(2.2 * np.sin(ph)) * np.minimum(1, t / 0.003) * np.exp(-t / 0.16) + 0.5 * amb.bp(rng.normal(0, 1, n), 200, 1800, 2) * np.exp(-t / 0.035)


def heaven_snd(rng):
    C = FILM['cuts']; TX = FILM['text']; n = int((FILM['len'] + 0.9) * SR); out = np.zeros(n)
    # 光の 和音（ミの 明るい 和音：ミ・ソ♯・シ・上の ミ）：場面の はじめから。カットごとに 1だん 上がる（ぜんぶが 見える 場面が いちばん 高い）
    put(out, 0.30 * choir([329.6, 415.3, 493.9, 659.3], C[0] + 0.25, 0.10, 0.3), 0.0)
    put(out, 0.30 * choir([370.0, 466.2, 554.4, 740.0], C[1] - C[0] + 0.2, 0.05, 0.25), C[0])
    put(out, 0.31 * choir([415.3, 523.3, 622.3, 830.6], C[2] - C[1] + 0.2, 0.05, 0.25), C[1])
    put(out, 0.34 * choir([466.2, 587.3, 698.5, 932.3], TX - C[2] + 0.3, 0.04, 0.3), C[2])
    # 上って いく ハープ（「40」が 降りて くる 間）
    hs = [659.3, 830.6, 987.8, 1318.5, 1661.2, 1975.5, 2637.0, 3322.4]
    for i, f in enumerate(hs):
        put(out, 0.16 * modes([f, f * 2.0, f * 3.01], [1.0, 0.35, 0.12], [0.5, 0.3, 0.2], 0.9, 0.002), 0.03 + 0.045 * i)
    put(out, 0.22 * thump(rng, 60, 0.4), 0.33)                                             # 「40」が 着く（0.33秒）
    # きらきら（ずっと：高い 鈴）
    for i in range(22):
        put(out, rng.uniform(0.02, 0.05) * modes([rng.uniform(3800, 7600)], [1.0], [rng.uniform(0.08, 0.2)], 0.45), rng.uniform(0.05, FILM['len'] - 0.1))
    # カット（00・0P）：シャキーン ＋ ドン。だんだん 高く
    for i, tc in enumerate(C[:2]):
        put(out, 0.20 * shing(rng, 2900 + 450 * i), tc); put(out, 0.30 * thump(rng, 66 + 6 * i), tc)
    # ぜんぶが 見える 場面（1.5秒）：ドーン（重い 音 ＋ 低い 鐘の ような うなり）＋ 長い シャキーン
    put(out, 0.26 * shing(rng, 2400, 0.8), C[2]); put(out, 0.50 * thump(rng, 54, 0.7), C[2])
    put(out, 0.22 * modes([110.0, 164.8, 220.0, 329.6, 440.0], [1.0, 0.8, 0.7, 0.5, 0.3], [0.5, 0.42, 0.36, 0.28, 0.2], 0.9, 0.004), C[2])
    # テデーンへ 上がって いく 音（1.52 → 1.97秒）
    m = int(0.45 * SR); tm = np.arange(m) / SR
    put(out, 0.09 * amb.bp(rng.normal(0, 1, m), 900, 7000, 2) * (tm / 0.45) ** 2.2 * np.minimum(1, np.maximum(0, 0.45 - tm) / 0.02), TX - 0.45)
    ph = 2 * np.pi * np.cumsum(440 * 2 ** (1.6 * (tm / 0.45) ** 1.5)) / SR
    put(out, 0.045 * np.sin(ph) * (tm / 0.45) ** 2 * np.minimum(1, np.maximum(0, 0.45 - tm) / 0.02), TX - 0.45)
    return amb.lp(out, 11000, 2)


def brass(f, dur, tau, bright=1.0):
    """金管の ような 太い 音（出だしで 下から ぐっと 上がる）"""
    n = int(dur * SR); t = np.arange(n) / SR; bend = 2 ** (-2.0 / 12 * np.exp(-t / 0.02)); y = np.zeros(n)
    for d in (0.994, 1.0, 1.006):
        ph = 2 * np.pi * np.cumsum(f * d * bend) / SR
        for h in range(1, 14):
            if f * h > 6500: break
            y += np.sin(h * ph + 0.3 * h) / h ** (1.15 / bright) * (1 - (0.6 * np.exp(-t / 0.035) if h > 3 else 0))
    return y * np.minimum(1, t / 0.010) * np.exp(-np.maximum(0, t - 0.06) / tau) * np.minimum(1, np.maximum(0, dur - t) / 0.04)


def tedeen_snd(rng):
    """テ・デーン！：テ（短い 和音：0秒）→ デーン（長い 和音：0.17秒）＋ 太鼓・シンバル・鈴"""
    T2 = 0.17; out = np.zeros(int(2.7 * SR))
    for f, a in ((392.0, 1.0), (493.9, 0.7), (587.3, 0.6), (196.0, 0.7)):                 # テ（ソ・シ・レ）
        put(out, 0.5 * a * brass(f, 0.15, 0.3), 0.0)
    for f, a in ((523.3, 1.0), (659.3, 0.75), (784.0, 0.7), (1046.5, 0.55), (261.6, 0.8), (130.8, 0.6)):      # デーン（ド・ミ・ソ・上の ド ＋ 下の ド）
        put(out, 0.5 * a * brass(f, 2.2, 0.75, 1.1), T2)
    put(out, 0.32 * thump(rng, 62, 0.4), 0.0); put(out, 0.5 * thump(rng, 52, 0.9), T2)
    k = int(2.0 * SR); tk = np.arange(k) / SR; nz = rng.normal(0, 1, k)
    put(out, 0.22 * amb.hp(amb.bp(nz, 3000, 12000, 2), 2500, 2) * np.minimum(1, tk / 0.004) * (0.7 * np.exp(-tk / 0.12) + 0.3 * np.exp(-tk / 0.7)), T2)      # シンバル
    put(out, 0.22 * choir([523.3, 659.3, 784.0, 1046.5], 2.2, 0.06, 1.2), T2)             # うしろの 光の 和音
    for i, f in enumerate([2093.0, 2637.0, 3136.0, 4186.0, 5274.0, 4186.0, 6272.0]):      # 鈴（きらきら 上へ）
        put(out, 0.07 * modes([f, f * 2.01], [1.0, 0.3], [0.35, 0.2], 0.8), T2 + 0.10 + 0.07 * i)
    y = amb.lp(out, 11000, 2); y = 1.8 * y / np.abs(y).max(); a = np.abs(y); kk = 0.5      # 重なって 高く なった 山 だけ やわらかく おさえる
    return np.sign(y) * np.where(a <= kk, a, kk + (1 - kk) * np.tanh((a - kk) / (1 - kk)))


def render():
    """→ { 名前: (2, n) の 音 }（アプリの ファイルの 名前：tc_se_gk_<名前>.m4a）"""
    import loud
    rng = np.random.default_rng(175); S = {}
    S['pchun'] = amb.place(pchun_snd(rng), 0.0, 0.5 * 1.41, 0.03, wet0=0.04)
    S['heaven'] = amb.place(heaven_snd(rng), 0.0, 0.4 * 1.41, 0.08, wet0=0.22)
    S['tedeen'] = amb.place(tedeen_snd(rng), 0.0, 0.5 * 1.41, 0.06, wet0=0.16)
    out = {}
    for k, y in S.items():
        y = y * 10 ** ((GB[k] - loud.dba(y, SR)) / 20); assert np.abs(y).max() <= PEAK_MAX, (k, float(np.abs(y).max()))
        a = np.abs(y).max(0); nz = np.nonzero(a > 1e-4)[0]
        y = y[:, :min(y.shape[1], nz[-1] + int(0.06 * SR))].copy()
        m = min(int(0.02 * SR), y.shape[1]); y[:, -m:] *= np.linspace(1, 0, m)
        out[k] = y
    return out


if __name__ == '__main__':
    D = sys.argv[1]; os.makedirs(D, exist_ok=True); wav = len(sys.argv) > 2 and sys.argv[2] == 'wav'
    only = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    tmp = tempfile.mkdtemp()
    for k, y in render().items():
        if only and k not in only: continue
        w = os.path.join(D if wav else tmp, f'tc_se_gk_{k}.wav'); wavfile.write(w, SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
        if not wav:
            o = os.path.join(D, f'tc_se_gk_{k}.m4a')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', w, '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', o], check=True)
        print(k, round(y.shape[1] / SR, 2), '秒', 'peak', round(float(np.abs(y).max()), 3), '' if wav else f'{os.path.getsize(o)} B', flush=True)
