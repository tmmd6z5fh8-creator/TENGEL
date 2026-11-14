# テンゲルBGM と 神様馬が 出て いる 間の BGM（第4.171版・まさちゃん 2026/11/14 16:18）
#   「②テンゲルのBGMを考える
#     ・テンゲルBGM(トレーニングセンター、思い出フィギュア、作戦会議、推し馬の画面では流れない)
#     ・トレーニングセンターの神様馬出現中のBGM:もっとアップテンポで掻き立てられるようなBGM」
#   ぜんぶ 計算で 作る（録音・素材・ほかの 曲は 使わない＝姫の 作曲）。つなぎ目なく くり返せる（音の のこり と ひびき は 頭へ まわす：輪の ように）。
#
#   ■ テンゲルBGM（tengel）：判定・記録・実測・設定の 画面で 流す（bgm.js）。数字を 入れながら ずっと 聞ける、明るくて 前向きな 曲
#     ニ長調・108 BPM・24小節（約53.3秒）＝ A（8）→ A'（8）→ B（8）。和音は「王道進行」（G△7 → A7 → F#m7 → Bm7）から 主和音へ
#     ・ふし：ビブラフォン（やわらかい 鉄琴）。A' だけ 口笛の ような 音が 重なる・長い 音の 上で 小さく 鈴（グロッケン）
#     ・エレピ（うらで きざむ）・やわらかい 弦・指で はじく ベース・軽い ドラム（キック・リム・ハイハット・シェイカー）・B は マリンバの 分散和音
#     大きさ：全体 −26dB・山は −12dB まで（的中の 演出の 音〈山 −2〜−7dB〉より ずっと 小さい＝うしろで 鳴る 音）
#
#   ■ 神様馬の BGM（divine2）：神様馬フィールドの 間（tc_app.js の AMB.divine）。アップテンポで 掻き立てられる 曲
#     まさちゃん 11/14 17:08「神様馬のBGMもう少しカッコよく！もう少し神様ぽさを混ぜて！」で 作り直した（第2稿）：
#     ホ短調・156 BPM・32小節（約49.2秒）＝ A1（8：降臨 → 勇ましい 主題）→ A2（8：主題に ハモリ・合唱の 掛け声・オルガン）→ B（8：神々しい 所：半分の 速さの 感じ）→ C（8：山場・さいごは ホ長調の 光）
#     ・カッコよく：キックと ベースが「ダッダダ」と 走る（馬の ギャロップ）＋ 低い 金管が いっしょに 刻む リフ・A2 と C は 合唱の 掛け声が「3・3・2」の リズム・
#       区切りは 全員で 同じ リズムを 打つ「キメ」（16小節め と さいごの 小節）・太鼓の おかず・弦の 駆け上がり・金管は 長い 音の 入りで 下から しゃくる
#     ・神様っぽさ：パイプオルガン（頭の 降臨の 和音・A2 は 16分の 分散和音・B と C は 和音を のばす）・合唱（アー：前より 大きく・B と C は ふしを ソプラノが 歌う）・
#       教会の 鐘・ハープ（B の 分散和音・区切りの 駆け上がり）・きらきら（ウィンドチャイム・鈴）・B は ひびきを 長く（大聖堂の ような ひびき）
#     ・金管の ふし（トランペットの 高さ ＋ 下に ホルン ＋ 上に 高い 弦）・弦の きざみ（16分）・ティンパニ・シンバル・さいごの 小節は スネアの ロールで 頭へ
#     大きさ：全体 −28dB・山は −14dB まで（前の 神様馬の BGM は −36dB＝やさしく。こんどは はっきり 聞こえる 大きさ：お世話の 音〈山 −15dB〉は うもれない）
#
#   ■ テンゲルBGM の 第2稿（tengel2＝nodoka）：まさちゃん 11/14 17:49「テンゲルのBGMは、この動画の背景で流れているBGMが理想！まずは、同じやつを作ってみて！その後、アレンジしよう！」
#     → 動画の 曲（ゲームの 村の BGM の ような 曲：ほかの 人が 作った 曲）と 同じ ものは 作らない（著作権）。その 曲の「ふんいき」だけ ＝ ゆったり・あたたかい・のどかな 村の 感じ を
#       もらって、姫が 新しく 作った 曲（ふし・和音の ならび・リズムの 形は 姫の もの）
#     ト長調・116 BPM（1小節を 2つに 感じる ゆったりした ノリ）・24小節（約49.7秒）＝ A（8）→ A'（8）→ B（8）
#     ・ふし：笛（オカリナの ような やわらかい 音）。A' は 下に もう 1本・B は 鈴が 重なる
#     ・ポロンと 弾く 弦の 分散和音（3・3・2 の ノリ）・低い 太鼓（1拍め・2拍めの うら・4拍め）・シャラシャラ（シェイカー）・やわらかい 弦・指で はじく ベース・B は マリンバ・区切りに 雨の 棒（レインスティック）
#     大きさ：全体 −26dB・山は −12dB まで（第1稿と 同じ）
#
#   ■ テンゲルBGM の 第3稿（tengel3＝nodoka(88, 笛, 鳥)）：まさちゃん 11/14 18:49「BGMもっとゆっくりで、鳥の声や笛の音入れて！」
#     第2稿と 同じ 曲を、もっと ゆっくり（116 → 88 BPM・24小節・約65.5秒）・ふしは 息の 入った 笛（竹の 横笛の ような 音：長い 音の 入りに かざりの 音）・オカリナは 下で よりそう・
#     鳥の 声（ピチチチ・チュン チュン・ヒー ヨ・遠くで ホー… ：3〜5秒に 1回・計算で 作った 声）
#
#   ■ テンゲルBGM の 第4稿（tengel4＝yuttari）：まさちゃん 11/14 19:09「一回、鳥の声と笛の音だけにしてみて！もっとゆったりで！」
#     鳴るのは 笛 1本 と 鳥の 声 だけ（太鼓・弦・ベース・シャラシャラ・雨の 棒・オカリナは なし）。ト長調の 5つの 音（ソ ラ シ レ ミ）・60 BPM（1拍＝1秒）・16小節（64秒）
#     ・笛：ひと息（約10〜13秒）を 切らずに つなげて 吹く（fue_line：音と 音の 間は すべらせる・長い 音は ふくらんで ゆれる・ひと息の さいごは ゆっくり 小さく）→ 3〜4.5秒 休む ×4
#     ・鳥：笛が 休んで いる 間は 近くの 鳥が 鳴いて、反対側の 鳥が 答える・笛が 鳴って いる 間は 遠くで 小さく。
#       声は 第3稿の 4つ（ピチチチ・チュン チュン・ヒー ヨ・ホー…）＋ 空の 高い 所の「ピー ヒョロロロ」＋「ツツピー ツツピー」
#     ・ひびきを 長く（谷に ひびく 感じ）
#
#   ■ テンゲルBGM の 第5稿（tengel5＝yuttari(True)）：まさちゃん 11/14 19:25「ここに馬の走る音と、もう少し太い音の笛を混ぜて！ゆったりね！」
#     第4稿（笛 と 鳥の 声・60 BPM・16小節・64秒）に 2つ 足す：
#     ・太い 音の 笛（fue_line の thick：低い 所〈1オクターブ下 あたり〉・倍音が 多い・息の 音は 少なく・ゆれは ゆっくり）。
#       1つめの ひと息＝いままでの 笛が ふし／太い 笛は 下で のばす → 2つめ＝太い 笛が ふし（1オクターブ下）／いままでの 笛は 上で そっと 重なる
#       → 3つめ＝いままでの 笛が ふし／太い 笛が 下で ハモる → 4つめ（おわりの ひと息）＝太い 笛が ふし／さいごの 音に いままでの 笛が 上で 重なる
#     ・馬の 走る 音（canter：ゆったりした かけ足「パカラッ … パカラッ」1歩 2/3秒＝3歩で 2拍）。遠くから 走って きて、前を 通って、遠くへ（約22秒：はっきり 聞こえるのは まん中の 12秒 くらい）を 2回：
#       1回め＝左から 右へ（いちばん 近いのは 13.5秒：1つめの 休み）・2回め＝右から 左へ（46.5秒：3つめの 休み）。土の 地面を うつ 音（低い ドッ ＋ ポクッ ＋ 土の ザッ）
#
#   ■ テンゲルBGM の 第6稿（tengel6＝yuttari(6)）：まさちゃん 11/14 19:41「もう一段階太い笛と、かなり音が低い笛も重ねて音入れて！」
#     第5稿（笛 2本・鳥の 声・馬の 走る 音）に 笛を 2本 重ねる（ぜんぶで 笛 4本・速さと 長さは 同じ）：
#     ・もう 一段階 太い 笛（fue_line の 音色 2：倍音が もっと 多い・1オクターブ下の 音を 少し まぜる・息の 音は 少なく・入りは ゆっくり）：
#       ふしを 1オクターブ下で なぞる（1つめ・3つめ・4つめの ひと息）／2つめは 太い 笛と 同じ 高さで 重なる（2本で 1本の 太い 音に 聞こえる）
#     ・かなり 低い 笛（音色 3：ファの 下の レ〈147Hz〉〜 シ〈247Hz〉・倍音を 多く ＝ 電話の スピーカーでも 高さが わかる）：ひと息ごとに 3〜4つの 長い 音で 下を ささえる
#       （ソ → ミ → ソ／ミ → ソ → ミ／ソ → シ → ラ → ミ／ミ → レ → ソ）
#     まさちゃん 11/14 19:42「馬の鳴き声と、馬が走る音追加して！」も 第6稿に 入れる：
#     ・馬の 鳴き声（neigh：ヒヒーン＝高い 声で 入って、ふるえながら 低く なって、さいごは ブルルッ）：2つめの 休み（28.4秒・右の 方）と 4つめの 休み（59.9秒・左の 遠く・少し 低い 声で 短く）
#     ・馬の 走る 音を 足す：第5稿の 2回（1つめ・3つめの 休み：近くを 通る）を 3dB 大きく ＋ もう 1頭（少し 速い 足・低い 音・遠め）が 2つめ・4つめの 休みに 通る ＝ 休みごとに 馬が 通る
#
#   ■ テンゲルBGM の 第7稿（tengel7＝yuttari(7)）：まさちゃん 11/14 19:57「この笛を、バイオリンぽくできる？」
#     第6稿と 同じ ふし・同じ 重ね方（4本）・同じ 鳥と 馬。4本の 音を 弓で ひく 弦の 音に（vn_line）：
#     いままでの 笛 → バイオリン／太い 笛 → 少し 低い バイオリン（ビオラの ような 音）／もう 一段階 太い 笛・かなり 低い 笛 → チェロの ような 音
#     ・弦の 音の 作り方：倍音が たくさん ある 音（のこぎり波：大きく ひくほど 明るい）＋ 弓が こする ざらつき → 楽器の 胴の ひびき（バイオリンは 285・470・560Hz と 2.6kHz あたりが 強い）を つける
#     ・ひき方：音と 音の 間は 指を すべらせて つなぐ（笛より ゆっくり）・長い 音は 0.3秒 たって から ゆれる（1秒に 6回 くらい・笛より 深い）・弓の 入りは やわらかく
#
#   ■ テンゲルBGM の 第8稿（tengel8＝yuttari(8)）：まさちゃん 11/14 20:12「ごめん！笛に戻して！もっとゆったりで！」・20:15「あと風の音も入れて！」
#     第6稿（笛 4本・鳥の 声・馬の 鳴き声と 走る 音）に もどして、
#     ・もっと ゆったり：60 → 48 BPM（1拍＝1.25秒）・16小節＝80秒。笛の ひと息は 約12.5〜16秒・休みは 約4〜5.5秒。馬の 足も ゆっくり（1歩 0.72秒・遠くの 馬は 0.65秒）
#     ・風の 音（wind_gust：そよ風が 草や 木の 葉を わたる「サァー…」＋ 風の 通る「ヒュゥ…」。ゆっくり 強く なって ゆっくり やむ・左右に 流れる）：
#       笛の ひと息が おわる ころ から 吹いて、休みの はじめに いちばん 強く、休みの 間に やむ（4回：約9.5秒ずつ）＋ ひと息の とちゅうに 弱い 風（2回）＋ ずっと うしろで ごく 小さく
#
#   ■ テンゲルBGM の 第9稿（tengel9＝yuttari(9)）：まさちゃん 11/14 20:27「もっと笛の音ゆっくりして！」
#     第8稿と 同じ 音（笛 4本・鳥・馬・風）で、笛を もっと ゆっくり：
#     ・48 → 36 BPM（1拍＝約1.67秒）・16小節＝約106.7秒。笛の 音 1つ 1つが 第8稿の 1.33倍の 長さ（短い 音でも 0.83秒・長い 音は 5〜6.7秒）・休みは 約5.3〜7.5秒
#     ・笛の 吹き方も ゆっくり（fue_line の slow）：かざりの 音（すばやく 入る 音）は なし・音から 音へ 移る ときは もっと なめらかに・吹きはじめは もっと やわらかく・ゆれは 少し ゆっくり
#     ・休みが 長く なる ぶん、鳥の 声の ならびを 足す
#
#   python3 bgm_tengel.py <tengel|divine2|tengel2|tengel3|tengel4|tengel5|tengel6|tengel7|tengel8|tengel9> <出す wav>     （アプリ用の m4a は export_app.py：bgm_tengel.m4a・tc_bgm_divine2.m4a）
import math, os, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amb
SR = amb.SR
TAU = 2 * np.pi


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)


class Song:
    """1曲ぶんの きまり（速さ・小節の 数）と 音の 置き場"""
    def __init__(self, bpm, bars, tail=4.0):
        self.bpm = bpm; self.beat = 60.0 / bpm; self.bar = 4 * self.beat; self.bars = bars; self.loop = bars * self.bar
        self.n = int(round(self.loop * SR)); self.tailn = int(tail * SR)

    def stem(self): return Stem(self)
    def at(self, bar, beat=0.0): return bar * self.bar + beat * self.beat


class Stem:
    """音の 置き場（ループ ＋ のこり）。fold() で のこりを 頭へ まわす"""
    def __init__(self, s): self.s = s; self.b = np.zeros((2, s.n + s.tailn))

    def put(self, x, at, pan=0.0, gain=1.0):
        x = np.asarray(x) * gain; i = int(round(at * SR)) % self.s.n
        st = np.stack([x * math.sqrt((1 - pan) / 2), x * math.sqrt((1 + pan) / 2)])
        while st.shape[1] > 0:
            m = min(st.shape[1], self.b.shape[1] - i); self.b[:, i:i + m] += st[:, :m]; st = st[:, m:]; i = 0

    def put2(self, st, at, gain=1.0):
        """ステレオの 音（2, n）を そのまま 置く"""
        st = np.asarray(st) * gain; i = int(round(at * SR)) % self.s.n
        while st.shape[1] > 0:
            m = min(st.shape[1], self.b.shape[1] - i); self.b[:, i:i + m] += st[:, :m]; st = st[:, m:]; i = 0

    def fold(self):
        n = self.s.n; y = self.b[:, :n].copy(); rest = self.b[:, n:]
        y[:, :rest.shape[1]] += rest; return y


