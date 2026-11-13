# 「お世話トークン購入」の ボタンの 絵を アプリ用に 置く（第4.165版）
#   まさちゃん 2026/11/13 11:46「お世話トークン購入、のアイコンを左下のお世話などの項目の上に設置　アイコンは一枚目」（横長の ボタンの 絵）
#   → 12:36「お世話トークン購入のアイコンやっぱりこっちで！お世話とかのところに上手く入れられない？」（丸い 絵：金の 輪・折り紙の 馬の コインと 緑の ＋・ニンジン・ハート・
#     リボンに「お世話トークン／購入」）→ 12:38「1番右側に入れて！」＝ 下の 列（撫でる・ごはん・おそうじ・呼ぶ）の 1番 右に 丸い 絵（tc/tc_care.js の BUYG）
#   python3 kisekae/tc/buy_asset.py <まさちゃんの 丸い 絵（PNG・すき通し）> [ios/tc_assets]
#     → 12:46「周りの大きさと合わせて！バランス調整して！」＝ ほかの ボタンと 同じ 大きさ（輪の 直径 140）・5つを 同じ 間かくで・下に 名前「トークン購入」
#   → tc_icon_buy2.webp：絵の まわりの 余白を 切って 幅 480px（画面では 幅 142 ＝ 3倍の 画面で 158〜178px。大きく 見せる ことに なっても 足りる 細かさで 持つ：
#     描く ときは なめらかに ちぢめる〈imageSmoothingQuality high〉）・WebP 92・すき通しは ロスなし
#   ・はじめの 絵（横長：tc_icon_buy.webp・幅 720）は 使わなく なった。もとの フォルダには 残す（消さない・上書きしない）・アプリには 入れない（assets_dir.superseded）
#   ・もとの 絵（まさちゃんの PNG）と できた ファイルは リポジトリに 入れない（ios/tc_assets/ は .gitignore）
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc/tc_care.js の 名前も かえる）
#   ・kisekae/tc/collect_assets.py は 出す フォルダを 作り直す ので、走らせた あとは これを もう一度。足した あとは python3 kisekae/lite_assets.py
import io, os, sys
import numpy as np
from PIL import Image
W_OUT, PAD, Q = 480, 6, 92
NAME = 'tc_icon_buy2.webp'


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


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ios', 'tc_assets')
    assert os.path.isdir(out_dir), out_dir
    im, box = art(src)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=Q, method=6, exact=True, alpha_quality=100); data = buf.getvalue()
    dst = os.path.join(out_dir, NAME)
    if os.path.exists(dst):
        if open(dst, 'rb').read() == data: print('同じ ものが もう ある：', dst); return
        raise SystemExit(f'もう ある ファイルと 中身が ちがう（上書きしない）：{dst}')
    with open(dst, 'xb') as f: f.write(data)
    print(f'{NAME}：{im.size[0]}×{im.size[1]}・{len(data):,}B（もとの 絵の 箱 {box}）→ {dst}')


if __name__ == '__main__':
    main()
