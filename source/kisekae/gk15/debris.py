# 神様極的中：ばくはつの かけらを、画面に 近づく ほど うすく 写す（第4.215版・まさちゃん 2026/11/24 01:35 ②）
#   「爆発後の 破片の 演出、濃く 残りすぎて 不自然 → 奥から 画面に 向かって 散らばる タイミングで、画面に 近く なるに 連れて、破片を 薄く 写す」
#   かけらは ばくはつの まん中から 外へ（＝画面の 手前へ）とぶ：あとの コマ ほど・まん中から はなれた かけら ほど 画面に 近い。
#   かけらの ない 白い 光の 面（bg）を 作って（かけらを うめる：大きな closing → ならす）、かけらの 暗さ（bg − もと）を k 倍に する（k＝1 そのまま・0 で 消える）
#   python3 debris.py     … debris_out/<コマ>.png（116〜130）を 作る（GK15_WORK＝作業フォルダ：src/ に 第14稿の コマ）
import numpy as np, cv2, os, sys
D = os.environ.get('GK15_WORK', '/home/claude/work/v215/gk')
CENTER = (385.0, 650.0)                                          # ばくはつの まん中（画素）
# コマごとの 倍率（大きな かけら）：116 から 少しずつ うすく → 124 で 3わり → 130 で 1わり（もとの 動画も 124 から 自分で うすく なる ＝ かけ合わせ）
KT = {115: 1.0, 116: .95, 117: .86, 118: .76, 119: .66, 120: .57, 121: .49, 122: .42, 123: .36, 124: .31, 125: .27, 126: .23, 127: .20, 128: .17, 129: .14, 130: .11}
LO, HI = 116, 130
R0, R1, K_EDGE = 200.0, 750.0, .40                              # まん中から R0 まで：コマの 倍率 だけ／R1 より 外（＝画面に いちばん 近い）：さらに (1 − K_EDGE) 倍
SMALL_POW = .5                                                  # 小石・細い すじ（小さい ＝ 遠い）は ゆるく：倍率の 0.5乗（3わり → 5わり半）
D_KEEP = 12.0                                                   # 光の すじ（ばくはつの 放射の あわい かげ）の 深さ：ここまでは うすく しない
R_SMALL = 9                                                     # これより 細い 暗い もの（はば 18px より 下）＝ 小石・すじ・光の 細い 線


def background(F, r=36, s=4):
    """かけらの ない 面：1/4 に 小さく して、はば 288px より 細い 暗い もの（かけら・小石・すじ）を うめる → ならす → もとの 大きさ"""
    h, w = F.shape[:2]; sm = cv2.resize(F, (w // s, h // s), interpolation=cv2.INTER_AREA)
    cl = cv2.morphologyEx(sm, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    cl = cv2.GaussianBlur(cl, (0, 0), 5.0)
    return np.maximum(cv2.resize(cl, (w, h), interpolation=cv2.INTER_CUBIC), F)


def kmap(f, shape):
    y, x = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32); r = np.hypot(x - CENTER[0], y - CENTER[1])
    t = np.clip((r - R0) / (R1 - R0), 0, 1); t = t * t * (3 - 2 * t)
    return KT[f] * (1 - K_EDGE * t)


def fix(img, f):
    """大きな かけら（ぼやけた 暗い かたまり ＝ 画面に 近い）と 小さな もの（小石・すじ ＝ 遠い）を 分けて、べつの 倍率で うすく する"""
    if not LO <= f <= HI: return img
    F = img.astype(np.float32); bg = background(F)
    mid = cv2.morphologyEx(F, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * R_SMALL + 1, 2 * R_SMALL + 1)))   # 小さな ものを うめた 絵（大きな かけら だけ のこる）
    mid = np.minimum(np.maximum(cv2.GaussianBlur(mid, (0, 0), 1.2), F), bg)
    k = kmap(f, F.shape)[..., None]
    d = bg - mid; d = np.minimum(d, D_KEEP) + np.maximum(d - D_KEEP, 0) * k                       # 光の すじの あわい かげ（D_KEEP まで）は そのまま・それより 深い 暗さ（かけら）だけ k 倍
    out = bg - d - (mid - F) * np.power(k, SMALL_POW)
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    out = f'{D}/debris_out'; os.makedirs(out, exist_ok=True)
    for f in range(LO, HI + 1):
        o = fix(cv2.imread(f'{D}/src/{f:04d}.png'), f); cv2.imwrite(f'{out}/{f:04d}.png', o)
    print('ok', out)