# ---------------------------------------------------------------- 音の もと
def fade(y, a=0.004, r=0.01):
    ka = max(1, min(len(y) // 2, int(a * SR))); kr = max(1, min(len(y) - ka, int(r * SR)))
    y = y.copy(); y[:ka] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ka)); y[len(y) - kr:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, kr)); return y


def adsr(n, a, d, s, r):
    """立ち上がり a 秒 → d 秒で s まで 下がる → おわりの r 秒で 消える"""
    e = np.full(n, float(s)); ka = max(1, int(a * SR)); kd = max(1, int(d * SR)); kr = max(1, int(r * SR))
    ka = min(ka, n); e[:ka] = np.linspace(0, 1, ka)
    kd = min(kd, max(0, n - ka)); e[ka:ka + kd] = 1 + (s - 1) * (1 - np.exp(-4 * np.linspace(0, 1, kd))) / (1 - math.exp(-4)) if kd else e[ka:ka + kd]
    kr = min(kr, n); e[n - kr:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, kr))
    return e


def saw(f, n, fmax=6000.0, tilt=1.0, ph0=0.0):
    """のこぎり波（倍音を 足して 作る：折り返しの 雑音が 出ない）。f は 数 か 1サンプルごとの 列・fmax より 上の 倍音は 入れない・tilt＝倍音の 落ち方（1 で のこぎり）"""
    fa = np.full(n, float(f)) if np.isscalar(f) else np.asarray(f, float)
    ph = TAU * np.cumsum(fa) / SR + ph0; k_max = max(1, int(min(fmax, SR * 0.45) / float(fa.max())))
    y = np.zeros(n)
    for k in range(1, k_max + 1): y += np.sin(k * ph) / k ** tilt
    return y * (2 / np.pi)


def square(f, n, fmax=5000.0):
    fa = np.full(n, float(f)); ph = TAU * np.cumsum(fa) / SR; k_max = max(1, int(min(fmax, SR * 0.45) / f)); y = np.zeros(n)
    for k in range(1, k_max + 1, 2): y += np.sin(k * ph) / k
    return y * (4 / np.pi)


def vib(f, n, rate, depth, delay):
    """ビブラート（delay 秒 たって から だんだん かかる）"""
    t = np.arange(n) / SR; k = np.clip((t - delay) / 0.25, 0, 1)
    return f * (1 + depth * k * np.sin(TAU * rate * t))


# ---- 打楽器
def kick(f0=118.0, f1=47.0, dec=0.11, click=0.5, drive=1.0):
    n = int(0.34 * SR); t = np.arange(n) / SR; f = f1 + (f0 - f1) * np.exp(-t / 0.03)
    y = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t / dec)
    y[:int(0.004 * SR)] += click * np.hanning(2 * int(0.004 * SR))[int(0.004 * SR):]
    if drive != 1.0: y = np.tanh(y * drive) / math.tanh(drive)
    return fade(y, 0.0015, 0.03)


def rim(rng):
    n = int(0.07 * SR); t = np.arange(n) / SR
    y = 0.8 * amb.bp(rng.normal(0, 1, n), 1500, 5200, 2) * np.exp(-t / 0.012) + 0.7 * np.sin(TAU * 820 * t) * np.exp(-t / 0.018) + 0.3 * np.sin(TAU * 1730 * t) * np.exp(-t / 0.01)
    return fade(y, 0.0008, 0.01)


def snare(rng, dec=0.11, body=190.0, bright=7000.0):
    n = int((dec * 3 + 0.05) * SR); t = np.arange(n) / SR
    y = amb.bp(rng.normal(0, 1, n), 220, bright, 2) * np.exp(-t / dec) + 0.55 * np.sin(TAU * body * t) * np.exp(-t / 0.035) + 0.3 * np.sin(TAU * body * 1.72 * t) * np.exp(-t / 0.025)
    return fade(y, 0.001, 0.02)


def hat(rng, dec=0.03, f=7200.0):
    n = int((dec * 4 + 0.02) * SR); t = np.arange(n) / SR
    return fade(amb.hp(rng.normal(0, 1, n), f, 2) * np.exp(-t / dec), 0.0008, 0.01)


