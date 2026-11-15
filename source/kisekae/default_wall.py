# 「いつもの」（デフォルト）の 壁紙の 絵を アプリに 入れる 形に する（第4.176版・まさちゃん 2026/11/16 01:26「いつもの(デフォルト)壁紙これにして！ バージョン2.1完全自動分析エンジンの文字だけ消して！」）
#   python3 kisekae/default_wall.py            … ios/wall_src/default_tenger.jpg（まさちゃんの 絵・1408×768）→ ios/kisekae_blobs/<名前>.webp（1170×480：判定タブの 上の絵・選ぶ 画面の 小さな絵）
#   python3 kisekae/default_wall.py --check    … できて いる 絵が 今の もと・今の 決めごとで 作った ものか だけ 見る（ちがえば 1 で おわる）
#   もと（ios/wall_src/）は **読む だけ**（上書きしない・消さない）。どちらの フォルダも リポジトリには 入れない（.gitignore）
#   する こと：
#     ① 金の 札「テンゲル」の 下の 小さい 字「バージョン 2.1 - 完全自動分析エンジン」だけ 消す（字は y 519〜537・x 772〜1112、その 下に 字の かげが y 546 まで）：
#        行ごとに、字の 左と 右の 背景の 色を まっすぐ つないで うめる（背景は なめらかな 濃い 青緑。札の 下の かげで 上ほど 暗い ので、上下では つながない）＋ もとの 絵と 同じ くらいの ざらつき。
#        うめる 所の 上下 3行は もとの 絵と まぜる。ほかの 所は 1点も さわらない
#     ② 上の絵の 形（390:160）に 切る：横は ぜんぶ（左右の 細い 線の かざりも）・たては 中身（エンブレム〜字）が まん中に 来る 578px（y 104〜682：上下の はしの 帯だけ 切る）
#     ③ 1170×480（390×160 の 3倍：ほかの 壁紙の 止まった 絵と 同じ 大きさ）に して WebP に する
#   できた 絵の 名前＝中身の MD5（32けた）.webp。同じ 名前が もう あれば 書かない（前の 絵は 消さない・上書きしない）。その 名前を build_kisekae.py の DEFAULT_WALL に 書く
import hashlib, io, os, sys
import numpy as np
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
SRC = os.path.join(W, 'ios', 'wall_src', 'default_tenger.jpg'); OUT = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
SRC_SIZE, SRC_SHA1 = (1408, 768), 'a824581c531a35041a82ce944afd302e5ac7742a'
FILL = (513, 551, 764, 1122)       # うめる 所（上・下・左・右：どれも 入る）
CROP = (0, 104, 1408, 682)         # 切る 所（左・上・右・下）
SIZE = (1170, 480)
Q = dict(quality=88, method=6)


def sha1(p):
    return hashlib.sha1(open(p, 'rb').read()).hexdigest()


def make():
    """もとの 絵 → (WebP の 中身, できた 絵)。もとの 絵が ない／ちがう ときは 止める"""
    if not os.path.isfile(SRC): sys.exit('※ もとの 絵が ない：' + SRC)
    if sha1(SRC) != SRC_SHA1: sys.exit('※ もとの 絵が かわって いる（うめる 所・切る 所を 見直してね）：' + SRC)
    im = Image.open(SRC).convert('RGB'); assert im.size == SRC_SIZE, im.size
    a = np.asarray(im).astype(np.float32); b = a.copy()
    y0, y1, x0, x1 = FILL; n = x1 - x0 + 1
    rng = np.random.default_rng(20261116)
    ref = lambda y, xa, xb: a[y - 1:y + 2, xa:xb].reshape(-1, 3).mean(axis=0)      # その 行と 上下 1行の 平均（線に ならない ように）
    t = np.linspace(0, 1, n)[:, None]
    for y in range(y0, y1 + 1):
        L, R = ref(y, x0 - 18, x0 - 2), ref(y, x1 + 2, x1 + 18)
        b[y, x0:x1 + 1] = L * (1 - t) + R * t + rng.normal(0, 0.7, (n, 3))
    for k in range(3):                                                             # 上下 3行は もとの 絵と まぜる
        w = (k + 1) / 4
        for y in (y0 + k, y1 - k): b[y, x0:x1 + 1] = a[y, x0:x1 + 1] * (1 - w) + b[y, x0:x1 + 1] * w
    out = Image.fromarray(np.clip(b + 0.5, 0, 255).astype(np.uint8)).crop(CROP).resize(SIZE, Image.LANCZOS)
    buf = io.BytesIO(); out.save(buf, 'WEBP', **Q)
    return buf.getvalue(), out


def blob_id():
    return hashlib.md5(make()[0]).hexdigest()


if __name__ == '__main__':
    data, im = make(); bid = hashlib.md5(data).hexdigest(); p = os.path.join(OUT, bid + '.webp')
    if '--check' in sys.argv:
        ok = os.path.isfile(p) and open(p, 'rb').read() == data
        sys.path.insert(0, H)
        import build_kisekae as K
        same = K.DEFAULT_WALL == bid
        print('いつもの の 壁紙：', bid + '.webp', 'ある' if ok else 'ない／ちがう', '・build_kisekae.py の DEFAULT_WALL と', '同じ' if same else 'ちがう')
        sys.exit(0 if ok and same else 1)
    os.makedirs(OUT, exist_ok=True)
    if os.path.isfile(p): print('もう ある（書かない）：', p)
    else:
        open(p, 'wb').write(data); print('書いた：', p, len(data), 'バイト', im.size)
    print('build_kisekae.py の DEFAULT_WALL =', repr(bid))
