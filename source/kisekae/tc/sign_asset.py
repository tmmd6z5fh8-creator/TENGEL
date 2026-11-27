# トレーニングセンターの 牧場の 看板の 絵を アプリ用に 置く（第4.234版・まさちゃん 2026/11/28 02:59「トレーニングセンターの牧場の名前をユーザーが決められるようにできる？
#   一枚目の黄四角のところに、二枚目みたいに、看板置いて！三枚目が看板のモデル！ユーザーが名前打ち込んで決められるようにして！」）
#   python3 kisekae/tc/sign_asset.py [ios/tc_assets]
#   もと：ios/tc_src/ranch_sign.png（まさちゃんの 看板の 絵：何も 書いて いない 木の 板・金の びょう 2つ・すき通し つき 2172×724）。**読む だけ**（上書きしない・消さない）
#   → tc_sign.webp（幅 840px＝看板の 幅 いちばん 大きい 280pt の 3倍：まわりの かげ〈濃さ 4 より 上〉まで 切りぬいて、たてよこの 比は もとの まま）
#   ・使う 所：tc/tc_app.js の .tcnm（フィールドの すぐ 上の 帯：名前は 字で 書く ＝ 絵には 書かない）。字を 書く 所（板の 中の、金の びょうの 内がわ）は
#     tc_app.js の SIGN（切りぬいた 絵の 中の 割合：左 8.94%・幅 82.51%・上 14.37%・高さ 67.07%）。絵を かえる ときは そこも 合わせる
#   ・もとの 絵と できた ファイルは リポジトリに 入れない（ios/tc_src/・ios/tc_assets/ は .gitignore）
#   ・**上書きしない**：同じ 名前の ファイルが もう あって 中身が ちがう ときは 止まる（かえる ときは 新しい 名前に して tc_app.js の 名前も）
#   ・足した あとは python3 kisekae/lite_assets.py（アプリに 入るのは 軽い 版の フォルダ ios/lite/tc_assets：この 絵は そのまま 写る）
import hashlib, io, os, sys
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)); WK = os.path.dirname(os.path.dirname(H))
SRC = os.path.join(WK, 'ios', 'tc_src', 'ranch_sign.png')
SRC_SHA1, SRC_SIZE = 'ca366a51f9735594b90f010968ff0444aed6cc65', (2172, 724)
NAME, W_OUT, Q = 'tc_sign.webp', 840, 92
CROP = (68, 198, 2104, 532)          # 板と かげ（濃さ 4 より 上：72〜2100 × 202〜528）に 4px の すきま
TEXT = (250, 246, 1930, 470)         # 字を 書く 所（もとの 絵の 画素：左の びょう〈165〜235〉と 右の びょう〈1944〜2013〉の 内がわ・板の 明るい 木目〈246〜470〉）


def make():
    if not os.path.isfile(SRC): sys.exit('※ もとの 絵が ない：' + SRC)
    if hashlib.sha1(open(SRC, 'rb').read()).hexdigest() != SRC_SHA1: sys.exit('※ もとの 絵が かわって いる（切りぬく 所・字の 所を 見直してね）：' + SRC)
    im = Image.open(SRC).convert('RGBA'); assert im.size == SRC_SIZE, im.size
    box = im.getchannel('A').point(lambda v: 255 if v > 4 else 0).getbbox()
    assert box == (72, 202, 2101, 529), box          # かげの はしまで（getbbox は 右・下が 1つ 先）
    cut = im.crop(CROP); w, h = cut.size
    hh = int(round(W_OUT * h / w))
    out = cut.convert('RGBa').resize((W_OUT, hh), Image.LANCZOS).convert('RGBA')       # ちぢめる ときは 色に すき通り具合を かけてから（ふちに すじが 出ない）
    buf = io.BytesIO(); out.save(buf, 'WEBP', quality=Q, method=6)
    x0, y0 = CROP[0], CROP[1]
    pct = dict(left=(TEXT[0] - x0) / w * 100, width=(TEXT[2] - TEXT[0]) / w * 100, top=(TEXT[1] - y0) / h * 100, height=(TEXT[3] - TEXT[1]) / h * 100, ar=w / h)
    return out, buf.getvalue(), pct


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WK, 'ios', 'tc_assets')
    assert os.path.isdir(out_dir), out_dir
    im, data, pct = make()
    dst = os.path.join(out_dir, NAME)
    if os.path.exists(dst):
        if open(dst, 'rb').read() == data: print('同じ ものが もう ある：', dst, {k: round(v, 4) for k, v in pct.items()}); return
        raise SystemExit(f'もう ある ファイルと 中身が ちがう（上書きしない）：{dst}')
    with open(dst, 'xb') as f: f.write(data)
    print(f'{NAME}：{im.size[0]}×{im.size[1]}・{len(data):,}B → {dst}', {k: round(v, 4) for k, v in pct.items()})


if __name__ == '__main__':
    main()