def shaker(rng, dur=0.07):
    n = int(dur * SR); e = np.hanning(n) ** 1.5; e[:n // 3] *= np.linspace(0.2, 1, n // 3)
    return amb.bp(rng.normal(0, 1, n), 4500, 10500, 2) * e


def crash(rng, dec=0.9):
    n = int((dec * 3.2) * SR); t = np.arange(n) / SR; x = amb.hp(rng.normal(0, 1, n), 3800, 2)
    for fq in (3140.0, 4270.0, 5330.0, 6820.0, 8410.0): x += 0.25 * np.sin(TAU * fq * t + rng.uniform(0, 6))
    return fade(x * (0.25 * np.exp(-t / 0.05) + np.exp(-t / dec)), 0.002, 0.2)


def timpani(m, dec=0.75):
    n = int(dec * 3 * SR); t = np.arange(n) / SR; f = mtof(m) * (1 + 0.04 * np.exp(-t / 0.03)); ph = TAU * np.cumsum(f) / SR
    y = (np.sin(ph) + 0.5 * np.sin(1.5 * ph) * np.exp(-t / 0.3) + 0.3 * np.sin(1.99 * ph) * np.exp(-t / 0.2)) * np.exp(-t / dec)
    y[:int(0.02 * SR)] += 0.5 * amb.lp(np.random.default_rng(int(m)).normal(0, 1, int(0.02 * SR)), 900, 2) * np.linspace(1, 0, int(0.02 * SR))
    return fade(y, 0.002, 0.1)


# ---- 音の 高さの ある 楽器
def ebass(m, dur, bright=620.0):
    """指で はじく ベース"""
    n = int((dur + 0.06) * SR); t = np.arange(n) / SR; f = mtof(m)
    y = 0.75 * np.sin(TAU * f * t) + 0.5 * amb.lp(saw(f, n, 2200), bright, 2)
    e = np.exp(-t / max(0.12, dur * 1.1)); e[t > dur] *= np.exp(-(t[t > dur] - dur) / 0.02)
    return fade(y * e, 0.004, 0.02)


def gbass(m, dur):
    """走る ベース（のこぎり＋四角・すばやく はじく・少し ひずませる）"""
    n = int((dur + 0.04) * SR); t = np.arange(n) / SR; f = mtof(m)
    y = 0.7 * saw(f, n, 2600) + 0.35 * square(f, n, 1800) + 0.5 * np.sin(TAU * f * t)
    y = amb.lp(y, 520 + 1500 * np.exp(-1.0), 2) * (0.35 + 0.65 * np.exp(-t / 0.07))
    e = np.ones(n); e[t > dur] = np.exp(-(t[t > dur] - dur) / 0.012)
    return fade(np.tanh(1.4 * y * e) / 1.1, 0.003, 0.012)


def epiano(m, dur):
    """エレピ（FM：金属の 棒を たたく 音 ＋ 弱い 鈴の 成分）"""
    n = int((dur + 0.5) * SR); t = np.arange(n) / SR; f = mtof(m)
    idx = 1.6 * np.exp(-t / 0.35) + 0.25
    y = np.sin(TAU * f * t + idx * np.sin(TAU * f * t)) + 0.07 * np.sin(TAU * 14 * f * t) * np.exp(-t / 0.04) * (14 * f < 16000)
    e = np.exp(-t / 0.9); e[t > dur] *= np.exp(-(t[t > dur] - dur) / 0.12)
    return fade(y * e, 0.003, 0.05)


def pad_note(m, dur, cut=1700.0):
    """やわらかい 弦（少し ずらした のこぎり 3つ・ゆっくり 立ち上がる）"""
    n = int((dur + 0.6) * SR); f = mtof(m); y = np.zeros(n)
    for i, d in enumerate((-0.07, 0.0, 0.08)): y += saw(f * 2 ** (d / 12), n, 3200, 1.15, ph0=1.7 * i)
    e = np.ones(n); a = int(0.35 * SR); e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a)); r = int(0.6 * SR); e[n - r:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return amb.lp(y, cut, 2) * e / 3


def whistle(m, dur, rng):
    """口笛・フルートの ような やわらかい ふしの 音"""
    n = int((dur + 0.09) * SR); t = np.arange(n) / SR; f = vib(mtof(m), n, 5.4, 0.0045, 0.22)
    f = f * (1 - 0.012 * np.exp(-t / 0.035))                                    # 入りで 少し 下から
    ph = TAU * np.cumsum(f) / SR
    y = np.sin(ph) + 0.16 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    br = amb.bp(rng.normal(0, 1, n), max(200.0, mtof(m) * 0.9), min(9000.0, mtof(m) * 2.6), 1) * 0.05      # 息の 音（少し）
    e = adsr(n, 0.035, 0.12, 0.82, 0.09)
    return (y + br) * e


def vibe(m, dur):
    """ビブラフォン（やわらかい ばちで たたく 鉄琴：ふわっと ゆれて 消える）"""
    n = int((dur + 0.9) * SR); t = np.arange(n) / SR; f = mtof(m)
    y = np.sin(TAU * f * t) + 0.25 * np.sin(TAU * 4 * f * t) * np.exp(-t / 0.08) + 0.08 * np.sin(TAU * 10 * f * t) * np.exp(-t / 0.03) * (10 * f < 18000)
    e = np.exp(-t / 0.75); e[t > dur] *= np.exp(-(t[t > dur] - dur) / 0.2)
    return fade(y * e * (1 + 0.16 * np.sin(TAU * 5.2 * t)), 0.004, 0.05)


def glock(m, dec=0.55):
    n = int(dec * 3.2 * SR); t = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for r_, a_, d_ in ((1.0, 1.0, 1.0), (2.76, 0.35, 0.45), (5.4, 0.18, 0.25), (8.93, 0.06, 0.12)):
        if f * r_ < SR * 0.45: y += a_ * np.sin(TAU * f * r_ * t) * np.exp(-t / (dec * d_))
    return fade(y, 0.002, 0.05)


def marimba(m, dur=0.34):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    y = np.sin(TAU * f * t) * np.exp(-t / 0.12) + 0.28 * np.sin(TAU * 4 * f * t) * np.exp(-t / 0.035) + 0.1 * np.sin(TAU * 10 * f * t) * np.exp(-t / 0.012) * (10 * f < 18000)
    return fade(y, 0.002, 0.02)


def spicc(m, dec=0.1):
    """弦を 弓で 短く はねる 音（きざみ）"""
    n = int((dec * 3 + 0.03) * SR); t = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for i, d in enumerate((-0.06, 0.05)): y += saw(f * 2 ** (d / 12), n, 5200, 1.0, ph0=2.1 * i)
    y = amb.lp(y, 3600, 2); e = (1 - np.exp(-t / 0.006)) * np.exp(-t / dec)
    return fade(y * e, 0.002, 0.02) / 2


def hstr(m, dur, rng):
    """高い 弦（バイオリン：のばす・ビブラート）"""
    n = int((dur + 0.18) * SR); f0 = mtof(m); y = np.zeros(n)
    for i, d in enumerate((-0.08, 0.0, 0.07)): y += saw(vib(f0 * 2 ** (d / 12), n, 5.6 + 0.2 * i, 0.0045, 0.15), n, 7000, 1.05, ph0=rng.uniform(0, 6))
    y = amb.lp(y, 4200, 2); e = adsr(n, 0.07, 0.1, 0.9, 0.18)
    return y * e / 3


def brass(m, dur, rng, hard=1.0, rip=0.0):
    """金管（ずらした のこぎり 3つ・吹きはじめは 明るく あとは 少し 丸く・のばすと ビブラート）。rip＝入りで 下から しゃくる 幅（半音）"""
    n = int((dur + 0.1) * SR); t = np.arange(n) / SR; f0 = mtof(m); y = np.zeros(n)
    for i, d in enumerate((-0.05, 0.0, 0.06)):
        f = vib(f0 * 2 ** (d / 12), n, 5.2, 0.004, 0.3) * (1 - 0.02 * np.exp(-t / 0.02)) * 2 ** (-(rip / 12) * np.exp(-t / 0.04)); y += saw(f, n, 6000, 1.0, ph0=1.3 * i)
    dark, bright = amb.lp(y, 900, 2), amb.lp(y, 3400, 2)
    k = np.clip(0.35 + 0.65 * np.exp(-t / 0.12) * hard + 0.25 * np.clip(t / max(dur, 0.01), 0, 1), 0, 1)      # 明るさ（吹きはじめ・のばした おわりで 少し ふくらむ）
    y = dark * (1 - k) + bright * k
    e = adsr(n, 0.028, 0.1, 0.8, 0.1)
    return y * e / 3


def choir(ms, dur, rng, att=0.22, rel=0.7):
    """合唱「アー」（のこぎりの 重ねを 口の 形の 帯で 通す・ゆっくり 立ち上がる）→ ステレオ。att・rel を 短く すると 掛け声（ハッ）"""
    n = int((dur + rel) * SR); t = np.arange(n) / SR; out = np.zeros((2, n))
    for j, m in enumerate(ms):
        f0 = mtof(m); y = np.zeros(n)
        for i, d in enumerate((-0.09, 0.0, 0.1)):
            f = f0 * 2 ** (d / 12) * (1 + 0.004 * np.sin(TAU * (4.6 + 0.4 * i) * t + rng.uniform(0, 6))); y += saw(f, n, 5000, 1.0, ph0=rng.uniform(0, 6))
        v = 0.55 * amb.bp(y, 600, 1000, 1) + 0.3 * amb.bp(y, 1000, 1500, 1) + 0.22 * amb.bp(y, 2400, 3400, 1) + 0.6 * amb.lp(y, 650, 2)
        pan = (-0.5, 0.5, -0.2, 0.2, 0.0)[j % 5]; out[0] += v * math.sqrt((1 - pan) / 2); out[1] += v * math.sqrt((1 + pan) / 2)
    e = np.ones(n); a = min(n // 2, int(att * SR)); e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a)); r = min(n - a, int(rel * SR)); e[n - r:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return out * e / max(1, len(ms))


def tbell(m, dec=1.6):
    """教会の 鐘（管の 鐘）"""
    n = int(dec * 2.6 * SR); t = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for r_, a_, d_ in ((0.5, 0.25, 1.4), (1.0, 1.0, 1.0), (2.0, 0.6, 0.8), (2.76, 0.4, 0.55), (3.0, 0.3, 0.5), (4.07, 0.22, 0.35), (5.43, 0.15, 0.25), (6.8, 0.08, 0.18)):
        if f * r_ < SR * 0.45: y += a_ * np.sin(TAU * f * r_ * t + 0.3 * r_) * np.exp(-t / (dec * d_))
    return fade(y, 0.003, 0.1)


def riser(rng, dur):
    """上がって いく 風の 音（さいごの 小節）"""
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.normal(0, 1, n); y = np.zeros(n); k = 2048
    for i in range(0, n, k):                                                    # だんだん 高く なる 帯（区切って かける）
        fc = 500 * (9000 / 500) ** (min(1.0, (i + k / 2) / n)); seg = x[max(0, i - k):min(n, i + 2 * k)]
        yy = amb.bp(seg, fc * 0.7, min(fc * 1.4, SR * 0.45), 2); o = i - max(0, i - k); y[i:i + k] = yy[o:o + min(k, n - i)]
    return fade(y * (t / dur) ** 2, 0.05, 0.02)


def organ(m, dur, rng, bright=1.0):
    """パイプオルガン（倍音を 足して 作る：8フィート ＋ 4フィート ＋ 2フィートの 管・ゆれない まっすぐな 音・入りに 息の 音）"""
    n = int((dur + 0.1) * SR); t = np.arange(n) / SR; f0 = mtof(m); y = np.zeros(n)
    for mul, amp in ((1, 1.0), (2, 0.55), (3, 0.3), (4, 0.33), (5, 0.1), (6, 0.14), (8, 0.12 * bright), (10, 0.04 * bright), (12, 0.05 * bright), (16, 0.04 * bright)):
        if f0 * mul < 9000: y += amp * np.sin(TAU * f0 * mul * (1 + rng.uniform(-0.0012, 0.0012)) * t + rng.uniform(0, 6))
    chiff = amb.bp(rng.normal(0, 1, n), min(f0 * 3, 5000.0), min(f0 * 7, 9000.0), 1) * np.exp(-t / 0.018) * 0.5
    e = np.ones(n); a = min(n // 2, int(0.02 * SR)); e[:a] = np.linspace(0, 1, a) ** 0.7; r = min(n - a, int(0.1 * SR)); e[n - r:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return (y + chiff) * e / 2.2


def harp(m, dec=0.8):
    """ハープ（はじく 弦：高い 倍音ほど 早く 消える）"""
    n = int(dec * 2.8 * SR); t = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for k in range(1, 13):
        if f * k > 12000: break
        y += (1.0 / k ** 1.25) * np.sin(TAU * f * k * (1 + 0.0004 * k * k) * t + 0.4 * k) * np.exp(-t / (dec / (1 + 0.55 * (k - 1))))
    return fade(y, 0.002, 0.05)


def tom(rng, f0=95.0, dec=0.28):
    """太鼓（タム：皮の 音が 下がりながら 消える）"""
    n = int(dec * 3.5 * SR); t = np.arange(n) / SR; f = f0 * (1 + 0.5 * np.exp(-t / 0.035)); ph = TAU * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / dec) + 0.35 * np.sin(1.5 * ph) * np.exp(-t / (dec * 0.4)) + 0.6 * amb.lp(rng.normal(0, 1, n), 1800, 2) * np.exp(-t / 0.02)
    return fade(np.tanh(1.5 * y) / 1.2, 0.001, 0.05)


def chimes(rng, dur=1.3, up=False):
    """きらきら（ウィンドチャイム：高い 金の 棒を 順に なでる）→ ステレオ"""
    n = int((dur + 1.4) * SR); out = np.zeros((2, n)); k = 26
    for i in range(k):
        q = i / (k - 1); f = 2300 * 2 ** ((q if up else 1 - q) * 1.9) * rng.uniform(0.985, 1.015)
        i0 = max(0, int((q * dur + rng.uniform(-0.012, 0.012)) * SR)); tt = np.arange(n - i0) / SR
        y = (np.sin(TAU * f * tt) + 0.4 * np.sin(TAU * f * 2.76 * tt) * (f * 2.76 < 16000)) * np.exp(-tt / 0.45) * rng.uniform(0.6, 1.0)
        y[:64] *= np.linspace(0, 1, 64); pan = -0.7 + 1.4 * q
        out[0, i0:] += y * math.sqrt((1 - pan) / 2); out[1, i0:] += y * math.sqrt((1 + pan) / 2)
    return out / 6


def swell(rng, dur):
    """シンバルを 細かく たたいて 大きく して いく 音（区切りへ 向かう）"""
    n = int((dur + 0.25) * SR); t = np.arange(n) / SR; x = amb.hp(rng.normal(0, 1, n), 3200, 2)
    e = np.clip(t / dur, 0, 1) ** 2.4; e[t > dur] = np.exp(-(t[t > dur] - dur) / 0.07)
    return fade(x * e, 0.05, 0.05)


# ---------------------------------------------------------------- まとめ
def anorm(x):
    """鳴って いる 所 だけの 大きさで そろえる（ときどき しか 鳴らない 音：曲 全体で そろえると 鳴って いる 間が 大きく なりすぎる）"""
    k = int(0.05 * SR); nf = x.shape[1] // k; p = (x[:, :nf * k] ** 2).reshape(2, nf, k).mean((0, 2)); act = p > p.max() * 1e-3
    return x / max(math.sqrt(float(p[act].mean())) if act.any() else 0.0, 1e-12)


def norm(x):
    r = math.sqrt(float(np.mean(x ** 2))); return x / max(r, 1e-12)


def reverb(x, n_loop, rt, wet, seed, lpf, pre=0.012):
    rng = np.random.default_rng(seed); n = int(rt * SR); y = x * (1 - 0.5 * wet)
    for c in range(2):
        ir = rng.normal(0, 1, n) * np.exp(-6.9 * np.arange(n) / n); ir = amb.lp(ir, lpf, 1); ir[:int(pre * SR)] = 0; ir /= np.sqrt(np.sum(ir ** 2))
        w = signal.fftconvolve(x[c], ir); out = w[:n_loop].copy(); rest = w[n_loop:]
        while len(rest): m = min(len(rest), n_loop); out[:m] += rest[:m]; rest = rest[m:]          # ひびきの のこりは 頭へ（輪）
        y[c] += wet * out
    return y


def circ(fn, x, *a):
    """輪の ように つながった 音に フィルタ（頭と おしりを つないで かける）"""
    pad = 16384; return fn(np.concatenate([x[..., -pad:], x], -1), *a)[..., pad:]


def master(x, rms_db, peak_db, air=0.0):
    """大きさを そろえる：全体（RMS）を rms_db に・山は peak_db まで（こえる 所 だけ なめらかに おさえる）"""
    x = circ(amb.hp, x, 30, 2)
    if air: x = x + air * circ(amb.hp, x, 4500, 1)                              # 高い 所（4.5kHz から 上）を 少し 明るく
    lim = 10 ** (peak_db / 20)
    for _ in range(3):
        x = x * 10 ** (rms_db / 20) / max(math.sqrt(float(np.mean(x ** 2))), 1e-12)
        k = 0.6 * lim; a = np.abs(x); over = a > k
        x[over] = np.sign(x[over]) * (k + (lim - k) * np.tanh((a[over] - k) / (lim - k)))
    return x


# ================================================================ テンゲルBGM
#   和音：(ベースの 音, [和音の 音])。ニ長調
T_CH = {
    'G':   (43, [59, 62, 66, 69]),      # G△7(9)
    'A7':  (45, [61, 64, 67, 69]),
    'F#m': (42, [61, 64, 66, 69]),      # F#m7
    'Bm':  (47, [59, 62, 66, 69]),      # Bm7
    'D':   (38, [57, 61, 66, 69]),      # D△7
    'D7':  (38, [57, 60, 62, 66]),
    'Em':  (40, [59, 62, 64, 67]),      # Em7
    'D/F#': (42, [57, 62, 66, 69]),
    'As':  (45, [57, 62, 64, 69]),      # Asus4
}
T_PROG = ['G', 'A7', 'F#m', 'Bm', 'G', 'A7', 'D', 'D7',
          'G', 'A7', 'F#m', 'Bm', 'Em', 'A7', 'D', 'D',
          'Bm', 'F#m', 'G', 'D/F#', 'Em', 'F#m', 'G', 'As']
T_HALF = {23: 'A7'}                       # 小節の 後半（3拍め から）で 和音が かわる 所：さいごの 小節は Asus4 → A7（頭の G△7 へ もどる）
# ふし：小節ごとに (拍, 音, 長さ〈拍〉)
T_MEL = {
    0: [(1, 78, .5), (1.5, 81, .5), (2, 83, 1.5), (3.5, 81, .5)],
    1: [(0, 76, 1.5), (2, 74, .5), (2.5, 76, .5), (3, 78, 1)],
    2: [(0, 81, 1), (1, 78, .5), (1.5, 76, .5), (2, 78, 1.5), (3.5, 76, .5)],
    3: [(0, 74, 2), (2.5, 71, .5), (3, 74, .5), (3.5, 76, .5)],
    4: [(1, 78, .5), (1.5, 81, .5), (2, 83, 1), (3, 86, 1)],
    5: [(0, 85, 1), (1, 83, .5), (1.5, 81, 1), (2.5, 78, .5), (3, 81, 1)],
    6: [(0, 78, 1.5), (1.5, 76, .5), (2, 74, 2)],
    7: [(2.5, 69, .5), (3, 74, .5), (3.5, 76, .5)],
    8: [(0, 78, 1), (1, 78, .5), (1.5, 81, .5), (2, 83, 1.5), (3.5, 81, .5)],
    9: [(0, 76, 1.5), (2, 74, .5), (2.5, 76, .5), (3, 78, 1)],
    10: [(0, 81, 1), (1, 83, .5), (1.5, 81, .5), (2, 78, 1), (3, 76, .5), (3.5, 78, .5)],
    11: [(0, 74, 1.5), (1.5, 78, .5), (2, 83, 2)],
    12: [(0, 83, 1), (1, 79, .5), (1.5, 76, .5), (2, 79, 1), (3, 83, 1)],
    13: [(0, 81, 1), (1, 85, 1), (2, 88, 1.5), (3.5, 86, .5)],
    14: [(0, 86, 2.5), (3, 81, .5), (3.5, 78, .5)],
    15: [(0, 74, 2.5)],
    16: [(0.5, 74, .5), (1, 78, 1), (2, 83, 1.5), (3.5, 81, .5)],
    17: [(0, 81, 1), (1, 78, .5), (1.5, 76, .5), (2, 73, 2)],
    18: [(0.5, 74, .5), (1, 79, 1), (2, 83, 1.5), (3.5, 81, .5)],
    19: [(0, 81, 1), (1, 78, 1), (2, 74, 2)],
    20: [(0.5, 76, .5), (1, 79, .5), (1.5, 83, .5), (2, 86, 1), (3, 83, 1)],
    21: [(0, 85, 1), (1, 81, 1), (2, 78, 1), (3, 81, 1)],
    22: [(0, 83, 1.5), (1.5, 81, .5), (2, 83, 1), (3, 86, 1)],
    23: [(0, 88, 2), (2, 85, 1), (3, 81, .75)],
}


def tengel():
    S = Song(108, 24, 4.0); rng = np.random.default_rng(171)
    B = S.beat; S8, S16 = B / 2, B / 4
    drum, hats, shk, bass, keys, pad, vbs, lead, glk, arp = (S.stem() for _ in range(10))
    for bar in range(S.bars):
        root, ch = T_CH[T_PROG[bar]]; t0 = S.at(bar); sec = bar // 8                # 0＝A・1＝A'・2＝B
        ch2 = T_CH[T_HALF[bar]][1] if bar in T_HALF else ch                        # 後半の 和音
        last = bar % 8 == 7
        # ドラム：キック（1拍・2拍の うら・3拍）・リム（2拍・4拍）・ハイハット（8分）
        for b_, g_ in ((0, 1.0), (1.5, 0.55), (2, 0.9)) + (((3.5, 0.5),) if bar % 2 == 1 else ()):
            drum.put(kick(), t0 + b_ * B, 0.0, g_)
        for b_ in (1, 3): drum.put(rim(rng), t0 + b_ * B, 0.1, 0.8)
        if last:                                                                   # 区切りの 小節：小さな おかず（スネア 3つ）
            for b_, g_ in ((2.5, 0.35), (3.0, 0.45), (3.5, 0.6)): drum.put(snare(rng, 0.07), t0 + b_ * B, -0.1, g_)
        for k in range(8):
            hats.put(hat(rng, 0.045 if k == 7 else 0.022), t0 + k * S8, 0.3, (0.55 if k % 2 == 0 else 0.9) * rng.uniform(0.85, 1.0))
        if sec >= 1:                                                               # A'・B：シェイカー（16分）
            for k in range(16): shk.put(shaker(rng), t0 + k * S16 - 0.012, -0.35, (0.5, 0.25, 0.7, 0.3)[k % 4] * rng.uniform(0.85, 1.0))
        # ベース：根音 → うらで 根音 → 5度 → オクターブ上 → つぎの 和音へ 半歩 近づく
        nxt = T_CH[T_PROG[(bar + 1) % S.bars]][0]
        appr = nxt + (1 if nxt < root else -1) if nxt != root else root + 7
        for b_, m_, d_, g_ in ((0, root, 1.3, 1.0), (1.5, root, 0.45, 0.8), (2, root + 7, 0.9, 0.9), (3, root + 12, 0.45, 0.8), (3.5, appr, 0.45, 0.75)):
            bass.put(ebass(m_, d_ * B), t0 + b_ * B, 0.0, g_)
        # エレピ：頭で 長く・うらで 短く きざむ（左右に ゆっくり ゆれる）
        for b_, d_, g_ in ((0, 1.4, 1.0), (1.5, 0.5, 0.7), (2.5, 0.9, 0.8)) + (((3.5, 0.4, 0.6),) if sec == 2 else ()):
            for i, m_ in enumerate(ch if b_ < 2 else ch2):
                tt = t0 + b_ * B + 0.006 * i                                       # 少し ずらして はじく
                keys.put(epiano(m_, d_ * B), tt, 0.45 * math.sin(TAU * tt / 3.3 + i), g_ * (0.9 if i else 1.0))
        # やわらかい 弦：和音を のばす
        if bar in T_HALF:
            for h_, cc in ((0, ch), (2, ch2)):
                for i, m_ in enumerate(cc[:3] + [cc[0] + 12]): pad.put(pad_note(m_, 2 * B * 0.96), t0 + h_ * B, (-0.5, 0.5, -0.2, 0.25)[i], 1.0)
        else:
            for i, m_ in enumerate(ch[:3] + [ch[0] + 12]): pad.put(pad_note(m_, S.bar * 0.98), t0, (-0.5, 0.5, -0.2, 0.25)[i], 1.0)
        # B：マリンバの 分散和音（8分）
        if sec == 2:
            for k in range(8):
                cc = ch if k < 4 else ch2; tones = [cc[0] + 12, cc[1] + 12, cc[2] + 12, cc[3] + 12, cc[2] + 12, cc[1] + 12, cc[3] + 12, cc[2] + 12]
                arp.put(marimba(tones[k]), t0 + k * S8, -0.4 if k % 2 == 0 else 0.4, 0.9 if k % 2 == 0 else 0.65)
        # ふし：ビブラフォン（ずっと）・A' だけ 口笛が 重なる（もり上がる）・長い 音の 上に 小さく 鈴
        for b_, m_, d_ in T_MEL.get(bar, []):
            vbs.put(vibe(m_, d_ * B * 0.96), t0 + b_ * B, 0.12, 1.0)
            if sec == 1: lead.put(whistle(m_, d_ * B * 0.96, rng), t0 + b_ * B, -0.05, 1.0)
            if d_ >= 1: glk.put(glock(m_ + 12), t0 + b_ * B, -0.25, 0.8 if sec == 1 else 0.55)
    x = sum(10 ** (db / 20) * norm(s.fold()) for s, db in ((drum, -8.5), (hats, -19), (shk, -22), (bass, -9), (keys, -12), (pad, -15.5), (vbs, -9.5), (lead, -15), (glk, -17), (arp, -14.5)))
    x = reverb(x, S.n, 0.9, 0.15, 21, 7500)
    return master(x, -26.0, -12.0, 0.7), S


# ================================================================ 神様馬の BGM
#   ホ短調。(ベースの 音, [和音の 音])
D_CH = {
    'Em': (40, [64, 67, 71]), 'C': (36, [64, 67, 72]), 'G': (43, [62, 67, 71]), 'D': (38, [62, 66, 69]), 'B7': (35, [63, 66, 69, 71]),
    'Am': (45, [64, 69, 72]), 'E': (40, [64, 68, 71]), 'G/B': (47, [62, 67, 71]),
}
D_PROG = ['Em', 'Em', 'C', 'C', 'G', 'G', 'D', 'D', 'Em', 'Em', 'C', 'C', 'D', 'D', 'B7', 'B7',
          'C', 'D', 'Em', 'Em', 'C', 'D', 'G', 'G/B', 'Am', 'B7', 'Em', 'D', 'C', 'D', 'E', 'B7']
D_MEL = {
    0: [(0, 76, .75), (.75, 76, .25), (1, 79, .5), (1.5, 83, 2.4)], 1: [(0, 83, 1), (1, 81, .5), (1.5, 79, .5), (2, 78, 1), (3, 79, 1)],
    2: [(0, 76, .75), (.75, 76, .25), (1, 79, .5), (1.5, 84, 2.4)], 3: [(0, 84, 1), (1, 83, .5), (1.5, 81, .5), (2, 79, 2)],
    4: [(0, 74, .75), (.75, 74, .25), (1, 79, .5), (1.5, 83, 1.5), (3, 86, 1)], 5: [(0, 86, 1.5), (1.5, 84, .5), (2, 83, 2)],
    6: [(0, 81, 1.5), (1.5, 78, .5), (2, 81, 1), (3, 86, 1)], 7: [(0, 81, 1), (1, 83, 1), (2, 81, 1), (3, 78, 1)],
    8: [(0, 76, .75), (.75, 76, .25), (1, 79, .5), (1.5, 83, 2.4)], 9: [(0, 88, 2), (2, 86, 1), (3, 83, 1)],
    10: [(0, 84, 1.5), (1.5, 83, .5), (2, 81, 1), (3, 79, 1)], 11: [(0, 76, 1), (1, 79, 1), (2, 84, 2)],
    12: [(0, 86, 2), (2, 81, 1), (3, 86, 1)], 13: [(0, 88, 1), (1, 86, 1), (2, 81, 2)],
    14: [(0, 83, 1.5), (1.5, 87, .5), (2, 90, 2)], 15: [(0, 90, .5), (0.75, 87, .5), (1.5, 83, 2.3)],
    16: [(0, 79, 1), (1, 84, 1), (2, 88, 2)], 17: [(0, 81, 1), (1, 86, 1), (2, 90, 2)],
    18: [(0, 91, 2), (2, 90, 1), (3, 88, 1)], 19: [(0, 83, 2), (2, 88, 2)],
    20: [(0, 79, 1), (1, 84, 1), (2, 88, 2)], 21: [(0, 81, 1), (1, 86, 1), (2, 90, 2)],
    22: [(0, 91, 3), (3, 86, 1)], 23: [(0, 83, 2), (2, 86, 2)],
    24: [(0, 84, 1.5), (1.5, 83, .5), (2, 81, 2)], 25: [(0, 83, 1.5), (1.5, 87, .5), (2, 90, 2)],
    26: [(0, 88, 2), (2, 83, 2)], 27: [(0, 86, 2), (2, 81, 2)],
    28: [(0, 84, 1.5), (1.5, 86, .5), (2, 88, 2)], 29: [(0, 86, 1.5), (1.5, 88, .5), (2, 90, 2)],
    30: [(0, 88, 1), (1, 92, 3)], 31: [(0, 90, 1.25), (1.5, 87, .45), (2, 83, 1.9)],
}


D_KIME = {15: (0, 0.75, 1.5), 31: (0, 1.5)}      # キメ（全員で 同じ リズムを 打つ）の 小節：打つ 拍
D_GLISS = {15: (11, 3, 4, 6, 9), 23: (4, 7, 9, 11, 2), 31: (11, 3, 4, 6, 9)}      # ハープの 駆け上がり（3拍めの うら から つぎの 小節の 頭へ）：使う 音（シ レ# ミ ファ# ラ／ミ ソ ラ シ レ）
STEMS_OUT = None                                 # ためす 用：ここに 入れ物（dict）を 置くと、まぜる 前の 音（重みを かけた あと）が 入る


def chord_above(bass, ch):
    """ベースの 音から 上へ ならべた 和音の 音（半音の 数。ベースと 同じ 名前の 音は のぞく）"""
    return sorted({(c - bass) % 12 for c in ch} - {0})


def under(m, ch):
    """ふしの 下の ハモリ：3〜9半音 下に ある 和音の 音"""
    pcs = {c % 12 for c in ch}
    for d in range(3, 10):
        if (m - d) % 12 in pcs: return m - d
    return m - 12


def divine2():
    S = Song(156, 32, 5.0); rng = np.random.default_rng(1713)
    B = S.beat; S8, S16 = B / 2, B / 4
    st = {k: S.stem() for k in 'drum toms hats cym timp bass riff strg pad lead harm horn vln sop chr chant org harp bell glk chm fx'.split()}
    P = st.__getitem__
    def gliss(t_a, t_b, lo, hi, pcs):
        ms = [m for m in range(lo, hi + 1) if m % 12 in pcs]
        for i, m in enumerate(ms):
            q = i / max(1, len(ms) - 1); P('harp').put(harp(m, 0.7), t_a + (t_b - t_a) * q, -0.6 + 1.2 * q, 0.5 + 0.5 * q)
    for bar in range(S.bars):
        root, ch = D_CH[D_PROG[bar]]; t0 = S.at(bar); sec = bar // 8      # 0＝A1・1＝A2・2＝B（神々しい 所）・3＝C（山場）
        ab = chord_above(root, ch); third, fifth = ab[0], ab[1]
        kime = D_KIME.get(bar); drive = sec != 2 and not kime; holy = sec == 2 and not kime; last = bar == S.bars - 1
        # ---- ドラム
        if drive:                                                                  # 走る 所：キックは「ダッダダ」（馬の ギャロップ）・2拍と 4拍に スネア・16分の ハイハット
            for b_ in range(4):
                if b_ % 2 == 0: P('drum').put(kick(150, 46, 0.15, 0.7, 1.6), t0 + b_ * B, 0.0, 1.0)
                else:
                    P('drum').put(snare(rng, 0.11, 185, 8000), t0 + b_ * B, 0.0, 0.9); P('drum').put(kick(150, 46, 0.12, 0.4, 1.4), t0 + b_ * B, 0.0, 0.5)
                P('drum').put(kick(140, 46, 0.1, 0.5, 1.4), t0 + (b_ + 0.5) * B, 0.0, 0.55); P('drum').put(kick(140, 46, 0.1, 0.5, 1.4), t0 + (b_ + 0.75) * B, 0.0, 0.68)
            for k in range(16):
                P('hats').put(hat(rng, 0.05 if k % 4 == 2 else 0.018, 7600), t0 + k * S16, 0.3, (1.0, 0.45, 0.75 if sec < 3 else 1.0, 0.5)[k % 4] * rng.uniform(0.85, 1.0))
        elif holy:                                                                 # 神々しい 所：半分の 速さの 感じ（1拍めに キックと 太鼓・3拍めに 大きな スネア・つぎの 小節へ「ドド」）
            P('drum').put(kick(150, 44, 0.2, 0.7, 1.6), t0, 0.0, 1.0); P('toms').put(tom(rng, 82, 0.34), t0, 0.0, 1.0)
            P('drum').put(snare(rng, 0.17, 170, 7000), t0 + 2 * B, 0.0, 1.0)
            P('drum').put(kick(140, 46, 0.1, 0.5, 1.4), t0 + 3.5 * B, 0.0, 0.6); P('drum').put(kick(140, 46, 0.1, 0.5, 1.4), t0 + 3.75 * B, 0.0, 0.75)
            for k in range(8): P('hats').put(hat(rng, 0.06 if k % 2 == 0 else 0.03, 7000), t0 + k * S8, 0.3, (0.9 if k % 2 == 0 else 0.45) * rng.uniform(0.85, 1.0))
        if bar % 8 == 0: P('cym').put(crash(rng, 1.0), t0, -0.2, 1.0)               # 区切りの 頭：シンバル
        elif bar % 4 == 0: P('cym').put(crash(rng, 0.7), t0, 0.2, 0.55)
        if bar in (7, 23, 27):                                                     # 区切りの 小節：太鼓の おかず（高い → 低い）
            for i, (b_, f_) in enumerate(((2.5, 150), (2.75, 150), (3.0, 120), (3.25, 120), (3.5, 95), (3.75, 95))): P('toms').put(tom(rng, f_, 0.2), t0 + b_ * B, (-0.4, -0.4, 0.0, 0.0, 0.4, 0.4)[i], 0.6 + 0.08 * i)
        if (bar % 2 == 0 or holy) and not kime: P('timp').put(timpani(root + 12), t0, 0.15, 0.85 if holy else 1.0)
        # ---- ベース と 低い 金管の リフ
        if drive:                                                                  # 「ダッダダ」＋ 拍の 頭で 上の 音へ（根音 → 1オクターブ上 → 3度 → 5度 → 1オクターブ上）
            for i_, m_, l_ in ((0, root, 2), (2, root, 1), (3, root, 1), (4, root + 12, 2), (6, root, 1), (7, root, 1), (8, root + 12 + third, 2), (10, root, 1), (11, root, 1), (12, root + 12 + fifth, 2), (14, root + 12, 2)):
                P('bass').put(gbass(m_, l_ * S16 * 0.86), t0 + i_ * S16, 0.0, 1.0 if l_ == 2 else 0.75)
                if l_ == 2: P('riff').put(brass(m_ if m_ >= 45 else m_ + 12, S8 * 0.8, rng, 1.2), t0 + i_ * S16, -0.25, 1.0 if i_ == 0 else 0.8)
        elif holy:                                                                 # 神々しい 所：8分で まっすぐ 刻む
            for k in range(8): P('bass').put(gbass(root + 12 if k == 7 else root, S8 * 0.9), t0 + k * S8, 0.0, 1.0 if k % 2 == 0 else 0.7)
        # ---- 弦
        if drive:
            if bar in (14, 29):                                                    # つぎへ 駆け上がる（3拍め から 16分で 8つ）：はじめの 2拍は きざみ
                run = (59, 60, 63, 64, 66, 67, 69, 71) if bar == 14 else (62, 64, 66, 67, 69, 71, 73, 74)
                for k in range(8): P('strg').put(spicc(ch[k % 3], 0.085), t0 + k * S16, -0.45 if k % 2 == 0 else 0.45, (1.0, 0.6, 0.8, 0.6)[k % 4])
                for k, m_ in enumerate(run):
                    for o_, pan in ((0, -0.3), (12, 0.3)): P('strg').put(spicc(m_ + o_, 0.09), t0 + 2 * B + k * S16, pan, 0.75 + 0.05 * k)
            else:
                tones = [ch[0], ch[1], ch[2], ch[1]] if sec == 0 else [ch[0] + 12, ch[1], ch[2], ch[0] + 12, ch[2], ch[1], ch[2], ch[1]]
                for k in range(16): P('strg').put(spicc(tones[k % len(tones)], 0.085), t0 + k * S16, -0.45 if k % 2 == 0 else 0.45, (1.0, 0.6, 0.8, 0.6)[k % 4])
        elif holy:                                                                 # 神々しい 所：やわらかい 弦で 和音を のばす
            for i, m_ in enumerate([ch[0] - 12, ch[0], ch[1], ch[2]]): P('pad').put(pad_note(m_, S.bar * 0.98, 2400), t0, (-0.5, 0.5, -0.2, 0.25)[i], 1.0)
        # ---- パイプオルガン
        vo = [root + 12, root + 19, ch[0], ch[1], ch[2]]
        if bar == 0:                                                               # 降臨：頭で 2小節 のばす
            for j, m_ in enumerate(vo): P('org').put(organ(m_, 2 * S.bar * 0.97, rng), t0, (-0.4, 0.4, -0.2, 0.2, 0.0)[j], 0.85)
        if sec == 1 and not kime:                                                  # A2：16分の 分散和音（高い 所で）
            ar = [ch[2] + 12, ch[1] + 12, ch[0] + 12, ch[1] + 12]
            for k in range(16): P('org').put(organ(ar[k % 4], S16 * 0.9, rng, 0.6), t0 + k * S16, 0.3 if k % 2 == 0 else -0.3, 0.7 if k % 4 else 0.86)
        if holy or (sec == 3 and not kime):                                        # B・C：和音を のばす（B は 上の 音も 足して 大きく）
            for j, m_ in enumerate(vo + ([ch[0] + 12] if holy else [])): P('org').put(organ(m_, S.bar * 0.98, rng), t0, (-0.4, 0.4, -0.2, 0.2, 0.0, 0.1)[j], 1.0 if holy else 0.62)
        # ---- 合唱
        if not kime:                                                               # アー：和音を のばす（低い 声で 太く・B と C は 1オクターブ上も）
            cm = [ch[0] - 12] + list(ch[:3]) + ([ch[0] + 12] if sec >= 2 else [])
            P('chr').put2(choir(cm, S.bar * 0.97, rng), t0, (0.7, 0.8, 1.0, 1.0)[sec])
        if drive and sec in (1, 3):                                                # 掛け声（ハッ）：「3・3・2」の リズム
            for b_ in (0, 1.5, 3): P('chant').put2(choir([ch[0], ch[1], ch[2], ch[0] + 12], S8 * 0.7, rng, 0.025, 0.12), t0 + b_ * B, 1.0 if b_ == 0 else 0.85)
        # ---- 鐘・きらきら・ハープ
        if bar % 8 == 0 or holy or D_PROG[bar] != D_PROG[bar - 1]: P('bell').put(tbell(ch[0] + 12, 1.3), t0, 0.3 if bar % 2 else -0.3, 1.0 if bar % 8 == 0 else 0.5 if holy else 0.45)
        if holy:
            up = [ch[0], ch[1], ch[2], ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24, ch[1] + 24]; seq = up + up[::-1]
            for k in range(16 if bar not in D_GLISS else 10):
                P('harp').put(harp(seq[k]), t0 + k * S16, -0.5 + (seq[k] - up[0]) / max(1, up[-1] - up[0]), 1.0 if k % 4 == 0 else 0.7)
            for k in (1, 3, 5, 7): P('glk').put(glock(ch[int(rng.integers(3))] + 24), t0 + k * S8, float(rng.uniform(-0.6, 0.6)), float(rng.uniform(0.5, 1.0)))
        if bar in D_GLISS: gliss(t0 + 2.5 * B, t0 + 4 * B - 0.02, 52, 88, D_GLISS[bar])
        # ---- ふし
        for b_, m_, d_ in D_MEL.get(bar, []):
            tt = t0 + b_ * B; du = d_ * B * 0.94; rip = 5.0 if d_ >= 2 and not holy else 0.0
            if not holy or bar >= 22:                                              # 金管（トランペットの 高さ）：B の はじめの 6小節は お休み（もどって くる 所が 引き立つ）
                P('lead').put(brass(m_ - 12, du, rng, 1.0, rip), tt, 0.08, 1.0)
                if sec in (1, 3): P('harm').put(brass(under(m_ - 12, ch), du, rng, 0.8, rip), tt, 0.3, 1.0)      # A2・C：ハモリ
            if sec >= 1 or d_ >= 2: P('horn').put(brass(m_ - 24, du, rng, 0.4 if holy else 0.5, 0.0 if holy else rip), tt, -0.3, 1.0)      # ホルン（1オクターブ下）で 太く
            if sec >= 2 or d_ >= 1.5: P('vln').put(hstr(m_, du, rng), tt, 0.35, 1.0)                              # 高い 弦（もとの 高さ）
            if sec >= 2 and not kime: P('sop').put2(choir([m_ - 12], du, rng, 0.07, 0.25), tt, 1.0)               # B・C：ソプラノが ふしを 歌う
        # ---- キメ（全員で 同じ リズム）と、つぎの 小節への 盛り上げ
        if kime:
            for i, hb in enumerate(kime):
                tt = t0 + hb * B; lg = i == len(kime) - 1; du = B * (1.5 if lg else 0.4)
                P('drum').put(kick(150, 44, 0.18, 0.8, 1.7), tt, 0.0, 1.0); P('drum').put(snare(rng, 0.13, 180, 8000), tt, 0.0, 0.9)
                P('cym').put(crash(rng, 0.8 if lg else 0.3), tt, 0.2 if i % 2 else -0.2, 0.9); P('timp').put(timpani(root + 12, 0.5), tt, 0.15, 1.0)
                P('bass').put(gbass(root, B * (1.2 if lg else 0.5)), tt, 0.0, 1.0); P('riff').put(brass(root + 12, du, rng, 1.3), tt, -0.25, 1.0)
                P('chant').put2(choir([ch[0], ch[1], ch[2], ch[0] + 12], du, rng, 0.025, 0.15), tt, 1.0)
                for j, m_ in enumerate(vo): P('org').put(organ(m_, du, rng), tt, (-0.4, 0.4, -0.2, 0.2, 0.0)[j], 0.8)
                for j, m_ in enumerate(ch[:3]): P('strg').put(spicc(m_, 0.16), tt, (-0.45, 0.45, 0.0)[j], 1.0)
            for k in range(8): P('timp').put(timpani(root + 12, 0.3), t0 + 2 * B + k * S16, 0.15, 0.35 + 0.09 * k)      # ティンパニの ロール（3拍め から・だんだん 大きく）
            P('fx').put(swell(rng, 2 * B), t0 + 2 * B, 0.0, 1.0)
        if bar == 23:                                                              # B の おわり：ティンパニの ロールと シンバルで C へ
            for k in range(8): P('timp').put(timpani(root + 12, 0.3), t0 + 2 * B + k * S16, 0.15, 0.35 + 0.09 * k)
            P('fx').put(swell(rng, 2 * B), t0 + 2 * B, 0.0, 1.0)
        if last:                                                                   # さいごの 小節：スネアの ロール（3拍め から：16分 → 32分・だんだん 大きく）と 上がる 風 → 頭へ
            ts = [2 * B + k * S16 for k in range(4)] + [3 * B + k * S16 / 2 for k in range(8)]
            for i, tt in enumerate(ts): P('drum').put(snare(rng, 0.05), t0 + tt, 0.0, 0.3 + 0.65 * (i / (len(ts) - 1)) ** 1.5)
            P('fx').put(riser(rng, S.bar), t0, 0.0, 0.8)
    P('chm').put2(chimes(rng, 1.3, False), S.at(0), 0.6); P('chm').put2(chimes(rng, 1.3, False), S.at(16), 1.0); P('chm').put2(chimes(rng, 1.2, True), S.at(30), 1.0)
    # まぜる：走る 音（ドラム・ベース・リフ）は ひびきを 短く・ほかは 大聖堂の ような 長い ひびき
    #   重み（dB）：ずっと 鳴る 音は 曲 全体で そろえる（norm）・ときどき 鳴る 音は 鳴って いる 所で そろえる（anorm）
    dry = (('drum', -7.5, norm), ('toms', -11, anorm), ('hats', -20, norm), ('bass', -9.5, norm), ('riff', -15, anorm))
    hall = (('cym', -15, anorm), ('timp', -12, anorm), ('strg', -15, anorm), ('pad', -17, anorm), ('lead', -9, anorm), ('harm', -15, anorm), ('horn', -13, anorm), ('vln', -15, anorm), ('sop', -12, anorm),
            ('chr', -13.5, anorm), ('chant', -12, anorm), ('org', -14.5, anorm), ('harp', -15, anorm), ('bell', -13, anorm), ('glk', -20, anorm), ('chm', -21, anorm), ('fx', -17, anorm))
    W = {k: 10 ** (db / 20) * fn(st[k].fold()) for k, db, fn in dry + hall}
    if STEMS_OUT is not None: STEMS_OUT.update(W)
    x = reverb(sum(W[k] for k, _, _ in dry), S.n, 0.9, 0.12, 77, 7000, 0.012) + reverb(sum(W[k] for k, _, _ in hall), S.n, 2.2, 0.27, 78, 6500, 0.02)
    return master(x, -28.0, -14.0, 0.5), S


# ================================================================ テンゲルBGM 第2稿（のどかな 村の ふんいき）
#   ト長調。(ベースの 音, [弦で 弾く 和音の 音：下から 5つ])
N_CH = {
    'G':    (43, [55, 59, 62, 67, 71]), 'D/F#': (42, [54, 57, 62, 66, 69]), 'Em':  (40, [52, 55, 59, 64, 67]), 'Em7': (40, [52, 55, 59, 62, 67]),
    'C':    (36, [48, 55, 60, 64, 67]), 'G/B':  (47, [55, 59, 62, 67, 71]), 'Am7': (45, [52, 57, 60, 64, 67]), 'D':   (38, [50, 57, 62, 66, 69]),
    'Bm':   (47, [54, 59, 62, 66, 71]),
}
N_PROG = ['G', 'D/F#', 'Em', 'Em7', 'C', 'G/B', 'Am7', 'D',
          'G', 'D/F#', 'Em', 'Bm', 'C', 'G/B', 'Am7', 'D',
          'C', 'D', 'Bm', 'Em', 'C', 'D', 'G', 'D']
N_MEL = {
    0: [(0, 74, 1.5), (1.5, 76, .5), (2, 79, 2)], 1: [(0, 78, 1), (1, 76, 1), (2, 74, 2)],
    2: [(0, 71, 1.5), (1.5, 74, .5), (2, 76, 1.5), (3.5, 74, .5)], 3: [(0, 71, 3)],
    4: [(0, 72, 1.5), (1.5, 76, .5), (2, 79, 2)], 5: [(0, 81, 1), (1, 79, 1), (2, 74, 2)],
    6: [(0, 72, 1), (1, 76, 1), (2, 81, 1.5), (3.5, 79, .5)], 7: [(0, 78, 2), (2, 74, 1), (3, 76, 1)],
    8: [(0, 79, 1.5), (1.5, 81, .5), (2, 83, 2)], 9: [(0, 81, 1), (1, 78, 1), (2, 74, 2)],
    10: [(0, 76, 1.5), (1.5, 79, .5), (2, 83, 1.5), (3.5, 81, .5)], 11: [(0, 78, 3)],
    12: [(0, 76, 1.5), (1.5, 79, .5), (2, 84, 2)], 13: [(0, 83, 1), (1, 79, 1), (2, 74, 2)],
    14: [(0, 72, 1), (1, 76, 1), (2, 79, 1.5), (3.5, 76, .5)], 15: [(0, 74, 3)],
    16: [(1, 76, 1), (2, 79, 1), (3, 84, 1)], 17: [(0, 86, 2), (2, 81, 2)],
    18: [(1, 74, 1), (2, 78, 1), (3, 83, 1)], 19: [(0, 83, 1.5), (1.5, 81, .5), (2, 79, 2)],
    20: [(1, 76, 1), (2, 79, 1), (3, 84, 1)], 21: [(0, 86, 1.5), (1.5, 88, .5), (2, 86, 1), (3, 81, 1)],
    22: [(0, 83, 2), (2, 79, 2)], 23: [(0, 81, 2), (2, 78, 1), (3, 76, .75)],
}


def ocarina(m, dur, rng):
    """笛（オカリナ・土の 笛の ような まるい 音：倍音は 少し・息の 音・入りで 少し 下から・のばすと ゆっくり ゆれる）"""
    n = int((dur + 0.12) * SR); t = np.arange(n) / SR; f = vib(mtof(m), n, 4.6, 0.006, 0.3) * (1 - 0.018 * np.exp(-t / 0.05))
    ph = TAU * np.cumsum(f) / SR
    y = np.sin(ph) + 0.09 * np.sin(2 * ph) + 0.14 * np.sin(3 * ph) * np.exp(-t / 0.4) + 0.03 * np.sin(5 * ph)
    br = amb.bp(rng.normal(0, 1, n), max(300.0, mtof(m) * 1.5), min(9000.0, mtof(m) * 5), 1) * (0.05 + 0.09 * np.exp(-t / 0.06))      # 息（入りで 少し 多い）
    return (y + br) * adsr(n, 0.045, 0.15, 0.85, 0.12)


def nylon(m, dec=1.1):
    """ポロンと 弾く 弦（ナイロンの ギター・たて琴の あいだ：やわらかい つめ・高い 倍音は すぐ 消える）"""
    n = int(dec * 2.6 * SR); t = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for k in range(1, 11):
        if f * k > 9000: break
        y += (1.0 / k ** 1.6) * np.sin(TAU * f * k * (1 + 0.0003 * k * k) * t + 0.5 * k) * np.exp(-t / (dec / (1 + 0.8 * (k - 1))))
    y[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR)) ** 0.5
    return fade(y, 0.001, 0.06)


def fdrum(rng, f0=62.0, dec=0.32, soft=1.0):
    """低い 太鼓（手で たたく 大きな 皮の 太鼓：やわらかい）"""
    n = int(dec * 3.2 * SR); t = np.arange(n) / SR; f = f0 * (1 + 0.35 * np.exp(-t / 0.03)); ph = TAU * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / dec) + 0.3 * np.sin(1.6 * ph) * np.exp(-t / (dec * 0.35)) + 0.35 * soft * amb.lp(rng.normal(0, 1, n), 900, 2) * np.exp(-t / 0.018)
    return fade(y, 0.002, 0.05)


