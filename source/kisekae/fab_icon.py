# 右上の 丸い ボタンの 絵（まさちゃんの アイコン：トレーニングセンター・思い出フィギュア）を アプリ用の WebP に する
#   python3 kisekae/fab_icon.py <元の 絵（RGBA の PNG）> <出す .webp>
#   ・どちらの アイコンも 同じ 大きさで 出る ように：すきとおって いない 所（丸）を 切り出して 240×240 の まん中に 232px で 置く
#     （tc/tc_launch.js の .fabi＝66px の 中で 丸が 64px ほど）
#   ・ちぢめる ときは 色に すきとおり具合を かけてから（ふちに 黒や 白の すじが 出ない ように）
#   ・絵（まさちゃんの アイコン）と 出した WebP は リポジトリに 入れない（ios/tc_assets/・ios/fig_assets/ は .gitignore）
#   kisekae/tc/collect_assets.py（tc_icon_tc.webp）と kisekae/fig/collect_assets.py（fg_icon.webp）が make() を 使う
import sys
from PIL import Image

SIZE, ART, Q = 240, 232, 92


def make(src, dst, size=SIZE, art=ART, q=Q):
    im = Image.open(src).convert('RGBA')
    box = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    assert box, ('すきとおって いない 所が ない', src)
    w, h = box[2] - box[0], box[3] - box[1]; s = max(w, h)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    sq = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    sq.paste(im, (int(round(s / 2 - cx)), int(round(s / 2 - cy))))
    small = sq.convert('RGBa').resize((art, art), Image.LANCZOS).convert('RGBA')
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(small, ((size - art) // 2, (size - art) // 2))
    out.save(dst, 'WEBP', quality=q, method=6)
    return out


if __name__ == '__main__':
    o = make(sys.argv[1], sys.argv[2])
    print('できた', sys.argv[2], o.size)
