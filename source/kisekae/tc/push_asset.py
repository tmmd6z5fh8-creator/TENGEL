# お世話の あとの PUSH の 絵と 音を アプリ用に 置く（第4.159版・まさちゃん 2026/11/12 10:37「お世話が終わったあとに、pushボタンが出てくるようにして(pushボタンは俺が準備する)」
#   ＋ 赤い 折り紙の ボタンの 絵 1まい。字は 入れない（11:0x「入れない」＝絵の まま））
#   python3 kisekae/tc/push_asset.py <まさちゃんの 絵（PNG・すき通し）> <音の フォルダ（kisekae/tc/snd/export_app.py <フォルダ> tc_se_pfo,tc_se_dedeen,tc_se_kyuin の 出力）> [ios/tc_assets]
#   → tc_push_cap.webp（赤い ボタン だけ）・tc_push_base.webp（黒い 台 だけ）：押した とき 赤い ボタン だけが 台の 中へ 沈む（アプリは 赤い ボタンを 少し 下へ ずらして 描いて から 台を 上に 描く）。
#       2まいを 重ねると もとの 絵（さかいに すきまが 出ない ように、赤い ボタンの 色を 台の 下へ 少し ひろげて ある）。
#       絵の まわりの 余白を 切って 幅 660px（画面では 148pt ＝ 3倍の 画面で 444px）・WebP 90・すき通しは ロスなし
#     tc_push.webp（もとの 絵を そのまま 小さく した 1まい：はじめに 作った もの。アプリには 入れない＝assets_dir.superseded）
#     tc_se_pfo.m4a（ハズレ：プフォ）・tc_se_dedeen.m4a（200〜300P：デデーン）・tc_se_kyuin.m4a（ルーレット当選：キュインキュイーン）
#   ・もとの 絵（まさちゃんの PNG）と できた ファイルは リポジトリに 入れない（ios/tc_assets/ は .gitignore）
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc/tc_care.js の 名前も かえる）
#   ・kisekae/tc/collect_assets.py は 出す フォルダを 作り直す ので、走らせた あとは これを もう一度。足した あとは python3 kisekae/lite_assets.py
import os, shutil, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
W_OUT, PAD, Q = 660, 12, 90
SOUNDS = ('tc_se_pfo.m4a', 'tc_se_dedeen.m4a', 'tc_se_kyuin.m4a')


def art(src):
    """絵の ある 所（すき通って いない 所）＋余白 PAD で 切って、幅 W_OUT に → (RGBA の 絵, もとの 絵の 中の 箱)"""
    im = Image.open(src).convert('RGBA'); a = np.array(im)[..., 3]
    ys, xs = np.nonzero(a > 8)
    box = (max(int(xs.min()) - PAD, 0), max(int(ys.min()) - PAD, 0), min(int(xs.max()) + 1 + PAD, im.size[0]), min(int(ys.max()) + 1 + PAD, im.size[1]))
    c = im.crop(box); h = int(round(c.size[1] * W_OUT / c.size[0]))
    # すき通しを かけた 色で 小さく する（ふちに 外の 色が まざらない）
    p = np.array(c).astype(np.float32); al = p[..., 3:4] / 255; pm = np.dstack([p[..., :3] * al, p[..., 3]])
    ch = [np.array(Image.fromarray(pm[..., i], 'F').resize((W_OUT, h), Image.LANCZOS)) for i in range(4)]
    al2 = np.clip(ch[3], 0, 255); rgb = np.dstack(ch[:3]) / np.maximum(al2[..., None] / 255, 1e-3)
    out = np.dstack([np.clip(rgb + 0.5, 0, 255), al2 + 0.5]).astype(np.uint8); out[out[..., 3] == 0] = 0
    return Image.fromarray(out, 'RGBA'), box


def crop_box(src):
    im = Image.open(src).convert('RGBA'); a = np.array(im)[..., 3]
    ys, xs = np.nonzero(a > 8)
    return im, (max(int(xs.min()) - PAD, 0), max(int(ys.min()) - PAD, 0), min(int(xs.max()) + 1 + PAD, im.size[0]), min(int(ys.max()) + 1 + PAD, im.size[1]))