def rainstick(rng, dur=1.8):
    """雨の 棒（レインスティック：小さな 粒が たくさん 流れる 音）→ ステレオ"""
    n = int((dur + 0.4) * SR); out = np.zeros((2, n))
    for _ in range(1100):
        q = rng.beta(2.2, 2.2); i0 = int(q * dur * SR); m_ = int(rng.uniform(0.004, 0.014) * SR)
        g = amb.bp(rng.normal(0, 1, m_ + 128), rng.uniform(2500, 4500), rng.uniform(6000, 10000), 1)[128:] * np.exp(-np.arange(m_) / SR / rng.uniform(0.002, 0.006)) * rng.uniform(0.25, 0.7)
        pan = -0.6 + 1.2 * q + rng.uniform(-0.2, 0.2); pan = max(-0.9, min(0.9, pan))
        out[0, i0:i0 + m_] += g * math.sqrt((1 - pan) / 2); out[1, i0:i0 + m_] += g * math.sqrt((1 + pan) / 2)
    return out


def fue(m, dur, rng, grace=0):
    """笛（竹の 横笛・フルートの ような 息の 入った 音：倍音が 少し 多い・吹きはじめに 息の 音・のばすと ゆれる）。grace＝入りの かざりの 音（半音の 数：その 高さから すばやく 本当の 音へ）"""
    n = int((dur + 0.14) * SR); t = np.arange(n) / SR; f = vib(mtof(m), n, 5.0, 0.007, 0.28) * (1 - 0.015 * np.exp(-t / 0.045))
    if grace: f = f * 2 ** ((grace / 12) * (t < 0.07))                                  # かざりの 音（0.07秒）
    ph = TAU * np.cumsum(f) / SR
    y = np.sin(ph) + 0.34 * np.sin(2 * ph) + 0.13 * np.sin(3 * ph) + 0.05 * np.sin(4 * ph)
    wob = 1 + 0.12 * amb.lp(rng.normal(0, 1, n), 9, 2) * 6                              # 息の ゆらぎ（音の 大きさが 少し ゆれる）
    br = amb.bp(rng.normal(0, 1, n), 1800.0, 7000.0, 1) * (0.11 + 0.22 * np.exp(-t / 0.05))      # 息の 音（吹きはじめに 多い）
    return (y * np.clip(wob, 0.6, 1.4) + br) * adsr(n, 0.05, 0.16, 0.86, 0.14)


