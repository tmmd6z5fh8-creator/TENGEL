"""テンゲル（780×320）：アプリの説明書の上の絵（manual/banner.webp：テンゲルの絵）を、着せ替えの壁紙の大きさにする
   - 絵そのものは変えない（金と紺の盾のエンブレム・騎手を乗せて走る馬・TENGER の金の文字・「テンゲル」の金の札）
   - 下の小さな「バージョン …」の行だけ消す（まわりの紺でぬりつぶす：App Store 版に決まった版の名前を出さないため）
   - 内側のパネルの中から、横長（780×320）に切り出す（パネルのふちの線は入れない）
   python3 flat/tengel_banner.py <出力.webp> [元の絵]（元の絵は、なければ manual/tools/banner_src.webp＝前の 1200×655）
   ※ 第4.59版から アプリの マスター帯の 壁紙と PUSH の 絵は manual/tools/banner_hd.py（文字を 描き直した 2340×960・1800×982）で 作る。ここは 見本（キャンバス）と 数字の 場所の 元"""
import sys, os
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
from style2d import save_webp

W, Hh = 780, 320
SRC = os.path.join(HERE, '..', '..', 'manual', 'tools', 'banner_src.webp')   # 元の 絵（1200×655・文字は 前の まま）。第4.59版から 説明書の 上の絵（manual/banner.webp）は 2400×1310 の 描き直した 絵（manual/tools/banner_hd.py）で、アプリの 壁紙と PUSH の 絵も そこから 作る
CROP = (82, 124, 1118, 549)          # 元の絵（1200×655）から切り出す所：パネル（x 66〜1134・y 〜581）の中で、絵の中身がまん中に来る（下のすみの丸みは入れない）
VER = (600, 436, 990, 470)           # 「バージョン …」の行のある所


def clean_full(src=SRC):
    """「バージョン …」の行を消した 元の絵（1200×655・BGR：外の すじの わくも ふくむ）と 消した所のマスク。
       的中ボタン（マスター帯の 長方形の PUSH：flat/tengel_run.py）は この絵を そのまま 使う"""
    im = cv2.imread(src, cv2.IMREAD_COLOR)
    assert im is not None and im.shape[:2] == (655, 1200), (src, None if im is None else im.shape)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    x0, y0, x1, y1 = VER
    sub = g[y0:y1, x0:x1]
    base = cv2.morphologyEx(sub, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))       # 細い明るい文字をとった地の明るさ
    m = ((sub.astype(np.int16) - base.astype(np.int16)) > 14).astype(np.uint8)
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    mask = np.zeros(g.shape, np.uint8)
    mask[y0:y1, x0:x1] = m * 255
    return cv2.inpaint(im, mask, 6, cv2.INPAINT_TELEA), mask


def clean_crop(src=SRC):
    """「バージョン …」の行を消して 切り出した絵（元の大きさ 1036×425・BGR）と 消した所のマスク（元の絵の大きさ）。
       壁紙の 数字（flat/tengel_run.py）も この絵から さがす"""
    clean, mask = clean_full(src)
    cx0, cy0, cx1, cy1 = CROP
    return clean[cy0:cy1, cx0:cx1], mask


def make(src=SRC):
    crop, mask = clean_crop(src)
    out = cv2.resize(crop, (W, Hh), interpolation=cv2.INTER_AREA)
    return out[..., ::-1].astype(np.float32) / 255.0, mask


if __name__ == '__main__':
    out = sys.argv[1]
    src = sys.argv[2] if len(sys.argv) > 2 else SRC
    img, _ = make(src)
    save_webp(np.clip(img, 0, 1), out)
