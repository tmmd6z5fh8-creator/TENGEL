# ルーレットの 高い 方が 当たった ときの テロップ「大量ポイント」の 絵と 音を アプリ用に 置く
#   （第4.159版・まさちゃん 2026/11/12 13:27「ルーレット高い方が当たった時に、プチュンしてまたルーレットの画面に戻ると変だから、光輝きながら獲得ポイントを表示するようにして！一枚目がテロップの画像！」
#     ・13:30「ドーン！！みたいな音と一緒にテロップ出して！」）
#   python3 kisekae/tc/telop_asset.py <まさちゃんの 絵（PNG・すき通し）> <音の フォルダ（kisekae/tc/snd/export_app.py <フォルダ> tc_se_doon の 出力）> [ios/tc_assets]
#   → tc_telop_big.webp：絵の まわりの 余白を 切って 幅 1110px（画面では 370pt ＝ 3倍の 画面で 1110px）・WebP 90・すき通しは ロスなし
#       ・まさちゃんの 絵の まわりに うすい 黄色の もや（すき通し 1〜8/255 が 5万 画素：黒い 画面に 重ねると うっすら 四角く 見える）→ 消す：
#         すき通し 16 以下は 0／うすい 画素（200 未満）は はっきり した 所（200 以上）から 3px より 遠ければ 0／12 画素 より 小さい かけらは 0
#       ・まん中の クリーム色の 板（ポイントを 書く 所）の 場所を 測って 出す（tc/tc_fx.js の TELOP.panel：絵の 幅・高さに 対する 割合）
#     tc_se_doon.m4a（ドーン！！：kisekae/tc/snd/sfx_push.py の doon_snd）
#   ・もとの 絵（まさちゃんの PNG）と できた ファイルは リポジトリに 入れない（ios/tc_assets/ は .gitignore）
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc/tc_fx.js の 名前も かえる）
#   ・kisekae/tc/collect_assets.py は 出す フォルダを 作り直す ので、走らせた あとは これを もう一度。足した あとは python3 kisekae/lite_assets.py
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
W_OUT, PAD, Q = 1110, 6, 90
A_MIN, A_SOLID, NEAR, SPECK = 16, 200, 3, 12
SOUNDS = ('tc_se_doon.m4a',)


def clean(src):
    """うすい もやを 消して、絵の ある 所＋余白 PAD で 切る → RGBA（uint8）・消した 画素の 数"""
    import cv2
    p = np.array(Image.open(src).convert('RGBA')); a = p[..., 3]
    solid = a >= A_SOLID
    near = cv2.dilate(solid.astype(np.uint8), np.ones((2 * NEAR + 1, 2 * NEAR + 1), np.uint8)) > 0
    keep = (a > A_MIN) & (solid | near)
    n, lab, st, _c = cv2.connectedComponentsWithStats(keep.astype(np.uint8), 8)
    small = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] < SPECK])
    keep &= ~small
    gone = int(((a > 0) & ~keep).sum())
    p[~keep] = 0
    ys, xs = np.nonzero(keep)
    box = (max(int(xs.min()) - PAD, 0), max(int(ys.min()) - PAD, 0), min(int(xs.max()) + 1 + PAD, p.shape[1]), min(int(ys.max()) + 1 + PAD, p.shape[0]))
    return p[box[1]:box[3], box[0]:box[2]], gone, box


def small(rgba_u8, w_out=W_OUT):
    """すき通しを かけた 色で 幅 w_out に 小さく する（ふちに 外の 色が まざらない）"""
    p = rgba_u8.astype(np.float32); h = int(round(p.shape[0] * w_out / p.shape[1])); al = p[..., 3:4] / 255; pm = np.dstack([p[..., :3] * al, p[..., 3]])
    ch = [np.array(Image.fromarray(pm[..., i], 'F').resize((w_out, h), Image.LANCZOS)) for i in range(4)]
    al2 = np.clip(ch[3], 0, 255); rgb = np.dstack(ch[:3]) / np.maximum(al2[..., None] / 255, 1e-3)
    out = np.dstack([np.clip(rgb + 0.5, 0, 255), al2 + 0.5]).astype(np.uint8); out[out[..., 3] < 3] = 0
    return Image.fromarray(out, 'RGBA')


def panel(im):
    """まん中の クリーム色の 板（いちばん 大きい かたまり）→ 箱（左・上・右・下：絵の 幅・高さに 対する 割合）と、角を さけた 中の 箱（字を 書いて よい 所）"""
    import cv2
    p = np.array(im).astype(np.int32); r, g, b, a = (p[..., i] for i in range(4))
    cream = (a > 200) & (r > 228) & (g > 208) & (b > 165) & (r - b < 75) & (r - g < 40)
    n, lab, st, _c = cv2.connectedComponentsWithStats(cream.astype(np.uint8), 8)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); x, y, w, h = (int(v) for v in st[i][:4]); m = lab == i
    rows, cols = m.sum(1), m.sum(0)
    ys = np.nonzero(rows > 0.97 * rows.max())[0]; xs = np.nonzero(cols > 0.97 * cols.max())[0]      # 角（ななめに 欠けて いる）を さけた 中
    W, H = im.size
    return [round(x / W, 4), round(y / H, 4), round((x + w) / W, 4), round((y + h) / H, 4)], [round(int(xs.min()) / W, 4), round(int(ys.min()) / H, 4), round((int(xs.max()) + 1) / W, 4), round((int(ys.max()) + 1) / H, 4)]


def put(data, dst):
    if os.path.exists(dst):
        assert open(dst, 'rb').read() == data, dst + '：同じ 名前で 中身の ちがう ファイルが もう ある（上書きしない。新しい 名前に する）'
        return 'そのまま'
    open(dst, 'wb').write(data); return '足した'


def build(src):
    """→ (WebP の 中身, 絵〈RGBA〉, 消した 画素, もとの 絵の 中の 箱)"""
    import io
    raw, gone, box = clean(src); im = small(raw)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=Q, method=6, alpha_quality=100, exact=False)
    back = np.array(Image.open(io.BytesIO(buf.getvalue())).convert('RGBA')); assert np.array_equal(back[..., 3], np.array(im)[..., 3]), 'すき通しが かわった'
    return buf.getvalue(), im, gone, box


if __name__ == '__main__':
    src, snd = sys.argv[1], sys.argv[2]
    out = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, '..', '..', 'ios', 'tc_assets'))
    assert os.path.isdir(out), out
    data, im, gone, box = build(src)
    pb, pin = panel(im)
    print('tc_telop_big.webp', im.size, len(data), 'B', 'もとの 絵の 箱', box, 'うすい もやを 消した 画素', gone, put(data, os.path.join(out, 'tc_telop_big.webp')))
    print('  板（割合）', pb, '・字を 書いて よい 所', pin, '・たて÷よこ', round(im.size[1] / im.size[0], 4))
    for f in SOUNDS:
        d = open(os.path.join(snd, f), 'rb').read()
        print(f, len(d), 'B', put(d, os.path.join(out, f)))