def chirp(fs, dur, rng, tril=0.0):
    """鳥の ひと声：高さが fs（Hz の ならび）を なめらかに たどる 口笛の ような 音。tril＝ふるえ（速い 高さの ゆれ）"""
    n = int(dur * SR); t = np.arange(n) / SR; f = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(fs)), fs)
    if tril: f = f * (1 + tril * np.sin(TAU * rng.uniform(24, 34) * t))
    ph = TAU * np.cumsum(f) / SR
    return (np.sin(ph) + 0.18 * np.sin(2 * ph)) * np.hanning(n) ** 0.7


def bird(rng, kind):
    """鳥の 声 1回ぶん（1〜2秒）：0＝ピチチチ（小さな 鳥が 速く）・1＝チュン チュン・2＝ヒー ヨ（長い 口笛と 短い 声）・3＝ホー… と のばして から 3つの 音（遠くの 鳥）"""
    out = np.zeros(int(2.4 * SR))
    def put_(x, at):
        i = int(at * SR); out[i:i + len(x)] += x[:max(0, len(out) - i)]
    k = rng.uniform(0.92, 1.1)                                                         # 鳥ごとに 少し 高さが ちがう
    if kind == 0:
        for i in range(int(rng.integers(3, 6))): put_(chirp([3300 * k, 4900 * k, 3700 * k], 0.075, rng) * (0.7 + 0.3 * rng.random()), i * rng.uniform(0.1, 0.125))
    elif kind == 1:
        for i in range(2 + int(rng.integers(0, 2))): put_(chirp([4700 * k, 3900 * k, 3000 * k], 0.07, rng), i * 0.19 + rng.uniform(0, 0.02))
    elif kind == 2:
        put_(chirp([2500 * k, 3000 * k, 3500 * k, 3300 * k], 0.5, rng, 0.012), 0.0); put_(chirp([3900 * k, 2900 * k], 0.11, rng), 0.62)
    elif kind == 3:
        put_(chirp([1380 * k, 1400 * k, 1440 * k, 1500 * k], 0.95, rng) * np.linspace(0.5, 1.0, int(0.95 * SR)), 0.0)
        for i, (a_, b_) in enumerate(((2250, 2500), (3050, 2800), (2100, 1900))): put_(chirp([a_ * k, b_ * k], 0.13, rng), 1.05 + i * 0.15)
    elif kind == 4:                                                                    # ピー ヒョロロロ（空の 高い 所を まわる 鳥：長い 口笛 → ふるえながら 下がる）
        n1 = int(0.62 * SR); n2 = int(1.05 * SR)
        put_(chirp([3350 * k, 3900 * k, 3880 * k, 3780 * k], 0.62, rng), 0.0)
        f2 = np.linspace(3780 * k, 2550 * k, n2) * (1 + 0.055 * np.sin(TAU * 13.0 * np.arange(n2) / SR)); ph2 = TAU * np.cumsum(f2) / SR
        put_((np.sin(ph2) + 0.15 * np.sin(2 * ph2)) * np.hanning(n2) ** 0.5 * np.linspace(1.0, 0.45, n2) * (0.75 + 0.25 * np.cos(TAU * 13.0 * np.arange(n2) / SR)), 0.56)
    else:                                                                              # ツツピー ツツピー（小さな 鳥：短い 高い 音 2つ → 少し 低い のばす 音）を 2〜3回
        for i in range(2 + int(rng.integers(0, 2))):
            t1 = i * 0.46
            put_(chirp([5600 * k, 5400 * k], 0.055, rng) * 0.8, t1); put_(chirp([5600 * k, 5400 * k], 0.055, rng) * 0.8, t1 + 0.085); put_(chirp([4300 * k, 4150 * k, 4200 * k], 0.19, rng), t1 + 0.18)
    return out