def small(rgba_u8):
    """すき通しを かけた 色で 幅 W_OUT に 小さく する（ふちに 外の 色が まざらない）"""
    p = rgba_u8.astype(np.float32); h = int(round(p.shape[0] * W_OUT / p.shape[1])); al = p[..., 3:4] / 255; pm = np.dstack([p[..., :3] * al, p[..., 3]])
    ch = [np.array(Image.fromarray(pm[..., i], 'F').resize((W_OUT, h), Image.LANCZOS)) for i in range(4)]
    al2 = np.clip(ch[3], 0, 255); rgb = np.dstack(ch[:3]) / np.maximum(al2[..., None] / 255, 1e-3)
    out = np.dstack([np.clip(rgb + 0.5, 0, 255), al2 + 0.5]).astype(np.uint8); out[out[..., 3] == 0] = 0
    return Image.fromarray(out, 'RGBA')


def split(src, grow=7):
    """赤い ボタン（cap）と 黒い 台（base）に 分ける → (cap, base)：どちらも 幅 W_OUT の RGBA・同じ 大きさ。
       cap は 台の 下へ grow px（もとの 絵の 画素）だけ 色を ひろげる（台を 上に 描く ので 見えない：小さく した ときに さかいが すけない）"""
    import cv2
    im, box = crop_box(src); p = np.array(im.crop(box)); r, g, b, a = (p[..., i].astype(np.int32) for i in range(4))
    red = (a > 8) & (r - np.maximum(g, b) > 45)
    n, lab, st, _c = cv2.connectedComponentsWithStats(red.astype(np.uint8), 8)
    cap = lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))                 # いちばん 大きい 赤い かたまり＝ボタン
    cap = cv2.morphologyEx(cap.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    base = (a > 8) & ~cap
    ext = (cv2.dilate(cap.astype(np.uint8), np.ones((2 * grow + 1, 2 * grow + 1), np.uint8)) > 0) & base      # 台の 下へ ひろげる 所
    _d, near = cv2.distanceTransformWithLabels((~cap).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(cap); lut = np.zeros((near.max() + 1, 3), np.uint8); lut[near[ys, xs]] = p[ys, xs, :3]
    capI = np.zeros_like(p); capI[cap] = p[cap]; capI[ext, :3] = lut[near][ext]; capI[ext, 3] = 255
    baseI = np.zeros_like(p); baseI[base] = p[base]
    return small(capI), small(baseI), box


def put(data, dst):
    if os.path.exists(dst):
        assert open(dst, 'rb').read() == data, dst + '：同じ 名前で 中身の ちがう ファイルが もう ある（上書きしない。新しい 名前に する）'
        return 'そのまま'
    open(dst, 'wb').write(data); return '足した'


if __name__ == '__main__':
    src, snd = sys.argv[1], sys.argv[2]
    out = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, '..', '..', 'ios', 'tc_assets'))
    assert os.path.isdir(out), out
    im, box = art(src)
    tmp = os.path.join(out, '.tc_push.tmp.webp'); im.save(tmp, 'WEBP', quality=Q, method=6, alpha_quality=100, exact=False)
    back = np.array(Image.open(tmp).convert('RGBA')); assert np.array_equal(back[..., 3], np.array(im)[..., 3]), 'すき通しが かわった'
    data = open(tmp, 'rb').read(); os.remove(tmp)
    print('tc_push.webp', im.size, len(data), 'B', 'もとの 絵の 箱', box, put(data, os.path.join(out, 'tc_push.webp')))
    cap, base, _b = split(src)
    for nm, q in (('tc_push_cap.webp', cap), ('tc_push_base.webp', base)):
        q.save(tmp, 'WEBP', quality=Q, method=6, alpha_quality=100, exact=False)
        back = np.array(Image.open(tmp).convert('RGBA')); assert np.array_equal(back[..., 3], np.array(q)[..., 3]), nm + '：すき通しが かわった'
        d = open(tmp, 'rb').read(); os.remove(tmp)
        print(nm, q.size, len(d), 'B', put(d, os.path.join(out, nm)))
    for f in SOUNDS:
        d = open(os.path.join(snd, f), 'rb').read()
        print(f, len(d), 'B', put(d, os.path.join(out, f)))