def nodoka(bpm=116, flute=False, birds=False):
    """bpm＝速さ・flute＝ふしを 息の 入った 笛（fue）で 吹く（オカリナは 下の ハモリと かけあい）・birds＝鳥の 声を 入れる"""
    S = Song(bpm, 24, 4.0); rng = np.random.default_rng(1714)
    B = S.beat; S8 = B / 2
    st = {k: S.stem() for k in 'drum shk bass gtr pad lead low mar glk rain bird'.split()}; P = st.__getitem__
    for bar in range(S.bars):
        root, ch = N_CH[N_PROG[bar]]; t0 = S.at(bar); sec = bar // 8      # 0＝A・1＝A'・2＝B
        # 低い 太鼓：1拍め（強く）・2拍めの うら（弱く）・4拍め（中ぐらい）＝ 3・3・2 の ノリ。A' と B は 4拍めの うらに 小さく 1つ
        for b_, g_, f_ in ((0, 1.0, 60), (1.5, 0.5, 66), (3, 0.72, 62)) + (((3.5, 0.4, 72),) if sec >= 1 and bar % 2 == 1 else ()):
            P('drum').put(fdrum(rng, f_, 0.34 if b_ == 0 else 0.24), t0 + b_ * B, 0.0, g_)
        # シャラシャラ（8分・うらを 少し 強く）
        for k in range(8): P('shk').put(shaker(rng, 0.085), t0 + k * S8 - 0.014, 0.35, (0.5, 0.85)[k % 2] * rng.uniform(0.8, 1.0))
        # ベース：1拍め → 2拍めの うら → 4拍め（5度 か 根音）
        for b_, m_, d_, g_ in ((0, root, 1.3, 1.0), (1.5, root, 1.2, 0.7), (3, ch[0] if ch[0] % 12 != root % 12 else root + 7, 0.9, 0.8)):
            P('bass').put(ebass(m_, d_ * B, 480.0), t0 + b_ * B, 0.0, g_)
        # ポロンと 弾く 弦：8分の 分散和音（3・3・2 の 頭を 少し 強く・左右に ゆれる）
        for k, i_ in enumerate((0, 2, 3, 2, 4, 3, 2, 3)):
            P('gtr').put(nylon(ch[i_]), t0 + k * S8 + rng.uniform(0, 0.006), 0.4 * math.sin(TAU * (bar * 8 + k) / 13.0), (1.0 if k in (0, 3, 6) else 0.7) * rng.uniform(0.9, 1.0))
        # やわらかい 弦：和音を のばす
        for i, m_ in enumerate((ch[1], ch[2], ch[3])): P('pad').put(pad_note(m_, S.bar * 0.98, 1300.0), t0, (-0.45, 0.45, 0.0)[i], 1.0)
        # B：マリンバが うらで 答える（2拍めと 4拍めの うら から 2つずつ）
        if sec == 2:
            for b_, i_ in ((1.5, 3), (2.0, 4), (3.5, 4), (3.75, 3)): P('mar').put(marimba(ch[i_] + 12), t0 + b_ * B, -0.35 if b_ < 3 else 0.35, 0.8)
        # ふし：笛。A' は 下に もう 1本（和音の 音）・B は 長い 音に 鈴
        for b_, m_, d_ in N_MEL.get(bar, []):
            if flute:                                                                  # 笛：長い 音の 入りに かざりの 音（上から すばやく）
                P('lead').put(fue(m_, d_ * B * 0.95, rng, 2 if d_ >= 1.5 and b_ == 0 else 0), t0 + b_ * B, 0.05, 1.0)
                if sec == 2 and d_ >= 1: P('low').put(ocarina(m_ - 12, d_ * B * 0.95, rng), t0 + b_ * B, -0.3, 0.8)      # B：オカリナが 1オクターブ下で よりそう
            else: P('lead').put(ocarina(m_, d_ * B * 0.95, rng), t0 + b_ * B, 0.05, 1.0)
            if sec == 1 and d_ >= 1: P('low').put(ocarina(under(m_, ch), d_ * B * 0.95, rng), t0 + b_ * B, -0.3, 1.0)
            if sec == 2 and d_ >= 1.5: P('glk').put(glock(m_ + 12, 0.7), t0 + b_ * B, 0.3, 0.7)
        # 区切り（8小節ごとの さいごの 小節）：雨の 棒が 流れて つぎへ
        if bar % 8 == 7: P('rain').put2(rainstick(rng, 1.9), t0 + 2 * B, 1.0)
    if birds:                                                                          # 鳥の 声：3〜5秒に 1回・左右と 遠さは ばらばら・同じ 鳥が つづかない（曲の つなぎ目を またいでも とぎれない）
        tt = 1.2; last = -1
        while tt < S.loop - 0.5:
            kd = int(rng.choice([k_ for k_ in range(4) if k_ != last])); last = kd; far = rng.uniform(0.35, 1.0)
            P('bird').put(amb.lp(bird(rng, kd), 9000 - 4500 * (1 - far), 1), tt, float(rng.uniform(-0.8, 0.8)), far)
            tt += rng.uniform(2.6, 5.2)
    W = {k: 10 ** (db / 20) * fn(st[k].fold()) for k, db, fn in (('drum', -10.5, norm), ('shk', -23, norm), ('bass', -10.5, norm), ('gtr', -11, norm), ('pad', -16.5, norm), ('lead', -9.5, norm),
                                                                 ('low', -18, anorm), ('mar', -15.5, anorm), ('glk', -20, anorm), ('rain', -15, anorm), ('bird', -19.5, anorm)) if birds or k != 'bird'}
    if STEMS_OUT is not None: STEMS_OUT.update(W)
    x = reverb(sum(W.values()), S.n, 1.5, 0.2, 31, 6500, 0.015)
    return master(x, -26.0, -12.0, 0.5), S


# ================================================================ テンゲルBGM 第4稿（鳥の 声 と 笛 だけ・もっと ゆったり）
#   ひと息ごとの ふし：(はじめ〈拍：ひと息の 頭から〉, 高さ, 長さ〈拍〉, かざり〈半音：その 高さから すばやく 入る〉)。ト長調の 5つの 音（ソ ラ シ レ ミ）だけ
Y_BARS = 16
Y_MEL = {
    0:  [(0, 71, 1.5), (1.5, 74, .5), (2, 76, 2), (4, 79, 3, 2), (7, 76, 1), (8, 74, 3.5)],
    4:  [(0, 76, 1.5), (1.5, 79, .5), (2, 81, 2), (4, 83, 2.5, 3), (6.5, 81, .5), (7, 79, 1), (8, 76, 1), (9, 74, 1), (10, 71, 2.5)],
    8:  [(0, 74, 1), (1, 79, 1), (2, 83, 2), (4, 86, 3, 2), (7, 83, 1), (8, 81, 1.5), (9.5, 79, .5), (10, 76, 3)],
    12: [(0, 76, 1.5), (1.5, 74, .5), (2, 71, 2), (4, 69, 1.5), (5.5, 71, .5), (6, 74, 2, 2), (8, 67, 4)],
}


# 第5稿：太い 音の 笛を まぜる。(小節, はじめの 拍, 大きさ, ふし)。ふしの 形は Y_MEL と 同じ（はじめ〈拍〉, 高さ, 長さ〈拍〉, かざり）
Y2_THIN = [(0, 0, 1.0, Y_MEL[0]), (4, 4, 0.36, [(0, 79, 2.5)]), (4, 10, 0.4, [(0, 71, 2.5)]), (8, 0, 1.0, Y_MEL[8]), (12, 9, 0.36, [(0, 79, 3)])]
Y2_THICK = [(0, 4, 0.5, [(0, 67, 4), (4, 71, 3.5)]),
            (4, 0, 1.0, [(0, 64, 1.5), (1.5, 67, .5), (2, 69, 2), (4, 71, 2.5, 3), (6.5, 69, .5), (7, 67, 1), (8, 64, 1), (9, 62, 1), (10, 59, 2.5)]),
            (8, 0, 0.5, [(0, 62, 2), (2, 67, 2), (4, 71, 3), (7, 67, 1), (8, 72, 2), (10, 67, 3)]),
            (12, 0, 1.0, Y_MEL[12])]
Y2_HORSE = ((13.5, 1), (46.5, -1))       # 馬が いちばん 近く なる 時（秒）・向き（1＝左から 右へ）
Y3_HORSE = ((13.5, 1, 2.0 / 3.0, 1.0, 1.0), (46.5, -1, 2.0 / 3.0, 1.0, 1.0), (31.0, -1, 0.6, 0.9, 0.5), (62.8, 1, 0.6, 0.9, 0.5))      # 第6稿の 馬：(いちばん 近い 時, 向き, 1歩の 秒, 音の 高さ, 大きさ)
Y3_NEIGH = {1: (1.8, 1.0, 0.35, 1.0), 3: (1.4, 0.9, -0.45, 0.7)}                                                              # 鳴き声：休みの 番号 → (長さ, 声の 高さ, 左右, 大きさ)
# 第6稿：もう 一段階 太い 笛（Y3_C：ふしの 1オクターブ下・2つめの ひと息は 太い 笛と 同じ 高さ）・かなり 低い 笛（Y3_D：長い 音で 下を ささえる）
Y3_C = [(0, 0, 1.0, [(0, 59, 1.5), (1.5, 62, .5), (2, 64, 2), (4, 67, 3, 2), (7, 64, 1), (8, 62, 3.5)]),
        (4, 0, 1.0, [(0, 64, 1.5), (1.5, 67, .5), (2, 69, 2), (4, 71, 2.5), (6.5, 69, .5), (7, 67, 1), (8, 64, 1), (9, 62, 1), (10, 59, 2.5)]),
        (8, 0, 1.0, [(0, 62, 1), (1, 67, 1), (2, 71, 2), (4, 74, 3, 2), (7, 71, 1), (8, 69, 1.5), (9.5, 67, .5), (10, 64, 3)]),
        (12, 0, 1.0, [(0, 64, 1.5), (1.5, 62, .5), (2, 59, 2), (4, 57, 1.5), (5.5, 59, .5), (6, 62, 2), (8, 55, 4)])]
Y3_D = [(0, 0, 1.0, [(0, 55, 4), (4, 52, 4), (8, 55, 3.5)]), (4, 0, 1.0, [(0, 52, 4), (4, 55, 4), (8, 52, 4.5)]),
        (8, 0, 1.0, [(0, 55, 4), (4, 59, 4), (8, 57, 2), (10, 52, 3)]), (12, 0, 1.0, [(0, 52, 4), (4, 50, 4), (8, 55, 4)])]
# 笛の 音色：0＝いままでの 笛・1＝太い 笛（第5稿）・2＝もう 一段階 太い 笛・3＝かなり 低い 笛（第6稿）
#   (入りの 秒, ゆれの 速さ, ゆれの 深さ, 2〜4倍音, 息の 音の 帯, 息の 大きさ, 吹きはじめの 息, 足す 倍音 [(何倍, もと, 大きさで ふえる ぶん, ずれ)], 1オクターブ下の 音, 高い 所を まるく する 高さ)
FUE_TONE = ((0.11, 4.7, 0.0062, (0.2, 0.18, 0.06, 0.1, 0.05), (1600.0, 7500.0), 0.085, 0.24, (), 0.0, 0.0),
            (0.16, 4.3, 0.0075, (0.5, 0.2, 0.26, 0.14, 0.12), (900.0, 4200.0), 0.05, 0.14, ((5, 0.05, 0.05, 0.9),), 0.0, 3600.0),
            (0.2, 4.0, 0.008, (0.62, 0.22, 0.36, 0.16, 0.2), (700.0, 3500.0), 0.04, 0.1, ((5, 0.1, 0.06, 0.9), (6, 0.05, 0.03, 0.4)), 0.2, 3000.0),
            (0.26, 3.8, 0.005, (0.7, 0.2, 0.45, 0.15, 0.3), (500.0, 2600.0), 0.05, 0.12, ((5, 0.2, 0.05, 0.9), (6, 0.12, 0.03, 0.4), (7, 0.06, 0.0, 1.3)), 0.0, 2400.0))


def hoof(rng, f=1.0):
    """ひづめ 1つ（土の 地面を うつ「ポクッ」）：低い ドッ ＋ 木を たたく ような 胴（520・960Hz あたり：電話の スピーカーでも 聞こえる 高さ）＋ 土の ザッ"""
    n = int(0.16 * SR); t = np.arange(n) / SR
    low = np.sin(TAU * np.cumsum(62 + 70 * np.exp(-t / 0.018)) / SR) * np.exp(-t / 0.05)
    body = np.sin(TAU * 520 * f * t) * np.exp(-t / 0.022) + 0.55 * np.sin(TAU * 960 * f * t + 0.7) * np.exp(-t / 0.014)
    grit = amb.bp(rng.normal(0, 1, n), 700.0, 3200.0, 1) * np.exp(-t / 0.016)
    y = 0.8 * low + 0.75 * body + 0.28 * grit; k = int(0.0015 * SR); y[:k] *= np.linspace(0, 1, k)
    return fade(y, 0.0005, 0.03)


def neigh(rng, dur=1.8, k=1.0):
    """馬の 鳴き声（ヒヒーン）：高い 声で 入って すぐ いちばん 高く なり、ふるえながら（1秒に 11〜13回：高さも 大きさも）だんだん 低く なって、さいごは 低い「ブルルッ」。
       声の もとは 倍音の 多い 音 2つ（低い 方と、その 2.3倍 あたりの 高い 方が いっしょに 鳴る）＋ 息。口と のどの ひびき（1.1・2.4・3.9kHz あたり）を つける"""
    from scipy.ndimage import gaussian_filter1d
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    f0 = gaussian_filter1d(np.interp(u, [0, 0.07, 0.16, 0.35, 0.55, 0.75, 0.9, 1.0], np.array([700.0, 930, 1000, 860, 700, 540, 400, 320]) * k), 0.012 * SR)
    pm = TAU * np.cumsum(11.0 + 2.5 * u) / SR
    f = f0 * (1 + np.interp(u, [0, 0.12, 0.3, 0.8, 1], [0.0, 0.012, 0.045, 0.085, 0.06]) * np.sin(pm)) * (1 + 0.25 * amb.lp(rng.normal(0, 1, n), 30, 1))
    am = 1 - np.interp(u, [0, 0.12, 0.3, 0.8, 1], [0.0, 0.1, 0.42, 0.62, 0.5]) * (0.5 - 0.5 * np.sin(pm + 0.8))
    x = saw(f, n, 7000.0, 1.0) + saw(f * 2.31, n, 7000.0, 1.3) * np.interp(u, [0, 0.1, 0.6, 0.8, 1], [0.3, 0.55, 0.45, 0.12, 0.0])
    x = x + amb.bp(rng.normal(0, 1, n), 1500.0, 6000.0, 1) * (0.12 + 0.15 * u)
    y = 0.5 * amb.bp(x, 800.0, 1500.0, 2) + 1.0 * amb.bp(x, 1700.0, 3100.0, 2) + 0.45 * amb.bp(x, 3100.0, 4800.0, 2) + 0.22 * x
    env = np.clip(t / 0.05, 0, 1) ** 1.5 * np.interp(u, [0, 0.1, 0.55, 0.85, 1.0], [0.7, 1.0, 0.85, 0.45, 0.0])
    fl = 1 - np.clip((u - 0.72) / 0.12, 0, 1) * 0.65 * (0.5 + 0.5 * np.sin(TAU * 24 * t))                 # さいごの ブルルッ（1秒に 24回 大きさが 切れる）
    return fade(y * env * am * fl, 0.004, 0.06)


def canter(stem, rng, tc, dirn, T=2.0 / 3.0, span=11.0, wid=4.2, fk=1.0, gain=1.0):
    """馬が 遠くから 走って きて、前を 通って、遠くへ（ゆったりした かけ足：1歩 T 秒に ひづめ 4つ「パカラッ」→ 少し 間）。tc＝いちばん 近い 時（秒）・dirn＝1 なら 左から 右へ"""
    for k in range(int(math.ceil((tc - span) / T)), int(math.floor((tc + span) / T)) + 1):
        for dt_, g_, f_ in ((0.0, 0.8, 0.92), (0.145, 1.0, 1.0), (0.162, 0.7, 1.08), (0.3, 0.9, 1.15)):      # うしろ足 → ななめの 2本（ほぼ 同時）→ 前足（少し 高い 音）
            tt = k * T + dt_ + float(rng.uniform(-0.008, 0.008)); d = tt - tc
            g = 1.0 / (1 + (d / wid) ** 2) * (0.5 + 0.5 * math.cos(math.pi * min(1.0, abs(d) / span)))          # 近いほど 大きい・はしで なめらかに 消える
            x = amb.lp(hoof(rng, f_ * fk * float(rng.uniform(0.96, 1.04))), 700 + 3600 * g ** 0.7, 1)            # 遠い 間は こもる
            stem.put(x, tt, dirn * 0.85 * math.tanh(d / (wid * 1.1)), gain * g * g_ * float(rng.uniform(0.85, 1.0)))


def arms(x):
    """鳴って いる 所 だけの 大きさ（anorm と 同じ 測り方）"""
    k = int(0.05 * SR); nf = x.shape[1] // k; p = (x[:, :nf * k] ** 2).reshape(2, nf, k).mean((0, 2)); act = p > p.max() * 1e-3
    return max(math.sqrt(float(p[act].mean())) if act.any() else 0.0, 1e-12)


def fue_line(notes, B, rng, thick=False, slow=False):
    """笛の ひと息（ゆったり 吹く）：音と 音を 切らずに つなげる（高さは すべる・つなぎ目で 息を ほんの 少し ぬく）・長い 音は ふくらんで から ゆれる・ひと息の さいごの 音は ゆっくり 小さく。
       notes＝[(はじめ〈拍〉, 高さ, 長さ〈拍〉, かざり)]。高さと 大きさの 線は 1秒に 2000こ の 点で 作って なめらかに して から 音に する。
       slow＝もっと ゆっくり 吹く（第9稿：かざりの 音なし・音の 移り変わりを なめらかに・入りを やわらかく・ゆれを 少し ゆっくり）。
       thick＝太い 音の 笛（第5稿）：倍音が 多い・息の 音は 少なく 低め・入りは もっと やわらかく・ゆれは ゆっくり・高い 所を 少し まるく"""
    att, rate0, vdep, H_, brf, brg, brb, more, sub, lpf = FUE_TONE[int(thick)]      # thick：False／True（太い 笛）／2（もう 一段階 太い 笛）／3（かなり 低い 笛）
    CR = 2000; T = max(n_[0] + n_[2] for n_ in notes) * B; nc = int((T + 0.5) * CR); semi = np.full(nc, float(notes[0][1])); amp = np.zeros(nc); vd = np.zeros(nc); art = np.zeros(nc)
    for i, n_ in enumerate(notes):
        b_, m_, d_ = n_[:3]; g_ = n_[3] if len(n_) > 3 else 0
        i0 = int(b_ * B * CR); i1 = int((b_ + d_) * B * CR); nx = int(notes[i + 1][0] * B * CR) if i + 1 < len(notes) else nc
        semi[i0:nx] = m_
        if g_ and not slow: semi[i0:i0 + int(0.08 * CR)] = m_ + g_
        k = i1 - i0; u = np.linspace(0, 1, k); dur = d_ * B; last = i + 1 == len(notes)
        if last: e = np.where(u < 0.3, 0.8 + 0.2 * u / 0.3, 1.0 - 0.86 * (np.clip(u - 0.3, 0, 1) / 0.7) ** 1.5)       # さいごの 音：少し ふくらんで から ゆっくり 小さく（ひびきの 中へ 消える）
        elif dur >= 1.8: e = 0.78 + 0.22 * np.sin(np.pi * u ** 0.8)                                                # 長い 音：まん中で ふくらむ
        else: e = np.full(k, 0.84)
        amp[i0:i1] = e
        if i: amp[i0 - int(0.02 * CR):i0 + int(0.03 * CR)] *= (0.84 if slow else 0.72); art[i0:i0 + int(0.03 * CR)] = 1.0      # つなぎ目：息を ほんの 少し ぬいて 入れ直す
        if dur >= 1.2: vd[i0:i1] = np.clip((np.arange(k) / CR - 0.45) / 0.8, 0, 1) * (np.clip(1.5 - u, 0.35, 1) if last else 1.0)      # ゆれ：0.45秒 たって から だんだん 深く
    from scipy.ndimage import gaussian_filter1d
    semi = gaussian_filter1d(semi, (0.032 if slow else 0.014) * CR); amp = gaussian_filter1d(amp, (0.055 if slow else 0.03) * CR); vd = gaussian_filter1d(vd, 0.06 * CR); art = gaussian_filter1d(art, 0.012 * CR)
    if slow: att = att * 1.7
    amp[:int(0.4 * CR)] *= np.clip(np.arange(int(0.4 * CR)) / (att * CR), 0, 1) ** 1.5                                 # 吹きはじめ：やわらかく 入る（0.11秒・太い 笛は 0.16秒）
    n = int(nc * SR / CR); t = np.arange(n) / SR; tc = np.arange(nc) / CR; up = lambda c: np.interp(t, tc, c)
    semi, amp, vd, art = up(semi), up(amp), up(vd), up(art)
    if slow: rate0 = rate0 * 0.88
    rate = rate0 + 5.0 * amb.lp(rng.normal(0, 1, n), 0.7, 1); pv = TAU * np.cumsum(rate) / SR                         # ゆれの 速さ（1秒に 4.7回 くらい・ゆっくり かわる）
    f = 440.0 * 2 ** ((semi - 0.22 * np.exp(-t / 0.05) - 69) / 12) * (1 + vdep * vd * np.sin(pv))                     # 吹きはじめは ほんの 少し 低い 所から
    ph = TAU * np.cumsum(f) / SR; a = amp * (1 + 0.1 * vd * np.sin(pv + 0.6)) * np.clip(1 + 0.45 * amb.lp(rng.normal(0, 1, n), 7, 2), 0.75, 1.25)
    y = np.sin(ph) + (H_[0] + H_[1] * amp) * np.sin(2 * ph + 0.3) + (H_[2] + H_[3] * amp) * np.sin(3 * ph) + H_[4] * amp * np.sin(4 * ph)
    for k_, c0, c1, p_ in more: y = y + (c0 + c1 * amp) * np.sin(k_ * ph + p_)
    if sub: y = y + sub * np.sin(0.5 * ph)
    br = amb.bp(rng.normal(0, 1, n), brf[0], brf[1], 1) * (brg + brb * np.exp(-t / 0.06) + 0.1 * art) * np.maximum(amp, 0) ** 0.75      # 息の 音（吹きはじめと つなぎ目で 少し 多い・音が 小さく なると いっしょに 消える）
    return amb.lp(y * a + br, lpf, 1) if thick else y * a + br


# 第7稿：弓で ひく 弦の 音（バイオリンの ような 音）。胴の ひびき＝(山の 高さ Hz, するどさ, 大きさ dB)・lp＝高い 所を 落とす 高さ・rate／vdep＝ゆれの 速さ／深さ・noise＝弓の ざらつき・att＝弓の 入り（秒）・tilt＝倍音の 落ち方
VN_TONE = {
    'vn': dict(pk=((285, 5, 5), (470, 4, 6), (560, 5, 4), (1100, 2.5, 2), (2600, 1.3, 7), (3400, 2.5, 3)), lp=6000.0, rate=5.9, vdep=0.0105, noise=0.035, att=0.07, tilt=1.05),
    'va': dict(pk=((225, 5, 5), (380, 4, 6), (480, 5, 3), (900, 2.5, 2), (2000, 1.3, 6), (2900, 2.5, 2)), lp=4800.0, rate=5.6, vdep=0.0095, noise=0.03, att=0.09, tilt=1.1),
    'vc': dict(pk=((105, 4, 4), (180, 4, 6), (260, 4, 5), (520, 2.5, 3), (1250, 1.4, 6), (2100, 2.5, 2)), lp=3800.0, rate=5.2, vdep=0.008, noise=0.03, att=0.11, tilt=1.1),
}


def peak_eq(x, f0, q, gdb):
    """ある 高さの まわり だけ 強める（胴の ひびきの 山 1つ）"""
    A = 10 ** (gdb / 40); w0 = TAU * f0 / SR; al = math.sin(w0) / (2 * q); c = math.cos(w0)
    return signal.lfilter([1 + al * A, -2 * c, 1 - al * A], [1 + al / A, -2 * c, 1 - al / A], x)


def vn_line(notes, B, rng, kind='vn'):
    """弓で ひく 弦の ひと弓（バイオリンの ような 音）：notes は fue_line と 同じ 形。音と 音の 間は 指を すべらせて つなぐ・長い 音は ふくらんで ゆれる・さいごの 音は ゆっくり 小さく"""
    from scipy.ndimage import gaussian_filter1d
    Tn = VN_TONE[kind]; CR = 2000; T = max(n_[0] + n_[2] for n_ in notes) * B; nc = int((T + 0.5) * CR); semi = np.full(nc, float(notes[0][1])); amp = np.zeros(nc); vd = np.zeros(nc); art = np.zeros(nc)
    for i, n_ in enumerate(notes):
        b_, m_, d_ = n_[:3]; g_ = n_[3] if len(n_) > 3 else 0
        i0 = int(b_ * B * CR); i1 = int((b_ + d_) * B * CR); nx = int(notes[i + 1][0] * B * CR) if i + 1 < len(notes) else nc
        semi[i0:nx] = m_
        if g_: semi[i0:i0 + int(0.09 * CR)] = m_ + g_
        k = i1 - i0; u = np.linspace(0, 1, k); dur = d_ * B; last = i + 1 == len(notes)
        if last: e = np.where(u < 0.3, 0.8 + 0.2 * u / 0.3, 1.0 - 0.86 * (np.clip(u - 0.3, 0, 1) / 0.7) ** 1.5)
        elif dur >= 1.8: e = 0.76 + 0.24 * np.sin(np.pi * u ** 0.8)
        else: e = np.full(k, 0.86)
        amp[i0:i1] = e
        if i: amp[i0 - int(0.02 * CR):i0 + int(0.03 * CR)] *= 0.86; art[i0:i0 + int(0.04 * CR)] = 1.0                 # つなぎ目：弓は 止めない（ほんの 少し ぬく だけ）
        if dur >= 1.0: vd[i0:i1] = np.clip((np.arange(k) / CR - 0.3) / 0.6, 0, 1) * (np.clip(1.5 - u, 0.35, 1) if last else 1.0)       # ゆれ：0.3秒 たって から
    semi = gaussian_filter1d(semi, 0.024 * CR); amp = gaussian_filter1d(amp, 0.03 * CR); vd = gaussian_filter1d(vd, 0.06 * CR); art = gaussian_filter1d(art, 0.015 * CR)
    amp[:int(0.4 * CR)] *= np.clip(np.arange(int(0.4 * CR)) / (Tn['att'] * CR), 0, 1) ** 1.3
    n = int(nc * SR / CR); t = np.arange(n) / SR; tc = np.arange(nc) / CR; up = lambda c: np.interp(t, tc, c)
    semi, amp, vd, art = up(semi), up(amp), up(vd), up(art)
    rate = Tn['rate'] + 6.0 * amb.lp(rng.normal(0, 1, n), 0.7, 1); pv = TAU * np.cumsum(rate) / SR
    f = 440.0 * 2 ** ((semi - 69) / 12) * (1 + Tn['vdep'] * vd * np.sin(pv)) * (1 + 0.06 * amb.lp(rng.normal(0, 1, n), 12, 1))      # ゆれ ＋ 指と 弓の 小さな ゆらぎ
    ph = TAU * np.cumsum(f) / SR; y = np.zeros(n); ex = Tn['tilt'] + 0.4 * (1 - amp)                                     # 小さく ひく ほど 倍音が 少ない（やわらかい）
    for k_ in range(1, int(9000.0 / float(f.min())) + 1):
        w = np.clip((9000.0 - k_ * f) / 1500.0, 0, 1)
        if not w.any(): break
        y += np.sin(k_ * ph) * w * np.exp(-math.log(k_) * ex)
    a = amp * np.clip(1 + 0.35 * amb.lp(rng.normal(0, 1, n), 6, 2), 0.8, 1.2)
    br = amb.bp(rng.normal(0, 1, n), 1500.0, 7000.0, 1) * (Tn['noise'] + 0.09 * np.exp(-t / 0.05) + 0.05 * art) * np.maximum(amp, 0) ** 0.8      # 弓が こする ざらつき（入りと つなぎ目で 少し 多い）
    x = y * a + br
    for f0_, q_, g_ in Tn['pk']: x = peak_eq(x, f0_, q_, g_)
    return amb.lp(x, Tn['lp'], 2)


def wind_gust(rng, dur=8.0, peak=0.5, flow=1):
    """風 ひと吹き → ステレオ（2, n）。そよ風が 草や 木の 葉を わたる「サァー…」（高い 所）＋ 風の 通る「ヒュゥ…」（強く なると 少し 高く なる）。
       ゆっくり 強く なって（peak＝いちばん 強い 所：長さの 0〜1）ゆっくり やむ・強さに むら・flow＝1 なら 左から 右へ 流れる"""
    n = int(dur * SR); u = np.arange(n) / n
    env = np.where(u < peak, 0.5 - 0.5 * np.cos(np.pi * u / peak), 0.5 + 0.5 * np.cos(np.pi * (u - peak) / (1 - peak))) ** 1.6
    out = np.zeros((2, n)); BANDS = ((250.0, 450.0), (450.0, 800.0), (800.0, 1400.0), (1400.0, 2400.0))
    for c in range(2):
        m = amb.lp(rng.normal(0, 1, n), 1.2, 2); fl = np.clip(1 + 0.3 * m / (m.std() + 1e-12), 0.5, 1.6)                 # 強さの むら
        nz = rng.normal(0, 1, n); ctr = np.log2(420.0) + 1.1 * env * fl; wh = np.zeros(n)                                  # ヒュゥ…：強く なると 高く（420 → 900Hz あたり）
        for lo, hi in BANDS: wh += amb.bp(nz, lo, hi, 2) * np.exp(-((math.log2(math.sqrt(lo * hi)) - ctr) / 0.6) ** 2)
        m2 = amb.lp(rng.normal(0, 1, n), 4.0, 2); rs = amb.bp(rng.normal(0, 1, n), 1800.0, 5500.0, 1) * env ** 0.5 * np.clip(1 + 0.4 * m2 / (m2.std() + 1e-12), 0.4, 1.5)      # サァー…（葉の 音）
        side = (1 - 0.35 * u) if (c == 0) == (flow > 0) else (0.65 + 0.35 * u)                                             # 左右に 流れる
        out[c] = (2.2 * wh + 0.35 * rs) * env * fl * side
    return out


def yuttari(ver=4):
    """第4稿：笛 1本 と 鳥の 声 だけ。60 BPM・16小節（64秒）。ver=5＝第5稿：太い 音の 笛 と 馬の 走る 音を まぜる・ver=6＝第6稿：もう 一段階 太い 笛 と かなり 低い 笛も 重ねる"""
    v5 = ver >= 5; v6 = ver >= 6; v7 = ver == 7; v8 = ver >= 8; v9 = ver >= 9            # 第7稿 だけ 弦の 音（第8稿は 笛に もどす）・第9稿は 笛を もっと ゆっくり
    S = Song(36 if v9 else 48 if v8 else 60, Y_BARS, 5.0); rng = np.random.default_rng({4: 1909, 5: 1925, 6: 1941, 7: 1957, 8: 1973, 9: 1989}[ver]); B = S.beat
    st = {k: S.stem() for k in ('fue near far' + (' fue2 hoof ref1 ref2' if v5 else '') + (' fue3 fue4 ref3 ref4 neigh' if v6 else '')).split()}; P = st.__getitem__; rest = []      # rest＝笛が 休んで いる 間（秒：はじめ, おわり）
    for bar, notes in Y_MEL.items():
        if not v5: P('fue').put(fue_line(notes, B, rng), S.at(bar), 0.04, 1.0)
        rest.append((S.at(bar) + max(n_[0] + n_[2] for n_ in notes) * B - 0.3, S.at(bar + 4) - 0.5))
    if v5:
        for nm, ref, pan, thick, score in (('fue', 'ref1', 0.12, False, Y2_THIN), ('fue2', 'ref2', -0.12, True, Y2_THICK)) + ((('fue3', 'ref3', -0.3, 2, Y3_C), ('fue4', 'ref4', 0.05, 3, Y3_D)) if v6 else ()):      # いままでの 笛は 少し 右・太い 笛は 少し 左・もっと 太い 笛は 左・低い 笛は まん中
            for bar, b0, g_, notes in score:
                x = vn_line(notes, B, rng, ('vn', 'va', 'vc', 'vc')[int(thick)]) if v7 else fue_line(notes, B, rng, thick, v9); P(nm).put(x, S.at(bar, b0), pan, g_)
                if g_ == 1.0: P(ref).put(x, S.at(bar, b0), pan, 1.0)                        # 大きさを そろえる もと（ふしを 吹く ひと息 だけ）
        if v6:
            for tc, dirn, T_, fk, g_ in Y3_HORSE: canter(P('hoof'), rng, tc * B, dirn, T_ * (1.12 if v9 else 1.08 if v8 else 1.0), 11.0, 4.2, fk, g_)      # 第8稿：時刻は 拍に 合わせて のびる・足も ゆっくり
        else:
            for tc, dirn in Y2_HORSE: canter(P('hoof'), rng, tc, dirn)
    # 鳥：笛が 休んで いる 間 ＝ 鳥の 番（近くの 鳥が 鳴く → 反対側の 鳥が 答える → … と、つぎの 笛が 入る 少し 前まで つづく）。声の ならびは 休みごとに かえる（空の 鳥・ホー… は 1回ずつ）
    def blen(x): return (int(np.nonzero(np.abs(x) > 1e-4)[0][-1]) + 1) / SR
    for idx, ((a_, b_), seq) in enumerate(zip(rest, ((5, 0, 2, 1, 5, 0), (3, 1, 0, 2), (2, 5, 0, 1, 2), (4, 1, 5, 0, 2)) if v9 else ((5, 0, 2, 1), (3, 1, 0), (2, 5, 0), (4, 1, 5, 0)))):      # 第9稿：休みが 長い ぶん 声を 足す
        side = 1 if idx % 2 == 0 else -1; tt = a_ + 0.15
        if v6 and idx in Y3_NEIGH:                                                         # 第6稿：この 休みは 馬の 鳴き声から（鳥は その あと）
            nd_, nk_, npan, ng_ = Y3_NEIGH[idx]; P('neigh').put(neigh(rng, nd_, nk_), tt, npan, ng_); tt += nd_ + 0.1
        for j, kd in enumerate(seq):
            if tt > b_ + 0.2: break                                                        # つぎの 笛が 入る 0.3秒前 までに 鳴きはじめる
            x = bird(rng, kd); sky = kd == 4                                               # 空の 鳥（ピー ヒョロロロ）は 遠く
            P('far' if sky else 'near').put(amb.lp(x, 5200 if sky else (9000, 7500)[j % 2], 1), tt, (-0.55, 0.6, -0.2, 0.35)[j % 4] * side, 1.6 if sky else (1.0, 0.72, 0.85, 0.65)[j % 4])
            tt += blen(x) + float(rng.uniform(0.3, 0.55))
    # 笛が 鳴って いる 間：遠くで 小さく（3.5〜5.5秒に 1回・笛の 入りの 1秒は あける）
    tt = 2.4; last = -1
    while tt < S.loop - 0.5:
        if not any(a_ - 1.9 < tt < b_ + 1.0 for a_, b_ in rest):
            kd = int(rng.choice([k_ for k_ in (0, 1, 2, 5) if k_ != last])); last = kd
            P('far').put(amb.lp(bird(rng, kd), 4800, 1), tt, float(rng.uniform(-0.85, 0.85)), float(rng.uniform(0.45, 0.8)))
        tt += float(rng.uniform(3.5, 5.5))
    if v5:
        hf = st['hoof'].fold(); i0 = int((Y2_HORSE[0][0] * B - 2) * SR); hr = math.sqrt(float(np.mean(hf[:, i0:i0 + int(4 * SR)] ** 2)))      # 馬：いちばん 近い 4秒の 大きさで そろえる
        W = {'fue': 10 ** (-10 / 20) * st['fue'].fold() / arms(st['ref1'].fold()), 'fue2': 10 ** (Y5_THICK / 20) * st['fue2'].fold() / arms(st['ref2'].fold()),
             'near': 10 ** (-17.5 / 20) * anorm(st['near'].fold()), 'far': 10 ** (-25 / 20) * anorm(st['far'].fold()), 'hoof': 10 ** (Y5_HOOF / 20) * hf / max(hr, 1e-12)}
        if v6:
            W.update(fue3=10 ** (Y6_C / 20) * st['fue3'].fold() / arms(st['ref3'].fold()), fue4=10 ** (Y6_D / 20) * st['fue4'].fold() / arms(st['ref4'].fold()),
                     neigh=10 ** (Y6_NEIGH / 20) * anorm(st['neigh'].fold()), hoof=10 ** (Y6_HOOF / 20) * hf / max(hr, 1e-12))
        if STEMS_OUT is not None: STEMS_OUT.update(W)
        x = (reverb(W['fue'], S.n, 3.2, 0.36, 41, 5200, 0.03) + reverb(W['fue2'], S.n, 3.2, 0.34, 44, 4200, 0.03) + reverb(W['near'], S.n, 2.2, 0.24, 42, 6000, 0.02)
             + reverb(W['far'], S.n, 2.8, 0.6, 43, 4500, 0.04) + reverb(W['hoof'], S.n, 1.8, 0.3, 45, 3500, 0.02))
        if v6: x = x + reverb(W['fue3'], S.n, 3.2, 0.32, 46, 3600, 0.03) + reverb(W['fue4'], S.n, 2.8, 0.28, 47, 2800, 0.03) + reverb(W['neigh'], S.n, 2.6, 0.5, 48, 4200, 0.035)
        if v8:                                                                             # 風：休みごとに ひと吹き ＋ ずっと うしろで ごく 小さく（輪の ように つながる：曲の つなぎ目を またぐ）
            wd = np.zeros((2, S.n))
            def blow(x_, at):
                idx = (int(at * SR) + np.arange(x_.shape[1])) % S.n; np.add.at(wd, (slice(None), idx), x_)
            for j, (a_, b_) in enumerate(rest):                                            # 笛の ひと息が おわる ころ から 吹いて、休みの はじめに いちばん 強く、休みの 間に やむ
                blow(wind_gust(rng, 9.5, 0.5, 1 if j % 2 == 0 else -1) * (1.0, 0.8, 0.9, 0.75)[j], a_ - 4.2)
            for j, bar in enumerate((1.5, 9.5)): blow(wind_gust(rng, 8.0, 0.45, -1 if j % 2 == 0 else 1) * 0.5, S.at(0) + bar * S.bar - 4.0)      # ひと息の とちゅうにも 弱い 風（1つめ・3つめ）
            pk = max(math.sqrt(float(np.mean(wd[:, i:i + 4 * SR] ** 2))) for i in range(0, S.n - 4 * SR, SR))          # いちばん 強い 4秒の 大きさで そろえる
            for j in range(8): blow(wind_gust(rng, S.loop / 4, 0.5, 1 if j % 2 else -1) * 0.2, S.loop * j / 8)           # うしろの 風（半分ずつ 重ねる ＝ とぎれない）
            wd = np.tanh(wd / (4 * max(pk, 1e-12))) * 4                                        # とがった 山を まるく（いちばん 強い 時の 大きさの 4倍 まで）
            W['wind'] = 10 ** (Y8_WIND / 20) * wd; x = x + W['wind']
            if STEMS_OUT is not None: STEMS_OUT['wind'] = W['wind']
        return master(x, Y9_RMS if v9 else Y8_RMS if v8 else Y7_RMS if v7 else Y6_RMS if v6 else Y5_RMS, -12.0, 0.3), S
    W = {'fue': 10 ** (-10 / 20) * anorm(st['fue'].fold()), 'near': 10 ** (-17.5 / 20) * anorm(st['near'].fold()), 'far': 10 ** (-25 / 20) * anorm(st['far'].fold())}
    if STEMS_OUT is not None: STEMS_OUT.update(W)
    x = reverb(W['fue'], S.n, 3.2, 0.36, 41, 5200, 0.03) + reverb(W['near'], S.n, 2.2, 0.24, 42, 6000, 0.02) + reverb(W['far'], S.n, 2.8, 0.6, 43, 4500, 0.04)
    return master(x, Y_RMS, -12.0, 0.3), S


Y_RMS = -30.0       # 全体の 大きさ（電話の スピーカーで 聞こえる 高さ〈300〜8000Hz〉の 大きさを 第3稿と そろえた：笛 だけ なので 低い 音が ない ぶん 数字は 小さい）
Y5_RMS, Y5_THICK, Y5_HOOF = -29.5, -10.0, -25.0      # 第5稿：全体の 大きさ・太い 笛（ふしの とき）・馬（いちばん 近い 時）
Y6_RMS, Y6_C, Y6_D, Y6_HOOF, Y6_NEIGH = -28.7, -13.0, -13.0, -22.0, -22.0      # 第6稿：全体の 大きさ・もう 一段階 太い 笛・かなり 低い 笛・馬の 走る 音（近くを 通る 時）・馬の 鳴き声
Y7_RMS = -28.2                                       # 第7稿：全体の 大きさ
Y8_RMS, Y8_WIND = -28.7, -21.0                        # 第8稿：全体の 大きさ・風（いちばん 強い 時）
Y9_RMS = -28.7                                       # 第9稿：全体の 大きさ
SONGS = {'tengel': tengel, 'divine2': divine2, 'tengel2': nodoka, 'tengel3': lambda: nodoka(88, True, True), 'tengel4': yuttari, 'tengel5': lambda: yuttari(5), 'tengel6': lambda: yuttari(6), 'tengel7': lambda: yuttari(7),
         'tengel8': lambda: yuttari(8), 'tengel9': lambda: yuttari(9)}

if __name__ == '__main__':
    y, S = SONGS[sys.argv[1]]()
    wavfile.write(sys.argv[2], SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))
    print(sys.argv[1], sys.argv[2], round(y.shape[1] / SR, 3), '秒', f'{S.bars}小節 {S.bpm}BPM', 'RMS %.1f dB' % (20 * math.log10(math.sqrt(float(np.mean(y ** 2))))), 'peak %.1f dB' % (20 * math.log10(float(np.abs(y).max()))))
